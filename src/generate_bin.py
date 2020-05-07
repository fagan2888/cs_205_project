from bin import *
from util import *
import numpy as np

tracers_info = read_dataset('spark-illustris-tng/tracers_info')
particles_info = read_dataset('spark-illustris-tng/particles_info')
print('finish loading data')
subhalo_pos = np.array([37448.52, 42239.434, 66705.08])
spin = np.array([396.40796,-595.03217,-1046.6497 ])
snap = 1604

tracers = tracers_info[tracers_info[:,0] == snap]
particles = particles_info[particles_info[:,0] == snap]

gas_pos = particles[:,1:4]
gas_mass = particles[:,4]

tracer_pos = tracers[:,1:4]
tracer_mass = tracers[:,4]
tracer_snap = tracers[:,5]

print(output_binned_map(1604, spin, subhalo_pos, gas_pos, gas_mass, tracer_pos, tracer_mass, tracer_snap))

