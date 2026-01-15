import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import math

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

latitude = input("Enter latitude(in °N): ")
for _ in range(len(latitude)):
	if "," in latitude:
		latitude = latitude.replace(",", ".")
	if "°" in latitude:
		latitude = latitude.replace("°", "")
	if " "in latitude:
		latitude = latitude.replace(" ", "")
try:
	latitude = float(latitude)
	print(f"latitude: {latitude}")
except:
	print("Latitude must be a number without any character.")
	latitude = 45
if not -90 <= latitude <= 90:
	print("Latitude must be between -90 and 90 degrees.")
	latitude = 45


longitude = input("Enter longitude(in °E): ")
for _ in range(len(longitude)):
	if "," in longitude:
		longitude = longitude.replace(",", ".")
	if "°" in longitude:
		longitude = longitude.replace("°", "")
	if " "in longitude:
		longitude = longitude.replace(" ", "")
try:
	longitude = float(longitude)
	print(f"longitude: {longitude}")
except:
	print("Longitude must be a number without any character.")
	longitude = 45
if not -180 <= longitude <= 180:
	print("Longitude must be between -180 and 180 degrees.")
	longitude = 45



sector_size = 365.242
try:
	sector_size = float(input(f"Enter sector size in days (default: {sector_size}(Just enter for default)): "))
	print(f"sector_size: {sector_size}")
except:
	sector_size = 365.242
	print(f"sector_size is set to default: {sector_size}")
if sector_size == "":
	sector_size = 365.242
	print(f"sector_size is set to default: {sector_size}")

start_date = "1940-01-01"
try:
	start_date = input(f"Enter start date (YYYY-MM-DD)(default: {start_date}): ")
	print(f"start_date: {start_date}")
except:
	start_date = "1940-01-01"
	print(f"start_date is set to default: {start_date}")
if start_date == "":
	start_date = "1940-01-01"
	print(f"start_date is set to default: {start_date}")

end_date = str(datetime.now().strftime("%Y-%m-%d"))
try:
	end_date = input(f"Enter end date (YYYY-MM-DD) (default: {end_date}): ")
	print(f"end_date: {end_date}")
except:
	end_date = str(datetime.now().strftime("%Y-%m-%d"))
	print(f"end_date is set to default: {end_date}")
if end_date == "":
	end_date = str(datetime.now().strftime("%Y-%m-%d"))
	print(f"end_date is set to default: {end_date}")


print(f"Fetching data for {latitude}°N | {longitude}°E from {start_date} to {end_date} (sector-size: {sector_size})...")



cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

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

response = responses[0]


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
sums.index = [f"{int(start_date[:4]) + i * (sector_size /365.242)}" for i in range(len(sums))]
sums.plot(kind="bar", y="snowfall_sum", title=f"Annual Snowfall Sum in {latitude}°N | {longitude}°E (1940-2025) in cm", ylabel="Snowfall Sum (cm)", xlabel="Year")

plt.show()