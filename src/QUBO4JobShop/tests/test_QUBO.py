from collections import OrderedDict

from JobShop_QUBO import Job, JobShop

from JobShop_QUBO import QUBO_Variables, Implement_QUBO, add_to_dict
from instances import instance_4q, instance_5q
from instances import create_QUBO_dict


def test_suxiliary():

    d = {}

    add_to_dict(d, key = 1, value = 2)

    assert d == {1:2}

    add_to_dict(d, key = 1, value = 2)
    add_to_dict(d, key = 2, value = 2)

    assert d == {1:4, 2:2}


def test_QUBO_variables():

    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)

    JS = JobShop([J2, J3])

    q = QUBO_Variables(JS)
    
    """ k:(j,m,t) """
    assert q.vars == {1: (2, 2, 3), 2: (2, 2, 4), 3: (2, 2, 5), 4: (2, 2, 6), 
                        5: (2, 2, 7), 6: (2, 2, 8), 7: (2, 3, 5), 8: (2, 3, 6), 
                        9: (2, 3, 7), 10: (2, 3, 8), 11: (2, 3, 9), 12: (2, 3, 10), 
                        13: (3, 1, 2), 14: (3, 1, 3), 15: (3, 1, 4), 16: (3, 1, 5), 
                        17: (3, 1, 6), 18: (3, 1, 7), 19: (3, 3, 5), 20: (3, 3, 6), 
                        21: (3, 3, 7), 22: (3, 3, 8), 23: (3, 3, 9), 24: (3, 3, 10)}
    
    assert q.size == 24


    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=8, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=8, weight=0.5)

    JS = JobShop([J2, J3])
    q = QUBO_Variables(JS)

    """ k:(j,m,t) """
    assert q.vars == {1: (2, 2, 3), 2: (2, 2, 4), 3: (2, 2, 5), 4: (2, 2, 6), 
                        5: (2, 3, 5), 6: (2, 3, 6), 7: (2, 3, 7), 8: (2, 3, 8), 
                        9: (3, 1, 2), 10: (3, 1, 3), 11: (3, 1, 4), 12: (3, 1, 5), 
                        13: (3, 3, 5), 14: (3, 3, 6), 15: (3, 3, 7), 16: (3, 3, 8)}

    
    assert q.size == 16

    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=8, weight=0.5)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=0.5)

    JS = JobShop([J1, J2])
    q = QUBO_Variables(JS)

    """ k:(j,m,t) """


    assert q.vars == {1: (1, 1, 3), 2: (1, 1, 4), 3: (1, 1, 5), 4: (1, 1, 6), 5: (1, 2, 5), 
                        6: (1, 2, 6), 7: (1, 2, 7), 8: (1, 2, 8), 9: (2, 2, 4), 
                        10: (2, 2, 5), 11: (2, 2, 6), 12: (2, 2, 7)}
    
    assert q.vars_jmt == {(1, 1, 3): 1, (1, 1, 4): 2, (1, 1, 5): 3, (1, 1, 6): 4, 
                        (1, 2, 5): 5, (1, 2, 6): 6, (1, 2, 7): 7, (1, 2, 8): 8,
                        (2, 2, 4): 9, (2, 2, 5): 10, (2, 2, 6): 11, (2, 2, 7): 12}


    assert q.size == 12




