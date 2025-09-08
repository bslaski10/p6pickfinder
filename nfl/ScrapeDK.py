import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

# Define URLs for NFL stat types
urls = {
    "passing_yards": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C9524&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%279524%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%279524%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "rushing_yards": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C9514&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%279514%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%279514%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "receiving_yards": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C14114&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%2714114%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%2714114%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "passing_TDs": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C9525&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%279525%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%279525%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "receptions": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C14115&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%2714115%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%2714115%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "completions": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C9522&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%279522%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%279522%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "passing_attempts": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C9517&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%279517%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%279517%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "rushing_attempts": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C9518&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%279518%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%279518%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "interceptions": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C15937&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%2715937%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%2715937%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "kicking_points": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C17062&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%2717062%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%2717062%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "tackles": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C18539&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%2718539%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%2718539%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "tackles+assists": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C18537&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%2718537%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%2718537%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events",
    "field_goals": "https://sportsbook-nash.draftkings.com/sites/US-SB/api/sportscontent/controldata/league/leagueSubcategory/v1/markets?isBatchable=false&templateVars=88808%2C17061&eventsQuery=%24filter%3DleagueId%20eq%20%2788808%27%20AND%20clientMetadata%2FSubcategories%2Fany%28s%3A%20s%2FId%20eq%20%2717061%27%29&marketsQuery=%24filter%3DclientMetadata%2FsubCategoryId%20eq%20%2717061%27%20AND%20tags%2Fall%28t%3A%20t%20ne%20%27SportcastBetBuilder%27%29&include=Events&entity=events"
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


# Ensure the 'nfl/data' folder exists
os.makedirs('nfl/data', exist_ok=True)

# Function to fetch JSON from a URL and save it to a file in the 'nfl/data' folder
def fetch_and_save_json(url, filename):
    driver.get(url)
    json_data = driver.find_element(By.TAG_NAME, "pre").text
    parsed_data = json.loads(json_data)
    
    # Save JSON file inside the 'nfl/data' folder
    with open(f"nfl/data/{filename}", "w", encoding="utf-8") as file:
        json.dump(parsed_data, file, ensure_ascii=False, indent=4)
    print(f"✅ JSON data saved successfully to 'nfl/data/{filename}'")

# Fetch and save data for all NFL stat types
for key, url in urls.items():
    filename = f"{key}.json"
    fetch_and_save_json(url, filename)

# Close the WebDriver
driver.quit()
