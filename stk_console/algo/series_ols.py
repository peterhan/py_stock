#coding:utf8

import numpy as np
import pandas as pd
import statsmodels.api as sm #方法一
import statsmodels.formula.api as smf #方法二
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
 
def practice():
    df = pd.read_csv('Advertising.csv', index_col=0)
    X = df[['TV', 'radio','newspaper']]
    y = df['sales']
     
    # est = sm.OLS(y, sm.add_constant(X)).fit() #方法一
    est = smf.ols(formula='sales ~ TV + radio + newspaper', data=df).fit() #方法二
    y_pred = est.predict(X)
     
    df['sales_pred'] = y_pred
    print est
    print(df)
    print(est.summary()) #回归结果
    print(est.params) #系数
     
    fig = plt.figure()
    ax = fig.add_subplot(211, projection='3d') #ax = Axes3D(fig)
    ax.scatter(X['TV'], X['radio'], y, c='b', marker='o')
    ax.scatter(X['TV'], X['radio'], y_pred, c='r', marker='+')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    ax = fig.add_subplot(212, projection='3d') #ax = Axes3D(fig)
    ax.scatter(X['TV'], X['newspaper'], y, c='b', marker='o')
    ax.scatter(X['TV'], X['newspaper'], y_pred, c='r', marker='+')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    # plt.show()
    #--------------------- 
    #作者：薛定谔的DBA 
    #来源：CSDN 
    #原文：https://blog.csdn.net/kk185800961/article/details/79220724 
    #版权声明：本文为博主原创文章，转载请附上博文链接！


    X = df[['TV']]
    y = df['sales']
     
    est = smf.ols(formula='sales ~ TV ', data=df).fit()
    y_pred = est.predict(X)
    print(est.summary())
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(X, y, c='b')
    ax.plot(X, y_pred, c='r')
    # plt.show()
    # --------------------- 
    # 作者：薛定谔的DBA 
    # 来源：CSDN 
    # 原文：https://blog.csdn.net/kk185800961/article/details/79220724 
    # 版权声明：本文为博主原创文章，转载请附上博文链接！
    
def stock_fit():
    df = pd.read_csv('600438.csv')
    y = df['change']
    X = df[['IND_SUM','volume']]
    est = smf.ols(formula='change ~ IND_SUM + volume', data=df).fit()
    est = smf.ols(formula='change ~ IND_SUM ', data=df).fit()
    y_pred = est.predict(X)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d') #ax = Axes3D(fig)
    ax.scatter(X['IND_SUM'], X['volume'], y, c='b', marker='o')
    ax.scatter(X['IND_SUM'], X['volume'], y_pred, c='r', marker='+')
    ax.set_xlabel('X IND_SUM')
    ax.set_ylabel('Y volume')
    ax.set_zlabel('Z Label')
    plt.show()
    
# practice()
stock_fit()