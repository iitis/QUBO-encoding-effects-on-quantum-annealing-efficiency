from itertools import chain

class Job:
    """ stores jobs """
    def __init__(self, schedule:dict, release:int, due:int, weight:float):
        """ schedule should be initialised {m1: p(j, m1), ....} """
        self.schedule = schedule
        self.release = release
        self.due = due
        self.weight = weight



class JobShop:
    """ stores job shop problem """

    def get_no_machines(self, jobs):
        machines = []
        for job in jobs:
            for m in job.schedule.keys():
                if m not in machines:
                    machines.append(m)
        return len(machines)

    def __init__(self, jobs: dict):
        self.jobs = jobs
        self.no_jobs = len(jobs)
        self.no_machines = self.get_no_machines(jobs)
