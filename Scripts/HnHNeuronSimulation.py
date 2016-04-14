'''
Author: Erwin Diepgrond
Copyright 2016 under GNU license
e.j.diepgrond@gmail.com

	This file is part of NeuroNet.

	NeuroNet is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, 
	or any later version.

	NeuroNet is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with NeuroNet.  If not, see <http://www.gnu.org/licenses/>.
'''

import networkx as nx
import pylab as pl

from Engine.ENN_Models import *
from Engine.ENNet import *

if __name__ == '__main__':

    # Use networkx library to create nodes and edges (neurons and synapses)
    # TODO: the possibility of nodes being networks
    N = 20  # Set network size
    nWorkers = 2  # used in sim.simulate(), Specifies the number of parallel networks to simulate (in this case none, we only have 1 network)
    verbose = True  # A lot of timing information
    dt = 0.01  # Simulation stepsize

    # Create a random networkx object (graphx) Others should be supported as well
    G = nx.fast_gnp_random_graph(N, p=0.4)

    # Show generated network
    nx.draw_networkx(G, with_labels=True)
    pl.show()

    # Create sim class
    sim = Simulator()

    # Create a neuron and synapse using the modelname
    neuron = HodgkinAndHuxleyNeuron
    synapse = erwinHandHsynapse
    gausNeuron = neuronGauss
    neuronDict = default_Hodgkin_Huxley_neuron_dict

    # Setting model depended information
    synapseDict = {
        'I': ([0] * int(5 / dt)),
        'i': 0,  # iterator
        'i2': 0,  # iterator recovery
        'rp': 1 / dt,  # refractive period in dt
        'threshold': 10,
        'w': 1  # Mathematisch gewicht (v*w) Zie synapse (induces a 10mV * 0.01ms * 1000weight current = 100 )
    }
    neuronDict['Imax'] = 2000

    gaussDict = {
        'mu': 30,
        'mean': 30,
        'Vm': 0,
        'I': 0,
        'u': 0
    }

    # Create network with neurons of specified type and behavior
    # And synapses of specified type and behavior
    # Every network can have its own time step (dt)
    network = Network(networkx=G, neuronFun=neuron, neuronDict=neuronDict, synapseFun=synapse, synapseDict=synapseDict,
                      dt=dt, verbose=verbose)

    # Add one gaussian generator 'neuron' and link it to neuronId 0
    neuron_id = network.addNeuron(neuronDict=gaussDict, neuronFun=gausNeuron)
    network.connect(sourceId=neuron_id, destinationId=0)  # neuron id --> neuron 0

    # Add neuron stimulation to neuron id 3
    network.getNeuronByID(3)['Istim'] = 10

    # You can also remove a neuron from the network.
    # Effectivly removing all synapses as well
    # network.deleteNeuron(id=4)

    # you can get all neuron ids!
    nIDs = network.getNeuronIDs()  # All IDs from network

    # Add network - id1 now contains the id of the network in the simulator
    id1 = sim.addNetwork(network)

    # The same network, only tunneled through the simulator (all functions are availible, its just a reference to the network)
    id2 = sim.createNetwork(G, neuronFun=neuron, neuronDict=neuronDict, synapseFun=synapse, synapseDict=synapseDict,
                            dt=dt, verbose=verbose)  # returns network ID
    neuron_id2 = sim.getNetwork(networkId=id2).addNeuron(gausNeuron, gaussDict)
    sim.getNetwork(id2).connect(neuron_id2, 1)  # neuron_id2 --> neuron 1

    # create recorders
    m1 = Recorder(networkId=id1, neuronIds=range(N), variables=['Vm', 'I'],
                  withTime=True)  # withTime gives it a timeline variable.
    m2 = Recorder(networkId=id2, neuronIds=range(N), variables=['Vm', 'I'], withTime=True)  # m1 already has a timeline

    # Add recorders to network
    m1id = sim.addRecorder(recorder=m1)
    m2id = sim.addRecorder(recorder=m2)

    # You can use m1 variable (since its a reference)
    # But you can recall  one with the ID as well
    m1 = sim.getRecorder(recorderId=m1id)

    # start simulation - Note: ignoreWarnings not implemented yet
    sim.simulate(
        duration_ms=200)  # 100ms  ignoreWarnings (default) = false (will give warning if you change variables after simulation
    # Note that we also dont give a poolSize, for 150 ms, a pool is a bit overkill
    # you can change neurons and variables here and simulate again. No matter! (though you will get warnings) (no warnings yet)

    sim.getNetwork(id1).getNeuronByID(3)['Istim'] = 0

    # Sim second round
    t = clock()
    # Note: When simulating with pools, the reference to the recorders is lost!
    sim.simulate(duration_ms=1800, poolSize=nWorkers)
    print(clock() - t)

    # Get the recorders
    m1 = sim.getRecorder(m1id)
    m2 = sim.getRecorder(m2id)

    #m1.save('neuronNetData')
    m1.saveToXML('neuronNetData')
    m1.getSpikeEventtimes(var='Vm', neurons=None, file='spikeEvents')

    pl.figure(1)
    for i in m1['Vm'].keys():
        if not len(m1['Vm'][i]) < 1:  # TODO: Fix missing neuron data for deleted neurons.
            pl.subplot(2, 1, 1)
            pl.plot(m1.timeline, m1['Vm'][i])
            pl.hold(True)
            pl.subplot(212)
            pl.plot(m1.timeline, m1['I'][i])
            pl.hold(True)
    pl.figure(2)
    for i in m2['Vm'].keys():
        if not len(m2['Vm'][i]) < 1:
            pl.subplot(2, 1, 1)
            pl.plot(m2.timeline, m2['Vm'][i])
            pl.hold(True)
            pl.subplot(212)
            pl.plot(m2.timeline, m2['I'][i])
            pl.hold(True)
    pl.show()
