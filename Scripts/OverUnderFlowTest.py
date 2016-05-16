from numpy import exp
import numpy
numpy.seterr(all='raise')
for i in range(-1000, 1000, 10):
    try:
        x = exp(i)
    except:
        print(i)