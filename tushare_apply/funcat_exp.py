import pdb
import tushare as ts
import pandas as pd
import talib as ta
import statsmodels.api as sm
from funcat import *
from matplotlib import pyplot as plt
from matplotlib import rcParams
rcParams['figure.figsize'] = (24, 12)

T("20170104")
# 设置关注股票为上证指数
S("000001.XSHG")

# 打印 Open High Low Close
print(O, H, L, C)

# https://github.com/cedricporter/funcat
M1, M2 = 14, 6

TR = SUM(MAX(MAX(HIGH - LOW, ABS(HIGH - REF(CLOSE, 1))), ABS(LOW - REF(CLOSE, 1))), M1)
HD = HIGH - REF(HIGH, 1)
LD = REF(LOW, 1) - LOW

DMP = SUM(IF((HD > 0) & (HD > LD), HD, 0), M1)
DMM = SUM(IF((LD > 0) & (LD > HD), LD, 0), M1)
DI1 = DMP * 100 / TR
DI2 = DMM * 100 / TR
ADX = MA(ABS(DI2 - DI1) / (DI1 + DI2) * 100, M2)
ADXR = (ADX + REF(ADX, M2)) / 2

print(DI1, DI2, ADX, ADXR)