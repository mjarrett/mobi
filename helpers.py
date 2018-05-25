import pandas as pd

def load_csv(f):
    df = pd.read_csv(f,index_col=0,parse_dates=[0])
    return df

def get_dailydf(d):
    return pd.read_csv(d+'/daily_mobi_dataframe.csv',parse_dates=['time'])






