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



def generateNetworkCoordinates(G, forRadius=4, forSize=(800,600)):#, layout='dot'):
    '''
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
    '''
    import networkx as nx
    if forSize[0] > forSize[1]:
        scale = 1.0-(float(forRadius)/float(forSize[1]))
    else:
        scale = 1.0-(float(forRadius)/float(forSize[0]))

    try:
        G = nx.random_layout(G, dim=2, scale=scale, center=(0,0))
    except TypeError: # Fixes the problem of having another version of nx
        G = nx.random_layout(G, dim=2)
        for (key,(x,y)) in G.items():
            x = 2 * x - 1
            y = 2 * y - 1
            G[key] = [x,y]

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


def addGaussNoise(data, sd=0.4, chunksize=1000):
    """
    Add gaussian noise to the given data (simple np.random.normal wrapper)
    Recursivly goes through dictionaries or list to find lists containing non list/dict things (numbers!)
    :param data: Can be a list or a dictionary with lists or a np.matrix or a np.ndarray
    If data is np.matrix, all items must be data.
    If a list contains lists with data, this is recognised. Mixed
    :param sd: Standart Deviation
    :return: data with noise
    """
    if isinstance(data, dict): # If dict, recurse every entry
        for (i, value) in data.items():
                data[i] = addGaussNoise(data[i], sd, chunksize) #Recursion
    elif isinstance(data, (list, np.ndarray)): #If its a list or array
        if isinstance(data[0], (list, dict, np.matrix, np.ndarray)): #And contains lists or arrays
            for (i, v) in enumerate(data): # For every entry
                if isinstance(data[i], (list, dict, np.matrix, np.ndarray)): # If its a list, array or dict
                    data[i] = addGaussNoise(data[1], sd, chunksize)  # Recurse
                else:                                           #Else
                    data[i] = data[i] + np.random.normal(0, sd) # its a number, add sd
        else:
            offset = 0
            while True:
                if offset + chunksize < len(data):
                    data[offset:offset+chunksize] += np.random.normal(0,sd,chunksize)
                    offset += chunksize
                else:
                    data[offset:len(data)] += np.random.normal(0,sd,len(data)-offset)
                    break
    elif isinstance(data, np.matrix):
        data += np.random.normal(0, sd, data.shape)
    else:
        raise TypeError('addGaussNoise: Unsupported type')
    return data



def extractPosDataFromNetworkx(G):
    pass

def renderCa2Video(data, netpos, output='video.avi', recfps=120.0, playfps=24.0, size=(800,600), radius=4, maxrgb=[255, 255, 255], dt=0.01, mode='mean', noisemax=10, noiserep=256):
    """
    Renders a video based on the data and the network structure
    :param data: A dictionary with the data. Keys must correspond to the keys of the networkx (networkStructure)
    :param netpos: The locations of every neurons: dict { neuronID: [x,y] } where x and y are doubles between -1 and 1
    :param output: Name of the output
    :param recfps: Frames per seconds. Please choose a value that results in a rounded answer for frametime/dt where frametime is 1/fps
    :param 24.0: The fps for playback.
    :param size: video size
    :param radius: size of the neurons in pixels
    :param maxrgb: maximum value of RGB representation of the data
    :param dt: time step size
    :param mode: how the inter frame data is used, modes: 'mean' | 'sum' | 'point' | 'highest'
     mean: Average over all interframe samples
     sum:  Sum over all interframe samples (may cause constant max value due to max limit)
     point:All interframe samples are dumped except for the last one
     highest: Highest value is taken
     :param noisemax: Maximum value ( 0-255) for noise (all channels)
     :param noiserep: x-frames of noise repeated (for performance)
    :return:
    """
    #dt in ms
    import networkx as nx
    import cv2
    isColor = True

    video = cv2.VideoWriter(output, cv2.VideoWriter_fourcc('M','J','P','G'), playfps, size, isColor )
    if not video.isOpened():
        print('Unable to open video file, are you missing "opencv_mmpeg.dll"?')
        return False

    # Reformat data and assign positions
    positions = []
    dataarray = []
    maxarray = []
    length = len(data[data.keys()[0]])
    for key in data.keys():
        (x,y) = netpos[key]
        positions.append( (int(np.round(((np.double(x)+1.0)/2.0) * np.double(size[0]))), int(np.round(((np.double(y)+1.0)/2.0) * np.double(size[1])))) )
        dataarray.append(data[key])
        maxarray.append(np.array(data[key]).max())
        if not length == len(data[key]):
            raise AssertionError('Not all data lengths are equal')

    # Create base image
    frame = np.zeros((size[1], size[0], 3), np.uint8)

    # Find max value
    maxy = np.array(maxarray).max()

    # Calculate frame bin size
    dt = dt / 1000
    frametime = 1/recfps
    stepsPerFrame = int(np.ceil(frametime/dt))
    print('Advised FPS: %i' % (.10 / dt) )
    print('Used FPS: %i' % (recfps))
    print('Total samples: %i' % length)
    print('data per frame: %.2f\nRounded to: %i' % ((frametime/dt),int(np.ceil(frametime/dt))))
    print('Total video time: %.2fs' % ((length/stepsPerFrame)/recfps))
    print('Total playback time: %.2fs' % ((length/stepsPerFrame)/playfps))

    assert((frametime/dt) >= 1)


    prev = 0
    maxrgb = np.array(maxrgb)

    if mode is 'mean':
        modefun = np.mean
    elif mode is 'sum':
        modefun = np.sum
    elif mode is 'point':
        modefun = lastElm
    elif mode is 'highest':
        modefun = np.max

    # Pre calculate noise
    nnframes = int(noiserep)
    noiseframes = []
    for i in range(0, nnframes):
        uninoise = np.uint8(np.random.random_integers(0, noisemax, (size[1], size[0])))
        nframe = np.zeros((size[1], size[0], 3), np.uint8)
        nframe[:, :, 0] += uninoise
        nframe[:, :, 1] += uninoise
        nframe[:, :, 2] += uninoise
        noiseframes.append(nframe)

    # Frame renderer
    for i in range(stepsPerFrame-1,length-1,stepsPerFrame):
        for n in range(0,len(positions)):
            value = modefun(dataarray[n][prev:i]) / maxy
            value = maxrgb * value
            cv2.circle(frame, positions[n], radius, tuple(np.round(value).astype(int)), -1)
        # Add noise
        frame += noiseframes[np.mod(i,nnframes)]
        cv2.blur(frame, (5,5))
        video.write(frame)
        frame = np.zeros((size[1], size[0], 3), np.uint8)
        prev = i + 1

    video.release()
    print('Done!')

def lastElm(data):
    return data[-1]



