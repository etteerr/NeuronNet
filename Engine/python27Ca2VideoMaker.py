'''
This file is the cv2 depended results visualizer
It will be a collection of functions that convert raw data into video data.

Require:
Python 2.7
openCV2     http://opencv.org/
PyGraphvis  http://pygraphviz.github.io
networkx    conda install networkx (or pip)     https://networkx.github.io/documentation/latest/index.html
'''
import networkx
import numpy as np
from numpy import exp



def generateNetworkCoordinates(G, layout='dot'):
    """
    generates network coordinates in the attribute 'pos'
    :param G:
    :Param layout: neato|dot|twopi|circo|fdp|nop
    :return:
    """
    ag = networkx.nx_agraph.to_agraph(G)
    ag.layout(prog=layout)
    ag.write(path='dot.dot')
    G = networkx.nx_agraph.from_agraph(ag)
    return G

def spikeEventsFromFile(file, mode='r'):
    """
    Loads spike event data from file. (CSV style)
    CSV must have per row: [id],event1, event2, ...
    :param file: full filename inc ext.
    :param mode: open(file, mode) file modus
    :return: returns data
    """
    import csv
    res = {}
    with open(file, mode) as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 2:
                key = row[0]
                data = row[1:len(row)]
                data = [float(x) for x in data]
                res[key] = data
    return res


def spikeEventsToCa2Trace(spikeEventsData, start=0, end=None, dt=0.01, spikeForm=None):
    '''
    Converts spike events to a [Ca2+] trace. Time stamps must be in ms.
    :param spikeEventsData: a Dict with neuron Id's as keys and vectors with timestamps.
    :param start: Start time
    :param end: end time
    :param dt: time resolution (independend of input)
    :param spikeForm: The spike form to be convolved over the spike data
    :return:
    '''
    tauOn = 0.01 #s
    ampFast = 7
    tauFast = 0.5
    ampSlow = 0
    tauSlow = 0
    if end is None:
        #Find max spike time
        tmp = []
        for (key, data) in spikeEventsData.items():
            tmp.append(max(data)) # we dont assume the last value is the max value
        end = max(tmp)
        del tmp

    old = np.seterr(under='ignore')
    if spikeForm is None:
        x = np.linspace(0, 10, np.ceil(10/dt)+1)
        spikeForm = (1 - (exp(-(x - 0) / tauOn))) * (ampFast * exp(-(x - 0) / tauFast))# + (ampSlow * exp(-(x - 0) / tauSlow))
        spikeForm[np.isnan(spikeForm)] = 0
    res = {}
    for (key, data) in spikeEventsData.items():
        tx = np.zeros(np.ceil((end-start)/dt)+1)
        for y in data:
            if y > start and y <= end:
                index = np.floor((y-start)/dt)
                tx[index] += 1
        tx = np.convolve(tx, spikeForm)
        res[key] = tx
    np.seterr(** old)
    return res


def addGaussNoise(data, sd=0.4):
    """
    Add gaussian noise to the given data (simple np.random.normal wrapper)
    Recursivly goes through dictionaries or list to find lists containing non list/dict things (numbers!)
    :param data: Can be a list or a dictionary with lists or a np.matrix or a np.ndarray
    If data is np.matrix, all items must be data.
    If a list contains lists with data, this is recognised. Mixed
    :param sd: Standart Deviation
    :return: data with noise
    """
    if isinstance(data, dict):
        for (i, value) in data.items():
            if not isinstance(data[i], list) and isinstance(data[i][0], (list, dict, np.matrix, np.ndarray)):
                data[i] = addGaussNoise(data[i], sd) #Recursion
            else:
                data[i] = list(data[i] + np.random.normal(0, sd, len(data[i])))
    elif isinstance(data, (list, np.ndarray)):
        if isinstance(data[0], (list, dict, np.matrix, np.ndarray)):
            for (i, v) in enumerate(data):
                if isinstance(data[i], (list, dict, np.matrix, np.ndarray)):
                    data[i] = addGaussNoise(data[1], sd)
                else:
                    data[i] = list(data[i] + np.random.normal(0, sd, len(data[i])))
        else:
            data = list(data + np.random.normal(0, sd, len(data)))
    elif isinstance(data, np.matrix):
        data += np.random.normal(0, sd, data.shape)
    else:
        raise TypeError('addGaussNoise: Unsupported type')
    return data





def renderCa2Video(data, networkStructure, output='video.avi', fps=120.0, size=(800,600), isColor=False):
    import networkx as nx
    import cv2
    G = nx.circular_layout(networkStructure, dim = 2, scale = 1)
    video = cv2.VideoWriter(output, cv2.VideoWriter_fourcc('M','J','P','G'), fps, size, isColor )
    if ~video.isOpened():
        print('Unable to open video file, are you missing "opencv_mmpeg.dll"?')
        return False
    # Create base image
    frame = np.zeros(size[1], size[0], 3)
