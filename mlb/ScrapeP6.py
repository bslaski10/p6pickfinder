import os
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# Regular expression to strictly match the pattern "Pick <Player Name> for Less than"
player_regex = re.compile(r"^Pick\s+(.*?)\s+for\s+Less than", re.IGNORECASE)

# Set up Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without UI
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--log-level=3")  # Suppress unnecessary logs

# Function to initialize WebDriver
def get_driver():
    return webdriver.Chrome(options=chrome_options)

# MLB-specific stat URLs and their labels
urls = {
    "hits_runs_rbis": ("Hits + Runs + RBIs", "https://pick6.draftkings.com/?sport=MLB&stat=H%2BR%2BRBI"),
    "hits": ("Hits", "https://pick6.draftkings.com/?sport=MLB&stat=H"),
    "tbs": ("Total Bases", "https://pick6.draftkings.com/?sport=MLB&stat=Bases"),
    "singles": ("Singles", "https://pick6.draftkings.com/?sport=MLB&stat=1B"),
    "walks": ("Walks", "https://pick6.draftkings.com/?sport=MLB&stat=BB"),
    "SOs": ("Strikeouts Thrown", "https://pick6.draftkings.com/?sport=MLB&stat=SO"),
    "hits_allowed": ("Hits Against", "https://pick6.draftkings.com/?sport=MLB&stat=HA"),
    "walks_allowed": ("Walks Allowed", "https://pick6.draftkings.com/?sport=MLB&stat=Walks"),
    "era": ("Earned Runs Allowed", "https://pick6.draftkings.com/?sport=MLB&stat=ER"),
    "outs": ("Outs", "https://pick6.draftkings.com/?sport=MLB&stat=O")
}

# Function to clear all stats JSON files (set to empty list)
def clear_stats_files():
    os.makedirs('mlb/options', exist_ok=True)
    for stat_name in urls.keys():
        filename = f"mlb/options/{stat_name}_options.json"
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
        # Wait until at least one button with "for Less than" is present in the aria-label
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(@aria-label, "for Less than")]'))
        )
        time.sleep(5)  # Additional buffer

        # Verify the stat type is available on the page
        if not is_stat_type_available(driver, stat_label):
            print(f"⚠️ Stat type {stat_label} not available, skipping scraping.")
            driver.quit()
            return

        # Find all buttons whose aria-label contains "for Less than"
        player_buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "for Less than")]')
        valid_players = []

        for button in player_buttons:
            try:
                aria_label = button.get_attribute('aria-label')
                if not aria_label:
                    continue
                # Use regex to extract the player name only if it exactly follows the pattern.
                match = player_regex.search(aria_label)
                if match:
                    name = match.group(1).strip()
                    if name != "Contest Fill" and name not in valid_players:
                        valid_players.append(name)
            except Exception as e:
                print(f"Error extracting player name in {stat_label}: {e}")

        # Save valid player names to a JSON file
        filename = f"mlb/options/{stat_name}_options.json"
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(valid_players, json_file, ensure_ascii=False, indent=4)
        print(f"✅ {stat_label} data saved! ({len(valid_players)} valid players)")

    except Exception as e:
        print(f"⚠️ Error scraping {stat_label}: {e}")

    finally:
        driver.quit()

# Run the scraping process for all URLs concurrently
def run_scraping():
    clear_stats_files()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(scrape_and_save, stat_name, stat_label, url)
            for stat_name, (stat_label, url) in urls.items()
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error in thread: {e}")

# Start the scraping process
run_scraping()
