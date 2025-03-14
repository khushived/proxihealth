import sqlite3

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
        
        conn.commit()

def save_user(name, email, age, sex, prolonged_disease):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (name, email, age, sex, prolonged_disease) VALUES (?, ?, ?, ?, ?)", 
                       (name, email, age, sex, prolonged_disease))
        conn.commit()
