import matplotlib as mpl
mpl.use('AGG')

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mobi

def addgeo(shapef,ax,edgecolor='black',facecolor='white',alpha=1,zorder=1):
    shape = list(shpreader.Reader(shapef).geometries())
    record = list(shpreader.Reader(shapef).records())
    ax.add_geometries(shape, ccrs.epsg(26910),
                  edgecolor=edgecolor, facecolor=facecolor, alpha=alpha,zorder=zorder)
    return shape, record


def make_station_map(date,fname):
    f, ax = plt.subplots()
    ax = plt.axes(projection=ccrs.epsg(26910),frameon=False)
    ax.background_patch.set_facecolor('gray')

    colors=sns.color_palette()

    left = 485644
    right = 495313
    bottom = 5453579
    top = 5462500

    ax.set_extent([left,right,bottom,top ], ccrs.epsg(26910))
   
    bikeways = addgeo('/home/msj/shapes/bikeways.shp',ax,facecolor="none",edgecolor='green',zorder=95)

    coast,coastr = addgeo('/home/msj/shapes/shoreline2002.shp',ax,facecolor='#000000',zorder=1)
    #greenways = addgeo('/home/msj/shapes/greenways.shp',ax,edgecolor='green',alpha=1,zorder=90)
    streets = addgeo('/home/msj/shapes/public_streets.shp',ax,edgecolor='black',alpha=0,zorder=96)
    
    
    #Load mobi daily data
    addf = mobi.load_csv('/data/mobi/data/activity_daily_df.csv')
    ddf = mobi.get_dailydf('/data/mobi/data/')
    # Station activity
    sddf = mobi.load_csv('/data/mobi/data/stations_daily_df.csv')
    active_stations = (sddf.iloc[-1]>-1).index  # index of active stations 
    
    # Get yesterday's trip counts
    trips = addf.loc[date].reset_index()
    trips.columns = ['name','trips']

    
    ddf = ddf.set_index('name').loc[active_stations].reset_index()
    ddf = ddf[['coordinates','name']].drop_duplicates()
    ddf = pd.concat([ddf['coordinates'].str.split(',', expand=True),ddf['name']],axis=1)
    ddf.columns = ['lat','long','name']
    ddf.lat = ddf.lat[ddf.lat != ''].astype('float')
    ddf.long = ddf.long[ddf.long != ''].astype('float')
    
    ddf = pd.merge(trips, ddf, how='inner',on='name')
    
    
    sizes = ddf['trips']
    ax.scatter(ddf['long'],ddf['lat'],transform=ccrs.PlateCarree(),alpha=0.7,s=sizes,color=colors[0],zorder=100)
    
    
    # Dummy scatters for the legend
    l1 = ax.scatter([0],[0], s=10, edgecolors='none',color=colors[0],alpha=0.7)
    l2 = ax.scatter([0],[0], s=100, edgecolors='none',color=colors[0],alpha=0.7)
    labels=['10','100']
    ax.legend([l1,l2],labels,title='Station Activity\n{}'.format(date))
    
    f.savefig(fname,bbox_inches='tight',pad_inches=0.0,transparent = True)
    
if __name__=='__main__':
    make_station_map('2018-06-08','station_plot.png')