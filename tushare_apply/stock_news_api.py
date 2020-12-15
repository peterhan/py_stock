from requests import get,post
from bs4 import BeautifulSoup
from jsonpath_rw import jsonpath,parse
import pdb
import pandas as pd
from collections import OrderedDict
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT
from matplotlib import pyplot as plt

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format

urls='''http://live.wallstreetcn.com/?
https://api.wallstcn.com/apiv1/content/information-flow?channel=shares&accept=article&cursor=&limit=20&action=upglide
##global,shares,bonds,commodities,enterprise,economy,charts
https://wallstreetcn.com/news/commodities
https://api.wallstcn.com/apiv1/content/lives?channel=hk-stock-channel&client=pc&cursor=1606521252&limit=20&first_page=false&accept=live%2Cvip-live
https://api-ddc.wallstcn.com/market/trend?fields=tick_at%2Cclose_px%2Cavg_px%2Cturnover_volume%2Cturnover_value%2Copen_px%2Chigh_px%2Clow_px%2Cpx_change%2Cpx_change_rate&prod_code=TSLA.NASD%2C01818.HKEX%2CSTWD.NYSE
https://api-ddc.wallstcn.com/market/kline?prod_code=TSLA.NASD&tick_count=256&period_type=86400&fields=tick_at%2Copen_px%2Cclose_px%2Chigh_px%2Clow_px%2Cturnover_vol
https://api-ddc.wallstcn.com/market/rank?market_type=forexdata&stk_type=index&order_by=none&sort_field=px_change_rate&limit=15&fields=prod_name%2Cprod_en_name%2Cprod_code%2Csymbol%2Clast_px%2Cpx_change%2Cpx_change_rate%2Chigh_px%2Clow_px%2Cweek_52_high%2Cweek_52_low%2Cprice_precision%2Cupdate_time&cursor=0
https://api.wallstcn.com/apiv1/finance/macrodatas?start=1608048000&end=1608134399
https://api-ddc.wallstcn.com/market/real?prod_code=US500.OTC%2C000001.SS%2CEURUSD.OTC%2CUSDJPY.OTC%2CUS10YR.OTC%2C399001.SZ%2C399006.SZ&fields=prod_name%2Clast_px%2Cpx_change%2Cpx_change_rate%2Cprice_precision%2Csecurities_type
https://api-ddc.wallstcn.com/market/real?fields=symbol%2Cpx_change%2Cpx_change_rate%2Cprice_precision%2Cprod_name&prod_code=600375.SS%2C601127.SS
http://xuangubao.cn/
https://api.xuangubao.cn/api/pc/panzhongfengkou?limit=30&page=1
https://api.xuangubao.cn/q/quote/v1/real
http://xuangubao.cn/subjects
http://xuangubao.cn/
https://flash-api.xuangubao.cn/api/stage2/plate/top_info?count=9&fields=all
https://flash-api.xuangubao.cn/api/pool/detail?pool_name=limit_up
https://api.xuangubao.cn/api/pc/fastSubject
https://api.xuangubao.cn/api/pc/msgs?headmark=1489472187&limit=30&subjids=9,469,35,10
https://api-ddc-wscn.xuangubao.cn/market/real?fields=prod_name,last_px,px_change,px_change_rate,symbol,trade_status&prod_code=600257.SS,600097.SS,002447.SZ,600702.SS,603290.SS,600360.SS,600746.SS,600623.SS,600776.SS,002017.SZ,000011.SZ,000070.SZ,600511.SS,600196.SS,603986.SS,688008.SS
https://api-ddc-wscn.xuangubao.cn/extract/news_event/preview?message_ids=809721,809718,809710,809705
https://flash-api.xuangubao.cn/api/plate/data?fields=plate_id,plate_name,fund_flow,rise_count,fall_count,stay_count,limit_up_count,core_avg_pcp,core_avg_pcp_rank,core_avg_pcp_rank_change,top_n_stocks,bottom_n_stocks&plates=53556594,20621170,16842834,16961441,16930590,38499865,19384882,18469582,62120753,5364594,22431937,21277137,651982,63576990,1008158,36001721,17412529,19218721,6681777,37869777,25019689,38053809,17452705,16950418,16844702,16868321,387225,16847921,20054814,66814321
'''.split()


def get_url(url):
    print url
    resp = get(url)
    jo = resp.json()
    return jo

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
    return df

