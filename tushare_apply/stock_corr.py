import pdb
import glob
import pandas as pd
from gevent.pool import Pool
from matplotlib import pyplot as plt
pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format

pool=Pool(16)

def load_data(fname):
    return pd.read_csv(fname,index_col='date')
    
def iter_files():
    res=[]
    for fname in glob.glob('data/[0-9]*.csv'):
        df = pool.spawn(load_data,fname)
        res.append(df)
    pool.join()


    adf = pd.DataFrame()
    for jres in res:
        df = jres.value
        code = '%06d'%df['code'][0]
        close = df['close']
        if close.size<200:
            continue
        adf[code] = close[:]
        print 'load',code
    return adf


def main():
    adf = iter_files()
    cdf= adf.corr()
    # pdb.set_trace()
    ddf =cdf.describe()
    print ddf.ix['min'].min()
    code2 = ddf.ix['min'].idxmin()
    code1 = cdf[code2].idxmin()
    print code1,code2

    plt.plot(adf[code1].values)
    plt.plot(adf[code2].values)
    plt.show()
    
if __name__ =='__main__':
    main()