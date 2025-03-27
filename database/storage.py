import sqlite3
from datetime import datetime

def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_id TEXT UNIQUE,
            name TEXT,
            email TEXT UNIQUE,
            age INTEGER,
            sex TEXT,
            prolonged_disease TEXT
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            timestamp TEXT,
            latitude REAL,
            longitude REAL
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT,
            timestamp TEXT,
            disease TEXT,
            people_affected INTEGER,
            severity TEXT,
            latitude REAL,
            longitude REAL
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            message TEXT,
            timestamp TEXT
        )""")
        
        conn.commit()

def save_user(name, email, age, sex, prolonged_disease):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (name, email, age, sex, prolonged_disease) VALUES (?, ?, ?, ?, ?)", 
                       (name, email, age, sex, prolonged_disease))
        conn.commit()

def save_notification(user_email, message):
    """Save a notification for a specific user"""
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO notifications (user_email, message, timestamp) VALUES (?, ?, ?)", 
                       (user_email, message, timestamp))
        conn.commit()

def get_user_notifications(user_email):
    """Fetch notifications for a specific user"""
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT message, timestamp FROM notifications WHERE user_email = ? ORDER BY timestamp DESC", 
                       (user_email,))
        return cursor.fetchall()

def save_tweet_data(tweet_id, disease, people_affected, severity, latitude, longitude):
    """Save tweet-based disease data"""
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO tweets (tweet_id, timestamp, disease, people_affected, severity, latitude, longitude) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (tweet_id, timestamp, disease, people_affected, severity, latitude, longitude))
        conn.commit()

def fetch_disease_data_for_user(user_email):
    """Fetch disease data relevant to the user's location"""
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()

        # Get user's last known location
        cursor.execute("""
            SELECT latitude, longitude FROM locations 
            WHERE user_email = ? ORDER BY timestamp DESC LIMIT 1
        """, (user_email,))
        location = cursor.fetchone()

        if location:
            latitude, longitude = location
            cursor.execute("""
                SELECT disease, people_affected, severity, timestamp 
                FROM tweets 
                WHERE ABS(latitude - ?) < 0.1 AND ABS(longitude - ?) < 0.1
                ORDER BY timestamp DESC
            """, (latitude, longitude))
            return cursor.fetchall()
        return []

def generate_notifications_for_users():
    """Generate notifications for users based on disease data and location"""
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()

        # Get all users
        cursor.execute("SELECT email FROM users")
        users = cursor.fetchall()

        for (email,) in users:
            disease_data = fetch_disease_data_for_user(email)

            if disease_data:
                for disease, people_affected, severity, timestamp in disease_data:
                    message = f"Alert! {disease} outbreak near you. Severity: {severity}. Affected: {people_affected}."
                    save_notification(email, message)

