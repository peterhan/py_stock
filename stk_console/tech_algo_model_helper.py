import cPickle as pickle
import os
import pdb
import glob


from collections import OrderedDict,defaultdict
from collections import Counter
import pandas as pd

from tech_algo_analyse import DEFAULT_COMBO_LIST

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
        # print fr['boll_stage=>pchg_10d']['factor_df']
        # print fr['vswap_stage=>pchg_1d']['factor_df']
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
    df = ts.get_hist_data(tick)
    df['date'] = df.index
    ##
    tinfo,tdf = tech_analyse(df)    
    cinfo,cdf = candle_analyse(df)
    df = pd.concat([df,tdf,cdf],axis=1)
    res = [{'code':tick,'info':{}
        ,'tech':tinfo,'cdl':cinfo }]
    df,factor_results,pstr = catboost_process(tick,df)
 
def batch_run_model():    
    import ConfigParser
    fname = 'stk_console.v01.ini'
    conf  = ConfigParser.ConfigParser()
    conf.readfp(open(fname))
    conf_tks  = OrderedDict(conf.items('cn-ticks'))
    
    ticks = conf_tks['holding'].split(' ')
    tick = ticks[0]
    from multiprocessing import Pool
    p = Pool(4)
    res=p.map(run_tick_model,ticks)


    
if __name__ == '__main__':
    batch_run_model()
    # stat_model()