from time import clock
import Engine.ENN_Models as M

def sim(ds,time=100):
    times = int(time/ds[0]['dt'])
    t = clock()
    for d in ds:
        for i in range(times):
            d = M.HodgkinAndHuxleyNeuron(d)
    print(clock()-t)
ds = []
for i in range(10):
    d = M.default_Hodgkin_Huxley_neuron_dict
    d['dt'] = 0.01
    ds.append(d)
sim(ds,1000)
