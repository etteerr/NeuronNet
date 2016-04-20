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
#import pylab as pl
import pygraphviz
import numpy as np
from numpy import exp
import copy
import sys



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
            key = row[0]
            data = row[1:len(row)]
            data = [float(x) for x in data]
            res[key] = data
    return res


def spikeEventsToCa2Trace(spikeEventsData, start=0, end=None, dt=0.01):
    '''
    Converts spike events to a [Ca2+] trace. Time stamps must be in ms.
    :param spikeEventsData: a Dict with neuron Id's as keys and vectors with timestamps.
    :param start: Start time
    :param end: end time
    :param dt: time resolution (independend of input)
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
    x = np.linspace(start, end, np.ceil((end-start)/dt)+1)
    spikeForm = (1 - (exp(-(x - 0) / tauOn))) * (ampFast * exp(-(x - 0) / tauFast))# + (ampSlow * exp(-(x - 0) / tauSlow))
    spikeForm[np.isnan(spikeForm)] = 0
    res = {}
    for (key, data) in spikeEventsData.items():
        tx = np.zeros(np.ceil((end-start)/dt)+1)
        for y in data:
            if y > start and y < end:
                index = np.floor((y-start)*dt)
                tx[index] += 1
        np.convolve(tx, spikeForm)
        res[key] = tx
    np.seterr(** old)

'''
g['0']
Out[42]:
{'1': {'pos': u'e,1762,1332.1 1762,1367.7 1762,1360 1762,1350.7 1762,1342.1'},
 '10': {'pos': u'e,2002.6,669.82 1789,1384.6 1945,1382.2 2732.7,1368.2 2972,1332 3126,1308.7 3311,1398.8 3311,1243 3311,1243 3311,1243 3311,1169 \\\r\n3311,929.86 2567,769.56 2333,720 2217.2,695.46 2077.8,678.27 2012.8,670.95'},
 '11': {'pos': u'e,1189.4,598.02 1734.8,1384.9 1551.5,1384.2 500.8,1378.1 453,1332 219.33,1106.5 586.81,907.36 852,720 903.42,683.67 915.4,671.02 \\\r\n974,648 1043.9,620.53 1131.1,605.87 1179.4,599.33'},
 '12': {'pos': u'e,2420.6,525.72 1789.1,1385.2 1958.5,1386.6 2875,1391.1 3148,1332 3243.5,1311.3 3349,1340.7 3349,1243 3349,1243 3349,1243 3349,1169 \\\r\n3349,1036.9 3268,1015.1 3268,883 3268,883 3268,883 3268,809 3268,629.93 2596.9,545.08 2430.8,526.83'},
 '13': {'pos': u'e,1455.2,453.37 1734.9,1384.9 1558.6,1384.2 577.01,1378.4 453,1332 393.78,1309.8 342,1306.2 342,1243 342,1243 342,1243 342,809 342,\\\r\n572.07 1249.6,472.93 1445.2,454.32'},
 '14': {'pos': u'e,1130.2,380.33 1735,1385 1568.9,1384.7 684.01,1380.7 418,1332 295.38,1309.5 152,1367.7 152,1243 152,1243 152,1243 152,809 152,532.81 \\\r\n382.94,516.13 646,432 734.61,403.66 1018.1,386.31 1120.1,380.86'},
 '15': {'pos': u'e,2611,306.48 1788.9,1384.6 1978.1,1381.9 3103.9,1364.7 3252,1332 3351.4,1310.1 3463,1344.8 3463,1243 3463,1243 3463,1243 3463,953 \\\r\n3463,851.3 3382,840.7 3382,739 3382,739 3382,739 3382,665 3382,326.94 2778.5,306.12 2621.1,306.43'},
 '16': {'pos': u'e,2136,235.72 1789,1384.8 1986.3,1383.3 3202.7,1372.1 3361,1332 3446.7,1310.3 3539,1331.4 3539,1243 3539,1243 3539,1243 3539,953 \\\r\n3539,658.63 3503.5,498.93 3244,360 3147.7,308.44 3116.5,307.35 3009,288 2839.2,257.44 2294.3,240.21 2146.4,236.01'},
 '17': {'pos': u'e,1036.9,163.71 1734.9,1384.8 1523.1,1383.6 138.7,1373.6 62,1332 19.619,1309 0,1291.2 0,1243 0,1243 0,1243 0,665 0,543.75 201,269.1 \\\r\n310,216 374.81,184.43 883.94,168.01 1026.8,163.99'},
 '18': {'pos': u'e,1720.8,90.655 1735,1384.7 1531,1382.1 238.95,1364.8 164,1332 113.03,1309.7 76,1298.6 76,1243 76,1243 76,1243 76,233 76,29.126 \\\r\n323.58,168.26 526,144 990.82,88.282 1561.3,89.224 1710.8,90.559'},
 '19': {'pos': u'e,2136.2,19.288 1789,1385.1 1992.9,1385.7 3288,1387.3 3452,1332 3516.6,1310.2 3577,1311.2 3577,1243 3577,1243 3577,1243 3577,161 \\\r\n3577,83.864 3501.9,94.006 3428,72 3302.4,34.605 2347.9,21.719 2146.3,19.402'},
 '2': {'pos': u'e,1951.4,1260.2 1788.6,1382.1 1821.7,1377.2 1878.3,1364.4 1914,1332 1932,1315.6 1942.7,1289.7 1948.6,1270'},
'''