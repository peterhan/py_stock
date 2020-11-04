import json
import talib 
import pandas as pd
import pdb
from collections import OrderedDict
from matplotlib import pyplot as plt


def load_ta_pat_map():
    return json.load(open('talib_pattern_name.json'))
TA_PATTERN_MAP = load_ta_pat_map()


def candle_analyse(df):
    '''
    input:OHLC dataframe
    '''
    cn_names = []
    ## calc all candle score
    for funcname in talib.get_function_groups()[ 'Pattern Recognition']:
        func = getattr(talib,funcname) 
        score_data = func(df['open'],df['high'],df['low'],df['close'])
        cn_name = funcname[3:]        
        df[cn_name] = score_data
        cn_names.append(cn_name)
    
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
            res = 'DOWN'
        if (u_ag - m_ag) >= 0:
            res += '-EXPAND'
        else:
            res += '-SHRINK'
        return res
    df['boll_stage'] = df.apply(boll_judge,axis=1)
    row = df.iloc[-1]
    res = [row['boll_stage']]
    res += ['ANG[MID:%0.2f, UP:%0.2f], MID_PRC:%0.2f'%(mag[-1], uag[-1]-mag[-1], boll_mid[-1])]
    res += ['UP:%0.2f, MID:%0.2f, LOW:%0.2f'%(boll_up[-1],boll_mid[-1],boll_low[-1])]
    return res,df
 
def value_range_judge(vlu,up_down,up_down_mid_name): 
    if vlu>=up_down[0]:
        return up_down_mid_name[0]
    elif vlu<=up_down[1]:
        return up_down_mid_name[1]
    else:
        return up_down_mid_name[2]    

def cross_judge(row):    
    # pdb.set_trace()
    fast_ag = row['fast_ag']
    slow_ag = row['slow_ag']
    ag_dif = fast_ag - slow_ag
    value_gap = row['fast_line'] - row['slow_line']
    if fast_ag>0 and slow_ag>0:
        res='AftGoldX'
    elif fast_ag>0  and slow_ag<0:
        res='TrnBefGoldX'
    elif ag_dif>0 and slow_ag<0:
        res='CovBefGoldX'
    elif fast_ag<0 and slow_ag<0:
        res='AftDeathX'
    elif fast_ag<0  and slow_ag>0:
        res='TrnBefDeathX'
    elif  ag_dif<0 and slow_ag>0:
        res='CovBefDeathX'
    else:
        res='Unknown'
    return res
    
def get_crossx_type(fast_line,slow_line):
    fast_ag = get_angle(fast_line, 2)
    slow_ag = get_angle(slow_line, 2)
    df=pd.DataFrame({'fast_line':fast_line,'slow_line':slow_line,'fast_ag':fast_ag,'slow_ag':slow_ag})
    df['cross_stage'] = df.apply(cross_judge,axis=1)#,result_type='expand'    
    # print edf
    return df
    
def get_angle(ss,p=2):
    return talib.LINEARREG_ANGLE(ss, timeperiod=p)    
    
def macd_analyse(ohlcv,period=10):
    dif, dea, hist =  talib.MACD(ohlcv['close'],period)    
    df = pd.DataFrame({'macd_dif': dif, 'macd_dea':dea, 'macd_hist':hist })    
    # pdb.set_trace() 
    res = []    
    df =  get_crossx_type(dif,dea)
    df = df.rename({'fast_line':'dif','slow_line':'dea','cross_stage':'macd_stage','fast_ag':'dif_ag','slow_ag':'dea_ag'},axis=1)
    row = df.iloc[-1]         
    res += ['%s: ANG[IF:%0.2f, EA:%0.2f]'%(row['macd_stage'],row['dif_ag'],row['dea_ag'])]
    res += ['DIF:%0.2f, DEA:%0.2f, MACD:%0.2f'%(dif[-1],dea[-1],hist[-1]*2)]   
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
        return value_range_judge( row['roc'] ,[100,-100],['OverBrought','OverSell','MID'])
    df['roc_stage'] =  df.apply(roc_row, axis=1)
    # pdb.set_trace()
    row = df.iloc[-1]
    res_info = row['roc_stage']+', '+'CCI: %0.2f, ANG:%02.f'%(row['roc'],row['roc_ag'])
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
            sw += 'TRND-DVRG'
        elif (row['k_ag']>0 and row['k_aag']<0) or \
             (row['k_ag']<0 and row['k_aag']>0) or \
             (row['d_ag']>0 and row['d_aag']<0) or \
             (row['d_ag']<0 and row['d_aag']>0):
            sw += 'TRND-TURN'
        else:
            sw += 'TRND-NORM'
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

