# Simple test to generate ca trace based on spike data
# Python 2.7

import pickle
from spikeTrainCaTraceFun import *

trace = []
trace.append(spiketraintrace(1, 100, 1, 100))
trace.append(spiketraintrace(2, 100, 1, 100))
trace.append(spiketraintrace(5, 100, 1, 100))
trace.append(spiketraintrace(10, 100, 1, 100))
trace.append(spiketraintrace(20, 100, 1, 100))
# Save trace
with open('spikeCaImagingTestTrace.dat', mode='wb') as f:
    pickle.dump(trace, f)