from collections import OrderedDict


class Job:
    """ stores jobs """

    def get_machines_ids(self):
        return list(self.m_p.keys())

    def preceeding_machine(self, m_id):
        i = self.machines.index(m_id)
        if i == 0:
            raise ValueError ("this is first machine, no preceeding one")
        return self.machines[i-1]



    def get_first_machine(self):
        return self.machines[0]

    def get_last_machine(self):
        k = self.no_machines - 1
        return self.machines[k]


    def machines_to_m(self, m_id):
        m = self.machines
        i = m.index(m_id) + 1
        return self.machines[0:i]

    def machines_from_m(self, m_id):
        m = self.machines
        i = m.index(m_id) + 1
        l = len(m)
        return self.machines[i:l]

    
    def time_limits(self):
        # TODO this may be moved to the initi field to improve efficiency if necessary 
        all_processing_time = sum(list(self.m_p.values()))
        t_min = self.release
        t_max = self.due - all_processing_time

        t_lim = OrderedDict()

        for key, value in self.m_p.items():
            t_min += value
            t_max += value
            t_lim[key] = (t_min, t_max)

        assert t_max == self.due

        return t_lim



    def __init__(self, id:int, m_p:OrderedDict, release:int, due:int, weight:float):
        """ m_p should be initialised {m1: p(j, m1), ....} """

        if type(id) != int:
            raise ValueError (f"job id type {type(id)} should be int")

        self.id =id
        self.m_p = m_p
        self.release = release
        self.due = due
        self.weight = weight
        self.machines = self.get_machines_ids()
        self.no_machines = len(self.machines)
        self.machines_but_last = self.machines[0: self.no_machines-1]

        self.first_machine = self.get_first_machine()
        self.last_machine = self.get_last_machine()

        if type(self.m_p) != OrderedDict:
            raise ValueError ("machines should be in ordered dict")




class JobShop:
    """ stores job shop problem """

    def get_no_machines(self):
        machines = []
        for job in self.jobs:
            machines += job.machines
    
        unique_m = list(set(machines))
        return len(unique_m)


    def get_jobs_inds(self):
        return [job.id for job in self.jobs]

    def get_job(self, job_id):
        for job in self.jobs:
            if job.id == job_id:
                return ( job )
        raise ValueError (f"no job with id {job_id}")

    
    def machines_2_jobs(self, job1_id, job2_id) -> set:
        job1 = self.get_job(job1_id)
        job2 = self.get_job(job2_id)
        return( set.intersection(set(job1.machines), set(job2.machines)) )


    
    def get_t_with_ranges(self):
        t_ranges = {}

        for Job in self.jobs:
            j= Job.id
            lims_job = Job.time_limits()
            for m in Job.machines:

                t_ranges[(j,m)] = lims_job[m]
        return t_ranges



    def get_objective_vars(self):

        for Job in self.jobs:
            j = Job.id
            m = Job.last_machine

            (l,u)  = self.t_ranges[(j,m)]

            self.obj_vars[(j,m)] = Job.weight / (u-l)

            self.objoffset += Job.weight * l / (u-l)
        



    def __init__(self, jobs:list):

        self.jobs = jobs
        self.no_jobs = len(jobs)
        self.no_machines = self.get_no_machines()
        self.job_ids = self.get_jobs_inds()
        self.no_jobs = len(self.job_ids)

        if not self.no_jobs == len(list(set(self.job_ids))):
            raise ValueError ("jobs ids not unique")

        self.t_ranges = self.get_t_with_ranges()
        self.obj_vars = {}
        self.objoffset = 0
        self.get_objective_vars()

