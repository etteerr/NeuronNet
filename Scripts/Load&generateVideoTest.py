import Engine.python27Ca2VideoMaker as ca
import Engine.ENNet as enn
import time
import networkx as nx
import pickle

dt = 0.05
N = 500
fps = 2000.0
length = 60+250
G = nx.fast_gnp_random_graph(N, p=0)
for net in ['Network_Weight_2.00', 'Network_Weight_3.00', 'Network_Weight_4.00', 'Network_Weight_5.00']:
	rec = enn.Recorder(0, range(0,N), readonly=True, dt=0.05, diskMode=True, toDiskDir=net)
	a = rec.getSpikeEventtimes(var='Vm')
	trace = ca.spikeEventsToCa2Trace(a, dt=0.05, end=length)
	caTrace = ca.addGaussNoise(trace)


	start = time.clock()
	print('Generating network coordinates...')
	G = ca.generateNetworkCoordinates(G)
	print('Done (%.4f)' % (time.clock() - start))

	start = time.clock()
	print('Adding Gaussian noise to the trace...')
	caTrace = ca.addGaussNoise(caTrace,sd=0.2)
	print('Done (%.4f)' % (time.clock() - start))

	'''start = time.clock()
	print('Saving trace...')
	with open('caTrace.dat', 'wb') as f:
		pickle.dump(caTrace, f)
	print('Done (%.4f)' % (time.clock() - start))'''

	start = time.clock()
	print('Rendering video...')
	ca.renderCa2Video(caTrace, G, dt=dt, recfps=fps, mode='mean', noisemax=20, noiserep=256, output='Vid_%s.avi'%net)
	print('Done!!!! (%.2f)' % (time.clock() - start))