import json
import os
from pandas_datareader import data, wb
from pandas import DataFrame,read_csv

def load_ticker(ticker):
    fname='data_yahoo/'+ticker+'.csv'
    if os.path.exists(fname):
        df = read_csv(fname)
    else:
        df= data.get_data_yahoo(ticker,'1/1/2015','12/1/2017')    
        df.to_csv(fname)
    return df
    
def main():
    for l in open('idx/SHSEC.csv'):
        print l
        row=l.strip().split(',')
        ticker=row[0]+'.ss'
        try:load_ticker(ticker)
        except:
            print 'Fail:',ticker
            pass
    
def test():
    load_ticker('000043.sz')
    
if __name__=='__main__':
    # test()
    main()
