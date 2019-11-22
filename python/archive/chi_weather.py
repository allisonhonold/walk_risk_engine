# load necessary modules
from weather import get_weather, get_dates_list
from datetime import datetime, timedelta, date
# import requests
import json
from pymongo import MongoClient


def main():
    # secret file location
    secret_loc = "/Users/allisonhonold/.secrets/dark_sky_api.json"

    # get most recent date from NYC's year to date arrests
    final_date = datetime.strptime('10/10/2019', '%m/%d/%Y')
    
    # set initial date to 1/1/2006
    initial_date = datetime.strptime('01/01/2001', '%m/%d/%Y')

    # get list of dates in data range
    dates = get_dates_list(initial_date, final_date)
    print(len(dates))

    # load secret key
    with open(secret_loc, "r") as f:
        key = json.load(f)["key"]

    # store exclusions
    excl = "?exclude=currently,minutely,hourly,alerts,flags"

    # instatntiate MongoDB client, set database and collection
    client = MongoClient()
    db = client["walk"]
    weather = db["chi_weather"]

    # set location and url
    chi_lat_long = (41.8781, -87.6298) # google.com
    dk_sky_url = 'https://api.darksky.net/forecast/'

    # get_weather for first date - done
    # date = dates[0]
    # get_weather(date, chi_lat_long[0], chi_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for next 998 dates - Friday
    for date in dates[1:999]:
      get_weather(date, chi_lat_long[0], chi_lat_long[1],
                dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Saturday
    # for date in dates[999:1999]:
    #   get_weather(date, chi_lat_long[0], chi_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Sunday
    # for date in dates[1999:2999]:
    #   get_weather(date, chi_lat_long[0], chi_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Monday
    # for date in dates[2999:3999]:
    #   get_weather(date, chi_lat_long[0], chi_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Tuesday
    # for date in dates[3999:4999]:
    #   get_weather(date, chi_lat_long[0], chi_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for next 1000 dates - Wednesday
    # for date in dates[4999:5999]:
    #   get_weather(date, chi_lat_long[0], chi_lat_long[1],
    #             dk_sky_url, excl, key, weather)

    # get_weather for remaining dates - Thursday
    # for date in dates[5999:len(dates)]:
    #   get_weather(date, chi_lat_long[0], chi_lat_long[1],
    #             dk_sky_url, excl, key, weather)

if __name__ == "__main__":
    main()