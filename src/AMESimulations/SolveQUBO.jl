###
# PARAMTERS FOR TESTING
###

tf = 0.01 * 1e3






###
# Read the problem
###
include("LoadQUBOPkl.jl")

problem = QUBOProblem("../QUBO4JobShop/QUBOs/instance_qbits4_ppair2.0_psum2.0.pkl")
num_qubits = 4

###
# Set up the quantum annealing problem
###
using LinearAlgebra
using OpenQuantumTools
include("AnnealingSchedule.jl")

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
schedule = AnnealingSchedule("./09-1273A-E_Advantage_system6_4_annealing_schedule.xlsx")
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

# Set up the enviornment interaction
bath_coupling = collective_coupling("Z", num_qubits)
η = 1e-4
fc = 4 # GHz
T = 16 # mK
bath = Ohmic(η, fc, T)

# Annealing problem
ψi = (1 / sqrt(2^num_qubits)) * ones(Complex{Float64}, 2^num_qubits)
annealing = Annealing(
    H,
    ψi;
    coupling=bath_coupling,
    bath=bath
)

###
# Solve the problem with the unitary solver and an annealing time of 10ns (for testing)
###
using Printf
using Plots
using OrdinaryDiffEq

plot(H, 0:0.01:1, 16, linewidth=2)
title!("Hamiltonian Eigenenergies")
savefig("qubo_Henergies.pdf")

print("Solving with Schrodinger equation...")
sol_se = solve_schrodinger(annealing, tf, alg=Tsit5(), reltol=1e-9, abstol=1e-9)
println("Done!")

s_range = 0:0.01:1

plot(s_range, transpose((z -> abs(z)^2).(reduce(hcat, sol_se.(tf * s_range)))), linewidth=2)
ylims!(-0.01, 0.5)
title!("SE Simulation")
xlabel!("s")
ylabel!("Population")
savefig("qubopops.pdf")

println("** SE Pop. **")
map(z -> @printf("%.6f\n", abs(z)^2), sol_se(tf))
print("\n")
