import json
import talib 
from collections import OrderedDict

def load_ta_pat_map():
    return json.load(open('talib_pattern_name.json'))
TA_PATTERN_MAP = load_ta_pat_map()


def candle_analyse(df):
    '''
    input:OHLC dataframe
    '''
    cn_names = []
    for funcname in talib.get_function_groups()[ 'Pattern Recognition']:
        func = getattr(talib,funcname) 
        ohlc_data = func(df['open'],df['high'],df['low'],df['close'])
        cn_name = funcname[3:]        
        df[cn_name] = ohlc_data
        cn_names.append(cn_name)
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
            intro = the_info['intro']
            intro2 = the_info['intro2']
            cdl_info['data'][name] = {'figure':fig,'score':cdl_vlu,'cn_name':cn_name,'intro':intro,'intro2':intro2,'en_name':en_name}
    # print jsdump(cdl_info)
    return cdl_info,df
    
def boll_analyse(bl_upper,bl_middle,bl_lower):
    idx = 50.0/bl_middle[-1]
    u = talib.LINEARREG_ANGLE(bl_upper*idx, timeperiod=2)
    m = talib.LINEARREG_ANGLE(bl_middle*idx,timeperiod=2)    
    l = talib.LINEARREG_ANGLE(bl_lower*idx, timeperiod=2)
    if m[-1]>=0:
        res = ['UP']
    else:
        res = ['DOWN']
    if u[-1]-m[-1]>=0:
        res[0] += '-EXPAND'
    else:
        res[0] += '-SHRINK'
    res += ['mid_ang:%0.2f, up_ang:%0.2f, mid_prc:%0.2f'%(m[-1],u[-1]-m[-1] ,bl_middle[-1])]
    return res
 

def pivot_line(high,low,open,close, mode='classic'):
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
    
def tech_analyse( df):    
    '''
    input:OHLC dataframe
    '''
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    vol = df['volume'].values    
    ana_res = OrderedDict()
    
    bl_upper, bl_middle, bl_lower = talib.BBANDS(close)
    boll_analyse_res = boll_analyse(bl_upper, bl_middle, bl_lower )
    ##
    macd, macdsignal, macdhist =  talib.MACD(close)
    ##
    roc = talib.ROCR(close)
    ##
    slk,sld = talib.STOCH(high,low,close)
    slj = 3*slk-2*sld
    ##
    obv = talib.OBV(close,vol)
    ##
    sar = talib.SAREXT(high,low)
    ##
    rsi = talib.RSI(close)
    ##
    ema05  = talib.EMA(close,5)
    ema10  = talib.EMA(close,10)
    ema20  = talib.EMA(close,20)
    ema60  = talib.EMA(close,60)
    ema240 = talib.EMA(close,240)
    ##
    sma05  = talib.SMA(close,5)
    sma10  = talib.SMA(close,10)
    sma20  = talib.SMA(close,20)
    sma60  = talib.SMA(close,60)
    sma240 = talib.SMA(close,240)    
    ##
    atr14 = talib.ATR(high,low,close,timeperiod =14)
    atr28 = talib.ATR(high,low,close,timeperiod =28)
    ##
    pivot_point = map(lambda x:round(x[-1],2) , pivot_line(high,low,open,close) )    
    # name = ' '
    analyse_info = OrderedDict({'price':df['close'].values[-1]})
    
    ana_res['BOLL_Res'] =  boll_analyse_res
    # ana_res['BOLL'] = [bl_upper[-1],bl_middle[-1],bl_lower[-1] ]
    ana_res['MACD'] = round_float([ macd[-1],macdsignal[-1],macdhist[-1] ])
    ana_res['ROC'] = round_float([roc[-3],roc[-2],roc[-1]  ])
    ana_res['KDJ'] = round_float([slk[-1],sld[-1], slj[-1] ])
    ana_res['RSI'] = round_float([ rsi[-1] ])
    ana_res['OBV'] = round_float([ obv[-1] ])
    ana_res['SAR'] = round_float([ sar[-1] ])
    ana_res['EMA'] = round_float([ ema05[-1],ema10[-1],ema20[-1],ema60[-1],ema240[-1] ])
    ana_res['SMA'] = round_float([ sma05[-1],sma10[-1],sma20[-1],sma60[-1],sma240[-1] ])
    ana_res['VOL_Rate'] = round_float([vol[-1]*1.0/vol[-2]])
    ana_res['ATR14'] = round_float(list(atr14[-10::2]))
    ana_res['ATR28'] = round_float(list(atr28[-10::2]))
    ana_res['PIVOT'] = pivot_point
    
    analyse_info['data']=ana_res
    # pdb.set_trace()
    return analyse_info,df
    
  
def round_float(lst):
    return map(lambda x:'%0.2f'%x,lst)
 
def test():
    import tushare as ts
    import pdb
    df = ts.get_hist_data('002409')
    pdb.set_trace()
    candle_analyse(df)
    tech_analyse(df)
    
    
if __name__ == '__main__':
    test()