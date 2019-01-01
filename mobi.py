if __name__ == '__main__': 
    import matplotlib as mpl
    mpl.use('AGG')

import pandas as pd
import os
import time
import json
import datetime
from pandas.io.json import json_normalize
import urllib.request
import sys
from helpers import *
from jinja2 import Environment, FileSystemLoader

import plots
import geomobi

def breakdown_ddf(dailydf,workingdir='./'):

    """
    Takes as input input the dataframe created by
    running "query_mobi_api.py" N number of
    times.

    Returns dataframes with the number of bikes
    taken, returned and both, respectively, at
    each query
    """


    # Make pivot table from daily df
    pdf = pd.pivot_table(dailydf,columns='name',index='time',values='avl_bikes')
    pdf.index = pd.to_datetime(pdf.index)
    ddf = pdf.copy()

    for col in pdf.columns:
        ddf[col] = pdf[col] - pdf[col].shift(-1)

    takendf = ddf.fillna(0.0).astype(int)
    returneddf = ddf.fillna(0.0).astype(int)

    takendf[takendf>0] = 0
    returneddf[returneddf<0] = 0

    takendf = takendf*-1

    activitydf = ddf.abs()

    return takendf, returneddf, activitydf


def update_dataframes(takendf, returneddf, activitydf,workingdir='./'):

    """
    Takes as input the dataframes created by "breakdown_ddf()"
    Groups by hour and day to create summary dataframes. Appends
    to existing summary dataframes if extant, otherwise creates
    new pickled dataframes.
    """



    try:
        taken_hourly_df = pd.read_csv('{}/taken_hourly_df.csv'.format(workingdir),index_col=0)
        taken_hourly_df.index = pd.to_datetime(taken_hourly_df.index)

    except:
        #pass
        taken_hourly_df = pd.DataFrame()

    #taken_hourly_df = taken_hourly_df.drop_duplicates()
#    taken_hourly_df = taken_hourly_df.append(takendf.groupby(pd.Grouper(freq='H')).sum())
    taken_hourly_df = pd.concat([taken_hourly_df,takendf.groupby(pd.Grouper(freq='H')).sum()])

    taken_hourly_df = taken_hourly_df.groupby(taken_hourly_df.index).sum()
    taken_daily_df = taken_hourly_df.groupby(pd.Grouper(freq='D')).sum()
    taken_hourly_df.to_csv('{}/taken_hourly_df.csv'.format(workingdir))
    taken_daily_df.to_csv('{}/taken_daily_df.csv'.format(workingdir))

    try:
        returned_hourly_df = pd.read_csv('{}/returned_hourly_df.csv'.format(workingdir),index_col=0)
        returned_hourly_df.index = pd.to_datetime(returned_hourly_df.index)
    except:
        returned_hourly_df = pd.DataFrame()

    #returned_hourly_df = returned_hourly_df.drop_duplicates()
#    returned_hourly_df = returned_hourly_df.append(returneddf.groupby(pd.Grouper(freq='H')).sum())
    returned_hourly_df = pd.concat([returned_hourly_df,returneddf.groupby(pd.Grouper(freq='H')).sum()])
    returned_hourly_df = returned_hourly_df.groupby(returned_hourly_df.index).sum()
    returned_daily_df = returned_hourly_df.groupby(pd.Grouper(freq='D')).sum()
    returned_hourly_df.to_csv('{}/returned_hourly_df.csv'.format(workingdir))
    returned_daily_df.to_csv('{}/returned_daily_df.csv'.format(workingdir))

    try:
        activity_hourly_df = pd.read_csv('{}/activity_hourly_df.csv'.format(workingdir),index_col=0)
        activity_hourly_df.index = pd.to_datetime(activity_hourly_df.index)
    except:
        activity_hourly_df = pd.DataFrame()

    #activity_hourly_df = activity_hourly_df.drop_duplicates()
    #activity_hourly_df = activity_hourly_df.append(activitydf.groupby(pd.Grouper(freq='H')).sum())
    activity_hourly_df = pd.concat([activity_hourly_df,activitydf.groupby(pd.Grouper(freq='H')).sum()])
    activity_hourly_df = activity_hourly_df.groupby(activity_hourly_df.index).sum()
    activity_daily_df = activity_hourly_df.abs().groupby(pd.Grouper(freq='D')).sum()
    activity_hourly_df.to_csv('{}/activity_hourly_df.csv'.format(workingdir))
    activity_daily_df.to_csv('{}/activity_daily_df.csv'.format(workingdir))




def query_mobi_api(workingdir='.'):
    daily_df = '{}/daily_mobi_dataframe.csv'.format(workingdir)

    # Query mobi API
    with urllib.request.urlopen("http://vancouver-ca.smoove.pro/api-public/stations") as url:
        data = json.loads(url.read().decode())

    # Try to load daily df. If it doesn't exist, create it. Append newly queried data to the end of it.
    try:
        df = pd.read_csv(daily_df)
    except:
        df = pd.DataFrame()

    newdf = json_normalize(data['result'])
    newdf['time'] = datetime.datetime.now()
    newdf['id'],newdf['name'] = newdf['name'].str.split(' ', 1).str

    df = df.append(newdf,ignore_index=True)
    df.to_csv(daily_df,index=False)


