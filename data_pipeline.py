import pandas as pd
import os
import glob
import get_data
import train_model_A
import weather
import analysis
import feature_transformation
import train_model_B


def merge_data():
    energy_data = pd.read_csv('master_energy_history.csv')
    weather_data = pd.read_csv('weather_history.csv')

    weather_time_series = pd.to_datetime(weather_data['Time'])
    weather_hours = weather_time_series.dt.hour
    weather_dates = weather_time_series.dt.date.astype(str)

    weather_data['Hour'] = weather_hours + 1
    weather_data['Date'] = weather_dates
    weather_data = weather_data[['Date', 'Hour', 'Temperature_C', 'Wind_Speed_kmh']]

    master_df = pd.merge(energy_data, weather_data, on=['Date', 'Hour'])

    master_df.to_csv('master_energy_history_with_weather.csv', index=False)

def cleanup_files():
    patterns_to_delete = [
        'raw_data_*.xml',
        'ieso_cleaned_*.csv',
        'weather_history.csv',
    ]

    for pattern in patterns_to_delete:
        files_found = glob.glob(pattern)

        for file_path in files_found:
            try:
                os.remove(file_path)
            except OSError:
                print(f"Error deleting {file_path}")

    print("Cleanup complete!")


def main():
    get_data.aggregate_data()
    weather.main()
    merge_data()
    analysis.analyze_data()
    feature_transformation.main()
    train_model_A.main()
    train_model_B.main()
    cleanup_files()
    print("Done!")

if __name__ == "__main__":
    main()