def wscn_market_trend(stocks):    
    fields ='tick_at%2Cclose_px%2Cavg_px%2Cturnover_volume%2Cturnover_value%2Copen_px%2Chigh_px%2Clow_px%2Cpx_change%2Cpx_change_rate'
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
    fields = 'tick_at%2Copen_px%2Cclose_px%2Chigh_px%2Clow_px%2Cturnover_volume%2Cturnover_value%2Caverage_px%2Cpx_change%2Cpx_change_rate%2Cavg_px%2Cma2'
    url = 'https://api-ddc.wallstcn.com/market/kline?prod_code={0}&tick_count=512&period_type={1}&fields={2}'.format(stks,secs,fields)
    jo = get_url(url)
    candle = jo['data']['candle']
    fields = jo['data']['fields']
    result_dic = OrderedDict()
    for tick,data in candle.items():
        df = pd.DataFrame(data['lines'],columns=fields)
        df['tick_ts'] = df['tick_at'].apply(to_timestamp)
        df.set_index(df['tick_at'],inplace=True)
        print tick, df.head()
        result_dic[tick] = df
        # pdb.set_trace()
    return result_dic
   
def wscn_market_real(stocks=None):
    stks = 'US500.OTC%2C000001.SS%2CEURUSD.OTC%2CUSDJPY.OTC%2CUS10YR.OTC%2C399001.SZ%2C399006.SZ'
    if stocks:
        stks='%2C'.join(stocks)
    fields='prod_name%2Clast_px%2Cpx_change%2Cpx_change_rate%2Cprice_precision%2Csecurities_type'
    url='https://api-ddc.wallstcn.com/market/real?prod_code={0}&fields={1}'.format(stks,fields)
    jo = get_url(url)
    snapshot = jo['data']['snapshot']
    fields = jo['data']['fields']
    df = pd.DataFrame.from_dict(snapshot,orient='index',columns=fields)
    # pdb.set_trace()
    print df
    return df 
    
def wscn_market_rank():
    fields = 'prod_name%2Cprod_en_name%2Cprod_code%2Csymbol%2Clast_px%2Cpx_change%2Cpx_change_rate%2Chigh_px%2Clow_px%2Cweek_52_high%2Cweek_52_low%2Cprice_precision%2Cupdate_time'
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
    
    
def xgb_subject(url='https://xuangubao.cn/subject/151'):
    'https://api.xuangubao.cn/api/pc/subj/151?Mark=1606996991&limit=20'
    r=get(url)
    
    
def xgb_headmark():
    dt=''
    r=get('https://api.xuangubao.cn/api/pc/msgs?%slimit=50&subjids=9,469,35,10'%dt)
    jo = r.json()
    jsonpath_expr = parse('$.NewMsgs[*]')
    res = OrderedDict()
    for i,match in enumerate(jsonpath_expr.find(jo) ):        
        jo = match.value
        # print u'/'.join(jieba.analyse.textrank(jo['Title']+' '+jo['Summary'], topK=20, withWeight=False, allowPOS=('ns', 'n')) ).encode('gbk')
        ts,title,summary =jo['CreatedAt'],jo['Title'],jo['Summary']        
        stocks= jo.get('Stocks',)
        res['[%s]%s'%(ts,title)] = {'title':title,'ts':ts,'summary':summary,'stocks':stocks}        
    return res
        

def xgb_fastsubject():
    r = get('https://api.xuangubao.cn/api/pc/fastSubject')
    jo= r.json()
    res = OrderedDict()
    for elm in jo:        
        print js_dumps(elm)        
    return res
    
def xgb_top_info():
    r= get('https://flash-api.xuangubao.cn/api/stage2/plate/top_info?count=9&fields=all')
    jo = r.json()
    res = OrderedDict()
    for elm in jo['data']['top_plate_info']: 
        key = elm['plate_name']
        res[key] = elm
    return res

if __name__ =='__main__':
    stks = ['600438.SS','AMD.NASD','STWD.NYSE','TSLA.NASD','01818.HKEX']
    # wscn_content_info_flow()
    # wscn_content_lives('a-stock')
    # wscn_market_trend(stks)
    # wscn_market_kline(stks,days=30)
    # wscn_market_kline(stks,secs=60)
    # wscn_market_real(stks)
    # wscn_market_real()
    # wscn_finance_macrodatas(1,2)