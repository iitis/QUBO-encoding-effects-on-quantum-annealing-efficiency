import math
import numpy as np
import pickle
import itertools as it

from tqdm import tqdm

def qd_get_nqubits(qdent):
    _, _, qd = qdent
    n = -1
    for ((i, j), w) in qd['qubo'].items():
        if max(i,j) > n:
            n = max(i, j)
    return n

def qd_classify_solutions(qdent, nqb, vecs):
    ps, pp, qd = qdent

    qmat = np.zeros((nqb, nqb), dtype=np.float64)
    for ((i, j), w) in qd['qubo'].items():
        qmat[i-1, j-1] = w

    omat = np.zeros((nqb, nqb), dtype=np.float64)
    for ((i, j), w) in qd['objective_part'].items():
        omat[i-1, j-1] = w

    results = []
    offset = float(qd['offset'])
    for v in vecs:
        energy    = float(v @ qmat @ v)
        objective = float(v @ omat @ v)
        # Feasible solutions have (energy + offset) == objective
        results.append([energy, math.isclose(energy + offset, objective)])

    return results

def compute_splitness(classified_solutions):
    energies_feas, energies_infeas = [], []
    for (e, feasible) in classified_solutions:#qd_classify_solutions(qdent, nqb, vecs):
        if feasible:
            energies_feas.append(e)
        else:
            energies_infeas.append(e)
    return (
        np.amin(energies_infeas) - np.amax(energies_feas),
        np.amin(energies_infeas) - np.amin(energies_feas)
    )

def load_compute_metrics(filename):
    with open(filename, 'rb') as inf:
        qd_list = pickle.load(inf)

    nqb = qd_get_nqubits(qd_list[0])

    # Get values of psum, ppair
    ps_set, pp_set = set(), set()
    for qde in qd_list:
        ps_set.add(float(qde[0]))
        pp_set.add(float(qde[1]))
    ps_range = sorted(list(ps_set))
    pp_range = sorted(list(pp_set))

    vecs = [np.array(v, dtype=np.float64) for v in it.product([0,1], repeat=nqb)]

    result_spl  = np.zeros((len(ps_range), len(pp_range)), dtype=np.float64)
    result_off  = np.zeros((len(ps_range), len(pp_range)), dtype=np.float64)
    result_objs = np.zeros((len(ps_range), len(pp_range), 16), dtype=np.float64)
    result_feas = np.zeros((len(ps_range), len(pp_range), 16), dtype=np.bool_) # np.bool deprecated
    for qde in tqdm(qd_list):
        classified_solutions = qd_classify_solutions(qde, nqb, vecs)
        spl, off = compute_splitness(classified_solutions)

        ps_idx = ps_range.index(float(qde[0]))
        pp_idx = pp_range.index(float(qde[1]))
        result_spl[pp_idx, ps_idx] = spl
        result_off[pp_idx, ps_idx] = off
        
        for n in range(16):
            result_objs[pp_idx, ps_idx, n] = classified_solutions[n][0]
            result_feas[pp_idx, ps_idx, n] = classified_solutions[n][1]

    return np.array(ps_range), np.array(pp_range), result_spl, result_off, result_objs, result_feas

for n in [4, 5, 6, 8, 10]:
    scan_fn = f"../QUBO4JobShop/QUBOs/Scans/many_instances_qbits{n}_npts300_ppair0.1_10.0_psum0.1_10.0_logspace.pkl"
    print(f"Running on {scan_fn}")

    ps_range, pp_range, spl, off, objs, feas = load_compute_metrics(scan_fn)

    resdict = {
        'ps_range': ps_range,
        'pp_range': pp_range,
        'splitness': spl,
        'offset': off,
        'objective_values': objs,
        'feasible': feas,
        'vectors': [np.array(v, dtype=np.float64) for v in it.product([0,1], repeat=n)]
    }
    with open(f"computed_splitness_{n}QB_v2.pkl", 'wb') as outf:
        pickle.dump(resdict, outf)
