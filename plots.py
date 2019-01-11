#!/home/msj/miniconda3/bin/python3



import matplotlib as mpl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from jinja2 import Environment, FileSystemLoader
import time
import datetime
import vanweather as vw
import mobi
import matplotlib.lines as mlines
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader






class BasePlot():
    def __init__(self,n=1,m=1):
        #https://xkcd.com/color/rgb/
        self.colors = ['#3778bf','#7bb274','#825f87','#feb308','#59656d']
        mpl.rcParams['axes.prop_cycle'] = mpl.cycler('color',self.colors)
        self.bg_color = '#ffffff'
        self.fg_color = self.colors[1]
        self.fg_color2 = self.colors[0]
        self.fg_color3 = self.colors[3]
        self.ax_color = self.colors[4]
        
        
        
        
class Plot(BasePlot):
    def __init__(self,n=1,m=1):
        super().__init__(n,m)
        
        self.f, self.ax = plt.subplots(n,m,figsize=(7,5))
        if type(self.ax) == np.ndarray:
            self.ax = [self.set_ax_props(x) for x in self.ax]
        else:
            self.ax = self.set_ax_props()
        
    
    
    def set_ax_props(self,ax=None):
        if ax == None:
            ax = self.ax
        
        
        ax.set_ylabel("Trips",color=self.ax_color)    
        ax.set_xlabel("",color=self.ax_color)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.tick_params(axis='x',labelrotation=45)

        ax.patch.set_facecolor(self.bg_color)
        ax.xaxis.set_tick_params(color=self.ax_color, labelcolor=self.ax_color)
        ax.yaxis.set_tick_params(color=self.ax_color, labelcolor=self.ax_color)
        for spine in ax.spines.values():
            spine.set_color(self.ax_color)

        return ax

    def title(self,titletext,x=0.02,y=0.98,horizontalalignment='left',**kwargs):
        self.f.suptitle(titletext,x=x,y=y,color=self.ax_color,horizontalalignment=horizontalalignment,**kwargs)

    def tight_layout(self,*args,**kwargs): 
        self.f.tight_layout(rect=[0, 0.03, 1, 0.95],*args,**kwargs)


    def draw(self,df,fname,kind='line',weather=False,rolling=None,highlight=False):
        self.df = df               
        self.fname = fname
        self.kind = kind
        self.weather = weather
        self.rolling = rolling
        self.highlight = highlight
        
        
    
        
        if self.rolling is not None:
            self.df = self.df.rolling(self.rolling).mean()

        if self.weather == True:
            self.f,(self.ax,self.wax) = plt.subplots(2,sharex=True,gridspec_kw={'height_ratios':[4.5,1]},figsize=(7,5))
            self.ax = self.set_ax_props()
            self.wax = self.set_ax_props(self.wax)
            self.wdf = vw.get_weather_range(self.df.index[0].strftime('%Y-%m'),(self.df.index[-1]-datetime.timedelta(1)).strftime('%Y-%m'))
            self.wdf = self.wdf.loc[[x for x in self.wdf.index if x in self.df.index],:]

            self.wax.bar(self.wdf.index,self.wdf['Total Precipmm'],color=self.fg_color2)
            self.wax2 = self.wax.twinx()
            self.wax2 = self.set_ax_props(self.wax2)
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
                
        if self.kind == 'cumsum':
            def cumsum(df):
                df = df.sum(1).cumsum()
                df.index = df.index.map(lambda x: x.strftime('%H:%M'))
                df = df.shift()
                df.iloc[0] = 0
                return df
        
            for i,df in self.df.groupby(pd.Grouper(freq='d')):
                df = cumsum(df)
                self.ax.plot(df.index,df,color='gray',alpha=0.1)
    
            self.ax.plot(df.index,df,alpha=1,color=self.fg_color)
            self.ax.scatter(df.index,df,alpha=1,color=self.fg_color)
            self.ax.set_ylabel("Daily Cumulative Trips",color=self.ax_color)
            self.ax.set_xlabel("Hour",color=self.ax_color)
    
            year = self.df.index[-1].year
            date = self.df.index[-1].date().strftime('%Y-%m-%d')
            gray_line = mlines.Line2D([], [], color=self.ax_color,  label="{} so far".format(year))
            green_line= mlines.Line2D([], [], color=self.fg_color, marker='.',label="{}".format(date))
            self.ax.legend(handles=[green_line,gray_line])

        self.f.savefig(self.fname,bbox_inches='tight', facecolor=self.bg_color)


