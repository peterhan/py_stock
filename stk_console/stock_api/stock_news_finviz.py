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
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT,flatten_json
from stk_util import get_tags

class StockNewsFinViz():
    def __init__(self):
        self.urls='''https://finviz.com/api/futures_all.ashx?timeframe=NO
        '''
        self.base_url = 'https://finviz.com'
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
        
    def get_soup(self,url):
        resp = get(url,headers=self.headers)
        soup = BeautifulSoup(resp.text,"lxml")
        return soup
    
    def tags_to_tables(self,tags):
        rows = []
        for tr in tags:
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.replace('\n',' '))
                for atag in td.find_all('a'):
                    row.append(atag.attrs['href'])
            rows.append(row)
        return rows
        
    def get_market_all(self,market_type,timeframe):
        if market_type not in ('futures','crypto','forex'):
            raise Exception('Not Valid Market Tyep')
        url = self.base_url + '/api/%s_all.ashx?timeframe=%s'%(market_type,timeframe)
        jo = self.get_json(url)
        df = pd.DataFrame.from_dict(jo.values())        
        # pdb.set_trace()
        return df
        
    def get_futures_all(self,timeframe='NO'):
        return self.get_market_all('futures',timeframe)
        
    def get_crypto_all(self,timeframe='NO'):
        return self.get_market_all('crypto',timeframe)
        
    def get_forex_all(self,timeframe='NO'):
        return self.get_market_all('forex',timeframe)
      
    def get_quote(self,code):
        url = self.base_url+'/quote.ashx?t=%s&b=2'%code
        soup = self.get_soup(url)
        ##
        tags = get_tags(soup, 'td','.fullview-links')
        rows1 = []
        for tag in tags[1].find_all('a'):
            rows1.append([tag.text,tag.attrs['href']])
        ##
        tags = get_tags(soup, 'tr','.table-dark-row')
        rows2 = self.tags_to_tables(tags)
        ##
        tags = get_tags(soup, 'tr','.body-table-rating-neutral')
        rows3 = self.tags_to_tables(tags)
        pdb.set_trace()
        
    def get_income_stat(self,code):
        url = self.base_url+'/api/statement.ashx?t=%s&s=IA'%code
        soup = self.get_soup(url)
        # tags = get_tags(soup,'td','.fullview-links')
        pdb.set_trace()
        
    def get_screener(self,code):
        url = self.base_url+'/screener.ashx?v=111&amp;f=%s'%code
        soup = self.get_soup(url)
        pdb.set_trace()
        
    def get_insider_trading(self):
        ['or=-10&tv=100000&tc=7&o=-transactionValue',  'tc=7']
        query_str = 'or=10&tv=1000000&tc=7&o=-transactionValue'
        url = self.base_url + '/insidertrading.ashx?%s'%query_str   
        tags = get_tags(self.get_soup(url), 'tr','.insider-sale-row-2')
        rows = self.tags_to_tables(tags)
        # pdb.set_trace()
        header = 'Ticker,quotoe_url,Owner,owner_url,Relationship,Date,Transaction,Cost,#Shares,Value ($),Shares Total,SEC Form 4,sec_form_url'
        df = pd.DataFrame(rows,columns=header.split(','))
        return df

if __name__ =='__main__':
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    pd.set_option('display.width',None)
    pd.options.display.float_format = '{:.2f}'.format
    
    snfv = StockNewsFinViz()
    # df0 = snfv.get_futures_all()
    # df1 = snfv.get_futures_all('m5')
    # df2 = snfv.get_forex_all('h1')
    # df3 = snfv.get_crypto_all('d1')
    # df4 = snfv.get_insider_trading()
    snfv.get_quote('TSLA')
    pdb.set_trace()