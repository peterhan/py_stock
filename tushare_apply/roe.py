import tushare as ts
import pandas as pd

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
            rdf = get_p_df(y,q)
            if df is None:
                df = rdf
            else:
                df = df.append(rdf)
                
    df.to_csv('roe_5y.csv',encoding='utf8')

def analyze():
    df = pd.read_csv('roe_5y.csv',encoding='utf8')
    
if __name__ == '__main__':
    fetch_to_csv(2015,2020,2)