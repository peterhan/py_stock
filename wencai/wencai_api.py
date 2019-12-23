#! -*- coding:utf8 -*-
import wencai  as wc
from tabulate import tabulate as tb
import pandas as pd
import pdb
import cPickle
from itertools import combinations

# http://www.iwencai.com/stockpick/search?ts=1&tid=stockpick&querytype=fund&qs=fund_fhzs_a&w=%E4%B8%AD%E8%AF%81500%E5%9F%BA%E9%87%91
# http://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=3&qs=pc_%7Esoniu%7Estock%7Estock%7Ehistory%7Equery&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=%E7%89%9B%E5%8F%89%E9%80%89%E8%82%A1

# pd.set_option('display.height',1000)
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)

def get_query_comb(querys):
    querys =','.join(querys)
    # df = wc.get_scrape_report(querys)
    # df = wc.get_scrape_transaction(querys)
    df = wc.get_strategy(querys)
    print querys.encode('gbk')
    print df
    # df.index = [querys]
    return df
    
    
def combinate_rate():
    res = {}
    querys = u"boll突破上轨,周线cci买入信号,月线cr金叉,mtm金叉,资金净流入,社保持股,".split(',')
    querys = u"300303,机构密集调研,信托持股,保险持股,券商持股,社保持股,证金持股".split(',')
    querys = [querys for querys in combinations(querys, 1)]

    for equerys in querys[:1]:
        df = get_query_comb(equerys)
        res[equerys] = df
        
    cPickle.dump(res, open('stra.pickle','w'))

def sum_rate():
    res = cPickle.load(open('stra.pickle','r'))
    print 'Records:',len(res)    
    df = pd.concat(res.values())        
    df.to_csv('data.csv', encoding='gbk')
    
combinate_rate()
# sum_rate()
