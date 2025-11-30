import requests
import pandas as pd
from datetime import datetime


def main():
    today = datetime.now().strftime("%Y-%m-%d")

    response = requests.get(
        f"https://archive-api.open-meteo.com/v1/archive?latitude=43.7064&longitude=-79.3986&start_date=2020-01-01&end_date={today}&hourly=temperature_2m,wind_speed_10m&timezone=America%2FNew_York")

    if response.status_code == 200:
        data = response.json()

        hourly_data = data['hourly']

        df = pd.DataFrame({
            'Time': hourly_data['time'],
            'Temperature_C': hourly_data['temperature_2m'],
            'Wind_Speed_kmh': hourly_data['wind_speed_10m']
        })

        output_filename = 'weather_history.csv'

        df.to_csv(output_filename, index=False)
        print(f"Weather data saved to {output_filename}")
        print(df.tail())

    else:
        print(f"Error fetching weather data. Status code: {response.status_code}")


