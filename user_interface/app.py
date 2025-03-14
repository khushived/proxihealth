from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
import sqlite3

app = Flask(__name__)
app.secret_key = "secure_random_key"  # Change this to a strong secret key

# GitHub OAuth Setup
oauth = OAuth(app)
github = oauth.register(
    name="github",
    client_id="YOUR_GITHUB_CLIENT_ID",
    client_secret="YOUR_GITHUB_CLIENT_SECRET",
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    userinfo_url="https://api.github.com/user",
    client_kwargs={"scope": "user:email"},
)

# Initialize Database
def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_id TEXT UNIQUE,
                name TEXT,
                email TEXT UNIQUE,
                age INTEGER,
                ip_address TEXT,
                prolonged_disease TEXT
            )"""
        )
        conn.commit()

@app.route("/")
def home():
    return render_template("index.html")  # Login page

@app.route("/login")
def login():
    return github.authorize_redirect(url_for("callback", _external=True))

@app.route("/callback")
def callback():
    token = github.authorize_access_token()
    user_info = github.get("https://api.github.com/user").json()
    
    github_id = user_info.get("id")
    name = user_info.get("name", "No Name Provided")
    email = user_info.get("email", "No Email Provided")
    ip_address = request.remote_addr  # Get IP Address

    # Store user details in the database
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE github_id = ?", (github_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute(
                "INSERT INTO users (github_id, name, email, ip_address) VALUES (?, ?, ?, ?)",
                (github_id, name, email, ip_address),
            )
            conn.commit()

    session["user"] = {"name": name, "email": email, "github_id": github_id}
    
    return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    
    user = session["user"]
    
    if request.method == "POST":
        age = request.form.get("age")
        prolonged_disease = request.form.get("disease")

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET age = ?, prolonged_disease = ? WHERE github_id = ?",
                (age, prolonged_disease, user["github_id"]),
            )
            conn.commit()
        
        return "User details updated successfully! <a href='/dashboard'>Go Back</a>"

    return render_template("dashboard.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
