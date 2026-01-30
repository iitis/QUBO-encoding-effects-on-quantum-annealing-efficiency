using ArgParse
using CSV
using Plots
using Printf
using ProgressBars
using Serialization

include("LoadQUBOPkl.jl")
include("SolveQUBO.jl")

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
end

parsed_args = parse_args(ARGS, s)
println("Solver arguments:")
for (key,val) in parsed_args
    println("  $key  =>  $(repr(val))")
end

@printf("Solver will run with %d threads.\n", Threads.threadpoolsize())

fn_output = isempty(parsed_args["name"]) ? "AllStatesData.bin" : parsed_args["name"] * "_AllStatesData.bin"

# Add keys that we will not use
parsed_args["plot-energies"]    = false
parsed_args["plot-schedule"]    = false
parsed_args["plot-populations"] = false

###
# Set up the problem
###
print("Reading problem...")
problem = LoadQUBOProblem(parsed_args["srcfile"])
@printf("Done!")

print("Reading annealing schedule...")
schedule = AnnealingSchedule(parsed_args["annealing-schedule"], parsed_args["fast-anneal"])
println("Done!")

tf = parsed_args["annealing-time"]
s_range = 0:0.0025:1

nbits = QUBOHowManyQubits(problem)

results_list = Vector{Any}(undef, 2^nbits)
# Threads.@threads :greedy 
for statenum in ProgressBar(1:2^nbits)
    # Convert the initial state number to a (little-endian) string of 0s and 1s
    parsed_args["initial-state"] = bitstring(statenum)[end - (nbits-1):end]

    annealing = SetUpAnnealingProblem(problem, schedule, parsed_args)
    solution_pops = parsed_args["solve-ame"] ? SolveWithAME(annealing, tf, s_range) : SolveWithSE(annealing, tf, s_range)

    results_list[statenum] = (
        initial_state = parsed_args["initial-state"],
        final_results = ExtractFinalResults(problem, solution_pops)
    )
end

# *** Save results to CSV file ***
print("Saving results...")
Serialization.serialize(fn_output, results_list)
println("Done!")
