'''
Author: Erwin Diepgrond
Copyright 2016 under GNU license
e.j.diepgrond@gmail.com

	This file is part of NeuroNet.

	NeuroNet is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, 
	or any later version.

	NeuroNet is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with NeuroNet.  If not, see <http://www.gnu.org/licenses/>.
'''

import gc
import multiprocessing as mp
from math import floor
from time import clock


class Worker(mp.Process):
    static_parent_connections = []
    def __init__(self,id,verbose=False):
        mp.Process.__init__(self)
        self.child_conn, self.parent_conn = mp.Pipe(True)
        Worker.static_parent_connections.append(self.parent_conn)
        self.daemon = False
        self.id = id
        self.verbose = verbose
        if self.verbose: print('Starting child %i'%id)
        self.start() # Spawn process, main continues from here
        self.child_conn.close()

    def run(self):
        self.parent_conn.close() # We are the child!
        self.child_conn.send(True)
        if self.verbose: print('Child(%i) started'%self.id)
        self.loop()
        if self.verbose: print('Stopping child %i'%self.id)
        self.child_conn.close()

    def do(self,command):
        """
        Default class for various functions.
        You can overwrite this!
        :param command: commands in type 1, 2, 3 or 4
                        contains: [type,
        :return:
        """
        results = []
        if command[0]==1: #one function, [loads of data]
            function = command[1]
            data = command[2]
            for i in data:
                if type(i) == tuple:
                    results.append(function(*i))
                else:
                    results.append(function(i))
        elif command[0]==2: #[[one function, data] list]
            for i in command[1]:
                if type(i[1]) == tuple:
                    results.append(i[0](*i[1]))
                else:
                    results.append(i[0](i[1]))
        elif command[0]==3: #[[class,'member']] --> class.member() --> result --> [results]
            for i in command[1]:
                results.append(getattr(i[0],i[1])())
        elif command[0]==4: #[[class,'member',(arguments)]] --> class.member() --> result --> [results]
            for i in command[1]:
                results.append(getattr(i[0],i[1])(*i[2]))
        else:
            return None #Unknown
        return results

    def loop(self):
        while True:
            command = self.child_conn.recv()  # recieve command
            if command == None:
                break
            if self.verbose: print('Child(%i): Processing data...' % self.id)
            start = clock()
            self.child_conn.send(self.do(command))  # send answers
            if self.verbose: print('Child(%i): Done! in %.2f seconds' % (self.id, clock() - start))


