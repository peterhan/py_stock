#!coding:utf8
from requests import get,post
from bs4 import BeautifulSoup
from jsonpath_rw import jsonpath,parse
import webbrowser
import json
import re
import json
import datetime,time
# import ipdb
import pandas as pd
import re
import tushare as ts
from collections import OrderedDict
from urllib2 import urlopen, Request
# import jieba
# import jieba.analyse
'''
http://live.wallstreetcn.com/?
http://xuangubao.cn/
https://api.xuangubao.cn/api/pc/panzhongfengkou?limit=30&page=1
https://api.xuangubao.cn/q/quote/v1/real
http://xuangubao.cn/subjects
http://xuangubao.cn/
https://flash-api.xuangubao.cn/api/stage2/plate/top_info?count=9&fields=all
https://flash-api.xuangubao.cn/api/pool/detail?pool_name=limit_up
https://api.xuangubao.cn/api/pc/fastSubject
https://api.xuangubao.cn/api/pc/msgs?headmark=1489472187&limit=30&subjids=9,469,35,10
https://api-ddc-wscn.xuangubao.cn/market/real?fields=prod_name,last_px,px_change,px_change_rate,symbol,trade_status&prod_code=600257.SS,600097.SS,002447.SZ,600702.SS,603290.SS,600360.SS,600746.SS,600623.SS,600776.SS,002017.SZ,000011.SZ,000070.SZ,600511.SS,600196.SS,603986.SS,688008.SS
https://api-ddc-wscn.xuangubao.cn/extract/news_event/preview?message_ids=809721,809718,809710,809705
https://flash-api.xuangubao.cn/api/plate/data?fields=plate_id,plate_name,fund_flow,rise_count,fall_count,stay_count,limit_up_count,core_avg_pcp,core_avg_pcp_rank,core_avg_pcp_rank_change,top_n_stocks,bottom_n_stocks&plates=53556594,20621170,16842834,16961441,16930590,38499865,19384882,18469582,62120753,5364594,22431937,21277137,651982,63576990,1008158,36001721,17412529,19218721,6681777,37869777,25019689,38053809,17452705,16950418,16844702,16868321,387225,16847921,20054814,66814321
'''
import time
DATE_FORMAT='%Y-%m-%d %H:%M'
def ts2unix(str_date,mask=DATE_FORMAT):
    return int(time.mktime(
         time.strptime(str_date, mask)
        )) 

def js_dumps(obj):    
    return json.dumps(obj,indent=2,ensure_ascii=False).encode('gbk','ignore')
    
def nest_selector(obj,path):
    patharr=path.split('.')    
    sel = obj
    for pathpart in patharr:
        if isinstance(sel,dict):
            sel=sel.get(pathpart,'')
        elif isinstance(sel,list):
            sel=sel[int(pathpart)]
        else:
            try:sel=getattr(sel,pathpart)
            except:sel=''
    return sel
    
def xgb_subject(url='https://xuangubao.cn/subject/151'):
    'https://api.xuangubao.cn/api/pc/subj/151?Mark=1606996991&limit=20'
    r=get(url)
    
    
def xgb_headmark():
    dt=''
    r=get('https://api.xuangubao.cn/api/pc/msgs?%slimit=50&subjids=9,469,35,10'%dt)
    jo = r.json()
    jsonpath_expr = parse('$.NewMsgs[*]')
    res = OrderedDict()
    for i,match in enumerate(jsonpath_expr.find(jo) ):        
        jo = match.value
        # print u'/'.join(jieba.analyse.textrank(jo['Title']+' '+jo['Summary'], topK=20, withWeight=False, allowPOS=('ns', 'n')) ).encode('gbk')
        ts,title,summary =jo['CreatedAt'],jo['Title'],jo['Summary']        
        stocks= jo.get('Stocks',)
        res['[%s]%s'%(ts,title)] = {'title':title,'ts':ts,'summary':summary,'stocks':stocks}        
    return res
        

def xgb_fastsubject():
    r = get('https://api.xuangubao.cn/api/pc/fastSubject')
    jo= r.json()
    res = OrderedDict()
    for elm in jo:        
        print js_dumps(elm)        
    return res
    
def xgb_top_info():
    r= get('https://flash-api.xuangubao.cn/api/stage2/plate/top_info?count=9&fields=all')
    jo = r.json()
    res = OrderedDict()
    for elm in jo['data']['top_plate_info']: 
        key = elm['plate_name']
        res[key] = elm
    return res

# def get_stock_live():
    # print ts.get_realtime_quotes(['300750','002382','300330','600201','002430'])
    # print ts.get_realtime_quotes(['510070','510150','510050','510190','510030'])
    # pass

def _random(n=16):
    from random import randint
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))
    
    
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

def print_latest_news(df):
    for idx,row in df[['time','title','intro']].sort_values(['time']).iterrows():
        # pdb.set_trace()        
        tags = '[%s]'%(','.join(df.iloc[idx]['keywords']).encode('gbk'))
        time = '[%s]'%df.iloc[idx]['time']
        print time,'\n'.join(row.values[1:]).encode('gbk')
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
            rurl =  url%(code, code, mkt, _random())
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
    print xgb_fastsubject()
    # print js_dumps(xgb_top_info())
    # df = get_latest_news()
    # print_latest_news(df)
