import urllib2
import json
import bs4
import pdb
import pandas  as pd
import traceback
import sys
import re

token = ''

def get_token():
    url='http://www.bjbus.com/home/fun_rtbus.php'
    fd  = urllib2.urlopen(url)
    text = fd.read()
    for ln in text.splitlines():
        if ln.find('&token=')==-1:
            continue
        match = re.search('token\=([^\']*)',ln)
        tok = match.group(1)
        break
    return tok

def jdumps(jo):
    return json.dumps(jo,indent=2,ensure_ascii=False).encode('gbk')
    
def get_json(url):
    fd  = urllib2.urlopen(url)
    # print url
    text = fd.read()
    # pdb.set_trace()
    jo = json.loads(text)
    # print jdumps(jo)
    return jo


def query_lineno(keyword):
    url = 'http://www.bjbus.com/api/api_etaline_list.php?hidden_MapTool=busex2.BusInfo&city=%25u5317%25u4EAC&pageindex=1&pagesize=30&fromuser=bjbus&datasource=bjbus&clientid=9db0f8fcb62eb46c&webapp=mobilewebapp&what={keyword}'.format(keyword=keyword)
    return get_json(url)
    
def query_station(lineno):
    url = 'http://www.bjbus.com/api/api_etastation.php?lineId={lineno}&token={token}'.format(lineno=lineno,token=token)
    return get_json(url)
    
def query_etatime(lineno,station):
    url = 'http://www.bjbus.com/api/api_etartime.php?conditionstr={lineno}-{station}&token={token}'\
        .format(lineno=lineno,station=station,token=token)
    return get_json(url)


def df_select(df,idx=None,noselect=False):
    if not idx:
        print df
        if noselect:
            # pdb.set_trace()
            return
        idx = raw_input("[select-index]:")
    try: 
        idx = int(idx)
    except:
        return None
    row = df.iloc[idx]
    # pdb.set_trace()
    return row
    
def menu_select(line_name,line_select=None,station_select=None):
    jo = query_lineno(line_name)
    l_list = jo['response']['resultset']['data']['feature']
    lrow = df_select(pd.DataFrame(l_list), line_select)
    # pdb.set_trace()
    line,caption = lrow['id'],lrow['caption']

    jo = query_station(line)
    s_list = jo['data']
    srow = df_select(pd.DataFrame(s_list), station_select)

    station,stopName = srow['stationId'],srow['stopName']
    jo = query_etatime(line,station)
    # print jdumps(jo)
    t_list = jo['data'][0]['datas']['trip']
    print caption.encode('gbk'),'\n@',stopName.encode('gbk')
    df_select(pd.DataFrame(t_list),noselect=True)
    # pdb.set_trace()
    # query_etatime(line,sd)
    # query_etatime(line,sd)
    
if __name__ == '__main__':
    print ['93', '28', '32', '46', '76', '18', '77', '03', '88','81','14']
    print ['05 0 13']
    # menu_select('81',1,26),(1,41)    
    # menu_select('14',0,9),(1,14) 
    global token
    token = get_token()
    # sys.exit()
    while True:
        try:
            arr =raw_input('[Line Direct Station]:').split(' ')
            menu_select(*arr)
        except:
            traceback.print_exc()
            pass