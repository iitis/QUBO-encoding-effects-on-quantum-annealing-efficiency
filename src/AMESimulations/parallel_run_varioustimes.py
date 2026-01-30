import numpy as np
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

SIM_NPTS     = 10
SIM_PFX      = "variable"
SIM_TANNEALS = [10, 20, 30, 40, 50]#, 100, 200]
SIM_BETAS    = [1, 10, 100]
SIM_SUBSTEPS = 400

# Generate commands for forward and reverse annealing
command_list = []
for tanneal in SIM_TANNEALS:
    for penalty in np.logspace(-1, 1, SIM_NPTS)[:-1]:
        for beta in SIM_BETAS:
            args = {
                'no_qbits': 4,
                'psum': penalty,
                'ppair': penalty,
                'beta': beta
            }            
            
            fn = f"../QUBO4JobShop/QUBOs/Collection/instance_qbits{args['no_qbits']}_ppair{args['ppair']:.3f}_psum{args['psum']:.3f}.pkl"        
            nm_fwd = f"{SIM_PFX}_fwd_sweep_4q_t{tanneal}_b{args['beta']:.3f}_{args['ppair']:.3f}_{args['psum']:.3f}"
            nm_rev = f"{SIM_PFX}_rev_sweep_4q_t{tanneal}_b{args['beta']:.3f}_{args['ppair']:.3f}_{args['psum']:.3f}"
            
            # Check if result file already exists (execution was interrupted)
            if not os.path.exists(f"./{nm_fwd}_AnnealTrace.npz"):
                command_list.append(f"julia ./AnnealSaveIntermediateStates.jl {fn} -n {nm_fwd} -t {tanneal} --beta {args['beta']} --solve-ame")
            else:
                print(f"Skipping ./{nm_fwd}_AnnealTrace.npz")
            if not os.path.exists(f"./{nm_rev}_AnnealTrace.npz"):
                command_list.append(f"julia ./AnnealSaveIntermediateStates.jl {fn} -n {nm_rev} -t {tanneal} --beta {args['beta']} --reverse-anneal-point 0.5 --solve-ame")                
            else:
                print(f"Skipping ./{nm_rev}_AnnealTrace.npz")
            
def _run_command(command):
    subprocess.run(command, shell=True)
    print(f"FINISHED - '{command}'")
    
cpus = 32
with ProcessPoolExecutor(max_workers = cpus) as executor:
    futures = executor.map(_run_command, command_list)
    
# Processes will automatically wait for all tasks to complete
