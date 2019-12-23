import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tushare as ts
import talib as ta

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format


stks='600519 601012 600438 601318 600818 600438 510600 603288 600340 518880 601138 002475 600410 000681 000672 300012 002475 002236'