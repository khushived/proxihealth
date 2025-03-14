import pickle
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

# Load trained model
with open("model_training/disease_model.pkl", "rb") as file:
    model = pickle.load(file)

# Sample data for evaluation
data = {
    "heart_rate": [75, 120, 85],
    "step_count": [5000, 2000, 6000],
    "disease": ["Healthy", "Hypertension", "Healthy"]
}
df = pd.DataFrame(data)
df["disease"] = df["disease"].astype("category").cat.codes  

X = df[["heart_rate", "step_count"]]
y_true = df["disease"]
y_pred = model.predict(X)

print(f"✅ Model Accuracy: {accuracy_score(y_true, y_pred):.2f}")
print("\n📌 Classification Report:")
print(classification_report(y_true, y_pred))
