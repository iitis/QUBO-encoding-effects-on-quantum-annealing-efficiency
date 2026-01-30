using ArgParse
using NPZ
using Plots
using Printf
using ProgressBars
using Serialization

include("LoadQUBOPkl.jl")
include("SolveQUBO_Precomp.jl")

###
# Read & configure parameters
###
s = ArgParseSettings("Solve a collection of QUBO by explicit simulation of quantum annealing.")

@add_arg_table! s begin
    "srcfile"
        arg_type = String
        help = "pickled list of Python dictionaries containing QUBOs to solve"
        required = true
    "--name", "-n"
        arg_type = String
        nargs = '?'
        help = "problem name, used to set result file names"
        default = ""
    "--beta"
        arg_type = Float64
        nargs = '?'
        help = "temperature of initial state"
    "--annealing-time", "-t"
        arg_type = Float64
        nargs = '?'
        help = "annealing time in ns"
        default = 10
    "--annealing-schedule"
        arg_type = String
        nargs = '?'
        help = "annealing schedule to follow, xslx format from D-Wave website"
        default = "./09-1273A-E_Advantage_system6_4_annealing_schedule.xlsx"
    "--reverse-anneal-point"
        arg_type = Float64
        nargs = '?'
        help = "Reverse anneal, sweep s from 1.0 -> p -> 1.0"
    "--reverse-anneal-pause-frac"
        arg_type = Float64
        nargs = '?'
        help = "Reverse anneal, fraction of time to wait at turnaround point"
        default = 0
    "--fast-anneal"
        action = :store_true
        help = "use 'Fast-Annealing Schedule' instead of 'Standard-Annealing Schedule'"
    "--solve-ame", "-s"
        action = :store_true
        help = "simulate using the adiabatic master equation"
    "--sparse"
        action = :store_true
        help = "use sparse matrices"
    "--substeps"
        arg_type = Int64
        nargs = '?'
        help = "how many substeps to take (should be a large multiple of the annealing time)"
        default = 400
    "--precomp-points"
        arg_type = Int64
        nargs = '?'
        help = "how many points to use when precomputing the Lamb shift"
        default = 100
end

parsed_args = parse_args(ARGS, s)
println("Solver arguments:")
for (key,val) in parsed_args
    println("  $key  =>  $(repr(val))")
end

@printf("Solver will run with %d threads.\n", Threads.threadpoolsize())

fn_output     = isempty(parsed_args["name"]) ? "AnnealTrace.bin" : parsed_args["name"] * "_AnnealTrace.bin"
fn_output_npz = isempty(parsed_args["name"]) ? "AnnealTrace.npz" : parsed_args["name"] * "_AnnealTrace.npz"

# Add keys that we will not use
parsed_args["initial-state"]    = nothing
parsed_args["plot-energies"]    = false
parsed_args["plot-schedule"]    = false
parsed_args["plot-populations"] = false

###
# Set up the problem
###
print("Reading problem...")
problem = LoadQUBOProblem(parsed_args["srcfile"])
nbits = QUBOHowManyQubits(problem)
@printf("Done! Problem has %d bits.\n", nbits)

print("Reading annealing schedule...")
schedule = AnnealingSchedule(parsed_args["annealing-schedule"], parsed_args["fast-anneal"])
println("Done!")

tf = parsed_args["annealing-time"]
s_range = LinRange(0, 1, parsed_args["substeps"])


annealing = SetUpAnnealingProblem(problem, schedule, parsed_args)
solution_dms = parsed_args["solve-ame"] ? SolveWithAME_dm_v2(annealing, tf, s_range, parsed_args["precomp-points"]) : SolveWithVN_dm(annealing, tf, s_range)

# *** Serialize results ***
#print("Serializing results...")
#Serialization.serialize(fn_output, solution_dms)
print("Saving NPZ...")
npzwrite(fn_output_npz, Dict("T" => tf, "s" => s_range, "rho" => cat(solution_dms..., dims=3)))
println("Done!")
