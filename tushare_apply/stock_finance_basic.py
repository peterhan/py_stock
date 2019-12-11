#!coding:utf8
# import pdb

import sys
import tushare as ts
import pandas as pd
import talib 
import datetime
import time
import json
from collections import OrderedDict

def analyse_balance_sheet(df):
    print df.index.values,df.columns
    print df.iloc[:,0]
    
if __name__ == '__main__':    
    df=ts.get_balance_sheet('600438')
    analyse_balance_sheet(df)
    ts.pledged_detail()
    ts.get_profit_data()
    ts.get_cash_flow()
    # df=ts.get_balance_sheet('002236')