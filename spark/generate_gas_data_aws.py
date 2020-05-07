from pyspark import SparkConf, SparkContext
import h5py
from datetime import datetime
import numpy as np
import s3fs

def gen_tracer_ids_blackhole(file_list, position, radius):
    maxmass=0
    blackhole_ID = -1
    for fname in file_list:
        dat = h5py.File(s3.open(fname, 'rb'), mode='r')
        if 'PartType5' not in dat.keys():
            continue
        pos = np.array(dat['PartType5']['Coordinates'])
        pos = np.subtract(pos, position)

        keys = np.where(np.linalg.norm(pos, axis=1) < radius)[0]
        if len(keys) > 0:
            masses = dat['PartType5']['Masses'][keys]
            subkey = np.argmax(masses)

            if masses[subkey] > maxmass:
                maxmass = masses[subkey]
                blackhole_ID = dat['PartType5']['ParticleIDs'][keys[subkey]]

    assert blackhole_ID > 0

    tracer_list = np.array([], dtype=np.uint64)
    for fname in file_list:
        dat = h5py.File(s3.open(fname, 'rb'), mode='r')
        if 'PartType3' not in dat.keys():
            continue
        keys = np.where(np.isin(dat['PartType3']['ParentID'], blackhole_ID))[0]
        print(dat['PartType3']['ParentID'][keys])
        tracer_list = np.concatenate((tracer_list, dat['PartType3']['TracerID'][keys]))

    return blackhole_ID, tracer_list

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
    masses = np.reshape(dat[ptype]['Masses'][keys], (-1,1))
    volume = dat[ptype]['Masses'][keys] / dat[ptype]['Density'][keys]
    size = np.power(volume, 1.0/3).reshape(-1,1)
    return np.hstack((np.full((masses.shape[0], 1), snapnum), coordinates, masses, size))
    


### METADATA

timestamp = datetime.now().strftime("%m%d_%H%M")
print("timestamp: " + str(timestamp))

s3 = s3fs.S3FileSystem(key='', secret='')
files = s3.glob('s3://spark-illustris-tng/tng300-1/subbox1/snapshot-*/*.hdf5')
print('length: ' + str(len(files)))

subhalo_id = 19391
subhalo_id_fp = 'spark-illustris-tng/subhalo-list/subbox1_99.hdf5'
subhalo_positions = gen_position_of_subhalo(subhalo_id, subhalo_id_fp)
conf = SparkConf().setAppName('GenerateData')


### SPARK
sc = SparkContext(conf = conf)
subhalo_positions_bc = sc.broadcast(subhalo_positions)

def extract_map(filepath):
    try:
        snapshot_id = get_snapshot_number(filepath)
        position = subhalo_positions_bc.value[snapshot_id]
        ret = extract_gas_info(filepath, position, 140)
        return ret
    except Exception as ex:
        print(ex)
        return []

df = sc.parallelize(files) \
  .repartition(10)         \
  .flatMap(extract_map)

df.repartition(1).saveAsTextFile('s3a://spark-namluu-output/illustrisdata_{0}'.format(timestamp))
