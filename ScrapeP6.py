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
from bs4 import BeautifulSoup

# Regex to match "Pick <Name> for Less than"
player_regex = re.compile(r"^Pick\s+(.*?)\s+for\s+Less than", re.IGNORECASE)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--log-level=3")

def get_driver():
    return webdriver.Chrome(options=chrome_options)

# NBA stat categories and URLs
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

def normalize_to_initial_format(full_name):
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}. {' '.join(parts[1:])}"
    return full_name

# ✅ New: Check if a stat label exists on the page
def is_stat_type_available(driver, stat_label):
    try:
        driver.find_element(By.XPATH, f'//div[text()="{stat_label}"]')
        return True
    except Exception:
        return False

def clear_stats_files():
    os.makedirs("options", exist_ok=True)
    os.makedirs("data_p6", exist_ok=True)
    with open("locked.json", "w", encoding="utf-8") as f:
        json.dump([], f)
    for stat_name in urls:
        with open(f"options/{stat_name}_options.json", "w", encoding="utf-8") as f:
            json.dump([], f)

def scrape_and_save(stat_name, stat_label, url):
    driver = get_driver()
    try:
        driver.get(url)
    except Exception as e:
        print(f"Failed to load {stat_label}: {e}")
        driver.quit()
        return

    try:
        # Skip stat type if not visible
        if not is_stat_type_available(driver, stat_label):
            print(f"⚠️ {stat_label} not found on page. Skipping.")
            driver.quit()
            return

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(@aria-label, "for Less than")]'))
        )
        time.sleep(5)

        html = driver.page_source
        with open(f"data_p6/{stat_name}_p6.json", "w", encoding="utf-8") as f:
            json.dump({"html": html}, f)

        soup = BeautifulSoup(html, "html.parser")

        # Step 1: Get locked players
        locked_players_set = set()
        for card in soup.select('[data-testid="playerStatCard"]'):
            name_tag = card.select_one('[data-testid="player-name"]')
            if not name_tag:
                continue
            name = name_tag.get_text(strip=True)
            if card.find("use", {"href": "#lock-icon"}):
                locked_players_set.add(name)

        # Step 2: Get "Less than" players
        valid_players_set = set()
        buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "for Less than")]')
        for button in buttons:
            aria_label = button.get_attribute("aria-label")
            if not aria_label:
                continue
            match = player_regex.search(aria_label)
            if match:
                name = match.group(1).strip()
                if name != "Contest Fill":
                    valid_players_set.add(name)

        # Step 3: Exclude locked players
        unlocked_valid_players = sorted([
            name for name in valid_players_set
            if normalize_to_initial_format(name) not in locked_players_set
        ])

        with open(f"options/{stat_name}_options.json", "w", encoding="utf-8") as f:
            json.dump(unlocked_valid_players, f, indent=4)

        # Update locked.json globally
        locked_file = "locked.json"
        if os.path.exists(locked_file):
            with open(locked_file, "r", encoding="utf-8") as f:
                existing_locked = set(json.load(f))
        else:
            existing_locked = set()

        all_locked = sorted(existing_locked.union(locked_players_set))
        with open(locked_file, "w", encoding="utf-8") as f:
            json.dump(all_locked, f, indent=4)

        print(f"✅ {stat_label}: {len(unlocked_valid_players)} options, {len(locked_players_set)} locked")

    except Exception as e:
        print(f"⚠️ Error scraping {stat_label}: {e}")
    finally:
        driver.quit()

def run_scraping():
    clear_stats_files()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(scrape_and_save, stat, label, url) for stat, (label, url) in urls.items()]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Thread error: {e}")

run_scraping()
