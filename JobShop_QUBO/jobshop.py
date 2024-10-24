from itertools import chain

class Job:
    """ stores jobs """

    def get_machines_ids(self):
        return list(self.schedule.keys())


    def __init__(self, id:int, schedule:dict, release:int, due:int, weight:float):
        """ schedule should be initialised {m1: p(j, m1), ....} """


        self.id =id
        self.schedule = schedule
        self.release = release
        self.due = due
        self.weight = weight






class JobShop:
    """ stores job shop problem """

    def get_no_machines(self, jobs):
        machines = []
        for job in jobs:
            machines += job.get_machines_ids()
    
        unique_m = list(set(machines))
        return len(unique_m)


    def get_ids(self, jobs:list):
        return [job.id for job in jobs]


    def __init__(self, jobs:list):

        ids = self.get_ids(jobs)
        if not len(ids) == len(list(set(ids))):
            raise ValueError ("jobs ids not unique")

        self.jobs = jobs
        self.no_jobs = len(jobs)
        self.no_machines = self.get_no_machines(jobs)
