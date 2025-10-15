import matplotlib.pyplot as plt
import numpy as np
import pickle

NUM_SAMPLES = 10000
NPTS = 100

opt_keys = ['1001']

def _process_result(test_result):
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

with open("classical_solutions_par.pkl", 'rb') as inf:
    results = pickle.load(inf)

Pgs_sa, Pgs_pi, Pgs_rm = np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS))
Pop_sa, Pop_pi, Pop_rm = np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS))
Eav_sa, Eav_pi, Eav_rm = np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS)), np.zeros((NPTS, NPTS))
for i, psum in enumerate(np.logspace(-1, 1, NPTS)):
    for j, ppair in enumerate(np.logspace(-1, 1, NPTS)):
        rsa, rpi, rrm = _process_result(results[(psum, ppair)])
        Pgs_sa[i,j] = rsa['Pgs']
        Pgs_pi[i,j] = rpi['Pgs']
        Pgs_rm[i,j] = rrm['Pgs']
        Pop_sa[i,j] = rsa['Pop']
        Pop_pi[i,j] = rpi['Pop']
        Pop_rm[i,j] = rrm['Pop']
        Eav_sa[i,j] = rsa['Eavg']
        Eav_pi[i,j] = rpi['Eavg']
        Eav_rm[i,j] = rrm['Eavg']

fig, ax = plt.subplots(figsize=(18, 15), nrows=3, ncols=3, sharex=True, sharey=True, dpi=300)

ax[0,0].set_xscale('log')
ax[0,0].set_yscale('log')

ax[0,0].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Pgs_sa, cmap='magma', vmin=0, vmax=1)
ax[0,1].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Pgs_pi, cmap='magma', vmin=0, vmax=1)
ax[0,2].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Pgs_rm, cmap='magma', vmin=0, vmax=1)
ax[1,0].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Pop_sa, cmap='magma', vmin=0, vmax=1)
ax[1,1].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Pop_pi, cmap='magma', vmin=0, vmax=1)
ax[1,2].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Pop_rm, cmap='magma', vmin=0, vmax=1)
ax[2,0].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Eav_sa, cmap='magma')
ax[2,1].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Eav_pi, cmap='magma')
ax[2,2].pcolor(np.logspace(-1, 1, NPTS), np.logspace(-1, 1, NPTS), Eav_rm, cmap='magma')

ax[0,0].set_title("Simulated Annealing - P(g.s.)", fontsize=12)
ax[1,0].set_title("Simulated Annealing - P(opt.)", fontsize=12)
ax[2,0].set_title("Simulated Annealing - Avg. Excess E", fontsize=12)
ax[0,1].set_title("Path Integral Annealing - P(g.s.)", fontsize=12)
ax[1,1].set_title("Path Integral Annealing - P(opt.)", fontsize=12)
ax[2,1].set_title("Path Integral Annealing - Avg. Excess E", fontsize=12)
ax[0,2].set_title("Rotor Model Annealing - P(g.s.)", fontsize=12)
ax[1,2].set_title("Rotor Model Annealing - P(opt.)", fontsize=12)
ax[2,2].set_title("Rotor Model Annealing - Avg. Excess E", fontsize=12)

fig.savefig("output100.png", format='png', bbox_inches='tight')
