import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tushare as ts
import talib as ta

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',80)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format