# https://stackoverflow.com/questions/65720584/how-to-load-python-pickle-from-julia

using PyCall

py"""
import pickle
def load_pickle(path):
    with open(path, 'rb') as inf:
        return pickle.load(inf)
"""

load_pyobj_pkl = py"load_pickle"

struct QUBOProblem
    opt_objective::Float64
    opt_energy::Float64
    offset::Float64
    ground_states::Array{Int64, 2}
    qubo::Dict{Tuple{Int64, Int64}, Float64}
    obj_part_qubo::Dict{Tuple{Int64, Int64}, Float64}

    function QUBOProblem(qubo_pydict::Dict{Any, Any})
        opt_objective = qubo_pydict["ground_obj"]
        opt_energy = qubo_pydict["ground_energy"]
        offset = qubo_pydict["offset"]
        ground_states = qubo_pydict["ground_states"]
        qubo = Dict{Tuple{Int64, Int64}, Float64}(qubo_pydict["qubo"])
        obj_part_qubo = Dict{Tuple{Int64, Int64}, Float64}(qubo_pydict["objective_part"])

        new(opt_objective, opt_energy, offset, ground_states, qubo, obj_part_qubo)
    end
end

function LoadQUBOProblem(path::String)
    qubo_pydict = load_pyobj_pkl(path)
    return QUBOProblem(qubo_pydict)
end

function LoadManyQUBOs(path::String)
    # List of QUBO dictionaries, type is Vector{Tuple{Float64, Float64, Dict{Any, Any}}}
    pylist_qubos = load_pyobj_pkl(path)

    qubo_list = Vector{@NamedTuple{psum::Float64, ppair::Float64, qubo::QUBOProblem}}()
    for (py_psum, py_ppair, qubo_pydict) in pylist_qubos
        push!(qubo_list, (
            psum = py_psum,
            ppair = py_ppair,
            qubo = QUBOProblem(qubo_pydict)
        ))
    end
    return qubo_list
end

function EvaluateQUBOEnergy(qubo::Dict{Tuple{Int64, Int64}, Float64}, state::String)
    bits = (s -> parse(Int64, s)).(collect(state))

    energy = 0.0
    for ((i,j), w) in qubo
        si = bits[i]
        sj = bits[j]

        energy = energy + w * si*sj
    end

    energy
end



function EvaluateFeasibility(qubo::Dict{Tuple{Int64, Int64}, Float64}, 
                                obj_part_qubo::Dict{Tuple{Int64, Int64}, Float64}, 
                                offset::Float64, 
                                state::String)
    

    energy = EvaluateQUBOEnergy(qubo, state)
    objective = EvaluateQUBOEnergy(obj_part_qubo, state)

    return isapprox(energy, objective - offset)
end


function FeasibilityPercentage(results::Vector{Pair{String, Float64}}, problem::QUBOProblem)

    k = 0
    f_prob = 0
    for (state, pop) in results
        if EvaluateFeasibility(problem.qubo, problem.obj_part_qubo, problem.offset, state)
            k = k+1
            f_prob = f_prob + pop
        end
    end
    no_solutuons = length(results)
    return k , no_solutuons, f_prob 
end


function OptimalityPercentage(results::Vector{Pair{String, Float64}}, problem::QUBOProblem, ground_energy::Float64)

    k = 0
    f_prob = 0
    for (state, pop) in results
        if EvaluateFeasibility(problem.qubo, problem.obj_part_qubo, problem.offset, state)
            if isapprox(EvaluateQUBOEnergy(problem.qubo, state), ground_energy)
                k = k+1
                f_prob = f_prob + pop
            end
        end
    end
    no_solutuons = length(results)
    return k , no_solutuons, f_prob 
end


