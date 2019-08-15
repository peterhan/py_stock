import pdb
import sys
import tushare as ts
import pandas as pd
import talib as talib
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
    
def load_ta_pat_map():
    import json
    return json.load(open('talib_pattern_name.json'))
 
tam = load_ta_pat_map()
 
def process_cdl(row):
    stmts=[]
    for name,vlu in row.iteritems():
        # pdb.set_trace()
        if vlu!=0 and name in tam:
            stmts.append( '[%s: %s][%s]'%(str(vlu),tam[name]['figure'],tam[name]['name']) )
            # sts.append( tam[name]['intro2'])
    print '\t'.join(stmts).encode('gbk')
    return stmts
    
    
def focus_tick(tk,info):    
    fname='./data/'+tk+'.csv'
    df = ts.get_k_data(tk)
    df.to_csv(fname)
    df = pd.read_csv(fname)
    # print df.shape
    if df.shape[0]==0:
        return
    closed = df['close'].values
    high = df['high'].values
    low = df['low'].values
    vol = df['volume'].values
    
    bl_upper, bl_middle, bl_lower = talib.BBANDS(closed,matype=talib.MA_Type.T3)
    macd, macdsignal, macdhist =  talib.MACD(closed)
    roc = talib.ROCR(closed)
    slk,sld = talib.STOCH(high,low,closed)
    obv  = talib.OBV(closed,vol)
    sar  = talib.SAREXT(high,low)
    slj = 3*slk-2*sld
    print ''    
    name = info.get(tk,{}).get('name','')
    # name = ' '
    info = []
    
    info.append( 'code:%s, name:%s, price:%0.3f '%(tk,name,df['close'].values[-1]))
    
    # pdb.set_trace()
    
    idx_info = []
    idx_info.append( '[BOLL]: %0.2f,%0.2f,%0.2f '%(bl_upper[-1],bl_middle[-1],bl_lower[-1]) )
    idx_info.append( '[MACD]: %0.2f,%0.2f,%0.2f '%(macd[-1],macdsignal[-1],macdhist[-1]) )
    idx_info.append( '[VOL_Rate]: %0.2f'%( vol[-1]*1.0/vol[-2] ) )
    idx_info.append( '[ROC]: %0.2f,%0.2f,%0.2f '%(roc[-3],roc[-2],roc[-1]))
    idx_info.append( '[KDJ]: %0.2f,%0.2f,%0.2f'%( slk[-1],sld[-1], slj[-1]) )
    idx_info.append( '[OBV]: %0.2f'%( obv[-1] ) )
    idx_info.append( '[SAR]: %0.2f'%( sar[-1] ) )
    
    cnames = []
    for funcname in talib.get_function_groups()[ 'Pattern Recognition']:
        func = getattr(talib,funcname) 
        res_vlu = func(df['open'],df['high'],df['low'],df['close'])
        cname = funcname[3:]        
        df[cname]=res_vlu
        cnames.append(cname)
    df['CDLScore']=df[cnames].sum(axis=1)    
    idx_info.insert(0,'[CDLScore]:%s'% df.iloc[-1,-1])
    print '  '.join(info).encode('gbk')
    print '  '.join(idx_info).encode('gbk')
    # print df.iloc[-1]
    # pdb.set_trace()
    stmts = process_cdl(df.iloc[-1])
    df.to_csv(fname)
    return info,idx_info,stmts
    
    
def cli_select_keys(dic, input=None):
    idxmap = {}
    for i,key in enumerate(dic):
        idxmap[i+1]=key
        print ('(%s) %s'%(i+1,key)).ljust(20),
        if (i+1)%4==0:
            print ''
    print ''
    if input is None:
        res = raw_input('SEL>')
    else:
        res = input
    res_arr = res.replace(',',' ').split(' ')
    if res == ':q':
        system.exit()
    try:
        keys = [idxmap[int(i)] for i in res_arr]     
        return keys    
    except:
        return []
    
def split_stocks(tks):
    ntks = OrderedDict()
    for k,v in tks.items():
        ntks[k] = v.replace(',',' ').replace('  ',' ').split(' ')
    return ntks

def num(s):
    try:
        return int(s)
    except ValueError:
        return s

def main_loop(mode):
    fname = 'ticks.json'
    tks = json.load(open(fname))
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
    for id in keys:
        ttks = tks[id]
        print '[%s]ticks: %s'%(id,','.join(ttks))
        info = realtime_ticks(ttks)
        # print ttks
        # print info
        if '-d' in mode:
            flag = 'y'
        else:
            flag = raw_input('[ShowFocusInfo?](y/n):')
            
        if flag== 'y':
            if not gevent:
                for tk in ttks:
                    res = focus_tick(tk,info)
            else:
                jobs = [gevent.spawn(focus_tick,tk,info) for tk in ttks]
                gevent.joinall(jobs)
                # print [job.value for job in jobs]
        elif num(flag) < len(ttks): 
            focus_tick(ttks[int(flag)],info)
        elif unicode(flag)  in ttks: 
            focus_tick(unicode(flag),info)
            
        # print json.dumps(info,ensure_ascii=False).encode('gbk')
        print ''
    # raw_input("pause")
 
def test():
    ts.get_sz50s()
    ts.get_hs300s()
    ts.get_zz500s()

if __name__ == '__main__':    
    mode = sys.argv
    while 1:
        main_loop(mode)