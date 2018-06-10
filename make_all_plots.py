#!/home/msj/miniconda3/bin/python3



import matplotlib as mpl
mpl.use('AGG')


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from jinja2 import Environment, FileSystemLoader
import time
import datetime
import vanweather as vw
import mobi
import geomobi

#plt.style.use('ggplot')
import seaborn as sns

#Load mobi daily data

thdf = mobi.load_csv('/data/mobi/data/taken_hourly_df.csv')

thdf = thdf.loc['2017-07-01':]

tddf = thdf.groupby(pd.Grouper(freq='D')).sum()
#tddf = mobi.load_csv('/data/mobi/data/taken_daily_df.csv')

twdf = thdf.groupby(pd.Grouper(freq='w')).sum()
trdf = tddf.sum(1).rolling(7).mean()





def make_daily_plot(df,fname,kind='line',weather=False,rolling=None,highlight=False):


    colors = sns.color_palette()
        
    f,ax = plt.subplots()


    if rolling is not None:
        df = df.rolling(rolling).mean()

    if weather == True:
        f,(ax,wax) = plt.subplots(2,sharex=True,gridspec_kw={'height_ratios':[4.5,1]})
        wdf = vw.get_weather_range(df.index[0].strftime('%Y-%m'),(df.index[-1]-datetime.timedelta(1)).strftime('%Y-%m'))
        print('------')
        print(fname)
        print(wdf.index[-1])
        print(df.index[-1])
        wdf = wdf.loc[[x for x in wdf.index if x in df.index],:]
        
        wax.bar(wdf.index,wdf['Total Rainmm'],color=colors[0])
        wax2 = wax.twinx()
        wax2.plot(wdf.index,wdf['Max Temp'],color='yellow')
        wax2.set_ylabel('High ($^\circ$C)')
        wax.set_ylabel('Rain (mm)')
        wax.spines['top'].set_visible(False)
        wax2.spines['top'].set_visible(False)
        wax.tick_params(axis='x',labelrotation=45)
        wax2.tick_params(axis='x',labelrotation=45)
        
    if kind=='line':
        if highlight:
            ax.plot(df[:-23].index,df[:-23].values,color=colors[1])
            ax.plot(df[-24:].index,df[-24:].values,color=colors[2])
        else:
            ax.plot(df.index,df.values,color=colors[1])
            
    if kind=='bar':
        bars = ax.bar(df.index,df.values,color=colors[1])
        # set ticks every week
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        #set major ticks format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        if highlight:
            [x.set_alpha(0.6) for x in bars[:-1]]

    ax.set_ylabel("Trips")
    
    ax.set_xlabel("")
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x',labelrotation=45)

    
    f.savefig('/var/www/html/mobi/images/'+fname,bbox_inches='tight')


make_daily_plot(tddf.sum(1),'alltime.png')
make_daily_plot(tddf.sum(1).iloc[-30:],'lastmonth_daily.png',kind='bar',weather=True,highlight=True)
make_daily_plot(thdf.sum(1).iloc[-7*24:-1],'lastweek_hourly.png',weather=False,highlight=False)
make_daily_plot(tddf.sum(1),'alltime_rolling.png',weather=True,rolling=7)


yday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
yday_min7 = (datetime.datetime.now() - datetime.timedelta(8)).strftime('%Y-%m-%d')
yday_min31 = (datetime.datetime.now() - datetime.timedelta(31)).strftime('%Y-%m-%d')


make_daily_plot(thdf.sum(1).loc[yday_min7:yday],'lastweek_hourly_yesterday.png')
make_daily_plot(tddf.sum(1).loc[yday_min31:yday],'lastmonth_daily_yesterday.png',kind='bar',weather=True,highlight=True)

geomobi.make_station_map(yday,'/var/www/html/mobi/images/station_map_yesterday.png')


# Station activity
sddf = mobi.load_csv('/data/mobi/data/stations_daily_df.csv')
active_stations = (sddf.iloc[-1]>-1).index  # index of active stations 

tdf = thdf.loc[:,active_stations].sum()
t24df = thdf.ix[-25:-1,active_stations].sum()
station24h = t24df.idxmax()
stationalltime = tdf.idxmax()

station24hmin = t24df.idxmin()
stationalltimemin = tdf.idxmin()

status = mobi.get_status('/data/mobi/data/')



# Jinja context
context = {'lastupdated':time.strftime('%c'),
           'station24h': station24h,
           'stationalltime': stationalltime,
           'station24hmin': station24hmin,
           'stationalltimemin': stationalltimemin,
           'bikes' : status['bikes'],
           'stations' : status['stations']
}


j2_env = Environment(loader=FileSystemLoader('/home/msj/mobi/'),trim_blocks=True)
html = j2_env.get_template('index.html').render(context)

with open('/var/www/html/mobi/index.html','w') as outfile:
#with open('/home/msj/mobi/test.html','w') as outfile:

    try:
        outfile.write(html)
    except:
        print("hmmmm...")