def get_stations(workingdir):
    dailydf  = get_dailydf(workingdir)
    avail_df = pd.pivot_table(dailydf,columns='name',index='time',values='avl_bikes').iloc[-1]
    op_df    = pd.pivot_table(dailydf,columns='name',index='time',values='operative').iloc[-1]

    avail_df[op_df==False] = -1

    avail_df = pd.DataFrame(avail_df).transpose()
    avail_df.index = [x.strftime('%Y-%m-%d') for x in avail_df.index]

    try:
        stations_df = load_csv(workingdir+'/stations_daily_df.csv')
        stations_df = pd.concat([stations_df,avail_df])
    except:
        stations_df = avail_df

        
    stations_df.to_csv(workingdir+'/stations_daily_df.csv')

def get_status(workingdir):
    stations_df = load_csv(workingdir+'/stations_daily_df.csv')
    avail_bikes = stations_df.iloc[-1]
    n_bikes     = int(sum(avail_bikes[avail_bikes>=0]))
    n_stations  = int(len(avail_bikes[avail_bikes>=0]))
    n_closed    = int(sum(avail_bikes[avail_bikes<0]))


    return {'bikes':n_bikes,'stations':n_stations}


def update_html(workingdir):
    
    tddf = load_csv('{}/taken_daily_df.csv'.format(workingdir))
    thdf = load_csv('{}/taken_hourly_df.csv'.format(workingdir))

    tddf = tddf['2017-07':]
    thdf = thdf['2017-07':]
    
    
    # Station activity
    sddf = load_csv('{}/stations_daily_df.csv'.format(workingdir))
    active_stations = (sddf.iloc[-1]>-1).index  # index of active stations 

    tdf = thdf.loc[:,active_stations].sum()
    t24df = thdf.ix[-25:-1,active_stations].sum()
    station24h = t24df.idxmax()
    stationalltime = tdf.idxmax()

    station24hmin = t24df.idxmin()
    stationalltimemin = tdf.idxmin()

    status = get_status(workingdir)



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

    
if __name__ == '__main__':
    


    if len(sys.argv) < 3:
        usage = """
                 Usage: mobi.py [arg] [working directory]
                 arg must be one of:
                 --query   : query mobi api to update the daily database
                             (run every minute)
                 --update  : Compile hourly/daily stats and append to database
                 """
        print(usage)
        quit()

    arg = sys.argv[1]
    workingdir=os.path.normpath(sys.argv[2])


    if arg == '--update':
        # Load daily dataframe
        
        dailydf = pd.read_csv('{}/daily_mobi_dataframe.csv'.format(workingdir))
        a,b,c = breakdown_ddf(dailydf)
        update_dataframes(a,b,c,workingdir=workingdir)

        # Rename daily df
        timestr = time.strftime("%Y%m%d-%H%M%S")
        os.rename('{}/daily_mobi_dataframe.csv'.format(workingdir),'{}/backups/daily_mobi_dataframe.csv_BAK_{}'.format(workingdir,timestr))


    elif arg == '--query':
        query_mobi_api(workingdir=workingdir)


    elif arg == '--stations':
        get_stations(workingdir)

    elif arg == '--status':
        print(get_status(workingdir))
        
    elif arg == '--plots':
        #tddf = load_csv('{}/taken_daily_df.csv'.format(workingdir))
        thdf = load_csv('{}/taken_hourly_df.csv'.format(workingdir))

        #tddf = tddf['2017-07':]
        #thdf = thdf['2017-07':]
        tddf = thdf.groupby(pd.Grouper(freq='D')).sum()
        
        ######## HACK TO FIX FIREWORKS REBALANCING
        #thdf.loc['2018-07-28 11:00:00'] = thdf.loc['2018-07-28 10:00:00']//2
        def fix(x):
            if x>20:
                return x//2
            else: return x
        #thdf.loc['2018-07-28 11:00:00'] = thdf.loc['2018-07-28 10:00:00'].map(fix)
        
        
        imdir = '/var/www/html/mobi/images/'
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        thisyear = datetime.datetime.now().strftime('%Y')
        yday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        yday_min7 = (datetime.datetime.now() - datetime.timedelta(8)).strftime('%Y-%m-%d')
        yday_min31 = (datetime.datetime.now() - datetime.timedelta(31)).strftime('%Y-%m-%d')


        #print(yday)
        #print(yday_min7)

        #print(thdf.sum(1).loc[yday_min7:yday])

        
        plots.Plot().draw(tddf.sum(1).iloc[-365:],imdir+'lastyear_daily.png',weather=True)
        plots.Plot().draw(tddf.sum(1).iloc[-30:],imdir+'lastmonth_daily.png',kind='bar',weather=True,highlight=True)
        plots.Plot().draw(thdf.sum(1).iloc[-7*24:-1],imdir+'lastweek_hourly.png',kind='line')
        plots.Plot().draw(tddf.sum(1),imdir+'alltime_rolling.png',weather=True,rolling=7)
        plots.Plot().draw(thdf.sum(1).loc[yday_min7:yday],imdir+'lastweek_hourly_yesterday.png')
        
        plots.Plot().draw(thdf[thisyear:],imdir+'today_cumsum.png',kind='cumsum')
        plots.Plot().draw(thdf[thisyear:yday],imdir+'yesterday_cumsum.png',kind='cumsum')

        plots.Plot().draw(tddf.sum(1).loc[yday_min31:yday],imdir+'lastmonth_daily_yesterday.png',kind='bar',weather=True,highlight=True)


        #print(yday)
        geomobi.make_station_map(yday,imdir+'station_map_yesterday.png')
        geomobi.make_station_ani(yday,imdir+'station_ani_yesterday.gif')
                         
                         
    elif arg == '--html':
        update_html(workingdir)
