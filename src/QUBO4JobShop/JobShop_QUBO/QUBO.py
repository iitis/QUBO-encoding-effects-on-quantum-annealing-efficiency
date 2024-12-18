import numpy as np

# QUBO variables



class QUBO_Variables():
    """ class of QUBO variables """
    def __init__(self, JS):
        # t,m,j multiindex
        self.multiindices = self.make_multiindices(JS)
        self.vars = {}
        self.vars_jmt = {}
        for k, (j,m,t) in self.multiindices.items():
            q = (j,m,t)
            self.vars[k] = q
            self.vars_jmt[q] = k
        self.size = k


    
    def make_multiindices(self, JS) -> dict:
        """ return dict of multi indices given the problem class 
        k -> (j,m,t)
        """
        multiindices = {}
        k = 0
        for Job in JS.jobs:
            j = Job.id
            for m in Job.machines:
                l,u = Job.time_limits[m]
                for t in range(l, u+1):
                        k += 1
                        multiindices[k] = (j,m,t)
        return multiindices
    


def add_to_dict(d:dict, key, value):
    
    """ 
    add to exisiting value otherwise create new entry
    """
    if key in d:
        d[key] += value
    else:
        d[key] = value



class Implement_QUBO():
    """ class of the QUBO formulation  Q[inds] = Q[i,i'] """
    def __init__(self, JS, psum:float, ppair:float):
        """ initialize  with penalty values and the objective function """
        assert psum > 0
        assert ppair > 0
        self.psum = psum
        self.ppair = ppair
        self.obj_terms = {}
        self.qubo_terms = {}
        self.qubo_variables = QUBO_Variables(JS)
        self.inds_sum_same = {}
        self.inds_sum_diff = {}
        self.inds_pair = {}
        self.JS = JS

    
    def qubo_vec2_schedule(self, x):
        if len(x) != self.qubo_variables.size:
            raise ValueError (f"sol length {len(x)} not equal to n.o. QUBO vars {self.qubo_variables.size}")

        schedule = {}
        sched4plotter = {}

        for Job in self.JS.jobs:
            j = Job.id
            jobs = {}
            ms = []
            times = []
            for m in Job.machines:
                ms.append(m)
                ms.append(m)
                l,u = Job.time_limits[m]
                for t in range(l, u+1):
                    k = self.qubo_variables.vars_jmt[(j,m,t)]
                    if x[k-1] == 1:

                        times.append(t - Job.m_p[m])
                        times.append(t)

                        jobs[m] = (t - Job.m_p[m], t)
            
            sched4plotter[j] = [ms, times]

            schedule[j] = jobs
        return schedule, sched4plotter



    def schedule_2_x(self, sched:dict):

        x = [0 for _ in range(self.qubo_variables.size)]

        for j, value in sched.items():
            for m, (t_start, t) in value.items():

                k = self.qubo_variables.vars_jmt[(j,m,t)]

                # Python numbering
                x[k-1] = 1
        return x






    def sum_constraint(self):
        """ add sum constraints  and return dict of corresponding multi indices"""
        for Job in self.JS.jobs:
            j = Job.id
            for m in Job.machines:
                l,u = Job.time_limits[m]
                # for each job
                for t in range(l, u+1):
                    for tp in range(l, u+1):
                        k = self.qubo_variables.vars_jmt[(j,m,t)]
                        kp = self.qubo_variables.vars_jmt[(j,m,tp)]
                        if t == tp:
                            add_to_dict(self.qubo_terms, key = (k, k), value= -self.psum)
                            self.inds_sum_same[(k,kp)] = (j,m,t)
                        else:
                            add_to_dict(self.qubo_terms, key = (k, kp), value= self.psum)
                            self.inds_sum_diff[(k,kp)] = [(j,m,t), (j,m,tp)]



    def objective(self):
        """ add objective terms to QUBO """
        for Job in self.JS.jobs:
            j= Job.id
            m = Job.last_machine
            l,u = Job.time_limits[m]
            for t in range(l, u+1):
                k = self.qubo_variables.vars_jmt[(j,m,t)]
                acctual_weight = Job.weight*(t-l)/(u-l)
                add_to_dict(self.qubo_terms, key = (k, k), value= acctual_weight)
                add_to_dict(self.obj_terms, key = (k, k), value= acctual_weight)
                


    def pair_constraint_process_t(self):
        """ add pair constraints  for minimal processing time constraint """
        for Job in self.JS.jobs:
            j = Job.id
            for m in Job.machines_but_first:
                mp = Job.preceeding_machine(m)
                l,u = Job.time_limits[m]
                lp,up = Job.time_limits[mp]
                proc_t = Job.m_p[m]

                for tp in range(lp, up+1):
                    lim = np.min([tp+proc_t, u+1])
                    for t in range(l, lim):
                        k = self.qubo_variables.vars_jmt[(j,m,t)]
                        kp = self.qubo_variables.vars_jmt[(j,mp,tp)]

                        add_to_dict(self.qubo_terms, key = (k, kp), value = self.ppair)

                        assert (k,kp) not in self.inds_pair
                        self.inds_pair[(k,kp)] = [(j,m,t), (j, mp,tp)]
                        # include symmetric version

                        add_to_dict(self.qubo_terms, key = (kp, k), value = self.ppair)

                        assert (kp,k) not in self.inds_pair
                        self.inds_pair[(kp,k)] = [(j,mp,tp), (j, m,t)]
        

    ## tested till there in this class

    def pair_constraint_occupancy(self):
        """ add pair constraints  for machine occupancy constraint """
        for Job in self.JS.jobs:
            for Job_p in self.JS.jobs:
                j = Job.id
                jp = Job_p.id
                if j != jp:
                    for m in self.JS.machines_2_jobs(Job, Job_p):
                        l,u = Job.time_limits[m]
                        lp,up = Job_p.time_limits[m]
                        proc_t = Job.m_p[m]
                        proc_tp = Job_p.m_p[m]
                        for t in range(l, u+ 1):
                            lim_d = np.max([lp, t - proc_t + 1])
                            lim_u = np.min([t  + proc_tp, up + 1])
                            for tp in range(lim_d, lim_u):

                                k = self.qubo_variables.vars_jmt[(j,m,t)]
                                kp = self.qubo_variables.vars_jmt[(jp,m,tp)]

                                add_to_dict(self.qubo_terms, key = (k, kp), value = self.ppair)
                                assert (k,kp) not in self.inds_pair
                                self.inds_pair[(k,kp)] = [(j,m,t), (jp, m, tp)]



    def make_QUBO(self):
        """ make QUBO, add terms of constraints and objective """
        self.sum_constraint()
        self.pair_constraint_process_t()
        self.pair_constraint_occupancy()
        self.objective()



    def nonfeasible_pair_constraints(self, x) -> int:
        """ 
        returns an int, number of broken pair constraints of the solution in Vars and jobs in P
        returns 0 if no pair constraints are broken
        """
        if len(x) != self.qubo_variables.size:
            raise ValueError (f"sol length {len(x)} not equal to n.o. QUBO vars {self.qubo_variables.size}")
        broken_constraints = 0
        for (k,kp) in self.inds_pair:
            # phyton numbering
            if x[k-1] == x[kp-1] == 1:
                broken_constraints += 1

        # Each constraint is counted twice due to symmetry
        return broken_constraints//2
    

    # These functions are for the analysis of solutions

    def nonfeasible_sum_constraint(self, x) -> int:
        """
        returns an int, number of broken sum constraints of the solution 
        """
        if len(x) != self.qubo_variables.size:
            raise ValueError (f"sol length {len(x)} not equal to n.o. QUBO vars {self.qubo_variables.size}")
    
        broken_constraints = 0
        for Job in self.JS.jobs:
            j = Job.id
            for m in Job.machines:
                l,u = Job.time_limits[m]
                count = 0
                for t in range(l, u+1):
                    k = self.qubo_variables.vars_jmt[(j,m,t)]
                    # Python indexing
                    count += x[k-1]
                
                broken_constraints += np.abs(count - 1)

        return broken_constraints
    

    def is_feasible(self, x) -> bool:

        return self.nonfeasible_sum_constraint(x) == 0 and self.nonfeasible_pair_constraints(x) == 0


    def compute_objective(self, x) -> float:
        """
        returns objective of the solution in Vars and jobs in P
        """
        if len(x) != self.qubo_variables.size:
            raise ValueError (f"sol length {len(x)} not equal to n.o. QUBO vars {self.qubo_variables.size}")
    
        objective = 0

        for Job in self.JS.jobs:
            j= Job.id
            m = Job.last_machine
            l,u = Job.time_limits[m]
            for t in range(l, u+1):
                k = self.qubo_variables.vars_jmt[(j,m,t)]
                # Python numbering
                objective += Job.weight*(t-l)/(u-l)*x[k-1]

        assert objective <= self.JS.max_obj  
        return objective
    

    def compute_energy(self, x) -> float:
        """
        returns energy of QUBO
        """
        if len(x) != self.qubo_variables.size:
            raise ValueError (f"sol length {len(x)} not equal to n.o. QUBO vars {self.qubo_variables.size}")
        e = 0
        for i in range(self.qubo_variables.size):
            for j in range(self.qubo_variables.size):
                if (i+1, j+1) in self.qubo_terms:  # sparcity problem
                    e += x[i]*self.qubo_terms[(i+1, j+1)]*x[j]
        
        return e
    

    def compute_energy_offset(self, JS) -> float:
        """
        returns energy offset (objective - energy)
        """
        offset = 0
        for job in JS.jobs:
            offset += job.no_machines * self.psum

        return offset





