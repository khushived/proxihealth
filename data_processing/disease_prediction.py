import os
import psycopg2
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Define Base Directory
BASE_DIR = "D:\ProxiHealth (1)"

# Load Model & Preprocessing Tools
MODEL_PATH = os.path.join(BASE_DIR, "model_training", "model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model_training", "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "model_training", "label_encoder.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
encoder = joblib.load(ENCODER_PATH)

# Error Logging Function
def log_error(error_message):
    with open(os.path.join(BASE_DIR, "error.log"), "a") as log_file:
        log_file.write(error_message + "\n")

# Database Connection
def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="proxihealth_instance_6icz",
            user="proxihealth_instance_user",
            password="h6cZiUseYcSxlkp7FlJJnh98jS8Sz84t",
            host="dpg-cve0m6rtq21c73ea8cq0-a.singapore-postgres.render.com",
            port="5432",
            sslmode="require"
        )
    except psycopg2.Error as e:
        log_error(f"Database Connection Error: {e}")
        return None

# Fetch All User IDs
def get_all_user_ids():
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return user_ids
    except psycopg2.Error as e:
        log_error(f"Database Error (Fetching Users): {e}")
        return []

# Get Chronic Disease from Users Table
def get_chronic_disease(user_id):
    conn = get_db_connection()
    if conn is None:
        return "Unknown"

    try:
        cur = conn.cursor()
        cur.execute("SELECT chronic_disease FROM users WHERE id = %s", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result and result[0] else "Unknown"
    except psycopg2.Error as e:
        log_error(f"Database Error (Chronic Disease): {e}")
        return "Unknown"

# Get Latest Heart Rate
def fetch_heart_rate(user_id):
    conn = get_db_connection()
    if conn is None:
        return 70

    try:
        cur = conn.cursor()
        cur.execute("SELECT bpm FROM heart_rate WHERE id = %s ORDER BY timestamp DESC LIMIT 1", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else 70
    except psycopg2.Error as e:
        log_error(f"Database Error (Heart Rate): {e}")
        return 70

# Get Latest Step Count
def fetch_steps(user_id):
    conn = get_db_connection()
    if conn is None:
        return 1000

    try:
        cur = conn.cursor()
        cur.execute("SELECT step_count FROM steps WHERE id = %s ORDER BY timestamp DESC LIMIT 1", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else 1000
    except psycopg2.Error as e:
        log_error(f"Database Error (Steps): {e}")
        return 1000

# Predict Disease
def predict_disease(user_id):
    heart_rate = fetch_heart_rate(user_id)
    steps = fetch_steps(user_id)
    chronic_disease = get_chronic_disease(user_id)

    # Handle unknown chronic diseases
    if chronic_disease not in encoder.classes_:
        chronic_disease = "Unknown"

    # Encode chronic disease properly
    try:
        chronic_disease_encoded = encoder.transform([chronic_disease])[0]
    except Exception as e:
        log_error(f"Encoding Error (User {user_id}): {e}")
        chronic_disease_encoded = 0  

    # Prepare data for prediction
    input_data = pd.DataFrame([[heart_rate, steps, chronic_disease_encoded]],
                              columns=["Heart_Rate", "Steps", "Medical_Conditions"])
    input_data.fillna(0, inplace=True)

    # Display User Input Data
    print(f"\n📊 **User {user_id} Input Data**")
    print(f"   🏥 Chronic Disease: {chronic_disease} (Encoded: {chronic_disease_encoded})")
    print(f"   ❤️ Heart Rate: {heart_rate} BPM")
    print(f"   👣 Steps: {steps}")

    # Scale data
    try:
        input_data_scaled = scaler.transform(input_data)
    except Exception as e:
        log_error(f"Scaling Error (User {user_id}): {e}")
        return "Error: Scaling failed."

    # Make prediction
    try:
        prediction = model.predict(input_data_scaled)
        predicted_disease = encoder.inverse_transform(prediction)[0]
    except Exception as e:
        log_error(f"Prediction Error (User {user_id}): {e}")
        predicted_disease = "No clear disease detected. Maintain a healthy lifestyle!"

    # Display Prediction
    print(f"   🔮 Predicted Disease: {predicted_disease}")
    
    return predicted_disease

# Run Prediction for All Users
if __name__ == "__main__":
    user_ids = get_all_user_ids()
    results = {}

    if not user_ids:
        print("⚠ No users found.")
    else:
        print(f"🚀 Running predictions for {len(user_ids)} users...")
        for user_id in user_ids:
            results[user_id] = predict_disease(user_id)

        print("\n✅ All predictions completed!")
        print(results)
