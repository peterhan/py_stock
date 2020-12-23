#!coding:utf8
import json
import talib 
import pandas as pd
import numpy as np
import traceback
import pdb
import locale
from collections import OrderedDict
from matplotlib import pyplot as plt


def load_ta_pat_map():
    return json.load(open('talib_pattern_name.json'))
TA_PATTERN_MAP = load_ta_pat_map()

cdl_pat_names =  []
def candle_analyse(df):
    '''
    input:OHLC dataframe
    '''
    cn_names = []
    ## calc all candle score
    open,high,low,close = df['open'],df['high'],df['low'],df['close']    
    df=df[['date']].copy()
    for funcname in talib.get_function_groups()[ 'Pattern Recognition']:
        func = getattr(talib,funcname) 
        score_data = func(open,high,low,close)
        pat_name = funcname[3:]        
        cdl_pat_names.append(pat_name) 
        df[pat_name] = score_data
        cn_names.append(pat_name)
    
    ###
    total_cdl_score = df[cn_names].sum(axis=1)
    df['CDLScore'] =  total_cdl_score
    cdl_info = {'cdl_total' : '%s'% (total_cdl_score.values[-1]),'data':{} }
    last_cdlrow = df.iloc[-1]
    for name,cdl_vlu in last_cdlrow.iteritems():        
        if cdl_vlu != 0 and name in TA_PATTERN_MAP:
            the_info = TA_PATTERN_MAP[name]
            fig = the_info['figure'].split(' ')[1]
            cn_name = the_info['name'].split(' ')[0]
            en_name = the_info['name'].split(' ')[1]
            define = the_info['define']
            intro = the_info['intro']
            cdl_info['data'][name] = {'figure':fig,'score':cdl_vlu,'cn_name':cn_name,'define':define,'intro':intro,'en_name':en_name}
    # print jsdump(cdl_info)
    return cdl_info,df
    
def pivot_line(open,high,low,close, mode='classic'):
    pivot = (high + low + 2* close )/4
    r1 = pivot*2 - low 
    s1 = pivot*2 - high
    r2 = pivot + r1 - s1
    s2 = pivot - (r1 - s1)
    r3 = high + 2*(pivot - low)
    s3 = low - 2*(high - pivot)
    sm1 = (pivot+s1)/2
    sm2 = (s1+s2)/2
    sm3 = (s2+s3)/2
    rm1 = (pivot+r1)/2
    rm2 = (r1+r2)/2
    rm3 = (r2+r3)/2
    return r3,r2,r1,pivot,s1,s2,s3    
    
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
    row = df.iloc[-1]
    res = [row['boll_stage']]
    res += ['ANG[MID:%0.2f, UP:%0.2f], MID_PRC:%0.2f'%(row['bollmid_ag'], row['bollup_ag']-row['bollmid_ag'], row['boll_mid'])]
    res += ['UP:%0.2f, MID:%0.2f, LOW:%0.2f'%(row['boll_up'],row['boll_mid'],row['boll_low'])]
    return res,df
    
 
def value_range_judge(vlu,up_down,up_down_mid_name): 
    if vlu>=up_down[0]:
        return up_down_mid_name[0]
    elif vlu<=up_down[1]:
        return up_down_mid_name[1]
    else:
        return up_down_mid_name[2]    


    
def get_crossx_type(fast_line,slow_line):
    fast_ag = get_angle(fast_line, 2)
    slow_ag = get_angle(slow_line, 2)
    df=pd.DataFrame({'fast_line':fast_line,'slow_line':slow_line,'fast_ag':fast_ag,'slow_ag':slow_ag})
    def cross_judge(row):    
        # pdb.set_trace()
        fast_ag = row['fast_ag']
        slow_ag = row['slow_ag']
        ag_dif = fast_ag - slow_ag
        value_gap = row['fast_line'] - row['slow_line']
        if fast_ag>0 and slow_ag>0:
            res='Aft-GX'
        elif fast_ag>0  and slow_ag<0:
            res='TrnBef-GX'
        elif ag_dif>0 and slow_ag<0:
            res='CnvBef-GX'
        elif fast_ag<0 and slow_ag<0:
            res='Aft-DX'
        elif fast_ag<0  and slow_ag>0:
            res='TrnBef-DX'
        elif  ag_dif<0 and slow_ag>0:
            res='CnvBef-DX'
        else:
            # print ag_dif,fast_ag,slow_ag
            res='Unknown'
        return res
    df['cross_stage'] = df.apply(cross_judge,axis=1)#,result_type='expand'    
    # print edf
    return df
    
