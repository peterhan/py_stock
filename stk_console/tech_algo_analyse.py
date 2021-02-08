#!coding:utf8
import pandas as pd
import numpy as np
import traceback
## algo_analyse
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
    
def predict_cat_boost(fit_model, adf,i_stages,target_col):
    from catboost import CatBoostRegressor
    factor_results = {}
    test_pool = adf[i_stages][-100:]
    test_labels = adf[target_col].fillna(0)[-100:]
    model = fit_model
    # model = CatBoostRegressor(learning_rate=1, depth=6, loss_function='RMSE',cat_features=i_stages)
    # model.load_model('first.model')
    # preds_class = model.predict(test_pool, prediction_type='Class')
    # preds_proba = model.predict(test_pool, prediction_type='Probability')
    preds_raw_vals = model.predict(test_pool, prediction_type='RawFormulaVal')
    # pdb.set_trace()
    
    feat = [] 
    for i in range(0,len(i_stages)):
        srs = test_pool[i_stages[i]].unique()
        # pdb.set_trace()
        edf = pd.DataFrame(srs)
        edf['key']=1
        feat.append(edf)
    if len(feat)==1:
        cfeat=feat[0]
    else:
        cfeat = reduce(lambda x1,x2:pd.merge(x1,x2,on='key') ,feat)
        # pdb.set_trace()
    cfeat.pop('key')
    cfeat = cfeat.to_records(index=False)
    cfeat = [list(row) for row in cfeat]
    
    ps = model.predict(cfeat)
    sts = [' & '.join(row) for row in cfeat]
    pdf  = pd.DataFrame({'feature':sts,'weight':ps}).sort_values('weight',ascending=False)
    
    key=':'.join (i_stages)+'=>'+target_col
    factor_results[key] = {}
    check_result=factor_results[key]
    check_result['factor_detail']=pdf
    
    # print preds_raw_vals,test_labels

    rmsev = rmse( np.sign(test_labels.values), np.sign(preds_raw_vals) )
    check_result['rmsev']=rmsev
    pos_neg = pd.Series(np.sign(test_labels*preds_raw_vals)*10,index=test_labels.index)
    pnvc = pos_neg.value_counts()    
    check_result['correct_rate']=pnvc[10.0]*1.0/sum(pnvc.values)*100    
    return factor_results


def train_cat_boost(adf,i_stages,target_col):
    from catboost import CatBoostRegressor
    dataset = adf[i_stages][:]
    train_labels = adf[target_col].fillna(0)[:]
    model = CatBoostRegressor(learning_rate=1, depth=6, loss_function='RMSE',cat_features=i_stages)
    try:
        fit_model = model.fit(dataset, train_labels, verbose=0)
    except:
        traceback.print_exc()

    # print(fit_model.get_params())
    # fit_model.save_model('first.model')
    return fit_model
    # pdb.set_trace()


def cat_boost_factor_check(df,target_days = ['5d'],print_res=True):
    i_stages = [['cci_stage','ema_stage','volume_ema_stage','volume_sma_stage','sma_stage','ma_es_dif_stage','macd_stage','boll_stage','rsi_stage','kdj_stage','mom_stage','aroon_stage','vswap_stage','vwap_stage','week_stage'] ]    
    i_stage_list = [  ['ema_stage']  ,['sma_stage'],['volume_ema_stage'] ,['volume_sma_stage']  ,['macd_stage'] ,['cci_stage'] ,['roc_stage'] 
        ,['rsi_stage'] ,['ma_es_dif_stage'],['boll_stage'] ,['kdj_stage'] ,['mom_stage'], ['aroon_stage'],['vswap_stage'],['vwap_stage']
        ,['vwap_stage','ema_stage'],['week_stage','ema_stage'],['macd_stage','rsi_stage']]
    factor_results = {}
    for target_col in ['p_change_%s'%target_day for target_day in target_days]:    
        for i_stages in i_stage_list:
            try:
                if len(target_days)>2:
                    print '[Training]:',i_stages,target_col
                adf = caculate_indicator(df, i_stages, target_col)
                fit_model = train_cat_boost(adf,i_stages,target_col)
                cres = predict_cat_boost(fit_model ,adf,i_stages,target_col)
                factor_results.update(cres)
            except:
                traceback.print_exc()
    if print_res:
        print ''
        for key,check_result in sorted(factor_results.items(),key=lambda v:v[1]['correct_rate'],reverse=False):
            print '[%s]'%(key)
            print check_result['factor_detail']
            print 'rmse: %0.2f'%check_result['rmsev']
            print 'correct_rate: %0.2f%%'%(check_result['correct_rate'])
            print ''
    # from matplotlib import pyplot as plt
    # plt.title('%s %s'%(i_stages,target_col))
    # plt.plot(preds_raw_vals[:],'--')
    # plt.plot(test_labels.values[:])
    # plt.plot(pos_neg.values[:],':')
    # plt.show()
    # return preds_class,preds_proba,preds_raw_vals
    return factor_results


def main():
    pass
        
if __name__ == '__main__':    
    main()