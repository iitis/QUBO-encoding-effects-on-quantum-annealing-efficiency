import pytest
from JobShop_QUBO import Job, JobShop
from collections import OrderedDict


def test_Job():
    "test job"
    m_p = OrderedDict({1:2, 2:3})
    J = Job(id = 1, m_p=m_p, release=1, due=10, weight=0.5)
    assert J.id == 1
    assert J.m_p == {1:2, 2:3}
    assert J.machines == [1,2]
    assert J.release == 1
    assert J.due == 10
    assert J.weight == 0.5
    assert J.no_machines == 2
    assert J.first_machine == 1
    assert J.last_machine == 2
    assert J.machines_but_last == [1]

    assert J.preceeding_machine(2) == 1
    assert J.machines_to_m(m_id = 1) == [1]
    assert J.machines_to_m(m_id = 2) == [1,2]

    assert J.machines_from_m(m_id = 1) == [2]
    assert J.machines_from_m(m_id = 2) == []

    limits = J.time_limits()
    assert limits == {1:(3, 7), 2: (6, 10)}
    assert type(limits) == OrderedDict



    # reversed order of machines
    m_p = OrderedDict({2:3, 1:2})
    J = Job(id = 1, m_p=m_p, release=1, due=10, weight=0.5)
    assert J.id == 1
    assert J.m_p == {2:3, 1:2}
    assert J.machines == [2,1]

    assert J.preceeding_machine(1) == 2
    assert J.first_machine == 2
    assert J.last_machine == 1


def test_Jobs_different_instance():
    m_p = OrderedDict({1:2, 2:3, 7:1, 3:5, 5:1})
    J = Job(id = 1, m_p=m_p, release=1, due=20, weight=0.5)
    assert J.machines == [1,2,7,3,5]
    assert J.machines_but_last == [1,2,7,3]

    assert J.preceeding_machine(5) == 3
    assert J.preceeding_machine(3) == 7


    assert J.machines_to_m(m_id = 1) == [1]
    assert J.machines_from_m(m_id = 1) == [2,7,3,5]


    assert J.machines_to_m(m_id = 3) == [1,2,7,3]
    assert J.machines_from_m(m_id = 3) == [5]

    assert J.machines_to_m(m_id = 7) == [1,2,7]
    assert J.machines_from_m(m_id = 7) == [3,5]

    assert J.machines_to_m(m_id = 5) == [1,2,7,3,5]
    assert J.machines_from_m(m_id = 5) == []



    m_p = OrderedDict({1:2})
    J = Job(id = 1, m_p=m_p, release=1, due=5, weight=0.5)
    assert J.machines == [1]
    assert J.machines_but_last == []

    assert J.machines_to_m(m_id = 1) == [1]
    assert J.machines_from_m(m_id = 1) == []

    assert J.time_limits() == {1:(3,5)}



def test_Job_errors():

    m_p = OrderedDict({2:3, 1:2})
    J = Job(id = 1, m_p=m_p, release=1, due=10, weight=0.5)
    with pytest.raises(ValueError) as exc_info:
        J.preceeding_machine(2)
    assert exc_info.value.args[0] == "this is first machine, no preceeding one"


    with pytest.raises(ValueError) as exc_info:
        J = Job(id = 1, m_p={2:3, 1:2}, release=1, due=10, weight=0.5)
    assert exc_info.value.args[0] == "machines should be in ordered dict"




def test_JobShop():
    "test job shop"

    J = Job(id = 1, m_p= OrderedDict({1:2, 2:3}), release=1, due=10, weight=0.5)
    JS = JobShop([J])
    assert JS.jobs == [J]
    assert JS.no_jobs == 1
    assert JS.no_machines == 2

    J1 = Job(id = 2, m_p=OrderedDict({2:2, 3:2}), release=1, due=10, weight=0.5)
    J2 = Job(id = 3, m_p=OrderedDict({1:1, 3:3}), release=1, due=10, weight=0.5)

    JS = JobShop([J, J1, J2])
    assert JS.jobs == [J,J1, J2]
    assert JS.no_jobs == 3
    assert JS.no_machines == 3
    assert JS.job_ids == [1,2,3]
    assert JS.no_jobs == 3

    assert JS.machines_2_jobs(job1_id = 2, job2_id = 3) == set([3])
    assert JS.machines_2_jobs(job1_id = 1, job2_id = 3) == set([1])
    assert JS.get_job(job_id = 2) == J1



def test_JobShop_errors():
    J = Job(id = 1, m_p=OrderedDict({1:2, 2:3}), release=1, due=10, weight=0.5)
    with pytest.raises(ValueError) as exc_info:
        S = JobShop([J, J])
    assert exc_info.value.args[0] == "jobs ids not unique"

    S = JobShop([J])
    with pytest.raises(ValueError) as exc_info:
        S.get_job(job_id = 2)
    assert exc_info.value.args[0] == "no job with id 2"
    
