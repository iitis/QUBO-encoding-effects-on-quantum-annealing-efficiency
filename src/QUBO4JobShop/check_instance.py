# Auxiliary code for preparing parameters of large instances, determining ground state etc.


import pytest

from JobShop_QUBO import  ILP_Encoding, make_ilp_docplex, docplex_sol2_schedule

from JobShop_QUBO import Implement_QUBO

# small
from instances import instance_4q, instance_5q, instance_6q, instance_8q, instance_10q

# larger
from instances import instance_26q, instance_52q, instance_100q, instance_151q, instance_199q




def check_instance(d):
    JS = d["js_problem"]
    ILP = ILP_Encoding(JS)

    model = make_ilp_docplex(ILP)

    sol = model.solve()
        
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    print(d["ground_scheds"])


    print("optimal obj", sol.get_objective_value())

    print("optimal sched", sched)

    qubo = Implement_QUBO(JS, psum=10, ppair=10)
    print("n.o. qbits", qubo.qubo_variables.size )

    x = qubo.schedule_2_x(sched)

    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.nonfeasible_sum_constraint(x) == 0
    # check objective

    assert qubo.compute_objective(x) == pytest.approx(sol.get_objective_value())

    print("################   Final Check    ##############")

    assert sched in d["ground_scheds"]

    assert d["ground_obj"]  == pytest.approx(sol.get_objective_value())






if __name__ == "__main__":

    d = instance_4q()

    check_instance(d)

    d = instance_5q()

    check_instance(d)


    d = instance_6q()

    check_instance(d)


    d = instance_8q()

    check_instance(d)


    d = instance_10q()

    check_instance(d)


    d = instance_26q()

    check_instance(d)

    d = instance_52q()

    check_instance(d)

    d = instance_100q()

    check_instance(d)

    d = instance_151q()

    check_instance(d)

    d = instance_199q()

    check_instance(d)




