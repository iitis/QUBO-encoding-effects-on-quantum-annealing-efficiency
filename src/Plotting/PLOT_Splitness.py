import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pickle
import itertools as it

from tqdm import tqdm

matplotlib.rc('axes', axisbelow=True)
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('figure', dpi=600)
BIG_TEXT   = 12     # Font size for plot titles
MED_TEXT   = 10     # Font size for axis labels
SMALL_TEXT =  8     # Font size for tick labels, legend labels, etc.
TINY_TEXT  =  7

cmap_bluered = colors.LinearSegmentedColormap('BlueRedSplit', {
    'red':      ((0.0, 0.0, 0.0), (0.25, 0.0, 0.0), (0.5, 0.8, 1.0), (0.75, 1.0, 1.0), (1.0, 0.4, 1.0)),
    'green':    ((0.0, 0.0, 0.0), (0.25, 0.0, 0.0), (0.5, 0.9, 0.9), (0.75, 0.0, 0.0), (1.0, 0.0, 0.0)),
    'blue':     ((0.0, 0.0, 0.4), (0.25, 1.0, 1.0), (0.5, 1.0, 0.8), (0.75, 0.0, 0.0), (1.0, 0.0, 0.0))
})

for n in [4, 5, 6, 8, 10]:
    print(f"Processing n = {n}...")
    with open(f"./computed_splitness_{n}QB.pkl", 'rb') as inf:
        data = pickle.load(inf)
        ps_range = data['ps_range']
        pp_range = data['pp_range']
        spl = np.transpose(data['splitness'])
        off = np.transpose(data['offset'])

    fig, ax = plt.subplots(figsize=(3.5, 1.3), ncols=2, sharex=True, sharey=True, dpi=600)

    plot_args = {
        'cmap': 'bwr'
    }

    def make_norm(arr, symmetric=False):
        if symmetric:
            extent = max(abs(np.amin(arr)), abs(np.amax(arr)))
            return colors.TwoSlopeNorm(vmin=-extent, vmax=extent, vcenter=0)
        else:
            return colors.TwoSlopeNorm(vmin=np.amin(arr), vmax=np.amax(arr), vcenter=0)

    ax[0].set_ylabel(r"$p_{\rm sum}$", fontsize=MED_TEXT, labelpad=-1)
    for the_ax in ax:
        the_ax.set_xlabel(r"$p_{\rm pair}$", fontsize=MED_TEXT)
        the_ax.set_xscale('log')
        the_ax.set_yscale('log')
        the_ax.tick_params(which='major', direction='out', size=2, labelsize=SMALL_TEXT)

    im_spl = ax[1].pcolor(pp_range, ps_range, spl, norm=make_norm(spl, symmetric=True), **plot_args)
    im_off = ax[0].pcolor(pp_range, ps_range, off, norm=make_norm(off, symmetric=True), **plot_args)

    cb_spl = fig.colorbar(im_spl, ax=ax[1], aspect=30)
    cb_off = fig.colorbar(im_off, ax=ax[0], aspect=30)

    def cbticks(arr, symmetric=False):
        if symmetric:
            extent = max(abs(np.amin(arr)), abs(np.amax(arr)))
            return [-extent, 0, extent]
        else:
            return [np.amin(arr), 0, np.amax(arr)]

    cb_spl.ax.set_yticks(cbticks(spl, symmetric=True))
    cb_off.ax.set_yticks(cbticks(off, symmetric=True))
    for cb_ax in [cb_spl.ax, cb_off.ax]:
        cb_ax.tick_params(which='major', direction='out', size=1, labelsize=TINY_TEXT)

    ax[1].contour(pp_range, ps_range, spl, levels=[0], colors='black', linestyles='--', linewidths=0.5)
    ax[0].contour(pp_range, ps_range, off, levels=[0], colors='black', linestyles='--', linewidths=0.5)

    fig.subplots_adjust(wspace=0.2)

    fig.savefig(f"SplitnessGap{n}QB.png", format='png', bbox_inches='tight')
    fig.savefig(f"SplitnessGap{n}QB.pdf", format='pdf', bbox_inches='tight')
