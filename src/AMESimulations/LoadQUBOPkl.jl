# https://stackoverflow.com/questions/65720584/how-to-load-python-pickle-from-julia

using PyCall

py"""
import pickle
def load_pickle(path):
    with open(path, 'rb') as inf:
        return pickle.load(inf)
"""

load_pydict_pkl = py"load_pickle"

struct QUBOProblem
    opt_objective::Float64
    ground_states::Array{Int64, 2}
    qubo::Dict{Tuple{Int64, Int64}, Float64}

    function QUBOProblem(path::String)
        qubo_pydict = load_pydict_pkl(path)

        opt_objective = qubo_pydict["ground_obj"]
        ground_states = qubo_pydict["ground_states"]
        qubo = Dict{Tuple{Int64, Int64}, Float64}(qubo_pydict["qubo"])

        new(opt_objective, ground_states, qubo)
    end
end

function EvaluateQUBOObjective(qubo::Dict{Tuple{Int64, Int64}, Float64}, state::String, Nq::Int64)
    bits = (s -> parse(Int64, s)).(collect(state))

    objective = 0.0
    for ((i,j), w) in qubo
        si = bits[i]
        sj = bits[j]

        objective = objective + w * si*sj
    end

    objective
end
