import psycopg2
import time
import os
from datetime import datetime, timedelta

# ✅ PostgreSQL Connection Details
DB_CONFIG = {
    "dbname": "proxihealth_instance",
    "user": "proxihealth_instance_user",
    "password": "PUCCDSFTsEpV4DtLKg6bEqUMu5FxbyrH",
    "host": "dpg-cuujuda3esus73a9a1k0-a.singapore-postgres.render.com",
    "port": "5432"
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

                # ✅ Ensure it has at least 4 values (excluding the link)
                if len(parts) < 4:
                    print(f"⚠ Skipping line due to missing values: {line.strip()}")
                    continue  

                news_timestamp, disease_city, disease, severity = parts  # Removed link

                # ✅ Ensure timestamp is valid before adding
                try:
                    news_time = datetime.strptime(news_timestamp, "%Y-%m-%d %H:%M")
                    if news_time >= last_24_hours:
                        recent_diseases.append((news_timestamp, disease_city.lower(), disease, severity))
                except ValueError:
                    print(f"❌ Invalid timestamp format: {news_timestamp}")

    except Exception as e:
        print(f"❌ Error reading disease file: {e}")

    return recent_diseases

# ✅ Function to fetch stored IP locations from the database
def get_user_locations():
    user_locations = []
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cursor:
                query = "SELECT DISTINCT city, country FROM ip_info"  # ✅ Use DISTINCT to remove duplicates
                cursor.execute(query)
                user_locations = cursor.fetchall()  # List of (city, country)
    except psycopg2.Error as e:
        print(f"❌ Database Error: {e}")

    return user_locations

# ✅ Function to match user locations with disease outbreaks (Fixing Duplicate Alerts)
def match_diseases_with_users():
    print("\n🔍 Checking for disease alerts based on user locations...\n")

    # Fetch data
    recent_diseases = get_recent_disease_data()
    user_locations = get_user_locations()

    if not recent_diseases:
        print("⚠ No recent disease outbreaks found in the last 24 hours.")
        return

    if not user_locations:
        print("⚠ No user location data found in the database.")
        return

    matched_alerts = set()  # ✅ Use a set to store unique alerts

    for user_city, user_country in user_locations:
        user_city = user_city.lower().strip()  # Ensure lowercase and no trailing spaces
        for timestamp, disease_city, disease, severity in recent_diseases:  
            disease_city = disease_city.lower().strip()

            # ✅ **Only match if the user's city matches the disease location**
            if user_city == disease_city:
                alert_msg = (
                    f"🚨 ALERT for {user_city.title()}, {user_country.title()}\n"
                    f"🦠 Disease: {disease}\n"
                    f"📍 Location: {disease_city.title()}\n"
                    f"⚠ Severity: {severity}\n"
                    f"🕒 Reported On: {timestamp}\n"
                    "--------------------------------------"
                )
                matched_alerts.add(alert_msg)  # ✅ Add to set to avoid duplicates

    # ✅ Display unique matched alerts
    if matched_alerts:
        print("\n".join(matched_alerts))
    else:
        print("✅ No disease outbreaks detected in your area.")

# ✅ Run matching function every 10 minutes
while True:
    match_diseases_with_users()
    print("\n⏳ Waiting for the next check...\n")
    time.sleep(600)  # 600 seconds = 10 minutes
