# module load python/3.7.7-fasrc01
# python3

# /n/hernquistfs3/IllustrisTNG/Runs/L205n1250TNG/output/snapdir_000

def find_parent(filename, tracer_ids):
	dat = h5.File(filename, mode="r")
#
	tracers = np.array(dat["PartType3"]["TracerID"])
	parents = np.array(dat["PartType3"]["ParentID"])
#
	parent_ids = np.zeros((0, 1))
	for tracer_id in tracer_ids:
		idx = np.where(tracers==tracer_id)
		parent_id = parents[idx]
		print(parent_id)
#
	parent_ids = np.vstack((parent_ids, parent_id))
#
	return parent_ids

## TRACER TO PARENT ##
filename = "snap_000.0.hdf5"
tracer_ids = np.array([100000017356, 100000011490, 100000267723, 100019338711, 100019143999, 100019283435])
find_parent(filename, tracer_ids)
