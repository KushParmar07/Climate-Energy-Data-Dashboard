from sklearn.ensemble import RandomForestRegressor
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.multioutput import MultiOutputRegressor


def format_data():
    df = pd.read_csv("master_energy_history_with_weather.csv")

    df['Timestamp'] = pd.to_datetime(df['Date']) + pd.to_timedelta(df['Hour'], unit='h')

    pivot_df = df.pivot_table(index='Timestamp', columns='Fuel', values='MW', aggfunc='sum').reset_index()

    weather_df = df.groupby('Timestamp')[['Wind_Speed_kmh']].mean().reset_index()

    master_df = pd.merge(pivot_df, weather_df, on='Timestamp')

    fuel_types = ['NUCLEAR', 'HYDRO', 'WIND', 'SOLAR', 'GAS', 'BIOFUEL']
    master_df['Total_Demand'] = master_df[fuel_types].sum(axis=1)

    master_df.fillna(0)

    return master_df


def create_model(df):

    train_data = df[df['Timestamp'].dt.year < 2025]
    test_data = df[df['Timestamp'].dt.year == 2025]

    features = ['Wind_Speed_kmh', 'Total_Demand']
    targets = ['NUCLEAR', 'HYDRO', 'WIND', 'SOLAR', 'GAS', 'BIOFUEL']

    X_train = train_data[features]
    y_train = train_data[targets]

    X_test = test_data[features]
    y_test = test_data[targets]

    model = RandomForestRegressor(n_estimators=50, max_depth=15, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"MAE: {mae}")

    joblib.dump(model, 'model_B.pkl', compress=3)
    print("Model saved!")


def main():
    df = format_data()
    create_model(df)

if __name__ == "__main__":
    main()