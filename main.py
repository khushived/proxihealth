from threading import Thread
from scraping.scheduler import run_scheduler
from user_interface.app import app
from database.storage import init_db

if __name__ == "__main__":
    init_db()
    
    print("[INFO] Starting Web App & Scheduler...")
    Thread(target=run_scheduler).start()
    
    app.run(debug=True)
