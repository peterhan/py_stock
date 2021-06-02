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