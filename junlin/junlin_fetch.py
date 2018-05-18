#!coding:utf8
import json
import gzip
import datetime
from collections import OrderedDict

import requests
import bs4

cookies={
'z_c0':	"2|1:0|10:1515625766|4:z_c0|92:Mi4xdXVVQUFBQUFBQUFBQUFDR3VxQV9DaVlBQUFCZ0FsVk5KdXREV3dBUVh4ZklLTWpFY0djYWdLSTBCcnBadzM4Vml3|c5a841429a7555bb1ff760a0940a3c4de6d5b5ea6e610f7fda2f48d8cfc8f103",
}
headers={
'Accept':'application/json, text/plain, */*',
'Accept-Encoding':'gzip',
'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Connection':'keep-alive',
# 'origin':'https://zhuanlan.zhihu.com',
# 'Referer': 'https://zhuanlan.zhihu.com/c_36527123',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; ) Gecko/20100101 Firefox/60.0',
'Access-Control-Request-Headers':'x-udid',
'x-udid':'AAAAhrqgPwqPTm6UIXDSajRguY_Z20xRTo0=',
}
url='https://www.zhihu.com/api/v4/columns/c_36527123/articles?include=data%5B%2A%5D.admin_closed_comment%2Ccomment_count%2Csuggest_edit%2Cis_title_image_full_screen%2Ccan_comment%2Cupvoted_followees%2Ccan_open_tipjar%2Ccan_tip%2Cvoteup_count%2Cvoting%2Ctopics%2Creview_info%2Cauthor.is_following&limit=10&offset='

def unix2ts(uxts,mask='%Y-%m-%d %H:%M:%S',base=10):
    return \
        datetime.datetime.fromtimestamp( 
         int(uxts,base) 
        ).strftime(mask)
        
def get_one_index(offset):
    resp=requests.get(url+str(offset),cookies=cookies,headers=headers)
    print '[idx status]',resp,'[offset]',offset
    js= resp.json()
    return js
    
def get_one_article(url):
    resp=requests.get(url,cookies=cookies,headers=headers)
    html = resp.text
    print '[article]',url
    # print html.encode('gbk','ignore')
    return html

def file2json(fname):
    with open(fname) as fh:
        return json.load(fh, object_pairs_hook=OrderedDict)

def json2print(obj):
    print json.dumps(obj,ensure_ascii=False,indent=2).encode('gbk','ignore')    

def json2file(obj,fname):
    st= json.dumps(obj,ensure_ascii=False,indent=2).encode('utf8')    
    with open(fname,'w') as fh:
        fh.write(st)
        
def get_all_index(idx_fname):
    all_data=[]
    for i in range(100):
        data=get_one_index(i*10)
        if len(data['data'])==0:
            break
        all_data.extend(data['data'])
    json2file(all_data,idx_fname)
    
def key_by_url_index(idx):
    et_info = OrderedDict()
    if isinstance(idx,dict):
        idx=[idx]
    for entry in idx:                 
        url = entry['url']            
        et_info[url]=entry
    return et_info
    
def get_all_articles(idx_fname,article_fname):
    res = OrderedDict()
    idx = file2json(idx_fname)
    for entry in idx:        
        # print title.keys()
        url = entry['url']
        print '[topics]',entry['topics']
        html = get_one_article(url)
        res[url] = html
    json2file(res,article_fname)
        
        
def update_index_articles(idx_fname,article_fname):
    article = file2json(article_fname)
    idx = file2json(idx_fname)
    et_info = key_by_url_index(idx)
    for i in range(5):
        nidx = get_one_index(i*10)
        n_et = key_by_url_index(nidx)
        diff_url = set(n_et)-set(et_info)
        if len(diff_url)==0:
            break
    print diff_url
    
    
def merge_all_elm(elm,soup,joiner='\n'):
    return joiner.join([p.text.strip() for p in soup.find_all(elm)])
    
    
def extract_info(idx_fname,article_fname):
    import jieba.analyse
    stock_name='stock_name.txt'
    jieba.load_userdict(stock_name) 
    idx = file2json(idx_fname)
    et_info = key_by_url_index(idx)
    ##
    for url,info in file2json(article_fname).items():
        soup = bs4.BeautifulSoup(info,"lxml")
        title = merge_all_elm('h1',soup)
        text = merge_all_elm('p',soup)
        # print soup.prettify().encode('gbk','ignore')
        updated = unix2ts(str(et_info[url]['updated']))
        topics = ','.join([elm['name'] for elm in et_info[url]['topics']])
        title = title
        text = text
        tags = ','.join(jieba.analyse.extract_tags(text, topK=50))
        url
        print '#'*50   
        print (u'推荐时间：%s\n链接：%s\n推广标签：%s\n标题：%s\n语义标签：%s\n'%(updated,url,topics,title,tags)).encode('gbk','ignore')
        #break

        
def main():
    idx_fname='junlin_index.json'
    article_fname='junlin_article.json'
    
    # get_all_index(idx_fname)
    # get_all_articles(idx_fname,article_fname)
    
    # update_index_articles(idx_fname,article_fname)
    
    extract_info(idx_fname,article_fname)

    
if __name__=='__main__':
    main()