import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

# Define URLs for MLB stat types
urls = {
    "hits_runs_rbis": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/743/subcategories/17406",
    "hits": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/743/subcategories/6719",
    "tbs": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/743/subcategories/6607",
    "singles": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/743/subcategories/17409",
    "walks": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/743/subcategories/17411",
    "SOs": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/1031/subcategories/15221",
    "hits_allowed": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/1031/subcategories/9886",
    "walks_allowed": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/1031/subcategories/15219",
    "era": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/1031/subcategories/17412",
    "outs": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnc/v1/leagues/84240/categories/1031/subcategories/17413"
}

# Initialize the WebDriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--user-data-dir=/tmp/chrome-user-data')

driver = webdriver.Chrome(options=chrome_options)


# Ensure the 'mlb/data' folder exists
os.makedirs('mlb/data', exist_ok=True)

# Function to fetch JSON from a URL and save it to a file in the 'mlb/data' folder
def fetch_and_save_json(url, filename):
    driver.get(url)
    json_data = driver.find_element(By.TAG_NAME, "pre").text
    parsed_data = json.loads(json_data)
    
    # Save JSON file inside the 'mlb/data' folder
    with open(f"mlb/data/{filename}", "w", encoding="utf-8") as file:
        json.dump(parsed_data, file, ensure_ascii=False, indent=4)
    print(f"✅ JSON data saved successfully to 'mlb/data/{filename}'")

# Fetch and save data for all MLB stat types
for key, url in urls.items():
    filename = f"{key}.json"
    fetch_and_save_json(url, filename)

# Close the WebDriver
driver.quit()
