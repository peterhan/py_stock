from collections import Counter

import tushare as ts
import pandas as pd
import numpy as np
import os
import pdb
import statsmodels.formula.api as sm
from IPython import embed
tks='510600'
fname = tks+'.csv'
if not os.path.exists(fname):
    df = ts.get_hist_data(tks)
    df.to_csv(fname)
df = pd.read_csv(fname)
df['date']=pd.to_datetime(df['date'])
df['weekday'] = df['date'].apply(lambda x:x.dayofweek)
df['week'] = df['date'].apply(lambda x:x.week)
print(df.columns)
ols_result = df.query('p_change>0')\
.assign(ln_h = lambda df:np.log(df.p_change))\
.pipe((sm.ols,'data'),'volume ~ ln_h')\
.fit()\
.summary()
print(ols_result)
embed()
print df.groupby('weekday').sum()
for i,row in df.iterrows():
    print row['date']    
    dt=row['date']
    weekday = dt.dayofweek
    # pdb.set_trace()
    if i>3:
        break