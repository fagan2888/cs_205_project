from bin import *
from util import *
from gen import gen_position_of_subhalo
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from movie import *
tracers_info = read_dataset('../data/s3/tracers_info_full')
particles_info = read_dataset('../data/s3/particles_info_with_size')
print('finish loading data')
print(particles_info.shape)

final_gas_map = []
final_tracer_map = []
for snap in tqdm(range(0,2430)):
    #print('snap: ' + str(snap))
    subhalo_pos_list = gen_position_of_subhalo(19391, '../data/TNG100-3/subbox1_99.hdf5')
    subhalo_pos = subhalo_pos_list[snap]

    spin = np.array([396.40796,-595.03217,-1046.6497 ])

    tracers = tracers_info[tracers_info[:,0] == snap]
    particles = particles_info[particles_info[:,0] == snap]

    gas_pos = particles[:,1:4]
    gas_mass = particles[:,4]
    gas_size = particles[:,5]
    tracer_pos = tracers[:,1:4]
    #tracer_mass = tracers[:,4]
    tracer_mass = np.full(len(tracer_pos), 3E7/1E10)
    tracer_snap = tracers[:,5].astype(int)
    #tracer_size = tracers[:,6]
    tracer_size = np.full(np.shape(tracer_mass), 5)
    
    gas_map, tracer_map = output_binned_map(snap, spin, subhalo_pos, gas_pos, gas_mass, gas_size, tracer_pos, tracer_mass, tracer_size, tracer_snap, size_factor=0.3)
    final_gas_map.append(gas_map)
    final_tracer_map.append(tracer_map)
    #print(np.sum(gas_map), np.sum(tracer_map))

final_gas_map = np.array(final_gas_map)
final_tracer_map = np.array(final_tracer_map)

print(final_gas_map.shape)
print(final_tracer_map.shape)

make_movie(final_gas_map, final_tracer_map, 'res.mp4')
