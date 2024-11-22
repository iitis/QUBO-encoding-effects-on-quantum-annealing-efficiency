using ArgParse
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
    "--solve-ame", "-s"
        action = :store_true
        help = "simulate using the adiabatic master equation"
    "--plot-energies"
        action = :store_true
        help = "store a plot of the Ising Hamiltonian energies"
end

parsed_args = parse_args(ARGS, s)
println("Solver arguments:")
for (key,val) in parsed_args
    println("  $key  =>  $(repr(val))")
end

fn_energies    = isempty(parsed_args["name"]) ? "IsingEnergies.pdf" : parsed_args["name"] * "_IsingEnergies.pdf"
fn_populations = isempty(parsed_args["name"]) ? "FinalPopulations.pdf" : parsed_args["name"] * "_FinalPopulations.pdf"

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
function QUBO2Ising(qubo_dict, Nq)
    Hf   = zeros(Complex{Float64}, 2^Nq, 2^Nq)
    Heye = Matrix{Complex{Float64}}(I, 2^Nq, 2^Nq)
    for ((i,j), w) in qubo_dict
        if i == j
            # Si Si -> (I - Zi)/2
            Hf = Hf + (w/2)*Heye
            Hf = Hf + single_clause(["Z"], [i], -w/2, Nq)
        else
            # Si Sj -> (I - Zi - Zj - Zi Zj)/4
            Hf = Hf + (w/4)*Heye
            Hf = Hf + single_clause(["Z"], [i], -w/4, Nq)
            Hf = Hf + single_clause(["Z"], [j], -w/4, Nq)
            Hf = Hf + single_clause(["Z", "Z"], [i, j], w/4, Nq)
        end
    end
    Hf
end

# Set up Hamiltonian
print("Setting up annealing schedule...")
schedule = AnnealingSchedule(parsed_args["annealing-schedule"])
println("Done!")

print("Setting up Hamiltonian...")
H = DenseHamiltonian(
    [
        (s) -> schedule.A_func(s),
        (s) -> schedule.B_func(s)
    ],
    [
        (-1/2) * standard_driver(num_qubits),
        ( 1/2) * QUBO2Ising(problem.qubo, num_qubits)
    ],
    unit=:h # D-Wave annealing schedule has units of GHz
)
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
annealing = Annealing(
    H,
    ψi;
    coupling=bath_coupling,
    bath=bath
)
println("Done!")

###
# Solve the problem with the unitary solver and an annealing time of 10ns (for testing)
###
function SolveWithSE(annealing_problem, annealing_time, ss)
    println("Solving with Schrodinger equation...")
    sol_se = @time solve_schrodinger(annealing_problem, annealing_time, alg=Tsit5(), reltol=1e-9, abstol=1e-9)
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
    println("Solving adiabatic master equation, part 1 (Unitary)...")
    U = @time solve_unitary(annealing_problem, annealing_time, alg=Tsit5(), abstol=1e-9, reltol=1e-9)
    println("Solving adiabatic master equation, part 2 (Redfield)...")
    sol_ame = @time solve_redfield(annealing_problem, annealing_time, U; alg=Tsit5(), abstol=1e-9, reltol=1e-9)
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

println("\n*** Most likely results ***")
final_pops = solution_pops[:,end]
final_results = Dict{String, Float64}()
for idx = 0:(2^num_qubits-1)
    final_results[string(idx; base=2, pad=num_qubits)] = final_pops[idx+1]
end
sorted_final_results = sort(collect(final_results); by=x->x[2], rev=true) 

println("\tState\t\tProbability     Objective Value")
for (state, pop) in sorted_final_results[1:8]
    obj = EvaluateQUBOObjective(problem.qubo, state, num_qubits)
    @printf("\t%s\t\t%7.3f%%        %+.3f\n", state, 100*pop, obj)
    #@printf("\t%s\t\t%.6f\t\t%+.3f\n", state, pop, obj)
end

println("Target solution:  ", problem.ground_states)
@printf("Target objective: %.6f\n", problem.opt_objective)
println("\tNOTE: This value is offset by a quantity proportional to (penalty * num_jobs)")
print("\n")
