from pyhht.emd import EMD
from pyhht.visualization import plot_imfs
import tushare as ts
import matplotlib.pyplot as plt


def emd_plot(data):
    emd = EMD(data)
    imfs = emd.decompose()    
    plot_imfs(data,imfs)


if __name__=='__main__':
    df = ts.get_hist_data('600438')    
    df = df.sort_index()
    emd_plot(df['close'])
    emd_plot(df['close'][:-50])
    # emd_plot('600004')
    # emd_plot('601138')
    # emd_plot('518800')
    # emd_plot('515580')