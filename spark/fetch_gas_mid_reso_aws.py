from pyspark import SparkConf, SparkContext
import h5py
from datetime import datetime
import numpy as np
import s3fs
import os

### FUNCTIONS

def get_snapshot_number(fpath):
    return int(fpath.split('/')[-2][len('snapshot-'):])

def extract_gas_info(filepath, position, radius, snapnum):
    dat = h5py.File(s3.open(filepath, 'rb'), mode='r')

    ptype = 'PartType0'
    if (ptype not in dat.keys()):
        return np.array([]).shape(0,6)

    pos = np.array(dat[ptype]['Coordinates'])
    pos = np.subtract(pos, position)
    keys = np.where(np.linalg.norm(pos, axis=1) < radius)[0]

    coordinates = dat[ptype]['Coordinates'][keys]
    masses = dat[ptype]['Masses'][keys].reshape(-1,1)
    volume = dat[ptype]['Masses'][keys] / dat[ptype]['Density'][keys]
    size = np.power(volume, 1.0/3).reshape(-1,1)

    return np.hstack((np.full((masses.shape[0], 1), snapnum), coordinates, masses, size))
    
def extract_gas_from_snap(snap, position, radius):
    flist = snap_tofile(snap)
    files = s3.glob(flist)
    
    ret = np.array([]).reshape(0, 6)
    for f in files:
        ret = np.vstack((ret, extract_gas_info(f, position, radius, snap)))
    
    return ret
    
def extract_map(snap):
    try:
      position = subhalo_positions_bc.value[snap]
      ret = extract_gas_from_snap(snap, position, radius)
      return ret
    except Exception as ex:
      print('snap error: ' + str(snap))
      print(ex)
      return []
    
def snap_tofile(snap):
    return 'spark-illustris-tng/tng100-2/subbox1/snapdir_subbox1_{0}/*.hdf5'.format(snap)

def get_subhalo_pos(s3):
    f = s3.open('spark-illustris-tng/tng100_2_subhalo_pos').readlines()
    ret = []
    for row in f:
        row = row.strip().split(' ')
        vals = []
        for val in row:
            vals.append(float(val))
        
        ret.append(vals)
    return ret

### VARIABLES

conf = SparkConf().setAppName('GenerateParticleData')
ACCESS_KEY = conf.get('SPARK_ACCESS_KEY')
SECRET_KEY = conf.get('SPARK_SECRET_KEY')

timestamp = datetime.now().strftime("%m%d_%H%M")
print("timestamp: " + str(timestamp))

s3 = s3fs.S3FileSystem(key=ACCESS_KEY, secret=SECRET_KEY)

subhalo_id = 89587
subhalo_positions = get_subhalo_pos(s3)
radius = 140

snaps = range(0, 4380)
### SPARK

sc = SparkContext(conf = conf)
subhalo_positions_bc = sc.broadcast(subhalo_positions)

df = sc.parallelize(snaps) \
  .repartition(10)         \
  .flatMap(extract_map)

df.repartition(1).saveAsTextFile('s3a://spark-namluu-output/illustrisdata_gas_{0}'.format(timestamp))
