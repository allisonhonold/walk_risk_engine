/*
Object:         Materialized View
Author:         Allison Honold
Script Date:    October 30, 2019
Description:    Creates a materialized view with a combined column of lat 
                and long, the arrest_date, and the number of arrests in that
                location on that day for Manhattan for dates more recent than
                2017-01-01.
*/

CREATE MATERIALIZED VIEW manhattan_loc_d_ar_wea AS
    SELECT 
        CAST(manhattan_points.latitude AS REAL), 
        CAST(manhattan_points.longitude AS REAL), 
        CAST(dates.date AS DATE),
        CAST(n_arrests AS SMALLINT), 
        CAST("apparentTemperatureHigh"*100 AS SMALLINT) as ap_t_high100,
        CAST("apparentTemperatureLow"*100 AS SMALLINT) as ap_t_low100,
        CAST("cloudCover"*100 AS SMALLINT) as cloud,
        CAST(humidity*100 AS SMALLINT) as humidity,
        -- icon,
        -- CAST("moonPhase"*100 AS SMALLINT) as moon_phase,
        CAST("precipIntensityMax"*10000 AS SMALLINT) as precip_inten_max10000,
        CAST("precipProbability"*100 AS SMALLINT) as precip_proba100,
        -- "precipType",
        -- CAST(pressure AS SMALLINT) as pressure,
        CAST("sunriseTime" AS INTEGER),
        CAST("sunsetTime" AS INTEGER),
        -- CAST("uvIndex" AS SMALLINT),
        CAST("windGust"*100 AS SMALLINT) as wind_gust100,
        CAST("precipAccumulation"*100 AS SMALLINT) as precip_accum100
        -- , CAST(ozone*10 AS SMALLINT) as ozone10
    FROM manhattan_points
    CROSS JOIN dates
    JOIN (
            SELECT
                CONCAT(RPAD(CAST(latitude AS TEXT), 6, '0'), 
                        ' ', 
                        RPAD(CAST(longitude AS TEXT), 7, '0')) 
                        AS lat_long,
                        latitude,
                        longitude
            FROM manhattan_points) AS latlong_pts
        ON manhattan_points.latitude = latlong_pts.latitude
            AND manhattan_points.longitude = latlong_pts.longitude
    LEFT JOIN lat_long_daily_arrest_counts
        ON latlong_pts.lat_long = lat_long_daily_arrest_counts.lat_long
            AND lat_long_daily_arrest_counts.arrest_date = dates.date
    JOIN nyc_weather
        ON nyc_weather.date = dates.date
    WHERE dates.date > CAST('2018-01-01' AS DATE);