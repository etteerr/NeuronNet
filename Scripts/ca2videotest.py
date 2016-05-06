import numpy as np
import networkx as nx
import Engine.python27Ca2VideoMaker as ca
import Engine.ENNet as enn
import Engine.ENN_Models as models
import pickle
#import pylab as pl



'''
time = 20#sec
dt = 1.0 #ms
fps = 100.0

samples = (time * 1000) / dt
data = {}
data[1] = np.random.normal(4,4,samples)
data[2] = np.random.poisson(4,samples)
G = {1:[0,0],
     2:[0.5, 0.5]}

#G = nx.circular_layout(G, dim=2, scale=4/800)
'''
if __name__ == '__main__':
    dt = 0.05
    N = 100
    fps = 120.0
    G = nx.fast_gnp_random_graph(N, p=0.3)

    synapseDict = {
        'I': ([0] * int(5 / dt)),
        'i': 0,  # iterator
        'i2': 0,  # iterator recovery
        'rp': 1 / dt,  # refractive period in dt
        'threshold': 10,
        'w': 1  # Mathematisch gewicht (v*w) Zie synapse (induces a 10mV * 0.01ms * 1000weight current = 100 )
    }


    simulator = enn.Simulator()

    network = enn.Network(models.HodgkinAndHuxleyNeuron,
                          models.default_Hodgkin_Huxley_neuron_dict,
                          models.erwinHandHsynapse,
                          synapseDict,
                          dt,
                          G,
                          True)

    for i in network.getNeuronIDs():
        network.getNeuronByID(i)['Istim'] = 10

    id = simulator.addNetwork(network)

    # Add recorder
    rec = enn.Recorder(id, network.getNeuronIDs(), withTime=True)

    recID = simulator.addRecorder(rec)

    #sim

    simulator.simulate(100)

    for i in network.getNeuronIDs():
        simulator.getNetwork(id).getNeuronByID(i)['Istim'] = 0

    simulator.simulate(5000)

    # Analyse data and create trace
    rec = simulator.getRecorder(recID)
    spikeEvents = rec.getSpikeEventtimes(async=False)
    G = ca.generateNetworkCoordinates(G)
    caTrace = ca.spikeEventsToCa2Trace(spikeEvents,dt=dt, end=5100)
    caTrace = ca.addGaussNoise(caTrace)

    with open('caTrace.dat', 'wb'):
        pickle.dump(caTrace)



    ca.renderCa2Video(caTrace, G, dt=dt, fps=fps, mode='mean', noisemax=20, noiserep=fps*60)