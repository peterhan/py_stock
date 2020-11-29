#!coding:utf8
import sys
import tushare as ts
import pandas as pd
import talib 
import datetime
import time
import json
import pdb
import traceback
from collections import OrderedDict
from matplotlib import pyplot as plt
from tushare_patch import get_latest_news,get_today_ticks
from tech_analyse import tech_analyse,candle_analyse,pivot_line,analyse_res_to_str,cat_boost_factor_check

try:    
    import gevent
    from gevent import monkey
    from gevent.pool import Pool    
    monkey.patch_all()
    # print '[gevent ok]'
except:
    print '[Not Found gevent]'

FNAME_PAT_RT = 'data/realtime.%s.csv'
FNAME_PAT_HIST = 'data/hist.%s.csv'

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format

def get_mkt(tks):
    if tks[0] in ('0','3'):
        return '0'
    if tks[0] in ('6','5'):
        return '1'

def _random(n=13):
    from random import randint
    start = 10**(n-1)
    end = (10**n)-1
    return str(randint(start, end))
    

def real_time_ticks(tick,info,flags,use_cache = False):
    fname = FNAME_PAT_RT%tick
    if not use_cache:
        try:
            print '[tushare call]',tick
            df = get_today_ticks(tick,mkt =get_mkt(tick))
            # dt=datetime.datetime.now().strftime('%Y-%m-%d')
            # print dt
            # df = ts.get_tick_data(tick,date=dt,src='sn')
            df.index.name = 'id'
            df.to_csv(fname,encoding='utf8')
        except Exception as e:
            traceback.print_exc()
            pass
    df = pd.read_csv(fname,encoding='utf8',index_col='id')
    df['time_int'] = df['time']
    df['time'] = df['time'].apply(lambda x:'%06d'%x)
    df['volume'] = df['vol']    
    df['amount'] = df['price'] * df['vol']
    df['hour'] = df['time'].str[:2]
    info_t = info[tick]
    print ''
    print ''
    print '[%s][%s]'%(tick,info_t['name'])
    
    print df.groupby('type').agg({'volume':'sum','price':'mean' })
    # print df.groupby('type').agg({'volume':'sum','price':'mean','change':'count'})
    # print str(df.groupby(['change']).agg({'volume':'sum','price':'mean'}))
    
    # print df.corr()
    layout_dd = pd.crosstab(pd.cut(df.price,10),df.type)
    print layout_dd
    
    # df['time'] = pd.to_datetime(df['time'].apply(lambda x:' '+x))
    vcut =  pd.cut(df['volume'],5)
    # ccut =  pd.cut(df['change'],5)    
    tcut =  pd.cut(df['time_int'],5)
    # df['type'].astype('category')
    print pd.crosstab( vcut,df['type'])
    print df.groupby(['hour','type']).sum()['amount']
    #print pd.crosstab(df['time'].str[0:2],df['type'])
    # print pd.crosstab( ccut,df['type'])
    # print pd.crosstab( ccut,vcut)
    # print pd.crosstab( tcut,vcut)
    # print pd.crosstab( tcut,ccut)
    # print pd.crosstab( tcut,df['type'])
    # print df.describe()
    # df3 = ts.get_hist_data(tick)
    # quote_df = ts.get_realtime_quotes(tick) 
    # quote_df =  ts.get_today_ticks()
    # print rdf.melt()
    if 'pdb' in flags:
        pdb.set_trace()
    if 'graph' in flags:
        df.pop('time')
        df.pop('vol')
        df.plot(subplots=True,title=tick)
        plt.show()
        
    if 'emd' in flags:
        from stock_emd import emd_plot
        emd_res = emd_plot(df['price'])        
    return {'code':tick,'info':info[tick],'tech':{'price':'','data':{}}}
    
def summary_list_ticks(tks,flags):
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
    r3,r2,r1,pivot,s1,s2,s3 = pivot_line(rdf['open'],rdf['high'],rdf['low'],rdf['price'])
    rdf.insert(0,'code',rdf.pop('code'))
    rdf.insert(1,'op_gp',(rdf['open']-rdf['pclose'])/(rdf['pclose'])*100)
    rdf.insert(2,'mx_up',(rdf['high']-rdf['pclose'])/(rdf['pclose'])*100)
    rdf.insert(3,'mx_dn',(rdf['low']-rdf['pclose'])/(rdf['pclose'])*100)
    rdf.insert(4,'bunce',(rdf['price']-rdf['low'])/(rdf['high']-rdf['low'])*100)
    rdf.insert(5,'rate',(rdf['price']-rdf['pclose'])/(rdf['pclose'])*100)
    # rdf.insert(5,'r2',r2)
    rdf.insert(6,'price',rdf.pop('price'))
    rdf.insert(8,'pivot',pivot)
    rdf.insert(9,'r1',r1)
    rdf.insert(10,'s1',s1)
    rdf.insert(11,'amount',rdf.pop('amount')/100000000.0)
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
    
