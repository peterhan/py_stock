from collections import Counter

import tushare as ts
import pandas as pd
import numpy as np
import os
import pdb
import statsmodels.formula.api as sm
from IPython import embed

def prep_df(tks):
    fname = tks+'.csv'
    if not os.path.exists(fname):
        df = ts.get_hist_data(tks)
        df.to_csv(fname)
    df = pd.read_csv(fname)
    df['date']=pd.to_datetime(df['date'])
    df['weekday'] = df['date'].apply(lambda x:x.dayofweek)
    df['week'] = df['date'].apply(lambda x:x.week)
    df['month'] = df['date'].apply(lambda x:x.month)
    df['year'] = df['date'].apply(lambda x:x.year)
    df['p_raise'] = df['p_change']>=0
    print(df.columns)
    return df
    
def analyze_ols(df):
    ols_result = df.query('p_change>0')\
    .assign(ln_h = lambda df:np.log(df.p_change))\
    .pipe((sm.ols,'data'),'volume ~ ln_h')\
    .fit()\
    .summary()
    print(ols_result)
    #embed()
    # print df.groupby(['weekday','p_raise'])['volume'].sum()
    # print df.groupby(['year','month','p_raise'])['volume'].agg([('volume_avg',np.mean),('count','count'),('std','std'),('max','max'),('min','min')])
    print df.groupby(['year','month','p_raise'])['p_change'].agg([('p_change_avg',np.mean),('count','count'),('std','std'),('max','max'),('min','min')])
    # print df.groupby(['weekday','p_raise'])['volume'].count()
    for i,row in df.iterrows():
        # print row['date']    
        dt=row['date']
        weekday = dt.dayofweek
        # pdb.set_trace()
        if i>3:
            break
            
if __name__ == '__main__':
    # tks='510600'
    tks='000001'
    # tks='600438'
    # tks='601012'
    df = prep_df(tks)
    analyze_ols(df)