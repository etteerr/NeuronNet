import io
import numpy as np
import random
import struct


# Generate random array of random things
n = 1000000
arr = []
for i in range(n):
    arr.append(random.random())


# Write / read

with io.FileIO('TestFile', 'ab+') as f:
    buff = io.BufferedRandom(f, 1024*1024)
    for i in arr:
        buff.write(struct.pack('d', i))


buff.close()