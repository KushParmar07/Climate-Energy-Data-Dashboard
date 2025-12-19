import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from matplotlib import pyplot as plt


def main():
    df = pd.read_csv('feature_engineered_data.csv')

    train_df = df[df['Year'] < 2025]
    test_df = df[df['Year'] == 2025]

    features = ['Temperature_C', 'Month', 'Hour', 'Is_Weekend', 'Weekday', 'Year', 'DayOfYear']
    target = 'MW'

    X_train = train_df[features]
    y_train = train_df[target]

    X_test = test_df[features]
    y_test = test_df[target]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"MAE: {mae}")


    plt.figure(figsize=(12, 8))
    plt.plot(y_test.values[:200], label="Actual Demand", color='blue')
    plt.plot(predictions[:200], label="Predicted Demand", color='red', linestyle='--')
    plt.title('Reality vs AI Prediction (First 200 Hours of 2024)')
    plt.legend()
    plt.show()

    joblib.dump(model, 'model_A.pkl')
    print("Model saved!")


if __name__ == "__main__":
    main()
