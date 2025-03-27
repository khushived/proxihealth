import os
import json
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = "secure_random_key"

# Load environment variables if needed
GOOGLE_CLIENT_ID = "your_google_client_id"
GOOGLE_CLIENT_SECRET = "your_google_client_secret"

# Initialize OAuth
oauth = OAuth(app)

# 🔹 Register GitHub OAuth
github = oauth.register(
    name="github",
    client_id="Ov23lirKrVSyqLV6BDXz",
    client_secret="e2a330300a087bbe4838e74c7381c1b47b116294",
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    client_kwargs={"scope": "user:email"},
)

# 🔹 Register Google OAuth
google = oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "https://www.googleapis.com/auth/fitness.activity.read"},
)

# ────────────────────────────────────────
# 🔹 GitHub Authentication Routes
# ────────────────────────────────────────

@app.route("/")
def login():
    return redirect(url_for("github_login"))

@app.route("/github")
def github_login():
    return github.authorize_redirect(url_for("github_callback", _external=True))

@app.route("/github_callback")
def github_callback():
    token = github.authorize_access_token()
    user = github.get("user").json()
    session["user"] = user
    return f"✅ Welcome, {user['login']} ({user.get('email', 'No Email')})"

# ────────────────────────────────────────
# 🔹 Google Fit Authentication Routes
# ────────────────────────────────────────

@app.route("/google")
def google_login():
    """ Redirect to Google OAuth for authentication """
    return google.authorize_redirect(url_for("google_callback", _external=True))

@app.route("/google_callback")
def google_callback():
    """ Handle Google OAuth callback, save credentials, and fetch Google Fit data """
    token = google.authorize_access_token()
    session["google_token"] = token

    # Save credentials to a file for later use
    with open("token.json", "w") as f:
        json.dump(token, f)

    return redirect(url_for("fetch_google_fit_data"))

# ────────────────────────────────────────
# 🔹 Fetch Google Fit Data
# ────────────────────────────────────────

def get_google_fit_service():
    """ Load credentials and return Google Fit API service """
    token_path = "token.json"
    if not os.path.exists(token_path):
        print("❌ Token file missing. Please authenticate first.")
        return None  

    try:
        with open(token_path, "r") as token_file:
            data = json.load(token_file)
        credentials = Credentials.from_authorized_user_info(data)
        return build("fitness", "v1", credentials=credentials)
    except Exception as e:
        print("❌ Google Fit authentication error:", e)
        return None

@app.route("/fetch_google_fit_data")
def fetch_google_fit_data():
    """ Fetch Heart Rate and Step Count from Google Fit """
    service = get_google_fit_service()
    if not service:
        return "❌ Google Fit authentication failed. Please login again."

    try:
        # Fetch heart rate
        dataset = get_dataset()
        heart_rate_data = fetch_heart_rate(service, dataset)
        step_count_data = fetch_steps(service, dataset)

        return f"✅ Data fetched successfully! <br> {heart_rate_data} <br> {step_count_data}"

    except Exception as e:
        return f"❌ Error fetching data: {e}"

# ────────────────────────────────────────
# 🔹 Utility Functions for Google Fit
# ────────────────────────────────────────

import datetime

def get_dataset():
    """ Generate dataset ID for the past 7 days """
    end_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1e9)
    start_time = end_time - (7 * 24 * 60 * 60 * int(1e9))
    return f"{start_time}-{end_time}"

def fetch_heart_rate(service, dataset):
    """ Fetch heart rate data from Google Fit """
    data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"

    response = service.users().dataSources().datasets().get(userId="me", dataSourceId=data_source, datasetId=dataset).execute()
    if "point" not in response or not response["point"]:
        return "⚠ No heart rate data found."

    return [
        f"{p['value'][0]['fpVal']} BPM at {datetime.datetime.utcfromtimestamp(int(p['startTimeNanos']) / 1e9)}"
        for p in response["point"]
    ]

def fetch_steps(service, dataset):
    """ Fetch step count data from Google Fit """
    data_source = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"

    response = service.users().dataSources().datasets().get(userId="me", dataSourceId=data_source, datasetId=dataset).execute()
    if "point" not in response or not response["point"]:
        return "⚠ No step count data found."

    return [
        f"{p['value'][0]['intVal']} steps at {datetime.datetime.utcfromtimestamp(int(p['startTimeNanos']) / 1e9)}"
        for p in response["point"]
    ]

if __name__ == "__main__":
    app.run(debug=True)
