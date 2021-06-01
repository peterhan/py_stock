#!coding:utf8
import pandas as pd
import numpy as np
import traceback
import pdb
from stk_util import time_count
from collections import OrderedDict

## algo_analyse
@time_count
def caculate_indicator(df, i_stages, target_col):
    # i_stages = cdl_pat_names
    # adf = df[['turnover','rsi','dif_ag','rsi_ag','dif','k_ag','j_ag','d_ag','dea']+i_stages].copy()
    adf = df[['rsi','dif_ag','rsi_ag','dif','k_ag','j_ag','d_ag','dea']+i_stages].copy()
    bencols = []
    bencols.append(target_col)
    i=int(target_col.split('_')[-1].strip('d'))
    adf[target_col] =  (df['close'] / df['close'].shift(i) -1)*100
    #for i in (1,3,5,7,10,15):
    ## for i in (1,3,5,7):
    #    bname = 'p_change_%sd'%i
    #    # pdb.set_trace()
    #    adf[bname] = (df['close'] / df['close'].shift(i) -1)*100
    #    bencols.append(bname)
    # adf['p_change_20d'] = df['p_change'].shift(-20)
    # adf['p_change_30d'] = df['p_change'].shift(-30)
    # print adf.corr()
    
    adf.to_csv("veri/train_dump.csv")
    def stat_gp(gp):
        return gp.agg([np.size, np.mean, np.std, np.max, np.min]) 
        # gp.agg({'text':'size', 'sent':'mean'}) \        
        #.rename(columns={'text':'count','sent':'mean_sent'}) \
        #.reset_index()
        #.iloc[:,offset:]
    # df = stat_gp(adf.groupby(['macd_stage','sma_stage','rsi_stage'] )[bencols])
    # print df
    # df.to_csv('veri/comb.csv')
    for stage in i_stages:
        df = stat_gp(adf.groupby(stage )[bencols])
        # print df
        # df.to_csv('veri/'+stage+".csv")       
    # pdb.set_trace()
    return adf


def rmse(targets,predictions):
    return np.sqrt(((predictions - targets) ** 2).mean())

@time_count    
def predict_cat_boost(fit_model, adf,factor_combo,target_col,test_len=200):
    from catboost import CatBoostRegressor
    factor_results = {}
    test_pool = adf[factor_combo][-1*test_len:]
    test_labels = adf[target_col].fillna(0)[-1*test_len:]
    model = fit_model
    # model = CatBoostRegressor(learning_rate=1, depth=6, loss_function='RMSE',cat_features=i_stages)
    # model.load_model('first.model')
    # preds_class = model.predict(test_pool, prediction_type='Class')
    # preds_proba = model.predict(test_pool, prediction_type='Probability')
    preds_raw_vals = model.predict(test_pool, prediction_type='RawFormulaVal')
    # pdb.set_trace()
    
    feat = [] 
    test_pool['date']= test_pool.index
    #
    try:
        df_gg = test_pool.groupby(factor_combo).count()
        df_gg = df_gg.rename(columns={'date':'date_count'})
        data_rows = df_gg.index.to_list()
        if len(factor_combo)==1:
            data_rows = map(lambda x:[x],data_rows)
        score = model.predict(data_rows)
        df_gg['score_cb']=score
    except:
        traceback.print_exc()
        # pdb.set_trace()
    pdf  = df_gg.sort_values('score_cb',ascending=False)
    
    res_key=':'.join (factor_combo)+'=>'+target_col
    factor_results[res_key] = {}
    
    check_result=factor_results[res_key]
    check_result['factor_df']=pdf
    
    # print preds_raw_vals,test_labels

    rmsev = rmse( np.sign(test_labels.values), np.sign(preds_raw_vals) )
    check_result['rmsev']=rmsev
    pos_neg = pd.Series(np.sign(test_labels*preds_raw_vals)*10,index=test_labels.index)
    pnvc = pos_neg.value_counts()    
    check_result['correct_rate']=pnvc[10.0]*1.0/sum(pnvc.values)*100    
    return factor_results

