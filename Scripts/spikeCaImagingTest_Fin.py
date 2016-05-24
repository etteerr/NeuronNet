#Python 3.x
import pylab as pl
import pickle
import numpy as np
def test():
    with open('spikeCaImagingTestTrace.dat', mode='rb') as f:
        traces = pickle.load(f, encoding='bytes')

    pl.figure()
    for trace in traces:
        t = np.linspace(0, len(trace)*0.01, len(trace))  # dt in seconds (dt=10ms)
        pl.plot(t, trace)
        pl.hold('on')


    pl.xlabel('Time (s)')
    pl.ylabel('Change in [Ca2+]')
    pl.title('Spike train')
    pl.show()