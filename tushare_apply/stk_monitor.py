#!coding:utf8
# import pdb

import sys
import tushare as ts
import pandas as pd
import talib 
import datetime
import time
import json
import pdb
from collections import OrderedDict
from matplotlib import pyplot as plt
from stock_latest_news import get_latest_news  

try:    
    import gevent
    from gevent import monkey
    from gevent.pool import Pool    
    monkey.patch_all()
    # print '[gevent ok]'
except:
    print '[Not Found gevent]'


pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format


def real_time_ticks(tick,info,flags,use_cache = False):
    fname = 'data/today_tick.%s.csv'%tick
    if not use_cache:
        try:
            print 'tushare call',tick
            df = ts.get_today_ticks(tick)
            # dt=datetime.datetime.now().strftime('%Y-%m-%d')
            # print dt
            # df = ts.get_tick_data(tick,date=dt,src='sn')
            df.index.name = 'id'
            df.to_csv(fname,encoding='utf8')
        except Exception as e:            
            print e.print_stack()
            traceback.print_exc()
            pass
    df = pd.read_csv(fname,encoding='utf8',index_col='id')
    df['volume'] = df['vol']    
    print ''
    print ''
    print tick
    print df.groupby('type').agg({'volume':'sum','price':'mean' })
    # print df.groupby('type').agg({'volume':'sum','price':'mean','change':'count'})
    # print str(df.groupby(['change']).agg({'volume':'sum','price':'mean'}))
    print df.corr()
    layout_dd = pd.crosstab(pd.cut(df.price,10),df.type)
    print layout_dd
    if 'graph' in flags:
        df[['price','vol']].plot(subplots=True)
        plt.show()
    
    # df['time'] = pd.to_datetime(df['time'].apply(lambda x:' '+x))
    vcut =  pd.cut(df['volume'],5)
    # ccut =  pd.cut(df['change'],5)    
    tcut =  pd.cut(df['time'],5)
    df['type'].astype('category')
    print pd.crosstab( vcut,df['type'])
    # print pd.crosstab( ccut,df['type'])
    # print pd.crosstab( ccut,vcut)
    print pd.crosstab( tcut,vcut)
    # print pd.crosstab( tcut,ccut)
    print pd.crosstab( tcut,df['type'])
    # print df.describe()
    # df3 = ts.get_hist_data(tick)
    # quote_df = ts.get_realtime_quotes(tick) 
    # quote_df =  ts.get_today_ticks()
    # print rdf.melt()
    
def realtime_list_ticks(tks,flags):
    if len(tks) == 0:
        return pd.DataFrame()
    info = {}
    rdf = ts.get_realtime_quotes(tks)    
    # rdf=  ts.get_today_all()
    # print rdf
    if rdf is None:
        return
    rdfc = rdf.loc[:,'code']
    # print rdfc
    rdf = rdf.apply(pd.to_numeric,errors='ignore')
    rdf.rename({'pre_close':'pclose'}, inplace=True, axis=1)
    rdf['code'] = rdfc
    cname = rdf.columns
    # cname[3]='price'
    # rdf.rename(cname,inplace=True)
    if 'fullname' in flags:
        rdf['name'] = rdf['name'].str.slice(0,4,2)
    else:
        rdf['name'] = rdf['name'].str.slice(0,10,1)
    
    rdf.index.name = 'id'
    r3,r2,r1,pivot,s1,s2,s3 = pivot_line(rdf['high'],rdf['low'],rdf['open'],rdf['pclose'])
    rdf.insert(0,'code',rdf.pop('code'))
    rdf.insert(1,'op_gp',(rdf['open']-rdf['pclose'])/(rdf['open'])*100)
    rdf.insert(2,'mx_up',(rdf['high']-rdf['open'])/(rdf['open'])*100)
    rdf.insert(3,'mx_dwn',(rdf['low']-rdf['open'])/(rdf['open'])*100)
    rdf.insert(4,'bunc',(rdf['price']-rdf['low'])/(rdf['high']-rdf['low'])*100)
    rdf.insert(5,'rate',(rdf['price']-rdf['pclose'])/(rdf['pclose'])*100)
    # rdf.insert(5,'r2',r2)
    rdf.insert(6,'price',rdf.pop('price'))
    rdf.insert(8,'pivot',pivot)
    rdf.insert(9,'r1',r1)
    rdf.insert(10,'s1',s1)
    # rdf.insert(10,'s2',s2)
    # rdf.insert(16,'name',rdf.pop('name'))
    # rdf.insert(6,'openrise',(rdf['price']-rdf['open'])/(rdf['open'])*100)
    # rdf.insert(7,'openrisevspclose',(rdf['price']-rdf['open'])/(rdf['pclose'])*100)

    print rdf.loc[:,:'amount'].sort_values(by='rate',ascending=False)
    
    for idx,row in rdf.iterrows():
        dc = dict(zip(row.index,row.values))
        dc['id'] = str(idx)
        info[dc['code']] = dc
        
    
    # fc=ts.forecast_data(2019,1)
    # print fc
    # ttdf = ts.get_today_ticks(tks[6])
    # print ttdf[ttdf.volume>=100].groupby(ttdf.type).count()
    # print ttdf[ttdf.volume>=100].groupby(ttdf.type).sum()
    return info


