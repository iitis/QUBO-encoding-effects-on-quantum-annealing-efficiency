import pytest
from collections import OrderedDict

from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import ILP_Encoding, make_ilp_docplex, docplex_sol2_schedule



def instance_small():

    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=8, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=8, weight=0.5)

    JS = JobShop([J1, J2])
    ILP = ILP_Encoding(JS)
    return ILP


def instance_1():

    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)
    JS = JobShop([J2, J3])
    ILP = ILP_Encoding(JS)
    return ILP

def instance_2():

    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.0)
    JS = JobShop([J2, J3])
    ILP = ILP_Encoding(JS)
    return ILP

def instance_3():

    J1 = Job(id = 1, m_p=OrderedDict({2:2, 3:2}), release=0, due=10, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)
    JS = JobShop([J1, J2, J3])
    ILP = ILP_Encoding(JS)
    return ILP

def instance_4():
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=10, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 1:2}), release=1, due=10, weight=0.4)
    JS = JobShop([J1, J2])
    ILP = ILP_Encoding(JS)
    return ILP


def instance_5():
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=0, due=10, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 1:2}), release=1, due=10, weight=0.5)
    JS = JobShop([J1, J2])
    ILP = ILP_Encoding(JS)
    return ILP





def test_instances_ILP():

    ILP = instance_small()
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    print(sched)
    print(sol.get_objective_value())

    assert sched == {1: {1: (1.0, 3.0), 2: (4.0, 6.0)}, 2: {2: (2.0, 4.0)}}

    assert sol.get_objective_value() == pytest.approx(0.16666666)

    ILP = instance_1()
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {2: {2: (1.0, 3.0), 3: (5.0, 7.0)}, 3: {1: (1.0, 2.0), 3: (2.0, 5.0)}}
    assert sol.get_objective_value() == pytest.approx(0.2)

    ILP = instance_2()
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {2: {2: (1.0, 3.0), 3: (3.0, 5.0)}, 3: {1: (1.0, 2.0), 3: (5.0, 8.0)}}
    assert sol.get_objective_value() == pytest.approx(0.0)

    ILP = instance_3()
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {1: {2: (0.0, 2.0), 3: (2.0, 4.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 3: {1: (1.0, 2.0), 3: (6.0, 9.0)}}
    assert sol.get_objective_value() == pytest.approx(0.5)

    ILP = instance_4()
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {1: {1: (1.0, 3.0), 2: (3.0, 5.0)}, 2: {2: (1.0, 3.0), 1: (3.0, 5.0)}}
    assert sol.get_objective_value() == pytest.approx(0.0)

    ILP = instance_5()
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {1: {1: (0.0, 2.0), 2: (3.0, 5.0)}, 2: {2: (1.0, 3.0), 1: (3.0, 5.0)}}
    assert sol.get_objective_value() == pytest.approx(0.083333333333333333)


