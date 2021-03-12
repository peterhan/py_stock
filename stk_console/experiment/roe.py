import tushare as ts
import pandas as pd
import ipdb

def get_p_df(y,q):
    df = ts.get_profit_data(y,q)
    df.insert(0,'date','%sq%s'%(y,q))
    return df
    
def fetch_to_csv(ystart,yend,qend):
    df = None
    for y in range(ystart,yend+1):
        if y==yend:
            qend=qend+1
        else:
            qend=5
        for q in range(1,qend):
            print '\n',y,q
            try:
                rdf = get_p_df(y,q)
            except:
                continue
            if df is None:
                df = rdf
            else:
                df = df.append(rdf)
                
    df.to_csv('roe_5y.csv',encoding='utf8')

def analyze_roe():
    pd.set_option('display.max_columns',80)
    from matplotlib import pyplot as plt
    df = pd.read_csv('roe_5y.csv',encoding='utf8')
    df.set_index(df['date'])
    print df.columns
    ipdb.set_trace()
    
if __name__ == '__main__':
    # fetch_to_csv(2015,2020,2)
    analyze_roe()