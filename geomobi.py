import matplotlib as mpl
mpl.use('AGG')

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mobi
import sys
import matplotlib.animation as animation
import datetime


class GeoPlot(object):
    def __init__(self):

     
        #self.colors=sns.color_palette()
        colors = [ "dusty purple","windows blue", "amber", "greyish", "faded green"]
        self.colors = sns.xkcd_palette(colors)
    
        self.f, self.ax = plt.subplots()
        self.f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)
        self.ax = plt.axes(projection=ccrs.epsg(26910),frameon=False)
        self.ax.background_patch.set_facecolor(self.colors[3])
        
                

        self.left = 485644
        self.right = 495313
        self.bottom = 5453579
        self.top = 5462500

        self.ax.set_extent([self.left,self.right,self.bottom,self.top ], ccrs.epsg(26910))
        
        self.ax.text(self.left+5000,self.bottom+200,'@VanBikeShareBot',color=self.colors[1],size=18,alpha=0.8)
        
        
    def addgeo(self,shapef,edgecolor='black',facecolor='white',alpha=1,zorder=1):
        shape = list(shpreader.Reader(shapef).geometries())
        record = list(shpreader.Reader(shapef).records())
        self.ax.add_geometries(shape, ccrs.epsg(26910),
                      edgecolor=edgecolor, facecolor=facecolor, alpha=alpha,zorder=zorder)
        return shape, record    
        
    
    def draw(self,ddf,date):
        
        self.ax.scatter(ddf['long'],ddf['lat'],transform=ccrs.PlateCarree(),alpha=0.7,s=ddf['trips'],color=self.colors[1],zorder=100)
        
        
       
        # Dummy scatters for the legend
        l1 = self.ax.scatter([0],[0], s=10, edgecolors='none',color=self.colors[1],alpha=0.7)
        l2 = self.ax.scatter([0],[0], s=100, edgecolors='none',color=self.colors[1],alpha=0.7)
        labels=['10','100']
        self.ax.legend([l1,l2],labels,title='Station Activity\n{}'.format(date))

        return self.f
        
        f.savefig(fname,bbox_inches='tight',pad_inches=0.0,transparent = True)

    

    
    
    
def make_station_map(date,fname):
    workingdir='/data/mobi/data'
   
    #Load mobi daily data
    addf = mobi.load_csv(workingdir+'/activity_daily_df.csv')
    ddf = mobi.get_dailydf(workingdir)


    # Get yesterday's trip counts
    trips = addf.loc[date].reset_index()
    trips.columns = ['name','trips']

    ddf = ddf[['coordinates','name']].drop_duplicates()
    ddf = pd.concat([ddf['coordinates'].str.split(',', expand=True),ddf['name']],axis=1)
    ddf.columns = ['lat','long','name']
    ddf.lat = ddf.lat[ddf.lat != ''].astype('float')
    ddf.long = ddf.long[ddf.long != ''].astype('float')

    ddf = pd.merge(trips, ddf, how='inner',on='name')
    
    plot = GeoPlot()
    plot.addgeo('/home/msj/shapes/bikeways.shp',facecolor="none",edgecolor='green',zorder=95)
    plot.addgeo('/home/msj/shapes/shoreline2002.shp',facecolor='#ffffff',zorder=1)
    #plot.addgeo('/home/msj/shapes/greenways.shp',ax,edgecolor='green',alpha=1,zorder=90)
    #plot.addgeo('/home/msj/shapes/public_streets.shp',ax,edgecolor='black',alpha=0,zorder=96)
    f = plot.draw(ddf,date)
    f.savefig(fname,bbox_inches='tight',pad_inches=0.0,transparent = True)
    
    
    
