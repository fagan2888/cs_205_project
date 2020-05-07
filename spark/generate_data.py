from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions  import date_format, to_date,col
import glob
import h5py
from datetime import datetime
import numpy as np
import sys

sys.path.insert(0, '../src/')
from gen import gen_ids_of_interest

position = [37448.52, 42239.434, 66705.08]
radius = 230.64125

timestamp = datetime.now().strftime("%m%d_%H%M")
files = glob.glob('/n/hernquistfs3/IllustrisTNG/Runs/L75n455TNG/output/subbox1/snapdir_subbox1*/*.hdf5')

def read_file(filepath):
    with h5py.File(filepath, 'r') as f:
       try:
           result = gen_ids_of_interest(filepath, position, radius, 'blackhole') 
       except Exception:
           result = []
    return result

conf = SparkConf().setAppName('GenerateData')
sc = SparkContext(conf = conf)

sc.addFile('../src/gen.py')

df = sc.parallelize(files)
df.flatMap(read_file).saveAsTextFile('s3a://spark-namluu-output/illustrisdata_{0}'.format(timestamp))

