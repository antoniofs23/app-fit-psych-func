Fits specified psychometric function to an individual subject's
trial-wise responses [error is minimized via negative-log-likelihood]
    
**inputs:** 
1. file   {.csv}:  file containing trial-wise subject responses (should follow tidy-data format)
                        
2. chance  {float}:  what is chance performance in your task? example: if a detection task then there are 2 response alternatives (yes/no) so enter 0.5, if 4 response alternatives enter 0.25
                        
3. plot  {bool}:  if True plots the fits / False = no plots 
    
**output:**
output.npy file in the our_dir containing:
1. % correct per condition
2. best fit functions per condition
3. best fit parameters
          
    CREATED BY: Antonio Fernandez (af) [Oct. 20, 2022]
    
    last edited: Oct. 27, 2020 af
    
    contact: antoniofs23@gmail.com