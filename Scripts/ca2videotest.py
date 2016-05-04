import numpy as np
import networkx as nx
import Engine.python27Ca2VideoMaker as ca
time = 5#sec
dt = 0.01 #ms
fps = 10000.0

samples = (time * 1000) / dt
data = {}
data[1] = np.random.normal(4,4,samples)
data[2] = np.random.poisson(4,samples)
G = {1:[0,0],
     2:[0.5, 0.5]}

#G = nx.circular_layout(G, dim=2, scale=4/800)

ca.renderCa2Video(data, G, dt=dt, fps=fps, mode='mean')