import matplotlib
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
    "axes.titlesize": BIG_TEXT,
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

    sweep_Ex = np.full((32, 32), np.nan)
    sweep_Wt = np.full((32, 32), np.nan)
    sweep_Wx = np.full((32, 32), np.nan)
    sweep_Qt = np.full((32, 32), np.nan)
    for i, psum in enumerate(PENALTY_VALUES):
        for j, ppair in enumerate(PENALTY_VALUES):
            trace = traces_dict[(psum, ppair)]

            if trace is None:
                continue
            
            sweep_Ex[i,j] = trace['Et'][-1] - trace['GSEt'][-1]
            sweep_Wt[i,j] = sum(trace['Wt'])
            sweep_Wx[i,j] = sum(trace['Wt'] - trace['Wqst'])
            sweep_Qt[i,j] = sum(trace['Qt'])

    return {
        'Ex': sweep_Ex,
        'Wt': sweep_Wt,
        'Wx': sweep_Wx,
        'Qt': sweep_Qt,
    }

def symmetric_extent(arr):
    xlo = np.abs(np.nanmin(arr))
    xhi = np.abs(np.nanmax(arr))
    extent = max(xlo, xhi)
    return {'vmin': -extent, 'vmax':extent}

def make_plot(outfile, data):
    print(f"make_plot({outfile}, ...)")

#    fig, ax = plt.subplots(figsize=(7.0, 1.3), ncols=4, sharex=True, sharey=True)
    
    fig = plt.figure(figsize=(3.5, 3.3))
    grid = ImageGrid(fig, 111, nrows_ncols=(2, 2),
                     axes_pad=0.4, share_all=True,
                     cbar_location='right', cbar_mode='each', cbar_size='5%', cbar_pad=0.05)

    ax = grid

    plot_args = {
        'cmap': 'bwr',
        'origin': 'lower',
        'aspect': 'auto',
        'interpolation': 'bicubic',
    }

    im00 = ax[0].imshow(data['Wt'], **plot_args, **symmetric_extent(data['Wt']))
    im01 = ax[1].imshow(data['Qt'], **plot_args, **symmetric_extent(data['Qt']))
    im10 = ax[2].imshow(data['Wx'], **plot_args, **symmetric_extent(data['Wx']))
    im11 = ax[3].imshow(data['Ex'], **plot_args, **symmetric_extent(data['Ex']))

    ax[0].cax.cla()
    ax[1].cax.cla()
    ax[2].cax.cla()
    ax[3].cax.cla()
    cb00 = Colorbar(ax[0].cax, im00)
    cb01 = Colorbar(ax[1].cax, im01)
    cb10 = Colorbar(ax[2].cax, im10)
    cb11 = Colorbar(ax[3].cax, im11)


#    cb00 = fig.colorbar(im00, ax=ax[0], aspect=29)
#    cb01 = fig.colorbar(im01, ax=ax[1], aspect=29)
#    cb10 = fig.colorbar(im10, ax=ax[2], aspect=29)
#    cb11 = fig.colorbar(im11, ax=ax[3], aspect=29)

    cb00.ax.tick_params(labelsize=TINY_TEXT, length=2, pad=2)
    cb01.ax.tick_params(labelsize=TINY_TEXT, length=2, pad=2)
    cb10.ax.tick_params(labelsize=TINY_TEXT, length=2, pad=2)
    cb11.ax.tick_params(labelsize=TINY_TEXT, length=2, pad=2)

    cb00.ax.set_ylim(np.nanmin(data['Wt']), np.nanmax(data['Wt']))
    cb01.ax.set_ylim(np.nanmin(data['Qt']), np.nanmax(data['Qt']))
    cb10.ax.set_ylim(np.nanmin(data['Wx']), np.nanmax(data['Wx']))
    cb11.ax.set_ylim(np.nanmin(data['Ex']), np.nanmax(data['Ex']))

    ax[0].set_title(r"$W_{\rm tot}$")
    ax[1].set_title(r"$Q_{\rm tot}$")
    ax[2].set_title(r"$W_{\rm ex}$")
    ax[3].set_title(r"$E_{\rm ex}$")

    ax[0].set_ylabel(r"$P_{\rm sum}$", labelpad=-1)
    ax[2].set_ylabel(r"$P_{\rm sum}$", labelpad=-1)
    ax[2].set_xlabel(r"$P_{\rm pair}$", labelpad=-0.1)
    ax[3].set_xlabel(r"$P_{\rm pair}$", labelpad=-0.1)
    for the_ax in ax:#.flatten():
        the_ax.set_xticks([0, 31/2, 31])
        the_ax.set_xticklabels(["0.1", "1", "10"])
        the_ax.set_yticks([0, 31/2, 31])
        the_ax.set_yticklabels(["0.1", "1", "10"])

    fig.subplots_adjust(hspace=-1.0)
    fig.savefig(outfile + '_thermo_2x2.pdf', format='pdf', bbox_inches='tight')
    fig.savefig(outfile + '_thermo_2x2.png', format='png', bbox_inches='tight')

make_plot('sweep_fwd_b1'  , read_process_data('../AMEAnalysis/fwd/many_betas_b1_hightol.pkl'  ))
make_plot('sweep_fwd_b10' , read_process_data('../AMEAnalysis/fwd/many_betas_b10_hightol.pkl' ))
make_plot('sweep_fwd_b100', read_process_data('../AMEAnalysis/fwd/many_betas_b100_hightol.pkl'))
make_plot('sweep_rev_b1'  , read_process_data('../AMEAnalysis/rev/many_betas_b1_rev_hightol.pkl'  ))
make_plot('sweep_rev_b10' , read_process_data('../AMEAnalysis/rev/many_betas_b10_rev_hightol.pkl' ))
make_plot('sweep_rev_b100', read_process_data('../AMEAnalysis/rev/many_betas_b100_rev_hightol.pkl'))

PENALTY_VALUES = np.logspace(-1, 1, 32)
make_plot('sweep_ame_b10_pc100', read_process_data('../AMEAnalysis/ame32_100_t10_b10_fwd.pkl'))
make_plot('sweep_ame_b10_pc200', read_process_data('../AMEAnalysis/ame32_200_t10_b10_fwd.pkl'))
