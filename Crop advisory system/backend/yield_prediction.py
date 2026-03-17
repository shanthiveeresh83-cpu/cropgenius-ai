import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle

try:
    from xgboost import XGBRegressor
except Exception:
    XGBRegressor = None

class YieldPredictionModel:
    def __init__(self):
        self.model = None

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if XGBRegressor is not None:
            self.model = XGBRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05
            )
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        print(f"Yield Prediction RMSE: {rmse:.3f}")
        print(f"R² Score: {r2:.3f}")

        return self.model

    def predict_yield(self, features):
        return self.model.predict([features])[0]

if __name__ == '__main__':

    data = pd.DataFrame({
        'N': [90, 85, 60, 74, 78],
        'P': [42, 58, 55, 35, 42],
        'K': [43, 41, 44, 40, 42],
        'temperature': [20.87, 21.77, 23.00, 26.49, 20.13],
        'humidity': [82.00, 80.31, 82.32, 80.15, 81.60],
        'ph': [6.50, 7.03, 7.84, 6.98, 7.63],
        'rainfall': [202.93, 226.65, 263.96, 242.86, 262.72],
        'yield': [4.5, 5.2, 4.8, 3.9, 5.0]  # tons/hectare
    })

    X = data.drop('yield', axis=1)
    y = data['yield']

    yield_model = YieldPredictionModel()
    yield_model.train(X, y)

    pickle.dump(yield_model, open('yield_model.pkl', 'wb'))
    print("\nYield prediction model saved!")