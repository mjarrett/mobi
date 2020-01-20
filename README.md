# Mobi API query and analysis

**This package is deprecated**. See the [Bikedata](https://github.com/mjarrett/bikedata) package instead.

Some tools for grabbing live data from the Mobi API and storing it in Pandas Dataframes. 

## Usage



### Query API

```python3 mobi.py --query /path/to/workingdirectory/```

The first time this is run it will create a CSV file "daily_mobi_dataframe.csv" with a single row corresponding to the number of bikes currently at each station. Subsequent calls will add rows to the dataframe. I don't know how often Mobi updates the API, but I run this as a cron job every minute.

### Update analysis dataframes

Continuously updating the dataframe via the above script quickly becomes inneficient, and loading the dataframe every minute will kill your computer's performance after a few days. So once a day I run a second script to break down the raw data to more manageable datasets.

```python3 mobi.py --update /path/to/workingdirectory```

This will make 6 new CSV files -- one each for bikes taken from, returned to, or both from each station, then grouped by either hours or days. 

The  minute-by-minute dataframe is backed up and renamed with the current date and time. Keep or remove at your discretion.

### Secondary options
```python3 mobi.py --stations /path/to/workingdirectory/```

Create/update a CSV file with the number of available bikes at each station, or -1 for out-of-service stations. I run this at 4am daily (when there are close to zero ongoing trip) to get a snapshot of the total number of bikes and stations

```python3 mobi.py --status /path/to/workingdirectory/```

Prints the total number of bikes and active stations based on the last row in the csv file created with the --stations command.



## Analysis

I will include Jupyter notebooks with analysis of this data as I complete them

## Full dataset

If you would like access to the full dataset, please contact me directly: mike@mikejarrett.ca


