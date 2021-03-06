import requests
import pdb
import re

import json
# from jsonpath_rw import jsonpath,parse
import sys
import pdb,traceback
import time
import pandas as pd
from collections import OrderedDict

from requests import get,post
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import logging

if __name__ == '__main__':
    sys.path.append('..')
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT,flatten_json,get_article_detail

# https://portal-api.coinmarketcap.com/v1/platform/alerts?limit=20
# https://api.coinmarketcap.com/data-api/v3/map/all?listing_status=active,untracked
# https://api.coinmarketcap.com/data-api/v3/topsearch/rank

# https://www.futunn.com/stock/03690-HK/company-profile#company
# https://www.futunn.com/stock/03690-HK/news
# https://www.futunn.com/stock/03690-HK/dividends#financing
# https://www.futunn.com/new-quote/index-quote
# https://www.futunn.com/new-quote/top-heat-stock?market_type=1&_=1614059874996
# https://www.futunn.com/new-quote/quote-basic?security_id=63934883169938&market_type=1&_=1614059874995
## https://www.futunn.com/new-quote/quote-minute?security_id=63934883169938&market_type=1&_=1614059874997
## https://www.futunn.com/new-quote/kline?security_id=54082228193550&type=4&from=&market_type=1&_=1614152016466
## https://www.futunn.com/new-quote/news-list?page=0&page_size=10&_=1614060549335
# https://finance.futunn.com/api/finance/company-info?code=01682&label=hk
# https://finance.futunn.com/api/finance/dividend?code=01682&label=hk
# https://www.futunn.com/search-stock/predict?keyword=TSLA&_=1614858445525

