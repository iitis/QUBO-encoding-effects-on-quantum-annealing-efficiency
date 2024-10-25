""" solves ILP problem """
from docplex.mp.model import Model
from docplex.mp.solution import SolveSolution


from .jobshop import Job, JobShop


 
class ILP_Encoding:



    def get_y_vars(self, JobShop):

        jobs_machines = []
        lower = {}
        upper = {}
        for j1 in JobShop.job_ids:
            for j2 in JobShop.job_ids:
                if j1 < j2:
                    for m in JobShop.machines_2_jobs(job1_id = j1, job2_id = j2):
                        var_id = f"y_{j1}_{j2}_{m}"
                        lower[var_id] = 0
                        upper[var_id] = 1

                        jobs_machines.append((j1, j2, m))

        return lower, upper, jobs_machines



    def __init__(self, JobShop):

        lower_t = {}
        upper_t = {}
        for (j, m), (l,u) in JobShop.t_ranges.items():
            var = f"t_{j}_{m}"
            lower_t[var] = l
            upper_t[var] = u


        lower_y, upper_y, ys = self.get_y_vars(JobShop)

        self.JobShop = JobShop
        self.ys = ys
        self.lowerlim = lower_t | lower_y
        self.upperlim = upper_t | upper_y


        """ the objective  """
        obj_vars = {}
        for (j,m), w in JobShop.obj_vars.items():
            obj_vars[f"t_{j}_{m}"] = w

        self.obj_input = obj_vars 
        self.objoffset = JobShop.objoffset
        """  constraints """
        
        self.process_t_constr = self.processing_time_constraint()
        self.machine_constraint = self.machine_occupancy_constraint()

    
    def processing_time_constraint(self):
        """ left var + left const <= right var
              t_j_mp  p_j_m <+ t_j_m
        """ 
        constraints = []
        for Job in self.JobShop.jobs:
            j = Job.id
            m0 = Job.first_machine
            for m in Job.machines:
                if m != m0:
                    mp = Job.preceeding_machine(m)

                    constraints.append([f"t_{j}_{m0}", Job.m_p[m] , f"t_{j}_{m}"])

        return constraints

    
    def machine_occupancy_constraint(self, M = 50):
        """ left var + left const <=  right const + right const * right var1 +  right var2"""
        constraints = []
        for (j,jp,m) in self.ys:
            tp = f"t_{jp}_{m}"
            t = f"t_{j}_{m}"
            y = f"y_{j}_{jp}_{m}"

            JS = self.JobShop
            Job = JS.get_job(job_id =j)
            pt = Job.m_p[m]
            "t_jp_m + p_j_m <= 0 + M * y_j_jp_m, t_j_m"

            constraints.append([tp, pt, 0, M, y, t])
            """ other way around"""
            "t_j_m + p_jp_m <= M - M * y_j_jp_m, t_jp_m"
            Job = JS.get_job(job_id =jp)
            pt = Job.m_p[m]
            constraints.append([t, pt, M, -M, y, tp])

        return constraints



       


def make_ilp_docplex(ILP_vars):
    "create the docplex model return the docplex model object"
    model = Model(name='linear_programing_JobShop')

    lower_bounds = list(ILP_vars.lowerlim.values())
    upper_bounds = list(ILP_vars.upperlim.values())
    var_ids = ILP_vars.lowerlim.keys()


    variables = model.integer_var_dict(var_ids, lb=lower_bounds, ub=upper_bounds, name=var_ids)

    for (lhs_var, lhs_number, rhs_var) in ILP_vars.process_t_constr:
        model.add_constraint(
            variables[lhs_var] + lhs_number <= variables[rhs_var])


    for (lhs_v, lhs_num, rhs_num, rhs_const, rhs_v1, rhs_v2) in ILP_vars.machine_constraint:
        model.add_constraint(
            variables[lhs_v] + lhs_num <= rhs_num + rhs_const*variables[rhs_v1] + variables[rhs_v2] )

    model.minimize(sum(variables[k] * weight for k, weight in ILP_vars.obj_input.items()) - ILP_vars.objoffset)


    return model


def docplex_sol2_schedule(model, sol, ILP_vars):
    for var in model.iter_variables():
        print(f"{var.name}: {var.solution_value}")

    schedule = {}

    sched4plotter = {}
    JS = ILP_vars.JobShop

    for Job in JS.jobs:
        j = Job.id
        jobs = {}
        ms = []
        times = []
        for m in Job.machines:
            ms.append(m)
            ms.append(m)

            t = sol[f't_{j}_{m}']

            times.append(t - Job.m_p[m])
            times.append(t)

            jobs[m] = (t - Job.m_p[m], t)

        sched4plotter[j] = [ms, times]

        schedule[j] = jobs

    return schedule, sched4plotter

    




