import numpy as np

def basepath_from_sim(sim):
    assert isinstance(sim, str), "sim must be a string"

    base = '/n/hernquistfs3/IllustrisTNG/Runs/'

    sim_paths = {'TNG300-3': base + 'L205n625TNG/',
                 'TNG300-3-Dark': base + 'L205n625TNG_DM/',
                 'TNG300-2': base + 'L205n1250TNG/',
                 'TNG300-2-Dark': base + 'L205n1250TNG_DM/',
                 'TNG300-1': base + 'L205n2500TNG/',
                 'TNG300-1-Dark': base + 'L205n2500TNG_DM/',
   
                 'TNG100-3': base + 'L75n455TNG/',
                 'TNG100-3-Dark': base + 'L75n455TNG_DM/',
                 'TNG100-2': base + 'L75n910TNG/',
                 'TNG100-2-Dark': base + 'L75n910TNG_DM/',
                 'TNG100-1': base + 'L75n1820TNG/',
                 'TNG100-1-Dark': base + 'L75n1820TNG_DM/',
    
                 'TNG50-4': base + 'L35n270TNG/',
                 'TNG50-4-Dark': base + 'L35n270TNG_DM/',
                 'TNG50-3': base + 'L35n540TNG/',
                 'TNG50-3-Dark': base + 'L35n540TNG_DM/',
                 'TNG50-2': base + 'L35n1080TNG/',
                 'TNG50-2-Dark': base + 'L35n1080TNG_DM/',
                 'TNG50-1': base + 'L35n2160TNG/',
                 'TNG50-1-Dark': base + 'L35n2160TNG_DM/'}

    if sim in sim_paths.keys():
        return sim_paths[sim]
    else:
        raise NotImplementedError('I don\'t recognize sim: '+sim)

def read_dataset(path):
    f = open(path, 'r').readlines()
    ret = []
    i = 0

    while i < len(f):
      line = f[i].strip()
      if line[-1] != ']':
          line = line + ' ' + f[i+1].strip()
          i += 1
      line = line[1:-1]
      splt = line.split(' ')
      row = []
      for val in splt:
          row.append(float(val))
      
      ret.append(row)
      i += 1

    return np.array(ret)

if __name__ == '__main__':
    assert basepath_from_sim('TNG300-1') == '/n/hernquistfs3/IllustrisTNG/Runs/L205n2500TNG/'
    assert basepath_from_sim('TNG100-1') == '/n/hernquistfs3/IllustrisTNG/Runs/L75n1820TNG/'
    assert basepath_from_sim('TNG50-1') == '/n/hernquistfs3/IllustrisTNG/Runs/L35n2160TNG/'
    assert basepath_from_sim('TNG300-2-Dark') == '/n/hernquistfs3/IllustrisTNG/Runs/L205n1250TNG_DM/'

