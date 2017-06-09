# Mobi API query and analysis

Some tools for grabbing live data from the Mobi API and storing it in Pandas Dataframes. 

## Usage


### Setup config file

Currently you just need to set a working directory in the config file where your data will be stored. Leave it untouched to use present directory

### Query API

```python3 query_mobi_api.py```

The first time this is run it will create a pickled dataframe "daily_mobi_dataframe.p" with a single row corresponding to the number of bikes currently at each station. Subsequent calls will add rows to the dataframe. I don't know how often Mobi updates the API, but I run this as a cron job every minute.

### Update analysis dataframes

Continuously updating the dataframe via the above script quickly becomes inneficient, and loading the dataframe every minute will kill your computer's performance after a few days. So once a day I run a second script to break down the raw data to more manageable datasets.

```python3 update_mobi_dataframes.py```

This will make 6 new pickled dataframes -- one each for bikes taken from, returned to, or both from each station, then grouped by either hours or days. 

The full minute-by-minute dataframe is backed up and renamed with the current date and time. Keep or remove at your discretion.

