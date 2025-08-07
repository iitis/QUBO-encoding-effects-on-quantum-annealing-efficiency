import pickle
import argparse

from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import Implement_QUBO
from collections import OrderedDict


from instances import create_QUBO_dict
from instances import instance_4q, instance_5q, instance_6q, instance_8q, instance_10q

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
    assert args.no_qbits in [4, 5, 6, 8, 10]
    assert args.ppair > 0
    assert args.psum > 0

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
         
    d = create_QUBO_dict(args.no_qbits, instance, args.psum, args.ppair)
    JS = instance["js_problem"]

    print(f"save QUBO of {args.no_qbits} qbits")
    print(f"ppair = {args.ppair}, psum = {args.psum} and maximal objective = {JS.max_obj} ")

    file = f"QUBOs/instance_qbits{args.no_qbits}_ppair{args.ppair}_psum{args.psum}.pkl"

    with open(file, 'wb') as fp:
        pickle.dump(d, fp)



