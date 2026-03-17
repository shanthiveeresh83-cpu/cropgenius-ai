import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None

class AdvancedCropModels:
    def __init__(self):
        self.models = {}

    def train_ensemble_models(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        candidates = []

        if XGBClassifier is not None:
            xgb_model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
            xgb_model.fit(X_train, y_train)
            xgb_acc = accuracy_score(y_test, xgb_model.predict(X_test))
            print(f"XGBoost Accuracy: {xgb_acc:.3f}")
            candidates.append((xgb_model, xgb_acc, 'XGBoost'))
        else:
            print("XGBoost not installed, skipping XGBoost model.")

        gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5)
        gb_model.fit(X_train, y_train)
        gb_acc = accuracy_score(y_test, gb_model.predict(X_test))
        candidates.append((gb_model, gb_acc, 'GradientBoosting'))

        rf_model = RandomForestClassifier(n_estimators=100, max_depth=10)
        rf_model.fit(X_train, y_train)
        rf_acc = accuracy_score(y_test, rf_model.predict(X_test))
        candidates.append((rf_model, rf_acc, 'RandomForest'))

        print(f"Gradient Boosting Accuracy: {gb_acc:.3f}")
        print(f"Random Forest Accuracy: {rf_acc:.3f}")

        best_model = max(candidates, key=lambda x: x[1])

        self.models['crop_prediction'] = best_model[0]
        print(f"\nBest Model: {best_model[2]} with accuracy {best_model[1]:.3f}")
        return best_model[0]

if __name__ == '__main__':
    data = pd.read_csv('crop_data.csv')
    X = data[['N','P','K','temperature','humidity','ph','rainfall']]
    y = data['label']

    trainer = AdvancedCropModels()
    best_model = trainer.train_ensemble_models(X, y)

    pickle.dump(best_model, open('advanced_model.pkl', 'wb'))
    print("\nAdvanced model saved!")