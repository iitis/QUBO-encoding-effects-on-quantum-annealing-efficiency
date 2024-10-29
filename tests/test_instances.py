import pytest
from collections import OrderedDict

from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import ILP_Encoding, make_ilp_docplex, docplex_sol2_schedule
from JobShop_QUBO import QUBO_Variables, Implement_QUBO


def instance_small():

    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=1.0)

    JS = JobShop([J1, J2])
    return JS


def instance_1():

    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)
    JS = JobShop([J2, J3])
    return JS

def instance_2():
    # a bit pathological one job 3 has no penalty
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.0)
    JS = JobShop([J2, J3])
    return JS

def instance_3():

    J1 = Job(id = 1, m_p=OrderedDict({2:2, 3:2}), release=0, due=10, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)
    JS = JobShop([J1, J2, J3])
    return JS

def instance_4():
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=10, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 1:2}), release=1, due=10, weight=0.4)
    JS = JobShop([J1, J2])
    return JS


def instance_5():
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=0, due=10, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 1:2}), release=1, due=10, weight=0.5)
    JS = JobShop([J1, J2])
    return JS

def instance_6():
    J1 = Job(id = 1, m_p=OrderedDict({1:4, 2:2, 3:2}), release=1, due=10, weight=0.1)
    J2 = Job(id = 2, m_p=OrderedDict({1:2}), release=0, due=10, weight=1.0)
    JS = JobShop([J1, J2])
    return JS



def test_instances_ILP():

    JS = instance_small()
    ILP = ILP_Encoding(JS)

    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    print(sched)
    print(sol.get_objective_value())

    assert sched == {1: {1: (1.0, 3.0), 2: (4.0, 6.0)}, 2: {2: (2.0, 4.0)}}

    assert sol.get_objective_value() == pytest.approx(0.5)

    JS = instance_1()
    ILP = ILP_Encoding(JS)
    
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {2: {2: (1.0, 3.0), 3: (5.0, 7.0)}, 3: {1: (1.0, 2.0), 3: (2.0, 5.0)}}
    assert sol.get_objective_value() == pytest.approx(0.2)

    JS = instance_2()
    ILP = ILP_Encoding(JS)

    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {2: {2: (1.0, 3.0), 3: (3.0, 5.0)}, 3: {1: (1.0, 2.0), 3: (5.0, 8.0)}}
    assert sol.get_objective_value() == pytest.approx(0.0)

    JS = instance_3()
    ILP = ILP_Encoding(JS)

    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {1: {2: (0.0, 2.0), 3: (2.0, 4.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 3: {1: (1.0, 2.0), 3: (6.0, 9.0)}}
    assert sol.get_objective_value() == pytest.approx(0.5)

    JS = instance_4()
    ILP = ILP_Encoding(JS)

    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {1: {1: (1.0, 3.0), 2: (3.0, 5.0)}, 2: {2: (1.0, 3.0), 1: (3.0, 5.0)}}
    assert sol.get_objective_value() == pytest.approx(0.0)

    JS = instance_5()
    ILP = ILP_Encoding(JS)

    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {1: {1: (0.0, 2.0), 2: (3.0, 5.0)}, 2: {2: (1.0, 3.0), 1: (3.0, 5.0)}}
    assert sol.get_objective_value() == pytest.approx(0.083333333333333333)


    JS = instance_6()
    ILP = ILP_Encoding(JS)

    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)

    assert sched == {1: {1: (2.0, 6.0), 2: (6.0, 8.0) , 3: (8.0, 10.0)}, 2: {1: (0.0, 2.0)}}

    assert sol.get_objective_value() == pytest.approx(0.1)


def test_QUBO():

    JS = instance_1()
    
    ILP = ILP_Encoding(JS)
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)
    ilp_obj = sol.get_objective_value()

    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()

    x = qubo.schedule_2_x(sched)
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.nonfeasible_sum_constraint(x) == 0
    assert qubo.compute_objective(x) == pytest.approx(ilp_obj)


    JS = instance_2()
    
    ILP = ILP_Encoding(JS)
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)
    ilp_obj = sol.get_objective_value()

    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()

    x = qubo.schedule_2_x(sched)
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.nonfeasible_sum_constraint(x) == 0
    assert qubo.compute_objective(x) == pytest.approx(ilp_obj)


    JS = instance_3()
    
    ILP = ILP_Encoding(JS)
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)
    ilp_obj = sol.get_objective_value()

    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()

    x = qubo.schedule_2_x(sched)
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.nonfeasible_sum_constraint(x) == 0
    assert qubo.compute_objective(x) == pytest.approx(ilp_obj)


    JS = instance_4()
    
    ILP = ILP_Encoding(JS)
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)
    ilp_obj = sol.get_objective_value()

    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()
    assert qubo.qubo_variables.size == 24

    x = qubo.schedule_2_x(sched)
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.nonfeasible_sum_constraint(x) == 0
    assert qubo.compute_objective(x) == pytest.approx(ilp_obj)


    JS = instance_5()
    
    ILP = ILP_Encoding(JS)
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)
    ilp_obj = sol.get_objective_value()

    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()

    x = qubo.schedule_2_x(sched)
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.nonfeasible_sum_constraint(x) == 0
    assert qubo.compute_objective(x) == pytest.approx(ilp_obj)


    JS = instance_6()
    
    ILP = ILP_Encoding(JS)
    model = make_ilp_docplex(ILP)
    sol = model.solve()
    sched, _ = docplex_sol2_schedule(model, sol, ILP)
    ilp_obj = sol.get_objective_value()

    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()

    x = qubo.schedule_2_x(sched)
    assert sched == {1: {1: (2.0, 6.0), 2: (6.0, 8.0), 3: (8.0, 10.0)}, 2: {1: (0.0, 2.0)}}

    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.nonfeasible_sum_constraint(x) == 0
    assert qubo.compute_objective(x) == pytest.approx(ilp_obj)



















