def fit_psy_func(file,func,chance,plot):
    '''
    [UNDER CONSTRUCTION]
    
    Fits specified psychometric function to an individual subject's
    trial-wise responses and plots fit with bootstrapped errorbars
    
    inputs: 
        file   {.csv}:  file containing trial-wise subject responses
        func {string}:  function to fit [options]:
                        1) nakarushton
                        2) weibull
      chance  {float}:  what is chance performance in your task? example if a detection task
                        then there are 2 response alternatives (yes/no) so enter 0.5, 
                        if 4 response alternatives enter 0.25
         plot  {bool}:  if True plots the fits / False = no plots 
    output:
        output.npy file in the our_dir containing:
        1) % correct per condition
        2) best fit functions per condition
        3) best fit parameters
          
    CREATED BY: Antonio Fernandez (af) [Oct. 20, 2022]
    last edited: Oct. 27, 2020 af
    contact: antoniofs23@gmail.com
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from scipy import stats
    from scipy.optimize import minimize
    import fitting_funcs as ff

    # read csv file 
    data = pd.read_csv(file)
    col_labels = data.columns # extract column labels    
    xvals = np.unique(data[data.columns[0]]) # extract x-values from 1st col 
    
    # extract number of conditions/factors/subjects
    num_x    = np.unique(data[data.columns[0]])
    num_cond = np.unique(data[data.columns[2]])
    
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

    # check lower bound on x-vals given by chance input
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
    #plt.show() 

    # save output parameters in .npy format to be easily readable by other python-based apps
    # subject parameters/fits
    with open('./out_dir/output.npy','wb') as f:
        np.save(f,st_params)
        np.save(f,sub_fits)
        np.save(f,m_fit) 
        
    return  

# test cases
#[subject_params, subject_fits, mean_fits] = fit_psy_func('sample_csv_data3.csv','accuracy',chance=0.25)
#[subject_params, subject_fits, mean_fits] = fit_psy_func('sample_csv_data.csv','dprime')
#[subject_params, subject_fits, mean_fits] = fit_psy_func('sample_csv_data2.csv','dprime')

import json
#import numpy as np

# load inputs from config.json
with open('config.json') as config_json:
    config = json.load(config_json)

fit_psy_func(config['file'],config['units'],config['chance'],config['color'])

# to open output file
#with open('output.npy', 'rb') as f:
#    st_params = np.load(f)
#    sub_fits= np.load(f)
#    m_fit = np.load(f)
    
