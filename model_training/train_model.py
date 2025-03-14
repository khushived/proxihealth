import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score

# ✅ Load dataset
csv_file = "C:/Users/HP/Downloads/ProxiHealth (1)/disease_data.csv"
data = pd.read_csv(csv_file)

# ✅ Print column names for debugging
print("CSV Columns:", list(data.columns))

# ✅ Define Features (X) and Target (y)
FEATURES = ["Heart_Rate", "Steps", "Medical_Conditions"]  # Updated Features
TARGET = "Medical_Conditions"  # Update if needed

# ✅ Ensure all required columns exist
missing_features = [col for col in FEATURES if col not in data.columns]
if missing_features:
    raise ValueError(f"Missing columns in dataset: {missing_features}")

if TARGET not in data.columns:
    raise ValueError(f"Target column '{TARGET}' not found in dataset")

# ✅ Convert `Medical_Conditions` (Categorical) to Numerical
label_encoder = LabelEncoder()
data["Medical_Conditions"] = label_encoder.fit_transform(data["Medical_Conditions"].astype(str))

# ✅ Select Features & Target
X = data[FEATURES]
y = data[TARGET]

# ✅ Normalize Features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ✅ Split Data (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# ✅ Train the Model
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# ✅ Evaluate Model Performance
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Trained with Accuracy: {accuracy * 100:.2f}%")

# ✅ Save Model, Scaler & Encoder
joblib.dump(model, "C:/Users/HP/Downloads/ProxiHealth (1)/model_training/model.pkl")
joblib.dump(scaler, "C:/Users/HP/Downloads/ProxiHealth (1)/model_training/scaler.pkl")
joblib.dump(label_encoder, "C:/Users/HP/Downloads/ProxiHealth (1)/model_training/label_encoder.pkl")

print("✅ Model, Scaler, and Encoder Saved Successfully!")
