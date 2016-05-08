import multiprocessing as mp
class ParWriter:
    def __init__(self, file, mode='w'):
        self.file = file
        self.mode = mode
        # Init pipe
        self.pipeout, self.pipein = mp.Pipe(duplex=False)
        #init process
        self.process = mp.Process(target=self.mproutine, args=(file, mode, self.pipeout,))
        self.process.start()

    def mproutine(self, file, mode, pipeout):
        import time
        with open(file, mode) as fhandle:
            print('(ParWriter): %s open' % file)
            try:
                while True:
                    while not pipeout.poll():
                        time.sleep(0.01)
                    data = pipeout.recv()
                    if data == '\x04':
                        print('(ParWriter): EOF received, closing...')
                        pipeout.close()
                        fhandle.flush()
                        return
                    fhandle.write(data)

            except EOFError:
                print('(ParWriter): EOF error, closing...')
                pipeout.close()
                fhandle.flush()
            except:
                from sys import exc_info
                print('(ParWriter): Error: %s' % (exc_info()[0]))
                pipeout.close()
                fhandle.flush()

        print('(ParWriter): %s closed' % file)




    def checkopen(self):
        return (self.process.is_alive())

    def write(self, data):
        try:
            self.pipein.send(data)
            return True
        except IOError:
            print('(ParWriter): Pipe closed')
            return False
        except:
            from sys import exc_info
            print('(ParWriter): Error: %s' % (exc_info()[0]))
            return False

    def append(self, data):
        self.write(data) #small wrapper

    def close(self):
        self.pipein.send('\x04')
        self.pipein.close()
        self.process.join()
        self.process.terminate()
