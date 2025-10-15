import itertools as it
import numpy as np
import pickle
import csv
import os
import pickle

from qutip import *

# Set when processing reverse-annealing simulations
REVERSE = False

def oplist(N, op):
    ops = []
    for n in range(N):
        tensor_oplist = N*[qeye(2)]
        tensor_oplist[n] = op
        ops.append(tensor(tensor_oplist))
    return ops

def read_qubo(fn):
    with open(fn, 'rb') as inf:
        qubo_dict = pickle.load(inf)
    
    X = oplist(4, sigmax())
    Z = oplist(4, sigmaz())
    I = qeye(4*[2])
    
    Hmix = -sum(X)
    Hcost = qzero(4*[2])
    for (i,j), coeff in qubo_dict['qubo'].items():
        if i == j:
            Hcost += coeff * (I - Z[i-1])/2
        else:
            Hcost += coeff * (I - Z[i-1])/2 * (I - Z[j-1])/2

    return Hmix, Hcost

DWAVE_slist = []
DWAVE_Alist = []
DWAVE_Blist = []

with open('./09-1273A-E_Advantage_system6_4_annealing_schedule_STANDARD.csv', 'r') as inf:
    reader = csv.DictReader(inf)
    for row in reader:
        DWAVE_slist.append(float(row['s']))
        DWAVE_Alist.append(float(row['A(s) (GHz)']))
        DWAVE_Blist.append(float(row['B(s) (GHz)']))

ATOL           = 1e-10
RTOL           = 1e-10
print(f"Using tolerances ({ATOL:e}, {RTOL:e})")

def lerp(x, x0, y0, x1, y1):
    return (1 - (x-x0)/(x1-x0))*y0 + ((x-x0)/(x1-x0))*y1

def remap_s(s, reverse=False, reverse_point=0.5):
    if not reverse:
        return s
    else:
        return 2*(1-reverse_point)*abs(1/2 - s) + reverse_point

def compute_trace_info(trace):    
    trace['Us'] = propagator(trace['Ht_func'], trace['tlist'], options=Options(atol=ATOL, rtol=RTOL, nsteps=10000))
    trace['instant_ψs'], trace['instant_Es'] = [], []
    trace['GSEt'] = np.zeros_like(trace['tlist'])
    for n, t in enumerate(trace['tlist']):
        Es, ψs = trace['Ht_func'](t, None).eigenstates()
        trace['instant_Es'].append(Es)
        trace['instant_ψs'].append(ψs)
        trace['GSEt'][n] = Es[0]
    
    trace['Pt_comp']   = np.array([ρ.diag() for ρ in trace['ρlist']])
    trace['Pt_energy'] = np.array([expect(ρ, ψs) for ρ, ψs in zip(trace['ρlist'], trace['instant_ψs'])])
    
    Hcost_lams, Hcost_vecs = trace['Hcost'].eigenstates()
    if abs(Hcost_lams[1] - Hcost_lams[0]) < 1e-6:
        trace['GPt'] = expect(Hcost_vecs[0].proj() + Hcost_vecs[1].proj(), trace['ρlist'])
    else:
        trace['GPt'] = expect(Hcost_vecs[0].proj(), trace['ρlist'])
    
    trace['Et'] = np.zeros_like(trace['tlist'])
    trace['Ct'] = np.zeros_like(trace['tlist'])
    for n in range(len(trace['tlist'])):
        trace['Et'][n] = expect(trace['Ht_func'](trace['tlist'][n], None), trace['ρlist'][n])
        trace['Ct'][n] = expect(trace['Hcost'], trace['ρlist'][n])
    
    trace['Δt']   = np.zeros_like(trace['tlist'])
    trace['Wt']   = np.zeros_like(trace['tlist'])
    trace['Qt']   = np.zeros_like(trace['tlist'])
    trace['Wqst'] = np.zeros_like(trace['tlist'])
    trace['Ft']   = np.zeros_like(trace['tlist'])
    trace['Ft'][0] = 1
    trace['St']   = np.zeros_like(trace['tlist'])
    trace['St'][0] = entropy_vn(trace['ρlist'][0])
    for n in range(1, len(trace['tlist'])):
        ti, tf = trace['tlist'][n-1], trace['tlist'][n]
        Hi, Hf = trace['Ht_func'](ti, None), trace['Ht_func'](tf, None)
        ρi, ρf = trace['ρlist'][n-1], trace['ρlist'][n]
        Ei, Ef = expect(Hi, ρi), expect(Hf, ρf)
    
        Uti2tf = trace['Us'][n]*trace['Us'][n-1].dag()
        ρf_unitary = Uti2tf * ρi * Uti2tf.dag()
        trace['Ft'][n] = fidelity(ρf, ρf_unitary)
        Ef_unitary = expect(Hf, ρf_unitary)
    
        Pi = [expect(ρi, ϕ) for ϕ in trace['instant_ψs'][n-1]]
        Ef_quasistatic = sum([Pi[k] * trace['instant_Es'][n][k] for k in range(2**4)])
    
        # real(...) is due to some minor precision issues leading to tiny imaginary parts
        trace['Δt'][n]   = np.real(Ef - Ei)
        trace['Wt'][n]   = np.real(Ef_unitary - Ei)
        trace['Wqst'][n] = np.real(Ef_quasistatic - Ei)
        trace['Qt'][n]   = np.real(trace['Δt'][n] - trace['Wt'][n])
        trace['St'][n]   = entropy_vn(ρf)

