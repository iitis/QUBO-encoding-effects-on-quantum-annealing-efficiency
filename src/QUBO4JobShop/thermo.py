import argparse
import itertools as it
import math
import numpy as np
import dimod
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from tqdm import tqdm
import pickle
from scipy import optimize
import networkx as nx
import minorminer
# --- Import instance generators and QUBO creator ---
from make_qubos import instance_4q, instance_5q, instance_6q, instance_8q, instance_10q, create_QUBO_dict

# --- Import helper routines from utils ---
from utils import pseudo_likelihood_dense, extend, vectorize, gibbs_sampling_ising

# --- Import D-Wave reverse annealing components ---
from dwave.system import DWaveSampler, EmbeddingComposite, FixedEmbeddingComposite

# --- Instance mapping ---
instance_funcs = {
    4: instance_4q,
    5: instance_5q,
    6: instance_6q,
    8: instance_8q,
    10: instance_10q,
}

# ---------------------------
# Helper Functions
# ---------------------------
def compute_Q_matrix(qd, n):
    """Build Q matrix from QUBO dict, ensuring symmetry for off-diagonals."""
    Q = np.zeros((n, n))
    # Detect base (0 or 1 indexing)
    keys = list(qd['qubo'].keys())
    base = 1 if min(min(i, j) for (i, j) in keys) == 1 else 0
    for (i, j), w in qd['qubo'].items():
        ib, jb = i - base, j - base
        Q[ib, jb] += w
        if i != j:
            Q[jb, ib] += w  # Symmetrize for correct Ising conversion
    return Q

def convert_Q_to_Ising(Q):
    """
    Convert a QUBO matrix Q (from binary formulation) to Ising parameters.
    Using mapping: x = (1+s)/2   =>  s = 2*x - 1.
    
    Then define, for each i:
       h_i = Q[i,i]/2 + (sum_{j != i} Q[i,j])/4,
    and for i ≠ j:
       J_{ij} = Q[i,j] / 4.
       
    Returns: h (array) and J (matrix)
    """
    n = Q.shape[0]
    h = np.zeros(n)
    J = np.zeros((n, n))
    for i in range(n):
        h[i] = Q[i, i] / 2 + (np.sum(Q[i, :]) - Q[i, i]) / 4
        for j in range(i+1, n):
            J[i, j] = Q[i, j] / 4
            J[j, i] = J[i, j]
    return h, J

def ising_dicts_from_arrays(h, J):
    """
    Convert h (array) and J (matrix) to dictionaries suitable for pseudo_likelihood.
    h_dict: keys are integers 0 .. n-1.
    J_dict: keys are tuples (i,j) for i != j.
    """
    h_dict = {i: h[i] for i in range(len(h))}
    J_dict = {}
    n = len(h)
    for i in range(n):
        for j in range(n):
            if i != j:
                J_dict[(i, j)] = J[i, j]
    return h_dict, J_dict

def binary_to_spin(v):
    """
    Convert a binary vector v in {0,1}^n to a spin configuration s in {-1,1}^n using s = 2*v - 1.
    """
    return 2 * v - 1

def compute_ising_energy(sample, h, J):
    """
    Compute the Ising energy of a sample.
    sample: dictionary mapping qubit indices to spins (-1 or +1) OR an array of spins.
    h: array of linear coefficients.
    J: matrix of quadratic coefficients.
    For an array s, energy E = sum_i h[i]*s[i] + sum_{i<j} J[i,j]*s[i]*s[j].
    """
    # If sample is a dict, convert to array in order of sorted keys.
    if isinstance(sample, dict):
        n = len(sample)
        s = np.array([sample[i] for i in range(n)], dtype=float)
    else:
        s = np.array(sample, dtype=float)
    n = len(s)
    E = np.dot(h, s)
    for i in range(n):
        for j in range(i+1, n):
            E += J[i, j] * s[i] * s[j]
    return E

