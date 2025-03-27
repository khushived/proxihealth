from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import psycopg2
import os
import datetime
import time
import urllib.parse as urlparse
from dotenv import load_dotenv

# 🔹 Load environment variables from .env file
load_dotenv()

# 🔹 Define OAuth2 scopes
SCOPES = os.getenv("GOOGLE_FIT_SCOPES", "").split()

# 🔹 Load Google API credentials
CREDENTIALS_FILE = "credentials.json"  # Ensure this file exists

# 🔹 Load Database Credentials
DATABASE_URL = os.getenv("DATABASE_URL")
DB_SSL = os.getenv("DB_SSL", "false").lower() == "true"

# ✅ Parse the DATABASE_URL for connection
url = urlparse.urlparse(DATABASE_URL)
db_conn_params = {
    "dbname": url.path[1:],
    "user": url.username,
    "password": url.password,
    "host": url.hostname,
    "port": url.port,
    "sslmode": "require" if DB_SSL else "prefer"
}

# ✅ Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(**db_conn_params)

# ✅ Authenticate a new user and store credentials in the database
def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=5000)

    # Get user ID from Google Fit API
    service = build("fitness", "v1", credentials=creds)
    user_info = service.users().dataSources().list(userId="me").execute()
    google_user_id = user_info["userId"]

    access_token = creds.token
    refresh_token = creds.refresh_token
    token_expiry = creds.expiry

    # Store user tokens in PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (google_user_id, access_token, refresh_token, token_expiry)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (google_user_id) 
        DO UPDATE SET access_token = EXCLUDED.access_token, 
                      refresh_token = EXCLUDED.refresh_token, 
                      token_expiry = EXCLUDED.token_expiry;
    """, (google_user_id, access_token, refresh_token, token_expiry))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ User {google_user_id} authenticated and stored in DB.")

# ✅ Refresh access token if expired
def refresh_access_token(google_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT access_token, refresh_token, token_expiry FROM users WHERE google_user_id = %s", (google_user_id,))
    user = cursor.fetchone()

    if not user:
        print(f"❌ No user found with ID: {google_user_id}")
        return None

    access_token, refresh_token, token_expiry = user

    # Check if token is expired
    if token_expiry < datetime.datetime.utcnow():
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
        )

        creds.refresh(Request())

        # Update new token in DB
        cursor.execute("""
            UPDATE users SET access_token = %s, token_expiry = %s WHERE google_user_id = %s
        """, (creds.token, creds.expiry, google_user_id))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"🔄 Access token refreshed for {google_user_id}")
        return creds.token
    else:
        return access_token

# ✅ Fetch Google Fit data for all users
def fetch_all_users_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT google_user_id FROM users")
    users = cursor.fetchall()

    for user in users:
        google_user_id = user[0]
        access_token = refresh_access_token(google_user_id)

        if access_token:
            service = build("fitness", "v1", credentials=Credentials(token=access_token))
            fetch_fitness_data(service, google_user_id)  # Fetch & store data for user

    cursor.close()
    conn.close()

# ✅ Fetch fitness data (Heart rate, Steps, etc.)
def fetch_fitness_data(service, google_user_id):
    end_time = int(time.time() * 1000000000)
    start_time = end_time - (24 * 60 * 60 * 1000000000)
    dataset = f"{start_time}-{end_time}"

    # Fetch Steps
    response = service.users().dataSources().datasets().get(
        userId="me",
        dataSourceId="derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
        datasetId=dataset
    ).execute()

    steps = response.get("point", [])

    conn = get_db_connection()
    cursor = conn.cursor()

    for point in steps:
        timestamp = int(point["startTimeNanos"]) / 1e9
        readable_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        step_count = point["value"][0]["intVal"]

        cursor.execute("INSERT INTO fitness_data (google_user_id, timestamp, data_type, value) VALUES (%s, %s, %s, %s)",
                       (google_user_id, readable_time, "steps", step_count))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Step data saved for user {google_user_id}")

# ✅ Run the script
if __name__ == "__main__":
    fetch_all_users_data()

