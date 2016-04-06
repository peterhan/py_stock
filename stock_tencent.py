#!coding:utf8
import requests
import datetime
import time
import os
import json
from pprint import pprint
from bs4 import BeautifulSoup
from cStringIO import StringIO

stock_lst = '''
sz399001
sh000300
sz150028
sz399415
sh603333
sh000001
sz399006
sz300431
sz002702
sz000025
sh600401
sh600962
sh601001
sh600650
sz300330
sz300072
sz000629
sh603077
sz002702
'''
url='''
http://itindex.net/detail/41304-%E8%82%A1%E7%A5%A8-%E6%95%B0%E6%8D%AE-%E6%8E%A5%E5%8F%A3
http://qt.gtimg.cn/q=sz000858
'''

conf_str='''
# http://qt.gtimg.cn/q={stock}
# 未知,名字,代码,当前价格,昨收,今开,成交量（手）,外盘,内盘,买一,买一量（手）, 买二,买二量（手）, 买三,买三量（手）, 买四,买四量（手）, 买五,买五量（手）,卖一,卖一量, 卖二,卖二量, 卖三,卖三量, 卖四,卖四量, 卖五,卖五量,最近逐笔成交,时间,涨跌,涨跌%,最高,最低,价格/成交量（手）/成交额,成交量（手）,成交额（万）,换手率,市盈率,其他,最高,最低,振幅,流通市值,总市值,市净率,涨停价,跌停价
http://qt.gtimg.cn/q=ff_{stock}
代码, 主力流入, 主力流出, 主力净流入, 主力净流入/资金流入流出总和, 散户流入, 散户流出, 散户净流入, 散户净流入/资金流入流出总和, 资金流入流出总和1+2+5+6,未知,未知,名字,日期
http://qt.gtimg.cn/q=s_pk{stock}
买盘大单,买盘小单,卖盘大单,卖盘小单
http://qt.gtimg.cn/q=s_{stock}
未知,名字,代码,当前价格,涨跌,涨跌%,成交量（手）,成交额（万）, ,总市值
'''

def u2g(st): return st.encode('gbk','ignore')

def json_print(dic,ecd='gbk'): return json.dumps(dic,ensure_ascii=False,indent=4).encode(ecd)

def ts_to_str(i):
    return datetime.datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S')


def parse_conf(conf_str):
    conf=[]
    row=[]
    for l in StringIO(conf_str):
        if l.startswith('#'):
            continue
        l=l.strip().decode('utf8')
        if len(l)==0:continue
        row.append(l)
        if len(row)==2:
            conf.append( [ row[0], row[1].split(',') ] )
            row=[]
    return conf
        
def get_data(code,url,cols):
    r=requests.get(url.format(stock=code) )
    ret_s=r.text    
    ret_a=ret_s.split('"')
    if len(ret_a)>2:
        ret_s=ret_a[1]
    ret_a=ret_s.split('~')
    rdic=zip(cols,ret_a)
    # print  dic2str( rdic )
    return rdic
    
        
def main():
    conf=parse_conf(conf_str)
    codes = [s.strip() for s in StringIO(stock_lst) if not (s.startswith('#') or len(s)<3)]
    # print codes    
    for code in codes:
        for pair in conf:
            get_data(code,pair[0],pair[1])
            
if __name__=='__main__':
    main()
