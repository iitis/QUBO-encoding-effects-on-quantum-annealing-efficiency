""" solves ILP problem """
from docplex.mp.model import Model
from docplex.mp.solution import SolveSolution


from .jobshop import Job, JobShop


 
class ILP_Encoding:



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

        lower_t = {}
        upper_t = {}
        for (j, m), (l,u) in JobShop.t_ranges.items():
            var = f"t_{j}_{m}"
            lower_t[var] = l
            upper_t[var] = u


        lower_y, upper_y = self.get_y_vars(JobShop)

        self.JobShop = JobShop
        self.lowerlim = lower_t | lower_y
        self.upperlim = upper_t | upper_y

        """ the objective  """
        obj_vars = {}
        for (j,m), w in JobShop.obj_vars.items():
            obj_vars[f"t_{j}_{m}"] = w

        self.obj_input = obj_vars 
        self.objoffset = JobShop.objoffset
        """  constraints """
        
        self.processing_time_constraint(JobShop)



    
    def processing_time_constraint(self, JobShop):
        """ left val + left var <= right var""" 
        constraints = []
        for Job in JobShop.jobs:
            j = Job.id
            m0 = Job.first_machine
            for m in Job.machines:
                if m != m0:
                    mp = Job.preceeding_machine(m)

                    print(j, mp, m)
                    constraints.append([f"t_{j}_{m0}", Job.m_p[m] , f"t_{j}_{m}"])

       


def make_ilp_docplex(ILP_vars):
    "create the docplex model return the docplex model object"
    model = Model(name='linear_programing_JobShop')

    lower_bounds = list(ILP_vars.lowerlim.values())
    upper_bounds = list(ILP_vars.upperlim.values())
    var_ids = ILP_vars.lowerlim.keys()


    variables = model.integer_var_dict(var_ids, lb=lower_bounds, ub=upper_bounds, name=var_ids)

    model.minimize(sum(variables[k] * weight for k, weight in ILP_vars.obj_input.items()) - ILP_vars.objoffset)


    return model


