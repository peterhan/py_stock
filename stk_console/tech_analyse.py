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
import numpy as np
from collections import OrderedDict
from matplotlib import pyplot as plt
from stk_util import time_count,add_indent
import pickle 

from tech_cross_type import get_crossx_type,get_angle
from tech_algo_analyse import catboost_factor_verify,join_factor_result_to_df,get_factor_judge_result,print_factor_result,add_target_day_out_col
SYS_ENCODE = locale.getpreferredencoding()


def load_ta_pat_map():
    return json.load(open('talib_pattern_name.json'))
TA_PATTERN_MAP = load_ta_pat_map()


@time_count
def candle_analyse(df):
    '''
    input:OHLC dataframe
    '''
    cn_names = []
    ## calc all candle score
    open,high,low,close = df['open'],df['high'],df['low'],df['close']    
    df=df[['date']].copy()
    
    func_names = talib.get_function_groups()['Pattern Recognition']
    for func_name in func_names:
        func = getattr(talib,func_name) 
        score_data = func(open,high,low,close)
        patt_name = func_name[3:]
        # if score_data!=0:
        df[patt_name] = score_data
        cn_names.append(patt_name)
    
    def make_dict(row):
        res_d = OrderedDict()
        for func_name in func_names:
            patt_name = func_name[3:]
            score = row[patt_name]
            if score!=0:
                res_d[patt_name] = score
        st= ','.join(['%s:%s'%(k,v) for k,v in res_d.items()])
        return st
        
    df['candle_list'] = df.apply(make_dict,axis=1)
    ###
    total_cdl_score = df[cn_names].sum(axis=1)
    df['CDLScore'] =  total_cdl_score
    # print jsdump(cdl_info)
    return df

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
    bres = [row['boll_stage']]
    bres += ['ANG[MID:%0.2f, UP:%0.2f], MID_PRC:%0.2f'%(row['bollmid_ag'], row['bollup_ag']-row['bollmid_ag'], row['boll_mid'])]
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
    
def pivot_line(open,high,low,close, mode='classic'):
    pivot = (high + low + 2* close )/4
    r1 = pivot*2 - low 
    s1 = pivot*2 - high
    r2 = pivot + r1 - s1
    s2 = pivot - (r1 - s1)
    r3 = high + 2*(pivot - low)
    s3 = low - 2*(high - pivot)
    names = 'pivot,r1,s1,r2,s2,r3,s3'.split(',')
    res_d = OrderedDict(zip(names ,[pivot,r1,s1,r2,s2,r3,s3]))
    if mode == 'extend':
        res_d['sm1'] = (pivot+s1)/2
        res_d['sm2'] = (s1+s2)/2
        res_d['sm3'] = (s2+s3)/2
        res_d['rm1'] = (pivot+r1)/2
        res_d['rm2'] = (r1+r2)/2
        res_d['rm3'] = (r2+r3)/2
    return res_d

def pivot_line_analyse(open,high,low,close):
    df = pd.DataFrame({'open':open,'high':high,'low':low,'close': close})
    def pivot_line_judge(row):
        po= pivot_line(row['open'],row['high'],row['low'],row['close'])
        return ','.join(['%s:%0.2f'%(k,v) for k,v in po.items()])
    df = pd.DataFrame({'pivot_line':df.apply(pivot_line_judge,axis=1)})
    return df    
    
def value_range_judge(vlu,up_down,up_down_mid_name): 
    if vlu>=up_down[0]:
        return up_down_mid_name[0]
    elif vlu<=up_down[1]:
        return up_down_mid_name[1]
    else:
        return up_down_mid_name[2]
  
@time_count
def boll_analyse(ohlcv,period=10):
    boll_up, boll_mid, boll_low = talib.BBANDS(ohlcv['close'],period)
    scale = period
    uag = get_angle(boll_up *scale, 2)
    mag = get_angle(boll_mid*scale, 2)    
    lag = get_angle(boll_low*scale, 2)
    df = pd.DataFrame({'boll_up': boll_up, 'boll_mid':boll_mid, 'boll_low':boll_low 
        ,'bollup_ag':uag,'bollmid_ag':mag,'bolllow_ag':lag })
    def boll_judge(row):
        m_ag = row['bollmid_ag']
        u_ag = row['bollup_ag']
        # print m,u
        if m_ag >= 0:
            res = 'UP'
        else:
            res = 'DN'
        if (u_ag - m_ag) >= 0:
            res += '-EXPAND'
        else:
            res += '-SHRINK'
        return res
    df['boll_stage'] = df.apply(boll_judge,axis=1)        
    return df
   
