# import necessary packages
import json
import requests
import pandas as pd
import polyline
import geopandas as gpd
from shapely.geometry import LineString, Point
import numpy as np
from itertools import product
from haversine import haversine, Unit
from shapely.ops import nearest_points

def main():
    pass


def query_route_api(secret_loc, start_loc, end_loc):
    """queries the google maps api for walking route information

    Args:
        secret_loc: path to location of google api key
        start_loc: "lat,long" string of desired starting location for route
        end_loc: "lat,long" string of desired ending location for route

    Returns:
        response: google directions walking response
    """
    base_url = 'https://maps.googleapis.com/maps/api/directions/json?mode=walking'
    with open(secret_loc, "r") as f:
        key = json.load(f)['key']
    url = f"{base_url}&origin={start_loc}&destination={end_loc}&key={key}"
    response = requests.get(url)
    print(response.status_code, response.reason)
    return response


def extract_route_and_warnings(response_json):
    """extracts route and warnings from google directions API response
    
    args:
        response_json: the json of the google directions API response
    
    returns:
        rte: route as a geopandas dataframe with columns: longitude, latitude, geometry 
        warn: warnings for display
    """
    if "error_message" in response_json.keys():
        print(response_json['error_message'])
        return 'error', 'error'
    else:
        goog_polyline = response_json['routes'][0]['overview_polyline']['points']
        warnings = []
        if len(response_json['routes'][0]['warnings']) > 0:
            warnings.extend(response_json['routes'][0]['warnings'])
        rte = pd.DataFrame(polyline.decode(goog_polyline, geojson=True), columns=['longitude', 'latitude'])
        rte = gpd.GeoDataFrame(rte, geometry=gpd.points_from_xy(rte['longitude'], rte['latitude']))
        rte = LineString([[p.x, p.y] for p in rte['geometry']])
        return rte, warnings


def get_route(secret_loc, start_loc, end_loc):
    """Calls to Google Service API to return the recommended route.
    
    Args:
        secret_loc: location of file with api key
        start_loc: starting location of the desired walk 
            (lat,long stringw/out spaces)
        end_loc: ending location of the desired walk 
            (lat,long string w/out spaces)
        
    Returns:
        route: shapely line of the recommended path
        warnings: route-related warnings for display
    """
    response = query_route_api(secret_loc, start_loc, end_loc)
    resp_json = json.loads(response.text)
    route, warnings = extract_route_and_warnings(resp_json)
    return route, warnings
    
    
def get_pts_near_path(line, distance):
    """returns all lat/longs within specified distance of line
    
    Args:
        line: shapely linestring of route
        distance: maximum distance from path for returned points

    Returns:
        geopandas dataframe of all points within distance from line
    """
    # get line bounds
    (minx, miny, maxx, maxy) = line.bounds
    
    # extract values with buffer area
    minx = round(minx, 3) -0.002
    miny = round(miny, 3) -0.002
    maxx = round(maxx, 3) + 0.002
    maxy = round(maxy, 3) + 0.002
    
    # create a df of all lat, longs w/in bounds
    all_pts = create_pt_grid(minx, miny, maxx, maxy)
    
    all_pts['on_path'] = on_path(all_pts['geometry'], distance, line)
    return all_pts.loc[all_pts['on_path']==True]


def create_pt_grid(minx, miny, maxx, maxy):
    """creates a grid of points (lat/longs) in the range specified. lat longs 
    are rounded to hundredth place

    Args:
        minx: minimum longitude
        miny: minimum latitude
        maxx: maximum longitude
        maxy: maximum latitude

    Returns: geoDataFrame of all lat/long combinations in region
    """
    n_lats = round((maxy-miny)/.001) +1
    lats = np.linspace(miny, maxy, n_lats)
    n_longs = round((maxx - minx)/.001) +1
    longs = np.linspace(minx, maxx, n_longs)
    lat_long_df = pd.DataFrame(product(lats, longs), columns=['latitude', 'longitude'])
    geo_df = gpd.GeoDataFrame(lat_long_df,
                         geometry=gpd.points_from_xy(lat_long_df['longitude'], lat_long_df['latitude']))
    return geo_df


def on_path(geom_series, dist, line):
    on_path = []
    for index in geom_series.index:
        x = geom_series[index].x
        y = geom_series[index].y
        pt1, ln_pt = nearest_points(Point(x, y), line)
        on_path.append(haversine((pt1.y, pt1.x), (ln_pt.y, ln_pt.x), unit='ft') < dist)
    return on_path


# maybe break this out into mapping.py
def get_geojson_grid(upper_right, lower_left, n=6):
    """Returns a grid of geojson rectangles, and computes the exposure in each 
    section of the grid based on the vessel data.

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids" (the default is the 
        upper right hand [lat, lon] of the USA).

    lower_left: array_like
        The lower left hand corner of "grid of grids"  (the default is the 
        lower left hand [lat, lon] of the USA).

    n: integer
        The number of rows/columns in the (n,n) grid.

    Returns
    -------

    list
        List of "geojson style" dictionary objects   
    """

    all_boxes = []

    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for lat in lat_steps[:-1]:
        for lon in lon_steps[:-1]:
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]

            geo_json = {"type": "FeatureCollection",
                        "properties":{
                            "lower_left": lower_left,
                            "upper_right": upper_right
                        },
                        "features":[]}

            grid_feature = {
                "type":"Feature",
                "geometry":{
                    "type":"Polygon",
                    "coordinates": [coordinates],
                }
            }

            geo_json["features"].append(grid_feature)

            all_boxes.append(geo_json)

    return all_boxes

if __name__ == "__main__":
    main()