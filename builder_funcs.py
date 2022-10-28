import numpy as np
from scipy.stats import norm
from collections import Iterable
from scipy import stats
from scipy.optimize import minimize
import pandas as pd
    
        
# define objective functions for Weibull (accuracy units)
def weibull(x, m, n,  par, flag):
    gamma = par[0]  # guess rate [fixed and given by experiment]
    lam   = par[1]  # guess rate shouldnt  exceed 2%
    alpha = par[2]  # threshold
    beta  = par[3]  # slope

    fit = gamma+(1-gamma-lam)*(1-np.exp(-1*(x/alpha)**beta))

    if flag == True:
      return fit
    else:
        cost = sum(-(n*np.log(fit)+(m-n)*np.log(1-fit)))
        return cost
      
# evaluates the chosen function with given parameters
def func_run(x,par,flag,fc):
    if fc=='weibull':
      fit = weibull(x,[],[],par,flag)
    return fit

# finds best fitting parameters for given function 
def func_fit(x0,bnds,x,m,n,flag,fc):
  if fc == 'weibull':
    fun = lambda par: weibull(x,m,n,par,flag)
  return  minimize(fun,x0,method='SLSQP',bounds=bnds)
     
# split alphanumerical into string+num i.e. factor1 = 'factor','1'
def splitstr(s):
  num_split = s.rstrip('0123456789')
  str_split = s[len(num_split):]
  return num_split, str_split

#if iterable turn multiple lists into 1
def flatten(lis):
     for item in lis:
         if isinstance(item, Iterable) and not isinstance(item, str):
             for x in flatten(item):
                 yield x
         else:        
             yield item

# splits a data frame by a column index [factor in this case]
def split_fac(data,col_labels,split):
  splitFac = data[col_labels[split]].unique()
  DataFrameDict = {elem: pd.DataFrame() for elem in splitFac}
  for key in DataFrameDict.keys():
      DataFrameDict[key]=data[:][data[col_labels[split]]==key]
      
      return DataFrameDict
   
# for testing reasons -- can very loosely convert from d-prime to % correct via 
def dprime2corr(dprime):
    pcorr = [norm.cdf(d)**2 for d in dprime]
    return pcorr
     