import matplotlib.pyplot as plt
import itertools as it
import numpy as np
import pickle
import csv
import os
import pickle

from qutip import *

betas     = [1, 10, 100]
tanneals  = [10, 20, 30, 40, 50, 100] 
penalties = np.logspace(-1, 1, 10)

traces_dicts_fwd = {}
traces_dicts_rev = {}
for beta in betas:
    for tanneal in tanneals:
        with open(f"../../data/oct10/variable_t{tanneal}_b{beta}_fwd.pkl", 'rb') as inf:
            data = pickle.load(inf)
            d = dict()
            d['Ex'], d['Wt'], d['Wx'], d['Qt'], d['Ps'], d['Os'] = {}, {}, {}, {}, {}, {}
            for k, trace in data.items():
                if trace is None:
                    d['Ex'][k], d['Wt'][k], d['Wx'][k], d['Qt'][k], d['Ps'][k], d['Os'][k] = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
                    continue
                d['Ex'][k] = trace['Et'][-1] - trace['GSEt'][-1]
                d['Wt'][k] = sum(trace['Wt'])
                d['Wx'][k] = sum(trace['Wt'] - trace['Wqst'])
                d['Qt'][k] = sum(trace['Qt'])
                d['Ps'][k] = trace['GPt'][-1]
                d['Os'][k] = trace['Pt_comp'][-1][9]
            traces_dicts_fwd[(beta, tanneal)] = data | d
        with open(f"../../data/oct10/variable_t{tanneal}_b{beta}_rev.pkl", 'rb') as inf:
            data = pickle.load(inf)
            d = dict()
            d['Ex'] = {}
            d['Wt'] = {}
            d['Wx'] = {}
            d['Qt'] = {}
            d['Ps'] = {}
            d['Os'] = {}
            for k, trace in data.items():
                if trace is None:
                    continue
                d['Ex'][k] = trace['Et'][-1] - trace['GSEt'][-1]
                d['Wt'][k] = sum(trace['Wt'])
                d['Wx'][k] = sum(trace['Wt'] - trace['Wqst'])
                d['Qt'][k] = sum(trace['Qt'])
                d['Ps'][k] = trace['GPt'][-1]
                d['Os'][k] = trace['Pt_comp'][-1][9]
            traces_dicts_rev[(beta, tanneal)] = data | d

def make_plot(outfile, beta, reverse=False):
    fig, ax = plt.subplots(ncols=3, nrows=2, figsize=(18, 10))#, sharex=True, sharey=True)

    for TANNEAL in tanneals:
        if reverse:
            trace_dict = traces_dicts_rev[(beta, TANNEAL)]
        else: 
            trace_dict = traces_dicts_fwd[(beta, TANNEAL)]

        plot_penalties = []
        for p in penalties:
            if (p, p) in trace_dict['Wt'].keys():
                plot_penalties.append(p)

        ax[0,0].semilogx(plot_penalties, [trace_dict['Wt'][(p, p)] for p in plot_penalties])
        ax[0,1].semilogx(plot_penalties, [trace_dict['Qt'][(p, p)] for p in plot_penalties])
        ax[1,0].semilogx(plot_penalties, [trace_dict['Wx'][(p, p)] for p in plot_penalties])
        ax[1,1].semilogx(plot_penalties, [trace_dict['Ex'][(p, p)] for p in plot_penalties])
        ax[0,2].semilogx(plot_penalties, [trace_dict['Ps'][(p, p)] for p in plot_penalties])
        ax[1,2].semilogx(plot_penalties, [trace_dict['Os'][(p, p)] for p in plot_penalties])

    ax[0,0].set_title("Total Work", fontsize=14)
    ax[0,1].set_title("Total Heat", fontsize=14)
    ax[1,0].set_title("Nonadiabatic Work", fontsize=14)
    ax[1,1].set_title("Excess Energy", fontsize=14)
    ax[0,2].set_title("G.S. Probability", fontsize=14)
    ax[1,2].set_title("Opt. Sol. Probability", fontsize=14)

    fig.tight_layout()
    fig.savefig(outfile, format='pdf', bbox_inches='tight')

for beta in betas:
    make_plot(f'tanneal_fwd_b{beta}.pdf', beta, reverse=False)
    make_plot(f'tanneal_rev_b{beta}.pdf', beta, reverse=True)
