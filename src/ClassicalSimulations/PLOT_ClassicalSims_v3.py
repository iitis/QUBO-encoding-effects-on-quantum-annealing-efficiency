import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib
import numpy as np
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

NUM_SAMPLES = 10000
NPTS = 100

opt_solutions = {
    '4qb': ['1001'],
    '5qb': ['10010'],
    '6qb': ['101001']
}

ps_range = np.logspace(-1, 1, NPTS)
pp_range = np.logspace(-1, 1, NPTS)

def _process_result(test_result, opt_keys):
    gs_energy = np.amin([info['energy'] for info in test_result.values()])
    gs_keys = []
    for state, info in test_result.items():
        if abs(gs_energy - info['energy']) < 1e-6:
            gs_keys.append(state)

    result_sa = {'Pgs': 0.0, 'Pop': 0.0, 'Eavg': 0.0}
    result_pi = {'Pgs': 0.0, 'Pop': 0.0, 'Eavg': 0.0}
    result_rm = {'Pgs': 0.0, 'Pop': 0.0, 'Eavg': 0.0}

    for state, info in test_result.items():
        if state in gs_keys:
            result_sa['Pgs'] += info['sa_counts']  / NUM_SAMPLES
            result_pi['Pgs'] += info['pia_counts'] / NUM_SAMPLES
            result_rm['Pgs'] += info['rma_counts'] / NUM_SAMPLES
        if state in opt_keys:
            result_sa['Pop'] += info['sa_counts']  / NUM_SAMPLES
            result_pi['Pop'] += info['pia_counts'] / NUM_SAMPLES
            result_rm['Pop'] += info['rma_counts'] / NUM_SAMPLES            
        result_sa['Eavg'] += (info['energy'] - gs_energy) * (info['sa_counts']  / NUM_SAMPLES)
        result_pi['Eavg'] += (info['energy'] - gs_energy) * (info['pia_counts'] / NUM_SAMPLES)
        result_rm['Eavg'] += (info['energy'] - gs_energy) * (info['rma_counts'] / NUM_SAMPLES)

    return result_sa, result_pi, result_rm

def read_process(filename, opt_key):
    with open(filename, 'rb') as inf:
        results = pickle.load(inf)

    Pgs_sa, Pgs_pi, Pgs_rm = np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS))
    Pop_sa, Pop_pi, Pop_rm = np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS))
    Eav_sa, Eav_pi, Eav_rm = np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS))
    for i, psum in enumerate(ps_range):
        for j, ppair in enumerate(pp_range):
            rsa, rpi, rrm = _process_result(results[(psum, ppair)], opt_key)
            Pgs_sa[i,j] = rsa['Pgs']
            Pgs_pi[i,j] = rpi['Pgs']
            Pgs_rm[i,j] = rrm['Pgs']
            Pop_sa[i,j] = rsa['Pop']
            Pop_pi[i,j] = rpi['Pop']
            Pop_rm[i,j] = rrm['Pop']
            Eav_sa[i,j] = rsa['Eavg']
            Eav_pi[i,j] = rpi['Eavg']
            Eav_rm[i,j] = rrm['Eavg']

    return Pgs_sa, Pgs_pi, Pgs_rm

######################################
#### PLOT COMMANDS START HERE

