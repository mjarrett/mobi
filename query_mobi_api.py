import pandas as pd
import json
import datetime
from pandas.io.json import json_normalize
import urllib.request
import os

#filedir = os.path.dirname(os.path.realpath(__file__))
#filedir = os.path.dirname(__file__)
#print(filedir)
#with open(filedir+'/config.json') as json_data_file:
#    data = json.load(json_data_file)
#workingdir = data['datadir']
workingdir = '/home/msj/repos/mobi/'

daily_df = '{}daily_mobi_dataframe.p'.format(workingdir)
#print(daily_df)
#with open('stations.json') as data_file:
#    data = json.load(data_file)

with urllib.request.urlopen("http://vancouver-ca.smoove.pro/api-public/stations") as url:
    data = json.loads(url.read().decode())
 #   print(data)

try:
    df = pd.read_pickle(daily_df)
except:
    df = pd.DataFrame()

newdf = json_normalize(data['result'])
newdf['time'] = datetime.datetime.now()
newdf['id'],newdf['name'] = newdf['name'].str.split(' ', 1).str


df = df.append(newdf,ignore_index=True)

df.to_pickle(daily_df)
