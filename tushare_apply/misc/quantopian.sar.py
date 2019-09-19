"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""
from __future__ import division   
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume,CustomFactor,SimpleMovingAverage,RollingPearsonOfReturns,Returns
from quantopian.pipeline.filters import Q500US
from quantopian.pipeline.data import morningstar
from quantopian.pipeline.filters.morningstar import IsPrimaryShare   
from quantopian.pipeline.classifiers.morningstar import (Sector,SuperSector) 
import talib 
import pandas as pd 
import numpy as np
import statsmodels.api as sm
from scipy import stats
 
def initialize(context):
    """
    Called once at the start of the algorithm.
    """   
    context.close_positions= zip( pd.Series() )
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours =1))
     
    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())
    # schedule_function(check_trades,date_rules.every_day(),time_rules.market_close(minutes=5))
    
         
        # Create our dynamic stock selector.
    attach_pipeline(make_pipeline(context), 'my_pipeline')
         
def make_pipeline(context):
    """
    A function to create our dynamic stock selector (pipeline). Documentation on
    pipeline can be found here: https://www.quantopian.com/help#pipeline-title
    """
    primary = Q500US() # IsPrimaryShare()
    sma7 = SimpleMovingAverage(inputs=[USEquityPricing.close],window_length =7)
    sma3 = SimpleMovingAverage(inputs=[USEquityPricing.close],window_length =3)
    sma21 = SimpleMovingAverage(inputs=[USEquityPricing.close],window_length =21)
    
    above_10= sma3>10
    
    #dollar_volume = AverageDollarVolume(window_length=60)
    #high_dollar_volume = dollar_volume.percentile_between(85, 100,mask = above_10 & primary)
    
    smaRatio = sma7/sma21
    
    sma_rank = smaRatio.rank()
    
    shorts = sma_rank.percentile_between(90,100 )
   
    
    longs = sma_rank.percentile_between(0,10)
    
    # Create a dollar volume factor.
    
    
 
    # Pick the top 1% of stocks ranked by dollar volume.
   
    #high_dollar_volume = high_dollar_volume & primary 
    morn_cyc  =   SuperSector()
    Close = USEquityPricing.close.latest
        
    returns = Returns(window_length=10)
    returns_slice = returns[sid(8554)]
    spy_correlations = returns.pearsonr(
    target=returns_slice, correlation_length=30)
    LowBeta = (spy_correlations >= - 0.39) &( spy_correlations  <= 0.39)
    #LowBeta1 = spy_correla
     
    pipe = Pipeline(
        screen = primary & above_10,
        columns = {
            #'dollar_volume': dollar_volume,
            'longs': longs,
            'shorts': shorts,
            'sma_rank':sma_rank,
            'ratioCy':smaRatio,
            'SpyCor': LowBeta,
            'Q500':Q500US(),
            'Close': Close
            
        }
        
    )
    return pipe
 
def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    #pass
    
    context.output = pipeline_output('my_pipeline') ### 1)
    
    
    ##context.output = context.output[context.output.cycles ==3]
    '''print ('NUMBER OF SEC L AND S and all')
    log.info("\n" + str(len(context.output)))
    print (context.output).head(len(context.output)-1)'''    
    #context.shorts = context.output[context.output.shorts]
    
    #print "SHORT LIST"    
    #log.info("\n" + str(context.shorts.sort(['sma_rank'], ascending=True).head(10)))
    
    #if(context.output.longs > context.sar):    
    
    print(context.output).head() 
    
    context.longs=longs = context.output[context.output.longs].index   # 2)
    #if(context.output.shorts < context.sar):      
    context.shorts = shorts = context.output[context.output.shorts].index  #3)
    print('longs shorts first draft')    
    log.info('\n' + str( len(longs)))
    print('LONGS')
    #log.info('\n' + str( longs))
    print('SHORTS SHORT COUNT')
    log.info('\n' + str(len(shorts)))
    print('SHORTS')
    #log.info('\n' + str(shorts))'''      
                      
 
    
    
    longs = shorts = check_trades(context,data) 
    
    print('longs shorts SECOND draft')
    
    log.info('\n' + str(len(longs)))
    
    log.info('\n' + str(len(shorts)))
    
    '''for sec in context.portfolio.positions:
        if context.portfolio.positions[sec].amount > 0:
            if sec not in longs:
                context.close_positions.append(sec) 
        if context.portfolio.positions[sec].amount < 0:
            if sec not in shorts:
                context.close_positions.append(sec)'''
                
    
    
    #print(' This is Logs type', type(context.output.longs))  
    
    '''print('THIS IS # CONTEXT.OUTPT.LONGS')
    log.info("\n" + str(len(context.longs)))     
    print('THIS IS CONTEXT OUTPUT SHORTS')
    log.info("\n"+ str(len(context.shorts)))'''
    
  
    # These are the securities that we are interested in trading each day.
    context.security_list = context.output.index #4)
    '''print( 'MY_SEC in 1500')
    log.info(context.security_list == context.output.Q1500)'''
    
    '''print "SHORT LIST"    
    log.info("\n" + str(context.longs.sort(['sma_rank'], ascending=True).head(10)))'''
    #log.info("\n" + str(shortlist[shortlist.cycles >0]))
    
    
    '''print "LONG LIST"
    log.info("\n" + str(context.longs.sort(['sma_rank'], ascending=False).head(10)))'''
    print( context.output.SpyCor[True])
    #print(shorts[context.output.SpyCor])
    
    context.long_weights, context.short_weights = my_assign_weights(longs, shorts)  #5)
    ''' print 'long weights'
    log.info("\n" +str( context.long_weights))
    print 'short weights'
    log.info("\n" + str(context.short_weights))'''
    