def save_plot(prefix, Pgs_sa, Pgs_pi, Pgs_rm, offset_data):

    fig = plt.figure(figsize=(3.5, 3.3))
    grid = ImageGrid(fig, 111, nrows_ncols=(2, 2),
                     axes_pad=0.4, share_all=True,
                     cbar_location='right', cbar_mode='each', cbar_size='5%', cbar_pad=0.05)

    grid[0].set_title("Simulated Annealing", fontsize=MED_TEXT)
    grid[1].set_title("Path Integral Annealing", fontsize=MED_TEXT)
    grid[2].set_title("Rotor Model Annealing", fontsize=MED_TEXT)
    grid[3].set_title("Ground State Details", fontsize=MED_TEXT)

    grid[0].set_ylabel(r"$p_{\rm sum}$", fontsize=MED_TEXT, labelpad=-1)
    grid[2].set_ylabel(r"$p_{\rm sum}$", fontsize=MED_TEXT, labelpad=-1)    
    for the_ax in grid:
        the_ax.set_xlim(1e-1, 1e1)
        the_ax.set_ylim(1e-1, 1e1)
        the_ax.set_xscale('log')
        the_ax.set_yscale('log')
        the_ax.set_xlabel(r"$p_{\rm pair}$", fontsize=MED_TEXT)
        the_ax.tick_params(which='major', direction='out', size=2, labelsize=SMALL_TEXT)

    def make_norm(arr, symmetric=False):
        if symmetric:
            extent = max(abs(np.amin(arr)), abs(np.amax(arr)))
            return colors.TwoSlopeNorm(vmin=-extent, vmax=extent, vcenter=0)
        else:
            return colors.TwoSlopeNorm(vmin=np.amin(arr), vmax=np.amax(arr), vcenter=0)

    plot_args = {
        'cmap': 'viridis',
        'vmin': 0,
        'vmax': 1,
    }
    
    im0 = grid[0].pcolor(pp_range, ps_range, Pgs_sa, **plot_args)
    im1 = grid[1].pcolor(pp_range, ps_range, Pgs_pi, **plot_args)
    im2 = grid[2].pcolor(pp_range, ps_range, Pgs_rm, **plot_args)

    grid[0].cax.cla()
    grid[1].cax.cla()
    grid[2].cax.cla()
    cb00 = Colorbar(grid[0].cax, im0)
    cb01 = Colorbar(grid[1].cax, im1)
    cb10 = Colorbar(grid[2].cax, im2)
    cb00.ax.tick_params(labelsize=TINY_TEXT, length=2, pad=2)
    cb01.ax.tick_params(labelsize=TINY_TEXT, length=2, pad=2)
    cb10.ax.tick_params(labelsize=TINY_TEXT, length=2, pad=2)

    p_range = np.logspace(-1, 1, 500)

    grid[3].fill_between(p_range, 0.5, 1e1, p_range > 0.25, color='C0')
    grid[3].fill_between(p_range, np.minimum(2*p_range, 0.5), color='C2')
    grid[3].fill_betweenx(p_range, np.minimum(0.5*p_range, 0.25), color='C4')

    grid[3].plot(p_range[p_range < 0.25], 2*p_range[p_range < 0.25], color='black', linewidth=2, linestyle=':')
    grid[3].plot(p_range[p_range > 0.25], 2*p_range[p_range > 0.25], color='black', linewidth=2, linestyle=':')

    grid[3].vlines(0.25, 0.5, 1e1, color='black', linewidth=2, linestyle='-.')
    grid[3].vlines(0.25, 1e-1, 0.5, color='black', linewidth=2, linestyle='-.')

    grid[3].hlines(0.5, 0.25, 1e1, color='black', linewidth=2, linestyle='--')
    grid[3].hlines(0.5, 1e-1, 0.25, color='black', linewidth=2, linestyle='--')

    grid[3].annotate(r"${\rm I}$", (0.4, 0.8), xycoords='axes fraction', fontsize=TINY_TEXT)
    grid[3].annotate(r"${\rm III}$", (0.57, 0.15), xycoords='axes fraction', fontsize=TINY_TEXT)
    grid[3].annotate(r"${\rm II}$", (0.06, 0.66), xycoords='axes fraction', fontsize=TINY_TEXT)

    grid.cbar_axes[3].set_axis_off()

    fig.savefig(f"{prefix}_mix_v3.png", format='png', bbox_inches='tight')
    fig.savefig(f"{prefix}_mix_v3.pdf", format='pdf', bbox_inches='tight')

#########################################
#### Script

def get_offset_data(n):
    with open(f"../Plotting/computed_splitness_{n}QB.pkl", 'rb') as inf:
        data = pickle.load(inf)
        ps_range = data['ps_range']
        pp_range = data['pp_range']
        spl = np.transpose(data['splitness'])
        off = np.transpose(data['offset'])
    return pp_range, ps_range, off

#print("Plotting 4 qubit results...")
#save_plot("ClSims4QB", *read_process("classical_solutions_par.pkl", opt_solutions['4qb']), get_offset_data(4))

#print("Plotting 5 qubit results...")
#save_plot("ClSims5QB", *read_process("classical_solutions_par_5.pkl", opt_solutions['5qb']), get_offset_data(5))

print("Plotting 6 qubit results...")
save_plot("ClSims6QB", *read_process("classical_solutions_par_6.pkl", opt_solutions['6qb']), get_offset_data(6))
