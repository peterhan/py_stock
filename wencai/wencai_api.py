#! -*- coding:utf8 -*-
import wencai  as wc
from tabulate import tabulate as tb
import pandas as pd
import pdb
import cPickle
from itertools import combinations


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
        
    cPickle.dump(res, open('stra.p','w'))

def sum_rate():
    res = cPickle.load(open('stra.p','r'))
    print 'Records:',len(res)    
    df = pd.concat(res.values())        
    df.to_csv('data.csv', encoding='gbk')
    
combinate_rate()
# sum_rate()