import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.chrome.options import Options

# Define URLs for WNBA stat types
urls = {
    "points": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusva/v1/leagues/94682/categories/1215/subcategories/12488",
    "threes": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusva/v1/leagues/94682/categories/1218/subcategories/12497",
    "rebounds": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusva/v1/leagues/94682/categories/1216/subcategories/12492",
    "pra": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusva/v1/leagues/94682/categories/583/subcategories/5001",
    "assists": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusva/v1/leagues/94682/categories/1217/subcategories/12495"
}

# Setup Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--user-data-dir=/tmp/chrome-user-data')

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Ensure the 'wnba/data' folder exists
os.makedirs('wnba/data', exist_ok=True)

# Function to fetch JSON from a URL and save it to a file in the 'wnba/data' folder
def fetch_and_save_json(url, filename):
    driver.get(url)
    json_data = driver.find_element(By.TAG_NAME, "pre").text
    parsed_data = json.loads(json_data)
    
    with open(f"wnba/data/{filename}", "w", encoding="utf-8") as file:
        json.dump(parsed_data, file, ensure_ascii=False, indent=4)
    print(f"✅ JSON data saved successfully to 'wnba/data/{filename}'")

# Fetch and save data for all WNBA stat types
for key, url in urls.items():
    filename = f"{key}.json"
    fetch_and_save_json(url, filename)

# Close the WebDriver
driver.quit()