def get_angle(ss,p=2):
    fss = np.nan_to_num(ss,0)
    ang =  talib.LINEARREG_ANGLE(fss, timeperiod=p)    
    return ang
    
    
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
            res +=' POS-HIST'
        else:
            res +=' NEG-HIST'        
        return res
    # pdb.set_trace()
    df['macd_stage'] = df.apply(macd_judge,axis=1)    
    row = df.iloc[-1]         
    res += ['%s: ANG[IF:%0.2f, EA:%0.2f]'%(row['macd_stage'],row['dif_ag'],row['dea_ag'])]
    res += ['DIF:%0.2f, DEA:%0.2f, MACD:%0.2f'%(row['dif'],row['dea'],row['macd_hist']*2)]   
    return res,df
    
def rsi_analyse(ohlcv,period=10):
    close = ohlcv['close']
    rsi = talib.RSI(close)
    rsi_ag = get_angle(rsi,2)
    df = pd.DataFrame({'rsi':rsi,'rsi_ag':rsi_ag})
    def rsi_row(row):
        return value_range_judge( row['rsi'] ,[70,30],['OverBrought','OverSell','MID'])
    df['rsi_stage'] =  df.apply(rsi_row, axis=1)
    # pdb.set_trace()
    row = df.iloc[-1]
    res_info = row['rsi_stage']+', '+'RSI: %0.2f, ANG:%02.f'%(row['rsi'],row['rsi_ag'])
    return res_info,df

def cci_analyse(ohlcv,period=10):
    high,low,close = ohlcv['high'],ohlcv['low'],ohlcv['close']
    cci = talib.CCI(high,low,close)    
    cci_ag = get_angle(cci,2)
    df = pd.DataFrame({'cci':cci,'cci_ag':cci_ag})
    def cci_row(row):
        return value_range_judge( row['cci'] ,[100,-100],['OverBrought','OverSell','MID'])
    df['cci_stage'] =  df.apply(cci_row, axis=1)
    # pdb.set_trace()
    row = df.iloc[-1]
    res_info = row['cci_stage']+', '+'CCI: %0.2f, ANG:%02.f'%(row['cci'],row['cci_ag'])
    return res_info,df

def roc_analyse(ohlcv,period=10):
    high,low,close = ohlcv['high'],ohlcv['low'],ohlcv['close']
    roc = talib.ROCP(close)    
    roc_ag = get_angle(roc,2)
    maroc = talib.SMA(roc,14)
    maroc_ag = talib.SMA(maroc,14)
    # plt.plot(roc)
    # plt.plot(maroc)
    # plt.show()
    df = pd.DataFrame({'roc':roc,'roc_ag':roc_ag,'maroc':maroc,'maroc_ag':maroc_ag})
    def roc_row(row):
        return value_range_judge( row['roc'] ,[0,0],['STRONG','WEAK','ZERO'])
    df['roc_stage'] =  df.apply(roc_row, axis=1)
    # pdb.set_trace()
    row = df.iloc[-1]
    res_info = row['roc_stage']+', '+'ROC: %0.2f, ANG:%02.f'%(row['roc'],row['roc_ag'])
    return res_info,df

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
    row = df.iloc[-1]
    res_info = [
        row['kdj_stage']
        ,'KDJ:%0.2f,%02.f,%02.f'%(row['kdj_k'],row['kdj_d'],row['kdj_j']) 
        ,'ANG-KDJ:%0.2f,%02.f,%02.f'%(row['k_ag'],row['d_ag'],row['j_ag'])
        ]
    res_info = ', '.join(res_info)
    return res_info,df

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
    row = df.iloc[-1]
    res_info = [row['mom_stage'],row['mom_cross_stage'],'MOM:','%0.2f'%row['mom'],'MA-MOM:','%0.2f'%row['mamom']]
    return res_info,df


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
            res.append('UP_STRONG')
        elif  row['aroon_up'] < row['aroon_down']  or row['aroon_up'] <50:
            res.append('DN_WEAK')
        elif  row['aroon_up'] < row['aroon_down']  or row['aroon_down'] >50:
            res.append('DN_STRONG')
        elif  row['aroon_up'] > row['aroon_down']  or row['aroon_down'] <50:
            res.append('UP_WEAK')
        else:
            res.append('UNKNOWN')
        return ' '.join(res)
    df['aroon_stage'] = df.apply(aroon_row, axis=1)
    row = df.iloc[-1]
    res_info = [row['aroon_stage'],row['aroon_up'], row['aroon_down'] ]
    return res_info,df
   
    