class Pool:
    def __init__(self,nWorkers = mp.cpu_count(),verbose=False,workerClass=Worker):
        """
        Creates a pool of workerClasses
        :param nWorkers: amount of child processes
        :param verbose: Sets child verbosity (started, stopped, job received, job done(time))
        :param workerClass: The Worker class (or process)
        :return: Nothing
        """
        if nWorkers < 1 or not type(nWorkers)==int:
            TypeError('nWorkers must be > 1 integer')

        self._verbose = verbose
        self.nWorkers = nWorkers
        t=clock()
        print('Pool: Starting %i workers...'%nWorkers)
        for i in range(self.nWorkers):
            workerClass(i,verbose=verbose)
        for i in Worker.static_parent_connections:
            i.recv()
            print('Pool: Worker started (delta: %.4f)' % (clock()-t))

    def __del__(self):
        self.close()

    def close(self):
        self._stopWorkers()
        Worker.static_parent_connections = []

    def dispatchJobType1(self,function,data): #one function, [loads of data]
        """
        (function,data) --> function(data[i]) --> result --> [results]
        :param function: a function
        :param data:  one dimensional list containing data
        :return: Nothing
        """
        t=clock()
        data = self.splitArray(data,self.nWorkers)
        if self._verbose: print('Job spliced in %.5fs'%(clock()-t))
        t=clock()
        self.working = len(data)
        for i in range(len(data)):
            Worker.static_parent_connections[i].send([1,function,data[i]])
        if self._verbose: print('Job dispatched in %.5fs'%(clock()-t))

    def dispatchJobType2(self,batch):
        """
        batch = [(function,data),...] --> function(data) --> result --> [results]
        :param batch: a list containing tuples (function,data)
        :return: Nothing
        """
        t=clock()
        batch = self.splitArray(batch,self.nWorkers)
        if self._verbose: print('Job spliced in %.5fs'%(clock()-t))
        t=clock()
        self.working = len(batch)
        for i in range(len(batch)):
            Worker.static_parent_connections[i].send([2,batch[i]])
        if self._verbose: print('Job dispatched in %.5fs'%(clock()-t))

    def dispatchJobType3(self,batch):
        """
        batch = [ [class,'member'], ...] --> class.member() --> result --> [results]
        :param batch: a list containing list [class,'member']
        :return: Nothing
        """
        t=clock()
        batch = self.splitArray(batch,self.nWorkers)
        if self._verbose: print('Job spliced in %.5fs'%(clock()-t))
        t=clock()
        self.working = len(batch)
        for i in range(len(batch)):
            Worker.static_parent_connections[i].send([3,batch[i]])
        if self._verbose: print('Job dispatched in %.5fs'%(clock()-t))

    def dispatchJobType4(self,batch):
        """
        batch = [ [class,'member',(arguments)], ...] --> class.member(arguments) --> result --> [results]
        :param batch: a list containing list [class,'member',(arguments)]
        :return: Nothing
        """
        t=clock()
        batch = self.splitArray(batch,self.nWorkers)
        if self._verbose: print('Job spliced in %.5fs'%(clock()-t))
        t=clock()
        self.working = len(batch)
        for i in range(len(batch)):
            Worker.static_parent_connections[i].send([4,batch[i]])
        if self._verbose: print('Job dispatched in %.5fs'%(clock()-t))

    def getResult(self,dict = False):
        """
        Waits for each thread to be finished and returns data
        :param dict: Set dict to true if the results are dicts (dicts cant be +'ed)
        :return: [data]
        """
        if self.working == 0:
            return None
        gc.disable() #Disable garbage collection to speedup append and update
        t=clock()

        if not dict:
            res = []
            for i in range(self.working):
                res = res + Worker.static_parent_connections[i].recv()
        else:
            res = {}
            for i in range(self.working):
                res.update(Worker.static_parent_connections[i].recv())
        self.working = 0
        if self._verbose: print('Results gathered in %.5f seconds' % (clock()-t))
        gc.enable()
        return res

    def getResults(self):
        """
        Waits for each thread to be finished and returns data
        :return: [[data thread1], [data thread 2] , ...]
        """
        if self.working == 0:
            return None

        gc.disable()#Disable garbage collection to speedup append and update
        t = clock()

        self.working = 0
        res = []
        for i in range(self.working):
            res.append(Worker.static_parent_connections[i].recv())
        if self._verbose: print('Results gathered in %.5f seconds' % (clock()-t))
        gc.enable()
        return res

    def getResultsYielding(self):
        """
        Waits separately for each thread to be finished and yields data
        :yields: [data thread1], [data thread 2] , ...
        """
        if self.working == 0:
            return None

        gc.disable()#Disable garbage collection to speedup append and update
        t = clock()


        for i in range(self.working):
            yield Worker.static_parent_connections[i].recv()
        self.working = 0
        if self._verbose: print('All results yielded in %.5f seconds' % (clock()-t))
        gc.enable()

    def splitArray(self,arr,sn):
        if not type(sn)==int:
            Exception('Invalid input given. Expected int, received %s' % type(sn))

        if sn == 1:
            return [arr]

        l = len(arr)
        if l % sn == 0:
            step = int(l/sn)
            if step < 1: step = 1
            return [arr[i:i+step] for i in range(0,l,step)]
        else:
            step = floor(l/sn)
            if step < 1: step = 1
            res = [arr[i:i+step] for i in range(0,l-(l % sn),step)]
            #res[sn-1] = res[sn-1]+ arr[-(l % sn):l]
            cnt = 0
            if len(res) == 0: res = [[] for x in range((l % sn))]
            for i in arr[-(l % sn):l]:
                res[cnt].append(i)
                cnt+=1
            return res


    def _stopWorkers(self):
        for i in Worker.static_parent_connections:
            try:
                i.send(None)
                i.close()
            except:
                pass

