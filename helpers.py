import pandas as pd

def load_csv(f):
    df = pd.read_csv(f,index_col=0,parse_dates=[0])
    return df

def get_dailydf(f):
    ddf = pd.read_csv(f,parse_dates=['time'])
    ddf['coordinates'] = ddf['coordinates'].map(lambda x: x.split(','))
    ddf['coordinates'] = ddf['coordinates'].map(lambda x: [float(x[0]),float(x[1])])
    return ddf
    
# ddf = get_dailydf('/data/mobi/data/')
# print(ddf['coordinates'])


def update_stations_df(workingdir):
    ddf = get_dailydf('{}/daily_mobi_dataframe.csv'.format(workingdir))
    try:
        sdf = load_csv('{}/stations_df.csv'.format(workingdir))
    except:
        sdf = pd.DataFrame()


    ddf = ddf.drop_duplicates('name').copy()
    ddf = ddf[['coordinates','name']]
    ddf['coordinates'] = ddf['coordinates'].map(lambda x:tuple(x))
    ddf = ddf.set_index('name')

    sdf = pd.concat([sdf,ddf])
    sdf = sdf[~sdf.index.duplicated(keep='last')]
    
    #sdf.to_csv('{}/stations_df.csv'.format(workingdir))
    sdf.to_json('{}/stations_df.json'.format(workingdir))
