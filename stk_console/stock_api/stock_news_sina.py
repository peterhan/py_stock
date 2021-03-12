from requests import get,post
from bs4 import BeautifulSoup
import sys
import pdb
import pandas as pd
from collections import OrderedDict
from matplotlib import pyplot as plt 
if __name__ == '__main__':
    sys.path.append('..')
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT,flatten_json



class StockNewsSina():
    def __init__(self):
        self.urls='''
        http://finance.sina.com.cn/roll/index.d.html?cid=56615&page=1
        http://vip.stock.finance.sina.com.cn/moneyflow/#sczjlx
        http://vip.stock.finance.sina.com.cn/moneyflow/#blocktol_sina
        http://vip.stock.finance.sina.com.cn/moneyflow/#blocktol_zjh
        http://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/lhb/index.phtml
        http://vip.stock.finance.sina.com.cn/mkt/#chgn_700532
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount?node=sh_a
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=5&sort=changepercent&asc=0&node=sh_a&symbol=
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getRTHKStockCount?node=qbgg_hk
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getRTHKStockData?page=1&num=5&sort=changepercent&asc=0&node=qbgg_hk
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getFundNetCount?page=1&num=5&sort=date&asc=0&node=open_fund
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getFundNetData?page=1&num=5&sort=date&asc=0&node=open_fund
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeStockCount?node=chgn_700532
        http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=40&sort=symbol&asc=1&node=chgn_700532&symbol=&_s_r_a=init
        http://stock.finance.sina.com.cn/hkstock/view/money_flow.php
        http://money.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20liveDateTableList=/HK_MoneyFlow.getDayMoneyFlowOtherInfo?ts=2342354353&_=1609139875777
        http://money.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20liveChartDataList=/HK_MoneyFlow.getDayTotalMoneyFlowList?type=south&date=20201228&begintime=0900&endtime=1610&_=1609139875778
        http://money.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20liveChartDataList=/HK_MoneyFlow.getDayTotalMoneyFlowList?type=north&date=20201228&begintime=0900&endtime=1500&_=1609139875779
        http://money.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20historyDataList=/HK_MoneyFlow.getDailyHistoryMoneyFlowList?type=south&begindate=2020-11-28&enddate=2020-12-28&_=1609139875780
        http://money.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20historyDataList=/HK_MoneyFlow.getDailyHistoryMoneyFlowList?type=north&begindate=2020-11-28&enddate=2020-12-28&_=1609139875781
        http://money.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20totalDataList=/HK_MoneyFlow.getMoneyFlowSumByDate?begindate=2020-11-28&enddate=2020-12-28&_=1609139875782
        http://quotes.sina.cn/hq/api/openapi.php/XTongService.getTopTongList?type=1&callback=sina_160913987595611056164049210193&page=1&pagesize=10
        http://quotes.sina.cn/hq/api/openapi.php/XTongService.getTongHoldingRatioList?type=sh&callback=sina_16091398762458268830063516346&page=1&pagesize=10
        https://finance.sina.com.cn/realstock/company/sh600438/nc.shtml
        https://vip.stock.finance.sina.com.cn/quotes_service/view/cn_bill.php?symbol=sh600438
        https://vip.stock.finance.sina.com.cn/q/go.php/vInvestConsult/kind/nbjy/index.phtml?symbol=sh600438&bdate=2&edate=2
        http://data.eastmoney.com/hsgt/index.html
        https://www.investopedia.com/articles/active-trading/020915/mustknow-simple-effective-exit-trading-strategies.asp
        '''
        self.vip_api = 'http://vip.stock.finance.sina.com.cn/'
        self.money_api = 'http://money.finance.sina.com.cn/quotes_service/api/jsonp.php/'        
        self.quotes_api = 'http://quotes.sina.cn/hq/api/openapi.php/XTongService.getTopTongList'
        pass
        
    def get_json(self,url,mode='json'):
        print url
        resp = get(url)
        if mode=='json':
            jo = resp.json()
        elif mode=='jsonp':
            jsonp = ' '.join(res.text.splitlines())
            start = jsonp.find('(')
            jo = json.loads(jsonp[start+1:-1])
        return jo

    def unify_column(self,df):
        mapping = {
            'open_px':'open','high_px':'high','low_px':'low','close_px':'close'
            ,'avg_px':'avg'
            ,'turnover_volume':'volumne'
            ,'turnover_value' :'amount'
            ,'px_change' :'change'
            ,'px_change_rate' :'change_rate'
            }
        return df.rename(columns=mapping)
        
    def info_flow(self,type='global'):
        '''news flow'''
        url=self.apiv1+'/content/information-flow?channel={0}&accept=article&cursor=&limit=30&action=upglide'.format(type)
        jo = self.get_json(url)
        items = [elm['resource'] for elm in jo['data']['items']]
        df = pd.DataFrame.from_dict(items,orient='columns')
        df['display_time'] = df['display_time'].apply(to_timestamp)
        print df[['title','display_time','uri']]
        # pdb.set_trace()
        return df
        
    def article_detail(self,id):
        url = 'https://wallstreetcn.com/articles/{}'.format(id)
        html = get(url).text
        # pdb.set_trace()
        soup = BeautifulSoup(html,"lxml")
        text =  soup.find_all('article')[0].text
        
        return text
        
    



if __name__ =='__main__':
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    pd.set_option('display.width',None)
    pd.options.display.float_format = '{:.2f}'.format
    sn_sina = StockNewsSina()
    stks = ['UMC.NYSE','600438.SS','AMD.NASD','STWD.NYSE','TSLA.NASD','01818.HKEX','PLTR.NASD']
    
    pdb.set_trace()