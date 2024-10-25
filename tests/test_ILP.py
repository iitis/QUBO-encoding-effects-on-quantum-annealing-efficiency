import pytest
from JobShop_QUBO import Job, JobShop, ILP_Variables
from collections import OrderedDict


def test_var_creation():
    J2 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J3 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)

    JS = JobShop([J2, J3])

    ILP = ILP_Variables(JS)
    assert ILP.lowerlim == {'t_2_2': 3, 't_2_3': 5, 't_3_1': 2, 't_3_3': 5, 'y_2_3_3': 0}
    assert ILP.upperlim == {'t_2_2': 8, 't_2_3': 10, 't_3_1': 7, 't_3_3': 10, 'y_2_3_3': 1}
