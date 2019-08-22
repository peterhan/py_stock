import os
from datetime import datetime,timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tushare as ts
import seaborn as sns
import datetime


def real_time_tick(tick):
    fname = 'data/tick.%s.csv'%tick
    try:
        df = ts.get_today_ticks(tick)
        df.to_csv(fname,encoding='utf8')
    except:
        print 'Fail On URL'
        pass
    df=pd.read_csv(fname,encoding='utf8')
    print tick
    print df.groupby('type').agg({'volume':'sum','price':'mean','change':'count'})
    print df.corr()
    print df.describe()
    # df2 = ts.get_tick_data(tick,date=dt,src='tt')
    # df3 = ts.get_hist_data(tick)
    rdf = ts.get_realtime_quotes(tick) 
    # print rdf.melt()

def pro_api():
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
    
def test():
    df=pd.DataFrame(np.random.randn(10002,3),columns=['x','y','z'])
    sns.violinplot(y='y',data=df)
    plt.show()
    
def main():
    dt=datetime.datetime.now().strftime('%Y%m%d')    
    tick='300072'
    tick='300330'
    tick='600868'
    tick='002384'
    tick='002430'
    tick='002382'
    tick='518800'
    tick='600438'
    real_time_tick(tick)
    
    
if __name__ == '__main__':
    main()