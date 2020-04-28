import numpy as np
from os import path

def gen_all_snaps(basepath, subbox=None):
    assert isinstance(basepath, str)
    if subbox is not None:
        assert isinstance(subbox, int)

    output_path = basepath+'/output'
    if subbox is not None:
        output_path = output_path + '/subbox'+str(subbox)

    if subbox is None:
        snap_base = '/snapdir_'
    else:
        snap_base = '/snapdir_subbox'+str(subbox)+'_'

    i = 0
    imax = int(1E6)
    snap_list = []
    while(True):
        if i >= imax:
            raise Exception("are there really more than "+str(imax)+" snapshots?")

        test_dir = output_path + snap_base + "{:03d}".format(i)
        if(path.exists(test_dir)):
            snap_list.append(i)
            i+=1
        else:
            break

    return np.array(snap_list)

if __name__ == '__main__':
    from util import basepath_from_sim

    sim = 'TNG300-3'
    basepath = basepath_from_sim(sim)
    snap_list = gen_all_snaps(basepath)
    print(snap_list)
    snap_list = gen_all_snaps(basepath, subbox=1)
    print(snap_list) 