def jsdump(info, indent=None):
    return json.dumps(info, ensure_ascii=False, indent=indent).encode('gbk')    
    
def load_ta_pat_map():
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
    
def split_stocks(tks):
    ntks = OrderedDict()
    for k,v in tks.items():        
        ntks[k] = v.replace('   ',' ').replace('  ',' ').strip().replace(',',' ').split(' ')
    return ntks

def to_num(s):
    try:
        return int(s)
    except ValueError:
        return s

def line_cross(line1,line2):
    diff = line1 - line2

def boll_judge(bl_upper,bl_middle,bl_lower):
    idx = 50.0/bl_middle[-1]
    u = talib.LINEARREG_ANGLE(bl_upper*idx, timeperiod=2)
    m = talib.LINEARREG_ANGLE(bl_middle*idx,timeperiod=2)    
    l = talib.LINEARREG_ANGLE(bl_lower*idx, timeperiod=2)
    if m[-1]>=0:
        res = ['Up']
    else:
        res = ['Down']
    if u[-1]-m[-1]>=0:
        res += ['Expand']
    else:
        res += ['Shrink']
    res += ['mid_ang:%0.2f,updif_ang:%0.2f@mid_price:%0.2f'%(m[-1],u[-1]-m[-1] ,bl_middle[-1])]
    return res
  
def round2(lst):
    return map(lambda x:'%0.2f'%x,lst)
    
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
    
