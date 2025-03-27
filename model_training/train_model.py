import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import SMOTE  # Fix class imbalance

# ✅ Load dataset
csv_file = "D:/ProxiHealth (1)/disease_data.csv"
data = pd.read_csv(csv_file)

# ✅ Drop Missing Values & Unnecessary Columns
data = data.dropna(subset=["Medical_Conditions"])
FEATURES = ["Heart_Rate", "Steps", "Altitude", "Exercise_Duration"]  # More features
TARGET = "Medical_Conditions"

# ✅ Encode Disease Labels
label_encoder = LabelEncoder()
data[TARGET] = label_encoder.fit_transform(data[TARGET].astype(str))
joblib.dump(label_encoder, "D:/ProxiHealth (1)/model_training/label_encoder.pkl")

# ✅ Select Features & Target
X = data[FEATURES]
y = data[TARGET]

# ✅ Normalize Features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, "D:/ProxiHealth (1)/model_training/scaler.pkl")

# ✅ Fix Class Imbalance (Oversample Minority Classes)
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

# ✅ Split Data
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# ✅ Tune Model Using GridSearchCV
param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [10, 20, None],
    "min_samples_split": [2, 5, 10]
}

grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5, scoring="accuracy", n_jobs=-1)
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_

# ✅ Evaluate Model
y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Improved Model Accuracy: {accuracy * 100:.2f}%")
print("\n📌 Classification Report:")
print(classification_report(y_test, y_pred))

# ✅ Save Optimized Model
joblib.dump(best_model, "D:/ProxiHealth (1)/model_training/model.pkl")
print("✅ Optimized Model Saved Successfully!")
