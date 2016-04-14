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
import pylab as pl


def generateNetworkCoordinates(G, layout='dot',show=0):
    """
    generates network coordinates in the attribute 'pos'
    :param G:
    :Param layout: neato|dot|twopi|circo|fdp|nop
    :return:
    """
    ag = networkx.nx_agraph.to_agraph(G)
    ag.layout(prog=layout)
    ag.
