Fits specified psychometric function to an individual subject's
trial-wise responses 
[error is minimized via negative-log-likelihood]
---  
**inputs:** 
1. file   <code>{**.csv**}</code>:  file containing trial-wise subject responses (should follow tidy-data format and has to be named <code>'**datafile.csv**'</code> 
    should have the following column labels <code>{*'xvals','trialsIdx','conditions','accuracy'*} </code> in no specific order where:
    <code>'trialsIdx'</code> is the trial indexes eg. 1...nTrials 
    <code>'conditions'</code>is a column with condition labels could be numerial or string or both 
    <code>'accuracy'</code> is the observer's correct (1) or incorrect (0) responses across trials                

|trialsIdx|xvals|conditions|accuracy|
| ------- | --- | -------- | ------ | 
|   1      |  0.05   |  valid        |   0.57      |  
|   2      |  0.2   |  neutral        |   0.77      |  
|   3      |  0.85   |  invalid        |   0.90      |  


2. chance  <code>{**float**}</code>:  what is chance performance in your task? example: if a detection task then there are 2 response alternatives (yes/no) so enter 0.5, if 4 response alternatives enter 0.25

3. plot  <code>{**bool**}</code>:  if True plots the fits / False = no plots 

***

**output:**
<code>output.npy</code> file in the <code>our_dir</code> containing:
1. % correct per condition
2. best fit functions per condition
3. best fit parameters
          

***


    CREATED BY: Antonio Fernandez (af) [Oct. 20, 2022] 
    last edited: Oct. 28, 2020 af
    