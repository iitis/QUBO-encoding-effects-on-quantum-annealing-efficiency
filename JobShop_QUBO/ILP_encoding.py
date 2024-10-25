""" solves ILP problem """

from .jobshop import Job, JobShop


class ILP_Variables:

    def get_t_vars(self, JobShop):
        lower = {}
        upper = {}
        for Job in JobShop.jobs:
            j= Job.id
            lims_job = Job.time_limits()
            for m in Job.machines:
                var = f"t_{j}_{m}"

                (lower[var], upper[var]) = lims_job[m]
        return lower, upper

    def get_y_vars(self, JobShop):

        lower = {}
        upper = {}
        for j1 in JobShop.job_ids:
            for j2 in JobShop.job_ids:
                if j1 < j2:
                    for m in JobShop.machines_2_jobs(job1_id = j1, job2_id = j2):
                        var_id = f"y_{j1}_{j2}_{m}"
                        lower[var_id] = 0
                        upper[var_id] = 1

        return lower, upper



    def __init__(self, JobShop):

        lower_t, upper_t = self.get_t_vars(JobShop) 
        lower_y, upper_y = self.get_y_vars(JobShop)


        self.lowerlim = lower_t | lower_y
        self.upperlim = upper_t | upper_y



def make_ilp_docplex(prob, ILP_vars):
    "create the docplex model return the docplex model object"
    model = Model(name='linear_programing_JobShop')

    lower_bounds = ILP_vars.lowerlim.values()
    upper_bounds = ILP_vars.upperlim.values()
    var_ids = ILP_vars.lowerlim.keys()


    variables = model.integer_var_dict(var_ids, lb=lower_bounds, ub=upper_bounds, name=var_ids)


