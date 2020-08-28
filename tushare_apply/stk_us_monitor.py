import pdb 
import pandas as pd
import keyring
from alpha_vantage.timeseries import TimeSeries
pd.set_option('display.max_columns',80)


ticker = 'BYND'
ticker = 'BA'
ticker = 'STWD'
ticker = 'AMD'
ticker = 'MSFT'
ticker = 'SHLL'


def get_ticker_df(ticker):
    API_KEY=str(keyring.get_password('av','u1'))
    # print type(API_KEY)
    ts =TimeSeries(key=API_KEY)
    data,meta_data  = ts.get_monthly_adjusted(ticker)
    # data,meta_data  = ts.get_daily_adjusted(ticker)
    # data,meta_data = ts.get_intraday(ticker)
    df = pd.DataFrame(data)
    # pdb.set_trace()
    df['name'] = df.index
    df['name']  = df['name'].apply(lambda x:x.split('.')[1].strip())
    df.index=df['name']
    df.pop('name')
    df = df.stack()
    df = pd.to_numeric(df)
    df = df.unstack(0)
    ndf =  pd.DataFrame()
    ndf['pivot']=(df['high']+df['low']+df['close']*2)/4
    ndf['r1']=  2*ndf['pivot']-df['low']
    ndf['s1']=  2*ndf['pivot']-df['high']
    ndf['r2']=  ndf['pivot']+ndf['r1']-ndf['s1']
    ndf['s2']=  ndf['pivot']-ndf['r1']+ndf['s1']
    ndf['r3']=  df['high']+2*(ndf['pivot']-df['low'])
    ndf['s3']=  df['low']-2*(df['high']-ndf['pivot'])
    print ndf.cov()
    print ndf.describe()
    print ndf
    return ndf
    
get_ticker_df(ticker)