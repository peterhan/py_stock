import urllib2
import json
import bs4
import pdb

token = 'eyJhbGciOiJIUzI1NiIsIlR5cGUiOiJKd3QiLCJ0eXAiOiJKV1QifQ.eyJwYXNzd29yZCI6IjY0ODU5MTQzNSIsInVzZXJOYW1lIjoiYmpidXMiLCJleHAiOjE2MjE3MjA4MDF9.fiP0eWDkEb8jZ4V9JIpwkt9vIJuhFsD7DuBaR8S1ers'

def get_json(url):
    fd  = urllib2.urlopen(url)
    txt = fd.read()
    # pdb.set_trace()
    jo = json.loads(txt)
    print json.dumps(jo,indent=2,ensure_ascii=False).encode('gbk')
    return jo


def query_lineno(keyword):
    url = 'http://www.bjbus.com/api/api_etaline_list.php?hidden_MapTool=busex2.BusInfo&city=%25u5317%25u4EAC&pageindex=1&pagesize=30&fromuser=bjbus&datasource=bjbus&clientid=9db0f8fcb62eb46c&webapp=mobilewebapp&what={keyword}'.format(keyword=keyword)
    get_json(url)
    
def query_station(lineno):
    url = 'http://www.bjbus.com/api/api_etastation.php?lineId={lineno}&token={token}'.format(lineno=lineno,token=token)
    get_json(url)
    
def query_etatime(lineno,station):
    url = 'http://www.bjbus.com/api/api_etartime.php?conditionstr={lineno}-{station}&token={token}'\
        .format(lineno=lineno,station=station,token=token)
    get_json(url)


hlg_zj_681='000000058203710'
hdzj='110100014273002'
sdqd='110100014273018'
hlg_zj_681='000000058203711'
hdzj='110100015885040'
sdqd='110100015885025'
    
query_lineno('681')
query_station(hlg_zj_681)
query_etatime(hlg_zj_681,hdzj)
# query_etatime(hlg_zj_681,sdqd)