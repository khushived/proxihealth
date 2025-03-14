# ProxiHealth 🚀
ProxiHealth is a health tracking and disease outbreak notification system that:
1. **Scrapes Twitter** every 2 hours for disease-related tweets in Kerala.
2. **Stores and processes** the scraped data in a structured format.
3. **Matches user location** with disease outbreak data to send alerts.
4. **Provides simple disease prediction** using heart rate & step count.
5. **Secures user data** using OAuth authentication.

## How to Run 🛠
1. Install dependencies: `pip install -r requirements.txt`
2. Start Twitter scraping: `python scraping/scheduler.py`
3. Start the Flask API: `python user_interface/app.py`

Enjoy disease outbreak tracking with **ProxiHealth**! ✅
