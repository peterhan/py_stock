#!coding:utf8
'''
pageid="153" s_id="2509">全部</a> 
pageid="153" s_id="2510">国内</a> 
pageid="153" s_id="2511">国际</a> 
pageid="153" s_id="2669">社会</a> 
pageid="153" s_id="2512">体育</a> 
pageid="153" s_id="2513">娱乐</a> 
pageid="153" s_id="2514">军事</a> 
pageid="153" s_id="2515">科技</a> 
pageid="153" s_id="2516">财经</a> 
pageid="153" s_id="2517">股市</a> 
pageid="153" s_id="2518">美股</a> 
			
'''
import re
import json
import datetime,time
from urllib2 import urlopen,Request
import pandas as pd
import pdb

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)

def _random(n=16):
    from random import randint
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))
    
def get_latest_news(lid='2517'):
    url='https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&k=2&num=50&page=1&r=%s&callback=jQuery111200%s_%s&_=%s'%(lid,_random(),_random(),int(time.time()),int(time.time()))
    #2516 fin,2517 stock,2518 US stock

    LATEST_COLS_C = ['classify','title','time','url','content']
    r=Request(url)    
    print r.get_full_url()
    content = urlopen(r).read()
    pat=re.compile(r'try\{jQuery\d\d\d\d+_\d\d\d\d+\(')
    content = pat.split(content)[1]
    pat=re.compile(r'\);}catch\(e\){};')
    content = pat.sub('', content)
    jo = json.loads(content)
    # print json.dumps(jo,indent=2,ensure_ascii=False).encode('gbk','ignore')
    data = [] 
    for l in jo['result']['data']:
        row= [ l['title'],l['intro'],l['url'],l['keywords'].split(','),datetime.datetime.fromtimestamp(float(l['ctime']))]
        data.append(row)
    df = pd.DataFrame(data,columns='title,intro,url,keywords,time'.split(','))
    return df
    
if __name__ == '__main__':
    print get_latest_news()

# pdb.set_trace()