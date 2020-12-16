from requests import get,post
from bs4 import BeautifulSoup
from jsonpath_rw import jsonpath,parse
import pdb
import pandas as pd
from collections import OrderedDict
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT
from matplotlib import pyplot as plt




def get_url(url):
    print url
    resp = get(url)
    jo = resp.json()
    return jo

def unify_column(df):
    return df.rename(columns={'open_px':'open','high_px':'high','low_px':'low','close_px':'close'})
    
WSCN_INFO_CHANNEL = 'global,shares,bonds,commodities,enterprise,economy,charts'.split(',')
def wscn_content_info_flow(type='global'):
    url='https://api.wallstcn.com/apiv1/content/information-flow?channel={0}&accept=article&cursor=&limit=30&action=upglide'.format(type)
    jo = get_url(url)
    items = [elm['resource'] for elm in jo['data']['items']]
    df = pd.DataFrame.from_dict(items,orient='columns')
    df['display_time'] = df['display_time'].apply(to_timestamp)
    print df[['title','display_time','uri']]
    # pdb.set_trace()
    return df
    
#global,a-stock,us-stock,hk-stock,forex,commodity
WSCN_LIVE_CHANNEL = 'global,a-stock,us-stock,hk-stock,forex,commodity'.split(',')
def wscn_content_lives(type='a-stock',ts=None):
    ts_cond=''
    if ts!=None:
        ts_cond='&cursor=%s'%ts
    url = 'https://api.wallstcn.com/apiv1/content/lives?channel={type}-channel&client=pc{ts_cond}&limit=20&first_page=false&accept=live%2Cvip-live'.format(type=type,ts_cond=ts_cond)
    jo = get_url(url)    
    items = jo['data']['items']
    df = pd.DataFrame.from_dict(items,orient='columns')
    df['c_time'] = df['display_time'].apply(to_timestamp)    
    print df[['content_text','c_time']]
    # pdb.set_trace()
    return df

def wscn_market_trend(stocks):    
    fields ='tick_at,close_px,avg_px,turnover_volume,turnover_value,open_px,high_px,low_px,px_change,px_change_rate'.replace(',','%2C')
    stks ='%2C'.join(stocks)
    url = 'https://api-ddc.wallstcn.com/market/trend?fields={1}&prod_code={0}'.format(stks,fields)
    jo = get_url(url)
    candle = jo['data']['candle']
    fields = jo['data']['fields']
    result_dic = OrderedDict()
    for tick,data in candle.items():
        df = pd.DataFrame(data['lines'],columns=fields)
        df['tick_ts'] = df['tick_at'].apply(to_timestamp)
        df.set_index(df['tick_at'],inplace=True)
        df =  unify_column(df)
        print tick, df.head()
        result_dic[tick] = df
        # pdb.set_trace()
    return result_dic
   
def wscn_market_kline(stocks,days=1,secs=None):
    if secs is None:
        secs = days*86400
    else:
        secs = secs
    stks = '%2C'.join(stocks)
    fields = 'tick_at,open_px,close_px,high_px,low_px,turnover_volume,turnover_value,average_px,px_change,px_change_rate,avg_px,ma2'.replace(',','%2C')
    url = 'https://api-ddc.wallstcn.com/market/kline?prod_code={0}&tick_count=512&period_type={1}&fields={2}'.format(stks,secs,fields)
    jo = get_url(url)
    candle = jo['data']['candle']
    fields = jo['data']['fields']
    result_dic = OrderedDict()
    for tick,data in candle.items():
        df = pd.DataFrame(data['lines'],columns=fields)
        df['tick_ts'] = df['tick_at'].apply(to_timestamp)
        df.set_index(df['tick_at'],inplace=True)
        df =  unify_column(df)
        print tick, df.head()
        result_dic[tick] = df
        # pdb.set_trace()
    return result_dic
   
def wscn_market_real(stocks=None):
    stks = 'US500.OTC,000001.SS,CEURUSD.OTC,CUSDJPY.OTC,CUS10YR.OTC,C399001.SZ,C399006.SZ'.replace(',','%2C')
    if stocks:
        stks='%2C'.join(stocks)
    fields='prod_name,last_px,px_change,px_change_rate,price_precision,securities_type'.replace(',','%2C')
    url='https://api-ddc.wallstcn.com/market/real?prod_code={0}&fields={1}'.format(stks,fields)
    jo = get_url(url)
    snapshot = jo['data']['snapshot']
    fields = jo['data']['fields']
    df = pd.DataFrame.from_dict(snapshot,orient='index',columns=fields)
    # pdb.set_trace()
    print df
    return df 
    
def wscn_market_rank():
    fields = 'prod_name,prod_en_name,prod_code,symbol,last_px,px_change,px_change_rate,high_px,low_px,week_52_high,week_52_low,price_precision,update_time'.replace(',','%2C')
    url = 'https://api-ddc.wallstcn.com/market/rank?market_type=forexdata&stk_type=index&order_by=none&sort_field=px_change_rate&limit={0}&fields={1}&cursor=0'.format(200,fields)
    jo = get_url(url)
    candle = jo['data']['candle']
    fields = jo['data']['fields']
    df = pd.DataFrame(candle,columns = fields)
    df['update_time'] = df['update_time'].apply(to_timestamp)
    # pdb.set_trace()
    return df 

def wscn_finance_macrodatas(days_before=1,days_after=5):
    import datetime
    fmt = DATE_FORMAT
    dlt = datetime.timedelta(days=5)
    sts = (datetime.datetime.now()-datetime.timedelta(days=days_before)).strftime(fmt)
    ets = (datetime.datetime.now()+datetime.timedelta(days=days_after)).strftime(fmt)
    sts = ts2unix(sts)
    ets = ts2unix(ets)
    url = 'https://api.wallstcn.com/apiv1/finance/macrodatas?start={}&end={}'.format(sts,ets)
    jo = get_url(url)
    items = jo['data']['items']
    df = pd.DataFrame(items)
    df['public_date'] = df['public_date'].apply(to_timestamp)
    df.sort_values(['public_date'],ascending=False,inplace=True)
    df['short_title']='['+df['country']+'] '+df['title'].str[:20]
    cols = ['public_date','short_title','importance','previous','forecast','actual','unit']
    print df[cols]
    return df
    

if __name__ =='__main__':
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    pd.set_option('display.width',None)
    pd.options.display.float_format = '{:.2f}'.format
    stks = ['PTSH.OTC','UMC.NYSE','600438.SS','AMD.NASD','STWD.NYSE','TSLA.NASD','01818.HKEX']
    wscn_content_info_flow()
    wscn_content_lives('us-stock')
    wscn_content_lives('a-stock')
    wscn_content_lives('hk-stock')
    wscn_market_trend(stks)
    wscn_market_kline(stks,days=30)
    # wscn_market_kline(stks,secs=60)
    # wscn_market_real(stks)
    # wscn_market_real()
    wscn_finance_macrodatas(1,2)