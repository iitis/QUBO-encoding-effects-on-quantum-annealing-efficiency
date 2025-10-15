using DataFrames
using LinearAlgebra
using OpenQuantumTools
using OrdinaryDiffEq
using Printf
using Plots

include("LoadQUBOPkl.jl")
include("AnnealingSchedule.jl")

# Work out how many qubits this QUBO requires
function QUBOHowManyQubits(problem::QUBOProblem)
    maximum(map(maximum, collect(keys(problem.qubo))))
end

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

function MixerThermalState(Nq, beta)
    Hmix = (-1/2) * standard_driver(Nq)
    dm = exp(-beta * Hmix)
    
    dm / tr(dm)
end

function SetUpAnnealingProblem(problem, schedule, args)
    num_qubits = QUBOHowManyQubits(problem)

    # Set up Annealing schedule
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

    # Set up Hamiltonian
    if parsed_args["sparse"]
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

    # Set up the enviornment interaction
    bath_coupling = collective_coupling("Z", num_qubits)
    η = 1e-4
    fc = 4 # GHz
    T = 16 # mK
    bath = Ohmic(η, fc, T)

    # Annealing problem
    if parsed_args["beta"] != nothing
        if parsed_args["reverse-anneal-point"] != nothing
            println("Reverse annealing, initial thermal state is in basis of cost Hamiltonian")
            dm = exp(-parsed_args["beta"] * ( 1/2) * QUBO2Ising(problem.qubo, num_qubits))
        else
            dm = exp(-parsed_args["beta"] * (-1/2) * standard_driver(num_qubits))
        end
        annealing = Annealing(
            H,
            dm / tr(dm);
            coupling=bath_coupling,
            bath=bath
        )
    else
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
    end

    annealing
end



###
# Solve the problem 
###
function SolveWithSE(annealing_problem, annealing_time, ss)
    # Vern7 appears to be fastest on the largest problem, only a tiny bit faster than Vern6
    sol_se = solve_schrodinger(annealing_problem, annealing_time, alg=Vern9(), reltol=1e-9, abstol=1e-9)

    populations = map(
        z -> abs(z)^2,
        reduce(
            hcat,
            sol_se.(annealing_time * ss)
        )
    )

    populations
end

function SolveWithVN(annealing_problem, annealing_time, ss)
    sol_vn = solve_von_neumann(annealing_problem, annealing_time, alg=Vern9(), abstol=1e-9, reltol=1e-9)

    populations = reduce(
        hcat, 
        map(
            ρ -> abs.(diag(ρ)), # Convert Complex64 to Float64, also fix spurious tiny negative values
            sol_vn.(annealing_time * ss)
        )
    )

    populations
end

function SolveWithAME(annealing_problem, annealing_time, ss)
    # Vern6 appears to be fastest on the 4 qubit problem, probably Vern7 is faster on larger problems
    U = solve_unitary(annealing_problem, annealing_time, alg=Vern6(), abstol=1e-9, reltol=1e-9)
    sol_ame = solve_redfield(annealing_problem, annealing_time, U; alg=Vern6(), abstol=1e-9, reltol=1e-9)

    populations = reduce(
        hcat, 
        map(
            ρ -> abs.(diag(ρ)), # Convert Complex64 to Float64, also fix spurious tiny negative values
            sol_ame.(annealing_time * ss)
        )
    )

    populations
end

function SolveWithVN_dm(annealing_problem, annealing_time, ss)
    sol_vn = solve_von_neumann(annealing_problem, annealing_time, alg=Vern9(), abstol=1e-9, reltol=1e-9)
    
    sol_vn.(annealing_time * ss)
end

function SolveWithAME_dm(annealing_problem, annealing_time, ss)
    # Vern6 appears to be fastest on the 4 qubit problem, probably Vern7 is faster on larger problems
    U = solve_unitary(annealing_problem, annealing_time, alg=Vern6(), abstol=1e-9, reltol=1e-9)
    sol_ame = solve_redfield(annealing_problem, annealing_time, U; alg=Vern6(), abstol=1e-9, reltol=1e-9)

    sol_ame(annealing_time * ss)
end

function ExtractFinalResults(problem, solution_pops)
    num_qubits = QUBOHowManyQubits(problem)

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

    final_results
end