def tech_analyse(info,tk, df):    
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    vol = df['volume'].values    
    
    bl_upper, bl_middle, bl_lower = talib.BBANDS(close)
    boll_judge_res = boll_judge(bl_upper, bl_middle, bl_lower )
    
    macd, macdsignal, macdhist =  talib.MACD(close)
    roc = talib.ROCR(close)
    slk,sld = talib.STOCH(high,low,close)
    obv = talib.OBV(close,vol)
    sar = talib.SAREXT(high,low)
    slj = 3*slk-2*sld
    rsi = talib.RSI(close)
    ma05 = talib.SMA(close,5)
    ma10 = talib.SMA(close,10)
    ma20 = talib.SMA(close,20)
    ma240 = talib.SMA(close,240)
    atr14 = talib.ATR(high,low,close,timeperiod =14)
    atr28 = talib.ATR(high,low,close,timeperiod =28)
    pivot_point = map(lambda x:round(x[-1],2) , pivot_line(high,low,open,close) )
    name = info.get(tk,{}).get('name','')
    # name = ' '
    idx_info = OrderedDict({'code':tk,'name':name,'price':df['close'].values[-1],'data':{}})
    
    data = idx_info['data']
    data['BOLL_Res'] =  boll_judge_res
    # data['BOLL'] = [bl_upper[-1],bl_middle[-1],bl_lower[-1] ]
    data['MACD'] = round2([ macd[-1],macdsignal[-1],macdhist[-1] ])
    # data['ROC'] = [roc[-3],roc[-2],roc[-1] ]
    # data['KDJ'] = [slk[-1],sld[-1], slj[-1] ]
    # data['OBV'] = [ obv[-1] ]
    # data['SAR'] = [ sar[-1] ]
    data['MA'] = round2([ ma05[-1],ma10[-1],ma20[-1],ma240[-1] ])
    data['VOL_Rate'] = round2([vol[-1]*1.0/vol[-2]])
    data['ATR14'] = atr14[-1]
    data['ATR28'] = atr28[-1]
    data['PIVOT'] = pivot_point
    # pdb.set_trace()
    # data['RSI'] = [rsi[-1] ]
    return idx_info,df

def print_analyse_res(res):
    intro = {}
    for stock in res:
        if stock is None:
            continue
        
        if stock['tech'] != None:
            tech = stock['tech']
            print "[{0}:{1}] Price:{2}".format(tech['code'],tech['name'].encode('gbk'),tech['price'])
            for key,vlu in tech['data'].items():
                print ' [%s]'%key,jsdump(vlu)
            
        if stock['cdl'] != None:
            cdl = stock['cdl']
            cdl_ent_str = ','.join([u'[{}:{}]:{}{}'.format(info['score'],info['figure'],name,info['cn_name']) for name,info in cdl['data'].items()])
            for name,info in cdl['data'].items():
                intro[info['en_name']+info['cn_name']] = info['intro2']
            print " [CDL_Total:{0}]  {1}".format(cdl['cdl_total'], cdl_ent_str.encode('gbk'))
    for name,intro in intro.items():
        print u"[{}]:{}".format(name,intro).encode('gbk')

def add_delta_n(df):
    for i in [1,3,5,10,20,30,60,90]:
        df['delta_b_%02d'%i] = df['close'] - df.shift(i)['close']    
    for i in [1,3,5,10,20,30,60,90]:
        df['vol_delta_b_%02d'%i] = df['volume'] - df.shift(i)['volume']
    for i in [1,3,5,10,20,30,60,90]:
        df['delta_f_%02d'%i] = df.shift(-i)['close']  - df['close']
    for i in [1,3,5,10,20,30,60,90]:
        df['vol_delta_f_%02d'%i] = df.shift(-i)['volume'] - df['volume']
    return df
    
def get_one_ticker_k_data(tk,info,flags):    
    fname = './data/'+tk+'.csv'
    df = ts.get_k_data(tk)
    # add_delta_n(df)
    df.to_csv(fname,index='date')
    df = pd.read_csv(fname,index_col='date')
    # print df.shape
    if df.shape[0] == 0:
        return
    ## technical indicator
    tech_info,df = tech_analyse(info,tk, df)
    ## japanese candle pattern
    cdl_info,df = candle_analyse(df )
    # cdl_info = None
    df.to_csv(fname)    
    df['close'].plot(grid=True)
    return {'tech':tech_info,'cdl':cdl_info}
    
    
def cli_select_menu(dic, default_input=None, menu_width=5, column_width=25, opt_map = None):    
    idxmap = {}
    for i,key in enumerate(dic):
        idxmap[i+1] = key
        print ('(%s) %s'%(i+1,key)).ljust(column_width),
        if (i+1)%menu_width == 0:
            print ''
    print ''
    if default_input is None:
        this_input = raw_input('SEL>')
    else:
        this_input = default_input
    words = this_input.strip().replace(',',' ').replace('  ',' ').split(' ')
    flags = []
    if opt_map is None:
        opt_map = {'q':'quit','d':'detail','i':'pdb'
        ,'s':'onestock','n':'news'
        ,'r':'realtime','f':'fullname','g':'graph'}
    for k,v in opt_map.items():
        if k in words:
            flags.append(v)
            words.remove(k)    
    try:
        keys = [idxmap[int(word)] for word in words]     
        return keys, flags
    except Exception as e:
        print(e)
        return [], flags   

        