def test_QUBO_implmenetation():

    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=1.0)

    JS = JobShop([J1, J2])


    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)

    assert qubo.psum == 2
    assert qubo.ppair == 2
    assert qubo.qubo_terms == {}
    assert qubo.qubo_variables.size == 10


    assert qubo.qubo_variables.vars == {1: (1, 1, 3), 2: (1, 1, 4), 3: (1, 1, 5), 
                                        4: (1, 2, 5), 5: (1, 2, 6), 6: (1, 2, 7),
                                          7: (2, 2, 4), 8: (2, 2, 5), 9: (2, 2, 6),
                                          10: (2, 2, 7)}
    
    x = [1,0,0,1,0,0,0,0,0,1]
    schedule, _ = qubo.qubo_vec2_schedule(x)

    assert schedule == {1: {1: (1, 3), 2: (3, 5)}, 2: {2: (5, 7)}}

    d = {1: {1: (1, 3), 2: (3, 5)}, 2: {2: (5, 7)}}

    x1 = qubo.schedule_2_x(d)
    assert x1 == x

    qubo.sum_constraint()


    assert qubo.qubo_terms== {(1, 1): -2, (1, 2): 2, (1, 3): 2, (2, 1): 2, (2, 2): -2, (2, 3): 2, 
                              (3, 1): 2, (3, 2): 2, (3, 3): -2, (4, 4): -2, (4, 5): 2, (4, 6): 2, 
                              (5, 4): 2, (5, 5): -2, (5, 6): 2, (6, 4): 2, (6, 5): 2, (6, 6): -2, 
                              (7, 7): -2, (7, 8): 2, (7, 9): 2, (7, 10): 2, (8, 7): 2, (8, 8): -2,
                              (8, 9): 2, (8, 10): 2, (9, 7): 2, (9, 8): 2, (9, 9): -2, (9, 10): 2,
                              (10, 7): 2, (10, 8): 2, (10, 9): 2, (10, 10): -2}




    assert qubo.inds_sum_same == {(1, 1): (1, 1, 3), (2, 2): (1, 1, 4), (3, 3): (1, 1, 5), 
                                  (4, 4): (1, 2, 5), (5, 5): (1, 2, 6), (6, 6): (1, 2, 7), 
                                  (7, 7): (2, 2, 4), (8, 8): (2, 2, 5), (9, 9): (2, 2, 6), (10,10): (2,2,7)}


    assert qubo.inds_sum_diff == {(1, 2): [(1, 1, 3), (1, 1, 4)], (1, 3): [(1, 1, 3), (1, 1, 5)], 
                                  (2, 1): [(1, 1, 4), (1, 1, 3)], (2, 3): [(1, 1, 4), (1, 1, 5)], 
                                  (3, 1): [(1, 1, 5), (1, 1, 3)], (3, 2): [(1, 1, 5), (1, 1, 4)], 
                                  (4, 5): [(1, 2, 5), (1, 2, 6)], (4, 6): [(1, 2, 5), (1, 2, 7)], 
                                  (5, 4): [(1, 2, 6), (1, 2, 5)], (5, 6): [(1, 2, 6), (1, 2, 7)], 
                                  (6, 4): [(1, 2, 7), (1, 2, 5)], (6, 5): [(1, 2, 7), (1, 2, 6)], 
                                  (7, 8): [(2, 2, 4), (2, 2, 5)], (7, 9): [(2, 2, 4), (2, 2, 6)], 
                                  (7, 10): [(2, 2, 4), (2, 2, 7)], (8, 7): [(2, 2, 5), (2, 2, 4)], 
                                  (8, 9): [(2, 2, 5), (2, 2, 6)], (8, 10): [(2, 2, 5), (2, 2, 7)], 
                                  (9, 7): [(2, 2, 6), (2, 2, 4)], (9, 8): [(2, 2, 6), (2, 2, 5)], 
                                  (9, 10): [(2, 2, 6), (2, 2, 7)], (10, 7): [(2, 2, 7), (2, 2, 4)], 
                                  (10, 8): [(2, 2, 7), (2, 2, 5)], (10, 9): [(2, 2, 7), (2, 2, 6)]}


    qubo.objective()

    assert qubo.qubo_terms == {(1, 1): -2, (1, 2): 2, (1, 3): 2, (2, 1): 2, (2, 2): -2, (2, 3): 2, 
                              (3, 1): 2, (3, 2): 2, (3, 3): -2, (4, 4): -2+0, (4, 5): 2, (4, 6): 2, 
                              (5, 4): 2, (5, 5): -2+0.5, (5, 6): 2, (6, 4): 2, (6, 5): 2, (6, 6): -2+1, 
                              (7, 7): -2, (7, 8): 2, (7, 9): 2, (7, 10): 2, (8, 7): 2, (8, 8): -2+1/3,
                              (8, 9): 2, (8, 10): 2, (9, 7): 2, (9, 8): 2, (9, 9): -2+2/3, (9, 10): 2,
                              (10, 7): 2, (10, 8): 2, (10, 9): 2, (10, 10): -2+1}


    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)

    qubo.pair_constraint_process_t()



    assert qubo.inds_pair == {(4, 2): [(1, 2, 5), (1, 1, 4)], (2, 4): [(1, 1, 4), (1, 2, 5)], 
                              (4, 3): [(1, 2, 5), (1, 1, 5)], (3, 4): [(1, 1, 5), (1, 2, 5)], 
                              (5, 3): [(1, 2, 6), (1, 1, 5)], (3, 5): [(1, 1, 5), (1, 2, 6)]}
    
    

    assert qubo.qubo_terms == {(4,2): 2, (2, 4): 2, (4, 3): 2, (3, 4): 2, (5, 3): 2, (3, 5): 2}


    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)

    qubo.pair_constraint_occupancy()


    assert qubo.inds_pair == {(4, 7): [(1, 2, 5), (2, 2, 4)], (4, 8): [(1, 2, 5), (2, 2, 5)], 
                              (4, 9): [(1, 2, 5), (2, 2, 6)], (5, 8): [(1, 2, 6), (2, 2, 5)], 
                              (5, 9): [(1, 2, 6), (2, 2, 6)], (5, 10): [(1, 2, 6), (2, 2, 7)], 
                              (6, 9): [(1, 2, 7), (2, 2, 6)], (6, 10): [(1, 2, 7), (2, 2, 7)], 
                              (7, 4): [(2, 2, 4), (1, 2, 5)], (8, 4): [(2, 2, 5), (1, 2, 5)], 
                              (8, 5): [(2, 2, 5), (1, 2, 6)], (9, 4): [(2, 2, 6), (1, 2, 5)], 
                              (9, 5): [(2, 2, 6), (1, 2, 6)], (9, 6): [(2, 2, 6), (1, 2, 7)], 
                              (10, 5): [(2, 2, 7), (1, 2, 6)], (10, 6): [(2, 2, 7), (1, 2, 7)]}


    assert qubo.qubo_terms == {(4, 7): 2, (4, 8): 2, (4, 9): 2, (5, 8): 2, (5, 9): 2, (5, 10): 2, 
                               (6, 9): 2, (6, 10): 2, (7, 4): 2, (8, 4): 2, (8, 5): 2, (9, 4): 2, 
                               (9, 5): 2, (9, 6): 2, (10, 5): 2, (10, 6): 2}



