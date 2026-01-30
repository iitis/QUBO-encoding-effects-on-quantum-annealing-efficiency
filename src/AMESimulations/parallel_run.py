import numpy as np
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

SIM_NPTS     = 32
SIM_PFX      = "big32"
SIM_TANNEAL  = 20
SIM_BETA     = 5.0
SIM_SUBSTEPS = 400
SIM_AME      = True

# Generate commands
command_list = []
for psum in np.logspace(-1, 1, SIM_NPTS):
    for ppair in np.logspace(-1, 1, SIM_NPTS):
        args = {
            'no_qbits': 4,
            'psum': psum,
            'ppair': ppair
        }            
        
        fn = f"../QUBO4JobShop/QUBOs/Collection32x32/instance_qbits{args['no_qbits']}_ppair{args['ppair']:.3f}_psum{args['psum']:.3f}.pkl"        
        nm = f"{SIM_PFX}_sweep_4q_t{SIM_TANNEAL}_b{SIM_BETA}_{args['ppair']:.3f}_{args['psum']:.3f}"
        
        # Check if result file already exists (execution was interrupted)
        if os.path.exists(f"./{SIM_PFX}_sweep_4q_t{SIM_TANNEAL}_b{SIM_BETA}_{args['ppair']:.3f}_{args['psum']:.3f}_AnnealTrace.npz"):
            continue
        
        if SIM_AME:
            command_list.append(f"julia ./AnnealSaveIntermediateStates.jl {fn} -n {nm} -t {SIM_TANNEAL} --beta {SIM_BETA} --solve-ame")
        else:
            command_list.append(f"julia ./AnnealSaveIntermediateStates.jl {fn} -n {nm} -t {SIM_TANNEAL} --beta {SIM_BETA} --substeps {SIM_SUBSTEPS}")            
            
def _run_command(command):
    subprocess.run(command, shell=True)
    print(f"FINISHED - '{command}'")
    
cpus = 32
with ProcessPoolExecutor(max_workers = cpus) as executor:
    futures = executor.map(_run_command, command_list)
    
# Processes will automatically wait for all tasks to complete