def ma_analyse(ohlcv,period=10):    
    close = ohlcv['close']
    ma = OrderedDict()
    # cycles = [5,10,20,40,60,120,240]
    cycles = [5,10,20,40]
    for cyc in cycles:
        ma['EMA%s'%cyc]  = talib.EMA(close,cyc)
        ma['SMA%s'%cyc]  = talib.SMA(close,cyc)
    df = pd.DataFrame(ma)
    def ma_judge(row):
        res = []
        for cyc in cycles:
            ema = row['EMA%s'%cyc]
            sma = row['SMA%s'%cyc]
            if ema>sma:
                s= '%s:UP'%cyc
            else:
                s='%s:DN'%cyc
            res.append(s)
        return ','.join(res)
    df['ma_stage'] = df.apply(ma_judge,axis=1)
    row = df.iloc[-1]
    def ma_str(row,typ):
        res = []
        for cyc in cycles:            
            k = '%sMA%s'%(typ,cyc)
            v = row[k]
            res.append('%s:%0.2f'%(k,v))
        return ', '.join(res)
    res_info = [row['ma_stage'], ma_str(row,'E'), ma_str(row,'S')]
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
    ohlcv= {'open':open,'high':high,'low':low,'close':close,'vol':vol}
    
    ana_res = OrderedDict()
    
    def pd_concat(df1,df2):
        return pd.concat([df1,df2.set_index(df1.index)],axis=1)
    
    ## MA
    ma_anly_res,mdf = ma_analyse(ohlcv)
    df= pd_concat(df,mdf)
    ana_res['ES-MA'] = ma_anly_res
    
    ## MACD
    macd_anly_res,mdf = macd_analyse(ohlcv)
    df= pd_concat(df,mdf)
    ana_res['MACD'] = macd_anly_res

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
    
    ## ROC
    roc_anly_res,rdf = roc_analyse(ohlcv)
    df= pd_concat(df,rdf)
    ana_res['ROC'] = roc_anly_res
    
    tsf_res =  'Forcast: %0.2f'%talib.TSF(ohlcv['close'])[-1]
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
    analyse_info = OrderedDict({'price':df['close'].values[-1]})
    
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
    
ECODE='gbk'    
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
    print ''
    for name,intro in intro.items():
        pstr+= u"\n  [EXPLAIN:{}]:{}".format(name,intro).encode(ECODE)  
    return pstr

 
def test():
    import tushare as ts
    
    def pprint(info, indent=None):
        print json.dumps(info, ensure_ascii=False, indent=2).encode('gbk')
    
    # df = ts.get_hist_data('601865')
    # df = ts.get_hist_data('600438')
    # df.to_csv('temp.csv')
    df=pd.read_csv('temp.csv')
    df = df.sort_values('date')
    tinfo,df = tech_analyse(df)
    pprint(tinfo)
    # df.to_csv('temp_res.csv')
    # pdb.set_trace()
    # cinfo,df = candle_analyse(df)
    # pprint(cinfo)
    # print df.tail(1)
    ###
    verify_indicator(df)
    
def verify_indicator(df):
    
    adf = df[['turnover','cci_stage','ma_stage','macd_stage','boll_stage','rsi_stage','kdj_stage','rsi','dif_ag','rsi_ag','dif','k_ag','j_ag','d_ag','dea']].copy()
    adf['p_change_1d'] = df['p_change'].shift(-1)
    adf['p_change_3d'] = df['p_change'].shift(-3)
    adf['p_change_5d'] = df['p_change'].shift(-5)
    adf['p_change_7d'] = df['p_change'].shift(-7)
    adf['p_change_10d'] = df['p_change'].shift(-10)
    adf['p_change_15d'] = df['p_change'].shift(-15)
    # adf['p_change_20d'] = df['p_change'].shift(-20)
    # adf['p_change_30d'] = df['p_change'].shift(-30)
    # print adf.corr()
    offset = 9
    print adf.groupby('ma_stage').mean().iloc[:,offset:]
    print adf.groupby('macd_stage').mean().iloc[:,offset:]   
    print adf.groupby('boll_stage').mean().iloc[:,offset:]   
    print adf.groupby('rsi_stage' ).mean().iloc[:,offset:]   
    print adf.groupby('kdj_stage' ).mean().iloc[:,offset:]   
    print adf.groupby('cci_stage' ).mean().iloc[:,offset:]   
    # pdb.set_trace()
    
if __name__ == '__main__':
    pd.set_option('display.max_columns',80)
    test()