@time_count
def macd_analyse(ohlcv,period=10):
    dif, dea, hist =  talib.MACD(ohlcv['close'],period)
    # pdb.set_trace()
    # df = pd.DataFrame({'macd_dif': dif, 'macd_dea':dea, 'macd_hist':hist })        
    res = [] 
    df =  get_crossx_type(dif,dea)
    df['macd_hist'] = hist
    df = df.rename({'fast_line':'dif','slow_line':'dea','cross_stage':'macd_stage','fast_ag':'dif_ag','slow_ag':'dea_ag'},axis=1)
    def macd_judge(row):
        res = row['macd_stage']
        if row['macd_hist']>0:
            res +=' POS-HIS'
        else:
            res +=' NEG-HIS'        
        return res
    # pdb.set_trace()
    df['macd_stage'] = df.apply(macd_judge,axis=1) 
    return df
    
@time_count
def rsi_analyse(ohlcv,period=10):
    close = ohlcv['close']
    rsi = talib.RSI(close)
    rsi_ag = get_angle(rsi,2)
    df = pd.DataFrame({'rsi':rsi,'rsi_ag':rsi_ag})
    def rsi_row(row):
        return value_range_judge( row['rsi'] ,[70,30],['OverBrought','OverSell','MID'])
    df['rsi_stage'] =  df.apply(rsi_row, axis=1)
    # pdb.set_trace()
    return df

@time_count
def cci_analyse(ohlcv,period=10):
    high,low,close = ohlcv['high'],ohlcv['low'],ohlcv['close']
    cci = talib.CCI(high,low,close)    
    cci_ag = get_angle(cci,2)
    df = pd.DataFrame({'cci':cci,'cci_ag':cci_ag})
    def cci_row(row):
        return value_range_judge( row['cci'] ,[100,-100],['OverBrought','OverSell','MID'])
    df['cci_stage'] =  df.apply(cci_row, axis=1)
    # pdb.set_trace()
    return df

@time_count
def roc_analyse(ohlcv,period=10):
    high,low,close = ohlcv['high'],ohlcv['low'],ohlcv['close']
    roc = talib.ROCP(close)    
    roc_ag = get_angle(roc,2)
    maroc = talib.SMA(roc,14)
    maroc_ag = talib.SMA(maroc,14)
    df = pd.DataFrame({'roc':roc,'roc_ag':roc_ag,'maroc':maroc,'maroc_ag':maroc_ag})
    def roc_row(row):
        return value_range_judge( row['roc'] ,[0,0],['STRONG','WEAK','ZERO'])
    df['roc_stage'] =  df.apply(roc_row, axis=1)
    # pdb.set_trace()
    return df

@time_count
def kdj_analyse(ohlcv,period=10):
    high,low,close = ohlcv['high'],ohlcv['low'],ohlcv['close']
    slk,sld = talib.STOCH(high,low,close, fastk_period=9,slowk_period=3,slowk_matype=0,slowd_period=3,slowd_matype=0)
    slj = 3*slk-2*sld
    p_ag = get_angle(close)
    ##
    k_ag = get_angle(slk)
    d_ag = get_angle(sld)
    j_ag = get_angle(slj)
    ##
    k_aag = get_angle(k_ag)
    d_aag = get_angle(d_ag)
    j_aag = get_angle(j_ag)
    df = pd.DataFrame({'kdj_k':slk,'kdj_d':sld,'kdj_j':slj
        ,'k_ag':k_ag,'d_ag':d_ag,'j_ag':j_ag
        ,'p_ag':p_ag
        ,'k_aag':k_aag,'d_aag':d_aag,'j_aag':j_aag
        })
    def kdj_row(row):
        sw = 'MIDL'
        if row['kdj_k']>row['kdj_d']:
            sw = 'KD-STRG,'
        elif row['kdj_k']<row['kdj_d']:
            sw = 'KD-WEAK,'
        ##
        if row['p_ag']*row['k_ag']<0:
            sw += 'DVRG' ## 背离
        elif (row['k_ag']>0 and row['k_aag']<0) or \
             (row['k_ag']<0 and row['k_aag']>0) or \
             (row['d_ag']>0 and row['d_aag']<0) or \
             (row['d_ag']<0 and row['d_aag']>0):
            sw += 'TURN' ## 转向
        else:
            sw += 'NORM' ## 无现象
        res = [
            sw 
            # ,'K-'+value_range_judge( row['kdj_k'] ,[80,20],['OB','OS','MD']) +'-'+ value_range_judge( row['kdj_k'] ,[50,50],['S','W','M'])
            # ,'D-'+value_range_judge( row['kdj_d'] ,[80,20],['OB','OS','MD']) +'-'+ value_range_judge( row['kdj_d'] ,[50,50],['S','W','M'])        
            # ,'J-'+value_range_judge( row['kdj_j'] ,[80,20],['OB','OS','MD']) +'-'+ value_range_judge( row['kdj_j'] ,[50,50],['S','W','M'])
        ]
        return ','.join(res)
        
    df['kdj_stage'] =  df.apply(kdj_row, axis=1)
    return df

