import numpy as np
import networkx as nx
import Engine.python27Ca2VideoMaker as ca
import Engine.ENNet as enn
import Engine.ENN_Models as models
import pickle
import pylab as pl

dt = 0.05
N = 50
fps = 2000.0
#G = nx.fast_gnp_random_graph(N, p=1)


rec = enn.Recorder(0, range(0,N), variables=['Vm', 'I'], readonly=True, dt=0.05, diskMode=True, toDiskDir='TestDir')


pl.figure()


ax = pl.subplot(211)
for j in range(0,N):
    pl.plot(rec['Vm'][j].getList())
    pl.hold('on')

pl.ylabel('Membrane Voltage (mv)')

pl.subplot(212, sharex=ax, sharey=ax)
for j in range(0,N):
    pl.plot(rec['I'][j].getList())
    pl.hold('on')

pl.ylabel('input current (pA)')
pl.xlabel('Time (ms)')

pl.show()