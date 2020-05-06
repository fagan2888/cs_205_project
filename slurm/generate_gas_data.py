from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions  import date_format, to_date,col
import glob
import h5py
from datetime import datetime
import numpy as np
import sys
import os
from os.path import expanduser

sys.path.insert(0, '../src/')
from gen import gen_ids_of_interest, gen_position_of_subhalo

home = expanduser('~')
radius = 140
subhalo_id = 19391

timestamp = datetime.now().strftime("%m%d_%H%M")
files = glob.glob('/n/hernquistfs3/IllustrisTNG/Runs/L75n455TNG/output/subbox1/snapdir_subbox1*/*.hdf5')
subhalo_id_fp = glob.glob(home + '/data/subhalo/*.hdf5')[0]

subhalo_positions = gen_position_of_subhalo(subhalo_id, subhalo_id_fp)

def get_snapshot_number(fpath):
    return int(fpath.split('/')[-2][len('snapdir_subbox1_'):])

def extract_gas_info(filepath, position, radius):
    dat = h5py.File(filepath, mode='r')
    ptype = 'PartType0'
    if (ptype not in dat.keys()):
        return []
    pos = np.array(dat[ptype]['Coordinates'])
    pos = np.subtract(pos, position)
    keys = np.where(np.linalg.norm(pos, axis=1) < radius)[0]
    coordinates = dat[ptype]['Coordinates'][keys]
    masses = np.reshape(dat[ptype]['Masses'][keys], (-1,1))
    return np.hstack((coordinates, masses))

def read_file(filepath):
    try:
        snapshot_id = get_snapshot_number(filepath)
        ret = extract_gas_info(filepath, subhalo_positions[snapshot_id], radius)
        return ret
    except Exception as ex:
        print(ex)
        return []

conf = SparkConf().setAppName('GenerateData')
sc = SparkContext(conf = conf)

sc.addFile(os.getcwd() + '/../src/gen.py')

df = sc.parallelize(files)
df.flatMap(read_file).saveAsTextFile('s3a://spark-namluu-output/illustrisdata_{0}'.format(timestamp))

