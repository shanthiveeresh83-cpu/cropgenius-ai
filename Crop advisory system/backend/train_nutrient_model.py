import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

DATA_PATH = "crop_data.csv"
MODEL_PATH = "nutrient_model.pkl"

def train_nutrient_model():

    print("=" * 60)
    print("Nutrient Estimation Model Training")
    print("=" * 60)

    if not os.path.exists(DATA_PATH):
        print(f"Error: Training data not found at {DATA_PATH}")
        return False

    print(f"\nLoading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} samples")
    print(f"Features: {list(df.columns)}")

    feature_cols = ['K', 'temperature', 'humidity', 'ph', 'rainfall']

    X = df[feature_cols].values
    y_n = df['N'].values
    y_p = df['P'].values

    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Target variables: N (range: {y_n.min():.1f} - {y_n.max():.1f})")
    print(f"                 P (range: {y_p.min():.1f} - {y_p.max():.1f})")

    X_train, X_test, y_n_train, y_n_test = train_test_split(
        X, y_n, test_size=0.2, random_state=42
    )
    _, _, y_p_train, y_p_test = train_test_split(
        X, y_p, test_size=0.2, random_state=42
    )

    print("\n" + "=" * 60)
    print("Training Nitrogen (N) Model")
    print("=" * 60)

    n_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    n_model.fit(X_train, y_n_train)

    n_pred = n_model.predict(X_test)
    n_rmse = np.sqrt(mean_squared_error(y_n_test, n_pred))
    n_r2 = r2_score(y_n_test, n_pred)

    print(f"N Model Performance:")
    print(f"  - RMSE: {n_rmse:.4f}")
    print(f"  - R² Score: {n_r2:.4f}")

    print(f"\nFeature Importance (N):")
    for feat, imp in sorted(zip(feature_cols, n_model.feature_importances_), 
                           key=lambda x: x[1], reverse=True):
        print(f"  - {feat}: {imp:.4f}")

    print("\n" + "=" * 60)
    print("Training Phosphorus (P) Model")
    print("=" * 60)

    p_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    p_model.fit(X_train, y_p_train)

    p_pred = p_model.predict(X_test)
    p_rmse = np.sqrt(mean_squared_error(y_p_test, p_pred))
    p_r2 = r2_score(y_p_test, p_pred)

    print(f"P Model Performance:")
    print(f"  - RMSE: {p_rmse:.4f}")
    print(f"  - R² Score: {p_r2:.4f}")

    print(f"\nFeature Importance (P):")
    for feat, imp in sorted(zip(feature_cols, p_model.feature_importances_), 
                           key=lambda x: x[1], reverse=True):
        print(f"  - {feat}: {imp:.4f}")

    model = {
        'n_model': n_model,
        'p_model': p_model,
        'feature_cols': feature_cols
    }

    print("\n" + "=" * 60)
    print("Saving Model")
    print("=" * 60)

    try:
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to: {MODEL_PATH}")
    except Exception as e:
        print(f"Error saving model: {str(e)}")
        return False

    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = train_nutrient_model()
    if success:
        print("\nNutrient model is ready for use!")
    else:
        print("\nTraining failed. Please check the errors above.")