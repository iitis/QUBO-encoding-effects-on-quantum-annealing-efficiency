from JobShop_QUBO import Job, JobShop
from JobShop_QUBO import Implement_QUBO
from collections import OrderedDict


def instance_4q():
    """ 4 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1}), release=1, due=3, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=3, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2)}, 2: {1: (2, 3)}}]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}

def instance_5q():
    """ 5 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1}), release=1, due=3, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=4, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2)}, 2: {1: (2, 3)}}]

    ground_obj = 0.25
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_6q():
    """ 6 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1, 2:1}), release=1, due=4, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1}), release=1, due=3, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2), 2:(2,3)}, 2: {1: (2, 3)}}]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_8q():
    """ 8 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:1, 2:1}), release=1, due=4, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({1:1, 3:1}), release=1, due=4, weight=0.5)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 2), 2: (2,3)}, 2: {1: (2, 3), 3:(3,4)}}]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_10q():
    """ 10 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=7, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2}), release=2, due=7, weight=1.0)

    JS = JobShop([J1, J2])

    scheds = [{1: {1: (1, 3), 2: (4, 6)}, 2: {2: (2, 4)}},
                        {1: {1: (2, 4), 2: (4, 6)}, 2: {2: (2, 4)}}
    ]

    ground_obj = 0.5
    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}



######  new instances  #######


def instance_26q():
    """ 26 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=10, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=2, due=12, weight=1.0)

    JS = JobShop([J1, J2])

    scheds = [
        {1: {1: (1.0, 3.0), 2: (4.0, 6.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}}
    ]

    ground_obj = 0.2

    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_52q():
    """ 52 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2}), release=1, due=11, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=2, due=12, weight=1.0)
    J3 = Job(id = 3, m_p=OrderedDict({1:2, 2:2, 3:3}), release=1, due=15, weight=1.0)

    JS = JobShop([J1, J2, J3])

    scheds = [
        {1: {1: (1.0, 3.0), 2: (4.0, 6.0)}, 2: {2: (2.0, 4.0), 3: (4.0, 6.0)}, 
         3: {1: (3.0, 5.0), 2: (6.0, 8.0), 3: (8.0, 11.0)}}
    ]

    ground_obj = 0.5952380952380949

    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_100q():
    """ 100 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2, 4:2}), release=1, due=15, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2, 4:2}), release=2, due=15, weight=1.0)
    J3 = Job(id = 3, m_p=OrderedDict({1:2, 2:2, 3:3}), release=1, due=16, weight=1.0)
    J4 = Job(id = 4, m_p=OrderedDict({2:2, 4:3}), release=1, due=16, weight=1.0)

    JS = JobShop([J1, J2, J3, J4])

    scheds = [
        {1: {1: (5.0, 7.0), 2: (7.0, 9.0), 4: (9.0, 11.0)}, 2: {2: (3.0, 5.0), 3: (5.0, 7.0), 4: (7.0, 9.0)}, 
         3: {1: (1.0, 3.0), 2: (5.0, 7.0), 3: (7.0, 10.0)}, 4: {2: (1.0, 3.0), 4: (3.0, 6.0)}}
    ]

    ground_obj = 0.8928571428571432

    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_151q():
    """ 151 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2, 4:2, 5:3}), release=1, due=25, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2, 4:2}), release=2, due=22, weight=1.0)
    J3 = Job(id = 3, m_p=OrderedDict({1:2, 2:2, 3:3}), release=2, due=22, weight=1.0)


    JS = JobShop([J1, J2, J3])

    scheds = [
        {1: {1: (4.0, 6.0), 2: (6.0, 8.0), 4: (8.0, 10.0), 5: (10.0, 13.0)}, 
         2: {2: (2.0, 4.0), 3: (4.0, 6.0), 4: (6.0, 8.0)}, 
         3: {1: (2.0, 4.0), 2: (4.0, 6.0), 3: (6.0, 9.0)}}
    ]

    ground_obj = 0.19999999999999996

    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def instance_199q():
    """ 199 q-bits instance """
    J1 = Job(id = 1, m_p=OrderedDict({1:2, 2:2, 4:2, 5:3}), release=1, due=25, weight=1.0)
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2, 4:2, 5:3}), release=2, due=25, weight=1.0)
    J3 = Job(id = 3, m_p=OrderedDict({1:2, 2:2, 3:3}), release=1, due=22, weight=1.0)
    J4 = Job(id = 4, m_p=OrderedDict({2:2, 4:3}), release=1, due=20, weight=1.0)

    JS = JobShop([J1, J2, J3, J4])

    scheds = [
        {1: {1: (3.0, 5.0), 2: (5.0, 7.0), 4: (7.0, 9.0), 5: (9.0, 12.0)}, 2: {2: (7.0, 9.0), 
         3: (9.0, 11.0), 4: (11.0, 13.0), 5: (13.0, 16.0)}, 
         3: {1: (1.0, 3.0), 2: (3.0, 5.0), 3: (5.0, 8.0)}, 4: {2: (1.0, 3.0), 4: (3.0, 6.0)}}
    ]

    ground_obj = 0.49047619047619095

    return {"js_problem":JS, "ground_scheds": scheds, "ground_obj": ground_obj}


def create_QUBO_dict(no_qbits, instance, psum, ppair):
        
        JS = instance["js_problem"]

        qubo = Implement_QUBO(JS, psum=psum, ppair=ppair)
        qubo.make_QUBO()
        assert qubo.qubo_variables.size == no_qbits

        ground_states = []
        # check the solution given
        for sched in instance["ground_scheds"]:
            x = qubo.schedule_2_x(sched)
            ground_states.append(x)

            # check feasibility
            assert qubo.nonfeasible_pair_constraints(x) == 0
            assert qubo.nonfeasible_sum_constraint(x) == 0
            # check objective
            assert qubo.compute_objective(x) == instance["ground_obj"]

            offset = qubo.compute_energy_offset(JS)

            energy = qubo.compute_objective(x) - offset

        Q = qubo.qubo_terms

        return {"qubo": Q,
                "objective_part": qubo.obj_terms,
                "ground_states": ground_states, 
                "ground_obj": instance["ground_obj"], 
                "ground_energy": energy, 
                "offset": offset}