@time_count
def mtm_analyse(ohlcv,period1=6,period2=12):
    close = ohlcv['close']
    mom = talib.MOM(close,period1)
    mamom = talib.SMA(mom,period2)
    ag_mom = get_angle(mom)
    ag_mamom = get_angle(mamom)
    df = pd.DataFrame( {'mom':mom,'mamom':mamom,'ag_mom':ag_mom,'ag_mamom':ag_mamom} )
    def mom_row(row):
        res = []
        if row['mom']-row['mamom']>0:
            res.append('UP_MA')
        elif row['mom']-row['mamom']<=0:
            res.append('DN_MA')
        if row['mom']>0:
            res.append('POS_MOM')
        elif row['mom']<=0:
            res.append('NEG_MOM')
        
        return ' '.join(res)
    df['mom_cross_stage'] =  get_crossx_type(df['mom'],df['mamom'])['cross_stage']    
    df['mom_stage'] = df.apply(mom_row, axis=1)
    # pdb.set_trace()    
    return df

@time_count
def aroon_analyse(ohlcv,period=14):
    high = ohlcv['high']
    low = ohlcv['low']    
    adown,aup = talib.AROON(high,low,period)
    df = pd.DataFrame( {'aroon_down':adown,'aroon_up':aup} )
    '''当 AroonUp大于AroonDown，并且AroonUp大于50，多头开仓；
    当 AroonUp小于AroonDown，或者AroonUp小于50，多头平仓；
    当 AroonDown大于AroonUp，并且AroonDown大于50，空头开仓；
    当 AroonDown小于AroonUp，或者AroonDown小于50，空头平仓；'''
    def aroon_row(row):
        res = []
        if  row['aroon_up'] > row['aroon_down']  and row['aroon_up'] >50:
            res.append('UP-STRONG')
        elif  row['aroon_up'] < row['aroon_down']  or row['aroon_up'] <50:
            res.append('DN-WEAK')
        elif  row['aroon_up'] < row['aroon_down']  or row['aroon_down'] >50:
            res.append('DN-STRONG')
        elif  row['aroon_up'] > row['aroon_down']  or row['aroon_down'] <50:
            res.append('UP-WEAK')
        else:
            res.append('UNKNOWN')
        return ' '.join(res)
    df['aroon_stage'] = df.apply(aroon_row, axis=1)    
    return df
   
def get_weekday(dt):
    if isinstance(dt,basestring):
        dt = datetime.datetime.strptime(dt,'%Y-%m-%d')
    dic = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    w = dic[dt.weekday()]
    return w

@time_count
def weekday_analyse(df,col='date'):
    wd =pd.DataFrame()
    # pdb.set_trace()
    wd['week_stage'] = df[col].apply(get_weekday)
    return wd
    
@time_count    
def vwap_analyse(ohlcv,period = 3):  
    close,high,low,volume = ohlcv['close'],ohlcv['high'],ohlcv['low'],ohlcv['volume']
    df = ohlcv
    mse = np.square(close-(high+low)/2)
    df['mse'] = mse
    vwap,vswap = [],[]
    # pdb.set_trace()
    
    vsum = df['volume'].rolling(period).sum()
    pvsum = df['volume']*df['close']/vsum*period
    ma_pvsum = talib.SMA(pvsum, period)
    
    s_vsum = (df['volume']*df['mse']).rolling(period).sum()
    s_pvsum = (df['volume']*df['mse']*df['close'])/s_vsum*period
    s_ma_pvsum = talib.SMA(s_pvsum, period) 
    vwap = ma_pvsum
    vswap = s_ma_pvsum
    ndf = pd.DataFrame(df['close'])
    ndf['vwap'] = vwap
    ndf['vwap_stage'] = get_crossx_type(close,vwap)['cross_stage']
    ndf['vswap'] = vswap
    ndf['vswap_stage'] = get_crossx_type(close,vswap)['cross_stage']
    ndf.pop('close')
    return ndf
    
