#!coding:utf8
import os
import json
import gzip
import socket
import traceback,pdb
import yfinance as yf
import yfinance_cache

try:    
    import gevent
    from gevent import monkey
    from gevent.pool import Pool    
    monkey.patch_all()
    # print '[gevent ok]'
except:
    print '[Not Found gevent]'

YFINFO_CACHE = {}
YFCACHE_FNAME = 'yf_info_cache.json.gz'

def check_socket(ip,port):
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (ip,port)
    result_of_check = a_socket.connect_ex(location)
    return result_of_check==0

def yfinance_cache(ticks,use_cache=True):
    global YFINFO_CACHE,YFCACHE_FNAME
    if not os.path.exists(YFCACHE_FNAME):
        json.dump({},gzip.open(YFCACHE_FNAME,'w'))
    if len(YFINFO_CACHE)==0:
        YFINFO_CACHE = json.load(gzip.open(YFCACHE_FNAME))
    info_dic = {}
    need_update = set()
    for tick in ticks:
        if tick.strip()=='':
            continue
        if tick in YFINFO_CACHE and use_cache:
            # print 'use cache:',tick
            info_dic[tick] = YFINFO_CACHE[tick]
        else:
            need_update.add(tick)
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
    
    print 'need_update',need_update
    ## loop get info
    if not Pool:
        for tk in need_update:
            results = get_one_data(tk)
    else:
        pool = Pool(8)
        jobs = []
        for tk in need_update:
            job = pool.spawn(get_one_data,tk,)
            jobs.append(job)
        pool.join()
        results = [job.value for job in jobs]        
    
    ## make return/cache data
    if len(results)>0:
        for tick,info in results:
            YFINFO_CACHE[tick] = info
            info_dic[tick] = info
        json.dump(YFINFO_CACHE,gzip.open(YFCACHE_FNAME,'w'),indent=2)
    return info_dic
 
def load_cache(fname,use_cache=True):
    jobj = json.load(open(fname))
    ticks = set()
    for k,v in jobj["us-ticks"].items():
        # print k,':',v
        ticks.update(v.replace('  ','').split(' '))
    print 'Not_In_ConfigTicks:',set(YFINFO_CACHE.keys()) - ticks
    print 'Total Ticks:',len(ticks)    
    try:
        info = yfinance_cache(ticks,use_cache)
        print info
    except:
        traceback.print_exc()
    
    
if __name__ == '__main__':
    load_cache('stk_monitor.v01.json')
        