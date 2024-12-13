import argparse
import itertools as it
import math
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pickle
from tqdm.auto import tqdm

def qubodict_get_nqubits(qd_entry):
    _, _, qd = qd_entry

    n = -1
    for ((i, j), w) in qd['qubo'].items():
        if max(i,j) > n:
            n = max(i,j)
    return n

def qubodict_get_matrix(qd_entry, num_qb):
    psum, ppair, qd = qd_entry

    q = np.zeros((num_qb, num_qb))
    for ((i,j), w) in qd['qubo'].items():
        q[i-1,j-1] = w
    return q

def qubodict_classify_solutions(qd_entry, num_qb, vecs):
    psum, ppair, qdict = qd_entry

    # QUBO matrix
    qmat = np.zeros((num_qb, num_qb), dtype=np.float64)
    for ((i,j), w) in qdict['qubo'].items():
        qmat[i-1,j-1] = w
        
    # Objective matrix
    omat = np.zeros((num_qb, num_qb), dtype=np.float64)
    for ((i,j), w) in qdict['objective_part'].items():
        omat[i-1,j-1] = w

    results = []
    offset = float(qdict['offset'])
    for v in vecs:
        # Energy, Objective
        energy    = float(v @ qmat @ v)
        objective = float(v @ omat @ v)

        # Feasible solutions have (energy + offset) == objective
        results.append([energy, math.isclose(energy + offset, objective)])
        
    return results

def compute_splitness(qd_entry, num_qb, vecs):
    energies_feas   = []
    energies_infeas = []
    for (e, feasible) in qubodict_classify_solutions(qd_entry, num_qb, vecs):
        if feasible:
            energies_feas.append(e)
        else:
            energies_infeas.append(e)
    return (
        np.amin(energies_infeas) - np.amax(energies_feas),
        np.amin(energies_infeas) - np.amin(energies_feas)
    )

def get_splitness_data(qd_list):
    num_qb = qubodict_get_nqubits(qd_list[0])
    
    # Pick out the values of psum, ppair
    psums  = set()
    ppairs = set()
    for qd_entry in qd_list:
        psums.add(float(qd_entry[0]))
        ppairs.add(float(qd_entry[1]))
    psums  = sorted(list(psums))
    ppairs = sorted(list(psums))

    vecs = [np.array(v, dtype=np.float64) for v in it.product([0,1], repeat=num_qb)]

    result_spl = np.zeros((len(psums), len(ppairs)), dtype=np.float64)
    result_off = np.zeros((len(psums), len(ppairs)), dtype=np.float64)            
    for qd_entry in tqdm(qd_list):
        splitness, offset = compute_splitness(qd_entry, num_qb, vecs)

        ps_idx = psums.index(float(qd_entry[0]))
        pp_idx = ppairs.index(float(qd_entry[1]))
        result_spl[pp_idx, ps_idx] = splitness
        result_off[pp_idx, ps_idx] = offset

    return np.array(psums), np.array(ppairs), result_spl, result_off

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Make 2D plots of how split the QUBO spectrum is vs. parameters")
    parser.add_argument("qubolist", help="pkl file containing list of (psum, ppair, qubo) tuples", type=str)
    parser.add_argument("outputfile", help="destination path for image", type=str)
    parser.add_argument("--log", help="use a log scale", action="store_true")
    args = parser.parse_args()
    
    ## Get the data
    with open(args.qubolist, 'rb') as inf:
        qd_list = pickle.load(inf)
    pss, pps, res_spl, res_off = get_splitness_data(qd_list)
    
    ## Make the plots
    fig, ax = plt.subplots(ncols=2, figsize=(15, 6))
    
    im = None
    if np.amin(res_spl) < 0 and np.amax(res_spl) > 0:
        im = ax[0].imshow(
            res_spl,
            extent=[pss[0], pss[-1], pps[0], pps[-1]],
            origin='lower', aspect='auto', interpolation='gaussian', cmap='bwr',
            norm=colors.TwoSlopeNorm(vmin=np.amin(res_spl), vmax=np.amax(res_spl), vcenter=0)
        )
        cb = fig.colorbar(im, ax=ax[0], aspect=30)
        cb.ax.set_ylabel("MIN[E(infeasible)] - MAX[E(feasible)]", fontsize=16)
        cb.ax.set_yticks([np.amin(res_spl), np.amin(res_spl)/2, 0, np.amax(res_spl)/2, np.amax(res_spl)])
    else:
        im = ax[0].imshow(
            res_spl,
            extent=[pss[0], pss[-1], pps[0], pps[-1]],
            origin='lower', aspect='auto', interpolation='gaussian', cmap='Reds',
            vmin=np.amin(res_spl), vmax=np.amax(res_spl),
        )
        cb = fig.colorbar(im, ax=ax[0], aspect=30)
        cb.ax.set_ylabel("MIN[E(infeasible)] - MAX[E(feasible)]", fontsize=16)
    ax[0].set_title("Splitness", fontsize=16)
    ax[0].set_xlabel("Sum penalty", fontsize=16)
    ax[0].set_ylabel("Pair penalty", fontsize=16)
    if args.log:
        ax[0].set_xscale('log')
        ax[0].set_yscale('log')
    
    im = None
    if np.amin(res_off) < 0 and np.amax(res_off) > 0:
        im = ax[1].imshow(
            res_off,
            extent=[pss[0], pss[-1], pps[0], pps[-1]],
            origin='lower', aspect='auto', interpolation='gaussian', cmap='bwr',
            norm=colors.TwoSlopeNorm(vmin=np.amin(res_off), vmax=np.amax(res_off), vcenter=0)
        )
        cb = fig.colorbar(im, ax=ax[1], aspect=30)
        cb.ax.set_ylabel("MIN[E(infeasible)] - MIN[E(feasible)]", fontsize=16)
        cb.ax.set_yticks([np.amin(res_off), np.amin(res_off)/2, 0, np.amax(res_off)/2, np.amax(res_off)])
    else:
        im = ax[1].imshow(
            res_off,
            extent=[pss[0], pss[-1], pps[0], pps[-1]],
            origin='lower', aspect='auto', interpolation='gaussian', cmap='Reds',
            vmin=np.amin(res_off), vmax=np.amax(res_off),
        )
        cb = fig.colorbar(im, ax=ax[1], aspect=30)
        cb.ax.set_ylabel("MIN[E(infeasible)] - MIN[E(feasible)]", fontsize=16)
    ax[1].set_title("Feasibility Offset", fontsize=16)
    ax[1].set_xlabel("Sum penalty", fontsize=16)
    ax[1].set_ylabel("Pair penalty", fontsize=16)
    if args.log:
        ax[1].set_xscale('log')
        ax[1].set_yscale('log')
    
    fig.savefig(args.outputfile, bbox_inches='tight', format='pdf')
