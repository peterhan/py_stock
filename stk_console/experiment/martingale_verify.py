import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def matgel(v,b):
    if v<=0.5:
        return 0
    else:
        return 2*b
        
rnd=np.random.rand(500)
iswin =  rnd>1

def pos_martingale(rnd):
    b=8
    n=0
    sum=1000
    df= pd.DataFrame(columns=['account','bet'])

    for i in rnd:
        sum-=b
        res = matgel(i,b)
        sum+=res
        if res==0 and b<sum:
            b=2*b
        else:
            b=8
        # print sum,res,b
        df.loc[n] = [sum,b]
        n+=1
    print df
    plt.plot(df['account'])
    plt.plot(df['bet'])
    plt.show()
    
def neg_martingale(rnd):
    b=8
    n=0
    sum=1000
    df= pd.DataFrame(columns=['account','bet'])

    for i in rnd:
        sum-=b
        res = matgel(i,b)
        sum+=res
        if res!=0 and b<sum:
            b=2*b
        else:
            b=8
        # print sum,res,b
        df.loc[n] = [sum,b]
        n+=1
    print df
    plt.plot(df['account'])
    plt.plot(df['bet'])
    plt.show()
    
pos_martingale(rnd)
neg_martingale(rnd)