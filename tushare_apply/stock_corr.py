import pdb
import glob
import pandas as pd
from matplotlib import pyplot as plt
pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',None)
pd.options.display.float_format = '{:.2f}'.format


adf = pd.DataFrame()
for fname in glob.glob('data/[0-9]*.csv'):
    df=pd.read_csv(fname,index_col='date')
    code = 's%06d'%df['code'][0]
    close = df['close']
    if close.size<200:
        continue
    adf[code]=close[-100:]
    print 'load',code,''


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