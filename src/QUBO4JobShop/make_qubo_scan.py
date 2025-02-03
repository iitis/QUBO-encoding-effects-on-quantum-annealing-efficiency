import pickle
import argparse
import numpy
import itertools

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


def create_QUBO_dict(args, instance, psum, ppair):
        
        JS = instance["js_problem"]

        qubo = Implement_QUBO(JS, psum=psum, ppair=ppair)
        qubo.make_QUBO()
        assert qubo.qubo_variables.size == args.no_qbits

        ground_states = []
        # check the solution given
        for sched in instance["ground_scheds"]:
            x = qubo.schedule_2_x(sched)
            ground_states.append(x)

            # check feasibility
            assert qubo.nonfeasible_pair_constraints(x) == 0
            assert qubo.nonfeasible_sum_constraint(x) == 0
            # check objective
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


    parser = argparse.ArgumentParser("mode of problem solving: computation /  output analysis")

    parser.add_argument(
        "--no_qbits",
        type=int,
        help="number of qbits",
        default=10,
    )

    parser.add_argument(
        "--no_points",
        type=int,
        help="number of penalty values to scan",
        default=10,
    )

    parser.add_argument(
        "--psum_min",
        type=float,
        help="sum penalty",
        default=2.,
    )

    parser.add_argument(
        "--psum_max",
        type=float,
        help="sum penalty",
        default=20.,
    )

    parser.add_argument(
        "--ppair_min",
        type=float,
        help="pair penalty",
        default=2.,
    )

    parser.add_argument(
        "--ppair_max",
        type=float,
        help="pair penalty",
        default=20.,
    )

    parser.add_argument(
        "--log",
        help="logarithmic spacing",
        action='store_true'
    )

    args = parser.parse_args()

    # such QUBO sizes are supported
    assert args.no_qbits in [4, 5, 6, 8, 10]

    if args.no_qbits == 4:
        instance = instance_4q()

    if args.no_qbits == 5:
        instance = instance_5q()

    if args.no_qbits == 6:
        instance = instance_6q()

    if args.no_qbits == 8:
        instance = instance_8q()
        
    if args.no_qbits == 10:
        instance = instance_10q()
    
    file = None
    psum_range = None
    ppair_range = None
    if args.log:
        file = f"QUBOs/many_instances_qbits{args.no_qbits}_npts{args.no_points}_ppair{args.ppair_min}_{args.ppair_max}_psum{args.psum_min}_{args.psum_max}_logspace.pkl"
        psum_range = numpy.logspace(numpy.log10(args.psum_min), numpy.log10(args.psum_max), args.no_points)
        ppair_range = numpy.logspace(numpy.log10(args.ppair_min), numpy.log10(args.ppair_max), args.no_points)
    else:
        file = f"QUBOs/many_instances_qbits{args.no_qbits}_npts{args.no_points}_ppair{args.ppair_min}_{args.ppair_max}_psum{args.psum_min}_{args.psum_max}.pkl"
        psum_range = numpy.linspace(args.psum_min, args.psum_max, args.no_points)
        ppair_range = numpy.linspace(args.ppair_min, args.ppair_max, args.no_points)

    all_qubos = []
    for (psum, ppair) in itertools.product(psum_range, ppair_range):
        d = create_QUBO_dict(args, instance, psum, ppair)
        JS = instance["js_problem"]

        all_qubos.append((psum, ppair, d))

    

    with open(file, 'wb') as fp:
        pickle.dump(all_qubos, fp)
