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

import copy
import sys
import numpy as np
try:
    import peakutils as pu
except ImportError:
    print('Warning: Peakutils not found. Recorder.getSpikeEventtimes not working!')

from multiprocessing import Pool

from time import clock

import pickle


class Simulator:
    """
    Simulator class:
        Simulates networks with neurons and synapses
        Networks are isolated. (may change but useful for simulating in parallel)
        fills recorders with data
        Gives a nice interface
    """

    def __init__(self, ignoreWarnings=False):
        """

        Initializes basic simulator class
        :param ignoreWarnings: Suppresses warnings when changing settings after a simulation has ran
        :return: self
        """
        self._ignoreWarnings = ignoreWarnings
        self._networks = {}
        self._networkIDCounter = 0  # Static maybe?
        self._recorderIDCounter = 0
        self._recorders = {}

    def addNetwork(self, network):
        """
        addNetwork adds a network to the simulation.
        Note that networks are independent simulations of their own
        :param network: a Network class network
        :return: network id generated by this class
        """
        # Create network
        network._id = self._networkIDCounter
        self._networks[self._networkIDCounter] = network
        self._networkIDCounter += 1
        return network._id

    def createNetwork(self, G, neuronFun, synapseFun, neuronDict, synapseDict, dt, verbose=False):
        """
        createNetworks call Network(neuronFun,synapseFun,dt,G) for you
        :param G: networkx network
        :param neuronFun: neuron class derived from the BaseNeuron class in Neurons.py
        :param synapseFun: synapse class derived from the baseSynapse class in Synapses.py
        :param dt: the simulation time step in ms
        :return: network id generated by this class
        """
        network = Network(neuronFun=neuronFun, synapseFun=synapseFun,
                          neuronDict=neuronDict, synapseDict=synapseDict,
                          networkx=G, dt=dt, verbose=verbose
                          )
        return self.addNetwork(network)

    def getNetwork(self, networkId):
        """

        :param networkId: Hashable object specifying networkId
        :return: reference to Network class corresponding to networkId
        """
        try:
            return self._networks[networkId]
        except:
            print('getNetwork: Unknown network')
            return None

    def addRecorder(self, recorder):
        """

        :param recorder: recorder to add to the simulation
        :return: Hashable object specifying recorder ID
        """
        id = self._recorderIDCounter
        self._recorderIDCounter += 1
        recorder.id = id
        self._recorders[id] = recorder
        return id

    def getRecorder(self, recorderId):
        """

        :param recorderId:  Hashable object specifying recorder ID
        :return: Recorder class recorder corresponding to recorderId
        """
        try:
            return self._recorders[recorderId]
        except:
            print('getRecorder: Unknown recorder')
            return None

    def _asyncfun(self, network, time, recs):
        network.simulate(time, recs)
        return network

    def simulate(self, duration_ms, network=None, poolSize=None):
        """
        Starts the simulation for specified duration for all networks
        :param duration_ms: Duration of simulation in ms
        :param network: Specify a networkid to simulate
        :return: None
        """
        print('(Simulator) Starting a %fms network simulation..' % duration_ms)
        t = clock()
        if (network is None and poolSize is None) or sys.version_info < (3,0):
            if sys.version_info < (3,0)and not poolSize is None:
                print('(Simulator) Multiprocessing disabled on 2.7')
            for (id, i) in self._networks.items():
                print('(Simulator) Starting simulation of network %i' % id)
                i.simulate(duration_ms, self._recorders)
        elif network is None and not poolSize is None:

            if poolSize > len(self._networks): poolSize = len(self._networks)
            print('(Simulator) Creating pool of %i processes for %i networks...' % (poolSize, len(self._networks)))
            if poolSize > 0:
                pool = Pool(processes=poolSize)
            else:
                pool = Pool()
            processes = {}
            print('(Simulator) Simulating...')
            for (id, net) in self._networks.items():
                processes[id] = pool.apply_async(self._asyncfun, (net, duration_ms, self._recorders))
            del self._networks
            del self._recorders
            self._networks = {}
            self._recorders = {}
            for (id, proc) in processes.items():
                self._networks[id] = proc.get()
                for rec in self._networks[id]._recorders:
                    self._recorders[rec.id] = rec

                print('(Simulator) Network %i finished.' % id)
            pool.close()
            pool.join()

        elif network in self._networks.keys():
            print('(Simulator) Starting simulation of network %i' % network)
            self._networks[network].simulate(duration_ms, self._recorders)
        print('(Simulator) Done. (%.5f seconds)' % (clock() - t))


