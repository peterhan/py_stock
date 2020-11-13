#!coding:utf8
import os
import json
import yfinance as yf

YFINFO_CACHE = {}
YFCACHE_FNAME = 'yf_info_cache.json'

def yfinance_cache(tick,use_cache=True):
    global YFINFO_CACHE,YFCACHE_FNAME
    if not os.path.exists(YFCACHE_FNAME):
        json.dump({},open(YFCACHE_FNAME,'w'))
    if len(YFINFO_CACHE)==0:
        YFINFO_CACHE = json.load(open(YFCACHE_FNAME))
    if tick in YFINFO_CACHE and use_cache:
        return YFINFO_CACHE[tick]
    ticker = yf.Ticker(tick)
    info = ticker.info
    YFINFO_CACHE[tick] = info
    json.dump(YFINFO_CACHE,open(YFCACHE_FNAME,'w'),indent=2)
    return info
 
def load_cache(fname,use_cache=True):
    jobj = json.load(open(fname))
    ticks = set()
    for k,v in jobj["us-ticks"].items():
        print k,':',v
        ticks.update(v.split(' '))
    print 'need refresh:',len(ticks)
    for tick in ticks:
        try:
            info = yfinance_cache(tick,use_cache)
            print 'succ load:',tick,info
        except:
            print 'fail on:',tick
    
if __name__ == '__main__':
    load_cache('stk_monitor.v01.json')
        