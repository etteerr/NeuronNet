import numpy as np
import pylab as pl
from Engine.ENNet import *

if __name__ == '__main__':
    r = Recorder.load('neuronNetData')

    d = r.getSpikeEventtimes('Vm')

    pl.figure(1)
    for (neuron, data) in d.items():
        pl.plot(data,np.zeros(len(data))+neuron, '*')
        pl.hold('on')
    pl.show()
    '''
    timestamps = Recorder._calculateSpikeEventtimes(r['Vm'][2],r['dt'])
    import pylab as pl
    pl.plot(r.timeline, r['Vm'][2])
    pl.hold('on')
    pl.plot(timestamps,np.zeros(len(timestamps))+40, '*')
    pl.show()
    '''

