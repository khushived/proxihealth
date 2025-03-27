import requests
from bs4 import BeautifulSoup
import dateparser
import datetime
import time
import schedule

# ✅ List of diseases to search for
DISEASES = [
    "Dengue", "Nipah", "COVID-19", "Swine Flu", "Cholera", "Malaria",
    "Hepatitis", "Typhoid", "Leptospirosis", "Chikungunya", "Jaundice",
    "Conjunctivitis", "Food Poisoning", "H1N1", "Tuberculosis",
    "Pneumonia", "Skin Infection", "Asthma", "Fungal Infection",
    "Diarrhea", "Common Cold", "Cough", "Fever", "Stomach Infection",
    "Viral Fever", "Dysentery", "Allergy", "Sinusitis"
]

# ✅ Cities in Kerala to track
KERALA_CITIES = [
    "Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kottayam",
    "Palakkad", "Alappuzha", "Pathanamthitta", "Malappuram", "Kasaragod",
    "Kannur", "Idukki", "Ernakulam", "Wayanad", "Kollam"
]

# ✅ File to store the scraped data (TEXT file)
OUTPUT_FILE = "kerala_disease_data.txt"

# ✅ Function to scrape news for a specific disease
def scrape_news(disease):
    print(f"🔍 Fetching latest news for: {disease}...")

    query = f"{disease} outbreak in Kerala"
    url = f"https://www.google.com/search?q={query}&tbm=nws"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    news_data = []

    for article in soup.find_all("div", class_="SoaBEf"):
        title = article.find("div", class_="n0jPhd").get_text(strip=True) if article.find("div", class_="n0jPhd") else "Unknown"
        location = "Kerala"  # Default location if not found
        severity = "Low"  # Default severity

        # ✅ Extract news timestamp from Google News metadata
        time_element = article.find_next("span")
        news_time = time_element.get_text().strip() if time_element else None

        # ✅ Ensure valid timestamp
        news_timestamp = dateparser.parse(news_time) if news_time else datetime.datetime.now()
        if news_timestamp is None:
            news_timestamp = datetime.datetime.now()  # ✅ Prevent NoneType error

        # ✅ Try to extract specific city name
        for city in KERALA_CITIES:
            if city.lower() in title.lower():
                location = city
                break

        # ✅ Define severity levels
        if "death" in title.lower() or "severe" in title.lower():
            severity = "High"
        elif "hospitalized" in title.lower() or "outbreak" in title.lower():
            severity = "Moderate"

        news_data.append(f"{news_timestamp.strftime('%Y-%m-%d %H:%M')}\t{location}\t{disease}\t{severity}")

    return news_data

# ✅ Function to save data to a text file (Overwrite Mode)
def save_to_file(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:  # "w" mode overwrites old data
        file.write("Timestamp\tLocation\tDisease\tSeverity\n")  # ✅ Header line
        for entry in data:
            file.write(entry + "\n")

# ✅ Main function to run the scraper
def run_scraper():
    print("\n🕒 Running Kerala Disease News Scraper (Overwriting old data)...")

    all_news = []
    for disease in DISEASES:
        news = scrape_news(disease)
        all_news.extend(news)

    if all_news:
        save_to_file(all_news)
        print(f"✅ {len(all_news)} records saved to {OUTPUT_FILE} (Overwritten).\n")
    else:
        print("⚠️ No relevant news found.\n")

# ✅ Schedule scraper to run every 2 hours
schedule.every(2).hours.do(run_scraper)

# ✅ Run immediately before scheduling
run_scraper()

print("⏳ Waiting for next scheduled run...\n")
while True:
    schedule.run_pending()
    time.sleep(60)  # Checks every minute
