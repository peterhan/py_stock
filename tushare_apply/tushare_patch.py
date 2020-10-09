#!coding:utf8
from requests import get,post
from bs4 import BeautifulSoup
from jsonpath_rw import jsonpath,parse
import webbrowser
import json
# import ipdb
import tushare as ts
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
https://api.xuangubao.cn/api/pc/msgs?headmark=1489472187&limit=30&subjids=9,469,35,10
'''
import time
DATE_FORMAT='%Y-%m-%d %H:%M'
def ts2unix(str_date,mask=DATE_FORMAT):
    return int(time.mktime(
         time.strptime(str_date, mask)
        )) 
    
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
        
def headmark():
    dt=''
    # dt='headmark=%s&'%ts2unix('2017-03-14 10:12')
    r=get('https://api.xuangubao.cn/api/pc/msgs?%slimit=50&subjids=9,469,35,10'%dt)
    jo = r.json()
    jsonpath_expr = parse('$.NewMsgs[*]')
    # print json.dumps(jo,indent=2)
    for i,match in enumerate(jsonpath_expr.find(jo) ):
        # ipdb.set_trace()
        # print '\nLoop:[%s]'%i,match.full_path
        jo = match.value
        # print u'/'.join(jieba.analyse.textrank(jo['Title']+' '+jo['Summary'], topK=20, withWeight=False, allowPOS=('ns', 'n')) ).encode('gbk')
        print '\n'.join([jo['CreatedAt'],jo['Title'],jo['Summary'] ]).encode('gbk','ignore')
        stocks= jo.get('Stocks',)
        if stocks:
            print','.join([dic['Symbol'].encode('gbk')+':'+dic['Name'].encode('gbk') for dic in stocks])
        # print match.value.encode('gbk','ignore') 

def fengkou():
    import requests
    r = requests.get('https://api.xuangubao.cn/api/pc/panzhongfengkou?limit=30&page=1')
    jo= r.json()
    for elm in jo:
        # print json.dumps(elm,indent=2)        
        print ''
        print (elm['Title']+':'+elm.get('Desc','')).encode('gbk')
        for n in nest_selector(elm,'SubjSsetInfo.SsetStocks'):
            print (n['Symbol']+':'+n['Name']+';').encode('gbk')

def get_stock_live():
    print ts.get_realtime_quotes(['300750','002382','300330','600201','002430'])
    print ts.get_realtime_quotes(['510070','510150','510050','510190','510030'])
    pass
    


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
    raise IOError(ct.NETWORK_URL_ERROR_MSG)
    
if __name__=='__main__':
    headmark()
    fengkou()
    get_stock_live()
    