import Engine.ENNet as enn
import Engine.ENN_Models as ennmod
import Engine.python27Ca2VideoMaker as ca2


def spiketraintrace(nspikes, frequency, pulsewidth, current, trace_dt=10, net_dt=0.01, padding=100):
    '''
    nspikes = 1
    frequency = 100  # hz
    pulsewidth = 1  # ms
    current = 100
    :returns: catrace
    '''
    sim = enn.Simulator()

    # Create empty network
    net = enn.Network(ennmod.HodgkinAndHuxleyNeuron,
                      ennmod.default_Hodgkin_Huxley_neuron_dict,
                      ennmod.HodgkinAndHuxleyAxonSynapseSimple,
                      ennmod.HodgkinAndHuxleyAxonSynapseSimple_Dictwrapper(),
                      dt=net_dt, verbose=False)
    # add one neuron
    nid = net.addNeuron()

    # Add to simulator
    netid = sim.addNetwork(net)

    # attach recorder
    rec = enn.Recorder(netid, [nid], ['Vm', 'Istim'], withTime=True)
    sim.addRecorder(rec)

    # simulate 25 ms of no activity to ensure rest potential
    sim.simulate(padding)

    # injection pulses


    for spike in range(0, nspikes):
        sim.getNetwork(netid).getNeuronByID(nid)['Istim'] = current
        sim.simulate(pulsewidth)
        sim.getNetwork(netid).getNeuronByID(nid)['Istim'] = 0
        sim.simulate((1000 / frequency) - pulsewidth)

    # Finalize
    sim.simulate(padding)

    # Convert data to ca2+ trace

    spikeEvents = rec.getSpikeEventtimes()

    tauOn = 1
    ampFast = 17
    tauFast = 5
    trace = ca2.spikeEventsToCa2Trace(spikeEvents, end=sim.getNetwork(netid)._time+1000, dt=trace_dt, spikeLengthSeconds=40, tauOn=tauOn, ampFast=ampFast, tauFast=tauFast)
    trace = ca2.addGaussNoise(trace, sd=0.4)
    return list(trace[0])