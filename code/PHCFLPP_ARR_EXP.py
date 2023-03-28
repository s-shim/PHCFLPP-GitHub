import socket
import pandas as pd
#from gurobipy import *
import copy
import datetime
import time
import random
from itertools import product
import myDictionary as md
import math

machineName = socket.gethostname()

fileName = 'M6_J15_I400_r8'
fileName1 = 'M6_J15_I400_r8 - Part 1 of 3'
fileName2 = 'M6_J15_I400_r8 - Part 2 of 3'
fileName3 = 'M6_J15_I400_r8 - Part 3 of 3'

# =============================================================================
# fileName = 'M6_J10_I400_r5'
# fileName1 = 'M6_J10_I400_r5 - Part 1 of 2'
# fileName2 = 'M6_J10_I400_r5 - Part 1 of 2'
# fileName3 = 'M6_J10_I400_r5 - Part 2 of 2'
# =============================================================================

# =============================================================================
# fileName = 'M4_J15_I400_r8'
# fileName1 = 'M4_J15_I400_r8 - Part 1 of 2'
# fileName2 = 'M4_J15_I400_r8 - Part 1 of 2'
# fileName3 = 'M4_J15_I400_r8 - Part 2 of 2'
# =============================================================================

# =============================================================================
# for fileName in ['M4_J05_I050_r3','M4_J10_I050_r5','M4_J15_I050_r8','M6_J05_I050_r3','M6_J10_I050_r5','M6_J15_I050_r8','M4_J05_I100_r3','M4_J10_I100_r5','M4_J15_I100_r8','M6_J05_I100_r3','M6_J10_I100_r5','M6_J15_I100_r8','M4_J05_I200_r3','M4_J10_I200_r5','M4_J15_I200_r8','M6_J05_I200_r3','M6_J10_I200_r5','M6_J15_I200_r8','M4_J05_I400_r3','M4_J10_I400_r5','M6_J05_I400_r3','M6_J10_I400_r5']:
#     fileName1 = fileName 
#     fileName2 = fileName 
#     fileName3 = fileName 
# =============================================================================

iterations = 1 # number of iterations
timeLimit = 60 # seconds

print()
print('###### Randomized Rounding %s'%fileName,datetime.datetime.now())
print('###### Start Reading Data')


filePath = '../data_Urwolfen/%s.xlsx'%fileName
filePath1 = '../data_Urwolfen/%s.xlsx'%fileName1
filePath2 = '../data_Urwolfen/%s.xlsx'%fileName2
filePath3 = '../data_Urwolfen/%s.xlsx'%fileName3

g_all = pd.read_excel(open(filePath1, 'rb'), sheet_name='g_all', header = 2)
p_all = pd.read_excel(open(filePath2, 'rb'), sheet_name='p_all', header = 2)
I = pd.read_excel(open(filePath1, 'rb'), sheet_name='I', header = 1)
I = I.drop([0])
I = list(I['I'])
J = pd.read_excel(open(filePath1, 'rb'), sheet_name='J', header = 1)
J = J.drop([0])
J = list(J['J'])
M = pd.read_excel(open(filePath1, 'rb'), sheet_name='M', header = 1)
M = M.drop([0])
M = list(M['M'])
mu = pd.read_excel(open(filePath1, 'rb'), sheet_name='mu', header = 2)
Scalar = pd.read_excel(open(filePath1, 'rb'), sheet_name='Scalar', header = 1)
[len_r] = Scalar.loc[Scalar['Parameter']=='r','Value']

print('###### Finish Reading Data')

