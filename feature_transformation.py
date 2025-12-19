import pandas as pd

def main():
    df = pd.read_csv('hourly_summary.csv')

    df['Date_Object'] = pd.to_datetime(df['Date'])

    df['Year'] = df['Date_Object'].dt.year
    df['Month'] = df['Date_Object'].dt.month
    df['Day'] = df['Date_Object'].dt.day
    df['Weekday'] = df['Date_Object'].dt.dayofweek
    df['DayOfYear'] = df['Date_Object'].dt.dayofyear

    df["Is_Weekend"] = df['Weekday'].isin([5, 6]).astype(int)

    df = df.drop(columns=['Date_Object'])

    df.to_csv("feature_engineered_data.csv", index=False)


if __name__ == "__main__":
    main()