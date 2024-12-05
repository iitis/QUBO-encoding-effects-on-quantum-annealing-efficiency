import pytest
from collections import OrderedDict

from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import Implement_QUBO
from JobShop_QUBO import solve_on_DWave, sort_sols, dict_of_solutions

# set False if no D-Wave leep instaled
test_on_annealer = True

# test smallest instances

# smallest instances

def instance_4q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1}), release=1, due=3, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=3, weight=0.5)

    return JobShop([J1, J2])


def instance_5q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1}), release=1, due=3, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=4, weight=0.5)

    return JobShop([J1, J2])


def instance_6q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1, 2:1}), release=1, due=4, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=3, weight=0.5)

    return JobShop([J1, J2])


def instance_8q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1, 2:1}), release=1, due=4, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1, 3:1}), release=1, due=4, weight=0.5)

    return JobShop([J1, J2])



def test_smallest_instances_simulated_annelaing():
    if test_on_annealer:
        JS = instance_4q()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=10, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        assert xs[0]['obj'] == pytest.approx(0.5)
        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)
        
        assert sched == {1: {1: (1, 2)}, 2: {1: (2, 3)}}


        JS = instance_5q()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=10, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        assert xs[0]['obj'] == pytest.approx(0.25)
        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)
        
        assert sched == {1: {1: (1, 2)}, 2: {1: (2, 3)}}

        assert qubo.compute_objective(x) == pytest.approx(0.25)

        assert qubo.compute_energy(x) + qubo.compute_energy_offset(JS) == qubo.compute_objective(x) 


        JS = instance_6q()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=10, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        assert xs[0]['obj'] == pytest.approx(0.5)
        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)
        
        assert sched == {1: {1: (1, 2), 2:(2,3)}, 2: {1: (2, 3)}}


        JS = instance_8q()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=10, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        assert xs[0]['obj'] == pytest.approx(0.5)
        x = xs[0]['sol']

        assert qubo.compute_energy(x) + qubo.compute_energy_offset(JS) == qubo.compute_objective(x) 

        sched, _ = qubo.qubo_vec2_schedule(x)
        
        assert sched == {1: {1: (1, 2), 2: (2,3)}, 2: {1: (2, 3), 3:(3,4)}}



# test a bit larger instances

def instance_0():

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


