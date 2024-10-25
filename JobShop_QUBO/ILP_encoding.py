""" solves ILP problem """
from docplex.mp.model import Model
from docplex.mp.solution import SolveSolution


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


    def objective_vars(self, JobShop):
        obj_vars = {}
        for Job in JobShop.jobs:
            j = Job.id
            m = Job.last_machine

            var_id = f"t_{j}_{m}"

            r = self.upperlim[var_id]  - self.lowerlim[var_id]

            obj_vars[var_id] = Job.weight / r
        
        return obj_vars



    def __init__(self, JobShop):

        lower_t, upper_t = self.get_t_vars(JobShop) 
        lower_y, upper_y = self.get_y_vars(JobShop)

        #self.JobShop = JobShop
        self.lowerlim = lower_t | lower_y
        self.upperlim = upper_t | upper_y
        self.obj_input = self.objective_vars(JobShop)
        """ the objective for """
        self.objoffset = 0
        self.set_objective_offset(JobShop)


    
    def set_objective_offset(self, JobShop):

        for Job in JobShop.jobs:
            j = Job.id
            m = Job.last_machine

            var_id = f"t_{j}_{m}"

            r = self.upperlim[var_id] - self.lowerlim[var_id]

            self.objoffset += Job.weight / r * self.lowerlim[var_id]
        



def make_ilp_docplex(ILP_vars):
    "create the docplex model return the docplex model object"
    model = Model(name='linear_programing_JobShop')

    lower_bounds = list(ILP_vars.lowerlim.values())
    upper_bounds = list(ILP_vars.upperlim.values())
    var_ids = ILP_vars.lowerlim.keys()


    variables = model.integer_var_dict(var_ids, lb=lower_bounds, ub=upper_bounds, name=var_ids)

    model.minimize(sum(variables[k] * weight for k, weight in ILP_vars.obj_input.items()) - ILP_vars.objoffset)


    return model


