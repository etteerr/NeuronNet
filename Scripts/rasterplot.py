import pylab as pl
import Engine.ENNet as enn
import pickle

with open('events.dat', 'rb') as f:
    a = pickle.load(f, encoding='bytes')


for id in a.keys():
    data = a[id]
    for i in data:
        pl.vlines(i, id +0.5, id + 1.5, color='k')

pl.xlabel('Time (ms)')
pl.ylabel('Neuron id')
pl.show()
