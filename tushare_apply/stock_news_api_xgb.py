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

urls='''http://xuangubao.cn/
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
    
def xgb_subject():
    url='https://api.xuangubao.cn/api/pc/subj/151?Mark=1606996991&limit=20'
    jo = get_url(url)
    pdb.set_trace()
    
    
    
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
    xgb_subject()