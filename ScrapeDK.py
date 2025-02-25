import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

# Define URLs for all the stat types
urls = {
    "points": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1215/subcategories/12488",
    "rebounds": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1216/subcategories/12492",
    "pra": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/583/subcategories/5001",
    "assists": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1217/subcategories/12495",
    "threes": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1218/subcategories/12497",
    "steals": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1293/subcategories/13508",
    "pa": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/583/subcategories/9973",
    "pr": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/583/subcategories/9976",
    "ar": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/583/subcategories/9974",
    "turnovers": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1293/subcategories/13782",
    "blocks": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1293/subcategories/13780",
    "sb": "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusnj/v1/leagues/42648/categories/1293/subcategories/13781"
}

# Initialize the WebDriver
driver = webdriver.Chrome()

# Ensure the 'data' folder exists
os.makedirs('data', exist_ok=True)

# Function to fetch JSON from a URL and save it to a file in the 'data' folder
def fetch_and_save_json(url, filename):
    driver.get(url)
    json_data = driver.find_element(By.TAG_NAME, "pre").text
    parsed_data = json.loads(json_data)
    
    # Save JSON file inside the 'data' folder
    with open(f"data/{filename}", "w", encoding="utf-8") as file:
        json.dump(parsed_data, file, ensure_ascii=False, indent=4)
    print(f"✅ JSON data saved successfully to 'data/{filename}'")

# Fetch and save data for all stat types
for key, url in urls.items():
    filename = f"{key}.json"
    fetch_and_save_json(url, filename)

# Close the WebDriver
driver.quit()
