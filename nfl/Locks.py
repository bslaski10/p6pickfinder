import json
import time
from datetime import datetime
import pytz

def update_progress(value, message):
    progress = {"progress": value, "message": message}
    with open("progress.json", "w") as f:
        json.dump(progress, f)

def log_execution_time():
    # Convert current time to Eastern Time
    eastern = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern).strftime("%Y-%m-%d %H:%M:%S")
    time_data = {"execution_time": now_eastern}
    with open("nfl/time.json", "w") as f:
        json.dump(time_data, f)

# Stage 1: Fetching DK Data (ScrapeDK and Fetch)
update_progress(0, "Fetching DK Data")
import ScrapeDK
import Fetch
update_progress(30, "Fetching DK Data complete")

# Stage 2: Scraping Pick 6 (ScrapeP6)
update_progress(30, "Scraping Pick 6")
import ScrapeP6
update_progress(80, "Scraping Pick 6 complete")

# Stage 3: Getting Locks (Selection and Picks)
update_progress(80, "Getting Locks")
import Selection
import Picks
update_progress(99, "Getting Locks complete")

# Log execution time in Eastern Time
log_execution_time()

# Final update
update_progress(100, "Done!")
