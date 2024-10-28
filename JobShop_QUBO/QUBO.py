

# QUBO variables



class QUBO_Variables():
    """ class of QUBO variables """
    def __init__(self, JS):
        # t,m,j multiindex
        self.multiindices = self.make_multiindices(JS)
        self.q_vars = {}
        for k, (j,m,t) in self.multiindices.items():
            q = (j,m,t)
            self.q_vars[k] = q
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
    
    # tested till there

    def set_values(self, vals):
        """ set values of QUBO_var, given list or array in vals """
        assert len(vals) == self.size
        for i, v in enumerate(vals):
            assert v in [0,1]
            self.q_vars[i+1].value = v  # renumbering, Python is form 0
                        
        
    def get_k_and_varval(self, t_in:int, m_in:int, j_in:int):
        """ return index and [0,1] value of the QUBO variable of t_check,m_check,j_check """
        for k, (j,m,t) in self.multiindices.items():
            if (j,m,t) == (t_in, m_in,j_in):
                return k, self.q_vars[k].value
        return -1, -1