def get_one_ticker_k_data(tick,info,flags):    
    fname =  FNAME_PAT_HIST%tick
    df = ts.get_k_data(tick)
    # add_delta_n(df)
    df.to_csv(fname,index='date')
    df = pd.read_csv(fname,index_col='date')
    df['date'] = df.index
    # print df.shape
    if df.shape[0] == 0:
        return
    ## technical indicator
    tech_info,tdf = tech_analyse(df)
    ## japanese candle pattern
    cdl_info,cdf = candle_analyse(df)
    df = pd.concat([df,tdf,cdf],axis=1)
    if 'cat' in flags:
        cat_boost_factor_check(df)
    # cdl_info = None
    df.to_csv(fname)
    if 'emd' in flags:
        from stock_emd import emd_plot
        emd_res = emd_plot(df['close'])  
    return {'code':tick,'info':info[tick]
        ,'tech':tech_info,'cdl':cdl_info}

 

def cli_select_menu(select_dic, default_input=None, menu_width=5, column_width=22, opt_map = None):    
    select_map = {}
    flags = set()
    for i,key in enumerate(select_dic):
        select_map[i+1] = key
        print ('(%s) %s'%(i+1,key)).ljust(column_width),
        if (i+1)%menu_width == 0:
            print ''
    print ''
    if default_input is None:
        this_input = raw_input('SEL>')
    else:
        this_input = default_input
    words = this_input.strip().replace(',',' ').replace('  ',' ').split(' ')    
    if opt_map is None:
        opt_map = {'q':'quit','d':'detail','i':'pdb'
        ,'s':'onestock','n':'news'
        ,'top':'top','inst':'inst'
        ,'r':'realtime','f':'fullname','g':'graph'
        ,'u':'us','z':'zh','e':'emd','c':'cat'
        }
    
    for k,v in opt_map.items():
        if k in words:
            flags.add(v)
            words.remove(k)    
          
    try:
        selected_keys = []
        for word in words:
            if len(word)==0:
                continue
            if len(word)<=3 and word.isdigit():
                selected_keys.append(select_map[int(word)]) 
            else:
                selected_keys.append(word)
        return selected_keys, flags
    except Exception as e:
        print(e)
        return [], flags   

        
def interact_choose_ticks(mode):
    fname = 'stk_monitor.v01.json'
    conf_tks = json.load(open(fname), object_pairs_hook=OrderedDict)
    conf_tks = split_stocks(conf_tks['cn-ticks'])
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
        if id in conf_tks:
            sel_tks.update( conf_tks[id])
        else:
            sel_tks.add( id)
    sel_tks = list(sel_tks)
    #####
    print 'Input: %s, Ticks: %s'%(ticks,','.join(sel_tks)) 
    info = summary_list_ticks(sel_tks,flags)
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

  
def cn_main_loop(mode):
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
    elif 'top' in flags:
        df = ts.top_list()       
        print df.sort_values('amount',ascending=False)
    elif 'inst' in flags:
        df = ts.inst_tops()
        print df.sort_values('net',ascending=False)
        raw_input('pause')
        df = ts.inst_detail()
        print df.sort_values('bamount',ascending=False)
    elif 'quit' in flags:
        sys.exit()
      
    if not Pool:
        for tk in the_ticks:
            result = exec_func(tk,info)
    else:
        pool = Pool(32)
        jobs = []
        for tk in the_ticks:
            job = pool.spawn(exec_func,tk,info,flags)
            jobs.append(job)
        # pool.close()
        pool.join()
        # jobs = [gevent.spawn(get_one_ticker_k_data,tk,info,flags) for tk in the_tks]
        # gevent.joinall(jobs)
        result = [job.value for job in jobs]
    
    ## 读取分析结果
    fname = 'result.%s.json'%exec_func.func_name
    # print fname
    json.dump(result,open(fname,'w'),indent=2)
    print '\n\n'+analyse_res_to_str(result)+'\n'
    
    if 'graph' in flags and exec_func.func_name=='get_one_ticker_k_data':
        cols = len(result)        
        fig, ax = plt.subplots(nrows=3, ncols=cols, sharex=False)
        for i,onestk in enumerate(result):
            tick = onestk['code']
            name = onestk['info'].get('name')
            fname = FNAME_PAT_HIST%tick
            df = pd.read_csv(fname,encoding='utf8',index_col='date')
            df = df[-50:]
            title = '%s'%(tick)
            df['atr']=talib.ATR(df['high'],df['low'],df['close'])
            df['sma10']=talib.SMA(df['close'],10)
            df['ema10']=talib.EMA(df['close'],10)
            df['ema_dif']=df['ema10']-df['sma10']
            if cols>1:
                aax=[ax[0,i],ax[1,i],ax[2,i]]
            else:
                aax=[ax[0],ax[1],ax[2]]
            df[['close','sma10','ema10']].plot(title=title,ax = aax[0])
            df[['ema_dif']].plot(title=title,ax = aax[1])
            df[['volume']].plot(title=title,ax = aax[2])
        plt.show()
    return flags
    
 
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
    ts.inst_tops() # 获取机构席位追踪统计数据
    ts.inst_detail() 
    
if __name__ == '__main__':    
    mode = sys.argv
    main_loop = cn_main_loop
    from stk_us_monitor import us_main_loop   
    flags = set()
    while 1:
        # print 'MENU_FLAG:',flags
        if 'us' in flags:            
            main_loop = us_main_loop
        if 'zh' in flags:        
            main_loop = cn_main_loop  
        try:
            flags = main_loop(mode)
        except Exception as e:
            traceback.print_exc()