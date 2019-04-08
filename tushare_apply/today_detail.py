import os
from datetime import datetime,timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts
import datetime
dt=datetime.datetime.now().strftime('%Y%m%d')    
symbol='300072'
symbol='300330'
symbol='600868'
symbol='002384'
symbol='002430'
symbol='002382'

# df1 = ts.get_today_ticks(symbol)
# df2 = ts.get_tick_data(symbol,date=dt)
# df3 = ts.get_hist_data(symbol)
df = ts.get_realtime_quotes(symbol) 
ts.set_token('7e30dd0a070cd4306193a5925ec5b3c250a694f08ea390d7cc3af2d6')
pro = ts.pro_api()
df = pro.fina_mainbz(ts_code='000627.SZ', period='20171231', type='P')
# df = pro.index_basic('sw')
# df = pro.cashflow(ts_code='600000.SH', start_date='20180101', end_date='20180730')
# df =ts.moneyflow_hsgt()
# ts.cashflow(symbol)
print df.describe()
# ts.get_k_data
# ts.get_hist_data
# ts.get_today_all
# print df1,df2
# df2.to_csv('%s.today.csv'%symbol,encoding ='gbk' )
# print df
# exit()

