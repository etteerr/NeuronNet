from time import clock
import numpy as np
import multiprocessing as mp
from Engine.ENNet import Network, Recorder, Simulator
from Engine.ENN_Models import *
import networkx as nx

# ############ Globals ############
# mb = 1e6
# kb = 1e3
# gb = 1e9
# elem = 8  # byte
#
#
# def calc(x):
#     return x * x
#
#
#
# def calcPipe(pipe):
#     while True:
#         x = pipe.recv()
#         if x is None:
#             break
#         pipe.send(x * x)
#
# def simNetwork(network,duration, rec):
#     network.simulate(duration, rec)
#    return network

if __name__ == '__main__':

    # Use networkx library to create nodes and edges (neurons and synapses)
    # TODO: the possibility of nodes being networks
    N = 100 # Set network size
    nWorkers = 4# Spawned processes by simulator class(None or < 1 is local (no forks))
    verbose = False
    G = nx.fast_gnp_random_graph(N, p=1)

    #nx.draw_networkx(G,with_labels=True)
    #pl.show()

    # Set time step size
    duration = 100
    dt = 0.01


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
    network1 = Network(networkx=G, neuronFun=neuron, neuronDict=neuronDict, synapseFun=synapse, synapseDict=synapseDict, dt=dt,
                       debugVerbose=verbose)
    network2 = Network(networkx=G, neuronFun=neuron, neuronDict=neuronDict, synapseFun=synapse, synapseDict=synapseDict, dt=dt,
                       debugVerbose=verbose)
    network3 = Network(networkx=G, neuronFun=neuron, neuronDict=neuronDict, synapseFun=synapse, synapseDict=synapseDict, dt=dt,
                       debugVerbose=verbose)
    network4 = Network(networkx=G, neuronFun=neuron, neuronDict=neuronDict, synapseFun=synapse, synapseDict=synapseDict, dt=dt,
                       debugVerbose=verbose)

    network1.getNeuronByID(0)['Istim'] = 0
    network2.getNeuronByID(0)['Istim'] = 1
    network3.getNeuronByID(0)['Istim'] = 10
    network4.getNeuronByID(0)['Istim'] = 100

    sim = Simulator()

    id1 = sim.addNetwork(network1)
    id2 = sim.addNetwork(network2)
    id3 = sim.addNetwork(network3)
    id4 = sim.addNetwork(network4)

    m1 = Recorder(networkId = id1, neuronIds=range(N), variables=['Vm', 'I'],withTime=True) # withTime gives it a timeline variable.
    m2 = Recorder(networkId = id2, neuronIds=range(N), variables=['Vm', 'I'],withTime=True) # withTime gives it a timeline variable.
    m3 = Recorder(networkId = id3, neuronIds=range(N), variables=['Vm', 'I'],withTime=True) # withTime gives it a timeline variable.
    m4 = Recorder(networkId = id4, neuronIds=range(N), variables=['Vm', 'I'],withTime=True) # withTime gives it a timeline variable.

    sim.addRecorder(m1)
    sim.addRecorder(m2)
    sim.addRecorder(m3)
    sim.addRecorder(m4)

    sim.simulate(duration,poolSize=nWorkers)

    # pool = mp.Pool(processes=4)
    # simtime = 1000
    # results1 = pool.apply_async(simNetwork,(network1,simtime,{'0':m1}))
    # results2 = pool.apply_async(simNetwork,(network2,simtime,{'1':m2}))
    # results3 = pool.apply_async(simNetwork,(network3,simtime,{'2':m3}))
    # results4 = pool.apply_async(simNetwork,(network4,simtime,{'3':m4}))
    #
    # network1 = results1.get()
    # network2 = results2.get()
    # network3 = results3.get()
    # network4 = results4.get()

    # ########## Settings #########
    # # 8 bytes per element
    # # 1e6 MegaByte = 1 Byte
    # arraySize = 0.1 * gb  # in mb, kb or gb (number * unit)
    #
    # print('Generating array...')
    # elems = np.ceil(arraySize / elem)
    # a = np.linspace(0, 1000, elems)
    # realSize = a.nbytes
    # print('Setpoint: %.5fMB\nreal: %.5fMB' % (arraySize / mb, realSize / mb))
    #
    # print('Test 1: Numpy local')
    # t = clock()
    # for i in range(len(a)):
    #     a[i] = calc(a[i])
    # time = clock() - t
    # del a
    # print('Test 1: %.5f' % time)
    #
    # # print('Test 2: Process')
    # # p1, p2 = mp.Pipe(duplex=True)
    # # p12, p22 = mp.Pipe(duplex=True)
    # # p13, p23 = mp.Pipe(duplex=True)
    # # p14, p24 = mp.Pipe(duplex=True)
    # # proc = mp.Process(target=calcPipe,args=(p2,))
    # # proc2 = mp.Process(target=calcPipe,args=(p22,))
    # # proc3 = mp.Process(target=calcPipe,args=(p23,))
    # # proc4 = mp.Process(target=calcPipe,args=(p24,))
    # # proc.start()
    # # proc2.start()
    # # proc3.start()
    # # proc4.start()
    # # a = np.linspace(0, 1000, elems)
    # # t = clock()
    # # for i in range(0, len(a), 4):
    # #     p1.send(a[i])
    # #     p12.send(a[i+1])
    # #     p13.send(a[i+2])
    # #     p14.send(a[i+3])
    # #     a[i]=p1.recv()
    # #     a[i+1]=p12.recv()
    # #     a[i+2]=p13.recv()
    # #     a[i+3]=p14.recv()
    # # time = clock() - t
    # # print('Test 2: %.5f' % time)
    # # p1.send(None)
    # # p12.send(None)
    # # p13.send(None)
    # # p14.send(None)
    # # proc.join()
    # # proc2.join()
    # # proc3.join()
    # # proc4.join()
    #
    # print('Test 3: Process')
    # pool = mp.Pool()
    # a = np.linspace(0, 1000, elems)
    # t = clock()
    # b = pool.map(calc,a)
    # time = clock() - t
    # pool.close()
    # pool.join()
    # print('Test 3: %.5f' % time)
    # print(a[1:5])
    # print(b[1:5])