def interact_choose_ticks(mode):
    fname = 'stk_monitor.json'
    conf_tks = json.load(open(fname), object_pairs_hook=OrderedDict)
    conf_tks = split_stocks(conf_tks['ticks'])
    all = reduce(lambda x,y:x+y, conf_tks.values(),[])
    all = set(all)
    all.remove("")
    conf_tks['All'] = list(all)
    if '-d' in mode:
        input = '3'
        ticks,flags = cli_select_menu(conf_tks,input)        
    else:
        ticks,flags = cli_select_menu(conf_tks)
    #### selected ticks
    sel_tks=set()
    for id in ticks:
        sel_tks.update( conf_tks[id])
    sel_tks = list(sel_tks)
    #####
    print 'Input: %s, Ticks: %s'%(ticks,','.join(sel_tks)) 
    info = realtime_list_ticks(sel_tks,flags)
    time.sleep(3)
    if '-d' in mode or 'detail' in flags:
        input = 'y'
    elif 'realtime' in flags:
        # input = raw_input('[ShowDetailInfo?](y/n):')
        input = 'y'
    else:
        input = ''
    #####
    if input == 'y':
        the_ticks = sel_tks
    elif to_num(input) < len(sel_tks): 
        # pdb.set_trace()
        the_ticks = [ filter(lambda entry:entry[1]['id']==input, info.items())[0][1]['code'] ]
    elif unicode(input) in sel_tks: 
        the_ticks = [unicode(input)]   
    else:
        the_ticks = []
    #####
    return the_ticks, info, flags

  
def main_loop(mode):
    the_ticks, info, flags = interact_choose_ticks(mode)       
    # print the_ticks
    # print info
    exec_func = get_one_ticker_k_data
    if 'realtime' in flags :
        exec_func = real_time_ticks   
    elif 'onestock' in flags:
        exec_func = real_time_ticks
    elif 'news' in flags :
        df = get_latest_news()       
        print df.loc[:,['title','keywords','time']]
    elif 'quit' in flags:
        sys.exit()
        
    if not Pool:
        for tk in the_ticks:
            res = exec_func(tk,info)
    else:
        pool = Pool(8)
        jobs = []
        for tk in the_ticks:
            job = pool.spawn(exec_func,tk,info,flags)
            jobs.append(job)
        # pool.close()
        pool.join()
        # jobs = [gevent.spawn(get_one_ticker_k_data,tk,info,flags) for tk in the_tks]
        # gevent.joinall(jobs)
        res = [job.value for job in jobs]
    json.dump(res,open('result.json','w'),indent=2)
    print_analyse_res(res)
    if 'graph' in flags:
        plt.show()
        
    # raw_input("pause")
 
def test():
    ts.get_sz50s()
    ts.get_hs300s()
    ts.get_zz500s()
    ts.realtime_boxoffice()
    ts.get_latest_news()
    ts.get_notices(tk)
    ts.guba_sina()
    ts.get_cpi()
    ts.get_ppi()
    ts.get_stock_basics()
    ts.get_concept_classified()
    ts.get_money_supply()
    ts.get_gold_and_foreign_reserves()
    ts.top_list() #每日龙虎榜列表 
    ts.cap_tops()  #个股上榜统计
    ts.broker_tops()  #营业部上榜统计
    ts.inst_tops() 
    ts.inst_detail()
    
if __name__ == '__main__':    
    mode = sys.argv
    while 1:        
        main_loop(mode)