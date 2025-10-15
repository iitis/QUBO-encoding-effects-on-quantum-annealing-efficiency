import dimod
import dwave.samplers
import numpy as np
import pickle
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

NUM_SAMPLES = 10000

def bits_to_str(bits):
    return ''.join(str(b) for b in bits)

def classically_solve_problem(qubo):
    results_dict = {}
    for sample in dimod.ExactSolver().sample(qubo).record:
        state_vars, energy, _ = sample
        results_dict[bits_to_str(state_vars)] = {
            'energy': float(energy),
            'sa_counts': 0,
            'pia_counts': 0,
            'rma_counts': 0
        }

    def _merge_sampleset(ss, key):
        for sample in ss.record:
            state_vars, _, _ = sample
            results_dict[bits_to_str(state_vars)][key] += 1

    _merge_sampleset(dimod.SimulatedAnnealingSampler().sample(qubo, num_reads=NUM_SAMPLES), 'sa_counts')
    _merge_sampleset(dwave.samplers.PathIntegralAnnealingSampler().sample(qubo, num_reads=NUM_SAMPLES), 'pia_counts')
    _merge_sampleset(dwave.samplers.RotorModelAnnealingSampler().sample(qubo, num_reads=NUM_SAMPLES), 'rma_counts')

    return results_dict

problem_tups = []
for psum in np.logspace(-1, 1, 100):
    for ppair in np.logspace(-1, 1, 100):
        args = {
            'no_qbits': 4,
            'psum': psum,
            'ppair': ppair
        }

        fn = f"../QUBO4JobShop/QUBOs/Collection100x100/instance_qbits{args['no_qbits']}_ppair{args['ppair']:.3f}_psum{args['psum']:.3f}.pkl"
        with open(fn, 'rb') as inf:
            qubo_dict = pickle.load(inf)
        problem_tups.append((psum, ppair, dimod.BQM(qubo_dict['qubo'], 'BINARY')))

def _do_problem(ptup):
    psum, ppair, qubo = ptup
    return (psum, ppair, classically_solve_problem(qubo))


all_results_list = []
with ProcessPoolExecutor(max_workers = 32) as executor:
    with tqdm(total=len(problem_tups)) as progress:
        futures = []
        for ptup in problem_tups:
            future = executor.submit(_do_problem, ptup)
            future.add_done_callback(lambda p: progress.update())
            futures.append(future)

        for future in futures:
            all_results_list.append(future.result())

all_results = {}
for psum, ppair, clsol in all_results_list:
    all_results[(psum, ppair)] = clsol

with open("classical_solutions_par.pkl", 'wb') as outf:
    pickle.dump(all_results, outf)