def make_station_ani(date1,fname,days=1,spark=True):
    workingdir='/data/mobi/data'

    date2 = (datetime.datetime.strptime(date1,'%Y-%m-%d') +  datetime.timedelta(days-1)).strftime('%Y-%m-%d')
    

    #Load mobi daily data
    ahdf = mobi.load_csv(workingdir+'/activity_hourly_df.csv')
    ddf = mobi.get_dailydf(workingdir)

    # Get yesterday's trip counts
    trips = ahdf.loc[date1:date2].iloc[0].reset_index()
    trips.columns = ['name','trips']
    ddf = ddf[['coordinates','name']].drop_duplicates()
    ddf = pd.concat([ddf['coordinates'].str.split(',', expand=True),ddf['name']],axis=1)
    ddf.columns = ['lat','long','name']
    ddf.lat = ddf.lat[ddf.lat != ''].astype('float')
    ddf.long = ddf.long[ddf.long != ''].astype('float')

    df = pd.merge(trips, ddf, how='inner',on='name')
    plot = mobi.geomobi.GeoPlot()
    plot.addgeo('/home/msj/shapes/bikeways.shp',facecolor="none",alpha=0.5,edgecolor='green',zorder=95)
    plot.addgeo('/home/msj/shapes/shoreline2002.shp',facecolor='#ffffff',zorder=1)
    #plot.addgeo('/home/msj/shapes/greenways.shp',ax,edgecolor='green',alpha=1,zorder=90)
    #plot.addgeo('/home/msj/shapes/public_streets.shp',ax,edgecolor='black',alpha=0,zorder=96)

    f = plot.f
    f.set_facecolor([0.5,0.5,0.5])
    f.set_size_inches(5,4.7)
    #f.set_edgecolor('gray')
    f.subplots_adjust(left=-0.1, right=1.1, bottom=0, top=1)
    
    
    if spark==True:
        # Add small plot of total activity
        ax2 = f.add_axes([0.02, 0.65, 0.2, 0.2])
        ax2.patch.set_alpha(0)
        ax2.set_axis_off()
        scatter2, = ax2.plot(ahdf[date1:date2].sum(1).index[0],ahdf[date1:date2].sum(1).iloc[0],color=plot.colors[1],marker='o')
        ax2.plot(ahdf[date1:date2].sum(1),color=plot.colors[1])

    
    ax = f.axes[0]
    stations = ax.scatter(df.long,df.lat,color=plot.colors[1],alpha=0.7,s=10*df['trips'],zorder=100,transform=ccrs.PlateCarree())

    # Dummy scatters for the legend
    l1 = ax.scatter([0],[0], s=10, edgecolors='none',color=plot.colors[1],alpha=0.7)
    l2 = ax.scatter([0],[0], s=100, edgecolors='none',color=plot.colors[1],alpha=0.7)
    labels=['1','10']
    legend = ax.legend([l1,l2],labels,title="Station Activity",framealpha=0)
    legend.get_title().set_color(plot.colors[1])
    for lt in legend.get_texts():
        lt.set_color(plot.colors[1])
    
    def t2s(date):
        #return date.strftime('%Y-%m-%d\n%-I %p')
        return date.strftime('%-I %p')
    
    def d2s(date):
        return date.strftime('%a %b %-d')
    
    #text = ax.text(plot.left+200,plot.top-800,d2s(ahdf.loc[date1:date2].index[0]),size=10,bbox=dict(boxstyle="round",ec=(1., 1.0, 1.0),fc=(1., 1, 1),alpha=0.8))
    text = ax.text(plot.left+200,plot.top-800,t2s(ahdf.loc[date1:date2].index[0]),size=25,color=plot.colors[1])
    text2 = ax.text(plot.left+250,plot.top-1200,d2s(ahdf.loc[date1:date2].index[0]),size=10,color=plot.colors[1])
    
    def run(i):
        trips = ahdf.loc[date1:date2].iloc[i].reset_index()
        trips.columns = ['name','trips']
        
        df = pd.merge(trips, ddf, how='inner',on='name')

        stations.set_sizes(df['trips']*10)
        #legend.set_title(ahdf.loc[date1:date2].index[i])
        text.set_text(t2s(ahdf.loc[date1:date2].index[i]))
        text2.set_text(d2s(ahdf.loc[date1:date2].index[i]))
        
        if spark == True:
            scatter2.set_data(ahdf[date1:date2].sum(1).index[i],ahdf[date1:date2].sum(1).iloc[i])
    
    frames=len(ahdf.loc[date1:date2].index)
    ani = animation.FuncAnimation(f, run,frames=frames, interval=1200)
    ani.save(fname,writer='imagemagick')
    
if __name__=='__main__':
    make_station_ani('2018-06-20','ani.gif')