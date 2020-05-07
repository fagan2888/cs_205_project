from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions  import date_format, to_date,col
import glob
import h5py
from datetime import datetime
import numpy as np
import sys
import s3fs

### HELPER FUNCTIONS

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
    parent_list = np.array([], dtype=np.uint64)
    for fname in file_list:
        dat = h5py.File(s3.open(fname, 'rb'), mode='r')
        if 'PartType3' not in dat.keys():
            continue
        keys = np.where(np.isin(dat['PartType3']['ParentID'], blackhole_ID))[0]
        print(dat['PartType3']['ParentID'][keys])
        tracer_list = np.concatenate((tracer_list, dat['PartType3']['TracerID'][keys]))
        parent_list = np.concatenate((tracer_list, dat['PartType3']['ParentID'][keys]))
    return blackhole_ID, tracer_list, parent_list

def gen_position_of_subhalo(subhaloID, subhaloFile):
    dat = h5py.File(s3.open(subhaloFile), mode='r')
    key = np.where(np.array(dat['SubhaloIDs']) == subhaloID)[0][0]
    return dat['SubhaloPos'][key]

def get_snapnum(snap, tracerIDs_bc):
    try:
        snap_files = s3.glob(snap + '/*')
        tracerIDs = tracerIDs_bc.value
        tracer_map = np.array([]).reshape(0,2)
        
        for f in snap_files:
            dat = h5py.File(s3.open(f, 'rb'), 'r')
            if 'PartType3' in dat.keys():
                keys = np.where(np.isin(dat['PartType3']['TracerID'], tracerIDs))[0]
                parentId = dat['PartType3']['ParentID'][keys].reshape(-1,1)
                tracerId =  dat['PartType3']['TracerID'][keys].reshape(-1,1)
                tracer_map = np.vstack((tracer_map, np.hstack((tracerId, parentId))))
        snapnum = int(snap.split('/')[-1][len('snapshot-'):])
        keys = np.where(tracer_map[:,1] == blackholeID)
        tracers = tracer_map[:,0][keys].reshape(-1,1)
        return np.hstack((tracers, np.full((len(tracers), 1), snapnum)))

        return ret
    except Exception as ex:
      print(ex)
      return []

tracer_snaps = [(200111276192.0, 1811.0), (200095813192.0, 2174.0), (200095751092.0, 2174.0), (200095712792.0, 2174.0), (200095807792.0, 2174.0), (200111342341.0, 1933.0), (200095750441.0, 2174.0), (200111305741.0, 2174.0), (200111277941.0, 1847.0), (200095676441.0, 2174.0), (200095755641.0, 2174.0), (200095785342.0, 2174.0), (200097361842.0, 2174.0), (200095812542.0, 2174.0), (200111522342.0, 2174.0), (200095750491.0, 2174.0)]

def get_position(snap, tracerIDs_bc, tracer_snaps_bc):
    try:
        snap_files = s3.glob(snap + '/*')
        tracerIDs = tracerIDs_bc.value
        tracer_snaps = tracer_snaps_bc.value

        snapnum = int(snap.split('/')[-1][len('snapshot-'):])
        
        # map from tracer id -> parent id
        tracer_map = np.array([]).reshape(0,2)
        
        for f in snap_files:
            dat = h5py.File(s3.open(f, 'rb'), 'r')
            
            if 'PartType3' in dat.keys():
                keys = np.where(np.isin(dat['PartType3']['TracerID'], tracerIDs))[0]
                parentId = dat['PartType3']['ParentID'][keys].reshape(-1,1)
                tracerId =  dat['PartType3']['TracerID'][keys].reshape(-1,1)
                tracer_map = np.vstack((tracer_map, np.hstack((tracerId, parentId))))
        
        ret = np.array([]).reshape(0, 7)
        
        for f in snap_files:
            dat = h5py.File(s3.open(f, 'rb'), 'r')
            
            for i in [0]:
                ptype = 'PartType' + str(i)
                if ptype in dat.keys():
                    for row in tracer_map:
                        keys = np.where(np.array(dat[ptype]['ParticleIDs']) == row[1])[0]
                        if len(keys) == 1:
                            key = keys[0]
                            coord = dat[ptype]['Coordinates'][key].reshape(-1,3)
                            mass = dat[ptype]['Masses'][key].reshape(-1,1)
                            density = dat[ptype]['Masses'][key] / dat[ptype]['Density'][key] 
                            size = np.power(density, 1.0/3).reshape(-1,1)
                            tracer_key = np.where(tracer_snaps[:,0] == row[0])[0]
                            tracer_snap = tracer_snaps[:,1][tracer_key].reshape(-1,1)
                            
                            val = np.hstack((np.array([[snapnum]]), coord, mass, size, tracer_snap))
                            ret = np.vstack((ret, val))
                    
        return ret
    except Exception as ex:
      print(ex)
      return []

### METADATA

s3 = s3fs.S3FileSystem(key='AKIAQJR434DUQHGP3HWE', secret='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')
files = s3.glob('s3://spark-illustris-tng/tng300-1/subbox1/snapshot-*/*.hdf5')

subhalo_lists = h5py.File(s3.open('spark-illustris-tng/subhalo-list/subbox1_99.hdf5', 'rb'), 'r')
subhalo_lists.keys()

subhalo_id = 19391
subhalo_id_fp = 'spark-illustris-tng/subhalo-list/subbox1_99.hdf5'
subhalo_positions = gen_position_of_subhalo(subhalo_id, subhalo_id_fp)

lastfiles = s3.glob('s3://spark-illustris-tng/tng300-1/subbox1/snapshot-2430/*.hdf5')
blackholdID, tracerIDs, parents = gen_tracer_ids_blackhole(lastfiles, subhalo_positions[2430], 140)

timestamp = datetime.now().strftime("%m%d_%H%M")
print(timestamp)

snaps = s3.glob('s3://spark-illustris-tng/tng300-1/subbox1/snapshot*')

### SPARK

conf = SparkConf().setAppName('GenerateTracerData2')
sc = SparkContext(conf = conf)

parents_bc = sc.broadcast(parents)
tracer_snaps_bc = sc.broadcast(np.array(tracer_snaps))
tracerIDs_bc = sc.broadcast(tracerIDs)

get_position_map = lambda f: get_position(f, tracerIDs_bc, tracer_snaps_bc)

df = sc.parallelize(snaps).repartition(10)

df.flatMap(get_position_map).repartition(1).saveAsTextFile('s3a://spark-namluu-output/illustrisdata_{0}'.format(timestamp))
