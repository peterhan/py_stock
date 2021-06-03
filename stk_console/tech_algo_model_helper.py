import cPickle as pickle
import os
import pdb
import glob
import cPickle as pickle

from collections import OrderedDict,defaultdict,Counter
import pandas as pd

from tech_analyse import DEFAULT_COMBO_LIST

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
    for fname in glob.glob(path+'/*.factor.*.model'):
        # print fname
        key = os.path.split(fname)
        tick = key[1].split('.')[0]
        fr = pickle.load(open(fname))
        fr = filter_fr(fr,'=>')
        top = fr.keys()[:5]
        last = fr.keys()[-5:]
        print tick,len(fr),top,last
        cnt['top'].update(top)
        cnt['last'].update(last)
        #,fr.values()[:5]
        print fr
        # print fr['vswap_stage=>pchg_1d']['factor_df']
        # break
    # pdb.set_trace()
    print '\n\nstat_top\n'
    print cnt['top']

    print '\n\nstat_last\n'
    print cnt['last']
 
def run_tick_model(tick):
    import tushare as ts
    from tech_analyse import tech_analyse,candle_analyse,catboost_process
    print tick
    ##
    df = ts.get_k_data(tick)
    
    # df = ts.get_hist_data(tick)
    # df['date'] = df.index
    # df = df.sort_index()
    ##
    tinfo,tdf = tech_analyse(df)    
    cinfo,cdf = candle_analyse(df)
    df = pd.concat([df,tdf,cdf],axis=1)
    res = [{'code':tick,'info':{}
        ,'tech':tinfo,'cdl':cinfo }]
    fc_list=[['macd_stage']]
    fc_list= DEFAULT_COMBO_LIST
    tdays=['1d','3d','5d','7d','10d','14d','30d','60d']
    df,factor_results,pstr = catboost_process(tick,df,top_n=50,factor_combo_list=fc_list,target_days=tdays,no_cache=False)
    # print factor_results
    print pstr
 
def batch_run_model():    
    import ConfigParser
    fname = 'stk_console.v01.ini'
    conf  = ConfigParser.ConfigParser()
    conf.readfp(open(fname))
    conf_tks  = OrderedDict(conf.items('cn-ticks'))
    
    ticks = conf_tks['holding'].split(' ')
    # ticks = ['600004']
    use_pool =False
    if use_pool:
        from multiprocessing import Pool
        p = Pool(4)
        res=p.map(run_tick_model,ticks)
        p.close()
        p.join()
    else:
        for tick in ticks:
            run_tick_model(tick)
            break

    
if __name__ == '__main__':
    pd.set_option('display.width',None)
    pd.set_option('display.max_rows',None)
    pd.set_option('display.max_columns',80)
    flag = raw_input('run_mode[b:batch_run_model,s:stat_model]:')
    if flag.startswith('s'):
        stat_model()
    else:
        batch_run_model()
    # raw_input('finish:')