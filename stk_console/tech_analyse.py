#!coding:utf8
import json
import talib 
import traceback
import pdb
import datetime,time
import locale
import itertools
import os
import pandas as pd

from collections import OrderedDict
from matplotlib import pyplot as plt
from stk_util import time_count,add_indent,js_dumps,pd_concat
import pickle 
from tech_algo_analyse import catboost_factor_verify,join_factor_result_to_df,get_factor_judge_result,print_factor_result,add_target_day_out_col
from tech_analyse_indicator import *
SYS_ENCODE = locale.getpreferredencoding()

def extract_candle_tech_summary(row):
    # candle info
    cdl_info = {'cdl_total' : '%s'% (row['CDLScore']),'data':{} }
    for name,cdl_vlu in row.iteritems():        
        if cdl_vlu != 0 and name in TA_PATTERN_MAP:
            the_info = TA_PATTERN_MAP[name]
            fig = the_info['figure'].split(' ')[1]
            cn_name = the_info['name'].split(' ')[0]
            en_name = the_info['name'].split(' ')[1]
            define = the_info['define']
            intro = the_info['intro']
            cdl_info['data'][name] = {'figure':fig,'score':cdl_vlu,'cn_name':cn_name,'define':define,'intro':intro,'en_name':en_name}
    
    ## tech info
    tech_info = OrderedDict()
    tech_info['Price'] = row['close']
    
    bres = [row['boll_stage']]
    bres += ['ANG[MID:%0.2f, UP_DIF:%0.2f], MID_PRC:%0.2f'%(row['bollmid_ag'], row['bollup_ag']-row['bollmid_ag'], row['boll_mid'])]
    bres += ['UP:%0.2f, MID:%0.2f, LOW:%0.2f'%(row['boll_up'],row['boll_mid'],row['boll_low'])]
    tech_info['BOLL'] = bres
    
    tech_info['MACD'] = [
        '%s: ANG[IF:%0.2f, EA:%0.2f]'%(row['macd_stage'],row['dif_ag'],row['dea_ag']),
        'DIF:%0.2f, DEA:%0.2f, MACD:%0.2f'%(row['dif'],row['dea'],row['macd_hist']*2)
    ]
    
    tech_info['RSI'] = [row['rsi_stage']+', '+'RSI: %0.2f, ANG:%02.f'%(row['rsi'],row['rsi_ag'])]
    
    tech_info['CCI'] = row['cci_stage']+', '+'CCI: %0.2f, ANG:%02.f'%(row['cci'],row['cci_ag']) 
    
    tech_info['ROC'] = row['roc_stage']+', '+'ROC: %0.2f, ANG:%02.f'%(row['roc'],row['roc_ag'])
    
    tech_info['KDJ'] = [
        row['kdj_stage']
        ,'KDJ:%0.2f,%02.f,%02.f'%(row['kdj_k'],row['kdj_d'],row['kdj_j']) 
        ,'ANG-KDJ:%0.2f,%02.f,%02.f'%(row['k_ag'],row['d_ag'],row['j_ag'])
        ]
    
    
    tech_info['MOM'] = [row['mom_stage'],row['mom_cross_stage'],'MOM:','%0.2f'%row['mom'],'MA-MOM:','%0.2f'%row['mamom']]        
    
    tech_info['AROON'] = [row['aroon_stage'],'%0.2f'%row['aroon_up'], '%0.2f'%row['aroon_down'] ]
    
    tech_info['VWAP']={
        'vswap':'%0.2f'%row['vswap'],'vswap_stage':row['vswap_stage']
        ,'vwap':'%0.2f'%row['vwap'],  'vwap_stage':row['vwap_stage']
        ,'close':row['close']
        }
        
    def ma_str(row,typ,prefix,cycles):
        res = []
        for cyc in cycles:            
            k = '%sMA%s'%(typ,cyc)
            v = row[prefix+k]
            res.append('%s:%0.2f'%(k,v))
        return ', '.join(res)
        
    prefixes = ['','volume_']
    cycles = [3,5,20,60]
    for prefix in prefixes:
        tech_info['MA'+' '+prefix] = ['[S]'+row[prefix+'sma_stage'], '[E]'+row[prefix+'ema_stage'], 
            '[ES]'+row[prefix+'ma_es_dif_stage'],
            ma_str(row,'E',prefix,cycles), ma_str(row,'S',prefix,cycles)
        ]
    
    return cdl_info,{'data':tech_info}



    
