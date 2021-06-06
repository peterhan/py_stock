#!coding:utf8
import cPickle as pickle
import os
import pdb
import glob
import cPickle as pickle

from collections import OrderedDict,defaultdict,Counter
import pandas as pd

from tech_analyse import DEFAULT_COMBO_LIST
import tushare as ts
from tech_analyse import tech_analyse,candle_analyse,catboost_process
from tech_algo_analyse import add_target_day_out_col

def filter_fr(factor_result,parts):
    od  = OrderedDict()
    for k,v in factor_result.items():
        for part in parts.split(','):
            if k.find(part)!=-1:
                od[k]=v
    return od

def stat_model():    
    cnt = defaultdict(Counter)
    path='model_catboost.cache'
    frd = {}
    for fname in glob.glob(path+'/*.factor.*.model'):
        # print fname
        keypair = os.path.split(fname)
        tick = keypair[1].split('.')[0]
        fr = pickle.load(open(fname))
        fr = filter_fr(fr,'=>')
        frd[tick]=fr
        top = fr.keys()[:5]
        last = fr.keys()[-5:]
        print tick,len(fr),top,last
        cnt['top'].update(top)
        cnt['last'].update(last)
        #,fr.values()[:5]
        # print fr
        # print fr['vswap_stage=>pchg_1d']['factor_df']
        # break
    print '\n\nstat_top:', cnt['top']

    print '\n\nstat_last:',cnt['last']
    pdb.set_trace()
 
 
def run_multi_ticks_model(ticks,tgname,fc_list,tdays):    
    dfs = []
    from stk_adaptor import CachedStockAdaptor
    with CachedStockAdaptor() as csa:
        for tick in ticks:
            tdf = get_tech_df(csa, tick,fc_list,tdays)
            dfs.append( tdf )
    print tdf.columns.to_list()
    df = pd.concat(dfs,axis=0) 
    # pdb.set_trace()
    apply_model(tgname+'-multi-ticks',df,fc_list,tdays)
    
def run_tick_model(tick,fc_list,tdays):    
    df = get_tech_df(tick,fc_list,tdays)
    apply_model(tick,df,fc_list,tdays)
    
def get_tech_df(cached_sa, tick,fc_list,tdays):

    print tick
    ##
    # df = ts.get_k_data(tick)
    df = cached_sa.get_tick_data(tick,'ts')
    # pdb.set_trace()
    # df = ts.get_hist_data(tick)
    # df['date'] = df.index
    # df = df.sort_index()
    ##
    tinfo,tdf = tech_analyse(df)    
    cinfo,cdf = candle_analyse(df)
    df = pd.concat([df,tdf,cdf],axis=1)
    df = df.loc[:,~df.columns.duplicated()]
    res = [{'code':tick,'info':{}
        ,'tech':tinfo,'cdl':cinfo }]
    # pdb.set_trace()
    df = add_target_day_out_col(df, tdays)
    # print factor_results
    return df
    
def apply_model(tick,df,fc_list,tdays):
    df,factor_results,pstr = catboost_process(tick,df,top_n=50,factor_combo_list=fc_list,target_days=tdays,no_cache=True)
    print pstr
    print factor_results
 