def vwap_analyse(ohlcv,period = 3):  
    close,high,low,volume = ohlcv['close'],ohlcv['high'],ohlcv['low'],ohlcv['volume']
    df = ohlcv
    mse = np.square(close-(high+low)/2)
    df['mse'] = mse
    vwap,vswap = [],[]
    for i  in range(0,df.shape[0]):
        if i < period-1:
            vwap.append(np.NaN)
            vswap.append(np.NaN)
            continue
        idxs = [p for p in range(i-period,i+1)]
        ##
        v_sum = sum([df.iloc[p]['volume'] for p in range(i-period,i+1) ])
        pvsum = sum([df.iloc[p]['close']*df.iloc[p]['volume']/v_sum for p in range(i-period,i+1) ])
        vwap.append(pvsum)
        ##
        vm_sum    = sum([df.iloc[p]['mse']  *df.iloc[p]['volume'] for p in range(i-period,i+1) ])
        pvsum_fix = sum([df.iloc[p]['close']*df.iloc[p]['volume']*df.iloc[p]['mse']/vm_sum for p in range(i-period,i+1) ])
        vswap.append(pvsum_fix)
    ndf = pd.DataFrame(df['close'])
    ndf['vwap']=vwap
    ndf['vwap_stage']=  get_crossx_type(vwap,close)['cross_stage']
    ndf['vswap']=vswap
    ndf['vswap_stage']=  get_crossx_type(vswap,close)['cross_stage']
    row=ndf.iloc[-1]
    vwap_info={'close':row['close']
        ,'vswap':'%0.2f'%row['vswap'],'vswap_stage':row['vswap_stage']
        ,'vwap':'%0.2f'%row['vwap'],'vwap_stage':row['vwap_stage']
        }
    ndf.pop('close')
    return vwap_info,ndf
    
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
    ## 
    def ma_es_dif_judge(row):
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
    df[ prefix +'ma_es_dif_stage'] = df.apply(ma_es_dif_judge,axis=1)
    df[ prefix +'ema_stage'] = df.apply(lambda row:ma_stage_judge(row,'EMA'), axis=1)
    df[ prefix +'sma_stage'] = df.apply(lambda row:ma_stage_judge(row,'SMA'), axis=1)
    row = df.iloc[-1]
    def ma_str(row,typ):
        res = []
        for cyc in cycles:            
            k = '%sMA%s'%(typ,cyc)
            v = row[prefix+k]
            res.append('%s:%0.2f'%(k,v))
        return ', '.join(res)
    res_info = ['[S]'+row[prefix+'sma_stage'], '[E]'+row[prefix+'ema_stage'], '[ES]'+row[prefix+'ma_es_dif_stage'], ma_str(row,'E'), ma_str(row,'S')]
    return res_info,df
    
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
    
    ana_res = OrderedDict()
    
    def pd_concat(df1,df2):
        return pd.concat([df1,df2.set_index(df1.index)],axis=1)
    
    df = df[['date']].copy()

    ## MACD
    try:
        macd_anly_res,mdf = macd_analyse(ohlcv)
        df= pd_concat(df,mdf)
        ana_res['MACD'] = macd_anly_res
    except:
        traceback.print_exc()
    
    ## MTM
    mtm_res,mdf =  mtm_analyse(ohlcv)
    df= pd_concat(df, mdf)
    ana_res['MTM'] = mtm_res
    
    ## VWAP VSWAP
    vwap_res,vdf = vwap_analyse(ohlcv)
    df= pd_concat(df,vdf)
    ana_res['VWAP'] = vwap_res
    
    ## MA
    ma_anly_res,mdf = ma_analyse(ohlcv)
    df= pd_concat(df,mdf)
    ana_res['MA'] = ma_anly_res[0] + ' ' + ma_anly_res[1]    
    ana_res['ES-MA'] = ma_anly_res[2]
    ana_res['EMA-DTL'] = ma_anly_res[3]
    ana_res['SMA-DTL'] = ma_anly_res[4]    

    ## volma
    # pdb.set_trace()
    volume_ma_res, vdf = ma_analyse(ohlcv,target_col='volume')
    df= pd_concat(df,vdf)
    ana_res['VOL_MA'] = volume_ma_res[0] + ' ' + volume_ma_res[1]    
    ana_res['VOL_ES-MA'] = volume_ma_res[2]
    # ana_res['VOL_EMA-DTL'] = volume_ma_res[3]
    # ana_res['VOL_SMA-DTL'] = volume_ma_res[4]   
    
    ## BOLL
    boll_anly_res,bdf = boll_analyse(ohlcv)
    df= pd_concat(df,bdf)
    ana_res['BOLL'] =  boll_anly_res
    
    ## RSI
    rsi_anly_res,rdf = rsi_analyse(ohlcv)
    df= pd_concat(df,rdf)
    ana_res['RSI'] = rsi_anly_res    
    
    ## KDJ 
    kdj_anly_res,kdf = kdj_analyse(ohlcv)
    df= pd_concat(df,kdf)
    ana_res['KDJ'] = kdj_anly_res
    
    ## CCI 
    cci_anly_res,cdf = cci_analyse(ohlcv)
    df= pd_concat(df,cdf)
    ana_res['CCI'] = cci_anly_res
    
    
    ## talib.APO
    ## talib.AROON
    aroon_ana_res,adf = aroon_analyse(ohlcv)
    df= pd_concat(df,adf)
    ana_res['AROON'] = aroon_ana_res
    
    ## ROC
    try:
        roc_anly_res,rdf = roc_analyse(ohlcv)
        df = pd_concat(df,rdf)
        ana_res['ROC'] = roc_anly_res
    except:
        traceback.print_exc()
    
    ## Forcast
    tsf_res =  'Forcast: %0.2f'%list(talib.TSF(ohlcv['close']))[-1]
    ana_res['TSF'] = tsf_res
    
    ## OBV
    obv = talib.OBV(close,vol)
    
    ## SAR
    sar = talib.SAREXT(high,low)    
 
    ##
    atr14 = talib.ATR(high,low,close,timeperiod =14)
    atr28 = talib.ATR(high,low,close,timeperiod =28)
    ##
    pivot_point = map(lambda x:round(x[-1],2) , pivot_line(open,high,low,close) )    
    # name = ' '
    analyse_info = OrderedDict({'price':close[-1]})
    
    # ana_res['BOLL'] = [bl_upper[-1],bl_middle[-1],bl_lower[-1] ]
           
    # ana_res['OBV'] = round_float([ obv[-1] ])
    ana_res['SAR'] = round_float([ sar[-1] ])
    # ana_res['EMA'] = round_float([ ema05[-1],ema10[-1],ema20[-1],ema60[-1],ema240[-1] ])
    # ana_res['SMA'] = round_float([ sma05[-1],sma10[-1],sma20[-1],sma60[-1],sma240[-1] ])
    ana_res['VOL_Rate'] = round_float([vol[-1]*1.0/vol[-2]])
    # ana_res['ATR14'] = round_float(list(atr14[-10::2]))
    # ana_res['ATR28'] = round_float(list(atr28[-10::2]))
    ana_res['PIVOT'] = 'Resistance:%s, Mid:%s, Support:%s'%(pivot_point[0:3],pivot_point[3],pivot_point[4:])
    ### put into output 
    analyse_info['data']= ana_res
    # pdb.set_trace()
    return analyse_info,df
    
