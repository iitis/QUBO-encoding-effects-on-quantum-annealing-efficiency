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

    function AnnealingSchedule(path::String, fastanneal::Bool = false)
        sheet = fastanneal ? "Fast-Annealing Schedule" : "Standard-Annealing Schedule"

        xf = XLSX.readxlsx(path)
        s_range  = Vector{Float64}(vec(xf[sheet][2:end,1]))
        A_values = Vector{Float64}(vec(xf[sheet][2:end,2]))
        B_values = Vector{Float64}(vec(xf[sheet][2:end,3]))
        c_values = Vector{Float64}(vec(xf[sheet][2:end,4]))

        A_func = Interpolations.LinearInterpolation(s_range, A_values)
        B_func = Interpolations.LinearInterpolation(s_range, B_values)

        new(s_range, A_values, B_values, c_values, A_func, B_func)
    end
end
