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





def renderCa2Video(data, networkStructure, output='video.avi', fps=120.0, size=(800,600), radius=4, maxrgb=[255, 255, 255], dt=0.01, mode='mean'):
    """
    Renders a video based on the data and the network structure
    :param data: A dictionary with the data. Keys must correspond to the keys of the networkx (networkStructure)
    :param networkStructure: The networkx object
    :param output: Name of the output
    :param fps: Frames per seconds. Please choose a value that results in a rounded answer for frametime/dt where frametime is 1/fps
    :param size: video size
    :param radius: size of the neurons in pixels
    :param maxrgb: maximum value of RGB representation of the data
    :param dt: time step size
    :param mode: how the inter frame data is used, modes: 'mean' | 'sum'
    :return:
    """
    #dt in ms
    import networkx as nx
    import cv2
    isColor = True
    G = nx.circular_layout(networkStructure, dim = 2, scale = 1)
    video = cv2.VideoWriter(output, cv2.VideoWriter_fourcc('M','J','P','G'), fps, size, isColor )
    if not video.isOpened():
        print('Unable to open video file, are you missing "opencv_mmpeg.dll"?')
        return False

    # Reformat data and assign positions
    positions = []
    dataarray = []
    length = len(data[data.keys()[0]])
    for key in data.keys():
        (x,y) = G[key]
        positions.append( (int(np.round(((x+1)/2) * size[0])), int(np.round(((y+1)/2) * size[1]))) )
        dataarray.append(data[key])
        if not length == len(data[key]):
            raise AssertionError('Not all data lengths are equal')

    # Create base image
    frame = np.zeros((size[1], size[0], 3), np.uint8)

    # Find max value
    maxy = np.array(dataarray).max()

    # Calculate frame bin size
    dt = dt / 1000
    frametime = 1/fps
    stepsPerFrame = int(np.ceil(frametime/dt))
    print('Advised FPS: %i' % (.10 / dt) )
    print('Used FPS: %i' % (fps))
    print('Total samples: %i' % length)
    print('data per frame: %.2f\nRounded to: %i' % ((frametime/dt),int(np.ceil(frametime/dt))))
    print('Total video time: %.2fs' % ((length/stepsPerFrame)/fps))

    assert((frametime/dt) >= 1)


    prev = 0
    maxrgb = np.array(maxrgb)

    if mode is 'mean':
        modefun = np.mean
    elif mode is 'sum':
        modefun = np.sum

    # Frame renderer
    for i in range(stepsPerFrame-1,length-1,stepsPerFrame):
        for n in range(0,len(positions)):
            value = modefun(dataarray[n][prev:i]) / maxy
            value = maxrgb * value
            cv2.circle(frame, positions[n], radius, tuple(np.round(value).astype(int)), -1)
        video.write(frame)
        prev = i + 1

    video.release()
    print('Done!')