def sample_energies_reverse(qdict, anneal_time, sampler, init_beta, s_a, **sampler_kwargs):
    """
    Uses reverse annealing via sample_ising to obtain samples from the Ising formulation.
    
    Steps:
      1. Convert the QUBO dictionary to an n x n Q matrix.
      2. Convert the Q matrix to Ising parameters h and J.
      3. Create dictionaries h_dict and J_dict.
      4. Generate an initial state via gibbs_sampling_ising from utils.py.
      5. Set the reverse annealing schedule.
      6. Call sampler.sample_ising with the anneal schedule and initial state.
      7. For each sample, compute the energy using the Ising Hamiltonian.
      
    Returns:
      energies: array of energies for each sample.
      samples_spin: list of spin configurations (each as a dict or array).
    """
    #Q_matrix = compute_Q_matrix(qdict, n)
    oset=qdict.get("offset",0.0)
    h_dict, J_dict, add_offset = dimod.qubo_to_ising(qdict["qubo"], offset=oset)
    bqm = dimod.BinaryQuadraticModel.from_ising(h_dict, J_dict, offset=add_offset)
    #h_dict, J_dict = ising_dicts_from_arrays(h_arr, J_arr)
    
    # Generate an initial state (using Gibbs sampling) for reverse annealing.
    # init_beta: a parameter for Gibbs sampling; gibbs_steps: number of Gibbs steps.
    #initial_state_dict = gibbs_sampling_ising(h_dict, J_dict, beta=init_beta, num_steps=10**4)
    
    # Define the reverse annealing schedule:
    anneal_schedule = [[0, 1], [anneal_time / 2, s_a], [anneal_time, 1]]
    energies = []
    samples_spin = []
    deltas = []
    # Call sample_ising with reverse annealing.
    initial_state_dict = gibbs_sampling_ising(h_dict, J_dict, beta=init_beta, num_steps=1000)
    E_init = float(bqm.energy(initial_state_dict))
    sampleset = sampler.sample_ising(h_dict, J_dict, num_reads=100, 
                                     initial_state=initial_state_dict,
                                     anneal_schedule=anneal_schedule,
                                     **sampler_kwargs
                                     )
    
    n = len(h_dict)
    # Iterate over samples (each sample is a dict mapping qubit to spin value)
    for sample, energy in sampleset.data(['sample', 'energy']):
        E_fin = float(bqm.energy(sample))
        deltas.append(E_fin - E_init)
        samples_spin.append(sample)
    #h_int = {i: h_dict[variables[i]] for i in range(len(variables))}
    #J_int = {(i, j): J_dict[(variables[i], variables[j])] for i in range(len(variables)) for j in range(len(variables)) if (variables[i], variables[j]) in J_dict}
    variables = list(sampleset.variables)
    return np.array(deltas), samples_spin, h_dict, J_dict, variables

# def optimize_beta(h_dict, J_dict, spin_samples, variables):
#     """
#     Optimize effective beta_eff by minimizing the pseudo_likelihood function (from utils.py).
#     spin_samples: an array of spin configurations (each as array or appropriate format).
#     Returns the optimized beta_eff.
#     """
#     def objective(beta):
#         return pseudo_likelihood_new(beta, h_dict, J_dict, spin_samples, variables=variables)
#     res = optimize.minimize(objective, x0=[1.0])
#     return res.x.item()

def optimize_beta(h_dict, J_dict, samples_spin):
    # Use a deterministic variable order
    variables = sorted(h_dict.keys(), key=lambda x: (not isinstance(x, int), x))
    pos = {lbl: i for i, lbl in enumerate(variables)}
    n = len(variables)

    # Stack samples in that order
    S = np.array([[s[lbl] for lbl in variables] for s in samples_spin], dtype=float)

    # Dense arrays aligned with 'variables'
    h_vec = np.zeros(n)
    for lbl, hval in h_dict.items():
        h_vec[pos[lbl]] = hval

    J_mat = np.zeros((n, n))
    for (a, b), w in J_dict.items():
        if a in pos and b in pos:
            J_mat[pos[a], pos[b]] = w
    # Symmetrize strictly, zero diagonal
    J_mat = np.triu(J_mat, 1)
    J_mat = J_mat + J_mat.T

    # Fit beta with a positive constraint if desired
    res = optimize.minimize(lambda b: pseudo_likelihood_dense(b, h_vec, J_mat, S), x0=[1.0])
    return float(res.x[0])


def _heuristic_chain_strength(h_dict, J_dict, factor=2.0):
    vals = [abs(v) for v in h_dict.values()]
    vals += [abs(w) for w in J_dict.values()]
    m = max(vals) if vals else 1.0
    return max(1.0, factor * m)

def _logical_graph_edges(h_dict, J_dict):
    """Return node set and edge list (u,v) where J[(u,v)] != 0 and u!=v."""
    nodes = set(h_dict.keys())
    edges = [(u, v) for (u, v), w in J_dict.items() if u != v and w != 0.0]
    return nodes, edges

