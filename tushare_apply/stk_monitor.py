import pdb
import tushare as ts
import pandas as pd
import talib as talib
import datetime


def to_list(self):
    return self.strip().replace(',','\n').replace(' ','\n').splitlines()

#600438 13.397
#600585 42.562
tks={}
tks[0]='''
000001 000089 000333 000651 000681 
002008 002027 002202 002258 002338 
002382 002466 002531 002572 002702 
002733
'''
tks[1]='''159915 399001 sh000001 399006 sh000300'''
tks[2]='''
300012 300014 300017 300129 300203 
300330 300596 300616 300618 300750
'''
tks[3]='''
600004 600009 600025 600029 600131 6001132  
600183 600201 600311 600438 600459 
600519 600585 600848 600854 600887 
601012 601021 601601 600298 601088 601111 601138 
601222 601636 601888 601985 603259 
603501 603515 603605 603816
'''
tks[4]='''510300 510500 510600 510630 510150 '''
tks[5]='''002099 600585 600438 600854 601601 600132'''




pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)

def rt_ticks(tks):
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
    
def load_ta_map():
    import json
    return json.load(open('talib_pattern_name.json'))
 
tam = load_ta_map()
 
def focus_tick(tk):    
    fname=tk+'.csv'
    df = ts.get_k_data(tk)
    df.to_csv(fname)
    df = pd.read_csv(fname)
    closed=df['close'].values
    
    upper,middle,lower=talib.BBANDS(closed,matype=talib.MA_Type.T3)
    # print talib.MACD(closed)
    print 'BOLL %s,%0.2f,%0.2f,%0.2f'%(tk,upper[-1],middle[-1],lower[-1])
    cnames = []
    for funcname in talib.get_function_groups()[ 'Pattern Recognition']:
        func = getattr(talib,funcname) 
        res_vlu = func(df['open'],df['high'],df['low'],df['close'])
        cname = funcname[3:]        
        df[cname]=res_vlu
        cnames.append(cname)
    df['IND_SUM']=df[cnames].sum(axis=1)
    # print df.iloc[-1]
    print df.iloc[-1,-1]
    df.to_csv(fname)
    # for i,row in df.iterrows():
        # print i#,row
    # df = ts.get_sina_dd(tk, date='2019-04-18',vol=500)
    # print df
    # df = ts.get_index()
    
    
if __name__ == '__main__':
    tks=to_list(tks[5])
    rt_ticks(tks)
    
    for tk in tks:
        focus_tick(tk)
        # break