from JobShop_QUBO import Job, JobShop


def test_JobShop():
    "test job"
    schedule = {1:2, 2:3}
    J = Job(schedule=schedule, release=1, due=10, weight=0.5)
    assert J.schedule == {1:2, 2:3}
    assert J.release == 1
    assert J.due == 10
    assert J.weight == 0.5

    "test job shop"
    JS = JobShop([J, J])
    assert JS.jobs == [J,J]
    assert JS.no_jobs == 2
    assert JS.no_machines == 2

    J1 = Job(schedule={2:2, 3:2}, release=1, due=10, weight=0.5)
    J2 = Job(schedule={1:1, 3:3}, release=1, due=10, weight=0.5)

    JS = JobShop([J, J1, J2])
    assert JS.jobs == [J,J1, J2]
    assert JS.no_jobs == 3
    assert JS.no_machines == 3