def my_assign_weights(longs, shorts):
    """
    Assign weights to securities that we want to order.    
    """
    '''num_longs =num_shorts =0
    long_weights = short_weights =0'''
    
     
    
    
    num_longs =  len(longs) 
    num_shorts = len(shorts) 
     
   
    equal_weights = .5/(num_longs + num_shorts)
    long_weights = [equal_weights] * num_longs
    short_weights = [-equal_weights] * num_shorts
    #print( 'BOTH LONGS AND SHORTS') 
    #log.info("\n"+ str(long_weights,short_weights))
    return long_weights,short_weights                                                       
                             
def my_rebalance(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    
    """
    
    '''context.output = pipeline_output('my_pipeline') 
    context.longs=longs = context.output[context.output.longs].index
    context.shorts = shorts = context.output[context.output.shorts].index
    context.security_list = context.output.index 
    context.long_weights, context.short_weights = my_assign_weights(longs, shorts)'''
    
    
    '''for asset in context.portfolio.positions:
        #if(asset==context.output:
        print(asset)
        print(context.output.index)'''
    #print(context.longs)
    closed=0
    for asset in context.close_positions:   
                  if data.can_trade(asset):
                         order_target_value(asset,0)
                         closed += 1
    print( 'attempted closed positions')
    log.info('\n' + str(closed))
            
                
    for asset, weight in zip(context.longs, context.long_weights):
        #print(type(context.longs))
             
        if data.can_trade(asset):
            order_target_percent(asset, weight)
            
    for asset, weight in zip(context.shorts, context.short_weights):
        if data.can_trade(asset):
            order_target_percent(asset, weight)
 
 
 
def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    
    """
        
    x = context.account.leverage        
    y =  context.account.net_leverage   
    #record(cash_avail = x)   
    record(leverage = x,net_leverage = y)
    #Y=sar
    #ecord(X)
    #record
 
def check_trades(context,data):
    """
    Called every minute.
    """
      
    
    longs = context.longs
    #print('NUMBER OF LONGS',len(longs))
    shorts = context.shorts
    longs.temp= zip(pd.Series()) 
    shorts.temp =zip(pd.Series())
    highs = lows = 0
    highs  = data.history(longs,'high',20,'1d')
    lows =   data.history(longs,'low',20,'1d')
    #Shighs , Llows = data.history(context.shorts,('high','low'),20,'1d')
    #print ('longs',len(longs))
    for sec in longs:
        high=highs[sec]
        low=lows[sec]        
        sar = talib.SAR(high,low)[-1] 
        if( context.output.Close[sec] > sar):
                    #new_longs += 1
                    longs.temp.append(sec) 
                    
           
               
    highs  = data.history(shorts,'high',20,'1d')
    lows = data.history(shorts,'low',20,'1d') 
           
    for sec in shorts:
        high=highs[sec]
        low=lows[sec]        
        sar = talib.SAR(high,low)[-1] 
        if(context.output.Close[sec] < sar):
                    shorts.temp.append(sec)   
                
    return longs.temp, shorts.temp       
           #if data.can_trade(sec):
            # order_target(sec,0)     
           
            