class StockNewsFUTUNN():
    def __init__(self):
        self.debug = False
        self.headers = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
            ,"Accept": "application/json, text/javascript, */*; q=0.01"        
            ,"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
            ,"Accept-Encoding": "gzip, deflate, br"
            ,"Origin": "https://www.futunn.com"
            ,"Upgrade-Insecure-Requests": '1'
            ,"Cache-Control": "max-age=0"
            ,"Referer": "https://www.futunn.com/"
        }
        self.cyc_mode = {'day':'2','week':'3','month':'4','year':'5'
            ,'5min':'6','15min':'7','30min':'8','hour':'9','3min':'10'
            ,'season':'11','season':'12','pre':'12','minute':'13'}
        self.stock_code_cache={}
        self.stock_info_cache={}
        
        
    def get_ts(self):
        return '%0.0f'%(time.time()*1000)
        
    def stock_code_adaptor(self,stock_code):
        tick = stock_code.upper().replace('.','-')
        if tick.find('-')==-1:
            if re.match('[A-z]+',tick):
                tick+='-US'
            elif re.match('\d+',tick):
                tick+='-SH'            
        if tick.endswith('-SS'):
            tick = tick.replace('-SS','-SH')
        if tick.endswith('-HK') and len(tick)==7:
            tick='0'+tick
        return tick
        
    def get_sec_id(self,stock_code):
        if isinstance(stock_code, dict):
            return stock_code
        stock_code = self.stock_code_adaptor(stock_code)
        url = "https://www.futunn.com/stock/%s" %stock_code
        if stock_code in self.stock_code_cache:
            return self.stock_code_cache[stock_code]
        try:
            resp = requests.get(url,headers=self.headers)
            jsline = ''
            for line in resp.text.splitlines():
                if line.find('<script>window._langParams')!=-1:
                    jsline = line
            if len(jsline)==0:
                raise Exception('Not Found window._langParams @ %s'%url)
            start_seg = 'window.__INITIAL_STATE__='
            start = jsline.find(start_seg)
            end = jsline.find(',window._params')
            js_st = jsline[start+len(start_seg):end]
            jo = json.loads(js_st)
            # pdb.set_trace()
            sinfo = jo['prefetch']['stockInfo']
            sec_id = sinfo['stock_id'] 
            sec_label = sinfo['stock_market']
            sec_code = sinfo['stock_code']
            mkt_type = sinfo['market_type']
            ret_dic = {'id':sec_id,'label':sec_label,'code':sec_code,'mkt_type':mkt_type,'input_code':stock_code}
            self.stock_info_cache[stock_code] = jo['prefetch']
            self.stock_code_cache[stock_code] = ret_dic
            return ret_dic
        except Exception as e:            
            traceback.print_exc()
            return {'input_code':stock_code}           

    def get_cache_company_info(self,sec_id):
        sec_id = self.get_sec_id(sec_id)
        input_code = sec_id['input_code']
        return self.stock_info_cache.get(input_code,None)
            
    def get_kline(self,sec_id,cyc='day'):        
        sec_id = self.get_sec_id(sec_id)
        ts = self.get_ts()
        date_mode = self.cyc_mode.get(cyc,cyc)
        url ='https://www.futunn.com/new-quote'\
            +'/kline?security_id=%s&type=%s&from=&market_type=%s&_=%s'%(sec_id['id'],date_mode,sec_id['mkt_type'],ts)
        logging.info(url) 
        resp = requests.get(url,headers=self.headers)
        # pdb.set_trace()
        jo = resp.json()
        lst = jo['data'].pop('list')
        df = pd.DataFrame.from_dict(lst ,orient='columns')        
        df.rename(mapper={'k':'date','o':'open','h':'high','l':'low','c':'close','t':'amount','v':'volume'},axis=1,inplace=True)        
        for field in ('open','high','low','close','amount'):
            df[field] = df[field]/1000
        df['date'] = pd.to_datetime(df['date'],unit='s')
        df.index = df['date']
        if self.debug:
            print url
            pdb.set_trace()
        return df
    
    def get_stock_minute(self,sec_id):        
        sec_id = self.get_sec_id(sec_id)
        ts = self.get_ts()
        url = 'https://www.futunn.com/new-quote'\
            +'/quote-minute?security_id=%s&market_type=%s&_=%s'%(sec_id['id'],sec_id['mkt_type'],ts)        
        resp = requests.get(url,headers=self.headers)
        
        jo = resp.json()
        lst = jo['data'].pop('list')
        df = pd.DataFrame.from_dict(lst ,orient='columns')
        df['time'] = pd.to_datetime(df['time'],unit='s')
        df.index = df['time']
        df['price'] = df['price']/1000
        df['turnover'] = df['turnover']/1000
        if self.debug:
            print url
            pdb.set_trace()
        return df
        
    def set_referer(self,input_code):
        self.headers['Referer']='https://www.futunn.com/stock/%s/company-profile#company'%input_code
        
    def get_company_info(self,sec_id):
        sec_id = self.get_sec_id(sec_id)
        self.set_referer(sec_id['input_code'])
        url='https://finance.futunn.com/api/finance/company-info?code=%s&label=%s'%(sec_id['code'],sec_id['label'])
        # print url
        resp = requests.get(url,headers=self.headers)
        jo = resp.json()        
        df = pd.DataFrame.from_dict([jo['data']])
        pdb.set_trace()
        return df
    
    def get_dividend(self,sec_id):
        sec_id = self.get_sec_id(sec_id)    
        self.set_referer(sec_id['input_code'])
        url='https://finance.futunn.com/api/finance/dividend?code=%s&label=%s'%(sec_id['code'],sec_id['label'])
        resp = requests.get(url,headers=self.headers)
        jo = resp.json() 
        df = pd.DataFrame.from_dict(jo['data'])
        pdb.set_trace()
        return df
        
    def get_stock_news(self,sec_id):
        sec_id = self.get_sec_id(sec_id)    
        url = 'https://www.futunn.com/stock/%s/news'%(sec_id['input_code'])  
        resp = requests.get(url,headers=self.headers)
        soup = BeautifulSoup(resp.text,'lxml')
        text,tags = get_article_detail(soup,'li','.news-item')
        rows = []
        for tag in tags:
            try:
                rows.append([tag.text,tag.find_all('a')[0].attrs['href']])
            except:
                rows.append([tag.text,None])
                pass
        df = pd.DataFrame(rows, columns=['title','url'])
        return df
    
    def get_news(self,start=0,cnt=20):
        url='https://www.futunn.com/new-quote/'\
            +'news-list?page=%s&page_size=%s&_=%s'%(start,cnt,self.get_ts())
        resp = requests.get(url,headers=self.headers)
        jo = resp.json()
        df = pd.DataFrame.from_dict(jo['data']['news'],orient='columns')
        df['time'] = pd.to_datetime(df['time'],unit='s')
        df.index = df['time'] 
        df.pop('audio_url')
        df.pop('audio_duration')
        # pdb.set_trace()
        return df
        
# GET /questions/750604/freeing-up-a-tcp-ip-port HTTP/1.1

# url='https://www.futunn.com/stock/01682-HK/company-profile'
# resp = requests.get(url,headers=headers)
# print resp.text
# pdb.set_trace()

if __name__ =='__main__':
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    pd.set_option('display.width',None)
    pd.options.display.float_format = '{:.2f}'.format
    ftnn = StockNewsFUTUNN()
    # ftnn.get_news()
    for stk in ['TSLA-US', '300015-SZ']:
    # for stk in ['CCIV-US','TSLA-US','03690-HK']:
        ftnn.debug=True
        # ftnn.get_sec_id(stk)
        # ftnn.get_company_info(stk)
        # ftnn.get_dividend(stk)
        df0 = ftnn.get_stock_news(stk)
        df1 = ftnn.get_kline(stk,'15min')
        df2 = ftnn.get_stock_minute(stk)
        pdb.set_trace()
    
    