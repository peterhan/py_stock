#!coding:utf8
import os
import json
import socket
import traceback,pdb
import yfinance as yf
import yfinance_cache

try:    
    import gevent
    from gevent import monkey
    from gevent.pool import Pool    
    monkey.patch_all()
    # Pool = None
    print '[Gevent ok]'
except:    
    print '[Not Found gevent]'

YFINFO_CACHE = {}
YFCACHE_FNAME = 'yf_info_cache.json'

def check_socket(ip,port):
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (ip,port)
    result_of_check = a_socket.connect_ex(location)
    return result_of_check==0

def yfinance_cache(ticks,use_cache=True):
    global YFINFO_CACHE,YFCACHE_FNAME
    if not os.path.exists(YFCACHE_FNAME):
        json.dump({},open(YFCACHE_FNAME,'w'))
    if len(YFINFO_CACHE)==0:
        YFINFO_CACHE = json.load(open(YFCACHE_FNAME))
    info_dic = {}
    need_update = set()
    for tick in ticks:
        if tick.strip()=='':
            continue
        if tick in YFINFO_CACHE and use_cache:
            # print 'use cache:',tick
            info_dic[tick] = YFINFO_CACHE[tick]
        else:
            info_dic[tick]={}
            #need_update.add(tick)
    ## check proxy
    proxy=None
    if check_socket('127.0.0.1',7890):
        print 'use proxy'
        proxy={'https':'http://127.0.0.1:7890','http':'http://127.0.0.1:7890' }
        
    ## get one tick info
    def get_one_data(tk):
        info =  yf.Ticker(tk).get_info(proxy = proxy)
        print 'basic_info_get:%s'%tk
        return tk,info
    if len(need_update)>0:
        print '[yfinance info need update]',need_update
    ## loop get info
    results = []
    if not Pool:
        for tk in need_update:
            results = get_one_data(tk)
    else:
        pool = Pool(2)
        jobs = []
        for tk in need_update:
            job = pool.spawn(get_one_data,tk,)
            jobs.append(job)
        pool.join()
        results = [job.value for job in jobs]        
    
    ## make return/cache data
    if len(results)>0:
        #print results
        for tick,info in results:
            print info
            if len(info)==0:
                print 'skip:',tick
                continue
            YFINFO_CACHE[tick] = info
            info_dic[tick] = info
        json.dump(YFINFO_CACHE,open(YFCACHE_FNAME,'w'),indent=2)
    return info_dic
 
def load_cache(fname,use_cache=True):
    import ConfigParser
    from collections import OrderedDict
    conf  = ConfigParser.ConfigParser()
    conf.readfp(open(fname))
    conf_tks = OrderedDict(conf.items('us-ticks'))
    ticks = set(['xasdf'])
    for k,v in conf_tks.items():
        # print k,':',v
        ticks.update(v.replace('  ','').split(' '))
    yfinance_cache([])
    print 'Not_In_ConfigTicks:', ' '.join(set(YFINFO_CACHE.keys())-ticks)
    print 'Total Ticks:',len(ticks)    
    try:
        info = yfinance_cache(ticks,use_cache)
        for k,v in info.items():
            print '[%s]'%k
            print v.get('longBusinessSummary','No_Summary').encode('gbk','ignore')
    except:
        traceback.print_exc()    
    
if __name__ == '__main__':
    load_cache('stk_console.v01.ini')
        