from pyhht.emd import EMD
from pyhht.visualization import plot_imfs
import tushare as ts
import matplotlib.pyplot as plt

def emd_plot(tick):
    df = ts.get_hist_data(tick)    
    df = df.sort_index()
    emd = EMD(df['close'])
    imfs = emd.decompose()    
    plot_imfs(df['close'],imfs)


if __name__=='__main__':
    emd_plot('600438')
    # emd_plot('600004')
    # emd_plot('601138')
    # emd_plot('518800')
    # emd_plot('515580')