def batch_run_model():    
    import ConfigParser
    fname = 'stk_console.v01.ini'
    conf  = ConfigParser.ConfigParser()
    conf.readfp(open(fname))
    conf_tks  = OrderedDict(conf.items('cn-ticks'))
    
    tgname = 'holding'
    tgname = 'mao50'
    # tgname = 'mao20'
    ticks = conf_tks[tgname].split(' ')
    
    # ticks = ['600004']
    fc_list=[['macd_stage']]
    fc_list= DEFAULT_COMBO_LIST    
    fc_list=[['macd_stage']]
    fc_list= DEFAULT_COMBO_LIST
    fc_list = ['CDLList'.split('\t')]
    a=['date', 'open', 'close', 'high', 'low', 'volume', 'code', 'mse', 'boll_low', 'boll_mid', 'boll_up', 'bolllow_ag', 'bollmid_ag', 'bollup_ag', 'boll_stage', 'vwap', 'vwap_stage', 'vswap', 'vswap_stage', 'maroc', 'maroc_ag', 'roc', 'roc_ag', 'roc_stage', 'ag_mamom', 'ag_mom', 'mamom', 'mom', 'mom_cross_stage', 'mom_stage', 'dif_ag', 'dif', 'dea_ag', 'dea', 'macd_stage', 'macd_hist', 'EMA3', 'SMA3', 'EMA5', 'SMA5', 'EMA20', 'SMA20', 'EMA60', 'SMA60', 'ma_es_dif_stage', 'ema_stage', 'sma_stage', 'volume_EMA3', 'volume_SMA3', 'volume_EMA5', 'volume_SMA5', 'volume_EMA20', 'volume_SMA20', 'volume_EMA60', 'volume_SMA60', 'volume_ma_es_dif_stage', 'volume_ema_stage', 'volume_sma_stage', 'week_stage', 'rsi', 'rsi_ag', 'rsi_stage', 'd_aag', 'd_ag', 'j_aag', 'j_ag', 'k_aag', 'k_ag', 'kdj_d', 'kdj_j', 'kdj_k', 'p_ag', 'kdj_stage', 'cci', 'cci_ag', 'cci_stage', 'aroon_down', 'aroon_up', 'aroon_stage', '2CROWS', '3BLACKCROWS', '3INSIDE', '3LINESTRIKE', '3OUTSIDE', '3STARSINSOUTH', '3WHITESOLDIERS', 'ABANDONEDBABY', 'ADVANCEBLOCK', 'BELTHOLD', 'BREAKAWAY', 'CLOSINGMARUBOZU', 'CONCEALBABYSWALL', 'COUNTERATTACK', 'DARKCLOUDCOVER', 'DOJI', 'DOJISTAR', 'DRAGONFLYDOJI', 'ENGULFING', 'EVENINGDOJISTAR', 'EVENINGSTAR', 'GAPSIDESIDEWHITE', 'GRAVESTONEDOJI', 'HAMMER', 'HANGINGMAN', 'HARAMI', 'HARAMICROSS', 'HIGHWAVE', 'HIKKAKE', 'HIKKAKEMOD', 'HOMINGPIGEON', 'IDENTICAL3CROWS', 'INNECK', 'INVERTEDHAMMER', 'KICKING', 'KICKINGBYLENGTH', 'LADDERBOTTOM', 'LONGLEGGEDDOJI', 'LONGLINE', 'MARUBOZU', 'MATCHINGLOW', 'MATHOLD', 'MORNINGDOJISTAR', 'MORNINGSTAR', 'ONNECK', 'PIERCING', 'RICKSHAWMAN', 'RISEFALL3METHODS', 'SEPARATINGLINES', 'SHOOTINGSTAR', 'SHORTLINE', 'SPINNINGTOP', 'STALLEDPATTERN', 'STICKSANDWICH', 'TAKURI', 'TASUKIGAP', 'THRUSTING', 'TRISTAR', 'UNIQUE3RIVER', 'UPSIDEGAP2CROWS', 'XSIDEGAP3METHODS', 'CDLList', 'CDLScore', 'pchg_10d']
    a={'LONGLEGGEDDOJI:100': 101, 'DOJI:100': 101, 'SPINNINGTOP:100': 85, 'RICKSHAWMAN:100': 76, 'SPINNINGTOP:-100': 72, 'LONGLINE:100': 71, 'BELTHOLD:-100': 60, 'LONGLINE:-100': 56, 'BELTHOLD:100': 54, 'HIGHWAVE:100': 50, 'CLOSINGMARUBOZU:100': 44, 'HIGHWAVE:-100': 39, 'HIKKAKE:100': 35, 'SHORTLINE:-100': 30, 'ENGULFING:100': 28, 'SHORTLINE:100': 28, 'ENGULFING:-100': 27, 'HARAMI:100': 23, 'HIKKAKE:-100': 22, 'CLOSINGMARUBOZU:-100': 22, 'HARAMI:-100': 21, 'HAMMER:100': 19, '3OUTSIDE:100': 16, 'HANGINGMAN:-100': 13, 'HIKKAKE:200': 12, 'DOJISTAR:-100': 12, 'MATCHINGLOW:100': 12, 'MARUBOZU:100': 11, '3OUTSIDE:-100': 10, 'DRAGONFLYDOJI:100': 9, 'HARAMICROSS:100': 9, 'GRAVESTONEDOJI:100': 9, 'TAKURI:100': 9, 'MARUBOZU:-100': 8, 'HOMINGPIGEON:100': 7, 'INVERTEDHAMMER:100': 7, 'DOJISTAR:100': 7, 'SEPARATINGLINES:-100': 6, 'HARAMICROSS:-100': 6, 'HIKKAKE:-200': 5, '3INSIDE:100': 5, 'ADVANCEBLOCK:-100': 5, 'SHOOTINGSTAR:-100': 4, 'THRUSTING:-100': 4,'sma_stage':1}
    a={'LONGLEGGEDDOJI':1,'DOJI':1,'SPINNINGTOP':1,'RICKSHAWMAN':1,'LONGLINE':1,'HIGHWAVE':1,'BELTHOLD':1,'CLOSINGMARUBOZU':1,'ENGULFING':1}
    a={'CLOSINGMARUBOZU':1,'ENGULFING':1}
    a={'CLOSINGMARUBOZU':1,'ENGULFING':1}
    a={'macd_stage':1}
    fc_list = [list(set(map(lambda x:x.split(':')[0], a.keys())))]
    
    tdays=['7d','10d','14d']
    tdays=['10d']
    tdays=['1d','3d','5d','7d','10d','14d','30d','60d']
    
    run_multi_ticks_model(ticks,tgname,fc_list,tdays)
    # pdb.set_trace()
    return
    
    use_pool =False
    if not use_pool:
        for tick in ticks:
            run_tick_model(tick,fc_list,tdays)
            break
    else:
        from multiprocessing import Pool
        p = Pool(4)
        #res=p.map(run_tick_model,ticks,fc_list,tdays)
        p.close()
        p.join()

    
if __name__ == '__main__':
    pd.set_option('display.width',None)
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    flag = ''
    # flag = raw_input('run_mode[b:batch_run_model,s:stat_model]:')
    if flag.startswith('s'):
        stat_model()
    else:
        batch_run_model()
    # raw_input('finish:')