@time_count
def tech_analyse(df):  
    def round_float(lst):
        return map(lambda x:'%0.2f'%x,lst)   
    '''
    input:OHLC dataframe
    '''
    open = df['open'].values
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    vol = df['volume'].values.astype(float)
    # ohlcv= {'open':open,'high':high,'low':low,'close':close,'volume':vol}
    ohlcv = df    
    
    df = df[['date']].copy()

    ## BOLL
    bdf = boll_analyse(ohlcv)
    df= pd_concat(df,bdf)    
    
    ## VWAP VSWAP
    vdf = vwap_analyse(ohlcv)
    df= pd_concat(df,vdf)    
        
    ## ROC
    try:
        rdf = roc_analyse(ohlcv)
        df = pd_concat(df,rdf)
    except:
        traceback.print_exc()
    
    ## MTM
    mdf =  mtm_analyse(ohlcv)
    df = pd_concat(df, mdf)
    df.sort_index()    
    
    ## MACD
    try:
        mdf = macd_analyse(ohlcv)
        df= pd_concat(df,mdf)
    except:
        traceback.print_exc()
    
    ## MA
    mdf = ma_analyse(ohlcv)
    df = pd_concat(df,mdf)
    ## VOLMA
    # pdb.set_trace()
    vdf = ma_analyse(ohlcv,target_col='volume')
    df= pd_concat(df,vdf) 
    
    ## weekday
    wdf = weekday_analyse(df)
    df = pd_concat(df,wdf)
    
    ## RSI
    rdf = rsi_analyse(ohlcv)
    df = pd_concat(df,rdf) 
    
    ## KDJ 
    kdf = kdj_analyse(ohlcv)
    df = pd_concat(df,kdf)
    
    ## CCI 
    cdf = cci_analyse(ohlcv)
    df = pd_concat(df,cdf)    
    
    ## talib.APO
    
    ## talib.AROON
    adf = aroon_analyse(ohlcv)
    df = pd_concat(df,adf)
    
    ## Forcast
    df['tsf'] = talib.TSF(ohlcv['close'])
    
    ## OBV
    df['obv'] = talib.OBV(close,vol)
    
    ## SAR
    df['sar'] = talib.SAREXT(high,low)    
    
    ## ATR
    df['atr14'] = talib.ATR(high,low,close,timeperiod =14)
    df['atr28'] = talib.ATR(high,low,close,timeperiod =28)
    
    ##pivot line
    # df['pivot_point'] 
    ppdf = pivot_line_analyse(open,high,low,close)
    # pdb.set_trace()
    df = pd_concat(df,ppdf)
    # name = ' '
    
    analyse_info = OrderedDict({'price':close[-1]})
    
    df['vol_rate'] = pd.Series(vol) / pd.Series(vol).shift(1)
    
    ### put into output     
    df = df.loc[:,~df.columns.duplicated()]
    return df
    


def analyse_res_to_str(stock_anly_res):
    intro = {}
    pstrs = []
    for stock in stock_anly_res:
        pstr = ''
        if stock is None:
            continue        
        code = stock.get('code','no-code')
        name = stock.get('info',{}).get('name','')
        price = stock.get('info',{}).get('price','')
        pstr+= "#[{0}:{1}] Price:{2}".format(code,name.encode(SYS_ENCODE),price)
        if 'algo_cb' in stock :
            pstr+= stock['algo_cb']            
        if 'tech' in stock and stock['tech'] != None:
            tech = stock['tech']
            for key,vlu in tech.get('data',{}).items():
                pstr+= '\n[%s] %s'%(key,js_dumps(vlu))
            
        if 'cdl' in stock and stock['cdl'] != None:
            cdl = stock['cdl']            
            cdl_ent_arr = []            
            for name,info in cdl.get('data',{}).items():
                ent_st = u'[{}:{}]:{}{}'.format( info['score'], info['figure'], name, info['cn_name'] )
                cdl_ent_arr.append(ent_st)
                intro[info['en_name']+info['cn_name']] = info['intro']
            cdl_ent_str = ','.join(cdl_ent_arr)
            pstr += "\n[CDL_Total:{0}]  {1}".format(cdl.get('cdl_total','NaN'), cdl_ent_str.encode(SYS_ENCODE) )
        pstrs.append(pstr)
    pstr = '\n\n'.join(pstrs)
    for name,intro in intro.items():
        pstr+= u"\n[EXPLAIN:{}]:{}".format(name,intro).encode(SYS_ENCODE)     
    return add_indent(pstr,'  ')

