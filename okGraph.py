#finalgraph.py
import urllib2
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick #candlestick
import matplotlib.animation as animation
import matplotlib
import pylab

matplotlib.rcParams.update({'font.size':9})



def rsiFunc(prices, n=14): #n= time period
    #it tells you a stock is either overbought or over sold i.e. over 70-over bought,
    #and vice versa #relative strength = (average gain -average lost)/n
    deltas = np.diff(prices) #different in prices
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs =up/down
    rsi=np.zeros_like(prices)
    rsi[:n]=100 - 100/(1+rs)
    #rsi up to that time period
    for i in range(n, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0
        else:
            upval=0
            downval = -delta
        up=(up*(n-1)+upval)/n
        down =(down*(n-1)+downval)/n
        rs=up/down
        rsi[i]=100-100/(1+rs)
        
    return rsi
    
def movingAverage(values, window): #values-data, window-timeframe
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values, weights, 'valid') #smooths the line
    return smas #list of stuff in numpy array

def expMovingAverage(values, window):
    #weight more closer data to recent data
    weights = np.exp(np.linspace(-1.0,0.0, window))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a

def computeMACD(x, slow=26, fast = 12):# 12 period and 26 periods
    '''
    macd line = 12EMA -26 EMA(expotentail moving average)
    signal line = 9EMA of the Macdline
    histogram = macd line - signal line
    '''
    emaslow = expMovingAverage(x, slow)
    emafast = expMovingAverage(x, fast)
    return emaslow, emafast, emafast-emaslow


def graphData(stock, MA1, MA2):
    fig.clf()   #moving average 1, moving average 2
    try:
        try:
            print'pulling data on', stock, 'at', str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=3d/csv'
            stockFile=[]
            try:
                sourceCode=urllib2.urlopen(urlToVisit).read()
                splitSource= sourceCode.split('\n')
                for eachLine in splitSource:
                    splitLine = eachLine.split(',')
                    fixMe = splitLine[0]
                    
                    if len(splitLine)==6:
                        if 'values' not in eachLine:
                            fixed = eachLine.replace(fixMe, str(datetime.datetime.fromtimestamp(int(fixMe)).strftime('%Y-%m-%d %H:%M:%S')))
                            
                            stockFile.append(fixed)
                                              
            except Exception, e:
                print str(e), 'failed to organize pulled data'

        except Exception, e:
            print str(e), 'failed to pull price data'
 ##       stockFile = 'oneDayOHLC/'+stock+ '.txt'

        date, closep, highp, lowp, openp, volume = np.loadtxt(stockFile, delimiter=',', unpack=True,
                                                              converters={ 0:mdates.strpdate2num('%Y-%m-%d %H:%M:%S')}) 
####
        x = 0
        y = len(date)
        candleAr = []
        while x<y:
            appendLine = date[x],openp[x], closep[x], highp[x],lowp[x],volume[x]
            candleAr.append(appendLine)
            x+=1
            #build the array
            #(openp, closep, highp, lowp, volume)
            #only open p and close p candlestick

        Av1 = movingAverage(closep, MA1) #use the close value
        Av2 = movingAverage(closep, MA2)
        
        SP = len(date[MA2-1:])
        #starting point #can mess around with MA2 and the length
        label1=str(MA1)+' daysMovingAverage'
        label2=str(MA2)+' daysMA'
        
          #off black #background color

        
 
#ax1 is the stock price graph        
        ax1 = plt.subplot2grid((6,4),(1,0), rowspan=4, colspan=4,axisbg='#07000d')
        candlestick(ax1, candleAr[-SP:], width=.00001,colorup='#54C156',colordown='#ff1717') #-SP to have average value on all candlesticks
        ax1.plot(date[-SP:],Av1[-SP:],color='#e1edf9',label=label1, linewidth=1.0) #color white blue ish
        ax1.plot(date[-SP:],Av2[-SP:],color='#4ee6fd',label=label2, linewidth=1.0) #off white#e1edf9
  ####       
        ax1.grid(True, color='w')
        #when it goes up-green(g). when it goes down it is red(r)
        #DATA=the format is important
        #already did that with the while loop

           
        ax1.grid(True) #we want that grid
        ax1.xaxis.set_major_locator(mticker.MaxNLocator(31)) # number here is the interval
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%y%m%d %H:%M'))
        plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        ax1.yaxis.label.set_color('w')
        ax1.spines['bottom'].set_color('#5998ff')
        ax1.spines['top'].set_color('#5998ff')
        ax1.spines['left'].set_color('#5998ff')
        ax1.spines['right'].set_color('#5998ff')#ligt blue
        ax1.tick_params(axis='y', colors='w')
        ax1.tick_params(axis='x', colors='w')
        

        plt.ylabel(stock+"'s Stock Price and Volume")
        maLeg = plt.legend(loc=9, ncol=2, prop={'size':7}, fancybox=True)
        maLeg.get_frame().set_alpha(0.4)
        textEd = pylab.gca().get_legend().get_texts()
        pylab.setp(textEd[0:5], color ='w') #can have more than 5 moving average