for instance in [1]:#range(1,10+1):   
    print()
    print()     
    print('####### Instance =',instance,datetime.datetime.now())
    print('####### Start Pre-Process of Adaptive Randomized Rounding')
    ## extract instance
    ## extract instance
    g_instance = g_all.loc[g_all['instance']=='inst%s'%instance]
    g = {}
    for i in I:
        [g[i]] = g_instance.loc[g_instance['I']==i,'Value']
    
    p = {}
    p_instance = p_all.loc[p_all['instance']=='inst%s'%instance]
    for i in I:
        for j in J:
            for m in M:
                [p[i,j,m]] = p_instance.loc[(p_instance['I']==i)&(p_instance['J']==j)&(p_instance['Modes']==m),'Value']
    
    mode_names = []
    mode_low = []
    mode_up = []
    for m in M:
        mode_names += [m]
        if m not in list(mu['Modes']):
            mode_low += [0]
        else:
            [low] = mu.loc[mu['Modes']==m,'Value']
            mode_low += [low]
            mode_up += [low]
    mode_up += [-1]
    modeTable = pd.DataFrame(list(zip(mode_names,mode_low,mode_up)),columns =['Modes','Lower Bound','Upper Bound'])
    
    low = {}
    up = {}
    for m in M:
        [m_low] = modeTable.loc[modeTable['Modes']==m,'Lower Bound']
        [m_up] = modeTable.loc[modeTable['Modes']==m,'Upper Bound']
        low[m] = m_low
        up[m] = m_up    
                    
    Centroid = {}
    Zero = {}
    theNotSelected = []
    for j in J:
        for m in M:
            Centroid[j,m] = 0.5
            Zero[j,m] = 0.0
            theNotSelected += [(j,m)]

    print('####### Finish Pre-Process of Adaptive Randomized Rounding')
    for iteration in range(iterations):        
        print()
        print(datetime.datetime.now())
        print('####### File %s'%fileName)            
        print('####### Instance %s #######'%instance)    
        print('####### Iteration %s #######'%iteration)    
        print('####### Start Randomized Rounding for %s seconds #######'%timeLimit)    
        tic = time.time()
        Y = copy.deepcopy(Centroid)
        bestSelected = md.RR(Y,J,M,theNotSelected,len_r)
        #bestSelected = sorted(bestSelected)
        bestObj, feasibility = md.EvaluatorSingle(bestSelected,g,p,I,low,up)
        print(bestObj, feasibility, bestSelected)
        nLocal = 0
        
        # =============================================================================
        # print('####### Start %s trials of Randomized Rounding #######'%trials)
        # for trial in range(trials):
        # =============================================================================
        
        trial = 0
        toc = time.time()
    
        machineArray = [machineName]
        fileArray = [fileName]
        instanceArray = [instance]
        iterationArray = [iteration]
        trialArray = [trial]
        timeArray = [toc-tic]
        objectiveArray = [bestObj]
        intY = {}
        for j in J:
            for m in M:
                if (j,m) in bestSelected:
                    intY[j,m] = [1]
                else:
                    intY[j,m] = [0]
    
        summaryTable = pd.DataFrame(list(zip(machineArray,fileArray,instanceArray,iterationArray,trialArray,timeArray,objectiveArray)),columns =['Machine','File Name','Instance','Iteration','Trial','Time','Objective'])
        for j in J:
            for m in M:
                summaryTable['Y[%s,%s]'%(j,m)] = intY[j,m]
                
        summaryTable.to_csv(r'Summary_%s_Instance%s_Iteration%s.csv'%(fileName,instance,iteration), index = False)#Check
    
        while toc - tic < timeLimit:
            trial += 1
            #print(trial)
            
            theSelected = md.RR(Y,J,M,theNotSelected,len_r)
            #theSelected = sorted(theSelected)
            same = True
            for (j,m) in theSelected:
                if (j,m) not in bestSelected:
                    same = False
                    break
        
            RMSD = 0.0
            for j in J:
                for m in M:
                    RMSD = RMSD + (Y[j,m] - Centroid[j,m]) ** 2
            RMSD = RMSD / (len(J) * len(M))
            RMSD = math.sqrt(RMSD)
            
            #print(trial,RMSD)
            
            reset = False            
            if same == True:
                nLocal += 1
                if random.random() < min(1, nLocal / 20) * RMSD:
                    reset = True
                    nLocal = 0
            else:
                nLocal = 0
                objective, feasibility = md.EvaluatorSingle(theSelected,g,p,I,low,up)
                if bestObj < objective:
                    bestObj = objective
                    bestSelected = copy.deepcopy(theSelected)
                    print()
                    print('trial=',trial)            
                    print('bestObj=',bestObj)
                    toc = time.time()
                    print('time=',toc - tic)
                    
                    machineArray += [machineName]
                    fileArray += [fileName]
                    instanceArray += [instance]
                    iterationArray += [iteration]
                    trialArray += [trial]
                    timeArray += [toc-tic]
                    objectiveArray += [bestObj]
                    
                    for j in J:
                        for m in M:
                            if (j,m) in bestSelected:
                                intY[j,m] += [1]
                            else:
                                intY[j,m] += [0]
                
                    summaryTable = pd.DataFrame(list(zip(machineArray,fileArray,instanceArray,iterationArray,trialArray,timeArray,objectiveArray)),columns =['Machine','File Name','Instance','Iteration','Trial','Time','Objective'])
                    for j in J:
                        for m in M:
                            summaryTable['Y[%s,%s]'%(j,m)] = intY[j,m]
                            
                    summaryTable.to_csv(r'Summary_%s_Instance%s_Iteration%s.csv'%(fileName,instance,iteration), index = False)#Check
        
            if reset == True:
                Y = copy.deepcopy(Centroid)
            else:
                alpha = 1 / (1 + math.exp(4 * RMSD))
                for j in J:
                    for m in M:
                        Y[j,m] = (1 - alpha) * Y[j,m]
                        if (j,m) in bestSelected:
                            Y[j,m] = Y[j,m] + alpha
        
            toc = time.time()
        
        print()
        print('%s trials DONE'%trial)    
        print('Instance =',instance)
        print('Iteration =',iteration)
        print('time =',toc-tic)                    
        print('END OF ITERATION')
                
                
                
                
                
            
