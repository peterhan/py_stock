import pdb
import tushare as ts
import pandas as pd
import talib as talib
import datetime

#600438 13.397
#600585 42.562
tks='''002258,000001,000651,002027,002702
600183,600132,603501,002202,002466
002531,002572,159915,300014,300017
300129,300330,300618,300750,600004,600009
600025,600029,600201,600311
600438,600459,600519,600585
600887,601012,601021,601088
601111,601222,601636,601888
601985,603259,603605,600848
603816,000333,002008,603515
000089,000681,300012,300203
002382,601138,600854
002733,002338,300596'''.replace(',','\n').splitlines()

tks='512320'
tks='''510300,510500,510600,510630,510150,510150'''.replace(',','\n').splitlines()



pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)

def display_ticks_rt(tks):
    rdf=  ts.get_realtime_quotes(tks)
    # rdf=  ts.get_today_all()
    # print rdf
    rdf = rdf.apply(pd.to_numeric,errors='ignore')
    cname = rdf.columns
    # cname[3]='price'
    # rdf.rename(cname,inplace=True)
    rdf.insert(0,'pre_code',rdf['code'])
    rdf.insert(1,'bounce',(rdf['price']-rdf['low'])/(rdf['high']-rdf['low'])*100)
    rdf.insert(2,'osc',(rdf['high']-rdf['low'])/(rdf['open'])*100)
    rdf.insert(3,'gap',(rdf['open']-rdf['pre_close'])/(rdf['open'])*100)
    rdf.insert(4,'rate',(rdf['price']-rdf['pre_close'])/(rdf['pre_close'])*100)
    # rdf.insert(5,'rate2',(rdf['price']-rdf['open'])/(rdf['open'])*100)
    # rdf.insert(6,'rate3',(rdf['price']-rdf['open'])/(rdf['pre_close'])*100)


    print rdf.loc[:,:'amount'].sort_values(by='bounce',ascending=False)
    # pdb.set_trace()
    # fc=ts.forecast_data(2019,1)
    # print fc
    # ttdf = ts.get_today_ticks(tks[6])
    # print ttdf[ttdf.volume>=100].groupby(ttdf.type).count()
    # print ttdf[ttdf.volume>=100].groupby(ttdf.type).sum()
    
def special_stock(tk):
    tk='600438'
    # df = ts.get_k_data(tk)
    # df.to_csv(tk)
    df = pd.read_csv(tk)
    closed=df['close'].values
    
    upper,middle,lower=talib.BBANDS(closed,matype=talib.MA_Type.T3)
    print talib.MACD(closed)
    print upper[-1],middle[-1],lower[-1]
    # print df
    # df = ts.get_sina_dd(tk, date='2019-04-18',vol=500)
    # print df
    # df = ts.get_index()
    
    
if __name__ == '__main__':
    display_ticks_rt(tks)
    # special_stock(tks)