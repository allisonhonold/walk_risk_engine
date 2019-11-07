import pandas as pd
import numpy as np
from route import get_pts_near_path

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
    inputs_df['probability'] = 0.018
    probas = np.array(inputs_df['probability'])
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
    
