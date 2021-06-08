#!coding:utf8
import pdb 
import pandas as pd
import json
import traceback
import datetime,time
from collections import OrderedDict
import ConfigParser
import sys
import re
import math
import keyring

from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
from stock_api import StockNewsFUTUNN
from stock_api import StockNewsFinViz


from stock_emd import emd_plot
from matplotlib import pyplot as plt
from stk_util import time_count,cli_select_menu,get_article_detail
import talib
from tech_analyse import tech_analyse,extract_candle_tech_summary,candle_analyse,analyse_res_to_str,catboost_process
from yfinance_cache import yfinance_cache

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format

try:    
    import gevent
    from gevent import monkey
    from gevent.pool import Pool    
    monkey.patch_all()
    # print '[gevent ok]'
except:
    print '[Not Found gevent]'

def get_ticker_df_alpha_vantage(ticker,mode='day'):
    API_KEY=str(keyring.get_password('av','u1'))
    # print type(API_KEY)
    ts =TimeSeries(key=API_KEY)
    if mode == 'month':
        data,meta_data  = ts.get_monthly_adjusted(ticker)
    elif mode == 'day':
        data,meta_data  = ts.get_daily_adjusted(ticker)
    elif mode == 'intraday':
        data,meta_data = ts.get_intraday(ticker)
    df = pd.DataFrame(data)
    # pdb.set_trace()
    df['name'] = df.index
    df['name']  = df['name'].apply(lambda x:x.split('.')[1].strip())
    df.index=df['name']
    df.pop('name')
    df = df.stack()
    df = pd.to_numeric(df)
    df = df.unstack(0)

    # print ndf.cov()
    # print ndf.describe()
    # print ndf
    return df
    
# @time_count
def add_analyse_columns(df):
    ndf =  df
    ndf['pivot']= (df['high']+df['low']+df['close']*2)/4
    ndf['r1']=  2*ndf['pivot']-df['low']
    ndf['s1']=  2*ndf['pivot']-df['high']
    ndf['r2']=  ndf['pivot']+ndf['r1']-ndf['s1']
    ndf['s2']=  ndf['pivot']-ndf['r1']+ndf['s1']
    ndf['r3']=  df['high']+2*(ndf['pivot']-df['low'])
    ndf['s3']=  df['low']-2*(df['high']-ndf['pivot'])
    for i in [10,20,30,60,120,240] :        
        ndf['sma%s'%i] = talib.SMA(df['close'],i)
        ndf['ema%s'%i] = talib.EMA(df['close'],i)    
    ndf['pchange'] = df['close'].pct_change()*100
    ndf['vchange'] = df['volume'].pct_change()*100
    if 'date' not in df.columns:
        ndf['date']=df.index
        ndf['date']=pd.to_datetime(ndf['date']).apply(lambda x:x.strftime('%Y-%m-%d'))
    return ndf
    
    
def stock_map():
    "https://finviz.com/js/maps/sec_788.js?rev=226"
    "https://finviz.com/api/map_perf.ashx?t=sec"
    return 
  
