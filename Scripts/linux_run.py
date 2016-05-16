#!/usr/bin/python
import sys
if not len(sys.argv) == 1:
    print('Please give the path containing Engine as argument: python Scrips/linux_run.py pwd')
    exit()
sys.path.append(sys.argv[0])

import networkx as nx
import Engine.ENNet as enn
import Engine.ENN_Models as models


if __name__ == '__main__':
    dt = 0.05
    N = 500
    G = nx.fast_gnp_random_graph(N, p=0.4)


    synapseDict = models.HodgkinAndHuxleyAxonSynapseSimple_Dictwrapper(we=0.5)

    simulator = enn.Simulator()

    network = enn.Network(models.HodgkinAndHuxleyNeuron,
                          models.default_Hodgkin_Huxley_neuron_dict,
                          models.HodgkinAndHuxleyAxonSynapseSimple,
                          synapseDict,
                          dt,
                          G,
                          True)

    for i in network.getNeuronIDs():
        network.getNeuronByID(i)['Istim'] = 10

    id = simulator.addNetwork(network)

    # Add recorder
    rec = enn.Recorder(id, network.getNeuronIDs(),variables=['Vm', 'I'], withTime=True, diskMode=True, toDiskDir='TestDir', overwrite=True)

    recID = simulator.addRecorder(rec)

    #sim

    simulator.simulate(500)

    for i in network.getNeuronIDs():
        simulator.getNetwork(id).getNeuronByID(i)['Istim'] = 0

    simulator.simulate(2000)

