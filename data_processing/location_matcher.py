import psycopg2
import os
import time
import schedule
from datetime import datetime, timedelta

# ✅ PostgreSQL Connection Details
DB_CONFIG = {
    "dbname": "proxihealth_instance_6icz",
    "user": "proxihealth_instance_user",
    "password": "h6cZiUseYcSxlkp7FlJJnh98jS8Sz84t",
    "host": "dpg-cve0m6rtq21c73ea8cq0-a.singapore-postgres.render.com",
    "port": "5432",
    "sslmode": "require"
}

# ✅ Corrected Path to Disease Data File
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get script directory
DISEASE_DATA_FILE = os.path.join(SCRIPT_DIR, "..", "scraping", "kerala_disease_data.txt")

# ✅ Function to get the last 24 hours of disease data
def get_recent_disease_data():
    recent_diseases = []
    now = datetime.now()
    last_24_hours = now - timedelta(hours=24)

    try:
        with open(DISEASE_DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) < 4:
                    continue  # Skip lines with missing values
                news_timestamp, disease_city, disease, severity = parts
                try:
                    news_time = datetime.strptime(news_timestamp, "%Y-%m-%d %H:%M")
                    if news_time >= last_24_hours:
                        recent_diseases.append((news_timestamp, disease_city.lower(), disease, severity))
                except ValueError:
                    continue  # Skip invalid timestamps
    except Exception as e:
        print(f"❌ Error reading disease file: {e}")

    return recent_diseases

# ✅ Function to fetch stored IP locations from the database
def get_user_locations():
    user_locations = []
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DISTINCT city, country FROM ip_info")
                user_locations = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"❌ Database Error: {e}")

    return user_locations

# ✅ Function to match user locations with disease outbreaks
def match_diseases_with_users():
    print("\n🔍 Checking for disease alerts based on user locations...\n")
    recent_diseases = get_recent_disease_data()
    user_locations = get_user_locations()

    if not recent_diseases:
        print("⚠ No recent disease outbreaks found in the last 24 hours.")
        return
    if not user_locations:
        print("⚠ No user location data found in the database.")
        return

    matched_alerts = set()

    for user_city, user_country in user_locations:
        if user_city is None:
            continue
        user_city = user_city.lower().strip()
        user_country = user_country or "Unknown"

        for timestamp, disease_city, disease, severity in recent_diseases:
            if user_city == disease_city:
                alert_msg = (
                    f"🚨 ALERT for {user_city.title()}, {user_country.title()}\n"
                    f"🦠 Disease: {disease}\n"
                    f"📍 Location: {disease_city.title()}\n"
                    f"⚠ Severity: {severity}\n"
                    f"🕒 Reported On: {timestamp}\n"
                    "--------------------------------------"
                )
                matched_alerts.add(alert_msg)

    if matched_alerts:
        print("\n".join(matched_alerts))
    else:
        print("✅ No disease outbreaks detected in your area.")

# ✅ Schedule the function to run every 10 minutes
schedule.every(10).minutes.do(match_diseases_with_users)

# ✅ Run immediately before scheduling starts
match_diseases_with_users()

print("⏳ Waiting for next scheduled run...\n")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute