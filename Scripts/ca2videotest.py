import numpy as np
import networkx as nx
import Engine.python27Ca2VideoMaker as ca
time = 20#sec
dt = 1.0 #ms
fps = 100.0

samples = (time * 1000) / dt
data = {}
data[1] = np.random.normal(4,4,samples)
data[2] = np.random.poisson(4,samples)
G = nx.DiGraph()
G.add_node(1, {'pos': (0,0)})
G.add_node(2, {'pos': (0.5,0.5)})

ca.renderCa2Video(data, G, dt=dt, fps=fps, mode='mean')