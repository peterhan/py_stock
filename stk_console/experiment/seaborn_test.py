import tushare as ts
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
tk='600438'
# df = ts.get_today_ticks(tk)
df=pd.DataFrame(np.random.randn(10,3),columns=['x','y','z'])
print df
sns.violinplot(y='y',data=df)
plt.show()