class Network:
    _suppressChangeWarnings = False

    def __init__(self, neuronFun, neuronDict, synapseFun, synapseDict, dt, networkx=None, verbose=False,
                 debugVerbose=False, progressCallback=None):
        """
        Generates a network based on the parameters
        :param neuronFun: the neuron Update function with the form of: dict = fun(dict)
        :param synapseFun: the synapse Update function with the form of:
                            synapseDict, sourceDict, destinationDict = fun(synapseDict, sourceDict, destinationDict)
        :param dt: the simulation time step in ms
        :param networkx: a network from the networkx package. If None, initializes empty network
        """
        # Network id, set by simulator
        self._id = None

        # Timestep
        self._dt = dt

        # Verbosity settings
        self._debugVerbose = debugVerbose  # All timings
        self._verbose = verbose  # Progress times

        # Data dicts
        self._neurons = {}
        self._synapses = {}

        # Id counters
        self._neuronCounter = 0
        self._synapseCounter = 0

        # Update default update functions
        self._synapseFun = synapseFun
        self._neuronFun = neuronFun
        self._neuronDict = neuronDict
        self._synapseDict = synapseDict

        # Time
        self._time = 0
        self._timeline = []

        # Data gathering / recording
        self._recorders = []

        # Progress
        self._progressCallback = progressCallback
        self._pCallback = False
        if progressCallback is not None:
            self._pCallback = True

        # Init network
        if not networkx == None:
            if verbose:
                print('(Network  ) Creating network with %i nodes and %i connections...' % (
                    networkx.number_of_nodes(), networkx.number_of_edges()))
            if verbose: start = clock()
            for (i, data) in networkx.nodes_iter(data=True):
                n = copy.copy(neuronDict)
                n.update(data)
                self.addNeuron(neuronFun=neuronFun, neuronDict=n, id=i)

            for (i, j, data) in networkx.edges_iter(data=True):
                self.connect(i, j, data, synapseFun, synapseDict)
            if verbose: print('(Network  ) done! (%.2f seconds)' % (clock() - start))

    def addNeuron(self, neuronFun=None, neuronDict=None, id=None, ):
        """
        adds a neuron
        :param neuronFun: neuron class derived from the BaseNeuron class in Neurons.py
        :return: returns the ID of the generated neuron
        """
        if id == None:  # if none: Choose new Unused ID
            id = self._neuronCounter
            while id in self._neurons.keys():
                self._neuronCounter += 1
                id = self._neuronCounter
        elif id in self._neurons.keys():  # If specified but exists, Error time :D
            raise IndexError('(Network) Index already exists!')

        if neuronFun is None and neuronDict is None:
            neuronFun = self._neuronFun
            neuronDict = self._neuronDict
        elif neuronDict is None:
            raise ValueError('If a new neuron functions is specified, a neuron dictionary must also be specified.')
        elif neuronFun is None:
            neuronFun = self._neuronFun

        # Add neuron
        neuronDict = copy.deepcopy(neuronDict)
        neuronDict['fun'] = neuronFun
        neuronDict['id'] = id
        neuronDict['dt'] = self._dt
        self._neurons[id] = neuronDict
        return id

    def connect(self, sourceId, destinationId, settingsDict={}, synapseFun=None, synapseDict=None):
        """
        connects two neurons  (sourceId -> destinationId)
        :param sourceId: the source neuron
        :param settingsDict: a dictionary specifying attributes of the neuron.
                             These will override existing variables or those of synapseDict
        :param destinationId: the destination neuron
        :return: Synapse ID
        """
        id = self._synapseCounter
        if synapseDict == None and synapseFun == None:
            synapseDict = self._synapseDict
            synapseFun = self._synapseFun
        elif synapseDict == None:
            raise ValueError('If specifying a new synapse, one must also specify its dict')
        elif synapseFun is None:
            synapseFun = self._synapseFun

        synapseDict = copy.deepcopy(synapseDict)
        synapseDict.update(settingsDict)
        synapseDict['_source'] = sourceId
        synapseDict['_destin'] = destinationId
        synapseDict['id'] = id
        synapseDict['fun'] = synapseFun
        self._synapseCounter += 1
        self._synapses[id] = synapseDict
        return id

    def deleteConnection(self, id):
        """
        Deletes specified connection.
        :param id: Key specifying synapse
        :return: connection class (if you want it)
        """
        return self._synapses.pop(id)

    def deleteNeuron(self, id):
        """
        deletes neuron with id: id
        This id will not return, its a gap in the IDs. Keep this in mind when using recorders
        :param id: id of neuron to delete
        :return: returns the neuron class that is deleted
        """
        ids = []
        # find connections TODO: Create a function find to find neurons or connections based on dict
        for (_id, synapse) in self._synapses.items():
            if synapse['_source'] == id or synapse['_destin'] == id:
                ids.append(_id)
        # Delete synapses
        for _id in ids:
            self.deleteConnection(_id)

        return self._neurons.pop(id)

    def getNeuronIDs(self):
        """
        :return: a list containing all IDs of (not deleted) neurons
        """
        return self._neurons.keys()

    def getConnectionIDs(self):
        """
        :return: a list containing all IDs of (not deleted) synapses (connections
        """
        return self._synapses.keys()

    def getNeuronByID(self, id):
        return self._neurons[id]

    def drange(self, start, stop, step=1):
        line = []
        i = start
        while i < stop:
            line.append(i)
            i += step
        return line

    def simulate(self, duration, recorders, poolSize=None):
        """
        Simulates one neuron for time (ms)
        :param duration: duration of simulation in ms
        :param recorders: The recorders for this network
        :param poolSize: The amount of subprocess. < 1 or None = Local only.
        Note: poolSize dramatically increases simulation time... bad implementation
        :return: I wont return a value or anything... baka
        """
        # Generate timeline
        timeline = self.drange(self._time + self._dt, self._time + duration, self._dt)

        # Set recorders
        self._recorders = []
        for (_, recorder) in recorders.items():
            recorder['dt'] = self._dt
            if recorder._networkId == self._id and recorder._withTime:
                recorder.timeline.append( timeline)
                self._recorders.append(recorder)

        # Add to current timeline
        self._timeline += timeline

        # Start simulation
        self.localSim(timeline=timeline)

        return 'Baka!'

    ##################################### Local operations #####################################
    def localSim(self, timeline):
        etaEvery = 60  # seconds (no more than 1 in 5 seconds)
        sPassed = 0
        stepCounter = 0
        totalSteps = len(timeline)

        startTime = clock()
        # loop
        for time in timeline:
            stepTime = clock()
            self._time = time
            self._localStep()
            stepCounter += 1
            stepTime = clock() - stepTime
            sPassed += stepTime
            if sPassed > etaEvery:
                stepsRemaining = totalSteps - stepCounter
                runtime = clock() - startTime
                if self._verbose: print(
                '(Network %i) Estimated time remaining: %.4f seconds  (running %.2f seconds)' % (
                    self._id,
                    (runtime / stepCounter) * stepsRemaining, runtime))
                sPassed = 0
                sys.stdout.flush()

    def _localStep(self):
        if self._debugVerbose: t = clock()
        self._localUpdateNeurons()
        self._localUpdateSynapses()
        self._updateRecorders()
        if self._debugVerbose:
            print('(Network %i) Total update time: %.5f' % (self._id, clock() - t))
            print('(Network %i) -------------------------', self._id)

    def _localUpdateNeurons(self):
        if self._debugVerbose: t = clock()
        for (key, neuron) in self._neurons.items():
            neuron['fun'](neuron)
        if self._debugVerbose: print('(Network %i) update neurons total: %.5f' % (self._id, clock() - t))

    def _localUpdateSynapses(self):
        if self._debugVerbose: t = clock()
        for (key, synapse) in self._synapses.items():
            self._synapses[key], self._neurons[synapse['_source']], self._neurons[synapse['_destin']] = \
                synapse['fun'](synapse, self._neurons[synapse['_source']], self._neurons[synapse['_destin']])
        if self._debugVerbose: print('(Network %i) update synapses total: %.5f' % (self._id, clock() - t))

    def _updateRecorders(self):
        if self._debugVerbose: t = clock()
        for recorder in self._recorders:
            for nid in recorder._neuronIds:
                if nid in self._neurons.keys():
                    for var in recorder._variables:
                        recorder[var][nid].append(self._neurons[nid][var])
        if self._debugVerbose: print('(Network %i) Recorder updates: %.5f' % (self._id, clock() - t))

    def saveState(self, file):
        with open(file + ".pNet", 'wb') as fHandle:
            pickle.dump(self, fHandle)

    @staticmethod
    def loadNetworkState(file):
        with open(file + ".pNet", 'rb') as fHandle:
            return pickle.load(fHandle)


