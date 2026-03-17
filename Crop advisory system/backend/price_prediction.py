import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import pickle

class CropPricePrediction:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()

    def create_sequences(self, data, seq_length=30):
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:i+seq_length])
            y.append(data[i+seq_length])
        return np.array(X), np.array(y)

    def train_price_model(self, price_history):
        scaled_data = self.scaler.fit_transform(price_history.reshape(-1, 1))
        X, y = self.create_sequences(scaled_data.flatten())
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10)
        self.model.fit(X, y)
        return self.model

    def predict_future_prices(self, recent_prices, days=7):
        predictions = []
        current_sequence = recent_prices[-30:].copy()

        for _ in range(days):
            scaled_seq = self.scaler.transform(current_sequence.reshape(-1, 1)).flatten()
            next_price_scaled = self.model.predict([scaled_seq])[0]
            next_price = self.scaler.inverse_transform([[next_price_scaled]])[0][0]
            predictions.append(next_price)
            current_sequence = np.append(current_sequence[1:], next_price)

        return predictions

    def analyze_price_trend(self, prices):
        if prices is None or len(prices) == 0:
            return {
                'trend': 'Unknown',
                'change_percentage': 0,
                'current_price': 0,
                'predicted_avg': 0,
                'recommendation': 'Insufficient data for analysis'
            }

        if len(prices) < 2:
            return {
                'trend': 'Stable',
                'change_percentage': 0,
                'current_price': round(float(prices[0]), 2) if len(prices) > 0 else 2000,
                'predicted_avg': round(float(prices[0]), 2) if len(prices) > 0 else 2000,
                'recommendation': 'Insufficient data for trend analysis'
            }

        recent_avg = np.mean(prices[-7:])
        previous_avg = np.mean(prices[-14:-7]) if len(prices) >= 14 else np.mean(prices[:-7])
        change_pct = ((recent_avg - previous_avg) / previous_avg) * 100 if previous_avg != 0 else 0

        if change_pct > 5:
            trend = 'Rising'
            recommendation = 'Good time to sell'
        elif change_pct < -5:
            trend = 'Falling'
            recommendation = 'Consider holding or buying'
        else:
            trend = 'Stable'
            recommendation = 'Market is stable'

        return {
            'trend': trend,
            'change_percentage': round(change_pct, 2),
            'current_price': round(float(prices[-1]), 2),
            'predicted_avg': round(float(recent_avg), 2),
            'recommendation': recommendation
        }

if __name__ == '__main__':
    rice_prices = np.array([
        2000, 2050, 2100, 2080, 2120, 2150, 2180, 2200,
        2220, 2250, 2280, 2300, 2320, 2350, 2380, 2400,
        2420, 2450, 2480, 2500, 2520, 2550, 2580, 2600,
        2620, 2650, 2680, 2700, 2720, 2750, 2780, 2800,
        2820, 2850, 2880, 2900, 2920, 2950, 2980, 3000
    ])

    price_predictor = CropPricePrediction()
    price_predictor.train_price_model(rice_prices)
    future_prices = price_predictor.predict_future_prices(rice_prices, days=7)

    print("Predicted prices for next 7 days:")
    for i, price in enumerate(future_prices, 1):
        print(f"Day {i}: ₹{price:.2f}/quintal")

    trend_analysis = price_predictor.analyze_price_trend(rice_prices)
    print(f"\nTrend: {trend_analysis['trend']}")
    print(f"Change: {trend_analysis['change_percentage']}%")
    print(f"Recommendation: {trend_analysis['recommendation']}")

    pickle.dump(price_predictor, open('price_model.pkl', 'wb'))