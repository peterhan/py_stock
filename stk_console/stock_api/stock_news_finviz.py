from requests import get,post 
import sys
import pdb
import time
import pandas as pd
from collections import OrderedDict
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
if __name__ == '__main__':
    sys.path.append('..')
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT,flatten_json,get_article_detail

class StockNewsFinViz():
    def __init__(self):
        self.urls='''https://finviz.com/api/futures_all.ashx?timeframe=NO
        '''
        self.debug = False
        self.headers = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
        }
        self.query_types=['m5','h1','d1','w1','m1']        
        
    def get_json(self,url):
        print url
        resp = get(url,headers=self.headers)
        # pdb.set_trace()
        jo = resp.json()
        return jo 
        
    def get_info_all(self,market_type,timeframe):
        if market_type not in ('futures','crypto','forex'):
            raise Exception('Not Valid Market Tyep')
        url = 'https://finviz.com/api/%s_all.ashx?timeframe=%s'%(market_type,timeframe)
        jo = self.get_json(url)
        df = pd.DataFrame.from_dict(jo.values())        
        # pdb.set_trace()
        return df
        
    def get_futures_all(self,timeframe='NO'):
        return self.get_info_all('futures',timeframe)
        
    def get_crypto_all(self,timeframe='NO'):
        return self.get_info_all('crypto',timeframe)
        
    def get_forex_all(self,timeframe='NO'):
        return self.get_info_all('forex',timeframe)
        
    def get_insider_trading(self):
        url ='https://finviz.com/insidertrading.ashx?or=-10&tv=100000&tc=7&o=-transactionValue'
        url ='https://finviz.com/insidertrading.ashx?tc=7'
        url ='https://finviz.com/insidertrading.ashx?or=10&tv=1000000&tc=7&o=-transactionValue'
        resp = get(url,headers=self.headers)
        soup = BeautifulSoup(resp.text,"lxml")
        text,tags = get_article_detail(soup,'tr','.insider-sale-row-2')
        pdb.set_trace()

if __name__ =='__main__':
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    pd.set_option('display.width',None)
    pd.options.display.float_format = '{:.2f}'.format
    
    snfv = StockNewsFinViz()
    # snfv.get_futures_all()
    # df1= snfv.get_futures_all('m5')
    # df2= snfv.get_forex_all('h1')
    # df2= snfv.get_crypto_all('d1')
    snfv.get_insider_trading()
    pdb.set_trace()