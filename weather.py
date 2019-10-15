"""
Gets the weather data from dark sky API and dumps it into
the weather collection within the walk MongoDB.

Based on Cristian Nuno's soccer_stats/Weather_Getter and export_weather
https://github.com/cenuno/soccer_stats/blob/master/python/export_weather.py
https://github.com/cenuno/soccer_stats/blob/master/python/weathergetter.py
"""

# load necessary modules
import pandas as pd
from datetime import datetime, timedelta, date
import requests
import json
from pymongo import MongoClient

# secret file location
secret_loc = "/Users/allisonhonold/.secrets/dark_sky_api.json"

def main():
    # load dates from 01/01/2006 to most recent
    final_date_df = pd.read_csv('../nyc_ytd.csv', 
                        usecols=['ARREST_DATE'],
                        nrows=2)
    final_date = datetime.strptime(final_date_df.loc[0, 'ARREST_DATE'], '%m/%d/%Y')
    initial_date = datetime.strptime('01/01/2006', '%m/%d/%Y')
    dates = [initial_date + timedelta(x) for x in range(int((final_date - initial_date).days)+1)]


    # load secret key
    with open(secret_loc, "r") as f:
        key = json.load(f)["key"]

    # store exclusions
    excl = "?exclude=currently,minutely,hourly,alerts,flags"

    # instatntiate MongoDB client
    client = MongoClient()
    db = client["walk"]
    weather = db["weather"]

    # get_weather for first date - done
    # date = dates[0]
    # ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
    # dk_sky_url = 'https://api.darksky.net/forecast/'
    # get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for next 998 dates - done
    # for date in dates[1:999]:
    #     ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
    #     dk_sky_url = 'https://api.darksky.net/forecast/'
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Monday - done
    # for date in dates[999:1999]:
    #     ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
    #     dk_sky_url = 'https://api.darksky.net/forecast/'
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Tues
    for date in dates[1999:2999]:
        ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
        dk_sky_url = 'https://api.darksky.net/forecast/'
        get_weather(date, ny_lat_long[0], ny_lat_long[1],
                    dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Weds
    # for date in dates[2999:3999]:
    #     ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
    #     dk_sky_url = 'https://api.darksky.net/forecast/'
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Thurs
    # for date in dates[3999:4999]:
    #     ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
    #     dk_sky_url = 'https://api.darksky.net/forecast/'
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

    # get_weather for remaining dates - Fri
    # for date in dates[4999:len(dates)]:
    #     ny_lat_long = (40.7420, -73.9073) # atlasobscura.com
    #     dk_sky_url = 'https://api.darksky.net/forecast/'
    #     get_weather(date, ny_lat_long[0], ny_lat_long[1],
    #                 dk_sky_url, excl, key, weather)

def get_weather(date: datetime, lat, long, base_url, exclusions, 
                secret_key, collection):
    """Retrieve weather for a particular date based on exclusions passed.
    Stores weather in mongoDB collection passed
    
    Args:
        date: datetime object
        lat:
        long:
        base_url:
        exclusions:
        secret_key:
        collection:

    Returns:
        None
    """
    date_str = date.strftime('%Y-%m-%d') + 'T12:00:00'
    url = f"{base_url}{secret_key}/{lat},{long},{date_str}{exclusions}"
    response = requests.get(url)
    output = response.json()
    output['date'] = date
    collection.insert_one(output)

if __name__ == '__main__':
    main()