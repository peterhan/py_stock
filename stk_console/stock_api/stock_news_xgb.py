from requests import get,post
from bs4 import BeautifulSoup
import pdb
import pandas as pd
from collections import OrderedDict
from matplotlib import pyplot as plt
from jsonpath_rw import jsonpath,parse
if __name__ == '__main__':
    sys.path.append('..')
from stk_util import ts2unix,js_dumps,gen_random,to_timestamp,DATE_FORMAT,flatten_json,dict_selector




class StockNewsXGB():
    def __init__(self):
        self.urls='''http://xuangubao.cn/
http://xuangubao.cn/subjects
http://xuangubao.cn/zhutiku
http://xuangubao.cn/
https://api.xuangubao.cn/q/quote/v1/real
https://api.xuangubao.cn/api/pc/fastSubject
https://api.xuangubao.cn/api/pc/panzhongfengkou?limit=30&page=1
https://api.xuangubao.cn/api/pc/msgs?headmark=1489472187&limit=30&subjids=9,469,35,10
https://api-ddc-wscn.xuangubao.cn/market/real?fields=prod_name,last_px,px_change,px_change_rate,symbol,trade_status&prod_code=600257.SS,600097.SS,002447.SZ,600702.SS,603290.SS,600360.SS,600746.SS,600623.SS,600776.SS,002017.SZ,000011.SZ,000070.SZ,600511.SS,600196.SS,603986.SS,688008.SS
https://api-ddc-wscn.xuangubao.cn/market/real?fields=prod_name,last_px,px_change,px_change_rate,symbol,trade_status,market_type&prod_code=600877.SS,600816.SS,600006.SS,688005.SS,603025.SS,000995.SZ,603863.SS,600308.SS,600987.SS,600448.SS
https://api-ddc-wscn.xuangubao.cn/extract/news_event/preview?message_ids=809721,809718,809710,809705

https://flash-api.xuangubao.cn/api/stage2/plate/top_info?count=9&fields=all
https://flash-api.xuangubao.cn/api/pool/detail?pool_name=limit_up
https://flash-api.xuangubao.cn/api/plate/rank?field=core_avg_pcp&type=0 [0-3]
https://flash-api.xuangubao.cn/api/plate/data?fields=plate_id,plate_name,fund_flow,rise_count,fall_count,stay_count,limit_up_count,core_avg_pcp,core_avg_pcp_rank,core_avg_pcp_rank_change,top_n_stocks,bottom_n_stocks&plates=53556594,20621170,16842834,16961441,16930590,38499865,19384882,18469582,62120753,5364594,22431937,21277137,651982,63576990,1008158,36001721,17412529,19218721,6681777,37869777,25019689,38053809,17452705,16950418,16844702,16868321,387225,16847921,20054814,66814321
https://flash-api.xuangubao.cn/api/surge_stock/plates/info?plate_ids=26021321,2900690,21969081,17731137,24291465,34490066,16888094,16813522,15864050,64731897,4343649,21051521,16907470,18722817,16861993,2525138,16787698,1640169,37268510,13011026,26676721,61407774,31003602,26543321,64879134,34316942,12679250,36489377,25638417,60280094
https://baoer-api.xuangubao.cn/api/v2/tab/recommend?module=trending_plates'''.split('\n')
        self.flashapi = 'https://flash-api.xuangubao.cn/api'
        self.ddcwscn = 'https://api-ddc-wscn.xuangubao.cn'
        self.xgbapi  = 'https://api.xuangubao.cn/api'
        self.debug = False
        self.debug = True
        pass
        
    def get_json(self, url):
        print url
        resp = get(url)
        jo = resp.json()
        return jo
    
    def top_info(self):
        url = self.flashapi + '/stage2/plate/top_info?count=9&fields=all'
        jo  = self.get_json(url)        
        rows = []
        def gen_rows(plate_type,stock_type):
            for elm in jo['data'][plate_type]:
                bdat = dict_selector(elm,mode='plain')
                bdat['plate_type'] = plate_type
                bdat['stock_type'] = stock_type
                for item in elm[stock_type]['items']:
                    item.update(bdat)
                    yield item                    
        for row in gen_rows('top_plate_info','led_rising_stocks'):
            rows.append(row)
            
        for row in gen_rows('bottom_plate_info','led_falling_stocks'):
            rows.append(row)

        df = pd.DataFrame.from_records(rows)
        if self.debug: pdb.set_trace()
        return df
        
    def pool_detail(self):
        url = self.flashapi+'/pool/detail?pool_name=limit_up'
        jo = self.get_json(url)
        # dic = flatten_json(jo)
        rows = []
        for elm in jo['data']:
            bdat = dict_selector(elm,mode='plain')
            for item in elm['surge_reason']['related_plates']:
                item.update(bdat)
                rows.append(item)
        df = pd.DataFrame.from_records(rows)
        if self.debug: pdb.set_trace()
        return df
        
    def plate_rank(self,type):
        url = self.flashapi+'/plate/rank?field=core_avg_pcp&type={0}'.format(type)
        jo = self.get_json(url)
        rows = map(str,jo['data'])
        # dic = flatten_json(jo['data'])
        # if self.debug: pdb.set_trace()
        return rows
        
    def plate_data(self,plates):
        fields ='plate_id,plate_name,fund_flow,rise_count,fall_count,stay_count,limit_up_count,core_avg_pcp,core_avg_pcp_rank,core_avg_pcp_rank_change,top_n_stocks,bottom_n_stocks'
        url = self.flashapi+'/plate/data?fields={0}&plates={1}'.format(fields,','.join(plates))
        jo = self.get_json(url)
        rows = []
        dic = flatten_json(jo)
        for plate_id,elm in jo['data'].items():
            bdat = dict_selector(elm,mode='plain')
            bdat['key_plate'] = plate_id
            for item in elm['bottom_n_stocks']['items']:
                item.update(bdat)
                rows.append(item)
        df = pd.DataFrame.from_records(rows)
        if self.debug: pdb.set_trace()
        return df
        
    def surge_stock(self,plates):
        url = self.flashapi+'/surge_stock/plates/info?plates={0}'.format(','.join(plates))
        jo = self.get_json(url)
        dic = flatten_json(jo)
        if self.debug: pdb.set_trace()
        
    def headmark(self):
        dt=''
        r=get('https://api.xuangubao.cn/api/pc/msgs?%slimit=50&subjids=9,469,35,10'%dt)
        jo = r.json()
        jsonpath_expr = parse('$.NewMsgs[*]')
        res = OrderedDict()
        for i,match in enumerate(jsonpath_expr.find(jo) ):        
            jo = match.value            
            ts,title,summary =jo['CreatedAt'],jo['Title'],jo['Summary']        
            stocks= jo.get('Stocks',)
            res['[%s]%s'%(ts,title)] = {'title':title,'ts':ts,'summary':summary,'stocks':stocks}        
        return res
            

    def fastsubject(self):
        r = get('https://api.xuangubao.cn/api/pc/fastSubject')
        jo= r.json()
        res = OrderedDict()
        for elm in jo:        
            print js_dumps(elm)        
        return res

if __name__ =='__main__':
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    pd.set_option('display.width',None)
    pd.options.display.float_format = '{:.2f}'.format

    stks = ['600438.SS','AMD.NASD','STWD.NYSE','TSLA.NASD','01818.HKEX']
    xgb = StockNewsXGB()
    xgb.debug = False
    # xgb.pool_detail()
    # xgb.top_info()
    plates= xgb.plate_rank('0')
    xgb.plate_data(plates)
    # xgb.surge_stock(plates)