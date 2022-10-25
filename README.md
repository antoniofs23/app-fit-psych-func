 Fits individual data and plots mean psychometric functions with errorbars computed from SEM

    inputs:     file:    .csv file (named data.csv) including all performance data in specified units with column labels
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

                chance: what is chance performance in your task? if 2AFC then enter 50
                        defaults to zero if not specified

                color: specifiy a color per condition ranging from 0 to 1. Will be chosen 
                    pseudo-randomly (from 100 possible) if unspecified
    
    outputs:    a .csv for the individual observer fits and mean fits

    **no implementation exists for minimization via negative log likelihood as
    **that would require single trial data

    CREATED BY: Antonio Fernandez [Oct. 20, 2022]
    contact: antoniofs23@gmail.com



