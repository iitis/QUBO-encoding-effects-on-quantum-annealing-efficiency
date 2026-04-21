# Effects of QUBO encoding on the thermodynamics of quantum annealers

JobShop scheduling provides a powerful framework for allocating limited resources to sequences of tasks under precedence and timing constraints, making it essential in many complex operational settings. In public transport, JSS principles underpin timetabling, rolling-stock rotation, crew scheduling, and maintenance planning, where vehicles and staff must follow ordered task chains while sharing constrained infrastructure. The flexibility of JSS formulations allows the modeling of vehicle dispatching, depot operations, headway management, and multimodal coordination, especially when disruptions require rapid rescheduling. Beyond transport, job-shop scheduling is widely used in manufacturing, logistics, energy systems, and service operations, where it supports efficient throughput, reduced waiting times, and robust resource utilization.

Quantum annealing is a key paradigm in quantum computing that can be applied to solve a wide range of problems. This is done by transforming any given problem into the form of a quadratic unconstrained binary optimization (QUBO) problem.
We focus on a specific JobShop scheduling problem and examine how different encodings of this problem in QUBO form lead to different behavior when solved with quantum annealing. 
Through a combination of experiments on a D-Wave device and numerical simulations of the annealing process, we investigate the relationship between the accuracy of the solution and the efficiency of the annealer, which is interpreted as a thermodynamic machine. 


# Project Structure

```src``` – contains the code for solving JobShob problems on a quantum device and analysis of the thermodynamics of quantum annealers.
1. ```src/QUBO4JobShop``` - Scripts to generate JobShop problems for various problem sizes. For details, see ```src/QUBO4JobShop/REAMDE.md```
2. ```src/ClassicalSimulations``` - Scripts to solve QUBOs using the classical solvers provided by the D-Wave Ocean SDK and visualize the results.
3. ```src/AMESimulations``` - Code to simulate the quantum annealing process as well as wrapper scripts to orchestrate numerical parameter sweeps. For additional details, see ```src/AMESimulations/README.md```
4. ```src/QUBO4JobShop/thermo.py``` - Script used to perform thermodynamical experiment on D-Wave quantum annealer
5. ```src/AMEAnalysis``` - Script to post-process simulation results and extract thermodynamic quantities.
6. ```src/Plotting``` - Scripts to plot post-processed simulation outputs, and to visualize features of the QUBO solution landscape.

# Funding

Scientific work co-financed from the state budget under the program of the Minister of Education and Science, Poland (pl. Polska) under the name "Science for Society II" project number NdS-II/SP/0336/2024/01 funding amount ```1000000``` PLN total value of the project ```1000000``` PLN 


