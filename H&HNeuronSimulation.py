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

from Engine.ENNet import *
import pylab as pl
import networkx as nx
from Engine.ENN_Models import *

if __name__ == '__main__':
    # Use networkx library to create nodes and edges (neurons and synapses)
    # TODO: the possibility of nodes being networks
    N = 20 # Set network size
    nWorkers = 3 # Spawned processes by simulator class
    verbose = False
    G = nx.fast_gnp_random_graph(N, p=.6)

    nx.draw_networkx(G,with_labels=True)
    pl.show()

    # Set time step size
    dt = 0.01

    # Create sim class
    sim = Simulator()


    # Create a neuron and synapse using the modelname
    neuron = HodgkinAndHuxleyNeuron
    synapse = erwinHandHsynapse
    gausNeuron = neuronGauss
    neuronDict = default_Hodgkin_Huxley_neuron_dict

    synapseDict = {
        'I':([0] * int(5 / dt)),
        'i':0, # iterator
        'i2': 0, #iterator recovery
        'rp':1/dt, #refractive period in dt
        'threshold': 10,
        'w': 1#Mathematisch gewicht (v*w) Zie synapse (induces a 10mV * 0.01ms * 1000weight current = 100 )
    }
    neuronDict['Imax'] = 2000

    gaussDict = {
        'mu': 30,
        'mean': 30,
        'Vm': 0,
        'I':0,
        'u':0
    }

    # Create network with neurons of specified type and behavior
    # And synapses of specified type and behavior
    # Every network can have its own time step (dt)
    network = Network(networkx=G, neuronFun=neuron, neuronDict=neuronDict, synapseFun=synapse, synapseDict=synapseDict,poolSize=nWorkers, dt=dt,verbose=verbose)

    # Add one gaussian generator 'neuron' and link it to neuronId 0
    #neuron_id = network.addNeuron(neuronDict=gaussDict,neuronFun=gausNeuron)
    #network.connect(sourceId = neuron_id , destinationId = 0)  # neuron id --> neuron 0

    # Add neuron stimulation
    network.getNeuronByID(0)['Istim'] = 10

    # You can also remove a neuron from the network.
    # Effectivly removing all synapses as well
    #network.deleteNeuron(id=3)

    # you can get all neuron ids!
    nIDs = network.getNeuronIDs() # All IDs from network

    # Add network
    id1 = sim.addNetwork(network)

    # The same network, only tunneled through the simulator (all functions are availible, its just a reference to the network)
    #id2 = sim.createNetwork(G,neuronClass = neuron,synapseClass = synapse,dt=dt) #returns network ID
    #neuron_id2 = sim.getNetwork(networkId = id2).addNeuron(gausNeuron)
    #sim.getNetwork(id2).connect(neuron_id2,1) # neuron_id2 --> neuron 1


    # create recorders
    m1 = Recorder(networkId = id1, neuronIds=range(N), variables=['Vm', 'I'],withTime=True) # withTime gives it a timeline variable.
    #m2 = Recorder(networkId = id2, neuronIds=range(0,N), variables=['v', 'I', 'u']) #m1 already has a timeline

    # Add recorders to network
    m1id = sim.addRecorder(recorder=m1)
    #m2id = sim.addRecorder(recorder=m2)

    # You can use m1 variable (since its a reference)
    # But you can recall  one with the ID as well
    #m1 = sim.getRecorder(recorderId = m1id)

    #start simulation
    sim.simulate(duration_ms = 15) #100ms  ignoreWarnings (default) = false (will give warning if you change variables after simulation
    # you can change neurons and variables here and simulate again. No matter! (though you will get warnings) (no warnings yet)

    sim.getNetwork(id1).getNeuronByID(0)['Istim'] = 0

    # Sim second round
    sim.simulate(duration_ms= 100)

    for i in m1['Vm'].keys():
        pl.subplot(2,1,1)
        pl.plot(m1.timeline,m1['Vm'][i])
        pl.hold(True)
        pl.subplot(212)
        pl.plot(m1.timeline,m1['I'][i])
        pl.hold(True)
    pl.show()