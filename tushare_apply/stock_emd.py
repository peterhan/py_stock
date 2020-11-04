from pyhht.emd import EMD
from pyhht.visualization import plot_imfs
import tushare as ts
import matplotlib.pyplot as plt
import pdb


def emd_plot(data):
    emd = EMD(data)
    imfs = emd.decompose()
    # pdb.set_trace()
    plot_imfs(data,imfs)
    return imfs


if __name__=='__main__':
    tick = '300015'
    tick = '600509'
    tick = '600048'
    tick = '600599'
    tick = '600438'
    tick = '002409'
    df = ts.get_hist_data(tick)
    df = df.sort_index()
    emd_plot(df['close'])
    emd_plot(df['close'][-50:])
    # emd_plot('600004')
    # emd_plot('601138')
    # emd_plot('518800')
    # emd_plot('515580')