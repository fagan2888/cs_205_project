from pyspark import SparkConf, SparkContext
import glob
import h5py
from datetime import datetime
import numpy as np
import sys
import s3fs
import os

### GLOBAL VARIABLES
USE_S3 = True

### HELPER FUNCTIONS

def open_h5(fname):
  if USE_S3:
    return h5py.File(s3.open(fname, 'rb'), mode='r')
  else:
    return h5py.File(fname, 'r')

def gen_tracer_ids_blackhole(file_list, position, radius):
    maxmass=0
    blackhole_ID = -1
    for fname in file_list:
        dat = open_h5(fname)
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
    parent_list = np.array([], dtype=np.uint64)
    for fname in file_list:
        dat = open_h5(fname)

        if 'PartType3' not in dat.keys():
            continue
        keys = np.where(np.isin(dat['PartType3']['ParentID'], blackhole_ID))[0]
        
        tracer_list = np.concatenate((tracer_list, dat['PartType3']['TracerID'][keys]))

    return blackhole_ID, tracer_list

def gen_position_of_subhalo(subhalo_id, subhalo_file):
    dat = open_h5(subhalo_file)
    key = np.where(np.array(dat['SubhaloIDs']) == subhalo_id)[0][0]
    return dat['SubhaloPos'][key]

def get_snapnum(snap, tracer_ids_bc, blackhole_id):
    try:
        snap_files = s3.glob(snap_tofile(snap))
        tracer_ids = tracer_ids_bc.value
        tracer_map = np.array([]).reshape(0,2)
        
        for f in snap_files:
            dat = open_h5(f)
            if 'PartType3' in dat.keys():
                keys = np.where(np.isin(dat['PartType3']['TracerID'], tracer_ids))[0]
                parentId = dat['PartType3']['ParentID'][keys].reshape(-1,1)
                tracerId =  dat['PartType3']['TracerID'][keys].reshape(-1,1)
                tracer_map = np.vstack((tracer_map, np.hstack((tracerId, parentId))))

        keys = np.where(tracer_map[:,1] == blackhole_id)
        tracers = tracer_map[:,0][keys].reshape(-1,1)
        return np.hstack((tracers, np.full((len(tracers), 1), snap)))

        return ret
    except Exception as ex:
      print(ex)
      return np.array([]).reshape(0,2)

def get_position(snap, tracer_ids_bc, tracer_snaps_bc):
    try:
        snap_files = s3.glob(snap_tofile(snap))

        tracer_ids = tracer_ids_bc.value
        tracer_snaps = tracer_snaps_bc.value

        # map from tracer id -> parent id
        tracer_map = np.array([]).reshape(0,2)
        
        for f in snap_files:
            dat = open_h5(f)
            
            if 'PartType3' in dat.keys():
                keys = np.where(np.isin(dat['PartType3']['TracerID'], tracer_ids))[0]
                parentId = dat['PartType3']['ParentID'][keys].reshape(-1,1)
                tracerId =  dat['PartType3']['TracerID'][keys].reshape(-1,1)
                tracer_map = np.vstack((tracer_map, np.hstack((tracerId, parentId))))
        
        ret = np.array([]).reshape(0, 7)
        
        for f in snap_files:
            dat = open_h5(f)
            
            for i in [0, 2, 4, 5]:
                ptype = 'PartType' + str(i)
                if ptype in dat.keys():
                    for row in tracer_map:
                        keys = np.where(np.array(dat[ptype]['ParticleIDs']) == row[1])[0]
                        if len(keys) == 1:
                            key = keys[0]
                            coord = dat[ptype]['Coordinates'][key].reshape(-1,3)
                            # mass = dat[ptype]['Masses'][key].reshape(-1,1)
                            # density = dat[ptype]['Masses'][key] / dat[ptype]['Density'][key] 
                            # size = np.power(density, 1.0/3).reshape(-1,1)
                            mass = np.array([[1]])
                            density = np.array([[1]])
                            size = np.array([[1]])
                            tracer_key = np.where(tracer_snaps[:,0] == row[0])[0]
                            tracer_snap = tracer_snaps[:,1][tracer_key].reshape(-1,1)
                            
                            val = np.hstack((np.array([[snap]]), coord, mass, size, tracer_snap))
                            ret = np.vstack((ret, val))

                    
        return ret
    except Exception as ex:
      print(ex)
      return []

def extract_gas_from_snap(snap, position, radius):
    flist = snap_tofile(snap)
    files = s3.glob(flist)
    
    ret = np.array([]).reshape(0, 6)
    for f in files:
        ret = np.vstack((ret, extract_gas_info(f, position, radius, snap)))
    
    return ret
    
def extract_map(snap):
    position = subhalo_positions_bc.value[snap]
    ret = extract_gas_from_snap(snap, position, radius)
    return ret
    
def snap_tofile(snap):
    return 'spark-illustris-tng/tng100-2/subbox1/snapdir_subbox1_{0}/*.hdf5'.format(snap)
    
def extract_snapnum(snap):
    return get_snapnum(snap, tracer_ids_bc, blackhole_id)

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

### METADATA

conf = SparkConf().setAppName('GenerateTracerData')
sc = SparkContext(conf = conf)

ACCESS_KEY = conf.get('SPARK_ACCESS_KEY')
SECRET_KEY = conf.get('SPARK_SECRET_KEY')

s3 = s3fs.S3FileSystem(key=ACCESS_KEY, secret=SECRET_KEY)

subhalo_id = 89587
subhalo_positions = get_subhalo_pos(s3)
print('length subhalo positions')
print(len(subhalo_positions))
radius = 140

snaps = range(0, 4380)

last_snap = snaps[-1]
lastfiles = s3.glob(snap_tofile(last_snap))
blackhole_id, tracer_ids = gen_tracer_ids_blackhole(lastfiles, subhalo_positions[last_snap], 140)

timestamp = datetime.now().strftime("%m%d_%H%M")
print(timestamp)

### SPARK


"""
To recalculate tracer_snaps, use this, comment out and hard code its value to improve performance
"""
tracer_ids_bc = sc.broadcast(tracer_ids)

#tracer_snaps = sc.parallelize(snaps).repartition(10).flatMap(extract_snapnum).reduceByKey(lambda v1, v2: min(v1, v2)).collect()
tracer_snaps = [(200766509441.0, 3885.0), (200765701641.0, 3885.0), (200766489841.0, 3885.0), (200892167541.0, 3000.0), (200766488891.0, 3885.0), (200890415391.0, 3885.0), (200765403392.0, 3885.0), (200765408842.0, 3885.0), (200765686042.0, 3885.0), (200766484242.0, 3885.0)]

tracer_snaps_bc = sc.broadcast(np.array(tracer_snaps))


get_position_map = lambda f: get_position(f, tracer_ids_bc, tracer_snaps_bc)

df = sc.parallelize(snaps).repartition(10)

df.flatMap(get_position_map).repartition(1).saveAsTextFile('s3a://spark-namluu-output/illustrisdata_tracer{0}'.format(timestamp))
