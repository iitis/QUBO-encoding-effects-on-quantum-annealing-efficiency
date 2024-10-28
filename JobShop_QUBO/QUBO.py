

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
            t_lim = Job.time_limits()
            for m in Job.machines:
                l,u = t_lim[m]
                for t in range(l, u+1):
                        k += 1
                        multiindices[k] = (j,m,t)
        return multiindices
    
    # tested in the class till there

    def set_values(self, vals):
        """ set values of QUBO_var, given list or array in vals """
        assert len(vals) == self.size
        for i, v in enumerate(vals):
            assert v in [0,1]
            self.vars[i+1].value = v  # renumbering, Python is form 0
                        
        


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
        self.psum = psum
        self.ppair = ppair
        self.qubo_terms = {}
        self.qubo_variables = QUBO_Variables(JS)
        self.inds_sum_same = {}
        self.inds_sum_diff = {}

    # TODO think whether JS should be called within the class
    def sum_constraint(self, JS):
        """ add sum constraints  and return dict of corresponding multi indices"""
        for Job in JS.jobs:
            j = Job.id
            t_lim = Job.time_limits()
            for m in Job.machines:
                l,u = t_lim[m]
                # for each job
                for t in range(l, u+1):
                    for tp in range(l, u+1):
                        k = self.qubo_variables.vars_jmt[(j,m,t)]
                        kp = self.qubo_variables.vars_jmt[(j,m,tp)]
                        if t == tp:
                            add_to_dict(self.qubo_terms, key = (k, kp), value= - self.psum)
                            self.inds_sum_same[(k,kp)] = (j,m,t)
                        else:
                            add_to_dict(self.qubo_terms, key = (k, kp), value= self.psum)
                            self.inds_sum_diff[(k,kp)] = [(j,m,t), (j,m,tp)]

    

    ## tested till there in this class

    def pair_constraint(self, Vars, JS):
        """ add pair constraints  and return dict of corresponding multi indices """
        inds_multiinds ={}
        for k, (j,m,t) in Vars.multiindices.items():
            for kp, (jp,mp,tp) in Vars.multiindices.items():
                # the same machine
                if m == mp:
                    # different jobs
                    if j != jp:
                        tau = JS.jobs[j].process_t
                        taup = JS.jobs[jp].process_t
                        if t-taup < tp < t+tau:
                            self.add_qubo_term((k, kp), self.ppair)
                            inds_multiinds[(k,kp)] = [(t,m,j), (tp, mp,jp)]
        
        return inds_multiinds
    

    def objective(self, Vars, P):
        """ add objective terms to QUBO """
        for k, (t,m,j) in Vars.multiindices.items():
            weight = P.jobs[j].priority
            penalty = weight*self.obj(t + P.jobs[j].process_t - P.jobs[j].release_t)
            self.add_qubo_term((k, k), penalty)

    def make_QUBO(self, Vars, P):
        """ make QUBO, initialize, then add terms of constraints and objective """
        self.sum_constraint(Vars)
        self.pair_constraint(Vars, P)
        self.objective(Vars, P)


    # These functions are for the analysis of solutions

    def chech_feasibility_pair_constraint(self, Vars, P) -> int:
        """ 
        returns an int, number of broken pair constraints of the solution in Vars and jobs in P
        returns 0 if no pair constraints are broken
        """
        broken_constraints = 0
        for (k,kp) in self.pair_constraint(Vars, P):
            if Vars.vars[k].value == Vars.vars[kp].value == 1:
                broken_constraints += 1

        # Each constraint is counted twice due to symmetry
        return broken_constraints//2
    

    def check_feasibility_sum_constraint(self, Vars, P) -> int:
        """
        returns an int, number of broken sum constraints of the solution in Vars and jobs in P
        returns 0 if no sum constraints are broken
        """
        broken_constraints = 0
        for j_check in P.jobs:
            starts = 0
            for k, (j,m,t) in Vars.multiindices.items():
                if j == j_check:
                    starts += Vars.vars[k].value
            if starts != 1:
                broken_constraints += 1
        return broken_constraints


    def compute_objective(self, Vars, P) -> float:
        """
        returns objective of the solution in Vars and jobs in P
        """
        objective = 0
        for k, (j,m,t) in Vars.multiindices.items():
            obj = Vars.vars[k].value * self.obj(t + P.jobs[j].process_t - P.jobs[j].release_t)
            obj = obj * P.jobs[j].priority
            objective += obj    
        return objective
