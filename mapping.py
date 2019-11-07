import folium
import matplotlib as mpl
import pandas as pd
from matplotlib import pyplot


def map_predictions(start_lat, start_long, end_lat, end_long, pts_proba_df):
    m = get_basemap(start_lat, start_long, end_lat, end_long)
    geojson_grid = get_geojson_grid(pts_proba_df)
    m = add_grid_to_map(geojson_grid, m)
    return m


def get_basemap(start_lat, start_long, end_lat, end_long):
    folium_map = folium.Map(location=[str((float(start_lat)+float(end_lat))/2), 
                               str((float(start_long)+float(end_long))/2)], 
                     zoom_start=15, tiles='Stamen Terrain')
    folium.Marker(location=[start_lat, start_long], 
                  icon=folium.Icon(color='green', prefix='fa', icon='fas fa-circle')
                 ).add_to(folium_map)
    folium.Marker(location=[end_lat, end_long], 
              icon=folium.Icon(color='red', prefix='fa', icon='fas fa-circle')
              ).add_to(folium_map)
    return folium_map


def get_geojson_grid(df, proba_column='probability'):
    all_boxes = []

    for index in df.index:
        lat = df.loc[index, 'latitude']
        long = df.loc[index, 'longitude']
        proba = df.loc[index, proba_column]

        # Define json coordinates for polygon
        coordinates = [
            [long - .0005, lat - .0005],
            [long - .0005, lat + .0005],
            [long + .0005, lat + .0005],
            [long + .0005, lat - .0005],
            [long - .0005, lat - .0005]
        ]

        geo_json = {"type": "FeatureCollection",
                    "properties":{
                        "lat": lat,
                        "long": long,
                        "proba": proba
                    },
                    "features": []
                   }

        grid_feature = {
            "type": "Feature",
            "geometry":{
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }

        geo_json['features'].append(grid_feature)
        all_boxes.append(geo_json)
    return all_boxes


def add_grid_to_map(grid, m):
    for geo_json in grid:
        color = pyplot.cm.Reds(geo_json['properties']['proba'])
        color = mpl.colors.to_hex(color)
        gj = folium.GeoJson(geo_json,
                            style_function=lambda feature, color=color: {
                                                            'fillColor': color,
                                                            'color': color,
                                                            'weight': 0,
                                                            #'dashArray': '5, 5',
                                                            'fillOpacity': 0.5,
                            }
                        )
        m.add_child(gj)
    return m