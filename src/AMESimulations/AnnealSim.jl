using ArgParse
using CSV
using Printf
using Plots

include("LoadQUBOPkl.jl")
include("SolveQUBO.jl")

###
# Read & configure parameters
###
s = ArgParseSettings("Solve a QUBO by explicit simulation of quantum annealing.")

@add_arg_table! s begin
    "srcfile"
        arg_type = String
        help = "pickled Python dictionary containing QUBO to solve"
        required = true
    "--name", "-n"
        arg_type = String
        nargs = '?'
        help = "problem name, used to set result file names"
        default = ""
    "--initial-state"
        arg_type = String
        nargs = '?'
        help = "bitstring giving the initial state"
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
    "--plot-energies"
        action = :store_true
        help = "store a plot of the Ising Hamiltonian energies"
    "--plot-schedule"
        action = :store_true
        help = "store a plot of the annealing schedule"
    "--plot-populations"
        action = :store_true
        help = "store a plot of the state populations through the annealing process"
end

parsed_args = parse_args(ARGS, s)
println("Solver arguments:")
for (key,val) in parsed_args
    println("  $key  =>  $(repr(val))")
end

fn_energies    = isempty(parsed_args["name"]) ? "IsingEnergies.pdf" : parsed_args["name"] * "_IsingEnergies.pdf"
fn_populations = isempty(parsed_args["name"]) ? "FinalPopulations.pdf" : parsed_args["name"] * "_FinalPopulations.pdf"
fn_schedule    = isempty(parsed_args["name"]) ? "Schedule.pdf" : parsed_args["name"] * "_Schedule.pdf"
fn_remapfrac   = isempty(parsed_args["name"]) ? "Remapping.pdf" : parsed_args["name"] * "_Remapping.pdf"
fn_dataframe   = isempty(parsed_args["name"]) ? "FinalData.csv" : parsed_args["name"] * "_FinalData.csv"

###
# Set up the problem
###
print("Reading problem...")
problem = LoadQUBOProblem(parsed_args["srcfile"])

print("Reading annealing schedule...")
schedule = AnnealingSchedule(parsed_args["annealing-schedule"], parsed_args["fast-anneal"])

print("Setting up annealing problem...")
annealing = SetUpAnnealingProblem(problem, schedule, parsed_args)
println("Done!")

###
# Solve the problem 
###

tf = parsed_args["annealing-time"]
s_range = 0:0.0025:1

if parsed_args["plot-energies"]
    print("Plotting eigenenergies...")
    plot(
        H, 
        s_range, 
        2^QUBOHowManyQubits(problem), 
        linewidth=1,
        legend=false
    )
    title!("Hamiltonian Eigenenergies")
    savefig(fn_energies)
    println("Done!")
end

# *** Do the actual simulation ***
print("Running simulation...")
solution_pops = parsed_args["solve-ame"] ? SolveWithAME(annealing, tf, s_range) : SolveWithSE(annealing, tf, s_range)
println("Done!")

if parsed_args["plot-populations"]
    print("Plotting populations...")
    plot(
        s_range, 
        transpose(solution_pops),
        linewidth=1,
        legend=false
    )
    ylims!(0, 1)
    title!("Population Evolution")
    xlabel!("s")
    ylabel!("Population")
    savefig(fn_populations)
    println("Done!")
end

final_results = ExtractFinalResults(solution_pops)

# *** Save results to CSV file ***
print("Saving results...")
CSV.write(fn_dataframe, final_results; quotestrings=true)
println("Done!")

# *** Print some statistics to the terminal ***
println("\n*** Most likely results ***")
print(first(final_results, 8))
println()

final_results_infeasible = filter(:feasible => ==(false), final_results)
final_results_feasible   = filter(:feasible => ==(true),  final_results)
final_results_optimal    = filter(:energy => e -> isapprox(e, problem.opt_energy), final_results_feasible)

no_feas   = nrow(final_results_feasible)
no_sols   = nrow(final_results)
no_ground = nrow(final_results_optimal)

feas_prob   = sum(final_results_feasible.probability)
ground_prob = sum(final_results_optimal.probability)

@printf("Probability to reach feasible solution: %.6f\n", feas_prob)
@printf("Probability to reach ground state: %.6f\n", ground_prob)
println(".....................................................")
println("Ground state solution:  ", problem.ground_states)
@printf("Ground state energy: %.6f\n", problem.opt_energy)
println("total n.o. solutions: ", no_sols)
println("n.o. distinct ground states: ", no_ground)
println("n.o. distinct feasible sols: ", no_feas)
println()
