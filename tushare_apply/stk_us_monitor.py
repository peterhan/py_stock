#!coding:utf8
import pdb 
import pandas as pd
import json
import traceback
import datetime,time
from collections import OrderedDict
import sys
import keyring
from alpha_vantage.timeseries import TimeSeries
from matplotlib import pyplot as plt
import yfinance as yf
from stk_monitor import cli_select_menu
import talib
from tech_analyse import tech_analyse,candle_analyse,analyse_res_to_str,cat_boost_factor_check
from yfinance_cache import yfinance_cache

try:    
    import gevent
    from gevent import monkey
    from gevent.pool import Pool    
    monkey.patch_all()
    # print '[gevent ok]'
except:
    print '[Not Found gevent]'

pd.set_option('display.max_columns',80)

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
    return ndf
    
    
def stock_map():
    "https://finviz.com/js/maps/sec_788.js?rev=226"
    "https://finviz.com/api/map_perf.ashx?t=sec"
    return 
    
    
def get_one_tick_data(tick,infos,flags):
    yfinance = True
    start = (datetime.datetime.now()-datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    if tick.split('.')[0].isdigit() or '=' in tick or '^' in tick:
        yfinance = True
    if 'vantage' in flags:
        yfinance = False
    if not yfinance:
        mode = 'day'
        if 'month' in flags:
            mode='month'
        if 'day' in flags:
            mode='day'
        if 'intraday' in flags:
            mode='intraday'
        his_df = get_ticker_df_alpha_vantage(tick,mode)
    else:
        ytk = yf.Ticker(tick)            
        his_df = ytk.history(start=start)
        his_df = his_df.rename(columns={'Date':'date','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume','Dividends':'dividends' , 'Stock Splits':'splits'})
    if 'pdb' in flags:            
        pdb.set_trace()    
    ndf = add_analyse_columns(his_df)
    ndf['code']=tick
    
    
    df = ndf
    df['vol']= pd.to_numeric(df['volume'])
    df['date']  = df.index
    tinfo,tdf = tech_analyse(df)
    cinfo,cdf = candle_analyse(df)
    df = pd.concat([df,tdf,cdf],axis=1)
        
    res_info = {'code':tick,'info':infos.get(tick,{}),'tech':tinfo,'cdl':cinfo,'df':df}
    res_info['info'].update({'price':df['close'].values[-1],'name':''})    
    if 'cat' in flags:
        cat_boost_factor_check(ndf)     
    return res_info

        
def us_main_loop(mode):
    fname = 'stk_monitor.v01.json'
    conf_ticks = json.load(open(fname), object_pairs_hook=OrderedDict)
    conf_ticks = conf_ticks['us-ticks']
    # pdb.set_trace()
    all = reduce(lambda x,y:x+' '+y, conf_ticks.values())
    all = all.replace('  ',' ')
    
    conf_ticks['all'] = all
    opt_map = {
        'q':'quit','d':'detail','i':'pdb'
        ,'s':'onestock','n':'news','r':'realtime'
        ,'f':'fullname','a':'alpha_vantage','y':"yfinance",'vt':"vantage"
        ,'g':"graph",'ia':'intraday','id':'day','im':'month','u':'us','z':'zh'
        ,'e':'emd','c':'cat'
    }
    menu_dict = conf_ticks
    groups,flags = cli_select_menu(menu_dict,default_input= None,column_width=15,menu_width=7,opt_map=opt_map) 
    s_ticks = []
    for group in groups:
        s_ticks.extend(conf_ticks.get(group,group).split(' '))
    print 'ticks:',s_ticks,'flags:',flags
    if 'quit' in flags:
        sys.exit()
    if 'graph' in flags:
        fig, ax = plt.subplots(nrows=2, ncols=2*len(s_ticks), sharex=False)
    ### get infos
    yinfos = yfinance_cache(s_ticks)
    
    ### get data
    if not Pool:
        for tk in s_ticks:
            results = get_one_tick_data(tk,yinfos,flags)
    else:
        pool = Pool(8)
        jobs = []
        for tk in s_ticks:
            job = pool.spawn(get_one_tick_data,tk,yinfos,flags)
            jobs.append(job)
        pool.join()
        results = [job.value for job in jobs]
      
    # pdb.set_trace()
    for i,result in enumerate(results):
        ndf = result['df']
        info = result['info']
        print '#'*50
        if 'detail' in flags:
            print analyse_res_to_str([result])
        print ndf[['code','close','volume','pchange','vchange']].tail(3)
        print '[%s],[%s],[%s],[%s]'%( tk,info.get('shortName',''),info.get('sector',''),info.get('market','') )
        print ''
        if 'graph' in flags:
            ndf[['close','sma10','ema10' ,'sma30','ema30']].plot(title=tk,ax= ax[0,0+i*2])
            ndf[['volume']].plot(title=tk,ax = ax[0,1+i*2])
            try:
                ndf = get_ticker_df_alpha_vantage(tk,'intraday')
                add_analyse_columns(ndf)
                ndf[['close','sma10','ema10' ,'sma30','ema30']].plot(title=tk,ax= ax[1,0+i*2])
                ndf[['volume']].plot(title=tk,ax = ax[1,1+i*2])
            except:
                pass
        if 'emd' in flags:
            from stock_emd import emd_plot
            emd_plot(ndf['close'])
        if 'pdb' in flags:
            pdb.set_trace()
        if  'detail' in flags:
            ytk = yf.Ticker(tk)
            info = ytk.info
            opt = ytk.option_chain()
            print json.dumps(info ,indent=2)
            print opt
        else:
            info = {}
            opt = {}
    
    
    if 'graph' in flags:
        plt.show()    
    return flags

    
if __name__ == '__main__':
    while 1:        
        try:
            us_main_loop('')
        except Exception as e:
            traceback.print_exc()
            
        
    
   