def jsdump(info, indent=None):
    return json.dumps(info, ensure_ascii=False, indent=indent) 
    
ECODE=locale.getpreferredencoding()
def analyse_res_to_str(stock_anly_res):
    intro = {}
    pstr = ''
    for stock in stock_anly_res:
        if stock is None:
            continue        
        code = stock.get('code','no-code')
        name = stock.get('info',{}).get('name','')
        price = stock.get('info',{}).get('price','')
        pstr+= "\n[{0}:{1}] Price:{2}".format(code,name.encode(ECODE),price)
        if 'tech' in stock and stock['tech'] != None:
            tech = stock['tech']
            for key,vlu in tech['data'].items():
                pstr+= '\n  [%s] %s'%(key,jsdump(vlu))
            
        if 'cdl' in stock and stock['cdl'] != None:
            cdl = stock['cdl']
            cdl_ent_str = ','.join([u'[{}:{}]:{}{}'.format(info['score'],info['figure'],name,info['cn_name']) for name,info in cdl['data'].items()])
            for name,info in cdl['data'].items():
                intro[info['en_name']+info['cn_name']] = info['intro']
            pstr+= "\n  [CDL_Total:{0}]  {1}".format(cdl['cdl_total'], cdl_ent_str.encode(ECODE) )
    pstr += '\n'
    for name,intro in intro.items():
        pstr+= u"\n  [EXPLAIN:{}]:{}".format(name,intro).encode(ECODE)  
    return pstr


    
