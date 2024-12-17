using ArgParse
using CSV
using DataFrames
using LinearAlgebra
using OpenQuantumTools
using OrdinaryDiffEq
using Printf
using Plots

include("LoadQUBOPkl.jl")
include("AnnealingSchedule.jl")


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
# Read the problem
###
problem = QUBOProblem(parsed_args["srcfile"])

# Work out how many qubits there are (compute the largest index in the Q matrix)
num_qubits = maximum(map(maximum, collect(keys(problem.qubo))))
println("QUBO encoding requires ", num_qubits, " qubits.")

###
# Set up the quantum annealing problem
###

# Translate the QUBO into an Ising Hamiltonian
function QUBO2Ising(qubo_dict, Nq; sparse=false)
    Heye = (1/Nq) * collective_operator("I", Nq; sp=sparse)
    Hf   = 0 * Heye
    for ((i,j), w) in qubo_dict
        if i == j
            # Si Si -> (I - Zi)/2
            Hf = Hf + (w/2)*Heye
            Hf = Hf + single_clause(["Z"], [i], -w/2, Nq; sp=sparse)
        else
            # Si Sj -> (I - Zi - Zj - Zi Zj)/4
            Hf = Hf + (w/4)*Heye
            Hf = Hf + single_clause(["Z"], [i], -w/4, Nq; sp=sparse)
            Hf = Hf + single_clause(["Z"], [j], -w/4, Nq; sp=sparse)
            Hf = Hf + single_clause(["Z", "Z"], [i, j], w/4, Nq; sp=sparse)
        end
    end
    Hf
end

# Set up Annealing schedule
print("Setting up annealing schedule...")
schedule = AnnealingSchedule(parsed_args["annealing-schedule"], parsed_args["fast-anneal"])

remap_s = (s) -> s
if parsed_args["reverse-anneal-point"] != nothing
    pause_point = parsed_args["reverse-anneal-point"]
    pause_time  = parsed_args["reverse-anneal-pause-frac"]

    @assert (pause_point >= 0 && pause_point < 1) "Reverse annealing turnaround point must be between 0 and 1"
    @assert (pause_time >= 0 && pause_time < 1) "Reverse annealing pause time must be between 0 and 1"

    function lerp(x::Float64, x0::Float64, y0::Float64, x1::Float64, y1::Float64)
        t = (x - x0) / (x1 - x0)
        return (1-t) * y0 + t * y1
    end

    tps = 0.5 - 0.5*pause_time
    tpe = 0.5 + 0.5*pause_time
    remap_s = function(t)
        if t < tps              # Region one, drop linearly from 1.0 to pause_point
            return lerp(t, 0.0, 1.0, tps, pause_point)        
        elseif t < tpe          # Region two, wait at pause point
            return pause_point
        else                    # Region three, rise linearly from pause_point to 1.0
            return lerp(t, tpe, pause_point, 1.0, 1.0)
        end
    end
end

if parsed_args["plot-schedule"]
    # Plot the annealing schedule
    print("Plotting schedule...")
    plot(
         schedule.s_range, 
         [schedule.A_values, schedule.B_values], 
         label=["A(s)" "B(s)"], 
         lw=2
    )
    title!("Annealing Schedule")
    xlabel!("s")
    ylabel!("Coupling (GHz)")
    savefig(fn_schedule)

    print("Plotting fraction...")
    plot(
         schedule.s_range,
         remap_s.(schedule.s_range),
         label="Remapped s",
         lw=2
    )
    title!("Remapped annealing paramter")
    xlabel!("s")
    ylabel!("s'")
    savefig(fn_remapfrac)
end
println("Done!")

# Set up Hamiltonian
print("Setting up Hamiltonian...")
if parsed_args["sparse"]
    print("Hamiltonian is SPARSE...")
    H = SparseHamiltonian(
        [
             (s) -> schedule.A_func(remap_s(s)),
             (s) -> schedule.B_func(remap_s(s))
        ],
        [
            (-1/2) * standard_driver(num_qubits; sp=true),
            ( 1/2) * QUBO2Ising(problem.qubo, num_qubits; sparse=true)
        ],
        unit=:h # D-Wave annealing schedule has units of GHz
    )
