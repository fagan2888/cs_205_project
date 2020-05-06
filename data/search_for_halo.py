import numpy as np 
import h5py as h5 
import sys
import glob

if len(sys.argv)>1:
    name = 'TNG100-'+sys.argv[1]
    assert name in ['TNG100-3', 'TNG100-2', 'TNG100-1']
else:
    name = 'TNG100-1'

print(name)

center = np.array([37000, 43500, 67500])
boxsize = 7500

hlittle=0.6774

print('center=', center/1000)
print('boxsize=', boxsize/1000)

fof_list = glob.glob(name + '/fof_subhalo_tab_099.*.hdf5')

for fname in fof_list:
    fof = h5.File(fname, mode='r')

    if 'GroupPos' not in fof['Group'].keys():
        continue

    group_pos = np.array(fof['Group']['GroupPos'])
    group_pos = np.subtract(group_pos, center)

    xbool = np.abs(group_pos[:,0]) < boxsize/2.0
    ybool = np.abs(group_pos[:,1]) < boxsize/2.0
    zbool = np.abs(group_pos[:,2]) < boxsize/2.0

    keys = np.where(np.logical_and(np.logical_and(xbool, ybool), zbool))[0]

    xdist = boxsize/2.0 - np.abs(group_pos[:,0])
    ydist = boxsize/2.0 - np.abs(group_pos[:,1])
    zdist = boxsize/2.0 - np.abs(group_pos[:,2])

    dist_to_box = np.minimum(np.minimum(xdist, ydist), zdist)
    dist_to_box /= boxsize/2.0

    for k in keys:
        if fof['Group']['Group_M_Mean200'][k]/hlittle > 80:
            print(fof['Group']['GroupFirstSub'][k], fof['Group']['GroupPos'][k], dist_to_box[k], fof['Group']['Group_M_Mean200'][k]/hlittle, fof['Group']['Group_R_Mean200'][k])