def caculate_indicator(df, i_stages, target_col):
    # i_stages = cdl_pat_names
    # adf = df[['turnover','rsi','dif_ag','rsi_ag','dif','k_ag','j_ag','d_ag','dea']+i_stages].copy()
    adf = df[['rsi','dif_ag','rsi_ag','dif','k_ag','j_ag','d_ag','dea']+i_stages].copy()
    bencols = []
    bencols.append(target_col)
    i=int(target_col.split('_')[-1].strip('d'))
    adf[target_col] =  (df['close'] / df['close'].shift(i) -1)*100
    #for i in (1,3,5,7,10,15):
    ## for i in (1,3,5,7):
    #    bname = 'p_change_%sd'%i
    #    # pdb.set_trace()
    #    adf[bname] = (df['close'] / df['close'].shift(i) -1)*100
    #    bencols.append(bname)
    # adf['p_change_20d'] = df['p_change'].shift(-20)
    # adf['p_change_30d'] = df['p_change'].shift(-30)
    # print adf.corr()
    
    adf.to_csv("veri/train_dump.csv")
    def stat_gp(gp):
        return gp.agg([np.size, np.mean, np.std, np.max, np.min]) 
        # gp.agg({'text':'size', 'sent':'mean'}) \        
       #.rename(columns={'text':'count','sent':'mean_sent'}) \
       #.reset_index()
       #.iloc[:,offset:]
    # df = stat_gp(adf.groupby(['macd_stage','sma_stage','rsi_stage'] )[bencols])
    # print df
    # df.to_csv('veri/comb.csv')
    for stage in i_stages:
        df = stat_gp(adf.groupby(stage )[bencols])
        # print df
        # df.to_csv('veri/'+stage+".csv")       
    # pdb.set_trace()
    return adf


def rmse(targets,predictions):
    return np.sqrt(((predictions - targets) ** 2).mean())
    
def predict_cat(fit_model, adf,i_stages,target_col):
    from catboost import CatBoostRegressor
    factor_results = {}
    test_pool = adf[i_stages][-50:]
    test_labels = adf[target_col].fillna(0)[-50:]
    model = fit_model
    # model = CatBoostRegressor(learning_rate=1, depth=6, loss_function='RMSE',cat_features=i_stages)
    # model.load_model('first.model')
    # preds_class = model.predict(test_pool, prediction_type='Class')
    # preds_proba = model.predict(test_pool, prediction_type='Probability')
    preds_raw_vals = model.predict(test_pool, prediction_type='RawFormulaVal')
    # pdb.set_trace()
    
    ss = [[k] for k in  test_pool[i_stages[0]].value_counts().index]
    
    ps = model.predict(ss)
    sts = [row[0] for row in ss]
    pdf  = pd.DataFrame({'feature':sts,'weight':ps}).sort_values('weight',ascending=False)
    
    key=':'.join (i_stages)+'=>'+target_col
    factor_results[key] = {}
    check_result=factor_results[key]
    check_result['factor_detail']=pdf
    
    # print preds_raw_vals,test_labels

    rmsev = rmse( np.sign(test_labels.values), np.sign(preds_raw_vals) )
    check_result['rmsev']=rmsev
    pos_neg = pd.Series(np.sign(test_labels*preds_raw_vals)*10,index=test_labels.index)
    pnvc = pos_neg.value_counts()    
    check_result['correct_rate']=pnvc[10.0]*1.0/sum(pnvc.values)*100    
    return factor_results


