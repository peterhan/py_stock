import pdb 
import pandas as pd
import json
import traceback
from collections import OrderedDict
import keyring
from alpha_vantage.timeseries import TimeSeries
from matplotlib import pyplot as plt
import yfinance as yf
from stk_monitor import cli_select_keys

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
    
def get_pivot(df):
    ndf =  pd.DataFrame()
    ndf['pivot']=(df['high']+df['low']+df['close']*2)/4
    ndf['r1']=  2*ndf['pivot']-df['low']
    ndf['s1']=  2*ndf['pivot']-df['high']
    ndf['r2']=  ndf['pivot']+ndf['r1']-ndf['s1']
    ndf['s2']=  ndf['pivot']-ndf['r1']+ndf['s1']
    ndf['r3']=  df['high']+2*(ndf['pivot']-df['low'])
    ndf['s3']=  df['low']-2*(df['high']-ndf['pivot'])
    return ndf
    

def choose_ticks(mode):
    fname = 'stk_monitor.json'
    conf_tks = json.load(open(fname), object_pairs_hook=OrderedDict)
    conf_tks = conf_tks['yf_tks']
    opt_map = {'q':'quit','d':'detail','i':'pdb','s':'onestock','n':'news','r':'realtime'
        ,'f':'fullname','a':'alpha_vantage','y':"yf",'g':"graph"
        ,'ia':'intraday','id':'day','im':'month'}
    menu_dict = OrderedDict(zip(map(lambda x:x.upper(),conf_tks),conf_tks))
    ticks,flags = cli_select_keys(menu_dict,default_input= None,column_width=15,menu_width=7,opt_map=opt_map) 
    print ticks,flags
    for tk in ticks:
        ytk = yf.Ticker(tk)
        if 'yf' not in flags:
            mode = 'day'
            if 'month' in flags:
                mode='month'
            if 'day' in flags:
                mode='day'
            if 'intraday' in flags:
                mode='intraday'
            his_df = get_ticker_df_alpha_vantage(tk,mode)
        else:
            his_df = ytk.history()
        ndf = get_pivot(his_df)
        print his_df
        if 'graph' in flags:
            his_df[['close','open','high','low']].plot(figsize=(8,3))
            plt.show()
        if 'pdb' in flags:
            pdb.set_trace()
        
        if  'detail' in flags:
            info = ytk.info
            opt = ytk.option_chain()
            print json.dumps(info ,indent=2)
            print opt
        else:
            info = {}
            opt = {}
        
        
    
if __name__ == '__main__':
    while True:
        try:
            choose_ticks('')
        except:
            traceback.print_exc()    
    
   
