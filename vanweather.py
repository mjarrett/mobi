#!/usr/bin/env python3

import pandas as pd
from datetime import datetime

def get_monthly_weather(year,month):

    baseurl='http://climate.weather.gc.ca/climate_data/daily_data_e.html?hlyRange=2013-06-11%7C2017-05-06&dlyRange=2013-06-13%7C2017-05-06&mlyRange=%7C&StationID=51442&Prov=BC&urlExtension=_e.html&searchType=stnName&optLimit=yearRange&StartYear=1840&EndYear=2017&selRowPerPage=25&Line=39&searchMethod=contains&Month={}&Day=1&txtStationName=vancouver&timeframe=2&Year={}'.format(month,year)

    df = pd.read_html(baseurl,header=0)[0]

    df = df.iloc[1:-4]
    #print(df.columns[1:])
    #print(['Day'] + df.columns[1:])
    df.columns = ['Day'] + list(df.columns[1:])
    df.columns = [ x.replace(' Definition','') for x in df.columns]
    df.columns = [ x.replace('°C','') for x in df.columns]
    df['Day'] = df['Day'].str.split().apply(lambda x:x[0])
    df['Day'] = df['Day']+'-{}-{}'.format(month,year)
    df['Day'] = pd.to_datetime(df['Day'], format='%d-%m-%Y')
    #df['Day'] = df['Day'][0]
    df = df.set_index('Day')
    df = df.apply(pd.to_numeric, errors='coerce')


    return df

def get_weather_range(time1,time2):
    year1,month1 = time1
    year2,month2 = time2

    df = pd.DataFrame()


    #run through rest of 1st year
    if year2 - year2 < 1:
        for m in range(month1,month2+1):
            #print(year1,m)
            df = df.append(get_monthly_weather(year1,m))

    # run through middle years if any
    if year2 - year1 > 1:
        for m in range (month1,13):
            print(year1,m)
            df = df.append(get_monthly_weather(year1,m))

        for y in range(year1+1,year2):
            for m in range(1,13):
                print(y,m)
                df = df.append(get_monthly_weather(y,m))

        #run through last year
        for m in range(1,month2+1):
            print(year2,m)
            df = df.append(get_monthly_weather(year2,m))

    return df
# df = get_weather_range((2015,5),(2017,4))
# print(df)
#df = get_monthly_weather(2016,4)

#print(df)
