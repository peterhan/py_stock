#!coding:utf8
import os
import json
import gzip
import socket
import traceback,pdb
import yfinance as yf
import yfinance_cache

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
    for tick in ticks:
        if tick.strip()=='':
            continue
        if tick in YFINFO_CACHE and use_cache:
            # print 'use cache:',tick
            info_dic[tick] = YFINFO_CACHE[tick]
        else:
            print '[yf info use remote api]:',tick
            ticker = yf.Ticker(tick)          
            proxy=None
            if check_socket('127.0.0.1',7890):
                print 'use proxy'
                proxy={'https':'http://127.0.0.1:7890','http':'http://127.0.0.1:7890' }
            info = ticker.get_info(proxy=proxy)
            YFINFO_CACHE[tick] = info
            json.dump(YFINFO_CACHE,gzip.open(YFCACHE_FNAME,'w'),indent=2)
            info_dic[tick] = info
    return info_dic
 
def load_cache(fname,use_cache=True):
    jobj = json.load(open(fname))
    ticks = set()
    for k,v in jobj["us-ticks"].items():
        # print k,':',v
        ticks.update(v.replace('  ','').split(' '))
    print 'NotConfigTicks:',set(YFINFO_CACHE.keys()) - ticks
    print 'Total Ticks:',len(ticks)    
    for tick in ticks:
        try:
            info = yfinance_cache([tick],use_cache)
            # print 'succ load:',tick,info
            # pdb.set_trace()
        except:
            traceback.print_exc()
            print 'fail on:',tick
    
if __name__ == '__main__':
    load_cache('stk_monitor.v01.json')
        