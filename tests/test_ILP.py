import pytest
from collections import OrderedDict

from JobShop_QUBO import Job, JobShop, ILP_Variables, make_ilp_docplex



def test_var_creation():
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)

    JS = JobShop([J2, J3])

    ILP = ILP_Variables(JS)
    assert ILP.lowerlim == {'t_2_2': 3, 't_2_3': 5, 't_3_1': 2, 't_3_3': 5, 'y_2_3_3': 0}
    assert ILP.upperlim == {'t_2_2': 8, 't_2_3': 10, 't_3_1': 7, 't_3_3': 10, 'y_2_3_3': 1}
    assert ILP.obj_input == {'t_2_3': 0.1,  't_3_3': 0.1}
    assert ILP.objoffset == 1.0

    model = make_ilp_docplex(ILP)

    assert str(model.get_objective_expr()) == "0.100t_2_3+0.100t_3_3-1"


    sol = model.solve()

    assert sol.get_objective_value() == 0.0


    model.print_solution(print_zeros=True)
    assert sol['t_2_2'] == 3
    assert sol['t_2_3'] == 5
    assert sol['t_3_1'] == 2
    assert sol['t_3_3'] == 5
    assert sol['y_2_3_3'] == 0

