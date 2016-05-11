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

import numpy
from numpy import exp
numpy.seterr(all='raise')
##########################################
#### Simple neuron & synapse          ####
##########################################

################ Neuron ################
def neuronIzh(neuronDict):
    #dv/dt = 0.04v^2+5v+140-u+I
    def dvdt(v,u,I): return 0.04 * v * v + 5 * v + 140 + I - u

    #du/dt = a*(b*v - u)
    def dudt(v,u,a,b): return a * (b * v - u)

    dt = neuronDict['dt']
    v = neuronDict['v']
    u = neuronDict['u']
    I = neuronDict['I']
    a = neuronDict['a']
    b = neuronDict['b']
    c = neuronDict['c']
    d = neuronDict['d']
    neuronDict['v'] = v + dt * dvdt(v, u, I)
    neuronDict['u'] = u + dt * dudt(v, u, a, b)
    if neuronDict['v'] >= 30:
        neuronDict['v'] = c
        neuronDict['u'] = u + d
    neuronDict['I'] = 0 # is set by synapse! (addition)
    return neuronDict

def neuronGauss(neuronDict):
    neuronDict['Vm'] = numpy.random.normal(neuronDict['mean'], neuronDict['mu'])
    return neuronDict

################ Synapse ################
def erwinSynapse(synapseDict, source, dest):
    #I,i,w,source,dest = Synapse
    dest['I'] += synapseDict['I'][synapseDict['i']] ## Add it!!, dont overwrite other synapses!
    synapseDict['I'][synapseDict['i']] = 0
    if source['v'] > synapseDict['threshold']:
        synapseDict['I'][synapseDict['i']] += source['v'] * synapseDict['w']
    synapseDict['i'] = divmod(synapseDict['i'] + 1, len(synapseDict['I']))[1]
    return [synapseDict, source, dest]


##########################################
#### Hodgkin & Huxley                 ####
##########################################
default_Hodgkin_Huxley_neuron_dict = {
    'Vm'   : -65,   # The membrane Voltage
    'Eq'    : -65,# The resting voltage of the neuron
    'INa'   : 0,    # The natrium current
    'IK'    : 0,    # potassium current
    'Il'    : 0,    # The leakage current
    'gNa'  : 120,  # conductance constant for Na (mS)
    'gK'   : 36,   # conductance constant for K  (mS)
    'gl'   : 0.3,  # conductance constant for leakage (mS)
    'ENa'   : 115,  # resting potential Na
    'EK'    : -12,  # resting potential K
    'El'    : 10.6, # resting potential Leakage
    'Cm'    : 1,    # Membrane capacitance
    'n'     : 0.3,  # n-value
    'm'     : 0.5,  # m-value
    'h'     : 0.5, # h-value
    'dt'    : 0,    # Set by simulator
    'I'     : 0,    # Input current from synapse (set by synapse update: HodgkinAndHuxleyAxonSynapse() )
    'Imax'  : 200,   # max input current from synapse (overflow protection
    'Istim' : 0     # Artificial input current (set between simulations?)
}
################ Neuron ################
# Outside definition seems to be faster than nested functions
def alpha_n(Vm, Eq): return (0.01*(-(Vm+Eq)+10))/(exp((-(Vm+Eq)+10)/10)-1)
def alpha_m(Vm, Eq): return (0.1*(-(Vm+Eq)+25))/(exp((-(Vm+Eq)+25)/10)-1)
def alpha_h(Vm, Eq): return 0.07  * exp(-(Vm+Eq)/20)
def beta_n(Vm, Eq) : return 0.125 * exp(-(Vm+Eq)/80)
def beta_m(Vm, Eq) : return 4     * exp(-(Vm+Eq)/18)
def beta_h(Vm, Eq) : return 1/( exp((-(Vm+Eq)+30)/10)+1)
#delta values for n, m and h
def delta_n(Vm, n, Eq): return alpha_n(Vm, Eq) * (1 - n) - beta_n(Vm, Eq) * n
def delta_m(Vm, m, Eq): return alpha_m(Vm, Eq) * (1 - m) - beta_m(Vm, Eq) * m
def delta_h(Vm, h, Eq): return alpha_h(Vm, Eq) * (1 - h) - beta_h(Vm, Eq) * h
def HodgkinAndHuxleyNeuron(neuronDict):
    """
    This function will simulate a neuron with the hogdkin & huxley formula.
    It will simulate: connection -->> Dendrite[n] -->> soma -->> connection
    Where connection is the HodgkinAndHuxleyAxonSynapse or other 'synapse'
    :param neuronDict: All the properties of the neuron
    :return: changed neuronDict
    """
    Eq = -neuronDict['Eq'] #Setting the inverted Eq as resting potential of membrane
    #Functions
        #Now found outside

    #Lets go!
    d = neuronDict
    if d['I'] > 10: d['I'] = d['Imax']
    # Calculating currents
    #IK = gK n^4 (Vm - EK)
    d['IK'] =  d['gK']  * (d['n']**4) * ((d['Vm']+Eq) - d['EK'])
    #INa = gNa m^3 h (Vm - ENa)
    d['INa'] = d['gNa'] * (d['m']**3) * d['h'] * ((d['Vm']+Eq) - d['ENa'])
    #Il = gl (Vm - El)
    d['Il'] =  d['gl']  * ((d['Vm']+Eq) - d['El'])

    # Calculate voltage step
    d['Vm'] += d['dt'] * (1/d['Cm']) * ( (d['I'] + d['Istim']) - d['IK'] - d['INa'] - d['Il'] )

    # Calculate reaction of le ion channels
    d['m'] += d['dt'] *  delta_m(d['Vm'],d['m'], Eq)
    d['n'] += d['dt'] *  delta_n(d['Vm'],d['n'], Eq)
    d['h'] += d['dt'] *  delta_h(d['Vm'],d['h'], Eq)
    #We processed the input, rest it
    d['I'] = 0
    #Return the d!
    return d


################ Synapse ###############
def HodgkinAndHuxleyAxonSynapse(synapseDict, source, dest):
    pass

def erwinHandHsynapse(synapseDict, source, dest):
    #I,i,w,source,dest = Synapse
    dest['I'] += synapseDict['I'][synapseDict['i']] ## Add it!!, dont overwrite other synapses!

    synapseDict['I'][synapseDict['i']] = 0

    if source['Vm'] > synapseDict['threshold'] and synapseDict['i2'] <= 0:
        synapseDict['I'][synapseDict['i']] += source['Vm'] * synapseDict['w']/source['dt']
        synapseDict['i2'] = synapseDict['rp']#refractive period counter
    elif synapseDict['i2'] > 0:
        synapseDict['i2']-=1

    synapseDict['i'] = divmod(synapseDict['i'] + 1, len(synapseDict['I']))[1]
    return [synapseDict, source, dest]
# TODO: Compartment hodgkin huxley adaptation