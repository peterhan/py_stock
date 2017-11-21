#:coding:utf8
import requests
import datetime
import time
import os
from bs4 import BeautifulSoup
from util import ConfLoader
doc='''
http://itindex.net/detail/49971-sina-%E8%82%A1%E7%A5%A8-%E6%95%B0%E6%8D%AE
查看日K线图：
http://image.sinajs.cn/newchart/daily/n/sh601006.gif
分时线的查询：
http://image.sinajs.cn/newchart/min/n/sh000001.gif
日K线查询：
http://image.sinajs.cn/newchart/daily/n/sh000001.gif
周K线查询：
http://image.sinajs.cn/newchart/weekly/n/sh000001.gif
月K线查询：
http://image.sinajs.cn/newchart/monthly/n/sh000001.gif
http://hq.sinajs.cn/list=sh601006
http://itindex.net/detail/54764-%E8%82%A1%E7%A5%A8-%E5%AE%9E%E6%97%B6-%E4%BA%A4%E6%98%93
'''
from cStringIO import StringIO

s='''\
sz300072 14.627 6200
sz300330 39.540 2300'''

def u2g(st): 
    return st.encode('gbk','ignore')


def parse_js(st):
    rs = []
    st = st.replace('var hq_str_s_', '').replace(
        '=\"', '\t').replace('\";', '').replace(',', '\t')
    # print st
    for l in StringIO(st):
        row=l.strip().split('\t')[0:]
        row[0]=row[0][:]
        rs.append(row)
    return rs

# print int(datetime.datetime.ctime(now))


def ts_to_str(i):
    return datetime.datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S')


def get_index(holding):
    lst = ','.join(holding)
    tobj = time.time()
    gt = '%d' % (tobj * 1000)
    print ts_to_str(tobj)  # 1435729332785
    url = 'http://hq.sinajs.cn/rn=%s&list=%s' % (gt, lst)
    print url
    res = requests.get(url)
    rs = parse_js(u2g(res.text))
    def fmt(row):
        return ''.join(map(lambda x: '%10s' % x, row))
    print fmt(['code','name','current','price_chg','rate','sell','buy'])
    for row in rs:
        if row[0]=='':
            continue
        print fmt(row)
        
def guba(code):
    import urllib
    site='http://guba.eastmoney.com'
    url='%s/list,%s.html'%(site,code)
    # url='stockpage.10jqka.com.cn/%s'%code
    print url
    html=urllib.urlopen(url).read()
    # print html
    soup=BeautifulSoup(html,"lxml")
    for tag in soup.findAll('span',class_='l3')[6:16]:
        print u2g(tag.text ),'|',
        atag=tag.findAll('a')
        if len(atag)>0:
            print site+"/"+atag[0]['href']
        # print tag ,
    print ''
    
def main():
    holding=ConfLoader().holding    
    get_index(holding)
    
if __name__=='__main__':
    main()
    # guba('600401')
    # guba('300072')
    # guba('300330')