import pickle
import argparse
import numpy as np

from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import Implement_QUBO
from collections import OrderedDict


def instance_4q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1}), release=1, due=3, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=3, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2)}, 2: {1: (2, 3)}}]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}

def instance_5q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1}), release=1, due=3, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=4, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2)}, 2: {1: (2, 3)}}]

    ground_obj = 0.25
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_6q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1, 2:1}), release=1, due=4, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=3, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2), 2:(2,3)}, 2: {1: (2, 3)}}]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_8q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1, 2:1}), release=1, due=4, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1, 3:1}), release=1, due=4, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2), 2: (2,3)}, 2: {1: (2, 3), 3:(3,4)}}]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_10q():
    """ 10 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=1.0)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 3), 2: (4, 6)}, 2: {2: (2, 4)}},
                        {1: {1: (2, 4), 2: (4, 6)}, 2: {2: (2, 4)}}
    ]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def create_QUBO_dict(args, instance):
        
        JS = instance["js_problem"]

        qubo = Implement_QUBO(JS, psum = args['psum'], ppair = args['ppair'])
        qubo.make_QUBO()
        assert qubo.qubo_variables.size == args['no_qbits']

        ground_states = []
        # check the solution given
        for sched in instance["ground_scheds"]:
            x = qubo.schedule_2_x(sched)
            ground_states.append(x)

            # check feasibility
            assert qubo.nonfeasible_pair_constraints(x) == 0
            assert qubo.nonfeasible_sum_constraint(x) == 0
            # check objective
            print("objective = ", qubo.compute_objective(x))
            assert qubo.compute_objective(x) == instance["ground_obj"]

            offset = qubo.compute_energy_offset(JS)

            energy = qubo.compute_objective(x) - offset

        Q = qubo.qubo_terms

        return {"qubo": Q,
                "objective_part": qubo.obj_terms,
                "ground_states": ground_states, 
                "ground_obj": instance["ground_obj"], 
                "ground_energy": energy, 
                "offset": offset}


if __name__ == "__main__":

    npts = 10
    for psum in np.logspace(-1, 1, npts):
        for ppair in np.logspace(-1, 1, npts):
            args = {
                'no_qbits': 4,
                'psum': psum,
                'ppair': ppair
            }            
         
            instance = instance_4q()
            d = create_QUBO_dict(args, instance)
            JS = instance["js_problem"]
        
            print(f"save QUBO of {args['no_qbits']} qbits")
            print(f"ppair = {args['ppair']:.3f}, psum = {args['psum']:.3f} and maximal objective = {JS.max_obj} ")
        
            file = f"QUBOs/Collection{npts}x{npts}/instance_qbits{args['no_qbits']}_ppair{args['ppair']:.3f}_psum{args['psum']:.3f}.pkl"
        
            with open(file, 'wb') as fp:
                pickle.dump(d, fp)



