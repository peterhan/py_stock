import tushare as ts
import pandas as pd

#13.397
tks=[
'510300'
,'510600'
,'510500'
,'002572'
,'002466'
,'600025'
,'600438'
,'600585'
,'300618'
,'601012'
,'600029'
,'601111'
,'600004'
,'600009'
,'601888'
,'600519'
,'601636'
]
pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)
# rdf=  ts.get_realtime_quotes(tks)
rdf=  ts.get_today_all()
print rdf
rdf = rdf.apply(pd.to_numeric,errors='ignore')
cname = df.columns
cname[3]='price'
rdf.rename(cname,inplace=True)
rdf.insert(0,'bounce',(rdf['price']-rdf['low'])/(rdf['high']-rdf['low'])*100)
rdf.insert(1,'variance',(rdf['high']-rdf['low'])/(rdf['open'])*100)
rdf.insert(2,'rate',(rdf['price']-rdf['open'])/(rdf['open'])*100)

print rdf.loc[:,:]

# fc=ts.forecast_data(2019,1)
# print fc
# ttdf = ts.get_today_ticks(tks[6])
# print ttdf[ttdf.volume>=100].groupby(ttdf.type).count()
# print ttdf[ttdf.volume>=100].groupby(ttdf.type).sum()