@time_count
def train_cat_boost(adf,factor_combo,target_col):
    from catboost import CatBoostRegressor
    dataset = adf[factor_combo][:]
    train_labels = adf[target_col].fillna(0)[:]
    model = CatBoostRegressor(learning_rate=1, depth=6, loss_function='RMSE',cat_features=factor_combo)
    try:
        fit_model = model.fit(dataset, train_labels, verbose=0)
    except:
        traceback.print_exc()

    # print(fit_model.get_params())
    # fit_model.save_model('first.model')
    return fit_model
    # pdb.set_trace()

@time_count
def cat_boost_factor_verify(df,target_days = ['5d'],factor_combo_list=None):   
    if factor_combo_list is None:
        factor_combo_list = [ 
        ['roc_stage'] 
        # ,['macd_stage','rsi_stage']
        ,['vwap_stage','ema_stage'],['week_stage','ema_stage'],['week_stage']
        ,['CDLScore']
        ,['ema_stage']  ,['sma_stage'],['volume_ema_stage'] ,['volume_sma_stage']  ,['macd_stage'] ,['cci_stage'] 
        ,['rsi_stage']  ,['ma_es_dif_stage'],['boll_stage'] ,['kdj_stage'] ,['mom_stage']
        ,['aroon_stage'],['vswap_stage'],['vwap_stage']
        ]
    factor_results = {}
    o_factor_results = OrderedDict()
    for target_col in ['pchg_%s'%target_day for target_day in target_days]:    
        for factor_combo in factor_combo_list:
            try:
                if len(target_days)>=2:
                    print '[Training]:',factor_combo,target_col
                adf = caculate_indicator(df, factor_combo, target_col)
                fit_model = train_cat_boost(adf,factor_combo,target_col)
                pred_res = predict_cat_boost(fit_model ,adf,factor_combo,target_col)
                factor_results.update(pred_res)
            except:
                traceback.print_exc()
    for key,check_result in sorted(factor_results.items(),key=lambda v:v[1]['correct_rate'],reverse=True):
        o_factor_results[key] =  check_result
    
    return o_factor_results


def append_factor_result_to_df(df,factor_results):
    for algo_key,factor_info in factor_results.items():
        # pdb.set_trace()
        fdf = factor_info['factor_df']
        est_measure = 'cr:%0.2f%%,rms:%0.2f'%(factor_info['correct_rate'],factor_info['rmsev'])
        fdf['est_accu'] = est_measure
        fdf['est_accu'] = fdf['est_accu']+',cnt:'+fdf['date_count'].astype(str)
        fdf.drop('date_count',axis=1)
        fdf = fdf.add_prefix(algo_key+'.')
        key_columns = algo_key.split('=>')[0].split(':')
        df = df.join(fdf,on=key_columns)
    return df
    
def print_factor_result(o_factor_results,topn=5):    
    print ''
    for key,check_result in o_factor_results.items()[:topn:1]:            
        print '[%s]'%(key)
        print check_result['factor_df']
        print 'rmse: %0.2f'%check_result['rmsev']
        print 'correct_rate: %0.2f%%'%(check_result['correct_rate'])
        print ''
        
def print_factor_judge_result(df,last_n=1,top_n=3):    
    last_type = ''
    tcnt = 0
    for row in df.iloc[-1*last_n:].iterrows():
        odict = row[1].to_dict(into=OrderedDict)
        for key,vlu in odict.items():
            if key.find('=>')==-1:
                continue
            if key.find('.date_count')!=-1:
                continue
            t_type=key.split('.')[0]
            if t_type!=last_type:
                tcnt+=1
                last_type=t_type
                print ''
            if tcnt>top_n:
                break
            print '[%s]: '%key,vlu
        
def main():
    pass
        
if __name__ == '__main__':    
    main()