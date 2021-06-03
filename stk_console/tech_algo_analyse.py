#!coding:utf8
import pandas as pd
import numpy as np

import traceback
import pdb
from stk_util import time_count
from collections import OrderedDict


## algo_analyse
@time_count
def add_target_day_out_col(df, target_days,PREFIX_TARGET_DAY = 'pchg_'):
    direct = -1
    # pdb.set_trace()
    if df['date'].iloc[-1]<df['date'].iloc[-2]:
        direct = 1
        print '[date is decending!]'
    else:
        # print 'date is ascending'
        pass
    for target_day in target_days:
        td_name= PREFIX_TARGET_DAY+target_day
        days = int(target_day.split('_')[-1].strip('d'))
        if td_name not in df.columns:        
            df.loc[:,td_name] =  (df['close'].shift(direct*days) / df['close'] -1)*100
    # pdb.set_trace()
    return df
    


def rmse(targets,predictions):
    return np.sqrt(((predictions - targets) ** 2).mean())

@time_count    
def predict_cat_boost(fit_model, adf,factor_combo,target_col,test_len=200,round_digit=4):
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
        df_gg['score_cb']= score.round(round_digit)
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
def catboost_factor_verify(df,target_days ,factor_combo_list,PREFIX_TARGET_DAY = 'pchg_'):    
    factor_results = {}
    o_factor_results = OrderedDict()
    df = add_target_day_out_col(df,target_days)
    print '[Models to Train]:' ,len(target_days)*len(factor_combo_list)
    for target_col in [PREFIX_TARGET_DAY+'%s'%target_day for target_day in target_days]:    
        for factor_combo in factor_combo_list:
            try:
                if len(target_days)>=2:
                    print '[Training]:',factor_combo,target_col
                
                fit_model = train_cat_boost(df,factor_combo,target_col)
                pred_res = predict_cat_boost(fit_model ,df,factor_combo,target_col)
                factor_results.update(pred_res)
            except:
                traceback.print_exc()
    for key,check_result in sorted(factor_results.items(),key=lambda v:v[1]['correct_rate'],reverse=True):
        o_factor_results[key] =  check_result
    
    return o_factor_results


def join_factor_result_to_df(df,factor_results):
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

@time_count     
def get_factor_judge_result(row):
    pstr = ''
    res_dic = {}
    row_dic = row.to_dict()
    for lkey,vlu in row_dic.items():
        if lkey.find('=>')==-1:
            continue
        akey,atype = lkey.split('.',1)
        if atype=='score_cb' and not np.isnan(vlu):
            res_dic.setdefault(akey,['','',0,0,0,0])
            res_dic[akey][0] = '&'.join([str(row_dic[key]) for key in akey.split('=>')[0].split(':')])
            res_dic[akey][1] = vlu
        if atype=='est_accu' and type(vlu)==str:
            res_dic.setdefault(akey,['','',0,0,0,0])
            arr=vlu.split(',') 
            res_dic[akey][2:] = [float(e.split(':')[1].replace('%','')) for e in arr]
    nrows = []
    for k,v in res_dic.items():   
        row = k.split('=>')
        row[1] = row[1].replace('pchg_','')        
        row.extend(v)
        nrows.append(row)
    jdf = pd.DataFrame(nrows,columns=['factor','out','stage','score_cb','accu_rate','rmsev','s_cnt'])
    jdf = jdf.sort_values(['accu_rate','s_cnt'],ascending=False)
    jdf = jdf.reset_index()
    jdf = jdf[['factor','out','score_cb','accu_rate','s_cnt','rmsev','stage']]
    # pdb.set_trace()
    return jdf
    
  
@time_count       
def print_factor_result(o_factor_results,top_n=5):    
    pstr =''
    for key,check_result in o_factor_results.items()[:top_n:1]:            
        pstr+= '\n'+ '[%s]'%(key)
        pstr+= '\n'+ check_result['factor_df']
        pstr+= '\n'+ 'rmse: %0.2f'%check_result['rmsev']
        pstr+= '\n'+ 'correct_rate: %0.2f%%'%(check_result['correct_rate'])
        pstr+= '\n'+ ''
    return pstr
             
def main():
    pass
        
if __name__ == '__main__':    
    main()