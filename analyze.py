import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import tushare as ts

fname='tmp.csv'
# df = ts.get_tick_data('600868',date='2017-01-13')
# df = ts.get_realtime_quotes('600868')
# df.to_csv(fname,encoding ='utf8' )
df=pd.DataFrame.from_csv(fname)
df.index= df.time
df.iloc[1]