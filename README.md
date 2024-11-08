# Overview

Then encoding idea will be as follows.


1. JobShop parameters would be for each job: (S_j, r_j, d_j w_j and processing times) as in notes
2. The function that inputs the JobShop problem with all its parameters p_sum and p_pair, outputs QUBO
3. QUBOs can be solved on D-Wave (simulation and real)
4. Function that checks feasibility and return objective
5. Function that solves JobShop on ILP to have the ground state objective, and the ground state solution.



## to create QUBO please run 

```
python make_qubos.py --ppair 2 --psum 2 --no_qbits 10
```

Above parameters with default settings. QUBOSs are saved in ```./QUBOs``` directory, 
args are in the file name.

QUBO sizes (```--no_qbits```) of 4,5,6,8,10 qbits are supported.


## JobShop definition


## QUBO creation


## Quantum/simulated annealing


## ILP solution 
