import pickle
import argparse

from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import Implement_QUBO
from collections import OrderedDict


def instance_small():
    """ 10 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=1.0)

    JS = JobShop([J1, J2])

    ground_states = ([1,0,0,0,1,0,1,0,0,0], [0,1,0,0,1,0,1,0,0,0])

    ground_obj = 0.5
    return {"js_problem":JS, "ground_states": ground_states, "ground_obj": ground_obj}


def create_QUBO_dict(args, instance):
        
        JS = instance["js_problem"]

        qubo = Implement_QUBO(JS, psum = args.psum, ppair = args.ppair)
        qubo.make_QUBO()
        assert qubo.qubo_variables.size == args.no_qbits

        # check the solution given
        for x in instance["ground_states"]:
            assert qubo.compute_objective(x) == instance["ground_obj"]
            # check feasibility
            assert qubo.nonfeasible_pair_constraints(x) == 0
            assert qubo.nonfeasible_sum_constraint(x) == 0

        Q = qubo.qubo_terms

        return {"qubo": Q, "ground_states": instance["ground_states"], "ground_obj": instance["ground_obj"]}


if __name__ == "__main__":


    parser = argparse.ArgumentParser("mode of problem solving: computation /  output analysis")

    parser.add_argument(
        "--no_qbits",
        type=int,
        help="number of qbits",
        default=10,
    )


    parser.add_argument(
        "--psum",
        type=float,
        help="sum penalty",
        default=2.,
    )

    parser.add_argument(
        "--ppair",
        type=float,
        help="pair penalty",
        default=2.,
    )


    args = parser.parse_args()

    # such QUBO sizes are supported
    assert args.no_qbits in [10]
        
    if args.no_qbits == 10:
        instance = instance_small()
         
    d = create_QUBO_dict(args, instance)
    JS = instance["js_problem"]

    print(f"save QUBO of {args.no_qbits} qbits")
    print(f"ppair = {args.ppair}, psum = {args.psum} and maximal objective = {JS.max_obj} ")

    file = f"QUBOs/instance_qbits{args.no_qbits}_ppair{args.ppair}_psum{args.psum}.pkl"

    with open(file, 'wb') as fp:
        pickle.dump(d, fp)



