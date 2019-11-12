import pandas as pd
import numpy as np
from route import get_pts_near_path
from sqlalchemy import create_engine

def get_arrest_probas(pts_df, day_weather_df):
    """returns predicted arrest probabilities

    Args:
        pts_df: a dataframe with columns: latitude, longitude
        weather_df: a dataframe with columns:

    Returns:
        a numpy array with the resulting predictions
    """
    # setup dataframe for preprocessing
    inputs_df = setup_df_for_preprocessing(pts_df, day_weather_df)

    # preprocess data

    # get probabilities from model
        # connect to db
    engine = create_engine('postgresql:///walk')
        # query db
    ll_query = """SELECT latitude, longitude, COUNT(n_arrests) as arrest_days 
                FROM manhattan_loc_d_ar_wea GROUP BY latitude, longitude;"""
    ll_arrest_df = pd.read_sql_query(ll_query, engine)

    final_query = """SELECT date FROM manhattan_loc_d_ar_wea
                    ORDER BY date DESC LIMIT 1"""
    final_date = pd.read_sql_query(final_query, engine)

    start_query = """SELECT date FROM manhattan_loc_d_ar_wea
                    ORDER BY date ASC LIMIT 1"""
    start_date = pd.read_sql_query(start_query, engine)

    total_days = (final_date.iloc[0,0] - start_date.iloc[0,0]).days

    # set probability for each location based on the rate of days with arrests in the data set
    ll_arrest_df['probability'] = ll_arrest_df['arrest_days'] / total_days

    # create latlong column as unique identifier to join on
    inputs_df['latlong'] = (round(inputs_df['latitude'], 3).astype(str) 
                        + round(inputs_df['longitude'], 3).astype(str))
    ll_arrest_df['latlong'] = (round(ll_arrest_df['latitude'], 3).astype(str) 
                            + round(ll_arrest_df['longitude'], 3).astype(str))

    # clean lat_long_est_df for join
    ll_arrest_df = ll_arrest_df.drop(columns=['latitude', 'longitude'])

    # left join data tables on 'latlong', adding the probability of arrest
    # occuring to each latlong in pts_df
    inputs_df = inputs_df.set_index('latlong')
    ll_arrest_df = ll_arrest_df.set_index('latlong')
    output_df = inputs_df.join(ll_arrest_df)

    # convert probability column to numpy array and return
    probas = np.array(output_df['probability'])
    return probas

def get_overall_proba(path, weather):
    pts = get_pts_near_path(path, 200).reset_index(drop=True)
    arrest_probas = get_arrest_probas(pts, weather)
    return np.prod(arrest_probas)


def setup_df_for_preprocessing(pts_df, day_weather_df):
    pts_df = pts_df.drop(columns=['geometry', 'on_path'])
    for col in day_weather_df.columns:
        pts_df[col] = day_weather_df[col].values[0]
    return pts_df


def get_risk(path, weather, cutoffs=[.1, .2, .3, .4]):
    """gets the relative risk of a path.

    Args:
        path: shapely linestring of the path
        weather: pandas dataframe with columns ['date', 'ap_t_high100', 
          'ap_t_low100', 'cloud', 'humidity', 'precip_inten_max10000', 
          'precip_proba100', 'sunriseTime', 'sunsetTime',
          'wind_gust100', 'precip_accum100']
        cutoffs: (optional) division points between the five ratings

    Returns:
        tuple (number rating 1-5, rating desciption)
    """
    proba = get_overall_proba(path, weather)
    if proba < cutoffs[0]:
        return (1, 'low')
    elif proba < cutoffs[1]:
        return (2, "medium low")
    elif proba < cutoffs[2]:
        return (3, "medium")
    elif proba < cutoffs[3]:
        return (4, 'medium high')
    else:
        return (5, 'high')
    
