import numpy as np 
import h5py as h5 

center = np.array([37000, 43500, 67500])
boxsize = 7500

hlittle=0.6774

print('center=', center/1000)
print('boxsize=', boxsize/1000)

for i in range(7):
	fname = 'fof_subhalo_tab_099.' + str(i) + '.hdf5'
	fof = h5.File(fname, mode='r')

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
		print(fof['Group']['GroupPos'][k], dist_to_box[k], fof['Group']['Group_M_Mean200'][k]/hlittle, fof['Group']['Group_R_Mean200'][k])
