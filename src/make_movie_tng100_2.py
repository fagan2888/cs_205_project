from bin import *
from util import *
from gen import gen_position_of_subhalo
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from movie import *
import pymp

tracers_info = read_dataset('../data/s3/tracers_info_tng100_2')
particles_info = read_dataset('../data/s3/particles_info_tng100_2')
print('finish loading data')
print(particles_info.shape)

def get_subhalo_pos():
    f = open('../data/s3/tng100_2_subhalo_pos').readlines()
    ret = []
    for row in f:
        row = row.strip().split(' ')
        vals = []
        for val in row:
            vals.append(float(val))

        ret.append(vals)
    return ret

subhalo_pos_list = get_subhalo_pos()

snaps = range(3000, 4380)
nbins = 512
m = len(snaps)
final_gas_map = pymp.shared.array((m,nbins, nbins))
final_tracer_map = pymp.shared.array((m, nbins, nbins))

with pymp.Parallel(8) as p:
    for snap in p.range(snaps[0], snaps[-1]+1):
        print(snap)
        subhalo_pos = subhalo_pos_list[snap]

        spin = np.array([396.40796,-595.03217,-1046.6497 ])

        tracers = tracers_info[tracers_info[:,0] == snap]
        particles = particles_info[particles_info[:,0] == snap]

        gas_pos = particles[:,1:4]
        gas_mass = particles[:,4]
        gas_size = particles[:,5]
        tracer_pos = tracers[:,1:4]
        tracer_mass = np.full(len(tracer_pos), 3E7/1E10)
        tracer_snap = tracers[:,5].astype(int)
        tracer_size = np.full(np.shape(tracer_mass), 5)
        
        gas_map, tracer_map = output_binned_map(snap, spin, subhalo_pos, gas_pos, gas_mass, gas_size, tracer_pos, tracer_mass, tracer_size, tracer_snap, size_factor=0.3)
        idx = snap - snaps[0]
        final_gas_map[idx] = gas_map
        final_tracer_map[idx] = tracer_map

#final_gas_map = np.array(final_gas_map)
#final_tracer_map = np.array(final_tracer_map)

print(final_gas_map.shape)
print(final_tracer_map.shape)

make_movie(final_gas_map, final_tracer_map, 'res.mp4')
