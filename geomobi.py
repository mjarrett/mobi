import matplotlib as mpl
mpl.use('AGG')

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mobi
import sys



class GeoPlot(object):
    def __init__(self):

        
        self.f, self.ax = plt.subplots()
        self.ax = plt.axes(projection=ccrs.epsg(26910),frameon=False)
        self.ax.background_patch.set_facecolor('gray')
        
                
        self.colors=sns.color_palette()

        left = 485644
        right = 495313
        bottom = 5453579
        top = 5462500

        self.ax.set_extent([left,right,bottom,top ], ccrs.epsg(26910))
        
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
    plot.addgeo('/home/msj/shapes/shoreline2002.shp',facecolor='#000000',zorder=1)
    #plot.addgeo('/home/msj/shapes/greenways.shp',ax,edgecolor='green',alpha=1,zorder=90)
    #plot.addgeo('/home/msj/shapes/public_streets.shp',ax,edgecolor='black',alpha=0,zorder=96)
    f = plot.draw(ddf,date)
    f.savefig(fname)
    
if __name__=='__main__':
    make_station_map('2018-05-11','test.png')