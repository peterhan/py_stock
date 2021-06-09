import pdb
import numpy as np
import pandas as pd
import talib
from matplotlib import pyplot as plt


def get_angle(ss,p=4):
    fss = np.nan_to_num(ss,0)
    scale = (max(fss)-min(fss))/2*1.1
    nfss = fss/scale    
    # pdb.set_trace()
    angle =  talib.LINEARREG_ANGLE(nfss, timeperiod=p)    
    return angle
    
def get_crossx_type(fast_line,slow_line):
    fast_ag = get_angle(fast_line, 2)
    slow_ag = get_angle(slow_line, 2)
    ag_diff = fast_ag - slow_ag
    df=pd.DataFrame({'fast_line':fast_line,'slow_line':slow_line,'fast_ag':fast_ag,'slow_ag':slow_ag,'ag_diff':ag_diff}
                    ,columns=['fast_line','slow_line','fast_ag','slow_ag','ag_diff'])
    df['value_diff'] = df['fast_line'] - df['slow_line']
    def cross_judge(row):    
        # pdb.set_trace()   
        ag_diff ,value_diff = row['ag_diff'],row['value_diff']
        fast_ag ,slow_ag = row['fast_ag'],row['slow_ag']
        if value_diff>=0 and ag_diff>=0:
            res = 'After-Gx'
        elif value_diff>=0 and fast_ag<0:
            res = 'TrnTo-Dx'
        elif value_diff>=0 and ag_diff<0:
            res = 'CnvTo-Dx'
        elif value_diff<0 and ag_diff<0:
            res = 'After-Dx'
        elif value_diff<0 and fast_ag>=0:
            res = 'TrnTo-Gx'
        elif value_diff<0 and ag_diff>=0:
            res = 'CnvTo-Gx'        
        else:
            res = 'NaN'
        return res
    df['cross_stage'] = df.apply(cross_judge,axis=1)#,result_type='expand'    
    # print edf
    return df
    
if __name__ == '__main__':
    fast_s=np.sin(np.arange(80)*0.1+0.5)*5
    slow_s=np.sin(np.arange(80)*0.1)*5
    res = get_crossx_type(fast_s,slow_s)
    print res.columns.to_list()
    for row in res.iterrows():
        print row[1].to_list()
    print res.groupby('cross_stage')['cross_stage'].count()
    ag = get_angle(fast_s)
    print 'angle:',ag
    # pdb.set_trace()
    plt.plot(fast_s)
    plt.plot(slow_s)
    plt.plot(ag)
    plt.show()