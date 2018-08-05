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
        
        
#         colors = sns.color_palette()
#         self.bg_color = '#000000'
#         self.fg_color = colors[1]
#         self.fg_color2 = colors[0]
#         self.ax_color = '#ffffff'
        
        colors = [ "dusty purple","windows blue", "amber", "greyish", "faded green"]
        self.colors = sns.xkcd_palette(colors)
        self.bg_color = '#ffffff'
        self.fg_color = self.colors[4]
        self.fg_color2 = self.colors[1]
        self.fg_color3 = self.colors[2]
        self.ax_color = self.colors[3]
        
        
        self.f, self.ax = plt.subplots(figsize=(7,5))
        self.ax = self.__set_ax_props__(self.ax)
    
    
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
        
        

        
        if self.rolling is not None:
            self.df = self.df.rolling(self.rolling).mean()

        if self.weather == True:
            self.f,(self.ax,self.wax) = plt.subplots(2,sharex=True,gridspec_kw={'height_ratios':[4.5,1]},figsize=(7,5))
            self.ax = self.__set_ax_props__(self.ax)
            self.wax = self.__set_ax_props__(self.wax)
            self.wdf = vw.get_weather_range(self.df.index[0].strftime('%Y-%m'),(self.df.index[-1]-datetime.timedelta(1)).strftime('%Y-%m'))
            self.wdf = self.wdf.loc[[x for x in self.wdf.index if x in self.df.index],:]

            self.wax.bar(self.wdf.index,self.wdf['Total Rainmm'],color=self.fg_color2)
            self.wax2 = self.wax.twinx()
            self.wax2 = self.__set_ax_props__(self.wax2)
            self.wax2.plot(self.wdf.index,self.wdf['Max Temp'],color=self.fg_color3)
            self.wax2.set_ylabel('High ($^\circ$C)')
            self.wax2.yaxis.label.set_color(self.fg_color3)
            self.wax.set_ylabel('Rain (mm)')
            self.wax.yaxis.label.set_color(self.fg_color2)
            self.wax.spines['right'].set_visible(True)
            self.wax2.spines['right'].set_visible(True)
            self.wax.tick_params(axis='x',labelrotation=45)
            self.wax2.tick_params(axis='x',labelrotation=45)

        if self.kind=='line':

            line = self.ax.plot(self.df.index,self.df.values,color=self.fg_color)
            self.ax.fill_between(self.df.index,0,self.df.values,color=self.fg_color,alpha=0.8)

        if self.kind=='bar':
            bars = self.ax.bar(self.df.index,self.df.values,color=self.fg_color)
            # set ticks every week
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            #set major ticks format
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            if self.highlight:
                [x.set_alpha(0.6) for x in bars[:-1]]    

        self.f.savefig(self.imdir+self.fname,bbox_inches='tight', facecolor=self.bg_color)


def cumsum(thdf,date,fname):
    colors = [ "dusty purple","windows blue", "amber", "greyish", "faded green"]
    colors = sns.xkcd_palette(colors)
    bg_color = '#ffffff'
    fg_color = colors[4]
    fg_color2 = colors[1]
    fg_color3 = colors[2]
    ax_color = colors[3]
    f,ax = plt.subplots()  
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x',labelrotation=45)
    ax.patch.set_facecolor(bg_color)
    ax.xaxis.set_tick_params(color=ax_color, labelcolor=ax_color)
    ax.yaxis.set_tick_params(color=ax_color, labelcolor=ax_color)
    for spine in ax.spines.values():
        spine.set_color(ax_color)
    
    def cumsum_fix(df):
        df = df.sum(1).cumsum()
        df.index = df.index.map(lambda x: x.strftime('%H:%M'))
        df = df.shift()
        df.iloc[0] = 0
        return df
        
    for i,df in thdf.groupby(pd.Grouper(freq='d')):
        df = cumsum_fix(df)
        ax.plot(df.index,df,color='gray',alpha=0.1)
    
    ax.plot(df.index,df,alpha=1,color=colors[4])
    ax.scatter(df.index,df,alpha=1,color=colors[4])
    ax.set_ylabel("Daily Cumulative Trips",color=ax_color)
    ax.set_xlabel("Hour",color=ax_color)
    import matplotlib.lines as mlines
    gray_line = mlines.Line2D([], [], color='gray',  label="{} so far".format(date[:4]))
    green_line= mlines.Line2D([], [], color=colors[4], marker='.',label="{}".format(date))
    
    ax.legend(handles=[green_line,gray_line])
    f.savefig(fname)
        
        
def cumsum_monthly(thdf,fname):
    colors = [ "dusty purple","windows blue", "amber", "greyish", "faded green"]
    colors = sns.xkcd_palette(colors)
    bg_color = '#ffffff'
    fg_color = colors[4]
    fg_color2 = colors[1]
    fg_color3 = colors[2]
    ax_color = colors[3]
    f,ax = plt.subplots()  
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x',labelrotation=45)
    ax.patch.set_facecolor(bg_color)
    ax.xaxis.set_tick_params(color=ax_color, labelcolor=ax_color)
    ax.yaxis.set_tick_params(color=ax_color, labelcolor=ax_color)
    for spine in ax.spines.values():
        spine.set_color(ax_color)
        
    for i,df in thdf.groupby(pd.Grouper(freq='d')):
        df = df.sum(1).cumsum()
        df.index = df.index.map(lambda x: x.strftime('%B:%H'))
        ax.plot(df.index,df,alpha=0.1,color='gray')
        print(df.sum())
    
    ax.set_ylabel("Daily Cumulative Trips",color=ax_color)
    #ax.set_xlabel("Hour",color=ax_color)
    locs = ax.get_xticks()
    ax.set_xticks([x for x in locs if x%24==0])
    #print([x for x in ax.get_xticklabels()])
    #ax.set_xticklabels([x for x in ax.get_xticklabels()])
    #gray_line = mlines.Line2D([], [], color='gray',  label="{} so far".format(date[:4]))
    #green_line= mlines.Line2D([], [], color=colors[4], marker='.',label="{}".format(date))
    #ax.legend(handles=[green_line,gray_line])
    f.tight_layout()
    f.savefig(fname)
        
if __name__ == '__main__':
    
    tddf = mobi.load_csv('/data/mobi/data/taken_daily_df.csv')
    thdf = mobi.load_csv('/data/mobi/data/taken_hourly_df.csv')

    tddf = tddf['2017-07':]
    thdf = thdf['2017-07':]
    
    #Plot(tddf.sum(1)).draw('alltime.png')
    #Plot(tddf.sum(1).iloc[-30:]).draw('lastmonth_daily.png',kind='bar',weather=True,highlight=True)
    #Plot(thdf.sum(1).iloc[-7*24:-1]).draw('lastweek_hourly.png',kind='line')
    #Plot(tddf.sum(1)).draw('alltime_rolling.png',weather=True,rolling=7)
    
    #plot = Plot(thdf.sum(1).loc['2018-07-17'].cumsum())

    
    cumsum(thdf['2018-01':],'2018-08-05','cumsumtest.png')
        
        