def train_cat(adf,i_stages,target_col):
    from catboost import CatBoostRegressor
    dataset = adf[i_stages][:]
    train_labels = adf[target_col].fillna(0)[:]
    model = CatBoostRegressor(learning_rate=1, depth=6, loss_function='RMSE',cat_features=i_stages)
    try:
        fit_model = model.fit(dataset, train_labels, verbose=0)
    except:
        traceback.print_exc()

    # print(fit_model.get_params())
    # fit_model.save_model('first.model')
    return fit_model
    # pdb.set_trace()


def cat_boost_factor_check(df,target_days = ['5d'],print_res=True):
    i_stages = [['cci_stage','ema_stage','volume_ema_stage','volume_sma_stage','sma_stage','ma_es_dif_stage','macd_stage','boll_stage','rsi_stage','kdj_stage','mom_stage','aroon_stage','vswap_stage','vwap_stage'] ]    
    i_stage_list = [  ['ema_stage']  ,['sma_stage'],['volume_ema_stage'] ,['volume_sma_stage']  ,['macd_stage'] ,['cci_stage'] ,['roc_stage'] ,['rsi_stage'] ,['ma_es_dif_stage'],['boll_stage'] ,['kdj_stage'] ,['mom_stage'], ['aroon_stage'],['vswap_stage'],['vwap_stage']]
    factor_results = {}
    for target_col in ['p_change_%s'%target_day for target_day in target_days]:    
        for i_stages in i_stage_list:
            try:
                if len(target_days)>2:
                    print '[Training]:',i_stages,target_col
                adf = caculate_indicator(df, i_stages, target_col)
                fit_model = train_cat(adf,i_stages,target_col)
                cres = predict_cat(fit_model ,adf,i_stages,target_col)
                factor_results.update(cres)
            except:
                traceback.print_exc()
    if print_res:
        print ''
        for key,check_result in sorted(factor_results.items(),key=lambda v:v[1]['correct_rate'],reverse=False):
            print '[%s]'%(key)
            print check_result['factor_detail']
            print 'rmse: %0.2f'%check_result['rmsev']
            print 'correct_rate: %0.2f%%'%(check_result['correct_rate'])
            print ''
    # from matplotlib import pyplot as plt
    # plt.title('%s %s'%(i_stages,target_col))
    # plt.plot(preds_raw_vals[:],'--')
    # plt.plot(test_labels.values[:])
    # plt.plot(pos_neg.values[:],':')
    # plt.show()
    # return preds_class,preds_proba,preds_raw_vals
    return factor_results


def yf_get_hist_data(tick):
    import yfinance as yf    
    import datetime
    tk = yf.Ticker(tick)
    start = (datetime.datetime.now()-datetime.timedelta(days=300)).strftime('%Y-%m-%d')
    df = tk.history(start=start)
    df = df.rename(columns={'Date':'date','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume','Dividends':'dividends' , 'Stock Splits':'splits'})
    df['turnover'] = 0
    return df
    
def main():
    pd.set_option('display.max_columns',80)
    import tushare as ts
    
    def pprint(info, indent=None):
        print json.dumps(info, ensure_ascii=False, indent=2).encode(ENCODE)
    
    remote_call = False
    # remote_call = True
    # tick='tsla'
    tick='601601'
    if remote_call:
        # df = yf_get_hist_data(tick)
        
        df = ts.get_hist_data(tick)
                
        df = df.sort_index()
        
        df.index.name='date'
        # pdb.set_trace()
        df.to_csv('veri/origin.csv')
    
    # pdb.set_trace()
    
    df=pd.read_csv('veri/origin.csv',index_col='date')
    df['date'] = df.index
    
    # df = df.sort_values('date')
    tinfo,tdf = tech_analyse(df)
    # print df.tail(1)
    # df.to_csv('temp_res.csv')
    # pdb.set_trace()
    cinfo,cdf = candle_analyse(df)
    res = [{'code':tick,'info':{}
        ,'tech':tinfo,'cdl':cinfo}]
    print analyse_res_to_str(res)
    
    df = pd.concat([df,tdf,cdf],axis=1)
    df.to_csv('veri/tech.csv')
    # pdb.set_trace()
    # pprint(cinfo)
    # print df.tail(1)
    ###
    factor_results  = cat_boost_factor_check(df, target_days=['1d','3d','5d','10d','60d'])
    # factor_results  = cat_boost_factor_check(df, target_days=['5d'])
   
        
if __name__ == '__main__':    
    main()