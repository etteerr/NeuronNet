#python 3.x (pylab needed)
import Engine.ENNet as enn
import Engine.ENN_Models as models
import numpy as np
import pickle
import networkx as nx

# create network
percentageExt = 70
N = 200
avgConnPerNeuron = 4 # Must be smaller than N
avgWeight = 0
sdWeight = 10
synapseNoiseSd = 0.5
syndelay = 5

dt=0.05

net = enn.Network(neuronFun=models.HodgkinAndHuxleyNeuron,
                  neuronDict=models.default_Hodgkin_Huxley_neuron_dict,
                  synapseFun=models.HodgkinAndHuxleyAxonSynapseSimple,
                  synapseDict=models.HodgkinAndHuxleyAxonSynapseSimple_Dictwrapper(dt, delay=syndelay),
                  dt=dt, verbose=True, etaInterval=10)

# Add neurons
ext = int(np.floor(float(N) * (float(percentageExt)/100.0)))
ihb = int(N-ext)
extid = []
ihbid = []
for _ in range(0, ext):
    extid.append(net.addNeuron())

for __ in range(0, ihb):
    ihbid.append(net.addNeuron())

chance = float(avgConnPerNeuron) / float(N)
for i in extid:
    for j in net.getNeuronIDs():
        if np.random.rand() <= chance:
            net.connect(i,j,
                        settingsDict={
                            'we':np.abs(np.random.normal(avgWeight, sdWeight)),
                            'sd':synapseNoiseSd
                        }
                        )

for i in ihbid:
    for j in net.getNeuronIDs():
        if np.random.rand() <= chance:
            net.connect(i,j,
                        settingsDict={
                            'wi':np.abs(np.random.normal(avgWeight, sdWeight)),
                            'sd':synapseNoiseSd
                        }
                        )

# Remove all not-connected neurons
neurons = net.getNeuronIDs()
for synid in net.getConnectionIDs():
    conn = net.getConnectionByID(synid)
    neurons = [x for x in neurons if x != conn['_destin'] and x != conn['_source']]

for i in neurons:
    net.deleteNeuron(i)
print('Neurons: %i' % (N-len(neurons)))
print('Connection: %i' % (len(net._synapses)))

# Add random gauss generator
a = list(net.getNeuronIDs())
#for i in a:
#    id = net.addNeuron(models.neuronGauss, { 'mean':5, 'mu':5})
#    net.connect(id, i, synapseFun=models.directConnect, synapseDict={})

# Save network in DiGraph
G = net.getNetworkX('wi')
with open('networkStruct.dat', 'wb') as f:
    pickle.dump(G,f)

# Create recorder
rec = enn.Recorder(0, a,withTime=True, variables=['Vm'], diskMode=True, toDiskDir='recurrentNet', overwrite=True, dt=dt)
#rec = enn.Recorder(0, range(0,100),withTime=True, variables=['Vm', 'I'], diskMode=True, toDiskDir='Scripts\\recurrentNet', overwrite=False, dt=0.05)
# Start simulating away!
sim = enn.Simulator()
sim.addNetwork(net)
sim.addRecorder(rec)
sim.getNetwork(0).getNeuronByID(list(net.getNeuronIDs())[0])['Istim'] = 10
sim.getNetwork(0).getNeuronByID(list(net.getNeuronIDs())[1])['Istim'] = 10
sim.simulate(50)
sim.getNetwork(0).getNeuronByID(list(net.getNeuronIDs())[0])['Istim'] = 0
sim.getNetwork(0).getNeuronByID(list(net.getNeuronIDs())[1])['Istim'] = 0
sim.simulate(5000)

# PLot
import pylab as pl
nx.draw_networkx(G)

pl.figure(2)
for i in rec['Vm'].keys():
    try:
        pl.plot(net._timeline, rec['Vm'][i].getList())
    except:
        pass

#pl.figure(3)
#for i in rec['Vm'].keys():
#    pl.plot(net._timeline, rec['I'][i].getList())

pl.show()

dict = rec.getSpikeEventtimes()