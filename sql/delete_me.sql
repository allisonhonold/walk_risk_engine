/*
Object:         Materialized View
Author:         Allison Honold
Script Date:    October 19, 2019
Description:    
*/

-- CREATE MATERIALIZED VIEW lat_long_day_arrests AS
    SELECT 
        lat_long,
        arrest_date,
        SUM(n_arrests) as num
    FROM (
        SELECT 
            CONCAT(latitude, ' ', longitude) AS lat_long,
            arrest_date,
            COUNT(ARREST_KEY) as n_arrests
        FROM arrests
        WHERE arrest_date = '2017-12-31 00:00:00' 
        GROUP BY lat_long, arrest_date
        ORDER BY arrest_date
        ) AS count
    WHERE lat_long = '40.595175415 -73.758906568'
    GROUP BY arrest_Date, lat_long
    ORDER BY lat_long
    LIMIT 10;