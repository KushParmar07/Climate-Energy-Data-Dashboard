import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time



def download_data(year):
    filename = f"raw_data_{year}.xml"

    url = f"http://reports.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_{year}.xml"
    print(f"Fetching {year} data from {url}")

    response = requests.get(url)

    if response.status_code == 200:
        print(f"Success! Saving to {filename}")
        with open(filename, "wb") as file:
            file.write(response.content)

        return True


    else:
        print(f"Error fetching {year}. Status: {response.status_code}")
        return False


def clean_and_save_data(year):
    input_file = f'raw_data_{year}.xml'
    output_file = f'ieso_cleaned_{year}.csv'


    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
        namespaces = {"ns": "http://www.ieso.ca/schema"}

        data_to_store = []

        for daily_data in root.findall(".//ns:DailyData", namespaces):
            day_val = daily_data.find(".//ns:Day", namespaces).text

            for hourly_data in daily_data.findall("ns:HourlyData", namespaces):
                hour_val = hourly_data.find("ns:Hour", namespaces).text

                for fuel_total in hourly_data.findall("ns:FuelTotal", namespaces):
                    fuel_type = fuel_total.find("ns:Fuel", namespaces).text

                    energy_block = fuel_total.find("ns:EnergyValue", namespaces)

                    if energy_block is not None:
                        output_tag = energy_block.find("ns:Output", namespaces)

                        if output_tag is not None:
                            fuel_value = output_tag.text
                        else:
                            fuel_value = 0
                    else:
                        fuel_value = 0

                    data_to_store.append({
                        'Date': day_val,
                        'Hour': int(hour_val),
                        'Fuel': fuel_type,
                        'MW': int(fuel_value)
                    })

        df = pd.DataFrame(data_to_store)
        df.to_csv(output_file, index=False)
        print(f"Saved {output_file}")
        return df

    except Exception as e:
        print(f"Error cleaning and saving {year} data: {e}")
        return None


def aggregate_data():
    years_to_process = [2020, 2021, 2022, 2023, 2024, 2025]

    all_years_data = []

    for year in years_to_process:
        success = download_data(year)

        if success:
            df_year = clean_and_save_data(year)

            if df_year is not None:
                all_years_data.append(df_year)

        time.sleep(1)


    if len(all_years_data) > 0:
        master_df = pd.concat(all_years_data, ignore_index = True)

        master_df.to_csv('master_energy_history.csv', index=False)
        print("All done!")
    else:
        print("No data was collected")









