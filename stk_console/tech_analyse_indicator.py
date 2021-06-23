#!coding:utf8
import datetime,time
import json
from collections import OrderedDict

import talib 
import pandas as pd
import numpy as np

from stk_util import time_count
from tech_cross_type import get_crossx_type,get_angle,get_angle_diff_stage

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
        
    df['CDLList'] = df.apply(make_dict,axis=1)
    ###
    total_cdl_score = df[cn_names].sum(axis=1)
    df['CDLScore'] =  total_cdl_score
    # print jsdump(cdl_info)
    return df

@time_count   
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

@time_count
def pivot_line_analyse(open,high,low,close):
    df = pd.DataFrame({'open':open,'high':high,'low':low,'close': close})
    def pivot_line_judge(row):
        po= pivot_line(row['open'],row['high'],row['low'],row['close'])
        return ','.join(['%s:%0.2f'%(k,v) for k,v in po.items()])
    df = pd.DataFrame({'pivot_line':df.apply(pivot_line_judge,axis=1)})
    return df    

@time_count    
def value_range_map(vlu,up_down_points,up_mid_down_name): 
    for i,thre in enumerate(up_down_points):
        if vlu > thre:
            return up_mid_down_name[i]
    return up_mid_down_name[-1]
    
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
        res+='-'+get_angle_diff_stage(u_ag,m_ag)
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
        return value_range_map( row['rsi'] ,[70,30],['OverBrought','MID','OverSell'])
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
        return value_range_map( row['cci'] ,[100,-100],['OverBrought','MID','OverSell'])
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
        return value_range_map( row['roc'] ,[0,-0.0001],['STRONG','ZERO','WEAK'])
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
            # ,'K-'+value_range_map( row['kdj_k'] ,[80,20],['OB','MD','OS']) +'-'+ value_range_map( row['kdj_k'] ,[50,49.99],['S','M','W'])
            # ,'D-'+value_range_map( row['kdj_d'] ,[80,20],['OB','MD','OS']) +'-'+ value_range_map( row['kdj_d'] ,[50,49.99],['S','M','W'])        
            # ,'J-'+value_range_map( row['kdj_j'] ,[80,20],['OB','MD','OS']) +'-'+ value_range_map( row['kdj_j'] ,[50,49.99],['S','M','W'])
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
    