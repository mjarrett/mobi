import pandas as pd
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import shapely
import pyproj
import mobi

def prep_sys_df(f): 
    df = pd.read_csv(f,low_memory=False)

    #df = df[df['Membership Type']!='VIP']

    df['Duration (min.)'] = df['Duration (sec.)'].map(lambda x: x/60)

    stations_exclude = ['station for tests','WareHouse Workshop','Balancer Bike Check In','Temporary Station - Marketing Events']
    df = df[~df['Departure station'].isin(stations_exclude)]
    df = df[~df['Return station'].isin(stations_exclude)]

    # Drop duplicate trips:
    # This removes cases where multiple bikes take the same trip on the same account
    # Also will remove cases where someone takes the same trip within an hour.
    df = df.drop_duplicates(subset=['Departure','Return','Account','Departure station','Return station'])

    # Drop trips shorter than 60 seconds
    df = df[df['Duration (sec.)']>60]

    # Get average speed
    df['average speed (km/h)'] = (df['Covered distance (m)']/1000) / ((df['Duration (sec.)']-df['Stopover duration (sec.)'])/3600)
    
    df = df.dropna()
    
    df['Departure'] = pd.to_datetime(df['Departure'])
    df['Return'] = pd.to_datetime(df['Return'])
    
    
    
    return df


def get_mem_types(df):
    
    idx24 = list(df['Membership Type']=='24 Hour')
    idx365 = list(df['Membership Type'].str.contains('365.+Standard'))
    idx365p = list(df['Membership Type'].str.contains('365.+Plus'))
    idx365all = list(df['Membership Type'].str.contains('365'))
    idx90 = list(df['Membership Type'].str.contains('90'))
    
    return idx24,idx365,idx365p,idx365all,idx90


def add_station_coords(df,sdf,bidirectional=True):
    
    """
    WARNING: This drops records if the listed Departer/Return station name
             isn't in the stations_df.json file"
    """

    epsg  = pyproj.Proj(init='epsg:26910')
    pc = pyproj.Proj(proj='latlon')

    shapef = '/home/msj/shapes/local_area_boundary.shp'
    shapes = list(shpreader.Reader(shapef).geometries())
    records = list(shpreader.Reader(shapef).records())


    sdf['coordinates epsg'] = sdf['coordinates'].map(lambda x: pyproj.transform(pc,epsg, x[1],x[0]) )

    def f(coord):
        hoods =  [r.attributes['NAME'] for s,r in zip(shapes,records) if s.contains(shapely.geometry.Point(*coord))]
        if len(hoods) == 0:
            return "Stanley Park"
        else:
            return hoods[0]


    sdf['neighbourhood'] = sdf['coordinates epsg'].map(lambda x: f(x))

    df = pd.merge(df,sdf[['name','neighbourhood','coordinates']],how='inner',left_on='Departure station',right_on='name',
                  suffixes=('_x',' departure'))

    df = pd.merge(df,sdf[['name','neighbourhood','coordinates']],how='inner',left_on='Return station',right_on='name',
                  suffixes=(' departure',' return'))



    df = df.rename(columns={'neighbourhood return':'Return neighbourhood',
                    'neighbourhood departure':'Departure neighbourhood',
                    'coordinates return':'Return coords',
                    'coordinates departure':'Departure coords'})
    del df['name departure']
    del df['name return']


    df['stations coords'] = df[['Departure coords','Return coords']].values.tolist()
    df['stations'] = df[['Departure station','Return station']].values.tolist()
    df['stations coords'] = df['stations coords'].map(lambda x: tuple(sorted(x)))
    df['stations'] = df['stations'].map(lambda x: tuple(sorted(x)))
    


    return df


def make_con_df(df):
    condf = df.groupby(['stations coords','stations']).size()

    condf = condf.reset_index()
    condf.columns = ['stations coords','stations','trips']
    
    condf['start coords'] = condf['stations coords'].map(lambda x: x[0])
    condf['stop coords'] = condf['stations coords'].map(lambda x: x[1])
    condf['start station'] = condf['stations'].map(lambda x: x[0])
    condf['stop station'] = condf['stations'].map(lambda x: x[1])
    return condf