_ftnn = StockNewsFUTUNN()
@time_count
def get_stock_kline(tick,flags,api_route='futu'):    
    start = (datetime.datetime.now()-datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    # if tick.split('.')[0].isdigit() or '=' in tick or '^' in tick:
        # api_route = 'yfinance'
    for type in ['futu','yfinance','vantage']:
        if type in flags:
            api_route = type
    cyc = 'day'
    if 'month' in flags:
        cyc='month'
    if 'day' in flags:
        cyc='day'
    if 'week' in flags:
        cyc='week'
    if 'intraday' in flags:
        cyc='intraday'
    print 'api_route:',api_route,cyc
    if api_route == 'vantage':
        if '.' or '-' in tick:
            tick = tick.replace('-','.').split('.')[0]        
        his_df = get_ticker_df_alpha_vantage(tick,cyc)
    elif api_route=='yfinance':         
        his_df = yf.Ticker(tick).history(start=start)
        his_df = his_df.rename(columns={'Date':'date','Open':'open','High':'high'
        ,'Low':'low','Close':'close','Volume':'volume'
        ,'Dividends':'dividends','Stock Splits':'splits'})        
    elif api_route=='futu':
        if cyc=='intraday':
            cyc='15min'
        his_df = _ftnn.get_kline(tick, cyc)     
    return his_df
 
@time_count 
def get_one_tick_data(tick,stk_infos,flags,api_route = 'futu'):
    
    his_df = get_stock_kline(tick,flags,api_route) 
    his_df = his_df[-365:]
    
    if 'pdb' in flags:
        pdb.set_trace()
    ### 
    try:
        ndf = add_analyse_columns(his_df)
    except:
        traceback.print_exc()
        ndf = his_df
    ndf['code']=tick   
    
    df = ndf
    df['vol']= pd.to_numeric(df['volume'])
    
    res_info = {'code':tick, 'info':stk_infos.get(tick,{}), 'df':df}
    res_info['info'].update({'price':df['close'].values[-1],'name':''})
    # pdb.set_trace()
    if 'detail' in flags or 'catboost' in flags:
        tdf = tech_analyse(df)
        cdf = candle_analyse(df)
        df = pd.concat([df,tdf,cdf],axis=1)        
        cinfo,tinfo = extract_candle_tech_summary(df.iloc[-1]) 
        res_info['info'].update({'price':df['close'].values[-1],'name':''})
        res_info.update({'tech':tinfo,'cdl':cinfo})
    if 'catboost' in flags:
        df,factor_results,pstr = catboost_process(tick,df)
        res_info['algo_cb'] = pstr
    if 'option_chain' in flags:
        res_info['option_chain'] = ytk.option_chain()
        
    return res_info

        
def us_main_loop(mode):
    # fname = 'stk_console.v01.json'
    # conf_ticks = json.load(open(fname), object_pairs_hook=OrderedDict)
    # conf_ticks = conf_ticks['us-ticks']
    fname = 'stk_console.v01.ini'
    conf  = ConfigParser.ConfigParser()
    conf.readfp(open(fname))
    conf_tks  = OrderedDict(conf.items('us-ticks'))
    
    all = ' '.join( conf_tks.values())
    # pdb.set_trace()    
    all = all.replace('  ',' ')
    
    conf_tks['all'] = all
    opt_map = {
        'q':'quit','d':'detail','i':'pdb'
        ,'s':'onestock','n':'news','r':'realtime'
        ,'f':'fullname','a':'alpha_vantage','y':"yfinance",'f':'futu','vt':"vantage"
        ,'g':"graph",'ia':'intraday','id':'day','iw':'week','im':'month','u':'us','z':'zh'
        ,'e':'emd','ve':'vemd','c':'catboost','o':'option_chain','ft':'futures','fe':'futures_etc'
    }
    menu_dict = conf_tks
    groups,flags = cli_select_menu(menu_dict,default_input= None,\
        column_width=15,menu_columns=7,control_flag_map=opt_map) 
    s_ticks = []
    for group in groups:
        s_ticks.extend(conf_tks.get(group,group).replace('`','').replace('  ',' ').split(' ')) 
    s_ticks = filter(lambda x:len(x)>0,s_ticks)
    print 'ticks:',s_ticks,'flags:',flags
    if 'quit' in flags:
        sys.exit()
    if 'graph' in flags:
        fig, ax = plt.subplots(nrows=2, ncols=2*len(s_ticks), sharex=False)
    ### get infos
    stk_infos = yfinance_cache(s_ticks)
    # yinfos = {}
    
    ### get data
    if not Pool:
        for tk in s_ticks:
            results = get_one_tick_data(tk,stk_infos,flags)
    else:
        pool = Pool(8)
        jobs = []
        for tk in s_ticks:
            job = pool.spawn(get_one_tick_data,tk,stk_infos,flags)
            jobs.append(job)
        pool.join()
        results = [job.value for job in jobs]
      
    # pdb.set_trace()
    tail_n_res =  {}
    tail_n = 5
    for i,result in enumerate(results):
        if result is None:
            continue
        ndf = result['df']
        info = result['info']
        tick = result['code']        
        if 'detail' in flags:
            print analyse_res_to_str([result])
        if 'shortName' in info:
            shortname = info.get('shortName','').replace(', ','')
            sector = info.get('sector','')
        else:
            info = _ftnn.get_cache_company_info(tick)
            # pdb.set_trace()
            shortname = info['stockInfo']['name'].split(' ')[0]
            sector = info['stockInfo']['stock_market']
        pinfo = '[%s],[%s]'%(shortname ,sector )
        tail_n_res[tick+pinfo]= ndf[['close','volume','pchange','vchange']].tail(tail_n)
        print ''
        if 'graph' in flags:
            ndf[['close','sma10','ema10' ,'sma30','ema30']].plot(title=tick,ax= ax[0,0+i*2])
            ndf[['volume']].plot(title=tick,ax = ax[0,1+i*2])
            try:
                ndf = get_ticker_df_alpha_vantage(tick,'intraday')
                add_analyse_columns(ndf)
                ndf[['close','sma10','ema10' ,'sma30','ema30']].plot(title=tick,ax= ax[1,0+i*2])
                ndf[['volume']].plot(title=tick,ax = ax[1,1+i*2])
            except:
                pass
        if 'emd' in flags:                        
            emd_plot(ndf['close'])
        if 'vemd' in flags:
            emd_plot(ndf['volume'])
        if 'pdb' in flags:
            pdb.set_trace()
        if  'option_chain' in flags:
           print json.dumps(result['option_chain']  ,indent=2)
    if len(tail_n_res)>0:
        print pd.concat(tail_n_res,axis=0)
    if 'futures' in flags or 'futures_etc' in flags:
        fv = StockNewsFinViz()
        if 'futures_etc' in flags:        
            idic = fv.get_etc_brief(timeframe='d1')
        else:
            idic = fv.get_futures_brief(timeframe='d1')
        for key,df in idic.items():
            print '\n[%s]'%key
            print df.iloc[:,0:6]
    if 'news' in flags:
        df= _ftnn.get_news()
        df.index=pd.RangeIndex(df.shape[0])
        idxs,nflags = cli_select_menu(df['content'], menu_columns=1)
        for rowid in idxs:
            url = df.iloc[rowid]['detail_url']
            texts,tags = get_article_detail(url,'div','#content')
            print texts
    if 'graph' in flags:
        plt.show()    
    return flags

    
if __name__ == '__main__':
    pd.set_option('display.max_columns',80)
    while 1:
        try:
            us_main_loop('')
        except Exception as e:
            traceback.print_exc()
            
        
    
   
