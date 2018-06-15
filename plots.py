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





class Plot():
    def __init__(self,df,imdir='./'):
        
        self.df = df               
        #self.imdir = '/var/www/html/mobi/images/'
        self.imdir = imdir
        
        
        colors = sns.color_palette()
        self.bg_color = '#000000'
        self.fg_color = colors[1]
        self.fg_color2 = colors[0]
        self.ax_color = '#ffffff'
        
        
    
    def __set_ax_props__(self,ax):
        
        
        ax.set_ylabel("Trips",color=self.ax_color)    
        ax.set_xlabel("",color=self.fg_color)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.tick_params(axis='x',labelrotation=45)
        
        #self.f.facecolor=self.bg_color
        #self.f.edgecolor=self.ax_color
        ax.patch.set_facecolor(self.bg_color)
        ax.xaxis.set_tick_params(color=self.ax_color, labelcolor=self.ax_color)
        ax.yaxis.set_tick_params(color=self.ax_color, labelcolor=self.ax_color)
        for spine in ax.spines.values():
            spine.set_color(self.ax_color)

        return ax

        
    def draw(self,fname,kind='line',weather=False,rolling=None,highlight=False):
        
        
        self.fname = fname
        self.kind = kind
        self.weather = weather
        self.rolling = rolling
        self.highlight = highlight
        
        
        self.f, self.ax = plt.subplots()
        self.ax = self.__set_ax_props__(self.ax)
        
        if self.rolling is not None:
            self.df = self.df.rolling(self.rolling).mean()

        if self.weather == True:
            self.f,(self.ax,self.wax) = plt.subplots(2,sharex=True,gridspec_kw={'height_ratios':[4.5,1]})
            self.ax = self.__set_ax_props__(self.ax)
            self.wax = self.__set_ax_props__(self.wax)
            self.wdf = vw.get_weather_range(self.df.index[0].strftime('%Y-%m'),(self.df.index[-1]-datetime.timedelta(1)).strftime('%Y-%m'))
            self.wdf = self.wdf.loc[[x for x in self.wdf.index if x in self.df.index],:]

            self.wax.bar(self.wdf.index,self.wdf['Total Rainmm'],color=self.fg_color2)
            self.wax2 = self.wax.twinx()
            self.wax2 = self.__set_ax_props__(self.wax2)
            self.wax2.plot(self.wdf.index,self.wdf['Max Temp'],color='yellow')
            self.wax2.set_ylabel('High ($^\circ$C)')
            self.wax.set_ylabel('Rain (mm)')
            self.wax.spines['right'].set_visible(True)
            self.wax2.spines['right'].set_visible(True)
            self.wax.tick_params(axis='x',labelrotation=45)
            self.wax2.tick_params(axis='x',labelrotation=45)

        if self.kind=='line':
            if self.highlight:
                self.ax.plot(self.df[:-23].index,self.df[:-23].values,color=self.fg_color,alpha=0.6)
                self.ax.plot(self.df[-24:].index,self.df[-24:].values,color=self.fg_color)
            else:
                self.ax.plot(self.df.index,self.df.values,color=self.fg_color)

        if self.kind=='bar':
            bars = self.ax.bar(self.df.index,self.df.values,color=self.fg_color)
            # set ticks every week
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            #set major ticks format
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            if self.highlight:
                [x.set_alpha(0.6) for x in bars[:-1]]    

        self.f.savefig(self.imdir+self.fname,bbox_inches='tight', facecolor=self.bg_color)

if __name__ == '__main__':
    
    tddf = mobi.load_csv('/data/mobi/data/taken_daily_df.csv')
    thdf = mobi.load_csv('/data/mobi/data/taken_hourly_df.csv')

    tddf = tddf['2017-07':]
    thdf = thdf['2017-07':]
    
    Plot(tddf.sum(1)).draw('alltime.png')
    Plot(tddf.sum(1).iloc[-30:]).draw('lastmonth_daily.png',kind='bar',weather=True,highlight=True)
    Plot(thdf.sum(1).iloc[-7*24:-1]).draw('lastweek_hourly.png',kind='line')
    Plot(tddf.sum(1)).draw('alltime_rolling.png',weather=True,rolling=7)
# make_daily_plot(tddf.sum(1),'alltime.png')
# make_daily_plot(tddf.sum(1).iloc[-30:],'lastmonth_daily.png',kind='bar',weather=True,highlight=True)
# make_daily_plot(thdf.sum(1).iloc[-7*24:-1],'lastweek_hourly.png',weather=False,highlight=False)
# make_daily_plot(tddf.sum(1),'alltime_rolling.png',weather=True,rolling=7)


# yday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
# yday_min7 = (datetime.datetime.now() - datetime.timedelta(8)).strftime('%Y-%m-%d')
# yday_min31 = (datetime.datetime.now() - datetime.timedelta(31)).strftime('%Y-%m-%d')


# make_daily_plot(thdf.sum(1).loc[yday_min7:yday],'lastweek_hourly_yesterday.png')
# make_daily_plot(tddf.sum(1).loc[yday_min31:yday],'lastmonth_daily_yesterday.png',kind='bar',weather=True,highlight=True)

# geomobi.make_station_map(yday,'/var/www/html/mobi/images/station_map_yesterday.png')


# # Station activity
# sddf = mobi.load_csv('/data/mobi/data/stations_daily_df.csv')
# active_stations = (sddf.iloc[-1]>-1).index  # index of active stations 

# tdf = thdf.loc[:,active_stations].sum()
# t24df = thdf.ix[-25:-1,active_stations].sum()
# station24h = t24df.idxmax()
# stationalltime = tdf.idxmax()

# station24hmin = t24df.idxmin()
# stationalltimemin = tdf.idxmin()

# status = mobi.get_status('/data/mobi/data/')


