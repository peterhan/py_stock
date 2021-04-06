from requests import get,post 
import sys
import pdb
import ipdb
import time
import pandas as pd
from collections import OrderedDict
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
if __name__ == '__main__':
    sys.path.append('..')
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT,flatten_json
from stk_util import get_tags,list_to_dict

class StockNewsFinViz():
    def __init__(self):
        self.urls='''https://finviz.com/api/futures_all.ashx?timeframe=NO
        
        https://finviz.com/api/statement.ashx?t=TSLA&s=IA
        https://finviz.com/api/statement.ashx?t=TSLA&s=BA
        https://finviz.com/api/statement.ashx?t=TSLA&s=CA
        '''
        self.base_url = 'https://finviz.com'
        self.debug = False
        self.headers = { 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
        }
        self.query_types=['m5','h1','d1','w1','m1']        
        self.filter_select = {}
        
    def get_json(self,url):
        print url
        resp = get(url,headers=self.headers)
        # pdb.set_trace()
        jo = resp.json()
        return jo
        
    def get_soup(self,url):
        resp = get(url,headers=self.headers)
        soup = BeautifulSoup(resp.text,"lxml")
        # pdb.set_trace()
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
        ## concept category
        tags = get_tags(soup, 'td','.fullview-links')
        rows1 = []
        for tag in tags[1].find_all('a'):
            rows1.append([tag.text,tag.attrs['href']])
        ## overview
        tags = get_tags(soup, 'tr','.table-dark-row')
        rows2 = self.tags_to_tables(tags)
        for i,row in enumerate(rows2):
            rows2[i] = list_to_dict(row)
        ## rating         
        tags = get_tags(soup, 'td','.fullview-ratings-inner')
        rows3 = self.tags_to_tables(tags)
        ## news
        ssoup4 = get_tags(soup,'table','#news-table')[0]
        tags = ssoup4.find_all('tr')
        rows4 = self.tags_to_tables(tags)
        suff = ''
        for i,row in enumerate(rows4):
            if len(row[0])>15:
                suff = row[0].split(' ')[0]
            else:
                rows4[i][0] = suff+' '+row[0]
        ## profile
        ssoup5 = get_tags(soup,'td','.fullview-profile')[0]
        rows5  = ssoup5.text
        ## insider
        ssoup6 = get_tags(soup,'table','.body-table')[0]
        tags = get_tags(ssoup6,'tr')
        rows6 = self.tags_to_tables(tags)
        ##
        res = {'concept':rows1,'overview':rows2,'rating':rows3,'news':rows4,'profile':rows5,'insider':rows6}
        # pdb.set_trace()
        return res
       
    def format_query(self,query):
        qst = '&'.join(['%s=%s'%(k,v) for k,v in query.items()])
        return qst
    
    def parse_query(self,qst):
        rdic = OrderedDict()
        qst = qst.split('?')[-1]
        for part in qst.split('&'):
            p1,p2 = part.split('=',1)
            rdic[p1] = p2
        return rdic
    
    def get_scrn_page(self,query,soup=None,start_row=None):
        if start_row is not None:
            query['r'] = start_row
        if soup is None:
            url = self.base_url+'/screener.ashx?%s'%self.format_query(query)
            print url
            soup = self.get_soup(url)
        ssoup = get_tags(soup,'div','#screener-content')[0]
        ss_soup = get_tags(ssoup,'table')[3]
        tags = get_tags(ss_soup,'tr')
        table = self.tags_to_tables(tags)
        for i in range(1,len(table)):
            table[i]  = table[i][::2]
        df=pd.DataFrame(table[1:],columns=table[0])
        return df
        
    def get_screener(self, query = OrderedDict([['v','111'],['f','ind_broadcasting']]),page_limit=None ):
        url = self.base_url+'/screener.ashx?%s'%self.format_query(query)
        soup = self.get_soup(url)
        ## sector
        if len(self.filter_select)==0:
            tags = get_tags(soup,'select')
            select_tags = [tag for tag in tags if tag.attrs['id'].startswith('fs_')]
            filter_select = {}
            for tag in select_tags:
                gid = tag.attrs['id']
                sdic = {}
                for opt in tag.find_all('option'):
                    sdic[opt.attrs['value']]=opt.text
                filter_select[gid] = sdic        
            self.filter_select = filter_select
        ## page
        ssoup = get_tags(soup,'td','.screener_pagination')[0]
        tags = get_tags(ssoup,'a')
        page_info = [(tag.attrs['href'],tag.text) for tag in tags]
        ## table
        remain_r = []
        
        for info in page_info:
            if info[1] in ('1','next'):
                continue
            odc = self.parse_query(info[0])
            remain_r.append(odc['r'])
        if page_limit:
            remain_r = remain_r[:page_limit]
        
        df=self.get_scrn_page(query,soup=soup)
        print 'Extra-Screener-Page:',len(remain_r)
        for r in remain_r:
            ndf=self.get_scrn_page(query,start_row=r)
            # ipdb.set_trace()
            df = df.append(ndf)
        ##
        df=df.set_index(pd.RangeIndex(df.shape[0]))
        ipdb.set_trace()
        return df
        
    def get_statement(self,code,stat_type='IA'):
        '''IA,BA,CA'''
        url = self.base_url+'/api/statement.ashx?t=%s&s=%s'%(code,stat_type)
        json = self.get_json(url)
        # tags = get_tags(soup,'td','.fullview-links')
        df = pd.DataFrame(json['data'])
        # pdb.set_trace()
        return df
        
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
    
    fv = StockNewsFinViz()
    df0 = fv.get_futures_all()
    # df1 = fv.get_futures_all('m5')
    # df2 = fv.get_forex_all('h1')
    # df3 = fv.get_crypto_all('d1')
    # df4 = fv.get_insider_trading()
    # df5 = fv.get_quote('PLTR')
    # fv.get_statement('TSLA','IA')
    # fv.get_statement('TSLA','BA')
    # fv.get_statement('TSLA','CA')
    query = OrderedDict([['v','111'],['f','ind_banksdiversified']])
    fv.get_screener(query)
    ipdb.set_trace()