/*
Object:         Materialized View
Author:         Allison Honold
Script Date:    October 21, 2019
Description:    Creates a materialized view with a combined column of lat 
                and long, the arrest_date, and the number of arrests in that
                location on that day.
*/

CREATE MATERIALIZED VIEW lat_long_daily_arrest_counts AS
    SELECT 
            lat_long,
            arrest_date,
            COUNT(arrests.arrest_key) as n_arrests
    FROM 
        (SELECT
            CONCAT(SUBSTRING(CAST(latitude AS TEXT) FROM 1 FOR 6), 
                    ' ', 
                    SUBSTRING(CAST(longitude AS TEXT) FROM 1 FOR 7)) 
                    AS lat_long,
            arrest_key
        FROM arrests) AS latlong
    JOIN arrests
        ON arrests.arrest_key = latlong.arrest_key
    GROUP BY arrest_date, lat_long
    ORDER BY lat_long;