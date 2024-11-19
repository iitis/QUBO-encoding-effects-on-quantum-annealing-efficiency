import itertools
import neal
import dimod
from operator import itemgetter
from JobShop_QUBO import QUBO_Variables, Implement_QUBO

# these are D-Wave modules

from dwave.system import EmbeddingComposite, DWaveSampler, LeapHybridSampler
from dwave.system.composites import FixedEmbeddingComposite
from minorminer import find_embedding


# D-Wave and solutions

# https://docs.ocean.dwavesys.com/projects/neal/en/latest/

def solve_on_DWave(Q:dict, no_runs:int, real:bool = False, hyb:bool = False, at:float = 0.):
    """ Solve  QUBO in Q on the D-Wave  """

    if hyb:
        bqm = dimod.BQM.from_qubo(Q)
        sampler = LeapHybridSampler()

        # sampler = LeapHybridSampler(tokel = "") one can add there token from D-Wave account
        #sampler.properties["minimum_time_limit_s"]  = 5 # by default it is 5, and can be set
        sampleset = sampler.sample(bqm)
    elif not real:
        s = neal.SimulatedAnnealingSampler()
        sampleset = s.sample_qubo(
            Q, beta_range = (0.01, 10), num_sweeps = 200,
            num_reads = no_runs, beta_schedule_type="geometric"
        )
    else:

        solver = DWaveSampler(solver="Advantage_system4.1")

        #solver = DWaveSampler(solver="Advantage_system4.1", token="")  one can add there token from D-Wave account

        __, target_edgelist, _ = solver.structure

        emb = find_embedding(Q, target_edgelist, verbose=1)

        no_logical = len(emb.keys())
        physical_qbits_lists = list(emb.values())
        physical_qbits_list = list(itertools.chain(*physical_qbits_lists))
        no_physical =  len( set(physical_qbits_list) )
        
        if no_logical < 70:
            print(emb)
        
        print("logical qbits = ", no_logical)

        print("physical qbits", no_physical)

        sampler = FixedEmbeddingComposite(solver, emb)
        
        # Above can be automatic
        #sampler = EmbeddingComposite(DWaveSampler(solver="Advantage_system4.1", , token=""))


        sampleset = sampler.sample_qubo(
                Q,
                num_reads=no_runs,
                annealing_time=at
        )


    return sampleset


def dict_of_solutions(qubo, solutions, print_not_feasible:bool = False):
    """ checks feasibility and return the dict of feasible sols """
    sols = []

    if len(solutions[0]) == 4:
        for (sol, energy, occ, chain_strength) in solutions:

            broken_pairs = qubo.nonfeasible_pair_constraints(sol)
            broken_sum = qubo.nonfeasible_sum_constraint(sol)
            obj = qubo.compute_objective(sol)
            our_sol = {"broken_constr": broken_pairs+broken_sum, "obj": obj, "sol": sol}
            sols.append(our_sol)

            if print_not_feasible:
                print("...............")
                print("broken pair constraint", broken_pairs)
                print("broken sum constraint", broken_sum)

    elif len(solutions[0]) == 3:

        for (sol, energy, occ) in solutions:

            broken_pairs = qubo.nonfeasible_pair_constraints(sol)
            broken_sum = qubo.nonfeasible_sum_constraint(sol)
            obj = qubo.compute_objective(sol)

            our_sol = {"broken_constr": broken_pairs+broken_sum, "obj": obj, "sol": sol}
            sols.append(our_sol)

            if print_not_feasible:
                print("...............")
                print("broken pair constraint", broken_pairs)
                print("broken sum constraint", broken_sum)

    return sols



def sort_sols(sols):
    """ filter out non-feasible solutions and sort solutions according to objective """
    Y = list( filter(lambda x : x["broken_constr"] == 0, sols) )
    newlist = sorted(Y, key=itemgetter('obj'))

    print(len(newlist), "feasible solutions out of", len(sols))

    return newlist