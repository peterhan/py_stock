import pdb
import sys
import tushare as ts
import pandas as pd
import talib 
import datetime
import json
from collections import OrderedDict
try:
    import gevent
    from gevent import monkey
except:
    print 'no gevent'
monkey.patch_all()

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format

def realtime_ticks(tks):
    info={}
    rdf=  ts.get_realtime_quotes(tks)
    # rdf=  ts.get_today_all()
    # print rdf
    rdfc=rdf.loc[:,'code']
    # print rdfc
    rdf = rdf.apply(pd.to_numeric,errors='ignore')
    rdf.rename({'pre_close':'pclose'}, inplace=True, axis=1)
    rdf['code']=rdfc
    cname = rdf.columns
    # cname[3]='price'
    # rdf.rename(cname,inplace=True)
    rdf.insert(0,'pre_code',rdf['code'])
    rdf.insert(1,'bounce',(rdf['price']-rdf['low'])/(rdf['high']-rdf['low'])*100)
    rdf.insert(2,'osc',(rdf['high']-rdf['low'])/(rdf['open'])*100)
    rdf.insert(3,'gap',(rdf['open']-rdf['pclose'])/(rdf['open'])*100)
    rdf.insert(4,'rate',(rdf['price']-rdf['pclose'])/(rdf['pclose'])*100)
    # rdf.insert(5,'rate2',(rdf['price']-rdf['open'])/(rdf['open'])*100)
    # rdf.insert(6,'rate3',(rdf['price']-rdf['open'])/(rdf['pclose'])*100)

    print rdf.loc[:,:'amount'].sort_values(by='rate',ascending=False)
    for idx,row in rdf.iterrows():
        dc = dict(zip(row.index,row.values))
        info[dc['code']] = dc
    # pdb.set_trace()
    # fc=ts.forecast_data(2019,1)
    # print fc
    # ttdf = ts.get_today_ticks(tks[6])
    # print ttdf[ttdf.volume>=100].groupby(ttdf.type).count()
    # print ttdf[ttdf.volume>=100].groupby(ttdf.type).sum()
    return info


def jsdump(info):
    return json.dumps(info,ensure_ascii=False).encode('gbk')    
    
def load_ta_pat_map():
    import json
    return json.load(open('talib_pattern_name.json'))


TA_PATTERN_MAP = load_ta_pat_map()
 
 
def candle_analyse(df):
    cn_names = []
    for funcname in talib.get_function_groups()[ 'Pattern Recognition']:
        func = getattr(talib,funcname) 
        ohlc_data = func(df['open'],df['high'],df['low'],df['close'])
        cn_name = funcname[3:]        
        df[cn_name] = ohlc_data
        cn_names.append(cn_name)
    total_cdl_score = df[cn_names].sum(axis=1)
    df['CDLScore'] =  total_cdl_score
    # pdb.set_trace()
    cdl_info = {'cdl_total' : '%s'% (total_cdl_score.values[-1]),'data':{} }
    last_cdlrow = df.iloc[-1]
    for name,cdl_vlu in last_cdlrow.iteritems():        
        if cdl_vlu!=0 and name in TA_PATTERN_MAP:
            the_info = TA_PATTERN_MAP[name]
            fig =  the_info['figure'].split(' ')[1]
            cn_name = the_info['name'].split(' ')[0]
            en_name = the_info['name'].split(' ')[1]
            intro = the_info['intro']
            intro2 = the_info['intro2']
            cdl_info['data'][name]={'figure':fig,'score':cdl_vlu,'cn_name':cn_name,'intro':intro,'intro2':intro2,'en_name':en_name}
    # print jsdump(cdl_info)
    return cdl_info,df
    
def split_stocks(tks):
    ntks = OrderedDict()
    for k,v in tks.items():        
        ntks[k] = v.strip().replace(',',' ').replace('  ',' ').split(' ')
    return ntks

def to_num(s):
    try:
        return int(s)
    except ValueError:
        return s
        
def tech_analyse(info,tk, df):    
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    vol = df['volume'].values    
    
    bl_upper, bl_middle, bl_lower = talib.BBANDS(close,timeperiod=15, nbdevup=1, nbdevdn=1, matype=0)
    u = talib.LINEARREG_ANGLE(bl_upper, timeperiod=2)
    m = talib.LINEARREG_ANGLE(bl_middle,timeperiod=2)
    l = talib.LINEARREG_ANGLE(bl_lower, timeperiod=2)
    print 'Boll',[u[-1],m[-1],l[-1]]
    macd, macdsignal, macdhist =  talib.MACD(close,fastperiod=6, slowperiod=12, signalperiod=9)
    roc = talib.ROCR(close)
    slk,sld = talib.STOCH(high,low,close)
    obv  = talib.OBV(close,vol)
    sar  = talib.SAREXT(high,low)
    slj = 3*slk-2*sld
    rsi = talib.RSI(close)
    
    name = info.get(tk,{}).get('name','')
    # name = ' '
    idx_info = {'code':tk,'name':name,'price':df['close'].values[-1],'data':{}}         
    # pdb.set_trace()  
    data = idx_info['data']
    data['BOLL'] = [bl_upper[-1],bl_middle[-1],bl_lower[-1] ]
    data['MACD'] = [ macd[-1],macdsignal[-1],macdhist[-1] ]
    data['ROC'] = [roc[-3],roc[-2],roc[-1] ]
    data['KDJ'] = [slk[-1],sld[-1], slj[-1] ]
    data['OBV'] = [ obv[-1] ]
    data['SAR'] = [ sar[-1] ]
    data['VOL_Rate'] = [vol[-1]*1.0/vol[-2] ]
    data['RSI'] = [rsi[-1] ]
    return idx_info,df
    
