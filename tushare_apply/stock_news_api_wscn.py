from requests import get,post
from bs4 import BeautifulSoup
from jsonpath_rw import jsonpath,parse
import pdb
import pandas as pd
from collections import OrderedDict
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT
from matplotlib import pyplot as plt




class StockNewsWSCN():
    def __init__(self):
        self.urls='''http://live.wallstreetcn.com
        https://api-ddc.wallstcn.com/market/kline?prod_code=000001.SS&period_type=300&tick_count=256&fields=tick_at%2Copen_px%2Cclose_px%2Chigh_px%2Clow_px
        '''
        self.apiv1='https://api.wallstcn.com/apiv1'
        self.apiddc='https://api-ddc.wallstcn.com/market'
        
        self.LIVE_CHANNEL = 'global,a-stock,us-stock,hk-stock,forex,commodity'.split(',')
        self.INFO_CHANNEL = 'global,shares,bonds,commodities,enterprise,economy,charts'.split(',')
        self.MKTSTK_TYPE = 'forexdata#index,US#china,US#star,US#stock,HK#stock,mdc#stock'.split(',')       
        pass
        
    def get_json(self,url):
        print url
        resp = get(url)
        jo = resp.json()
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
        url=self.apiv1+'/content/information-flow?channel={0}&accept=article&cursor=&limit=30&action=upglide'.format(type)
        jo = self.get_json(url)
        items = [elm['resource'] for elm in jo['data']['items']]
        df = pd.DataFrame.from_dict(items,orient='columns')
        df['display_time'] = df['display_time'].apply(to_timestamp)
        print df[['title','display_time','uri']]
        # pdb.set_trace()
        return df
        
    #global,a-stock,us-stock,hk-stock,forex,commodity
    
    def lives(self,type='a-stock',ts=None):
        ts_cond=''
        if ts!=None:
            ts_cond='&cursor=%s'%ts
        url = self.apiv1+'/content/lives?channel={type}-channel&client=pc{ts_cond}&limit=20&first_page=false&accept=live%2Cvip-live'.format(type=type,ts_cond=ts_cond)
        jo = self.get_json(url)    
        items = jo['data']['items']
        df = pd.DataFrame.from_dict(items,orient='columns')
        df['c_time'] = df['display_time'].apply(to_timestamp)    
        print df[['content_text','c_time']]
        # pdb.set_trace()
        return df
    
    def macrodatas(self,days_before=1,days_after=5):
        import datetime
        fmt = DATE_FORMAT
        dlt = datetime.timedelta(days=5)
        sts = (datetime.datetime.now()-datetime.timedelta(days=days_before)).strftime(fmt)
        ets = (datetime.datetime.now()+datetime.timedelta(days=days_after)).strftime(fmt)
        sts = ts2unix(sts)
        ets = ts2unix(ets)
        url = self.apiv1+'/finance/macrodatas?start={}&end={}'.format(sts,ets)
        jo = self.get_json(url)
        items = jo['data']['items']
        df = pd.DataFrame(items)
        df['public_date'] = df['public_date'].apply(to_timestamp)
        df.sort_values(['public_date'],ascending=False,inplace=True)
        df['short_title']='['+df['country']+'] '+df['title'].str[:20]
        cols = ['public_date','short_title','importance','previous','forecast','actual','unit']
        print df[cols]
        return df
        
    def trend(self,stocks):    
        fields ='tick_at,close_px,avg_px,turnover_volume,turnover_value,open_px,high_px,low_px,px_change,px_change_rate'.replace(',','%2C')
        stks ='%2C'.join(stocks)
        url = self.apiddc+'/trend?fields={1}&prod_code={0}'.format(stks,fields)
        jo = self.get_json(url)
        candle = jo['data']['candle']
        fields = jo['data']['fields']
        result_dic = OrderedDict()
        for tick,data in candle.items():
            df = pd.DataFrame(data['lines'],columns=fields)
            df['tick_ts'] = df['tick_at'].apply(to_timestamp)
            df.set_index(df['tick_at'],inplace=True)
            df =  self.unify_column(df)
            print '\n[%s]'%tick
            print df.tail()
            result_dic[tick] = df
            # pdb.set_trace()
        return result_dic
       
    def kline(self, stocks,days=1,secs=None):
        if secs is None:
            secs = days*86400
        else:
            secs = secs
        stks = '%2C'.join(stocks)
        fields = 'tick_at,open_px,close_px,high_px,low_px,turnover_volume,turnover_value,average_px,px_change,px_change_rate,avg_px,ma2'.replace(',','%2C')
        url = self.apiddc+'/kline?prod_code={0}&tick_count=512&period_type={1}&fields={2}'.format(stks,secs,fields)
        jo = self.get_json(url)
        candle = jo['data']['candle']
        fields = jo['data']['fields']
        result_dic = OrderedDict()
        for tick,data in candle.items():
            df = pd.DataFrame(data['lines'],columns=fields)
            df['tick_ts'] = df['tick_at'].apply(to_timestamp)
            df.set_index(df['tick_at'],inplace=True)
            df =  self.unify_column(df)
            print '\n[%s]'%tick
            print df.tail()
            result_dic[tick] = df
            # pdb.set_trace()
        return result_dic
       
    def market_real(self,stocks=None):
        stks = 'US500.OTC,XAUUSD.OTC,BTCUSD.Bitfinex,UKOIL.OTC,USDCNH.OTC,EURUSD.OTC,USDJPY.OTC,US10YR.OTC,UK10YR.OTC,JP10YR.OTC,CN10YR.OTC,000001.SS,399001.SZ,399006.SZ'.replace(',','%2C')
        # stks = ''.replace(',','%2C')
        if stocks:
            stks='%2C'.join(stocks)
        fields='prod_name,last_px,px_change,px_change_rate,price_precision,securities_type'.replace(',','%2C')
        url = self.apiddc+'/real?prod_code={0}&fields={1}'.format(stks,fields)
        jo = self.get_json(url)
        snapshot = jo['data']['snapshot']
        fields = jo['data']['fields']
        df = pd.DataFrame.from_dict(snapshot,orient='index',columns=fields)
        # pdb.set_trace()
        print df
        return df 
        
    def market_rank(self,mkt_type,stk_type,cursor=0,limit=20,sort_by='px_change_rate',order_by='desc'):
        fields = 'prod_name,prod_en_name,prod_code,symbol,last_px,px_change,px_change_rate,high_px,low_px,week_52_high,week_52_low,price_precision,update_time'.replace(',','%2C')
        url = self.apiddc\
            +'/rank?market_type={3}&stk_type={4}&order_by={6}&sort_field={5}&limit={1}&fields={0}&cursor={2}'\
            .format(fields,limit,cursor,mkt_type,stk_type,sort_by,order_by)
        jo = self.get_json(url)
        candle = jo['data']['candle']
        fields = jo['data']['fields']
        df = pd.DataFrame(candle,columns = fields)
        df['update_time'] = df['update_time'].apply(to_timestamp)
        # pdb.set_trace()
        print df
        return df 



if __name__ =='__main__':
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    pd.set_option('display.width',None)
    pd.options.display.float_format = '{:.2f}'.format
    wscn = StockNewsWSCN()
    stks = ['UMC.NYSE','600438.SS','AMD.NASD','STWD.NYSE','TSLA.NASD','01818.HKEX','PLTR.NASD']
    wscn.macrodatas(1,2)
    wscn.info_flow()
    for channel in wscn.LIVE_CHANNEL:
        wscn.lives(channel)
    wscn.trend(stks)
    # wscn.kline(stks,days=30)
    # wscn.kline(stks,secs=60)
    wscn.market_real()
    for mstype in  wscn.MKTSTK_TYPE:    
        ma=mstype.split('#')
        wscn.market_rank(ma[0],ma[1])
    # pdb.set_trace()