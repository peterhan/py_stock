import requests
import tushare as ts
import pdb
shurl='http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1'
szurl='http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&random=0.07211526179588434'
'''
http://www.sse.com.cn/assortment/fund/etf/list/
http://query.sse.com.cn/security/stock/queryExpandName.do?jsonCallBack=jsonpCallback13000&secCodes=510650%2C510660%2C510680%2C510690%2C510710%2C510760%2C510800%2C510810%2C510850%2C510880%2C510890&_=1610341008016
http://www.sse.com.cn/assortment/fund/list/etfinfo/turnover/index.shtml?FUNDID=510650
'''
# fh = requests.get(shurl)
# pdb.set_trace()
df = ts.get_stock_basics()
df.to_csv('stock_index.csv')