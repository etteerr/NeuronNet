import numpy as np
import networkx as nx
import Engine.python27Ca2VideoMaker as ca
import Engine.ENNet as enn
import Engine.ENN_Models as models
import pickle
import pylab as pl

dt = 0.05
N = 2
fps = 2000.0
G = nx.fast_gnp_random_graph(N, p=1)


rec = enn.Recorder(0, range(0,N), variables=['Vm', 'I'], readonly=True, dt=0.05, diskMode=True, toDiskDir='TestDir')


pl.figure()

ax = pl.subplot(211)
pl.title('2 neurons: (0) -- 0.5 --> (1)    Neuron 0')
v = rec['Vm'][0].getList()
i = rec['I'][0].getList()
t = rec.timeline.getList()

pl.plot(t,v)
pl.plot(t,i)
pl.ylabel('Membrane Voltage (mv)')

pl.subplot(212, sharex=ax, sharey=ax)
pl.title('2 neurons: (0) -- 0.5 --> (1)    Neuron 1')
v = rec['Vm'][1].getList()
i = rec['I'][1].getList()
pl.plot(t,v)
pl.plot(t,i)

pl.ylabel('Membrane Voltage (mv) and input current (pA)')
pl.xlabel('Time (ms)')

pl.show()