import matplotlib.pyplot as plt
import itertools as it
import numpy as np
import pickle
import csv
import os
import pickle

from matplotlib.colorbar import Colorbar
from mpl_toolkits.axes_grid1 import ImageGrid

BIG_TEXT   = 10     # Font size for plot titles
MED_TEXT   =  8     # Font size for axis labels
SMALL_TEXT =  7     # Font size for tick labels, legend labels, etc.
TINY_TEXT  =  6

plt.rcParams.update({
    "text.usetex": True, 
    "font.family": "serif", 
    "text.latex.preamble": r"\usepackage{amsmath}\usepackage{amssymb}",
    "axes.labelsize": MED_TEXT,
    "xtick.labelsize": SMALL_TEXT,
    "ytick.labelsize": SMALL_TEXT,
    "figure.dpi": 600
})

PENALTY_VALUES = [
    0.100, 0.116, 0.135, 0.156, 0.181, 0.210, 0.244, 0.283,
    0.328, 0.381, 0.442, 0.512, 0.595, 0.690, 0.800, 0.928,
    1.077, 1.250, 1.450, 1.682, 1.951, 2.264, 2.626, 3.047,
    3.535, 4.101, 4.758, 5.520, 6.404, 7.430, 8.620, 10.000
]

def read_process_data(srcfile):
    with open(srcfile, 'rb') as inf:
        traces_dict = pickle.load(inf)

    sweep_Ps = np.full((32, 32), np.nan)
    sweep_Os = np.full((32, 32), np.nan)
    for i, psum in enumerate(PENALTY_VALUES):
        for j, ppair in enumerate(PENALTY_VALUES):
            trace = traces_dict[(psum, ppair)]

            if trace is None:
                continue
            
            sweep_Ps[i,j] = trace['GPt'][-1]
            sweep_Os[i,j] = trace['Pt_comp'][-1][9]

    return {
        'Ps': sweep_Ps,
        'Os': sweep_Os
    }

def symmetric_extent(arr):
    xlo = np.abs(np.nanmin(arr))
    xhi = np.abs(np.nanmax(arr))
    extent = max(xlo, xhi)
    return {'vmin': -extent, 'vmax':extent}

def make_plot(outfile, data):
    print(f"make_plot({outfile}, ...)")

#    fig, ax = plt.subplots(figsize=(3.5, 1.3), ncols=2, sharex=True, sharey=True)

    fig = plt.figure(figsize=(3.5, 1.3), dpi=600)
    grid = ImageGrid(fig, 111, nrows_ncols=(1, 2), 
                    axes_pad=0.25, share_all=True, 
                    cbar_location='right', cbar_mode='single', cbar_size='7%', cbar_pad=0.15)

    plot_args = {
        'cmap': 'viridis',
        'origin': 'lower',
        'aspect': 'auto',
        'interpolation': 'bicubic',
        'vmin': 0,
        'vmax': 1
    }
    
    ax = grid    

    im02 = ax[0].imshow(data['Ps'], **plot_args)
    im12 = ax[1].imshow(data['Os'], **plot_args)

    ax[0].cax.cla()
    ax[1].cax.cla()
#    cb02 = fig.colorbar(im02, ax=ax[0], aspect=29)
#    cb12 = fig.colorbar(im12, ax=ax[1], aspect=29)
    cb12 = Colorbar(ax[1].cax, im12)

#    cb02.ax.tick_params(labelsize=TINY_TEXT)
    cb12.ax.tick_params(labelsize=TINY_TEXT)

#    ax[0].set_title("G.S. Probability", fontsize=MED_TEXT)
#    ax[1].set_title("Opt. Sol. Probability", fontsize=MED_TEXT)

    ax[0].set_ylabel(r"$P_{\rm sum}$", labelpad=-1)
    for the_ax in ax:#.flatten():
        the_ax.set_xlabel(r"$P_{\rm pair}$", labelpad=-0.1)
        the_ax.set_xticks([0, 31/2, 31])
        the_ax.set_xticklabels(["0.1", "1", "10"])
        the_ax.set_yticks([0, 31/2, 31])
        the_ax.set_yticklabels(["0.1", "1", "10"])
        
    ax[0].set_title(r"$P_{\rm g.s.}$", fontsize=MED_TEXT)
    ax[1].set_title(r"$P_{\rm opt.}$", fontsize=MED_TEXT)

    fig.subplots_adjust(wspace=0.2)

    fig.savefig(outfile + '_probs.pdf', format='pdf', bbox_inches='tight')
    fig.savefig(outfile + '_probs.png', format='png', bbox_inches='tight')

make_plot('sweep_fwd_b1'  , read_process_data('../AMEAnalysis/fwd/many_betas_b1_hightol.pkl'  ))
make_plot('sweep_fwd_b10' , read_process_data('../AMEAnalysis/fwd/many_betas_b10_hightol.pkl' ))
make_plot('sweep_fwd_b100', read_process_data('../AMEAnalysis/fwd/many_betas_b100_hightol.pkl'))
make_plot('sweep_rev_b1'  , read_process_data('../AMEAnalysis/rev/many_betas_b1_rev_hightol.pkl'  ))
make_plot('sweep_rev_b10' , read_process_data('../AMEAnalysis/rev/many_betas_b10_rev_hightol.pkl' ))
make_plot('sweep_rev_b100', read_process_data('../AMEAnalysis/rev/many_betas_b100_rev_hightol.pkl'))

PENALTY_VALUES = np.logspace(-1, 1, 32)
make_plot('sweep_ame_b10_pc100', read_process_data('../AMEAnalysis/ame32_100_t10_b10_fwd.pkl'))
make_plot('sweep_ame_b10_pc200', read_process_data('../AMEAnalysis/ame32_200_t10_b10_fwd.pkl'))