def yf_get_hist_data(tick):
    import yfinance as yf    
    import datetime
    tk = yf.Ticker(tick)
    start = (datetime.datetime.now()-datetime.timedelta(days=300)).strftime('%Y-%m-%d')
    df = tk.history(start=start)
    df = df.rename(columns={'Date':'date','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume','Dividends':'dividends' , 'Stock Splits':'splits'})
    df['turnover'] = 0
    return df

def get_model_filename(tick,type,dt='210601'):
    folder = 'model_catboost.cache'
    if not os.path.exists(folder):
        os.mkdir(folder)
    fname=folder+'/'+tick.replace('.','_')+'.'+type+'.%s.model'%dt
    if os.path.exists(fname):
        return True,fname
    else:
        return False,fname

DEFAULT_COMBO_LIST = [ 
        ['roc_stage'] 
        ,['vwap_stage','ema_stage']
        ,['macd_stage','rsi_stage']
        ,['week_stage','ema_stage']
        ,['boll_stage'] ,['kdj_stage'] ,['mom_stage']
        ,['week_stage'] ,['CDLScore']
        ,['ema_stage']  ,['sma_stage']
        ,['volume_ema_stage'] ,['volume_sma_stage']  
        #,['aroon_stage']
        ,['macd_stage'] ,['cci_stage'] 
        ,['rsi_stage']  ,['ma_es_dif_stage']
        ,['vswap_stage'],['vwap_stage']
]

@time_count 
def catboost_process(tick,df,top_n=20,factor_combo_list=None,target_days=None,no_cache=False):
    global DEFAULT_COMBO_LIST
    if factor_combo_list is None:
        factor_combo_list = DEFAULT_COMBO_LIST
    if target_days is None:
        target_days=['1d','3d','5d','10d','20d','30d','60d']
        target_days=['1d','5d','10d']
    print '[factor_combo_list]:',factor_combo_list 
    print '[target_days]',target_days
    flag,pfname = get_model_filename(tick,'factor')
    df = df.loc[:,~df.columns.duplicated()]
    # cycles=['5d']
    if (not flag) or  no_cache:
        print('  [train_cb_model]')
        df = add_target_day_out_col(df,target_days)
        factor_results  = catboost_factor_verify(df, target_days=target_days,factor_combo_list=factor_combo_list)        
        pickle.dump(factor_results,open(pfname ,'w'))
        print('  [dump_cb_cache_finish]')
    else:
        factor_results = pickle.load(open(pfname ))
        print('  [read_cb_cache_finish]')    
    df = join_factor_result_to_df(df,factor_results)
    jdf = get_factor_judge_result(df.iloc[-1])    
    pstr = '\n'+str(jdf[:top_n])    
    return df,factor_results,pstr
    
def main():
    import tushare as ts
    pd.set_option('display.width',None)
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    def pprint(info, indent=None):
        print json.dumps(info, ensure_ascii=False, indent=2).encode(ENCODE)
    
    remote_call = False
    remote_call = True
    # tick='tsla'
    tick='600031'
    tick='600438'
    if remote_call:
        # df = yf_get_hist_data(tick) 
        
        df = ts.get_k_data(tick)  #df从旧到新
        # df = ts.get_hist_data(tick)  # 从新到旧
        # df['date'] = df.index        
        df = df.sort_index()
        
        # df.index.name='date'
        # pdb.set_trace()
        df.to_csv('veri/origin.csv')
    
    df=pd.read_csv('veri/origin.csv')
    if 'date' not in df.columns:
        df['date'] = df.index 
    # pdb.set_trace()
    df = df.sort_values('date')
    tdf = tech_analyse(df)    
    cdf = candle_analyse(df)    
    df = pd.concat([df,tdf,cdf],axis=1)
    
    cinfo,tinfo = extract_candle_tech_summary(df.iloc[-1])    
    # pdb.set_trace()
    
    res = [{'code':tick,'info':{}
        ,'tech':tinfo,'cdl':cinfo }]
    adf,factor_results,pstr = catboost_process(tick,df,top_n=20)
    res[0]['algo_cb']=pstr
    print analyse_res_to_str(res)
    
    print '##[10 days ago]'
    cinfo,tinfo = extract_candle_tech_summary(df.iloc[-10])
    res = [{'code':tick,'info':{}
        ,'tech':tinfo,'cdl':cinfo }]
    adf,factor_results,pstr = catboost_process(tick,df,top_n=20)
    res[0]['algo_cb']=pstr
    print analyse_res_to_str(res)
    # pprint(cinfo)
    # print df.tail(1)
    ###
    df.to_csv('veri/tech.csv')
    pdb.set_trace()

if __name__ == '__main__':    
    main()