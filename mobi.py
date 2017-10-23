import pandas as pd
import os
import time
import json






def breakdown_ddf(dailydf,workingdir='./'):

  """
  Takes as input input the dataframe created by
  running "query_mobi_database.py" N number of 
  times. 

  Returns dataframes with the number of bikes
  taken, returned and both, respectively, at 
  each query
  """

  
  # Make pivot table from daily df
  pdf = pd.pivot_table(dailydf,columns='name',index='time',values='avl_bikes')
  ddf = pdf.copy()

  for col in pdf.columns:
    ddf[col] = pdf[col] - pdf[col].shift(-1)

  takendf = ddf.fillna(0.0).astype(int)
  returneddf = ddf.fillna(0.0).astype(int)

  takendf[takendf>0] = 0
  returneddf[returneddf<0] = 0

  takendf = takendf*-1

  activitydf = ddf.abs()
  
  # Convert to correct timezone
  takendf  = takendf.tz_localize('UTC').tz_convert('US/Pacific')
  returneddf = returneddf.tz_localize('UTC').tz_convert('US/Pacific')
  activitydf = activitydf.tz_localize('UTC').tz_convert('US/Pacific')


  return takendf, returneddf, activitydf


def update_dataframes(takendf, returneddf, activitydf,workingdir='./'):

  """
  Takes as input the dataframes created by "breakdown_ddf()"
  Groups by hour and day to create summary dataframes. Appends
  to existing summary dataframes if extant, otherwise creates
  new pickled dataframes.
  """


  
  try:
    taken_hourly_df = pd.read_pickle('{}/taken_hourly_df.p'.format(workingdir))
  except:
    taken_hourly_df = pd.DataFrame()
  taken_hourly_df = taken_hourly_df.append(takendf.groupby(pd.TimeGrouper(freq='H')).sum())
  taken_daily_df = taken_hourly_df.groupby(pd.TimeGrouper(freq='D')).sum()
  taken_hourly_df.to_pickle('{}/taken_hourly_df.p'.format(workingdir))
  taken_daily_df.to_pickle('{}/taken_daily_df.p'.format(workingdir))

  try:
    returned_hourly_df = pd.read_pickle('{}/returned_hourly_df.p'.format(workingdir))
  except:
    returned_hourly_df = pd.DataFrame()
  returned_hourly_df = returned_hourly_df.append(returneddf.groupby(pd.TimeGrouper(freq='H')).sum())
  returned_daily_df = returned_hourly_df.groupby(pd.TimeGrouper(freq='D')).sum()
  returned_hourly_df.to_pickle('{}/returned_hourly_df.p'.format(workingdir))
  returned_daily_df.to_pickle('{}/returned_daily_df.p'.format(workingdir))


  try:
    activity_hourly_df = pd.read_pickle('{}/activity_hourly_df.p'.format(workingdir))
  except:
    activity_hourly_df = pd.DataFrame()
  activity_hourly_df = activity_hourly_df.append(activitydf.groupby(pd.TimeGrouper(freq='H')).sum())
  activity_daily_df = activity_hourly_df.abs().groupby(pd.TimeGrouper(freq='D')).sum()
  activity_hourly_df.to_pickle('{}/activity_hourly_df.p'.format(workingdir))
  activity_daily_df.to_pickle('{}/activity_daily_df.p'.format(workingdir))



if __name__ == '__main__':
  import sys
  #print('testing...')
  workingdir=os.path.normpath(sys.argv[1])

  # Load daily dataframe
  dailydf = pd.read_pickle('{}/daily_mobi_dataframe.p'.format(workingdir))


  a,b,c = breakdown_ddf(dailydf)
  update_dataframes(a,b,c)

  
  # Rename daily df
  timestr = time.strftime("%Y%m%d-%H%M%S")
  os.rename('{}/daily_mobi_dataframe.p'.format(workingdir),'{}/daily_mobi_dataframe.p_BAK_{}'.format(workingdir,timestr))