class Recorder(object):
    def __init__(self, networkId, neuronIds, variables=['Vm'], withTime=False, diskMode=False, toDiskDir='defaultDir', buffersize=128, readonly=False, overwrite=False, dt=None):  # TODO: WithTime
        # Buffer size in items
        self._networkId = networkId
        self._neuronIds = list(neuronIds)
        self._variables = variables
        self._withTime = withTime
        self._networkStucture = None
        self._toDisk = diskMode
        if dt is not None:
            self['dt'] = dt

        if diskMode:
            import Engine.DiskList as dl
            import os
            if not os.path.isdir(toDiskDir) and not readonly:
                os.mkdir(toDiskDir)
            elif not os.path.isdir(toDiskDir) and readonly:
                raise IOError('No such directory: %s' % toDiskDir)
            elif os.path.isdir(toDiskDir) and not readonly and not overwrite:
                print('%s opened in append mode!' % toDiskDir)

            self.timeline = dl.DiskList(os.path.join(toDiskDir, 'timeline'), readonly=readonly, overwrite=overwrite)
            for var in variables:
                self[var] = {}
                for i in neuronIds:
                    self[var][i] = dl.DiskList(os.path.join(toDiskDir, 'var_%s_neuron_%s' % (var, i)), readonly=readonly, overwrite=overwrite)
        else:
            self.timeline = []
            for var in variables:
                self[var] = {}
                for i in neuronIds:
                    self[var][i] = []

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def save(self, file):
        if self._toDisk:
            raise RuntimeError('Function not available in disk mode')
        try:
            with open(file + ".pRek", 'wb') as fHandle:
                p = pickle.Pickler(fHandle)
                p.fast = True
                p.dump(self)
        except MemoryError:
            print('Memory error while pickle dumping results, switching to Binary')
            self.saveToXML(file)

    def saveNetworkStucture(self, file):
        with open(file + '.nstruct', 'wb') as fhandle:
            p = pickle.Pickler(fhandle)
            p.dump(self._networkStucture)

    def saveToXML(self, file):
        if self._toDisk:
            raise RuntimeError('Function not available in disk mode')
        '''
        Saves the recorder to a txt file as backup to a pickle. This is not ment to be opened in excel
        :param file:
        :return:
        '''
        import csv
        for var in self._variables:
            with open(file + "_" + var + ".txt", 'w') as f:
                writer = csv.writer(f)
                for (key, value) in self[var].items():
                    writer.writerow([key]+value)

    def setNetworkStructure(self, network, synapseWeightVar='w'):
        """
        Takes a Network class object (from ENNet) and converts it to
        an networkx file. This maybe needed to render the network results.
        :param network:
        :return: Nothing
        """
        if self._toDisk:
            print('Usage warning: Manual save of network structure is still required in disk mode!')
        import networkx as nx
        G = nx.DiGraph()

        # Add nodes
        G.add_nodes_from(network._neurons.keys())

        # Add edges
        edges = []
        for (key, syn) in network._synapses.items():
            weight = syn[synapseWeightVar]
            edges.append((syn['_source'], syn['_desti'], weight))
        G.add_weighted_edges_from(edges)
        self._networkStucture = G


    @staticmethod
    def load(file):
        with open(file + '.pRek', 'rb') as fHandle:
            return pickle.load(fHandle)


    def getSpikeEventtimes(self, var='Vm', async=False, neurons=None, file=None):
        """
        Calculates the spike events and returns an array containing the timestamps of the spikes.
        This is calculated over var for each neuron in neurons. If neurons is None, all neurons are used.
        :param var:
        :param neurons:
        :return: Array of spike events per neuron
        """
        import csv
        if async:
            p = Pool()
            rets = []
            if neurons is None:
                neurons = self._neuronIds

            for nId in neurons:
                if self._toDisk:
                    data = self[var][nId].toList()
                else:
                    data = self[var][nId]
                rets.append((nId, p.apply_async(self._calculateSpikeEventtimes, (data, self['dt']))))

            data = {}
            if file is not None:
                with open(file+'.txt','w') as f:
                    writer = csv.writer(f)
                    for (nId, pId) in rets:
                        data[nId] = pId.get()
                        writer.writerow([nId] + data[nId])
            else:
                for (nId, pId) in rets:
                    data[nId] = pId.get()

            p.close()
            p.join()
        else:
            if neurons is None:
                neurons = self._neuronIds

            data = {}
            for nId in neurons:
                if self._toDisk:
                    data[nId] = self._calculateSpikeEventtimes(self[var][nId].getList(), self['dt'])
                else:
                    data[nId] = self._calculateSpikeEventtimes(self[var][nId], self['dt'])

            if file is not None:
                with open(file + '.txt', 'w') as f:
                    writer = csv.writer(f)
                    for nId in data.keys():
                        writer.writerow([nId] + data[nId])

        return data

    @staticmethod
    def _calculateSpikeEventtimes(data, dt):
        """
        returns for an trace all spike events
        :param data:
        :return:
        """
        #import pylab as pl
        idxs = pu.indexes(np.array(data), thres=0.1, min_dist=100)
        timeEvents = idxs * dt
        return timeEvents

def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print (v)
    else:
        print (obj)