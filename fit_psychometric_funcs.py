def fit_psy_func(filedir,units,stats)
'''
Fits individual data and plots mean fit with errorbars 

inputs: filedir: dir to .csv including all performance data in specified units with column labels
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
        stats: if "True" displays freq statistics for parameter values (i.e., ANOVA)
               if "False" does nothing


 CREATED BY: Antonio Fernandez [Oct. 20, 2022]
    contact: antoniofs23@gmail.com
   moreinfo: antoniofs23.github.io/web
'''

<<<<<<< HEAD
=======

>>>>>>> 4bc14ab3a62bd1a0addf1a6d53a1637ed35ec20b
import numpy as np
import matplotlib as plt
import pandas as pd
from scipy import stats

# if % correct check what chance is
if units=='accuracy'
    b = input('what is chance performance in your task?, i.e., if there are 2 response alternatives (yes/no) then enter 50, 4 alternatives? enter 25')

# test values
#xvals = [0,4,8,12,18,20]
#xvals = [2,7,13,24,46,85]

# remove 0s for checks
xvals = [num or 0.001 for num in xvals] 

# check if x-vals are linearly or logarithmically spaced
# compare to linear spacing
res_line = stats.linregress(xvals,np.linspace(xvals[0],xvals[-1],len(xvals)))
# compare to logarithmic spacing
res_log = stats.linregress(xvals,np.logspace(np.log10(xvals[0]),np.log10(xvals[-1]),len(xvals)))

# designated a flag for linear or log spacing
if res_line.rvalue > res_log.rvalue:
    spacing = 'linear'
else:
    spacing = 'log'


