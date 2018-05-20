import pandas as pd
import json
import datetime
from pandas.io.json import json_normalize
import urllib.request
import os
import sys

#workingdir = '/home/msj/repos/mobi/'
workingdir = sys.argv[1]

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
