import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import pickle

data = pd.read_csv("crop_data.csv")

X = data[['N','P','K','temperature','humidity','ph','rainfall']]
y = data['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)
rf_accuracy = accuracy_score(y_test, rf_model.predict(X_test))

gb_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
gb_model.fit(X_train, y_train)
gb_accuracy = accuracy_score(y_test, gb_model.predict(X_test))

print(f"Random Forest Accuracy: {rf_accuracy:.2f}")
print(f"Gradient Boosting Accuracy: {gb_accuracy:.2f}")

best_model = rf_model if rf_accuracy >= gb_accuracy else gb_model
pickle.dump(best_model, open("model.pkl", "wb"))

print(f"\nBest Model: {'Random Forest' if rf_accuracy >= gb_accuracy else 'Gradient Boosting'}")
print("Model Trained Successfully")