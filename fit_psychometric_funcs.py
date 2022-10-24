from turtle import color


def fit_psy_func(file,units,chance=0,color=False):
    '''
    Fits individual data and plots mean fit with errorbars 

        inputs: file:    .csv file name (ie., data.csv) including all performance data in specified units with column labels
        organized as such: 
    1st col - x-labels (ie, contrast values)
    2nd col - y-data   (ie, % correct or dprime)
    3rd col - alphanumerical condition labels (ie, if attention task then labels: valid/neutral/invalid OR 1,2,3)
    4th col - alphanumerical factor labels (ie, if conditions all attention then enter 1 OR attention)
    5th col - numerical subject labels
    Example with numerical labels:
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
    
    if units = 'accuracy'
    **if log x-vals the code defaults to fitting a log-Weibull or Gumble function
    **if linear x-vals the code defaults to fitting a Weibull function
    **for simplicity cost function is defined as sum squared error**
    if units = 'dprime'
    fits a nakarushton function

    chance: what is chance performance in your task? if 2AFC then enter 50
            defaults to zero if not specified

    color: specifiy a color per condition ranging from 0 to 1. Will be chosen 
           pseudo-randomly (from 100 possible) if unspecified
    
    **no implementation exists for minimization via negative log likelihood as
    **that would require single trial data

    CREATED BY: Antonio Fernandez [Oct. 20, 2022]
    contact: antoniofs23@gmail.com
    '''
    import random 
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from scipy import stats
    from scipy.optimize import minimize

    # read csv file 
    data = pd.read_csv(file)
    col_labels = data.columns # extract column labels    
    xvals = np.unique(data[data.columns[0]]) # extract x-values from 1st col 
    
    # extract number of conditions/factors/subjects
    num_x    = np.unique(data[data.columns[0]])
    num_cond = np.unique(data[data.columns[2]])
    num_fac  = np.unique(data[data.columns[3]])
    num_subs = np.unique(data[data.columns[4]])
    if units=='dprime':
        max_y    = np.max(data[data.columns[1]])
    else:
        max_y = 1
    min_y = chance 
    
    # check if user input colors
    if color:
        RGB = color   
    else:
        # generate an arbitrary number of colors (one per condition)
        # that are evenly distrubuted according to the golden ratio
        RGB=[]; RGB_list = np.random.permutation(100)
        for ii in range(0,len(num_cond)*3):
            id  = RGB_list[ii]
            phi = (1+np.sqrt(5))/2
            RGB.append(id*phi-np.floor(id*phi))
        RGB = list(np.array_split(RGB,3))
 
 
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
        fc = 'weibull'; flg = 'linear'
        print('assuming linear x-values')
    else:
        fc = 'gumbel'; flg = 'log'
        print('assuming logarithmic x-values')

    # if % correct check what chance is
    b = chance
    if units=='dprime':
         fc = 'nakarushton'
        
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
        
        
    # define objective functions for Weibull and log-Weibull (GUMBEL) (accuracy units)
    def weibull(x,data,par,flag):
        gamma = par[0] # guess rate [fixed and given by experiment] 
        lam   = par[1] # guess rate shouldnt  exceed 2%
        alpha = par[2] # threshold
        beta  = par[3] # slope

        fit = gamma+(1-gamma-lam)*(1-np.exp(-1*(x/alpha)**beta))
            
        if flag==True:
          return fit
        else:
          cost = sum(data-fit)**2
          return cost
        
    def gumbel(x,data,par,flag):
        gamma = par[0] # guess rate [fixed and given by experiment] 
        lam   = par[1] # guess rate shouldnt  exceed 2%
        alpha = par[2] # threshold
        beta  = par[3] # slope

        fit = gamma+(1-gamma-lam)*(1-np.exp(-1*10**(beta*(x-alpha))))
            
        if flag==True:
          return fit
        else:
          cost = sum(data-fit)**2
          return cost
    
    def func_run(x,data,par,flag,fc):
        if fc=='nakarushton':
            fit = nakarushton(x,data,par,flag)
        if fc=='weibull':
            fit = weibull(x,data,par,flag)
        if fc=='gumbel':
            fit = gumbel(x,data,par,flag)
        return fit
    
    def func_fit(x0,bnds,x,data,flag,fc):
        if fc == 'nakarushton':
            fun = lambda par: nakarushton(x,data,par,flag)
        if fc == 'gumbel':          
            fun = lambda par: gumbel(x,data,par,flag)
        if fc == 'weibull':
            fun = lambda par: weibull(x,data,par,flag)
        return  minimize(fun,x0,method='Nelder-Mead',bounds=bnds)
    
    # relaxed bounds and starting points for parameter space
    if units=='accuracy':
        bnds = ((b,b),(0,0.02),(np.quantile(xvals,0.25),np.quantile(xvals,0.75)),(1,5)) # parameter lower and upper bounds
        x0 = (0.5,0.01,xvals[1],2) # starting point for parameters
    else:
        bnds = ((0.1,8),(np.quantile(xvals,0.25),np.quantile(xvals,0.75)),(1,5),(-0.3,0.5)) # parameter lower and upper bounds
        x0 = (3,xvals[2],2,0.02) # starting point for parameters
        
    #fit the function to each condition and individual subjects
    st_params = np.zeros(shape=(len(UniqueNames),len(num_subs),len(num_cond),len(x0)))
    sub_fits = np.zeros(shape=(len(UniqueNames),len(num_subs),len(num_cond),len(num_x)))
    for f in range(len(UniqueNames)):        # factors
        temp_data = DataFrameDict[UniqueNames[f]]
        for s in range(len(num_subs)):       # subjects
            s_data = temp_data[:][temp_data.subjects==num_subs[s]]
            for c in range(len(num_cond)):   # conditions
                c_data = s_data[:][temp_data.conditions==num_cond[c]]
                x_data = np.array(c_data[c_data.columns[1]]) 
                res    = func_fit(x0,bnds,xvals,x_data,False,fc)
                sub_fits[f,s,c,:] = func_run(xvals,x_data,res.x,True,fc)
                st_params[f,s,c,:]=res.x # store parameters
        
    # fit and plot the mean across conditions for show
    m_fit = []
    for factor in UniqueNames:
        plt.figure(); c = 0
        data_m = DataFrameDict[factor]
        for cond in num_cond:
            data_full = np.array(data_m.dprime[:][data_m.conditions==cond]).reshape(len(num_subs),len(num_x))
            cond_data = np.mean(data_full,axis=0)
            res = func_fit(x0,bnds,xvals,cond_data,False,fc)
            
            if flg=='log':
                nx = np.logspace(np.log10(xvals[0]),np.log10(xvals[-1]))
                fit = func_run(nx,cond_data,res.x,True,fc)
                plt.semilogx(xvals,cond_data,'o',color=RGB[c])
                plt.errorbar(xvals,cond_data,np.std(data_full,axis=0)/np.sqrt(len(num_subs)),fmt='none',color=RGB[c])
                plt.semilogx(nx,fit,'-',color=RGB[c],label=num_cond[c])
            else:
               nx = np.linspace(xvals[0],xvals[-1],30)
               fit = func_run(nx,cond_data,res.x,True,fc)
               plt.plot(xvals,cond_data,'o',color=RGB[c])
               plt.errorbar(xvals,cond_data,np.std(data_full,axis=0)/np.sqrt(len(num_subs)),fmt='none',color=RGB[c])
               plt.plot(nx,fit,'-',color=RGB[c],label=num_cond[c])
            plt.title('factor: '+str(factor))
            plt.xlabel(col_labels[0])
            if units=='dprime':
                plt.ylabel('d-prime')
            else:
                plt.ylabel('% correct')
            c+=1
            m_fit.append(fit)
        plt.legend()
        plt.ylim((min_y,max_y))
    plt.show() 

    return  [st_params, sub_fits,m_fit]


[subject_params, subject_fits, mean_fits] = fit_psy_func('sample_csv_data.csv','dprime')
