import pytest
from JobShop_QUBO import Job, JobShop


def test_Job():
    "test job"
    schedule = {1:2, 2:3}
    J = Job(id = 1, schedule=schedule, release=1, due=10, weight=0.5)
    assert J.id == 1
    assert J.schedule == {1:2, 2:3}
    assert J.release == 1
    assert J.due == 10
    assert J.weight == 0.5

    assert J.get_machines_ids() == [1,2]




def test_JobShop():
    "test job shop"

    J = Job(id = 1, schedule= {1:2, 2:3}, release=1, due=10, weight=0.5)
    JS = JobShop([J])
    assert JS.jobs == [J]
    assert JS.no_jobs == 1
    assert JS.no_machines == 2

    J1 = Job(id = 2, schedule={2:2, 3:2}, release=1, due=10, weight=0.5)
    J2 = Job(id = 3, schedule={1:1, 3:3}, release=1, due=10, weight=0.5)

    JS = JobShop([J, J1, J2])
    assert JS.jobs == [J,J1, J2]
    assert JS.no_jobs == 3
    assert JS.no_machines == 3

    assert JS.get_ids(jobs) == [1,2,3]



def test_JobShop_errors():
    J = Job(id = 1, schedule={1:2, 2:3}, release=1, due=10, weight=0.5)
    with pytest.raises(ValueError) as exc_info:
        S = JobShop([J, J])
    assert exc_info.value.args[0] == "jobs ids not unique"
    
