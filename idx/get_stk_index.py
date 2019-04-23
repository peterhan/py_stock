import requests
import tushare as ts
import pdb
shurl='http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1'
szurl='http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&random=0.07211526179588434'
# fh = requests.get(shurl)
# pdb.set_trace()
df = ts.get_stock_basics()
df.to_csv('stock_index.csv')