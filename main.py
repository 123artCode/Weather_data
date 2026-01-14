import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import matplotlib.pyplot as plt
import numpy as np
import datetime


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

latitude = int(input("Enter latitude(°N): "))
longitude = int(input("Enter longitude(°E): "))
sector_size = int(input("Enter sector size (days): "))
start_date = "1940-01-01"
start_date = input(f"Enter start date (YYYY-MM-DD) [{start_date}]: ") or start_date
end_date = str(datetime.now().strftime("%Y-%m-%d"))
end_date = input(f"Enter end date (YYYY-MM-DD) [{end_date}]: ") or end_date



# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": latitude,
	"longitude": longitude,
	"start_date": start_date,
    "end_date": end_date,
	"timezone": "UTC",
	"daily": "snowfall_sum",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
# print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation: {response.Elevation()} m asl")
# print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_snowfall_sum = daily.Variables(0).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["snowfall_sum"] = daily_snowfall_sum

daily_dataframe = pd.DataFrame(data = daily_data)

sums = (
    daily_dataframe
    .reset_index(drop=True)
	.groupby(lambda i: i // sector_size)
    .sum(numeric_only=True)
)
sums.index = [f"{1940 + i}" for i in range(len(sums))]
# print(sums.to_string())
sums.plot(kind="bar", y="snowfall_sum", title=f"Annual Snowfall Sum in {latitude}°N | {longitude}°E (1940-2025) in cm", ylabel="Snowfall Sum (mm)", xlabel="Year")
sums = sums.to_numpy()

plt.show()