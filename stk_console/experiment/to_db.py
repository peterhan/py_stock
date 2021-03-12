import tushare as ts
import sqlite3
db=sqlite3.connect("testdb.db")
df = ts.get_k_data('300333',start='2016-01-01',end='2016-12-28')
df.to_sql("newtable",db,flavor='sqlite')