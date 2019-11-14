# Walk Risk Engine
This project provides the risk of walking between user-supplied start and end points in Manhattan, New York City.

## Data sources
Arrest data was downloaded from NYC Open Data's NYPD Arrests databases. This data set includes the latitude and longitude of arrests to the 0.000001 precision. Although this is an imperfect proxy for crimes and safety, considering the documented differences in policing, especially in communities of color. Unfortunately, more-precise proxies for disturbances such as 911 calls requiring police responses were not available.

Historic weather data was retrieved from darksky API for New York City over the date range provided by the NYC Arrest databases.

The recommended path is chosen via API calls to the Google Directions API.

## How it works
### Data cleaning
The arrest data was binned into latitude and longitude coordinates with a precision of 0.001 to reduce the number of lat/long pairs, while maintaining an umcertainty range of plus or minus ~150 ft.

## Attribution
[Powered by Dark Sky](https://darksky.net/poweredby/)

[NYPD Arrests Data (Historic)](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrests-Data-Historic-/8h9b-rp9u)

[NYPD Arrests Data (Year to Date)](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc)

[Google Directions API](https://developers.google.com/maps/documentation/directions/intro)