import os
import psycopg2
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Define Base Directory
BASE_DIR = "C:\\Users\\HP\\Downloads\\ProxiHealth (1)"

# Load Model & Preprocessing Tools
MODEL_PATH = os.path.join(BASE_DIR, "model_training", "model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model_training", "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "model_training", "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
encoder = joblib.load(ENCODER_PATH)

# Database Connection
def get_db_connection():
    return psycopg2.connect(
        dbname="proxihealth_instance",
        user="proxihealth_instance_user",
        password="PUCCDSFTsEpV4DtLKg6bEqUMu5FxbyrH",
        host="dpg-cuujuda3esus73a9a1k0-a.singapore-postgres.render.com",
        port="5432"
    )

# Fetch All User IDs
def get_all_user_ids():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return user_ids
    except psycopg2.Error as e:
        print("❌ Database error (Fetching Users):", e)
        return []

# Get Chronic Disease from Users Table
def get_chronic_disease(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT chronic_disease FROM users WHERE id = %s", (user_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()

        return result[0] if result and result[0] else "Unknown"  # Replace None with "Unknown"
    except psycopg2.Error as e:
        print("❌ Database error:", e)
        return "Unknown"

# Get Latest Heart Rate
def fetch_heart_rate(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT bpm FROM heart_rate 
            WHERE id = %s 
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        return result[0] if result else 70  # Default to 70 BPM if no data
    except psycopg2.Error as e:
        print("❌ Database error (Heart Rate):", e)
        return 70

# Get Latest Step Count
def fetch_steps(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT step_count FROM steps 
            WHERE id = %s 
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        return result[0] if result else 1000  # Default to 1000 steps if no data
    except psycopg2.Error as e:
        print("❌ Database error (Steps):", e)
        return 1000

# Predict Disease
def predict_disease(user_id):
    heart_rate = fetch_heart_rate(user_id)
    steps = fetch_steps(user_id)
    chronic_disease = get_chronic_disease(user_id)

    print(f"\n📊 User {user_id} → Heart Rate: {heart_rate}, Steps: {steps}, Chronic Disease: {chronic_disease}")

    # Ensure chronic disease value is valid
    if chronic_disease is None or chronic_disease not in encoder.classes_:
        chronic_disease = "Unknown"  # Set a default value

    # Encode chronic disease properly
    try:
        chronic_disease_encoded = encoder.transform([chronic_disease])[0]
    except Exception:
        print(f"⚠ Warning: '{chronic_disease}' was not seen during training. Assigning default value.")
        chronic_disease_encoded = 0  # Assigning default encoded value

    # Create DataFrame with proper column names
    input_data = pd.DataFrame([[heart_rate, steps, chronic_disease_encoded]],
                              columns=["Heart_Rate", "Steps", "Medical_Conditions"])

    # Ensure no NaN values before scaling
    input_data.fillna(0, inplace=True)

    print(f"🔍 Debugging Input Data before scaling:\n{input_data}")

    # Scale the data
    try:
        input_data_scaled = scaler.transform(input_data)
    except Exception as e:
        print(f"❌ Scaling error: {e}")
        return "Error: Scaling failed."

    print(f"🔍 Debugging Scaled Data:\n{input_data_scaled}")

    # Make prediction
    try:
        prediction = model.predict(input_data_scaled)
        predicted_disease = encoder.inverse_transform(prediction)[0]  # Convert back to disease name
    except Exception:
        predicted_disease = "No clear disease detected. Maintain a healthy lifestyle!"

    # Display Final Output
    print(f"🩺 Prediction for User {user_id}: {predicted_disease}")
    return predicted_disease

# Run Prediction for All Users
if __name__ == "__main__":
    user_ids = get_all_user_ids()

    if not user_ids:
        print("⚠ No users found in the database.")
    else:
        print(f"🚀 Running predictions for {len(user_ids)} users...\n")
        results = {}
        for user_id in user_ids:
            results[user_id] = predict_disease(user_id)

        print("\n✅ All predictions completed!")
        print(results)  # Dictionary of user_id → predicted disease
