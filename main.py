def fit_psy_func(file,func,chance,plot):
    '''
    [UNDER CONSTRUCTION]
    
    Fits specified psychometric function to an individual subject's
    trial-wise responses and plots fit with bootstrapped errorbars
    error is minimized via negative-log-likelihood
    
    inputs: 
        file   {.csv}:  file containing trial-wise subject responses (should follow tidy-data format)
        
        func {string}:  function to fit [options]:
                        1) nakarushton
                        2) weibull
                        
      chance  {float}:  what is chance performance in your task? example: if a detection task
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
    import builder_funcs as ff

    # read csv file 
    data = pd.read_csv(file)
    
    # extract number of conditions/factors/subjects
    xvals    = np.unique(data['xvals'])
    num_cond = np.unique(data['conditions'])
    
    # generate an arbitrary number of colors (one per condition)
    # that are evenly distrubuted according to the golden ratio
    RGB=[]; RGB_list = np.random.permutation(100)
    for ii in range(0,len(num_cond)*3):
        id  = RGB_list[ii]
        phi = (1+np.sqrt(5))/2
        RGB.append(id*phi-np.floor(id*phi))
    RGB = list(np.array_split(RGB,3))
    
    # check if x-vals are linearly or logarithmically spaced
    # compare to linear spacing
    res_line = stats.linregress(xvals,np.linspace(xvals[0],xvals[-1],len(xvals)))
    # compare to logarithmic spacing
    res_log = stats.linregress(xvals,np.logspace(np.log10(xvals[0]),np.log10(xvals[-1]),len(xvals)))

    # designated a flag for linear or log spacing
    if res_line.rvalue > res_log.rvalue:
        flg = 'linear'
        print('assuming linear x-values')
    else:
        flg = 'log'
        print('assuming logarithmic x-values')
    
    # check lower bound on x-vals given by chance input
    b = chance
    
    # relaxed bounds and starting points for parameter space
    bnds = ((b,b),(0,1),(np.quantile(xvals,0.1),np.quantile(xvals,0.9)),(0,5)) # parameter lower and upper bounds
    x0 = (b,0.02,xvals[2],2) # starting point for parameters
    
    # compute % correct per x val and condition
    
        
       

    # save output parameters in .npy format to be easily readable by other python-based apps
    # subject parameters/fits
    with open('./out_dir/output.npy','wb') as f:
        np.save(f,st_params)
        np.save(f,sub_fits)
        np.save(f,m_fit) 
        
    return  

import json
#import numpy as np

# load inputs from config.json
with open('config.json') as config_json:
    config = json.load(config_json)

fit_psy_func(config['file'],config['func'],config['chance'],config['plot'])

# to open output file
#with open('output.npy', 'rb') as f:
#    st_params = np.load(f)
#    sub_fits= np.load(f)
#    m_fit = np.load(f)
    
