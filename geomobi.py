import matplotlib as mpl

if __name__ == '__main__':
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


    
    
    
def make_station_map(date,fname,workingdir):
    #workingdir='/data/mobi/data/'
   
    #Load mobi daily data
    tddf = mobi.load_csv(workingdir+'/taken_daily_df.csv')
    rddf = mobi.load_csv(workingdir+'/returned_daily_df.csv')
    addf = tddf + rddf
    ddf = mobi.get_dailydf(workingdir)
    

    # Get day's trip counts
    trips = addf.loc[date].reset_index()
    trips.columns = ['name','trips']

    
    sdf = mobi.get_stationsdf(workingdir)
    sdf = pd.merge(trips, sdf, how='inner',on='name')
    #print(sdf.loc[0,'coordinates'][0]/2)
    
    
    plot = mobi.GeoPlot()
    plot.addgeo('/home/msj/shapes/bikeways.shp',facecolor="none",edgecolor='green',zorder=95)
    plot.addgeo('/home/msj/shapes/shoreline2002.shp',facecolor='#ffffff',zorder=1)
    f = plot.draw(sdf,date)
    

        
    f.savefig(fname,bbox_inches='tight',pad_inches=0.0,transparent=True)
    
    
    
def make_station_ani(date1,fname,workingdir,days=1,spark=True):
    #workingdir='/data/mobi/data'

    date2 = (datetime.datetime.strptime(date1,'%Y-%m-%d') +  datetime.timedelta(days-1)).strftime('%Y-%m-%d')
    

    #Load mobi daily data
    thdf = mobi.load_csv(workingdir+'/taken_hourly_df.csv')
    rhdf = mobi.load_csv(workingdir+'/returned_hourly_df.csv')
    ahdf = thdf	+ rhdf
    
    sdf = mobi.get_stationsdf(workingdir)
    # Only active stations
    ahdf = ahdf[sdf.loc[sdf['active'],'name']]
    
    # Get day's trip counts
    trips = ahdf.loc[date1:date2].iloc[0].reset_index()
    trips.columns = ['name','trips']
    # Add yesterday's trip counts
    df = pd.merge(trips, sdf, how='inner',on='name')
    df['lat'] = df['coordinates'].map(lambda x:x[0])
    df['long'] = df['coordinates'].map(lambda x:x[1])

    #df = pd.merge(trips, ddf, how='inner',on='name')
    plot = mobi.GeoPlot()
    plot.addgeo('/home/msj/shapes/bikeways.shp',facecolor="none",alpha=0.5,edgecolor='green',zorder=95)
    plot.addgeo('/home/msj/shapes/shoreline2002.shp',facecolor='#ffffff',zorder=1)

   
    
    plot.f.set_facecolor([0.5,0.5,0.5])
    plot.f.set_size_inches(5,4.7)
    plot.f.subplots_adjust(left=-0.1, right=1.1, bottom=0, top=1)
    
    
    if spark==True:
        # Add small plot of total activity
        ax2 = plot.f.add_axes([0.02, 0.65, 0.2, 0.2])
        ax2.patch.set_alpha(0)
        ax2.set_axis_off()
        scatter2, = ax2.plot(ahdf[date1:date2].sum(1).index[0],
                             ahdf[date1:date2].sum(1).iloc[0],
                             color=plot.fg_color2,marker='o')
        ax2.plot(ahdf[date1:date2].sum(1),color=plot.fg_color2)

    
    ax = plot.f.axes[0]

    # Draw stations
    stations = ax.scatter(df.long,df.lat,
                         color=plot.fg_color2,alpha=0.7,
                         s=10*df['trips'],
                         zorder=100,transform=ccrs.PlateCarree())

                              
                              
                
    # Dummy scatters for the legend
    l1 = ax.scatter([0],[0], s=10, edgecolors='none',color=plot.fg_color2,alpha=0.7)
    l2 = ax.scatter([0],[0], s=100, edgecolors='none',color=plot.fg_color2,alpha=0.7)
    labels=['1','10']
    legend = ax.legend([l1,l2],labels,title="Station Activity",framealpha=0)
    legend.get_title().set_color(plot.fg_color2)
    for lt in legend.get_texts():
        lt.set_color(plot.fg_color2)
    
    def t2s(date):
        #return date.strftime('%Y-%m-%d\n%-I %p')
        return date.strftime('%-I %p')
    
    def d2s(date):
        return date.strftime('%a %b %-d')
    
    #text = ax.text(plot.left+200,plot.top-800,d2s(ahdf.loc[date1:date2].index[0]),size=10,bbox=dict(boxstyle="round",ec=(1., 1.0, 1.0),fc=(1., 1, 1),alpha=0.8))
    text = ax.text(plot.left+200,
                   plot.top-800,
                   t2s(ahdf.loc[date1:date2].index[0]),
                   size=25,color=plot.fg_color2)
    text2 = ax.text(plot.left+250,
                    plot.top-1200,
                    d2s(ahdf.loc[date1:date2].index[0]),
                    size=10,color=plot.fg_color2)
    
    def run(i):
        trips = ahdf.loc[date1:date2].iloc[i].reset_index()
        trips.columns = ['name','trips']
        
        df = pd.merge(trips, sdf, how='inner',on='name')

        stations.set_sizes(df['trips']*10)
        #legend.set_title(ahdf.loc[date1:date2].index[i])
        text.set_text(t2s(ahdf.loc[date1:date2].index[i]))
        text2.set_text(d2s(ahdf.loc[date1:date2].index[i]))
        
        if spark == True:
            scatter2.set_data(ahdf[date1:date2].sum(1).index[i],ahdf[date1:date2].sum(1).iloc[i])
    
    frames=len(ahdf.loc[date1:date2].index)
    ani = animation.FuncAnimation(plot.f, run,frames=frames, interval=1200)
    ani.save(fname,writer='imagemagick')
    
if __name__=='__main__':
    #make_station_ani('2018-11-20','ani.gif','/data/mobi/data/')
    make_station_map('2019-01-10','geoplot.png','/data/mobi/data/')