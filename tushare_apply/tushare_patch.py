#!coding:utf8
from requests import get,post
from bs4 import BeautifulSoup
# from jsonpath_rw import jsonpath,parse
# import webbrowser
import json
import re
import json
import time
# import ipdb
import pandas as pd
import re
import tushare as ts
from collections import OrderedDict
from urllib2 import urlopen, Request

from stk_util import ts2unix,js_dumps,gen_random,to_timestamp
# import jieba
# import jieba.analyse
  
    
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


def get_latest_news(lid='2517'):
    url='https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&k=2&num=50&page=1&r=%s&callback=jQuery111200%s_%s&_=%s'%(lid,gen_random(),gen_random(),int(time.time()),int(time.time()))
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
        row= [ l['title'],l['intro'],l['url'],l['keywords'].split(','),to_timestamp(l['ctime'])]
        data.append(row)
    df = pd.DataFrame(data,columns='title,intro,url,keywords,time'.split(','))
    return df    

def print_latest_news(df,encode='gbk'):
    for idx,row in df[['time','title','intro']].sort_values(['time']).iterrows():
        # pdb.set_trace()        
        tags = '[%s]'%(','.join(df.iloc[idx]['keywords']).encode(encode))
        time = '[%s]'%df.iloc[idx]['time']
        print time,'\n'.join(row.values[1:]).encode(encode,'ignore')
        print tags,df.iloc[idx]['url']      
        print ''

def get_today_ticks(code=None, mkt='1', retry_count=3, pause=0.001):
    """
        获取分笔数据
    Parameters
    ------
        code:string
                  股票代码 e.g. 600848
                  如遇网络等问题重复执行的次数
        pause : int, 默认 0
                 重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
        src : 数据源选择，可输入sn(新浪)、tt(腾讯)、nt(网易)，默认sn
     return
     -------
        DataFrame 当日所有股票交易数据(DataFrame)
              属性:成交时间、成交价格、价格变动，成交手、成交金额(元)，买卖类型
    """
    bs_type = {'1':u'买入', 
           '2': u'卖出', 
           '4': u'-'}
    url = 'http://push2ex.eastmoney.com/getStockFenShi?pagesize=6644&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzfscj&pageindex=0&id=%s&sort=1&ft=1&code=%s&market=%s&_=%s'
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            rurl =  url%(code, code, mkt, gen_random())
            # print(rurl)
            re = Request(rurl)            
            lines = urlopen(re, timeout=10).read()
#             if ct.PY3:
#                 lines = lines.decode('GBK') 
            lines = json.loads(lines)
            lines = lines['data']['data']
            df = pd.DataFrame(lines)   
            df = df.rename(columns={'t': 'time', 'p': 'price', 'v': 'vol', 'bs': 'type'})
            df = df[['time', 'price', 'vol', 'type']]
            df['price'] = df['price'].map(lambda x: x*1.0/1000)
            df['type'] = df['type'].map(lambda x: bs_type[str(x)])
            df['time'] = df['time'].map(lambda x: str(x).zfill(6))
        except Exception as e:
            import traceback,pdb
            traceback.print_exc()
            # pdb.set_trace()
            print(e)
        else:
            return df
    raise IOError("ct.NETWORK_URL_ERROR_MSG")


    
if __name__=='__main__':
    import pdb
    # print js_dumps(xgb_headmark())
    #print xgb_fastsubject()
    # print js_dumps(xgb_top_info())
    print get_today_ticks('600438')
    df = get_latest_news()
    print_latest_news(df)
