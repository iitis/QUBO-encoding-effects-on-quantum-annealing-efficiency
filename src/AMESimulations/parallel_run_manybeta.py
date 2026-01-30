import numpy as np
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

SIM_NPTS     = 32
SIM_PFX      = "beta32"
SIM_TANNEAL  = 20
SIM_BETAS    = [1, 10, 100, 1000]
SIM_SUBSTEPS = 400

# Generate commands for forward and reverse annealing
command_list = []
for psum in np.logspace(-1, 1, SIM_NPTS):
    for ppair in np.logspace(-1, 1, SIM_NPTS):
        for beta in SIM_BETAS:
            args = {
                'no_qbits': 4,
                'psum': psum,
                'ppair': ppair,
                'beta': beta
            }            
            
            fn = f"../QUBO4JobShop/QUBOs/Collection32x32/instance_qbits{args['no_qbits']}_ppair{args['ppair']:.3f}_psum{args['psum']:.3f}.pkl"        
            nm_fwd = f"{SIM_PFX}_fwd_sweep_4q_t{SIM_TANNEAL}_b{args['beta']:.3f}_{args['ppair']:.3f}_{args['psum']:.3f}"
            nm_rev = f"{SIM_PFX}_rev_sweep_4q_t{SIM_TANNEAL}_b{args['beta']:.3f}_{args['ppair']:.3f}_{args['psum']:.3f}"
            
            # Check if result file already exists (execution was interrupted)
            if not os.path.exists(f"./{nm_fwd}_AnnealTrace.npz"):
                command_list.append(f"julia ./AnnealSaveIntermediateStates.jl {fn} -n {nm_fwd} -t {SIM_TANNEAL} --beta {args['beta']} --solve-ame")
            if not os.path.exists(f"./{nm_rev}_AnnealTrace.npz"):
                command_list.append(f"julia ./AnnealSaveIntermediateStates.jl {fn} -n {nm_rev} -t {SIM_TANNEAL} --beta {args['beta']} --reverse-anneal-point 0.5 --solve-ame")                
            
def _run_command(command):
    subprocess.run(command, shell=True)
    print(f"FINISHED - '{command}'")
    
cpus = 32
with ProcessPoolExecutor(max_workers = cpus) as executor:
    futures = executor.map(_run_command, command_list)
    
# Processes will automatically wait for all tasks to complete
