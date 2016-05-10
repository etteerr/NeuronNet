import Engine.python27Ca2VideoMaker as ca
import Engine.ENNet as enn
import time
import networkx as nx
import pickle

dt = 0.05
N = 500
fps = 120.0
G = nx.fast_gnp_random_graph(N, p=0.3)

rec = enn.Recorder(0, range(0,500), readonly=True, dt=0.05, diskMode=True, toDiskDir='Neuralnetwork1')
a = rec.getSpikeEventtimes(var='Vm')
trace = ca.spikeEventsToCa2Trace(a, dt=0.05, end=5100)
caTrace = ca.addGaussNoise(trace)


start = time.clock()
print('Generating network coordinates...')
G = ca.generateNetworkCoordinates(G)
print('Done (%.4f)' % (time.clock() - start))

start = time.clock()
print('Adding Gaussian noise to the trace...')
caTrace = ca.addGaussNoise(caTrace)
print('Done (%.4f)' % (time.clock() - start))

start = time.clock()
print('Saving trace...')
with open('caTrace.dat', 'wb') as f:
	pickle.dump(caTrace, f)
print('Done (%.4f)' % (time.clock() - start))

start = time.clock()
print('Rendering video...')
ca.renderCa2Video(caTrace, G, dt=dt, fps=fps, mode='mean', noisemax=20, noiserep=fps*60)
print('Done!!!! (%.2f)' % (time.clock() - start))