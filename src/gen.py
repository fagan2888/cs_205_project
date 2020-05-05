import numpy as np
from os import path
import h5py as h5

def gen_all_snaps(basepath, subbox=None, return_files=True):
    assert isinstance(basepath, str)
    if subbox is not None:
        assert isinstance(subbox, int)

    output_path = basepath+'/output'
    if subbox is not None:
        output_path = output_path + '/subbox'+str(subbox)

    if subbox is None:
        snap_base = '/snapdir_'
        file_base = '/snap_'
    else:
        snap_base = '/snapdir_subbox'+str(subbox)+'_'
        file_base = '/snap_subbox'+str(subbox)+'_'

    i = 0
    imax = int(1E6)
    snap_list = []
    file_list = []
    while(True):
        if i >= imax:
            raise Exception("are there really more than "+str(imax)+" snapshots?")

        test_dir = output_path + snap_base + "{:03d}".format(i)
        if(path.exists(test_dir)):
            snap_list.append(i)
            j=0
            while(True):
                if j >= imax:
                    raise Exception("are there really more than "+str(imax)+" files?")
                fname = test_dir+file_base+"{:03d}".format(i)+'.'+str(j)+'.hdf5'
                if(path.exists(fname)):
                    file_list.append((fname, i))
                    j+=1
                else:
                    break

            i+=1
        else:
            break

    if return_files:
        return file_list
    else:
        return np.array(snap_list)

def gen_tracer_ids_blackhole(file_list, position, radius):
    maxmass=0
    blackhole_ID = -1
    for fname in file_list:
        dat = h5.File(fname, mode='r')
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
        dat = h5.File(fname, mode='r')
        if 'PartType3' not in dat.keys():
            continue
        keys = np.where(np.isin(dat['PartType3']['ParentID'], blackhole_ID))[0]
        print(dat['PartType3']['ParentID'][keys])
        tracer_list = np.concatenate((tracer_list, dat['PartType3']['TracerID'][keys]))

    return blackhole_ID, tracer_list


def gen_ids_of_interest(filepath, position, radius, mode='radius_position', PartType=None):
    assert isinstance(filepath, str)
    assert path.exists(filepath)
    assert isinstance(radius, float)
    assert isinstance(position, (np.ndarray, list))

    if isinstance(position, list):
        position = np.array(position)
    assert len(position)==3

    if mode == 'blackhole':
        return _gen_ids_blackhole(filepath, position, radius)

    assert isinstance(PartType, (int, list, np.ndarray))
    if isinstance(PartType, int):
        PartType = [PartType]

    if mode == 'radius_position':
        return _gen_ids_radius_position(filepath, position, radius, PartType)

    raise NotImplementedError("mode="+mode+" is not implemented")

def _gen_ids_radius_position(filepath, position, radius, PartType):
    dat = h5.File(filepath, mode='r')
    ids_list = np.array([], dtype=np.uint64)

    for pt in PartType:
        ptype = 'PartType' + str(pt)
        assert ptype in dat.keys(), "I don\'t recognize particle type: "+str(pt)
        
        pos = np.array(dat[ptype]['Coordinates'])
        pos = np.subtract(pos, position)

        keys = np.where(np.linalg.norm(pos, axis=1) < radius)[0]
        ids_list = np.concatenate((ids_list, dat[ptype]['ParticleIDs'][keys]))

    return ids_list

def _gen_ids_blackhole(filepath, position, radius):
    dat = h5.File(filepath, mode='r')
    
    ptype = 'PartType5'
    if ptype not in dat.keys():
        return []

    pos = np.array(dat[ptype]['Coordinates'])
    pos = np.subtract(pos, position)

    keys = np.where(np.linalg.norm(pos, axis=1) < radius)[0]
    if len(keys) > 0:
        masses = dat[ptype]['Masses'][keys]
        subkey = np.argmax(masses)
        print(pos[keys[subkey]], masses[subkey])
        return (dat[ptype]['ParticleIDs'][keys[subkey]], masses[subkey])
    else:
        return []


if __name__ == '__main__':
    from util import basepath_from_sim

    sim = 'TNG300-3'
    basepath = basepath_from_sim(sim)
    snap_list = gen_all_snaps(basepath)
    print(snap_list)
    snap_list = gen_all_snaps(basepath, subbox=1)
    print(snap_list) 

    position = [37448.52, 42239.434, 66705.08]
    radius = 230.64125

    for i in range(7):
        fpath = '../data/snap_subbox1_2430.'+str(i)+'.hdf5'
        print(gen_ids_of_interest(fpath, position, radius, 'blackhole'))
    
    for i in range(7):
        fpath = '../data/snap_subbox1_2430.'+str(i)+'.hdf5'
        print(gen_ids_of_interest(fpath, position, radius, 'radius_position', 0))
