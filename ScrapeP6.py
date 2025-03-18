import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# Set up Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without UI
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--log-level=3")  # Suppress unnecessary logs

# Function to initialize WebDriver
def get_driver():
    return webdriver.Chrome(options=chrome_options)

# NBA-specific stat URLs and their labels
urls = {
    "points": ("Points", "https://pick6.draftkings.com/?sport=NBA&stat=PTS"),
    "rebounds": ("Rebounds", "https://pick6.draftkings.com/?sport=NBA&stat=REB"),
    "pra": ("Points + Rebounds + Assists", "https://pick6.draftkings.com/?sport=NBA&stat=P%2BR%2BA"),
    "assists": ("Assists", "https://pick6.draftkings.com/?sport=NBA&stat=AST"),
    "threes": ("3-Pointers Made", "https://pick6.draftkings.com/?sport=NBA&stat=3PM"),
    "steals": ("Steals", "https://pick6.draftkings.com/?sport=NBA&stat=STL"),
    "pa": ("Points + Assists", "https://pick6.draftkings.com/?sport=NBA&stat=PTS%2BAST"),
    "pr": ("Points + Rebounds", "https://pick6.draftkings.com/?sport=NBA&stat=PTS%2BREB"),
    "ar": ("Assists + Rebounds", "https://pick6.draftkings.com/?sport=NBA&stat=AST%2BREB"),
    "turnovers": ("Turnovers", "https://pick6.draftkings.com/?sport=NBA&stat=TO"),
    "blocks": ("Blocks", "https://pick6.draftkings.com/?sport=NBA&stat=BLK"),
    "sb": ("Steals + Blocks", "https://pick6.draftkings.com/?stat=STL%2BBLK")
}

# Function to clear all stats JSON files (set to empty list)
def clear_stats_files():
    os.makedirs('options', exist_ok=True)
    for stat_name in urls.keys():
        filename = f"options/{stat_name}_options.json"
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump([], json_file)
        print(f"Initialized {filename} with empty list.")

# Function to check if a stat type is available on the page
def is_stat_type_available(driver, stat_label):
    try:
        driver.find_element(By.XPATH, f'//div[text()="{stat_label}"]')
        return True
    except Exception:
        return False

# Function to scrape player names and save to a JSON file
def scrape_and_save(stat_name, stat_label, url):
    driver = get_driver()
    try:
        driver.get(url)
    except Exception as e:
        print(f"Error loading {stat_label} URL: {e}")
        driver.quit()
        return

    try:
        # Wait until a button with an aria-label starting with "Open " is present
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[starts-with(@aria-label, "Open ")]'))
        )
        time.sleep(5)  # Additional buffer

        # Verify the stat type is available on the page
        if not is_stat_type_available(driver, stat_label):
            print(f"⚠️ Stat type {stat_label} not available, skipping scraping.")
            driver.quit()
            return

        # Find all buttons with aria-label starting with "Open "
        player_buttons = driver.find_elements(By.XPATH, '//button[starts-with(@aria-label, "Open ")]')
        player_names = []

        for button in player_buttons:
            try:
                player_name = button.get_attribute('aria-label')
                # Extract the player name from the aria-label text
                name = player_name.split("Open ")[1].split("'")[0]
                player_names.append(name)
            except Exception as e:
                print(f"Error extracting player name in {stat_label}: {e}")

        # Save player names to a JSON file
        filename = f"options/{stat_name}_options.json"
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(player_names, json_file, ensure_ascii=False, indent=4)
        print(f"✅ {stat_label} data saved! ({len(player_names)} players)")

    except Exception as e:
        print(f"⚠️ Error scraping {stat_label}: {e}")

    finally:
        driver.quit()

# Run the scraping process for all URLs concurrently
def run_scraping():
    clear_stats_files()
    # Reduce concurrency to 4 workers to lessen load and potential timeouts
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(scrape_and_save, stat_name, stat_label, url)
            for stat_name, (stat_label, url) in urls.items()
        ]
        # Wait for all tasks to complete
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error in thread: {e}")

# Start the scraping process
run_scraping()
