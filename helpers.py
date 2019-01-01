import pandas as pd

def load_csv(f):
    df = pd.read_csv(f,index_col=0,parse_dates=[0])
    return df

def get_dailydf(d):
    ddf = pd.read_csv(d+'/daily_mobi_dataframe.csv',parse_dates=['time'])
    ddf['coordinates'] = ddf['coordinates'].map(lambda x: x.split(','))
    ddf['coordinates'] = ddf['coordinates'].map(lambda x: [float(x[0]),float(x[1])])
    return ddf
    
# ddf = get_dailydf('/data/mobi/data/')
# print(ddf['coordinates'])






