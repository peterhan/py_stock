#-*-coding=utf-8-*-
__author__ = 'rocky'
#��ȡ��ָ�������ڵ��¸� ������60���¸�
import tushare as ts
import datetime

info=ts.get_stock_basics()

def loop_all_stocks():
    for EachStockID in info.index:
         if is_break_high(EachStockID,60):
             print "High price on",
             print EachStockID,
             print info.ix[EachStockID]['name'].decode('utf-8').encode('gbk')



def is_break_high(stockID,days):
    end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
    days=days*7/5
    #���ǵ������շǽ���
    start_day=end_day-datetime.timedelta(days)

    start_day=start_day.strftime("%Y-%m-%d")
    end_day=end_day.strftime("%Y-%m-%d")
    try:
        df=ts.get_h_data(stockID,start=start_day,end=end_day)
    except:
        print stockID,start_day,end_day,'error'
        return False
    period_high=df['high'].max()
    #print period_high
    today_high=df.iloc[0]['high']
    #���ﲻ��ֱ���� .values
    #����õ�df����1�� ����Ҫ��.values
    #print today_high
    if today_high>=period_high:
        return True
    else:
        return False

loop_all_stocks()