def get_fixed_sampler_from_warmup_or_minorminer(qpu, h_ref, J_ref):
    """
    Try to retrieve an embedding from a 1-read warm-up **BQM** call.
    If not present, fall back to minorminer on the (unchanged) logical graph.
    Returns: (fixed_sampler, chain_strength, embedding)
    """
    embedding = None
    chain_strength = None

    # ---- Try warm-up on a BQM (EmbeddingComposite.sample(bqm, ...)) ----
    try:
        warm_sampler = EmbeddingComposite(qpu)
        bqm_ref = dimod.BinaryQuadraticModel.from_ising(h_ref, J_ref)  # BQM, not sample_ising
        warm_ss = warm_sampler.sample(bqm_ref, num_reads=1)
        emb_ctx = warm_ss.info.get("embedding_context", {})
        embedding = emb_ctx.get("embedding", None)
        chain_strength = emb_ctx.get("chain_strength", None)
    except Exception:
        embedding = None

    # ---- Fall back to minorminer if warm-up didn’t give us an embedding ----
    if not embedding:
        nodes, src_edges = _logical_graph_edges(h_ref, J_ref)
        # build target (hardware) graph from the sampler
        H = nx.Graph()
        H.add_nodes_from(qpu.nodelist)
        H.add_edges_from(qpu.edgelist)

        # Build a source graph with exactly your logical labels
        Gs = nx.Graph()
        Gs.add_nodes_from(nodes)
        Gs.add_edges_from(src_edges)

        embedding = minorminer.find_embedding(list(Gs.edges), list(H.edges))
        if not embedding:
            raise RuntimeError("Could not obtain an embedding via warm‑up or minorminer.")
        # chain_strength not known from minorminer path; pick a robust default
        chain_strength = _heuristic_chain_strength(h_ref, J_ref)

    # Safety net for chain_strength if warm-up path didn't provide it
    if chain_strength is None:
        chain_strength = _heuristic_chain_strength(h_ref, J_ref)

    fixed_sampler = FixedEmbeddingComposite(qpu, embedding)
    return fixed_sampler, chain_strength, embedding

# ---------------------------
# Main Routine
# ---------------------------
def main():

    # Create a grid for the penalty parameters.
    psum_vals = np.logspace(-1, 1, 30)
    ppair_vals = np.logspace(-1, 1, 30)

    #psum_vals = np.linspace(0.1,10,15)
    #ppair_vals = np.linspace(0.1,10,15)

    # Dictionaries to hold results:
    betas = {}       # Effective beta for each (instance_size, psum, ppair)
    energies = {}    # (mean energy, variance) for each combination
    Q_stats = {}     # (mean energy difference [E - ground_energy], variance)
    Q_dist = {}      # Full energy distribution for each combination

    # Initialize the D-Wave sampler with reverse annealing.
    qpu = DWaveSampler(
        solver='Advantage2_system1.7',
        token='julr-bf16fdadab879dbeb1960fe55070031134855957')

    # Loop by instance size
    for size in [10]:
        print(f"Processing instance size: {size}")
        instance = instance_funcs[size]()
        n_qb = size

        # ---------- WARM-UP: get one embedding for this size and reuse it ----------
        # Use a representative (same-graph) Ising created from the first grid point
        qubo_ref = create_QUBO_dict(n_qb, instance, float(1.0), float(1.0))  # any values that keep the same sparsity
        oset = qubo_ref.get("offset", 0.0)
        h_ref, J_ref, _ = dimod.qubo_to_ising(qubo_ref["qubo"], offset=oset)


        fixed_sampler, chain_strength, embedding = get_fixed_sampler_from_warmup_or_minorminer(qpu, h_ref, J_ref)
        # Build sampler kwargs once
        sampler_kwargs = {
            "reinitialize_state": True,        # avoid serial correlation across reads
            "chain_strength": chain_strength,  # use the one from warm-up or heuristic
        }
        for ta in [10, 100]:
            for init_beta in [1, 10, 100]:
                for sa in [0.15,0.27,0.35]:
                    for psum in tqdm(psum_vals, desc=f"Instance size {size} anneal {ta} beta {init_beta} sa {sa}"):
                        for ppair in ppair_vals:
                            qubo_dict = create_QUBO_dict(n_qb, instance, psum, ppair)
                            # Reverse-anneal with the fixed embedding
                            E_samples, samples_spin, h_int, J_int, variables = sample_energies_reverse(
                                qubo_dict, ta, fixed_sampler, init_beta, sa, **sampler_kwargs
                            )
                            Q_vec = E_samples
                            E_mean = float(np.mean(E_samples))
                            E_var  = float(np.var(E_samples))
                            energies[(size, psum, ppair, ta, init_beta, sa)] = (E_mean, E_var)
                            Q_stats[(size, psum, ppair, ta, init_beta, sa)]  = (float(np.mean(Q_vec)), float(np.var(Q_vec)))
                            Q_dist[(size, psum, ppair, ta, init_beta, sa)]   = Q_vec
                            beta_eff = optimize_beta(h_int, J_int, samples_spin)
                            betas[(size, psum, ppair, ta, init_beta, sa)] = beta_eff

        # Save per size
        with open(f"data/betas_reverse_dwave_{size}.pkl", "wb") as f:
            pickle.dump(betas, f)
        with open(f"data/energies_reverse_dwave_{size}.pkl", "wb") as f:
            pickle.dump(energies, f)
        with open(f"data/Q_stats_reverse_dwave_{size}.pkl", "wb") as f:
            pickle.dump(Q_stats, f)
        with open(f"data/Q_dist_reverse_dwave_{size}.pkl", "wb") as f:
            pickle.dump(Q_dist, f)

if __name__ == "__main__":
    main()