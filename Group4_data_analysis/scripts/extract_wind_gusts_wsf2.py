#This script extracts the fastest 2-minute sustained wind speeds for Miami 
# from 2015 to 2023 using the NOAA API. It loops year by year, handles retries, 
# and saves the data into a CSV for further analysis (e.g. detection of extreme gust events).

import requests
import pandas as pd
import os
import time

API_TOKEN = "gAeZlUchXkUzxowblhWeDzERXSYcXmdw"
headers = {"token": API_TOKEN}
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

# Dataset: GHCND (daily), datatype: WSF2 (gust)
base_params = {
    "datasetid": "GHCND",
    "stationid": "GHCND:USW00093193",  # Miami
    "datatypeid": "WSF2",              # Gust 2-minute
    "units": "metric",
    "limit": 1000
}

def fetch_wind_gusts(start_year=2015, end_year=2023):
    all_data = []

    for year in range(start_year, end_year + 1):
        print(f"📅 Year: {year}")
        params = base_params.copy()
        params["startdate"] = f"{year}-01-01"
        params["enddate"] = f"{year}-12-31"

        for attempt in range(3):
            try:
                response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        all_data.extend(results)
                        print(f"✅ {len(results)} gust entries added for {year}")
                    else:
                        print("⚠️ No gust data found.")
                    break
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"⚠️ Retry error: {e}")
                time.sleep(1)

        time.sleep(0.2)

    return pd.DataFrame(all_data)

def save_to_csv(df, filename):
    output_path = os.path.join("Group4_data_analysis", "data", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"📁 Wind gust data saved to: {output_path}")

if __name__ == "__main__":
    df_gusts = fetch_wind_gusts()
    save_to_csv(df_gusts, "noaa_wind_gusts_miami.csv")

