from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions  import date_format, to_date,col
import glob
import h5py
from datetime import datetime
import numpy as np
import sys
import s3fs

timestamp = datetime.now().strftime("%m%d_%H%M")
print('timestamp: ' + str(timestamp))

s3 = s3fs.S3FileSystem(key='AKIAQJR434DUQHGP3HWE', secret='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')
files = s3.glob('s3://spark-illustris-tng/tng300-1/subbox1/snapshot-*/*.hdf5')

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
    
def extract_parent_info(filepath):
    print(filepath)
    dat = h5py.File(s3.open(filepath, 'rb'), mode='r')
    tracers = np.array([])
    ptype = 'PartType3'
    if (ptype not in dat.keys()):
        return []
        
    keys = np.where(np.isin(dat[ptype]['TracerID'], tracerIDs))[0]
    return np.array(dat['PartType3']['ParentID'][keys])

def read_file(filepath):
    try:
        ret = extract_parent_info(filepath)
        return ret
    except Exception as ex:
        print(ex)
        return []

subhalo_lists = h5py.File(s3.open('spark-illustris-tng/subhalo-list/subbox1_99.hdf5', 'rb'), 'r')
subhalo_lists.keys()

subhalo_id = 19391
subhalo_id_fp = 'spark-illustris-tng/subhalo-list/subbox1_99.hdf5'
subhalo_positions = gen_position_of_subhalo(subhalo_id, subhalo_id_fp)

lastfiles = s3.glob('s3://spark-illustris-tng/tng300-1/subbox1/snapshot-2430/*.hdf5')

blackholdID, tracerIDs = gen_tracer_ids_blackhole(lastfiles, subhalo_positions[2430], 140)

conf = SparkConf().setAppName('GenerateTracerParent')
sc = SparkContext(conf = conf)

timestamp = datetime.now().strftime("%m%d_%H%M")
print(timestamp)

df = sc.parallelize(files).repartition(10)
df.flatMap(read_file)           \
    .map(lambda x: (x,1))       \
    .reduceByKey(lambda x,y: x) \
    .map(lambda x: x[0])        \
    .coalesce(1)                \
    .saveAsTextFile('s3a://spark-namluu-output/illustrisdata_{0}'.format(timestamp))
