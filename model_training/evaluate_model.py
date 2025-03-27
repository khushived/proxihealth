import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ✅ Load trained model & scaler
model = joblib.load("D:/ProxiHealth (1)/model_training/model.pkl")
scaler = joblib.load("D:/ProxiHealth (1)/model_training/scaler.pkl")
label_encoder = joblib.load("D:/ProxiHealth (1)/model_training/label_encoder.pkl")

print("Trained Disease Labels:", label_encoder.classes_)

# ✅ Sample Data for Evaluation
data = {
    "Heart_Rate": [120, 85, 90, 130],
    "Steps": [2000, 6000, 4000, 1500],
    "Altitude": [50, 120, 80, 200],
    "Exercise_Duration": [30, 45, 20, 50],
    "Medical_Conditions": ["Hypertension", "Diabetes", "Hypertension", "Diabetes"]
}

df = pd.DataFrame(data)
df["Medical_Conditions"] = label_encoder.transform(df["Medical_Conditions"])

# ✅ Extract Features & Normalize
X = df[["Heart_Rate", "Steps", "Altitude", "Exercise_Duration"]]
X_scaled = scaler.transform(X)

# ✅ Predict
y_true = df["Medical_Conditions"]
y_pred = model.predict(X_scaled)

# ✅ Model Performance Metrics
print(f"✅ Model Accuracy: {accuracy_score(y_true, y_pred):.2f}")
print("\n📌 Classification Report:")
print(classification_report(y_true, y_pred))

# 🔹 Confusion Matrix Visualization
conf_matrix = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="coolwarm",
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()
