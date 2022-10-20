def fit_psy_func(file,units):
    '''
    Fits individual data and plots mean fit with errorbars 

        inputs: file:    .csv file name (ie., data.csv) including all performance data in specified units with column labels
        organized as such: 
    1st col - x-labels (ie, contrast values)
    2nd col - y-data   (ie, % correct or dprime)
    3rd col - numerical condition labels (ie, if attention task valid/neutral/invalid, then 1,2,3)
    4th col - numerical factor labels (ie, if conditions all attention cues then enter 1)
    5th col - numerical subject labels
    Example:
    | contrast | dprime | conditions | factors| subjects |
    2         0.02        1           1        1
    7         1.1         1           1        1
    13        1.6         1           1        1
    24        1.75        1           1        1
    46        2.2         1           1        1
    85        2.25        1           1        1
    ...
    2         0.01        2           1        1
    7         0.8         2           1        1
    ...
    2         0.01        3           1        1
    7         0.8         3           1        1
    ...        ...        ...         ...      ...n
    -----------------------------------------------------

    units: if "accuracy" then units assumed to be in % correct from X to 100%
    if "dprime" then assumes units are 0 to infinity

    **if log x-vals the code defaults to fitting a log-Weibull or Gumble function
    **if linear x-vals the code defaults to fitting a Weibull function
    **for simplicity cost function is defined as sum squared error**
    **no implementation exists for minimization for negative log likelihood as
    **that would require single trial data

    CREATED BY: Antonio Fernandez [Oct. 20, 2022]
    contact: antoniofs23@gmail.com
    moreinfo: antoniofs23.github.io/web
    '''

    import numpy as np
    import matplotlib as plt
    import pandas as pd
    from scipy import stats
    from scipy.optimize import minimize

    # if % correct check what chance is
    if units=='accuracy':
        b = input('what is chance performance in your task?, i.e., if 2 resp alternatives (yes/no) enter 50')
    else:
       b = 0
    # read csv file 
    data = pd.read_csv(file)
    col_labels = data.columns # extract column labels    
    xvals = np.unique(data[data.columns[0]]) # extract x-values from 1st col 
    
    # extract number of conditions/factors/subjects
    num_cond = np.unique(data[data.columns[2]])
    num_fac  = np.unique(data[data.columns[3]])
    num_subs = np.unique(data[data.columns[4]])

    # create a dataframe dict to split factors
    UniqueNames = data.factors.unique()
    DataFrameDict = {elem : pd.DataFrame() for elem in UniqueNames}
    for key in DataFrameDict.keys():
        DataFrameDict[key]=data[:][data.factors == key] 

    # remove 0s for checks
    xvals = [num or 0.001 for num in xvals] 

    # check if x-vals are linearly or logarithmically spaced
    # compare to linear spacing
    res_line = stats.linregress(xvals,np.linspace(xvals[0],xvals[-1],len(xvals)))
    # compare to logarithmic spacing
    res_log = stats.linregress(xvals,np.logspace(np.log10(xvals[0]),np.log10(xvals[-1]),len(xvals)))

    # designated a flag for linear or log spacing
    if res_line.rvalue > res_log.rvalue:
        fun = lambda par: weibull(xvals,x_data,par,flag=False)
        print('assuming linear x-values')
    else:
        fun = lambda par: gumbel(xvals,x_data,par,flag=False)
        print('assuming logarithmic x-values')

    # define objective functions for Weibull and log-Weibull (GUMBEL)
    def weibull(x,data,par,flag):
        gamma = par[0] # guess rate [fixed and given by experiment] 
        lam   = par[1] # guess rate shouldnt  exceed 2%
        alpha = par[2] # threshold
        beta  = par[3] # slope

        fit = gamma+(1-gamma-lam)*(1-np.exp(-1*(x/alpha)**beta))
            
        cost = sum(data-fit)**2
        if flag==True:
          return [fit,cost]
        else:
          return cost
          
    def gumbel(x,data,par,flag):
        gamma = par[0] # guess rate [fixed and given by experiment] 
        lam   = par[1] # guess rate shouldnt  exceed 2%
        alpha = par[2] # threshold
        beta  = par[3] # slope

        fit = gamma+(1-gamma-lam)*(1-np.exp(-1*10**(beta*(x-alpha))))
            
        cost = sum(data-fit)**2
        if flag==True:
          return [fit,cost]
        else:
          return cost
    
    # relaxed bounds and starting points for parameter space
    bnds = ((b,b),(0,0.02),(np.min(xvals),np.max(xvals)),(1,5)) # parameter lower and upper bounds
    x0 = (0.5,0.01,xvals[1],2) # starting point for parameters
    #fit the function to each condition and individual subjects
    st_params = np.zeros(shape=(len(UniqueNames),len(num_subs),len(num_cond),len(x0)))
    for f in range(len(UniqueNames)):        # factors
        temp_data = DataFrameDict[UniqueNames[f]]
        for s in range(len(num_subs)):       # subjects
            s_data = temp_data[:][temp_data.subjects==num_subs[s]]
            for c in range(len(num_cond)):   # conditions
                c_data = s_data[:][temp_data.conditions==num_cond[c]]
                x_data = np.array(c_data[c_data.columns[1]]) 
                res = minimize(fun,x0,method='Nelder-Mead',bounds=bnds)          
                st_params[f,s,c,:]=res.x # store parameters


    # fit the mean across conditions for show
     
    return st_params  
