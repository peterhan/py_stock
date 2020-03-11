import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tushare as ts
import talib as ta

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format


stks='600519 601012 600438 601318 600818 600438 603288 600340  601138 600410 000681'
etfs='518880 510600 '
idxs='sh000001 399001 399006'
hlds='300274 300012 515580'
stks1='002050'
grq= ts.get_realtime_quotes