#!coding:gbk
import requests
import json
import csv
import os
from pprint import pprint
'''
http://www.sse.com.cn/assortment/stock/list/share/
http://mnews.gw.com.cn/wap/data/ipad/stock/SZ/02/002702/gsgg/1.json
http://mnews.gw.com.cn/wap/data/ipad/stock/SZ/38/300238/f10/F10_Sjm.json
http://mnews.gw.com.cn/wap/data/ipad/stock/SZ/38/300238/f10/F10_Jbm.json
url='http://mnews.gw.com.cn/wap/data/scfl.json'    
url='http://mnews.gw.com.cn/wap/data/ipad/stock/SZ/02/002702/gsgg/1.json'   
url='http://mnews.gw.com.cn/wap/data/ipad/stock/SZ/02/002702/gsxw/1.json'
url='http://mnews.gw.com.cn/wap/data/ipad/stock/SH/31/600231/yjbg/1.json' 
'''
def u2g(st):return st.encode('gbk')

def u2g_t(st):return '%s:%s'%(st[0].encode('gbk'),st[1].encode('gbk'))

def u2u(st):return st.encode('utf8')    

def dic2str(dic,ecd='gbk'):
    return json.dumps(dic,ensure_ascii=False,indent=4).encode(ecd)

def get_json_url(url):
    r=requests.get(url)
    return r.json()
    
url='http://mnews.gw.com.cn/wap/data/ipad/stock/SZ/38/300238/f10/F10_Sjm.json'

def parse_sjm(stock_code):
    stock_info={'market':stock_code[:2],'suffix':stock_code[-2:],'code':stock_code[2:]}
    url='http://mnews.gw.com.cn/wap/data/ipad/stock/{market}/{suffix}/{code}/f10/F10_Sjm.json'.format(**stock_info)    
    r=requests.get(url)
    jos= r.json()
    jos=jos[0]
    data=jos['data']
    # dic2str(data)
    for row in data[:3]:
        if 'url' in row:
            row['urldata']=get_json_url(row['url'])    
    return data
    
def parse_jbm(stock_code):
    stock_info={'market':stock_code[:2],'suffix':stock_code[-2:],'code':stock_code[2:]}
    url='http://mnews.gw.com.cn/wap/data/ipad/stock/{market}/{suffix}/{code}/f10/F10_Jbm.json'.format(**stock_info)
    # print url
    r=requests.get(url)
    jos= r.json()
    jos=jos[0]
    data=jos['data']
    rdic={}
    for key in data:
        info=data[key]
        title=info['title']
        if type(title)==unicode:
            rdic[key]=title
            # print u2g(title)
        else:
            for dc in title:
                for key,vlu in dc.items():
                    rdic[key]=vlu    
    return rdic

def load_list(market):
    rows=[]
    rdr=csv.reader(open('idx/%sSEC.csv'%market) )
    for row in rdr:
        rows.append( row)
    header=rows[0]
    rows.pop(0)
    return rows,header
    
    
def fetch_api_data(market):    
    lst,header=load_list(market)
    dir='data/'
    for row in lst[:]:
        stock_code= market+row[0]
        stock_name= row[1]
        try:
            fname='%s%s'%(dir,stock_code)
            if os.path.exists(fname):
                continue
            jbm= parse_jbm(stock_code)
            jbm['stock_code']=stock_code
            jbm['stock_name']=stock_name.decode('gbk')
            # print dic2str(jbm)
            fp=open(fname,'wb')
            s=dic2str(jbm,ecd='utf8')
            fp.write(s)
            fp.close()
            print 'Succ:'+stock_name
        except Exception,e:
            print 'Fail',e,stock_code,stock_name
            
def dump_text_data():
    import glob
    fp=open('info.txt','w')
    for file in glob.glob('data/*'):
        js=json.load(open(file))
        print >> fp, '\t'.join(map(u2g_t,js.items() ) ).replace('\n','').replace('\r','')
        
def query_data():
    import glob
    scols=u'stock_code,stock_name,总股本(万),每股公积金,每股收益(元),每股净资产(元)'
    cols=scols.split(',')
    print u2g(scols)
    for file in glob.glob('data/*'):
        js=json.load(open(file)) 
        row=[]
        for col in cols:
            row.append( u2g(js[col]) )
        print ','.join(row)
            
def main():
    # market='SH'
    # fetch_api_data(market)
    # dump_text_data()
    query_data()
    # sjm= parse_sjm('SZ300001')          
    # print dic2str(sjm)
    # url='http://mnews.gw.com.cn/wap/data/scfl.json'
    # print dic2str(get_json_url(url))
    
if __name__=='__main__':
    main()