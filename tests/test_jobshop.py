from JobShop_QUBO import Job


def test_Job():
    "test empty jon"
    J = Job()
    assert J.schedule == {}
    assert J.release == 0
    assert J.due == 0
    assert J.weight == 0
    print("tests")
