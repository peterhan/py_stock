import json,time
import requests
headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"}

# url='http://www.niuguwang.com/tr/getranke.ashx?type=5&topn=20&sign=0&version=2.6.1&packtype=1'
# url='http://www.niuguwang.com/tr/201411/other.ashx?userid=385324wandoujia&version=2.6.1&packtype=1'
# url='http://www.niuguwang.com/tr/201411/account.ashx?aid=151463&version=2.6.1&packtype=1'
url='http://www.niuguwang.com/tr/getranke.ashx?type=3&topn=20&sign=0&version=2.6.1&packtype=1'
# url='http://www.niuguwang.com/tr/201411/rankedhistor.ashx?type=1&topn=20&sign=0&version=2.6.1&packtype=1'

'''
http://www.niuguwang.com/user/getappinfo.ashx?appid=1&source=wandoujia&version=2.6.1&packtype=1
http://www.niuguwang.com/user/setmobile.ashx?userToken=Q5k-sgWTcsEE5gIWTk2pZJplFuSu8j9H91_zit05CO4*&token=040eebbb473&type=1&v=2.6.1&sv=4.3&xgtoken=&huaweitoken=08645870299642450000003221000001&version=2.6.1&packtype=1
http://www.niuguwang.com/tr/userindex20141111.ashx?userid=1570552&version=2.6.1&packtype=1
'''

'''
http://hq.niuguwang.com/aquote/quotedata/stocksyn.ashx?stockversion=1430150400&version=2.6.1&packtype=1

http://hq.niuguwang.com/aquote/basicdata/combrief.ashx?code=1709&version=2.6.1&packtype=1
http://hq.niuguwang.com/aquote/quotedata/stockshare.ashx?code=1709&version=2.6.1&packtype
=1
http://www.niuguwang.com/msg/stock/getnewslist.ashx?code=1709&page=1&pagesize=20&version=2.6.1&packtype=1



http://www.niuguwang.com/tr/201411/account.ashx?aid=44830&version=2.6.1&packtype=1
http://www.niuguwang.com/tr/201411/other.ashx?userid=44926&version=2.6.1&packtype=1
http://www.niuguwang.com/tr/201411/rankedhistor.ashx?topn=20&sign=0&uid=1570552&version=2.6.1&packtype=1

http://www.niuguwang.com/tr/getranke.ashx?type=3&topn=20&sign=0&version=2.6.1&packtype=1
http://www.niuguwang.com/tr/stocklistitem.ashx?id=2992664&version=2.6.1&packtype=1
'''
def inspect(jo,level=0):
    print json.dumps(jo, sort_keys=True, indent=2, separators=(',', ': '))
    
def get_uid_info(uid):
    time.sleep(1) 
    account = requests.get('http://www.niuguwang.com/tr/201411/account.ashx?aid=%s&version=2.6.1&packtype=1'%uid)
    other = requests.get('http://www.niuguwang.com/tr/201411/other.ashx?userid=%s&version=2.6.1&packtype=1'%uid)
    return account.json(),other.json()
    
def u2g(st):
    return st.encode('gbk','ignore')
    
def d2s(lst):   
    sl = []
    for dic in lst:
        ls = ['%s:%s'%(k,v) for k,v in dic.items()]
        sl.append(';'.join(ls))
    return u2g('\n'.join(sl))
    
def rank_data():    
    for typ in range(1,9):
    # for typ in range(1,2):
        print '*'*5+'type : %s'%typ 
        r = requests.get('http://www.niuguwang.com/tr/getranke.ashx?type=%s&topn=20&sign=0&version=2.6.1&packtype=1'%typ)
        jo = r.json()   
        for id,e in enumerate(jo['data']):
            if id > 1 :break        
            uid = e['UserID']
            print '\n\n',id,uid,u2g(e['UserName'])
            r1,r2 = get_uid_info(uid)
            inspect(r1)
            inspect(r2)
            history = r1['clearStockListData']
            hold = r1['stockListData']
            # print "#"*5+"history"
            # print d2s(history)
            # print "#"*5+"hold"
            # print d2s(hold)
            print 'recent : %s'%u2g(r2['stock'])
            
def get_stocklist():    
    r=requests.get('http://hq.niuguwang.com/aquote/quotedata/stocksyn.ashx?stockversion=14301504&version=2.6.1&packtype=1',headers=headers)
    # print r.headers['content-type']
    # print r.text
    jo=r.json()    
    print d2s(jo["stockdata"])
    
if __name__ == '__main__':
    get_stocklist()