#read in the data
#each row is an offtaker
#calculate score relative to max and min of all offtakers
#then calculate total score
def calculate(baseprofit, basecarbon, basewater, basesocial, totalprofit, totalcarbon, totalwater, socialscore, rownum, variable):

    import matplotlib.pyplot as plt
    import math as math
    import numpy as np
    import cmath as cmath
    import pandas as pd
    import numpy_financial as nf
    

    inputdata = pd.read_excel("totals.xlsx") 
    inputdata_trimmed = inputdata.iloc[:, 1:].astype(float)
    inputdata_trimmed.loc[rownum-1] = [baseprofit, basecarbon, basewater, basesocial]
    
    inputdata2_trimmed = inputdata_trimmed.copy()
    inputdata2_trimmed.loc[rownum-1] = [totalprofit, totalcarbon, totalwater, socialscore]
    #print(inputdata2_trimmed.iloc[rownum-1])
    
    #scores = inputdata_trimmed
    Se = 0.25#weights
    Sc = 0.25
    Sw = 0.25
    Ss = 0.25
    
    
    
    scores = (inputdata_trimmed - inputdata_trimmed.min()) / (inputdata_trimmed.max() - inputdata_trimmed.min()) #score calculation
    
    totalscore = Se*scores.iloc[:, 0] + Sc*scores.iloc[:, 1] + Sw*scores.iloc[:, 2] + Ss*inputdata_trimmed.iloc[:, 3] #array with the new scores
    #order of the scores corresponds to the order of the offtakers in the excel input sheet
    
    #newscores = inputdata2_trimmed
    newscores = (inputdata2_trimmed - inputdata2_trimmed.min()) / (inputdata2_trimmed.max() - inputdata2_trimmed.min())
    newtotalscore = Se*newscores.iloc[:, 0] + Sc*newscores.iloc[:, 1] + Sw*newscores.iloc[:, 2] + Ss*inputdata2_trimmed.iloc[:, 3] #array with the new scores

    senstotal = (newtotalscore[rownum-1]-totalscore[rownum-1])/(0.01*variable/1.01)
    #senss = newtotalscore[rownum-1]-totalscore[rownum-1]
    uncertaintytotal = abs(senstotal * 0.1 * variable/1.01)
    sensecon1 = (newscores.iloc[:, 0]-scores.iloc[:, 0])/(0.01*variable/1.01)
    sensecon = sensecon1[rownum-1]
    senscarbon1 = (newscores.iloc[:, 1]-scores.iloc[:, 1])/(0.01*variable/1.01)
    senscarbon = senscarbon1[rownum-1]
    senswater1 = (newscores.iloc[:, 2]-scores.iloc[:, 2])/(0.01*variable/1.01)
    senswater = senswater1[rownum-1]
    senssocial1 = (inputdata2_trimmed.iloc[:, 3]-inputdata_trimmed.iloc[:, 3])/(0.01*variable/1.01)
    senssocial = senssocial1[rownum-1]
    uncertaintyecon = abs(sensecon * 0.1 * variable/1.01)
    uncertaintycarbon = abs(senscarbon * 0.1 * variable/1.01)
    uncertaintywater = abs(senswater * 0.1 * variable/1.01)
    uncertaintysocial = abs(senssocial * 0.1 * variable/1.01)
    
    
    
    #print(scores)
    #print(newscores)
    #print(inputdata_trimmed)
    #print(inputdata2_trimmed)
    
    #print(newtotalscore[rownum-1]-totalscore[rownum-1])
    #print(newtotalscore)
    #print(newtotalscore[2])
    #print(inputdata2_trimmed)
    #print(repr(senstotal))
    #print(newtotalscore)
    #print(totalscore)
    #print(newtotalscore-totalscore)
    #print(f"{senss:.20e}")

    return uncertaintytotal, uncertaintyecon, uncertaintycarbon, uncertaintywater, newtotalscore[rownum-1], newscores.iloc[rownum-1, :]