def process_penalty_values_beta(vals, beta, tanneal):
    psum, ppair = vals
    
    #####
    
    # Post processing requires the QUBO and the Julia output

    qubo_fn = f"../QUBO4JobShop/QUBOs/Collection/instance_qbits4_ppair{ppair:.3f}_psum{psum:.3f}.pkl"
    rhot_fn = f"../AMESimulations/variable_fwd_sweep_4q_t{tanneal}_b{beta:.3f}_{ppair:.3f}_{psum:.3f}_AnnealTrace.npz"

    #####

    if not os.path.exists(rhot_fn):
        # Skip any missing data files
        # This is necessary in case not all Julia simulations finish due to runtime constraints, etc.
        print(f"Missing results with psum = {psum:.3f}, ppair = {ppair:.3f}, beta = {beta}")
        return ((psum, ppair), None)
    
    trace_julia = {}
    with np.load(rhot_fn) as julia_data:
        # np.copy to force numpy to load all the data at once rather than lazily
        trace_julia['Tanneal'] = float(julia_data["T"])
        trace_julia['tlist']   = np.copy(julia_data["s"]) * float(julia_data["T"])
        ρdata = np.copy(julia_data["rho"]) 
        trace_julia['ρlist'] = [Qobj(ρdata[:,:,n], dims=[[2, 2, 2, 2], [2, 2, 2, 2]]) for n in range(len(trace_julia['tlist']))]

    # Fixup for a unit mismatch between Julia and Python
    trace_julia['Tanneal'] = np.pi * trace_julia['Tanneal']
    trace_julia['tlist']   = np.pi * trace_julia['tlist']
    
    Hmix, Hcost = read_qubo(qubo_fn)
    Ht = lambda t, _: np.interp(remap_s(t/trace_julia['Tanneal'], REVERSE), DWAVE_slist, DWAVE_Alist)*Hmix + \
                                np.interp(remap_s(t/trace_julia['Tanneal'], REVERSE), DWAVE_slist, DWAVE_Blist)*Hcost
    trace_julia['Hmix']    = Hmix
    trace_julia['Hcost']   = Hcost
    trace_julia['Ht_func'] = Ht
    
    compute_trace_info(trace_julia)
    # Annoyingly we run out of memory, so make some space
    del trace_julia['Ht_func'] # Can't pickle lambda functions anyway
    del trace_julia['ρlist']
    del trace_julia['Us']
    del trace_julia['instant_ψs']
    del trace_julia['instant_Es']

    return ((psum, ppair), trace_julia)

if __name__ == '__main__':

    ###
    # Process all Julia results, collect post-processed output in a dictionary and save it.
    ###

    for tanneal in [10, 20, 30, 40, 50, 100]:
        for beta in [1, 10, 100]:
                
            results = parallel_map(
                process_penalty_values_beta,
                [(p, p) for p in np.logspace(-1, 1, 10)],
                task_args=(beta, tanneal),
                progress_bar=True,
                num_cpus=32
            )

            results_as_dict = {}
            for k, v in results:
                results_as_dict[k] = v
    
            with open(f"variable_t{tanneal}_b{beta}_fwd.pkl", 'wb') as outf:
                pickle.dump(results_as_dict, outf)  




