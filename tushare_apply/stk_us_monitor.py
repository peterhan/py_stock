import pdb 
import pandas as pd
import keyring
from alpha_vantage.timeseries import TimeSeries
API_KEY=str(keyring.get_password('av','u1'))
# print type(API_KEY)
ts =TimeSeries(key=API_KEY)
ticker = 'STWD'
# data,meta_data = ts.get_intraday(ticker)
# data,meta_data  = ts.get_monthly_adjusted(ticker)
data,meta_data  = ts.get_daily_adjusted(ticker)
df =pd.DataFrame(data)
df = df.stack()
df = df.unstack(0)

pdb.set_trace()