def add_delta_n(df):
    for i in [1,3,5,10,20,30,60,90]:
        df['delta_b_%02d'%i] = df['close'] - df.shift(i)['close']    
    for i in [1,3,5,10,20,30,60,90]:
        df['vol_delta_b_%02d'%i] = df['volume'] - df.shift(i)['volume']
    for i in [1,3,5,10,20,30,60,90]:
        df['delta_f_%02d'%i] =  df.shift(-i)['close']  - df['close']
    for i in [1,3,5,10,20,30,60,90]:
        df['vol_delta_f_%02d'%i] =  df.shift(-i)['volume'] - df['volume']
    return df
    
def focus_tick_k_data(tk,info):    
    fname='./data/'+tk+'.csv'
    df = ts.get_k_data(tk)
    add_delta_n(df)
    df.to_csv(fname,index='date')
    df = pd.read_csv(fname,index_col='date')
    # print df.shape
    if df.shape[0]==0:
        return
    ## technical indicator
    idx_info,df = tech_analyse(info,tk, df)
    ## japanese candle pattern
    cdl_info,df = candle_analyse(df )
    # cdl_info = None
    df.to_csv(fname)
    return {'idx':idx_info,'cdl':cdl_info}
    
    
def cli_select_keys(dic, input=None):
    idxmap = {}
    for i,key in enumerate(dic):
        idxmap[i+1]=key
        print ('(%s) %s'%(i+1,key)).ljust(25),
        if (i+1)%4==0:
            print ''
    print ''
    if input is None:
        res = raw_input('SEL>')
    else:
        res = input
    res_arr = res.replace(',',' ').split(' ')
    if res == ':q':
        sys.exit()
    try:
        keys = [idxmap[int(i)] for i in res_arr]     
        return keys    
    except:
        return []
    

        
def print_analyse_res(res):
    intro = {}
    for stock in res:
        if stock is None:
            continue
        
        if stock['idx'] != None:
            idx = stock['idx']
            print "[{0}:{1}] Price:{2}".format(idx['code'],idx['name'].encode('gbk'),idx['price'])
            print jsdump(idx['data'])
            
        if stock['cdl'] != None:
            cdl = stock['cdl']
            cdl_ent_str=','.join([u'[{}:{}]:{}{}'.format(info['score'],info['figure'],name,info['cn_name']) for name,info in cdl['data'].items()])
            intro[info['en_name']+info['cn_name']] = info['intro2']
            print "[CDL:{0}]; {1}".format(cdl['cdl_total'], cdl_ent_str.encode('gbk'))
    for name,intro in intro.items():
        print u"[{}]:{}".format(name,intro).encode('gbk')

def load_ticks(mode):
    fname = 'ticks.json'
    tks = json.load(open(fname), object_pairs_hook=OrderedDict)
    tks = split_stocks(tks['ticks'])
    all = reduce(lambda x,y:x+y, tks.values(),[])
    all = set(all)
    all.remove("")
    tks['All'] = list(all)
    if '-d' in mode:
        input = '3'
        keys  = cli_select_keys(tks,input)        
    else:
        keys = cli_select_keys(tks)
    the_tks=set()
    for id in keys:
        the_tks.update( tks[id])
    the_tks=list(the_tks)
    ####
    print '[%s]ticks: %s'%(keys,','.join(the_tks)) 
    info = realtime_ticks(the_tks)
    if '-d' in mode:
        input = 'y'
    else:
        input = raw_input('[ShowDetailInfo?](y/n):')
    ##############
    if input== 'y':
        pass
    elif to_num(input) < len(the_tks): 
        the_tks = [the_tks[int(input)]]
    elif unicode(input)  in the_tks: 
        the_tks = [unicode(input)]   
    else:
        the_tks = []
    return the_tks, info
    
def main_loop(mode):
    the_tks, info = load_ticks(mode)
       
    # print the_tks
    # print info
    if not gevent:
        for tk in the_tks:
            res = focus_tick_k_data(tk,info)
    else:
        jobs = [gevent.spawn(focus_tick_k_data,tk,info) for tk in the_tks]
        gevent.joinall(jobs)
        res = [job.value for job in jobs]
    json.dump(res,open('result.json','w'),indent=2)
    print_analyse_res(res)
        
       
        
    # raw_input("pause")
 
def test():
    ts.get_sz50s()
    ts.get_hs300s()
    ts.get_zz500s()

if __name__ == '__main__':    
    mode = sys.argv
    while 1:
        main_loop(mode)