# def cumsum(thdf,date,fname):

#     plot = Plot()
#     ax = plot.set_ax_props(plot.ax)

    
#     def cumsum_fix(df):
#         df = df.sum(1).cumsum()
#         df.index = df.index.map(lambda x: x.strftime('%H:%M'))
#         df = df.shift()
#         df.iloc[0] = 0
#         return df
        
#     for i,df in thdf.groupby(pd.Grouper(freq='d')):
#         df = cumsum_fix(df)
#         ax.plot(df.index,df,color='gray',alpha=0.1)
    
#     ax.plot(df.index,df,alpha=1,color=plot.fg_color)
#     ax.scatter(df.index,df,alpha=1,color=plot.fg_color)
#     ax.set_ylabel("Daily Cumulative Trips",color=plot.ax_color)
#     ax.set_xlabel("Hour",color=plot.ax_color)
    
#     gray_line = mlines.Line2D([], [], color=plot.ax_color,  label="{} so far".format(date[:4]))
#     green_line= mlines.Line2D([], [], color=plot.fg_color, marker='.',label="{}".format(date))
    
#     ax.legend(handles=[green_line,gray_line])
#     plot.f.savefig(fname)
        

class GeoPlot(Plot):
    def __init__(self):

        super().__init__(n=1,m=0)

        self.f, self.ax = plt.subplots()
        self.f.subplots_adjust(left=0, bottom=0.05, right=1, top=1, wspace=None, hspace=None)
        self.ax = plt.axes(projection=ccrs.epsg(26910),frameon=False)

        # This is a workaround... frameon=False should work in future versions of cartopy
        self.ax.outline_patch.set_visible(False)

        self.left = 485844
        self.right = 495513
        self.bottom = 5453579
        self.top = 5462500

        self.ax.set_extent([self.left,self.right,self.bottom,self.top ], ccrs.epsg(26910))
        
        self.ax.text(self.right,self.bottom-400,'@VanBikeShareBot',color=self.colors[1],size=18,alpha=0.6,horizontalalignment='right')
             
        
    def addgeo(self,shapef,edgecolor='black',facecolor='white',alpha=1,zorder=1):
        shape = list(shpreader.Reader(shapef).geometries())
        record = list(shpreader.Reader(shapef).records())
        self.ax.add_geometries(shape, ccrs.epsg(26910),
                      edgecolor=edgecolor, facecolor=facecolor, alpha=alpha,zorder=zorder)
        return shape, record    
        
    
    def draw(self,sdf,date):
        lats = sdf['coordinates'].map(lambda x: x[0])
        longs = sdf['coordinates'].map(lambda x: x[1])

        self.ax.scatter(longs,lats,transform=ccrs.PlateCarree(),alpha=0.7,
                        s=sdf['trips'],color=self.colors[0],zorder=100)
        
        
       
        # Dummy scatters for the legend
        l1 = self.ax.scatter([0],[0], s=10, edgecolors='none',color=self.colors[0],alpha=0.7)
        l2 = self.ax.scatter([0],[0], s=100, edgecolors='none',color=self.colors[0],alpha=0.7)
        labels=['10','100']
        self.ax.legend([l1,l2],labels,title='Station Activity\n{}'.format(date))

        return self.f
        
        f.savefig(fname,bbox_inches='tight',pad_inches=0.0,transparent = True)

    
        
if __name__ == '__main__':
    
    tddf = mobi.load_csv('/data/mobi/data/taken_daily_df.csv')
    thdf = mobi.load_csv('/data/mobi/data/taken_hourly_df.csv')

    tddf = tddf['2017-07':]
    thdf = thdf['2017-07':]
    
    #Plot().draw(tddf['2018-01':].sum(1),'alltime.png',weather=True)
    #Plot(tddf.sum(1).iloc[-30:]).draw('lastmonth_daily.png',kind='bar',weather=True,highlight=True)
    #Plot(thdf.sum(1).iloc[-7*24:-1]).draw('lastweek_hourly.png',kind='line')
    #Plot(tddf.sum(1)).draw('alltime_rolling.png',weather=True,rolling=7)
    
    #plot = Plot(thdf.sum(1).loc['2018-07-17'].cumsum())

    
    #cumsum(thdf['2018-01':],'2018-08-05','cumsumtest.png')
    #print(thdf['2018-01':'2018-08-04'])
    Plot().draw(thdf['2018-01':'2018-09-25'],'cumsumtest.png',kind='cumsum')    
        