def test_varying_sum_pair_pars():

        J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=7, weight=1.0)
        J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=1.0)

        JS = JobShop([J1, J2])

        for psum in [0.01, 0.5, 10, 100.5]:
            for ppair in [0.01, 0.5, 10, 100.5]:
                qubo = Implement_QUBO(JS, psum = psum, ppair = ppair)
                qubo.sum_constraint()
                assert qubo.qubo_variables.size == 10
                


                assert qubo.qubo_terms== {(1, 1): -psum, (1, 2): psum, (1, 3): psum, (2, 1): psum, 
                                        (2, 2): -psum, (2, 3): psum, (3, 1): psum, (3, 2): psum, 
                                        (3, 3): -psum, (4, 4): -psum, (4, 5): psum, (4, 6): psum, (5, 4): psum, 
                                        (5, 5): -psum, (5, 6): psum, (6, 4): psum, (6, 5): psum, 
                                        (6, 6): -psum, 
                                        (7, 7): -psum, (7, 8): psum, (7, 9): psum, (7, 10): psum, (8, 7): psum, 
                                        (8, 8): -psum, (8, 9): psum, (8, 10): psum, (9, 7): psum, (9, 8): psum, 
                                        (9, 9): -psum, (9, 10): psum, (10, 7): psum, (10, 8): psum, (10, 9): psum, 
                                        (10, 10): -psum}
                
                qubo = Implement_QUBO(JS, psum = psum, ppair = ppair)
                qubo.pair_constraint_process_t()

                assert qubo.qubo_terms == {(4,2): ppair, (2, 4): ppair, (4, 3): ppair, (3, 4): ppair, (5, 3): ppair, (3, 5): ppair}

                qubo = Implement_QUBO(JS, psum = psum, ppair = ppair)
                qubo.pair_constraint_occupancy()

                assert qubo.qubo_terms == {(4, 7): ppair, (4, 8): ppair, (4, 9): ppair, (5, 8): ppair, (5, 9): ppair, (5, 10): ppair, 
                                    (6, 9): ppair, (6, 10): ppair, (7, 4): ppair, (8, 4): ppair, (8, 5): ppair, (9, 4): ppair, 
                                    (9, 5): ppair, (9, 6): ppair, (10, 5): ppair, (10, 6): ppair}



