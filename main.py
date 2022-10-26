def fit_psy_func(file,units,chance=0,color=False):
    '''
    Fits individual data and plots mean fit with errorbars (SEM) 

    inputs: file:    .csv file including all performance data in specified units with column labels
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
        **the code defaults to fitting a Weibull function
        **for simplicity cost function is defined as sum squared error**
        if units = 'dprime'
        **fits a nakarushton function

        chance: what is chance performance in your task? 
                if units are accuracy:
                chance is derived from response alternatives i.e., if your
                task has two-choices (yes/no) then chance is 50% so enter 0.5
                if four-choices then chance is 25%  enter 0.25
                if units are dprime enter 0 regardless of task

        color: specifiy a color per condition ranging from 0 to 1. Will be chosen 
            pseudo-randomly (from 100 possible) if input is [0]
            i.e. specify three colors one for each condition via:
            [[0.1,0.1,0.1],[0.2,0.2,0.2],[0.3,0.3,0.3]]
    
    **no implementation exists for minimization via negative log likelihood as
    **that would require single trial data

    CREATED BY: Antonio Fernandez [Oct. 20, 2022]
    contact: antoniofs23@gmail.com
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    #import seaborn as sns
    import pandas as pd
    from scipy import stats
    from scipy.optimize import minimize
    import fitting_funcs as ff

    # change plotting style to seaborn
    #sns.set_theme()
    
    # read csv file 
    data = pd.read_csv(file)
    col_labels = data.columns # extract column labels    
    xvals = np.unique(data[data.columns[0]]) # extract x-values from 1st col 
    
    # extract number of conditions/factors/subjects
    num_x    = np.unique(data[data.columns[0]])
    #all_y    = data[data.columns[1]]
    num_cond = np.unique(data[data.columns[2]])
    num_fac  = np.unique(data[data.columns[3]])
    num_subs = np.unique(data[data.columns[4]])
    
    #pcorr = ff.dprime2corr(all_y)
    #np.savetxt('pcorr.csv',pcorr,delimiter=',',fmt='%s')
    
    if units=='dprime':
        max_y    = np.max(data[data.columns[1]])
    else:
        max_y = 1
    min_y = chance 
    
    # check if user input colors
    if len(color)==3:
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
        fc = 'weibull'; flg = 'log'
        print('assuming logarithmic x-values')

    # if % correct check what chance is
    b = chance
    if units=='dprime':
         fc = 'nakarushton'
        
    
    def func_run(x,data,par,flag,fc):
        if fc=='nakarushton':
            fit = ff.nakarushton(x,data,par,flag)
        if fc=='weibull':
            fit = ff.weibull(x,data,par,flag)
        return fit
    
    def func_fit(x0,bnds,x,data,flag,fc):
        if fc == 'nakarushton':
            fun = lambda par: ff.nakarushton(x,data,par,flag)
        if fc == 'weibull':
            fun = lambda par: ff.weibull(x,data,par,flag)
        return  minimize(fun,x0,method='SLSQP',bounds=bnds)
    
    # relaxed bounds and starting points for parameter space
    if units=='accuracy':
        bnds = ((b,b),(0,1),(np.quantile(xvals,0.1),np.quantile(xvals,0.9)),(0,5)) # parameter lower and upper bounds
        x0 = (b,0.02,xvals[2],2) # starting point for parameters
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
            if units=='dprime':
                data_full = np.array(data_m.dprime[:][data_m.conditions==cond]).reshape(len(num_subs),len(num_x))
            else:
                data_full = np.array(data_m.accuracy[:][data_m.conditions==cond]).reshape(len(num_subs),len(num_x))
            cond_data = np.mean(data_full,axis=0)
            res = func_fit(x0,bnds,xvals,cond_data,False,fc)
            
            if flg=='log':
                nx = np.logspace(np.log10(xvals[0]),np.log10(xvals[-1]),30)
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
            plt.xticks(num_x,num_x)
            if units=='dprime':
                plt.ylabel('d-prime')
            else:
                plt.ylabel('% correct')
            c+=1
            m_fit.append(fit)
        plt.legend()
        plt.ylim((min_y,max_y))
    plt.show() 

    # save output parameters and fits
    

    return  [st_params, sub_fits,m_fit]


# test cases
#[subject_params, subject_fits, mean_fits] = fit_psy_func('sample_csv_data3.csv','accuracy',chance=0.25)
#[subject_params, subject_fits, mean_fits] = fit_psy_func('sample_csv_data.csv','dprime')
#[subject_params, subject_fits, mean_fits] = fit_psy_func('sample_csv_data2.csv','dprime')

import json

# load inputs from config.json
with open('config.json') as config_json:
    config = json.load(config_json)

[subject_params, subject_fits, mean_fits] = fit_psy_func(config['file'],config['units'],config['chance'],config['color'])