@time_count
def ma_analyse(ohlcv,period=10,target_col='close'):
    close = ohlcv[target_col]
    ma = OrderedDict()
    prefix=''
    if target_col!='close':
        prefix = '%s_'%target_col
    # cycles = [5,10,20,40,60,120,240]
    cycles = [3,5,20,60]
    for cyc in cycles:
        ma[prefix+'EMA%s'%cyc]  = talib.EMA(close,cyc)
        ma[prefix+'SMA%s'%cyc]  = talib.SMA(close,cyc)
    df = pd.DataFrame(ma)
    ## ema_sma_dif_judge
    def ema_sma_dif_judge(row):
        es_res = []
        for cyc in cycles:
            ema = row[prefix+'EMA%s'%cyc]
            sma = row[prefix+'SMA%s'%cyc]
            if ema>sma:
                s= '%s:UP'%cyc
            else:
                s='%s:DN'%cyc
            es_res.append(s)
        return ','.join(es_res)
    ##    
    def ma_stage_judge(row,ma_type):
        ma_res = []
        for i,cyc in enumerate(cycles[:-1]):
            ma = row[prefix+'%s%s'%(ma_type,cyc)]
            ama = row[prefix+'%s%s'%(ma_type,cycles[i+1])]
            if ma >= ama:
                s= '%s-%s:UP'%(cyc,cycles[i+1])
            else:
                s= '%s-%s:DN'%(cyc,cycles[i+1])
            ma_res.append(s)
        return ','.join(ma_res)
    ##
    df[ prefix +'ma_es_dif_stage'] = df.apply(ema_sma_dif_judge,axis=1)
    df[ prefix +'ema_stage'] = df.apply(lambda row:ma_stage_judge(row,'EMA'), axis=1)
    df[ prefix +'sma_stage'] = df.apply(lambda row:ma_stage_judge(row,'SMA'), axis=1)    
    return df

@time_count
def td9_analyse(ohlcv):
    close = ohlcv['close']
    return ohlcv
    
def pd_concat(df1,df2):
    return pd.concat([df1,df2.set_index(df1.index)],axis=1)
    
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
    
def jsdump(info, indent=None):
    return json.dumps(info, ensure_ascii=False, indent=indent) 

def analyse_res_to_str(stock_anly_res):
    intro = {}
    pstr = ''
    for stock in stock_anly_res:
        if stock is None:
            continue        
        code = stock.get('code','no-code')
        name = stock.get('info',{}).get('name','')
        price = stock.get('info',{}).get('price','')
        pstr+= "\n#[{0}:{1}] Price:{2}".format(code,name.encode(SYS_ENCODE),price)
        if 'algo_cb' in stock :
            pstr+= stock['algo_cb']            
        if 'tech' in stock and stock['tech'] != None:
            tech = stock['tech']
            for key,vlu in tech.get('data',{}).items():
                pstr+= '\n[%s] %s'%(key,jsdump(vlu))
            
        if 'cdl' in stock and stock['cdl'] != None:
            cdl = stock['cdl']            
            cdl_ent_arr = []            
            for name,info in cdl.get('data',{}).items():
                ent_st = u'[{}:{}]:{}{}'.format( info['score'], info['figure'], name, info['cn_name'] )
                cdl_ent_arr.append(ent_st)
                intro[info['en_name']+info['cn_name']] = info['intro']
            cdl_ent_str = ','.join(cdl_ent_arr)
            pstr += "\n[CDL_Total:{0}]  {1}".format(cdl.get('cdl_total','NaN'), cdl_ent_str.encode(SYS_ENCODE) )
    pstr += '\n'
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
    tick='600438'
    tick='600031'
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
    df,factor_results,pstr = catboost_process(tick,df,top_n=20)
    res[0]['algo_cb']=pstr
    print analyse_res_to_str(res)
    # pprint(cinfo)
    # print df.tail(1)
    ###
    df.to_csv('veri/tech.csv')
    pdb.set_trace()

if __name__ == '__main__':    
    main()