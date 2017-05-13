#!/usr/bin/env python3

import pandas as pd

print('Loading mobi data...')
df = pd.read_pickle('/Users/msj/Dropbox/mobi/df.p')

pdf = pd.pivot_table(df,columns='name',index='time',values='avl_bikes')

ddf = pdf.copy()

for col in pdf.columns:
  ddf[col] = pdf[col] - pdf[col].shift(-1)


hdf = ddf.groupby(pd.TimeGrouper(freq='H')).sum().abs()

print('df  = full minute-by-minute dataset')
print('pdf = pivoted df with values=available bikes')
print('ddf = minute-by-minute change in available bikes')
print('hdf = hourly bike usage (total bikes taken + total bikes returned)')
