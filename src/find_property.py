# module load python/3.7.7-fasrc01
# python3

# /n/hernquistfs3/IllustrisTNG/Runs/L205n1250TNG/output/snapdir_000

import h5py as h5 # version 2.10.0
import numpy as np # version 1.18.1

def find_property(filename, ids_of_interest, property_of_interest):
	dat = h5.File(filename, mode="r")
#
#all_props = np.zeros((0, 3))
#
#
	ptypes = [key for key in list(dat.keys()) if ("PartType" in key and "PartType3" not in key)]
#
	for ptype in ptypes:
		#property_list = np.zeros((0, 6))
		#property_row = np.zeros((0, 0))
#
		pids = np.array(dat[ptype]["ParticleIDs"])
#
		if property_of_interest in list(dat[ptype].keys()):
			property = np.array(dat[ptype][property_of_interest])
#print(property)
#
			for id_of_interest in ids_of_interest:
				if id_of_interest in pids:
					idx = np.where(pids==id_of_interest)
					print(str(property[idx]))
					#property_row = np.column_stack((str(id_of_interest), str(pids[idx]), idx, property[idx]))
				#property_list = np.vstack((property_list, property_row))
		else:
			if id_of_interest in pids:
				idx = np.where(pids==id_of_interest)
				print("N/A")
				#property_row = np.column_stack((str(id_of_interest), str(pids[idx]), idx, "N/A"))
			#property_list = np.vstack((property_list, property_row))
#	
	return None
	#return property_list

#list of tuples

## EXTRACT MASSES ##
filename = "snap_000.0.hdf5"
ids_of_interest = np.array([100000000001, 19384481])
property_of_interest = "Masses"
find_property(filename, ids_of_interest, property_of_interest)

## EXTRACT COORDINATES ##
filename = "snap_000.0.hdf5"
ids_of_interest = np.array([100000000001, 19384481])
property_of_interest = "Coordinates"
find_property(filename, ids_of_interest, property_of_interest)




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
