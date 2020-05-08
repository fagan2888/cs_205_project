import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import matplotlib as mpl
import numpy as np
from tqdm import tqdm

def init_axes():
    fig, ax = plt.subplots(1, 1, frameon=False)
    ax.axis('off')
    return fig, ax

def animate(frame, im_gas, im_tracer, data_gas, data_tracer, vmin):
    heatmap = data_gas[frame]
    im_gas.set_data(heatmap.T)

    heatmap = data_tracer[frame]
    heatmap[heatmap < vmin] = np.nan
    #print(heatmap)

    keys = np.where(heatmap < vmin)[0].flatten()
    #print(len(keys))

    im_tracer.set_data(heatmap.T)
    

    return (im_gas, im_tracer, data_gas, data_tracer)

def make_movie(data_gas, data_tracer, fout):
    fig, ax = init_axes()

    # ax.set_xlim(-width/2.0, width/2.0)
    # ax.set_ylim(-width/2.0, width/2.0)

    heatmap = data_gas[-1]
    im_gas = ax.imshow(heatmap.T, origin='lower', norm=mpl.colors.LogNorm())
    ax.set_facecolor('k')

    vmax = np.max(data_tracer) * 0.9
    vmin = 0.01 * vmax

    heatmap = data_tracer[-1]
    im_tracer = ax.imshow(heatmap.T, origin='lower', norm=mpl.colors.LogNorm(), alpha=0.9, cmap='autumn_r')
    cmap = mpl.cm.get_cmap()
    cmap.set_bad(alpha=0.0)
    #im_tracer = None

    nframes = np.shape(data_gas)[0]

    animation = FuncAnimation(fig, animate, tqdm(np.arange(nframes)), fargs=[im_gas, im_tracer, data_gas, data_tracer, vmin], interval=1000 / 24)

    animation.save(fout)

if __name__ == '__main__':
    data_gas = np.random.rand(240, 256, 256)
    for i in range(50):
        data_gas[i] = np.ones((256, 256))
    
    data_tracer = np.random.rand(240, 256, 256)
    weight = np.logspace(-5, 0, 240)
    for i in range(240):
        data_tracer[i] *= weight[i]

    fout = 'test.mp4'

    make_movie(data_gas, data_tracer, fout)