def test_creating_QUBOs():
    """ this is 4q instnce splited in details"""

    no_qbits=4

    for psum in [0.01, 0.5, 10, 100.5]:
        for ppair in [0.01, 0.5, 10, 100.5]:


            d = create_QUBO_dict(no_qbits, instance_4q(), psum, ppair)
            obj = d["objective_part"]

            assert obj == {(1, 1): 0.0, (2, 2): 1.0, (3, 3): 0.0, (4, 4): 0.5}

            assert d["qubo"] == {(1, 1): -psum + obj[(1,1)], 
                                (1, 2): psum, (2, 1): psum, 
                                (2, 2): -psum + obj[(2,2)], 
                                (3, 3): -psum + obj[(3,3)], 
                                (3, 4): psum, (4, 3): psum, 
                                (4, 4): -psum + obj[(4,4)], 
                                (1, 3): ppair, (2, 4): ppair, (3, 1): ppair, (4, 2): ppair}
            

            assert d["offset"] == 2 * psum

        """ this is 4q instnce splited in details"""

    no_qbits=5

    for psum in [0.01, 0.5, 10, 100.5]:
        for ppair in [0.01, 0.5, 10, 100.5]:


            d = create_QUBO_dict(no_qbits, instance_5q(), psum, ppair)
            obj = d["objective_part"]

            assert obj == {(1, 1): 0.0, (2, 2): 1.0, (3, 3): 0.0, (4, 4): 0.25, (5, 5): 0.5}

            print(d["qubo"])
            assert d["qubo"] == {(1, 1): -psum + obj[(1,1)], 
                                (1, 2): psum, (2, 1): psum, 
                                (2, 2): -psum + obj[(2,2)], 
                                (3, 3): -psum + obj[(3,3)], (3, 4): psum, (3, 5): psum, 
                                (4, 3): psum, (4, 4): -psum + obj[(4,4)], (4, 5): psum,
                                (5, 3): psum, (5, 4):psum, (5, 5):  -psum + obj[(5,5)],
                                (1, 3): ppair, (2, 4): ppair, (3, 1): ppair, (4, 2): ppair}
            

            assert d["offset"] == 2 * psum




