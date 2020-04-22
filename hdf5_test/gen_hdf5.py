import h5py as h5
import numpy as np

t = h5.File('test.hdf5', 'w', libver='latest')
data = np.random.randint(0, 100, int(1E8))

t.create_dataset('random_ints', data=data, dtype='i8')
t.close()

