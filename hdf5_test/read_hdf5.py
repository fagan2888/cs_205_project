import time
import h5py as h5
import numpy as np

t0 = time.time()
t = h5.File('test.hdf5', 'r', libver='latest')
arr = np.array(t['random_ints'])
t1 = time.time()

for i in range(10):
    print(arr[i])

print('time(s): ', t1-t0)

