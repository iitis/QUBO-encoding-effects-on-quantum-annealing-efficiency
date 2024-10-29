import pickle
import argparse

from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import Implement_QUBO
from collections import OrderedDict


print("1")

def instance_small():
    """ 10 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=1.0)

    JS = JobShop([J1, J2])

    ground_states = ([1,0,0,0,1,0,1,0,0,0], [0,1,0,0,1,0,1,0,0,0])

    ground_obj = 0.5
    return {"js_problem":JS, "ground_sols": ground_states, "ground_obj": ground_obj}


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
        
    if args.no_qbits == 10:
        instance = instance_small()
        JS = instance["js_problem"]
