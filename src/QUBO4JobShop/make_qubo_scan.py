import pickle
import argparse
import numpy
import itertools

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
        d = create_QUBO_dict(args.no_qbits, instance, psum, ppair)
        JS = instance["js_problem"]

        all_qubos.append((psum, ppair, d))

    

    with open(file, 'wb') as fp:
        pickle.dump(all_qubos, fp)