else
    print("Hamiltonian is DENSE...")
    H = DenseHamiltonian(
        [
             (s) -> schedule.A_func(remap_s(s)),
             (s) -> schedule.B_func(remap_s(s))
        ],
        [
            (-1/2) * standard_driver(num_qubits),
            ( 1/2) * QUBO2Ising(problem.qubo, num_qubits)
        ],
        unit=:h # D-Wave annealing schedule has units of GHz
    )
end
println("Done!")

# Set up the enviornment interaction
print("Setting up bath...")
bath_coupling = collective_coupling("Z", num_qubits)
η = 1e-4
fc = 4 # GHz
T = 16 # mK
bath = Ohmic(η, fc, T)
println("Done!")

# Annealing problem
print("Setting up annealing problem for solver...")
ψi = (1 / sqrt(2^num_qubits)) * ones(Complex{Float64}, 2^num_qubits)
if parsed_args["initial-state"] != nothing
    @assert (length(parsed_args["initial-state"]) == num_qubits) "State bitstring must match number of qubits"
    ψi = q_translate_state(parsed_args["initial-state"])
end

annealing = Annealing(
    H,
    ψi;
    coupling=bath_coupling,
    bath=bath
)
println("Done!")

###
# Solve the problem 
###
function SolveWithSE(annealing_problem, annealing_time, ss)
    # Vern7 appears to be fastest on the largest problem, only a tiny bit faster than Vern6
    println("Solving with Schrodinger equation...")
    sol_se = @time solve_schrodinger(annealing_problem, annealing_time, alg=Vern7(), reltol=1e-9, abstol=1e-9)
    println("Done!")

    populations = map(
        z -> abs(z)^2,
        reduce(
            hcat,
            sol_se.(tf * s_range)
        )
    )

    populations
end

function SolveWithAME(annealing_problem, annealing_time, ss)
    # Vern6 appears to be fastest on the 4 qubit problem, probably Vern7 is faster on larger problems
    println("Solving adiabatic master equation, part 1 (Unitary)...")
    U = @time solve_unitary(annealing_problem, annealing_time, alg=Vern6(), abstol=1e-9, reltol=1e-9)
    println("Solving adiabatic master equation, part 2 (Redfield)...")
    sol_ame = @time solve_redfield(annealing_problem, annealing_time, U; alg=Vern6(), abstol=1e-9, reltol=1e-9)
    println("Done!")

    populations = reduce(
        hcat, 
        map(
            ρ -> abs.(diag(ρ)), # Convert Complex64 to Float64, also fix spurious tiny negative values
            sol_ame.(tf * s_range)
        )
    )

    populations
end

tf = parsed_args["annealing-time"]
s_range = 0:0.0025:1

if parsed_args["plot-energies"]
    print("Plotting eigenenergies...")
    plot(
        H, 
        s_range, 
        2^num_qubits, 
        linewidth=1,
        legend=false
    )
    title!("Hamiltonian Eigenenergies")
    savefig(fn_energies)
    println("Done!")
end

# *** Do the actual simulation ***
solution_pops = parsed_args["solve-ame"] ? SolveWithAME(annealing, tf, s_range) : SolveWithSE(annealing, tf, s_range)

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

final_results = DataFrame(
    state = String[],
    probability = Float64[],
    energy = Float64[],
    objective = Float64[],
    feasible = Bool[]
)
final_pops = solution_pops[:,end]
for idx = 0:(2^num_qubits-1)
    state = string(idx; base=2, pad=num_qubits)
    push!(final_results,(
        state,
        final_pops[idx+1],
        EvaluateQUBOEnergy(problem.qubo, state),
        EvaluateQUBOEnergy(problem.obj_part_qubo, state),
        EvaluateFeasibility(problem.qubo, problem.obj_part_qubo, problem.offset, state)
    ))
end
sort!(final_results, [order(:probability, rev=true)])
final_results_infeasible = filter(:feasible => ==(false), final_results)
final_results_feasible   = filter(:feasible => ==(true),  final_results)
final_results_optimal    = filter(:energy => e -> isapprox(e, problem.opt_energy), final_results_feasible)

# *** Save results to CSV file ***
print("Saving results...")
CSV.write(fn_dataframe, final_results; quotestrings=true)
println("Done!")

# *** Print some statistics to the terminal ***
println("\n*** Most likely results ***")
print(first(final_results, 8))
println()

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
