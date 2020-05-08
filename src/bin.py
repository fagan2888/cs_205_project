import numpy as np 
from ctypes import *
so_file = "./lbin.so"
lbin = CDLL(so_file)

NBINS = 256
width = 40.0

class MyArray(Structure):
    _fields_ = [("data", (c_float * NBINS) * NBINS)]

def gen_rot_matrix(vec):
    if isinstance(vec, list):
        vec = np.array(vec)

    vec_normed = vec / np.linalg.norm(vec)
    phi = np.arctan2(vec_normed[1], vec_normed[0])
    theta = np.arccos(vec_normed[2])

    firstrot = np.array([[np.cos(phi), np.sin(phi), 0],
                         [-np.sin(phi), np.cos(phi), 0],
                         [          0,      0,       1]])
    secondrot = np.array([[np.cos(theta),    0,   -np.sin(theta)],
                          [0,              1,       0],
                          [np.sin(theta),   0,   np.cos(theta)]])
    rot_mat = np.matmul(secondrot, firstrot)
    return rot_mat

def output_binned_map(snap, spin, subhalo_pos, gas_pos, gas_mass, gas_size, tracer_pos, tracer_mass, tracer_size, tracer_snap, size_factor=0.45):
    gas_pos = np.subtract(gas_pos, subhalo_pos)
    tracer_pos = np.subtract(tracer_pos, subhalo_pos)

    rotmat = gen_rot_matrix(spin)

    gas_pos    = np.matmul(rotmat, gas_pos.transpose()).transpose()
    tracer_pos = np.matmul(rotmat, tracer_pos.transpose()).transpose()

    ans_gas = MyArray()
    ans_tracer = MyArray()

    for i in range(NBINS):
        for j in range(NBINS):
            ans_gas.data[i][j] = 0.0
            ans_tracer.data[i][j] = 0.0
 
    keys = np.where(np.abs(gas_pos[:,2]) < width/2.0)[0]

    xpos = np.array(gas_pos[:,0][keys])
    ypos = np.array(gas_pos[:,1][keys])
    mass = np.array(gas_mass[keys])
    size = size_factor * np.array(gas_size[keys])
    lbin.bin_particles_smoothed(xpos.ctypes.data_as(POINTER(c_double)), ypos.ctypes.data_as(POINTER(c_double)), mass.ctypes.data_as(POINTER(c_double)), 
                       size.ctypes.data_as(POINTER(c_double)), c_int(len(mass)), c_double(width), c_int(NBINS), byref(ans_gas))

    keys = np.where(np.logical_and(tracer_snap - snap > 0, tracer_snap - snap < 32))[0]
    xpos = np.array(tracer_pos[:,0][keys])
    ypos = np.array(tracer_pos[:,1][keys])
    mass = np.array(tracer_mass[keys])
    size = size_factor * np.array(tracer_size[keys])
    lbin.bin_particles_smoothed(xpos.ctypes.data_as(POINTER(c_double)), ypos.ctypes.data_as(POINTER(c_double)), mass.ctypes.data_as(POINTER(c_double)), 
                       size.ctypes.data_as(POINTER(c_double)), c_int(len(mass)), c_double(width), c_int(NBINS), byref(ans_tracer))

    return np.array(ans_gas.data), np.array(ans_tracer.data)

    # f_h5.create_dataset('gas_snap'+str(snap), data=ans_gas.data, dtype='f8')
    # f_h5.create_dataset('tracer_snap'+str(snap), data=ans_tracer.data, dtype='f8')
