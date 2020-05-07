import numpy as np
import s3fs

def get_particles():
    s3 = s3fs.S3FileSystem(key='AKIAQJR434DUQHGP3HWE', secret='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')
    particles_info_file = s3.open('spark-illustris-tng/particles_info', 'r').readlines()
    particles_info = []
    i = 0
    while i < len(particles_info_file):
        line = particles_info_file[i].strip()
        if line[-1] != ']':
            line = line + ' ' + particles_info_file[i+1].strip()
            i += 1
        line = line[1:-1]
        splt = line.split(' ')
        row = []
        for val in splt:
            row.append(float(val))
        
        particles_info.append(row)
        i += 1

    return np.array(particles_info)
