from requests import get,post
from bs4 import BeautifulSoup
from jsonpath_rw import jsonpath,parse
import webbrowser
import json
import ipdb
import tushare as ts
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
    
if __name__=='__main__':
    headmark()
    fengkou()
    get_stock_live()
    