using Plots
using OpenQuantumTools
using OrdinaryDiffEq

import Interpolations
import XLSX

# Working with an annealing schedule from the D-Wave documentation
struct AnnealingSchedule
    s_range::Vector{Float64}   # Normalized time at which A, B, c are evaluated
    A_values::Vector{Float64}  # A(s) in GHz
    B_values::Vector{Float64}  # B(s) in GHz
    c_values::Vector{Float64}  # c (normalized)

    A_func::Any
    B_func::Any

    function AnnealingSchedule(path::String)
        xf = XLSX.readxlsx(path)
        s_range  = Vector{Float64}(vec(xf["Standard-Annealing Schedule"][2:end,1]))
        A_values = Vector{Float64}(vec(xf["Standard-Annealing Schedule"][2:end,2]))
        B_values = Vector{Float64}(vec(xf["Standard-Annealing Schedule"][2:end,3]))
        c_values = Vector{Float64}(vec(xf["Standard-Annealing Schedule"][2:end,4]))

        A_func = Interpolations.LinearInterpolation(s_range, A_values)
        B_func = Interpolations.LinearInterpolation(s_range, B_values)
        
        new(s_range, A_values, B_values, c_values, A_func, B_func)
    end
end
dwave_schedule = AnnealingSchedule("./09-1273A-E_Advantage_system6_4_annealing_schedule.xlsx")

plot(dwave_schedule.s_range, [dwave_schedule.A_values, dwave_schedule.B_values], label=["A(s)" "B(s)"], lw=2)
xlabel!("s")
ylabel!("Coupling (GHz)")
savefig("anneal_sched.pdf")

# Define initial and final Hamiltonians and configure the annealing schedule
Hi =(σx⊗σi⊗σi) + (σi⊗σx⊗σi) + (σi⊗σi⊗σx)
Hf = 0.75*(σi⊗σi⊗σi) + 0.25*(σz⊗σi⊗σi) + 0.25*(σi⊗σz⊗σi) - 0.50*(σi⊗σi⊗σz) + 0.25*(σz⊗σz⊗σi) - 0.50*(σz⊗σi⊗σz) - 0.50*(σi⊗σz⊗σz)

H = DenseHamiltonian(
    [(s)->dwave_schedule.A_func(s), (s)->dwave_schedule.B_func(s)], 
    # [(s)->1-s, (s)->s], 
    [-Hi/2, Hf/2],
    unit=:h         # Since the D-Wave annealing schedule is given in GHz
)

plot(H, 0:0.01:1, 8, linewidth=2)
savefig("energies.pdf")

# Set up the enviornment interaction
bath_coupling = ConstantCouplings(["ZII", "IZI", "IIZ"])
η = 1e-4
fc = 4 # GHz
T = 16 # mK
bath = Ohmic(η, fc, T)

p1 = plot(bath, :γ, range(0,20,length=200), label="", size=(800, 400), linewidth=2)
p2 = plot(bath, :S, range(0,20,length=200), label="", size=(800, 400), linewidth=2)
plot(p1, p2, layout=(1,2), left_margin=3Plots.Measures.mm)
savefig("bathspectra.pdf")

# Set up initial state and annealing problem
ψp = PauliVec[1][1]
ψi = ψp ⊗ ψp ⊗ ψp

annealing = Annealing(
    H, 
    ψi; 
    coupling=bath_coupling, 
    bath=bath
)


# Solve the problem with an annealing time of 10ns (for testing, since this is quick to run)
tf = 0.01 * 1e3 # time in μs

# Hamiltonian solver
sol_se = solve_schrodinger(annealing, tf, alg=Tsit5(), reltol=1e-9, abstol=1e-9)

# M.E. solver
U = solve_unitary(annealing, tf, alg=Tsit5(), abstol=1e-9, reltol=1e-9)
sol_ame = solve_redfield(annealing, tf, U; alg=Tsit5(), abstol=1e-9, reltol=1e-9)


s_range = 0:0.01:1

p1 = plot(s_range, transpose((z -> abs(z)^2).(reduce(hcat, sol_se.(tf * s_range)))))
p2 = plot(s_range, [
    [abs(m[1,1]) for m in sol_ame.(tf * s_range)],
    [abs(m[2,2]) for m in sol_ame.(tf * s_range)],
    [abs(m[3,3]) for m in sol_ame.(tf * s_range)],
    [abs(m[4,4]) for m in sol_ame.(tf * s_range)],
    [abs(m[5,5]) for m in sol_ame.(tf * s_range)],
    [abs(m[6,6]) for m in sol_ame.(tf * s_range)],
    [abs(m[7,7]) for m in sol_ame.(tf * s_range)],
    [abs(m[8,8]) for m in sol_ame.(tf * s_range)]
])
plot(p1, p2, layout=(1,2), left_margin=3Plots.Measures.mm)
savefig("populations.pdf")









