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
print(datetime.datetime.now())

instance = 0
timeLimit = 3600

tic = time.time()
#fileName = 'M4_J05_I050_r3_inst1'
fileName = 'Case Study Sydney'

filePath_g = '../data_Urwolfen/%s - g.xlsx'%fileName
filePath_p = '../data_Urwolfen/%s - p.xlsx'%fileName
filePath_Y = '../data_Urwolfen/%s - Y.xlsx'%fileName

g_all = pd.read_excel(open(filePath_g, 'rb'), sheet_name='Tabelle2', header = None)
p_all = pd.read_excel(open(filePath_p, 'rb'), sheet_name='Tabelle2', header = None)
Y_all = pd.read_excel(open(filePath_Y, 'rb'), sheet_name='Tabelle2', header = 0)

Y_all.rename( columns={'Unnamed: 0':'J'}, inplace=True )
Y_all.rename( columns={'Unnamed: 1':'M'}, inplace=True )

M = list(Y_all['M'])
M = set(M)
M = list(M)
M.sort()
print('M =',M)
I = list(g_all[0])
print('len(I) =',len(I))
J = list(Y_all['J'])
J = set(J)
J = list(J)
J.sort()
print('len(J) =',len(J))

# =============================================================================
# # threshold of M for M4_J05_I050_r3
# low = {}
# up = {}
# low['m1'] = 0
# low['m2'] = 3000
# low['m3'] = 3500
# low['m4'] = 4000
# up['m1'] = 3000     
# up['m2'] = 3500     
# up['m3'] = 4000     
# up['m4'] = -1     
# print('low_M =',low)
# print('up_M =',up)
# =============================================================================

# threshold of M for M4_J05_I050_r3
low = {}
up = {}
low['1w'] = 0
low['4w'] = 10000
up['1w'] = 10000     
up['4w'] = -1     
print('low_M =',low)
print('up_M =',up)

g = {}
for i in I:
    [g[i]] = g_all.loc[g_all[0]==i,1]

Y_selected = Y_all.loc[Y_all['Level']==1]    
len_r = len(Y_selected)
print('r =',len_r)

toc = time.time()
print('time to read data before reading p =',toc-tic)
print(datetime.datetime.now())

p = {}
for i in I:
    for j in J:
        for m in M:
            p[i,j,m] = 0.0
            
p_all = p_all.reset_index()  # make sure indexes pair with number of rows
for index, row in p_all.iterrows():
    i = row[0]
    j = row[1]
    m = row[2]
    value_ijm = row[3]
    p[i,j,m] += value_ijm

toc = time.time()
print('time to read data =',toc-tic)
print(datetime.datetime.now())
                
Centroid = {}
Zero = {}
theNotSelected = []
for j in J:
    for m in M:
        Centroid[j,m] = 0.5
        Zero[j,m] = 0.0
        theNotSelected += [(j,m)]

print('####### Finish Pre-Process of Adaptive Randomized Rounding')
for iteration in range(16):        
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
            
            
            
            
            
        
