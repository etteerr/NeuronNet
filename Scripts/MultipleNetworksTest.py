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
    N = 500
    G = nx.fast_gnp_random_graph(N, p=0.2)

    '''synapseDict = {
        'I': ([0] * int(5 / dt)),
        'i': 0,  # iterator
        'i2': 0,  # iterator recovery
        'rp': 1 / dt,  # refractive period in dt
        'threshold': 10,
        'w': 1  # Mathematisch gewicht (v*w) Zie synapse (induces a 10mV * 0.01ms * 1000weight current = 100 )
    }'''



    simulator = enn.Simulator()

    nets = []
    for we in [4,3,2,5]:
        synapseDict = models.HodgkinAndHuxleyAxonSynapseSimple_Dictwrapper(we=we)
        network = enn.Network(models.HodgkinAndHuxleyNeuron,
                              models.default_Hodgkin_Huxley_neuron_dict,
                              models.HodgkinAndHuxleyAxonSynapseSimple,
                              synapseDict,
                              dt,
                              G,
                              True)

        id = simulator.addNetwork(network)
        rec = enn.Recorder(id, network.getNeuronIDs(), variables=['Vm', 'I'], withTime=True, diskMode=True,
                           toDiskDir='Network_Weight_%.2f' % we, overwrite=True)
        recID = simulator.addRecorder(rec)
        network.getNeuronByID(0)['Istim'] = 10
        nets.append(id)



    #sim

    simulator.simulate(60, poolSize=4)

    for id in nets:
        simulator.getNetwork(id).getNeuronByID(0)['Istim'] = 0

    simulator.simulate(250, poolSize=4)