#ax0 is the RSI graph

        ax0 = plt.subplot2grid((6,4),(0,0),sharex=ax1, rowspan=1, colspan=4,axisbg='#07000d')
        rsiCol = '#c1f9f7'
        posCol= '#386d13'
        negCol='#8f2020'
        rsi = rsiFunc(closep) #close price #can change the closep #can have more than 14 days(defaulted)
        #can try average
        #can try average average(more complicated than just average)
        #can try open p and openp-closep
        ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
        ax0.axhline(70,color = negCol)
        ax0.axhline(30, color = posCol)
        ax0.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=negCol, edgecolor= negCol)
        ax0.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=posCol, edgecolor= posCol)
        
        ax0.set_ylim(0,100) #range for rsi is 100
        
        ax0.spines['bottom'].set_color('#5998ff')
        ax0.spines['top'].set_color('#5998ff')
        ax0.spines['left'].set_color('#5998ff')
        ax0.spines['right'].set_color('#5998ff')
        ax0.text(0.00000001, 0.99995, 'RSI(14)', va='center', color='w', transform=ax0.transAxes)
        #14 is hardcoded. it can be put in other variables
        ax0.tick_params(axis='x', colors='w')
        ax0.tick_params(axis='y', colors='w')
        ax0.set_yticks([30,70])
        ax0.yaxis.label.set_color('w')
 #       plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
        plt.ylabel('RSI')

        volumeMin = 0 #volume.min()    #how low to filler



####
#ax1v(olume) is the stock's volume graph
        ax1v = ax1.twinx() #volume axis share the xaxis #the volume axis #overlay
        #usually ppl just look at the amplitude
        ax1v.fill_between(date[-SP:],volumeMin,volume[-SP:], facecolor='#00ffe8', alpha=.5) #fill
        ax1v.axes.yaxis.set_ticklabels([])
        ax1v.grid(False)
        ax1v.spines['bottom'].set_color('#5998ff')
        ax1v.spines['top'].set_color('#5998ff')
        ax1v.spines['left'].set_color('#5998ff')
        ax1v.spines['right'].set_color('#5998ff')
        ax1v.set_ylim(0,3.5*volume.max()) #how the volume axis dominates the graph
        ax1v.tick_params(axis='x', colors='w')
        ax1v.tick_params(axis='y', colors='w')
              
        plt.subplots_adjust(left=0.09, bottom=.18, right=.95, top=.94, wspace=.20,hspace=0)

        plt.xlabel('Date', color='w')

        
#ax2 is for the MACD graph
        ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4,axisbg='#07000d')
        fillcolor='#00ffe8'
        nslow = 26
        nfast = 12
        nema=9
        emaslow, emafast, macd = computeMACD(closep) #usign closep
        ema9 = expMovingAverage(macd, nema) #macd?
        plt1 = ax2.plot(date[-SP:], macd[-SP:],color='#4eeffd', lw=2)
        plt2 = ax2.plot(date[-SP:], ema9[-SP:],color='#e1edf9', lw=1)
        ax2.fill_between(date[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.55, facecolor = fillcolor, edgecolor=fillcolor)               
##        ax2.text(0.5, 0.95, 'MACD 12, 26, 9', va= 'bottom', color='w', transform=ax2.transAxes)
        ax2.spines['bottom'].set_color('#5998ff')
        ax2.spines['top'].set_color('#5998ff')
        ax2.spines['left'].set_color('#5998ff')
        ax2.spines['right'].set_color('#5998ff')
        ax2.tick_params(axis='x', colors='w')
        ax2.tick_params(axis='y', colors='w')

        plt.ylabel('MACD', color='w')
        ##
        ax2.legend(('MACD', 'EMA9'), loc='lower left',prop={'size':5.5}, fancybox = True, framealpha = 0.5)

        ax1.text(0.001, 0.05,str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')+' Current Price: '+str(round(closep[-1],3))), va='top', color='yellow', transform=ax1.transAxes)
        ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5,prune='upper'))
        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(45)

        for i in range(int(len(date))-int(SP), int(len(date))):
            #this can be imporved a lot; like where exactly interesection happens
            ##THIS JUST PROVED THE EXISTENCE OF THE INERSECTION
            if macd[i]>ema9[i] and macd[i-1]<ema9[i-1]:
                ax2.plot((date[i]+date[i-1])/2, (macd[i]+ema9[i])/2, 'ro')
                
                    
            if macd[i]<ema9[i] and macd[i-1]>ema9[i-1]:
                ax2.plot((date[i]+date[i-1])/2, (ema9[i]+macd[i])/2, 'go')
                
            else:
                
                continue
        if closep[-1]>closep[-2]:
            fig.patch.set_facecolor('#333300')
        elif closep[-1]< closep[-2]:
            fig.patch.set_facecolor('#600000')
        else:
            fig.patch.set_facecolor('w')
        ax0.text(0.001, 0.05, str(datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')+' Current RSI: '+str(round(rsi[-1],3))), va='center', color='yellow', transform=ax0.transAxes)
        ax2.text(0.01, 0.95,'MACD 12, 26, 9 -- '+str(datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')+' Current MACD: '+str(round(macd[-1],3))), va='center', color='yellow', transform=ax2.transAxes)
        plt.suptitle(stock, color='w')


        plt.setp(ax0.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=False)
        
##        plt.show()
##        fig.savefig('Example2WithNotCandlestick.png', facecolor=fig.get_facecolor()) #save the figure after you cross it
        

    except Exception, e:
        print 'Failed main loop--', str(e)
###
fig = plt.figure(facecolor='#07000d')
def animate(i):
    graphData(stockToUse,12,26) #12 periods and 26 periods

while True:
    stockToUse = raw_input('Stock to Chart: ')
    
    ani = animation.FuncAnimation(fig, animate, interval = 60000)
    
    plt.show()
     

##    time.sleep(3600)
