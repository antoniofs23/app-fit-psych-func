def fit_psy_func(file,chance,plot):
    '''    
    Fits specified psychometric function to an individual subject's
    trial-wise responses [error is minimized via negative-log-likelihood]
    
    inputs: 
        file   {.csv}:  file containing trial-wise subject responses (should follow tidy-data format)
                        
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
    from itertools import compress, count
    
    # read csv file 
    readdata= pd.read_csv(file)
    
    #pre-process the data and remove rows with zeros from the data frame [indexed by column labeled trialsIdx]
    data = readdata[readdata['trialsIdx']!=0]
    
    # extract number of conditions/xvals
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
    
    # relaxed bounds and starting points for parameter space
    bnds = ((chance,chance),(0,1),(np.quantile(xvals,0.1),np.quantile(xvals,0.9)),(0,5)) # parameter lower and upper bounds
    x0 = (chance,0.02,xvals[2],2) # starting point for parameters
    
    # compute % correct per x val and condition
    acc = np.zeros(shape=[len(xvals),len(num_cond)]) # n/m
    m = np.zeros(shape=[len(xvals),len(num_cond)]) # total # of trials
    n = np.zeros(shape=[len(xvals),len(num_cond)]) # correct # of trials

    for x in range(len(xvals)):
        n_data = data[:][data.xvals==xvals[x]]
        for c in range(len(num_cond)):
            c_data   = n_data[:][n_data.conditions==num_cond[c]]
            m[x,c]   = len(c_data)
            n[x,c]   = sum(c_data['accuracy']==1)
            acc[x,c] = n[x,c]/m[x,c]
    
    # fit the data
    sampling = 100 # smooth the the fitted curve
    if flg=='linear':
        new_xvals=np.linspace(xvals[0],xvals[-1],sampling)
    elif flg=='log':
        new_xvals=np.logspace(np.log10(xvals[0]),np.log10(xvals[-1]),sampling)
    
    # initialize var store
    st_par = np.zeros(shape=(4,len(num_cond)))
    st_fit = np.zeros(shape=(sampling,len(num_cond)))
    # fit
    for c in range(len(num_cond)):
        temp_data = acc[:,c]
        res = ff.func_fit(x0,bnds,xvals,m[:,c],n[:,c],False,fc='weibull')
        st_fit[:,c] = ff.func_run(new_xvals,res.x,True,fc='weibull')
        st_par[:,c] = res.x # store best fit parameters
        
        #plot the data and fits
        if plot:
            if flg=='linear':
                plt.plot(xvals,temp_data,'.',color=RGB[c])
                plt.plot(new_xvals,st_fit[:,c],'-',color=RGB[c],label=num_cond[c])
            if flg=='log':
                plt.semilogx(xvals,temp_data,'o',color=RGB[c])
                plt.semilogx(new_xvals,st_fit[:,c],'-',color=RGB[c],label=num_cond[c])
    plt.ylabel('accuracy (% correct)')
    plt.legend()
    plt.show()
                
    #save output parameters in .npy format to be easily readable by other python-based apps
    # subject parameters/fits
    with open('./out_dir/output.npy','wb') as f:
        np.save(f,acc)
        np.save(f,st_fit)
        np.save(f,st_par) 
        
    return  

import json
#import numpy as np

# load inputs from config.json
with open('config.json') as config_json:
    config = json.load(config_json)

fit_psy_func(config['file'],config['chance'],config['plot'])

# to open output file
#with open('output.npy', 'rb') as f:
#    st_params = np.load(f)
#    sub_fits= np.load(f)
#    m_fit = np.load(f)
    