def test_on_simulated_annelaing():
    if test_on_annealer:
        JS = instance_0()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=10, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        print( [(x['sol'], x["obj"]) for x in xs] )

        assert xs[0]['obj'] == pytest.approx(0.5)

         # degeneracy, ground states:
        x = [1,0,0,0,1,0,1,0,0,0]
        schedule, _ = qubo.qubo_vec2_schedule(x)
        assert schedule == {1: {1: (1, 3), 2: (4, 6)}, 2: {2: (2, 4)}}
        x =[0,1,0,0,1,0,1,0,0,0]
        schedule, _ = qubo.qubo_vec2_schedule(x)
        assert schedule == {1: {1: (2, 4), 2: (4, 6)}, 2: {2: (2, 4)}}

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)
        
        assert sched  in ({1: {1: (1, 3), 2: (4, 6)}, 2: {2: (2, 4)}},
                        {1: {1: (2, 4), 2: (4, 6)}, 2: {2: (2, 4)}}
        )




        JS = instance_1()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=100, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)

        assert xs[0]['obj'] == pytest.approx(0.2)

        assert qubo.compute_energy(x) + qubo.compute_energy_offset(JS) == pytest.approx(qubo.compute_objective(x))

        # degeneracy
        assert sched in ( {2: {2: (1, 3), 3: (5, 7)}, 3: {1: (1, 2), 3: (2, 5)}},
                        {2: {2: (2, 4), 3: (5, 7)}, 3: {1: (1, 2), 3: (2, 5)}},
                        {2: {2: (3, 5), 3: (5, 7)}, 3: {1: (1, 2), 3: (2, 5)}}
        )


        JS = instance_2()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=100, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)

        assert xs[0]['obj'] == pytest.approx(0.0)

        print(sched)
        # degeneracy
        assert sched in ( 
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (1, 2), 3: (5, 8)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (1, 2), 3: (6, 9)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (1, 2), 3: (7, 10)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (2, 3), 3: (5, 8)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (2, 3), 3: (6, 9)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (2, 3), 3: (7, 10)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (3, 4), 3: (5, 8)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (3, 4), 3: (6, 9)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (3, 4), 3: (7, 10)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (4, 5), 3: (5, 8)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (4, 5), 3: (6, 9)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (4, 5), 3: (7, 10)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (5, 6), 3: (6, 9)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (5, 6), 3: (7, 10)}},
            {2: {2: (1, 3), 3: (3, 5)}, 3: {1: (6, 7), 3: (7, 10)}}
        )


        JS = instance_3()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=200, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)

        assert xs[0]['obj'] == pytest.approx(0.5)

        assert qubo.compute_energy(x) + qubo.compute_energy_offset(JS) == pytest.approx(qubo.compute_objective(x))

        assert sched in ( {1: {2: (0.0, 2.0), 3: (2.0, 4.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 3: {1: (1.0, 2.0), 3: (6.0, 9.0)}},
                        {1: {2: (0.0, 2.0), 3: (2.0, 4.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 3: {1: (2.0, 3.0), 3: (6.0, 9.0)}},
                        {1: {2: (0.0, 2.0), 3: (2.0, 4.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 3: {1: (3.0, 4.0), 3: (6.0, 9.0)}},
                        {1: {2: (0.0, 2.0), 3: (2.0, 4.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 3: {1: (4.0, 5.0), 3: (6.0, 9.0)}},
                        {1: {2: (0.0, 2.0), 3: (2.0, 4.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 3: {1: (5.0, 6.0), 3: (6.0, 9.0)}}
        )


        JS = instance_4()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=250, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)

        assert xs[0]['obj'] == pytest.approx(0.0)

        # no degeneracy here
        assert sched == {1: {1: (1.0, 3.0), 2: (3.0, 5.0)}, 2: {2: (1.0, 3.0), 1: (3.0, 5.0)}}

        JS = instance_5()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=250, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)

        assert xs[0]['obj'] == pytest.approx(0.083333333333333333)

        assert qubo.compute_energy(x) + qubo.compute_energy_offset(JS) == pytest.approx(qubo.compute_objective(x))

        assert sched in ( {1: {1: (0.0, 2.0), 2: (3.0, 5.0)}, 2: {2: (1.0, 3.0), 1: (3.0, 5.0)}},
                         {1: {1: (1.0, 3.0), 2: (3.0, 5.0)}, 2: {2: (1.0, 3.0), 1: (3.0, 5.0)}}
        )


        JS = instance_6()
        qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=250, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)

        assert xs[0]['obj'] == pytest.approx(0.1)

        assert qubo.compute_energy(x) + qubo.compute_energy_offset(JS) == pytest.approx(qubo.compute_objective(x))
        
        assert sched == {1: {1: (2.0, 6.0), 2: (6.0, 8.0) , 3: (8.0, 10.0)}, 2: {1: (0.0, 2.0)}}


        JS = instance_6()
        qubo = Implement_QUBO(JS, psum = 5, ppair = 1.9)
        qubo.make_QUBO()

        Q = qubo.qubo_terms
        sampleset = solve_on_DWave(Q, no_runs=250, real = False, hyb = False, at = 0.)
        d = dict_of_solutions(qubo, sampleset.record)
        xs = sort_sols(d)

        x = xs[0]['sol']
        sched, _ = qubo.qubo_vec2_schedule(x)

        assert xs[0]['obj'] == pytest.approx(0.1)

        assert qubo.compute_energy(x) + qubo.compute_energy_offset(JS) == pytest.approx(qubo.compute_objective(x))
        
        assert sched == {1: {1: (2.0, 6.0), 2: (6.0, 8.0) , 3: (8.0, 10.0)}, 2: {1: (0.0, 2.0)}}

        


def test_spectrum():
    JS = instance_4()
    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()

    sols = [[1,0,0,1], [0,1,1,0], [0,0,1,0], [1,0,0,0], [0,0,0,1], [1,0,1,0], [0,1,0,1], [1,1,0,0]]
    



    










