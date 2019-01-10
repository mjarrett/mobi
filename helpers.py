import pandas as pd

def load_csv(f):
    df = pd.read_csv(f,index_col=0,parse_dates=[0])
    return df

def get_dailydf(d):
    ddf = pd.read_csv('{}/daily_mobi_dataframe.csv'.format(d),parse_dates=['time'])
    ddf['coordinates'] = ddf['coordinates'].map(lambda x: x.split(','))
    ddf['coordinates'] = ddf['coordinates'].map(lambda x: [float(x[0]),float(x[1])])
    return ddf
    
# ddf = get_dailydf('/data/mobi/data/')
# print(ddf['coordinates'])


def update_stations_df(workingdir):
    ddf = get_dailydf(workingdir)
    try:
        sdf = pd.read_json('{}/stations_df.json'.format(workingdir))
    except:
        sdf = pd.DataFrame()


    ddf = ddf.drop_duplicates('name').copy()
    ddf = ddf[['coordinates','name']]
    ddf['coordinates'] = ddf['coordinates'].map(lambda x:tuple(x))
    ddf = ddf.set_index('name')

    sdf['coordinates'] = sdf['coordinates'].map(lambda x:tuple(x))
    sdf = pd.concat([sdf,ddf])
    sdf = sdf[~sdf.index.duplicated(keep='last')]
  
    
    #sdf.to_csv('{}/stations_df.csv'.format(workingdir))
    sdf.to_json('{}/stations_df.json'.format(workingdir))