def test_pair_constraints_further():
    """ degenerated instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:4}), release=1, due=7, weight=1.0)

    JS = JobShop([J1, J2])


    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)

    assert qubo.qubo_variables.vars == {1: (1, 1, 3), 2: (1, 1, 4), 3: (1, 1, 5), 4: (1, 1, 6), 
                                        5: (1, 1, 7), 6: (2, 1, 5), 7: (2, 1, 6), 8: (2, 1, 7)}
    

    qubo.pair_constraint_occupancy()


    assert qubo.inds_pair == {(1, 6): [(1, 1, 3), (2, 1, 5)], (1, 7): [(1, 1, 3), (2, 1, 6)], 
                              (2, 6): [(1, 1, 4), (2, 1, 5)], (2, 7): [(1, 1, 4), (2, 1, 6)], 
                              (2, 8): [(1, 1, 4), (2, 1, 7)], (3, 6): [(1, 1, 5), (2, 1, 5)], 
                              (3, 7): [(1, 1, 5), (2, 1, 6)], (3, 8): [(1, 1, 5), (2, 1, 7)], 
                              (4, 6): [(1, 1, 6), (2, 1, 5)], (4, 7): [(1, 1, 6), (2, 1, 6)], 
                              (4, 8): [(1, 1, 6), (2, 1, 7)], (5, 7): [(1, 1, 7), (2, 1, 6)], 
                              (5, 8): [(1, 1, 7), (2, 1, 7)], (6, 1): [(2, 1, 5), (1, 1, 3)], 
                              (6, 2): [(2, 1, 5), (1, 1, 4)], (6, 3): [(2, 1, 5), (1, 1, 5)], 
                              (6, 4): [(2, 1, 5), (1, 1, 6)], (7, 1): [(2, 1, 6), (1, 1, 3)], 
                              (7, 2): [(2, 1, 6), (1, 1, 4)], (7, 3): [(2, 1, 6), (1, 1, 5)], 
                              (7, 4): [(2, 1, 6), (1, 1, 6)], (7, 5): [(2, 1, 6), (1, 1, 7)], 
                              (8, 2): [(2, 1, 7), (1, 1, 4)], (8, 3): [(2, 1, 7), (1, 1, 5)], 
                              (8, 4): [(2, 1, 7), (1, 1, 6)], (8, 5): [(2, 1, 7), (1, 1, 7)]}


def test_check_solution():

    """ degenerated instance """

    J1 = Job(id = 1, m_p=OrderedDict({1:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:4}), release=1, due=7, weight=1.0)

    JS = JobShop([J1, J2])


    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)

    qubo.make_QUBO()

    # Job 1 first
    x = [1,0,0,0,0,0,0,1]
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.compute_objective(x) == 1.0
    assert qubo.obj_terms == {(1, 1): 0.0, (2, 2): 0.25, (3, 3): 0.5, (4, 4): 0.75, (5, 5): 1.0, (6, 6): 0.0, (7, 7): 0.5, (8, 8): 1.0}
    assert sum([x[i] * qubo.obj_terms[(i+1,i+1)] for i in range(len(x))]) == 1.0


    assert qubo.compute_energy(x) == 1.0 - 4
    assert qubo.compute_energy_offset(JS) == 4
    assert qubo.is_feasible(x) == True

    x = [0,1,0,0,0,0,0,1]
    assert qubo.nonfeasible_pair_constraints(x) == 1
    assert qubo.is_feasible(x) == False

    x = [0,0,1,0,0,0,0,1]
    assert qubo.nonfeasible_pair_constraints(x) == 1
    assert qubo.is_feasible(x) == False

    # Job 2 first
    x = [0,0,0,0,1,1,0,0]
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.compute_objective(x) == 1.0
    assert qubo.is_feasible(x) == True

    x = [0,0,0,0,1,0,1,0]
    assert qubo.nonfeasible_pair_constraints(x) == 1
    assert qubo.is_feasible(x) == False

    x = [0,0,0,0,1,0,0,1]
    assert qubo.nonfeasible_pair_constraints(x) == 1
    assert qubo.is_feasible(x) == False


    # sum constraint
    x = [1,0,0,0,0,0,0,1]
    assert qubo.nonfeasible_sum_constraint(x) == 0

    x = [1,1,0,0,0,0,0,1]
    assert qubo.nonfeasible_sum_constraint(x) == 1

    x = [0,0,0,0,0,0,0,1]
    assert qubo.nonfeasible_sum_constraint(x) == 1

    x = [0,0,0,0,0,0,1,1]
    assert qubo.nonfeasible_sum_constraint(x) == 2

def test_objective():

    """  non degenerated instance """

    J1 = Job(id = 1, m_p=OrderedDict({1:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:4}), release=1, due=7, weight=0.5)

    JS = JobShop([J1, J2])


    qubo = Implement_QUBO(JS, psum = 2, ppair = 2)
    qubo.make_QUBO()

    # Job 1 first
    x = [1,0,0,0,0,0,0,1]
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.compute_objective(x) == 0.5
    assert sum([x[i] * qubo.obj_terms[(i+1,i+1)] for i in range(len(x))]) == 0.5

    schedule, _ = qubo.qubo_vec2_schedule(x)

    assert schedule == {1: {1: (1, 3)}, 2: {1: (3, 7)}}

    x1 = qubo.schedule_2_x({1: {1: (1, 3)}, 2: {1: (3, 7)}})
    assert x1 == x


    # Job 2 first
    x = [0,0,0,0,1,1,0,0]
    assert qubo.nonfeasible_pair_constraints(x) == 0
    assert qubo.compute_objective(x) == 1.0

    schedule, _ = qubo.qubo_vec2_schedule(x)
    assert schedule == {1: {1: (5, 7)}, 2: {1: (1, 5)}}
    
    x1 = qubo.schedule_2_x({1: {1: (5, 7)}, 2: {1: (1, 5)}})
    assert x1 == x










