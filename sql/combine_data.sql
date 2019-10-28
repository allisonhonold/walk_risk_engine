/*
Object:         Materialized View
Author:         Allison Honold
Script Date:    October 28, 2019
Description:    Creates a materialized view with a combined column of lat 
                and long, the arrest_date, and the number of arrests in that
                location on that day.
*/

CREATE MATERIALIZED VIEW location_day_arrests AS
    SELECT 
        points.latitude, 
        points.longitude, 
        latlong_pts.lat_long,
        n_arrests, 
        nyc_weather.*
    FROM points
    CROSS JOIN dates
    JOIN (
            SELECT
                CONCAT(RPAD(CAST(latitude AS TEXT), 6, '0'), 
                        ' ', 
                        RPAD(CAST(longitude AS TEXT), 7, '0')) 
                        AS lat_long,
                        latitude,
                        longitude
            FROM points) AS latlong_pts
        ON points.latitude = latlong_pts.latitude
            AND points.longitude = latlong_pts.longitude
    LEFT JOIN lat_long_daily_arrest_counts
        ON latlong_pts.lat_long = lat_long_daily_arrest_counts.lat_long
            AND lat_long_daily_arrest_counts.arrest_date = dates.date
    JOIN nyc_weather
        ON nyc_weather.date = dates.date;