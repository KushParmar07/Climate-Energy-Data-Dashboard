import pandas as pd

def analyze_data():
    df = pd.read_csv('master_energy_history_with_weather.csv')

    emission_factors = {
        'NUCLEAR': 0,
        'HYDRO': 0,
        'WIND': 0,
        'SOLAR': 0,
        'GAS': 490,
        'BIOFUEL': 30
    }

    df['Factor'] = df['Fuel'].map(emission_factors).fillna(0)
    df['Total_Emissions'] = df['Factor'] * df['MW']

    hourly_stats = df.groupby(['Date', 'Hour', 'Temperature_C', 'Wind_Speed_kmh'])[['MW', 'Total_Emissions']].sum().reset_index()
    hourly_stats['Carbon_Intensity_g_kWh'] = hourly_stats['Total_Emissions'] / hourly_stats['MW']

    hourly_stats.to_csv(f'hourly_summary.csv', index=False)


