from pyspark import SparkConf, SparkContext
import h5py
from datetime import datetime
import numpy as np
import s3fs
import os

### FUNCTIONS

def gen_position_of_subhalo(subhaloID, subhaloFile):
    dat = h5py.File(s3.open(subhaloFile), mode='r')
    key = np.where(np.array(dat['SubhaloIDs']) == subhaloID)[0][0]
    return dat['SubhaloPos'][key]

def get_snapshot_number(fpath):
    return int(fpath.split('/')[-2][len('snapshot-'):])

def extract_gas_info(filepath, position, radius):
    dat = h5py.File(s3.open(filepath, 'rb'), mode='r')

    ptype = 'PartType0'
    snapnum = get_snapshot_number(filepath)
    if (ptype not in dat.keys()):
        return []

    pos = np.array(dat[ptype]['Coordinates'])
    pos = np.subtract(pos, position)
    keys = np.where(np.linalg.norm(pos, axis=1) < radius)[0]

    coordinates = dat[ptype]['Coordinates'][keys]
    masses = dat[ptype]['Masses'][keys].reshape(-1,1)
    volume = dat[ptype]['Masses'][keys] / dat[ptype]['Density'][keys]
    size = np.power(volume, 1.0/3).reshape(-1,1)

    return np.hstack((np.full((masses.shape[0], 1), snapnum), coordinates, masses, size))

### VARIABLES

ACCESS_KEY = os.environ['SPARK_ACCESS_KEY']
SECRET_KEY = os.environ['SPARK_SECRET_KEY']

timestamp = datetime.now().strftime("%m%d_%H%M")
print("timestamp: " + str(timestamp))

s3 = s3fs.S3FileSystem(key=ACCESS_KEY, secret=SECRET_KEY)
files = s3.glob('s3://spark-illustris-tng/tng300-1/subbox1/snapshot-*/*.hdf5')

print('length: ' + str(len(files)))

subhalo_id = 19391
subhalo_id_fp = 'spark-illustris-tng/subhalo-list/subbox1_99.hdf5'
subhalo_positions = gen_position_of_subhalo(subhalo_id, subhalo_id_fp)
conf = SparkConf().setAppName('GenerateParticleData')

radius = 140

### SPARK

sc = SparkContext(conf = conf)
subhalo_positions_bc = sc.broadcast(subhalo_positions)

def extract_map(filepath):
    try:
        snapshot_id = get_snapshot_number(filepath)
        position = subhalo_positions_bc.value[snapshot_id]
        ret = extract_gas_info(filepath, position, radius)
        return ret
    except Exception as ex:
        print(ex)
        return []

df = sc.parallelize(files) \
  .repartition(10)         \
  .flatMap(extract_map)

df.repartition(1)          \
  .saveAsTextFile('s3a://spark-namluu-output/illustrisdata_{0}'.format(timestamp))
