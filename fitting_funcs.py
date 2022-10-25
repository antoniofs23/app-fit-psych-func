import numpy as np
from scipy.stats import norm

# define objective function for Nakarushton (d-prime units)
def nakarushton(x,data,par,flag):
    dmax = par[0]
    c50  = par[1]
    n    = par[2]
    b    = par[3]
 
    fit = dmax*((x**n)/(x**n+c50**n))+b
        
    if flag==True:
      return fit
    else:
      cost = sum(data-fit)**2
      return cost
        
# define objective functions for Weibull (accuracy units)
def weibull(x, data, par, flag):
    gamma = par[0]  # guess rate [fixed and given by experiment]
    lam = par[1]  # guess rate shouldnt  exceed 2%
    alpha = par[2]  # threshold
    beta = par[3]  # slope

    fit = gamma+(1-gamma-lam)*(1-np.exp(-1*(x/alpha)**beta))

    if flag == True:
      return fit
    else:
        cost = sum(data-fit)**2
        return cost

# for testing reasons -- can very loosely convert from d-prime to % correct via 
def dprime2corr(dprime):
    pcorr = [norm.cdf(d)**2 for d in dprime]
    return pcorr
     