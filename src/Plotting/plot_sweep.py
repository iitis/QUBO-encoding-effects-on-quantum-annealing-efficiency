import matplotlib.pyplot as plt
import itertools as it
import numpy as np
import pickle
import csv
import os
import pickle

from qutip import *

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
    sweep_Ps = np.full((32, 32), np.nan)
    sweep_Os = np.full((32, 32), np.nan)
    for i, psum in enumerate(PENALTY_VALUES):
        for j, ppair in enumerate(PENALTY_VALUES):
            trace = traces_dict[(psum, ppair)]

            if trace is None:
                continue
            
            sweep_Ex[i,j] = trace['Et'][-1] - trace['GSEt'][-1]
            sweep_Wt[i,j] = sum(trace['Wt'])
            sweep_Wx[i,j] = sum(trace['Wt'] - trace['Wqst'])
            sweep_Qt[i,j] = sum(trace['Qt'])
            sweep_Ps[i,j] = trace['GPt'][-1]
            sweep_Os[i,j] = trace['Pt_comp'][-1][9]

    return {
        'Ex': sweep_Ex,
        'Wt': sweep_Wt,
        'Wx': sweep_Wx,
        'Qt': sweep_Qt,
        'Ps': sweep_Ps,
        'Os': sweep_Os
    }

def symmetric_extent(arr):
    xlo = np.abs(np.nanmin(arr))
    xhi = np.abs(np.nanmax(arr))
    extent = max(xlo, xhi)
    return {'vmin': -extent, 'vmax':extent}

def make_plot(outfile, data):
    fig, ax = plt.subplots(ncols=3, nrows=2, figsize=(18, 10), sharex=True, sharey=True)

    cmap1 = 'seismic'
    cmap2 = 'viridis'
    ax[0,0].imshow(data['Wt'], cmap=cmap1, origin='lower', interpolation='bicubic', **symmetric_extent(data['Wt']))
    ax[0,1].imshow(data['Qt'], cmap=cmap1, origin='lower', interpolation='bicubic', **symmetric_extent(data['Qt']))
    ax[1,0].imshow(data['Wx'], cmap=cmap1, origin='lower', interpolation='bicubic', **symmetric_extent(data['Wx']))
    ax[1,1].imshow(data['Ex'], cmap=cmap1, origin='lower', interpolation='bicubic', **symmetric_extent(data['Ex']))
    ax[0,2].imshow(data['Ps'], cmap=cmap2, origin='lower', interpolation='bicubic', vmin=0, vmax=1)
    ax[1,2].imshow(data['Os'], cmap=cmap2, origin='lower', interpolation='bicubic', vmin=0, vmax=1)

    print(f"{outfile}\t{symmetric_extent(data['Wt'])}")
    print(f"{outfile}\t{symmetric_extent(data['Qt'])}")
    print(f"{outfile}\t{symmetric_extent(data['Wx'])}")
    print(f"{outfile}\t{symmetric_extent(data['Ex'])}")
    print()

#    ax[0,0].set_xscale('log')
#    ax[0,0].set_yscale('log')
#
#    ax[0,0].pcolor(np.logspace(-1, 1, 32), np.logspace(-1, 1, 32), data['Wt'], cmap='magma')
#    ax[0,1].pcolor(np.logspace(-1, 1, 32), np.logspace(-1, 1, 32), data['Qt'], cmap='magma')
#    ax[1,0].pcolor(np.logspace(-1, 1, 32), np.logspace(-1, 1, 32), data['Wx'], cmap='magma')
#    ax[1,1].pcolor(np.logspace(-1, 1, 32), np.logspace(-1, 1, 32), data['Ex'], cmap='magma')#, vmin=0.12, vmax=1.16)
#    ax[0,2].pcolor(np.logspace(-1, 1, 32), np.logspace(-1, 1, 32), data['Ps'], cmap='magma', vmin=0.0, vmax=1.0)
#    ax[1,2].pcolor(np.logspace(-1, 1, 32), np.logspace(-1, 1, 32), data['Os'], cmap='magma', vmin=0.0, vmax=1.0)

    ax[0,0].set_title("Total Work", fontsize=14)
    ax[0,1].set_title("Total Heat", fontsize=14)
    ax[1,0].set_title("Nonadiabatic Work", fontsize=14)
    ax[1,1].set_title("Excess Energy", fontsize=14)
    ax[0,2].set_title("G.S. Probability", fontsize=14)
    ax[1,2].set_title("Opt. Sol. Probability", fontsize=14)

    fig.tight_layout()
    fig.savefig(outfile, format='pdf', bbox_inches='tight')

make_plot('sweep_fwd_b1.pdf'  , read_process_data('../AMEAnalysis/fwd/many_betas_b1_hightol.pkl'  ))
make_plot('sweep_fwd_b10.pdf' , read_process_data('../AMEAnalysis/fwd/many_betas_b10_hightol.pkl' ))
make_plot('sweep_fwd_b100.pdf', read_process_data('../AMEAnalysis/fwd/many_betas_b100_hightol.pkl'))
make_plot('sweep_rev_b1.pdf'  , read_process_data('../AMEAnalysis/rev/many_betas_b1_rev_hightol.pkl'  ))
make_plot('sweep_rev_b10.pdf' , read_process_data('../AMEAnalysis/rev/many_betas_b10_rev_hightol.pkl' ))
make_plot('sweep_rev_b100.pdf', read_process_data('../AMEAnalysis/rev/many_betas_b100_rev_hightol.pkl'))
