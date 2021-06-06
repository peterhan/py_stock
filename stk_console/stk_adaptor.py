#!coding:utf8
import pdb
import ConfigParser
import os,sys
import pickle
from collections import OrderedDict

import tushare as ts
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf

from stock_api import StockNewsFUTUNN
from stock_api import StockNewsFinViz

class StockAdaptor(object):
    def __init__(self,cache=False):
        self._ftnn = StockNewsFUTUNN()
        self._finvz = StockNewsFinViz()
        
                
    def get_tick_data(self,tick,mode='ts',cycle='day'):
        
        if mode in ('ts','tushare'):
            df = self.get_tick_data_ts(tick)
        elif mode in ('ts_hist','tushare_hist'):
            df = self.get_hist_data_ts(tick)
        elif mode in ('ft','ftnn'):            
            df = self._ftnn.get_kline(tick, cycle) 
        elif mode in ('yf','yfinance'):
            df = None
        elif mode in ('alvt','alpha_vantage'):
            df = None        
        return df
            
    def get_tick_data_ts(self,tick):
        df = ts.get_k_data(tick)
        df['date'] = df['date']
        df['volume'] = (df['volume']*100)
        return df
    
    def get_hist_data_ts(self,tick):
        df = ts.get_hist_data(tick)
        df['date'] = df.index
        df = df.sort_index()
        df['volume'] = (df['volume']*100)
        return df
 
    def load_ticks(self,conf_fname,section):        
        conf  = ConfigParser.ConfigParser()
        conf.readfp(open(conf_fname))
        conf_tks  = OrderedDict(conf.items(section))
        return conf_tks
    
    
class CachedStockAdaptor(StockAdaptor):
    def __init__(self):        
        self.cfname = 'c_stk_adaptor.cache'      
        if  not os.path.exists(self.cfname):
            self.cache = {}
        else:
            self.cache = pickle.load(open(self.cfname))
        
    def __enter__(self):
        print '[enter CachedStockAdaptor]'
        return self
        
    def get_tick_data(self,tick,mode='ts',cycle='day'):
        key = '%s-%s-%s'%(tick,mode,cycle)
        if key in self.cache:
            print '[Load cache key]:',key
            return self.cache[key]
        else:
            print '[Remote call key]:',key
            df = super(self.__class__, self).get_tick_data(tick,mode,cycle)
            self.cache[key] = df
            return df
        
    def __exit__(self, exc_type, exc_value, traceback):
        print '[exit CachedStockAdaptor]', exc_type,exc_value,traceback
        pickle.dump(self.cache,open(self.cfname,'w'))
        print '[dump finish]'
    
if __name__ == '__main__':
    with CachedStockAdaptor() as sa:
        # print sa
        df1 = sa.get_tick_data('600438','ts')
        # df2 = sa.get_tick_data('600438','ftnn')
        # df3 = sa.get_tick_data('tsla','ftnn')
        # df4 = sa.get_tick_data('600438','ts_hist')
        print df1.iloc[-1]
        # print df2.iloc[-1]
        # print df3.iloc[-1]
        pdb.set_trace()