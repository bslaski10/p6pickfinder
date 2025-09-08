import json
import os
from datetime import datetime
import pytz

# Function to normalize the minus sign to a regular hyphen
def normalize_minus_sign(odds):
    return odds.replace('−', '-').replace('âˆ’', '-').replace('\u00e2\u02c6\u2019', '-')

# Function to convert UTC game time to Eastern Time (ET)
def convert_to_est(utc_time_str):
    if not utc_time_str:
        return ""
    try:
        cleaned_time = utc_time_str.replace("Z", "+00:00")
        if ".0000000" in cleaned_time:
            cleaned_time = cleaned_time.replace(".0000000", ".000000")
        utc_time = datetime.fromisoformat(cleaned_time)
        est_zone = pytz.timezone("US/Eastern")
        est_time = utc_time.astimezone(est_zone)
        return est_time.strftime("%I:%M %p").lstrip("0")
    except Exception as e:
        print(f"[Time Parse Error] '{utc_time_str}' → {e}")
        return ""

# Suffixes to ignore when forming "F. Last" from a full name
_SUFFIXES = {"Jr", "Jr.", "Sr", "Sr.", "II", "III", "IV", "V"}

def full_to_initial_last(full_name: str) -> str:
    """
    Convert 'First Middle Last [Suffix]' -> 'F. Last' (where Last may be multi-word,
    e.g., 'Woods Richardson'). Suffixes like Jr/Sr/II are ignored.
    """
    if not full_name:
        return ""
    # Remove commas (often appear before suffixes) and collapse whitespace
    name = full_name.replace(",", " ").strip()
    parts = [p for p in name.split() if p]  # split on whitespace

    if not parts:
        return ""

    # First token is the first name
    first = parts[0]

    # Remove trailing suffix tokens (Jr, Sr, II, etc.)
    tail = parts[1:]  # everything after first name
    while tail and tail[-1] in _SUFFIXES:
        tail.pop()

    # Whatever remains after the first name is considered the last name block
    # (can be multi-word like "Woods Richardson" or "De La Cruz")
    last_block = " ".join(tail).strip()

    # Fallback: if for some reason we don't have a last name (single-token name),
    # just use the single token as "last" (rare in MLB but safe).
    if not last_block:
        last_block = first

    # Build "F. Last"
    first_initial = first[0] + "."
    return f"{first_initial} {last_block}"

# Function to process a given MLB stat category
def process_category(category_name):
    lines_file = f'mlb/lines/{category_name}_lines.json'
    options_file = f'mlb/options/{category_name}_options.json'

    if not os.path.exists(lines_file) or not os.path.exists(options_file):
        print(f"Skipping {category_name}: Missing data file.")
        return []

    with open(lines_file, 'r') as file:
        lines_data = json.load(file)

    with open(options_file, 'r') as file:
        options_data = json.load(file)

    # Expect options_data to be a list like ["B. Elder", "C. Dana", ...]
    # Convert to a set for faster membership checks
    if isinstance(options_data, list):
        options_set = set(options_data)
    else:
        # If the structure changes, try to coerce into a set of strings
        try:
            options_set = set(map(str, options_data))
        except Exception:
            options_set = set()

    selections = []

    for player in lines_data:
        # lines_data still has full names (e.g., "Simeon Woods Richardson")
        full_name = player.get('name', '')
        initial_last = full_to_initial_last(full_name)

        if initial_last in options_set:
            over_amer = normalize_minus_sign(str(player['over']['american']))
            under_amer = normalize_minus_sign(str(player['under']['american']))

            try:
                over_odds = int(over_amer)
                under_odds = int(under_amer)
            except ValueError:
                # Skip if odds aren't numeric for some reason
                continue

            # Pick the better (more negative) price
            if over_odds < under_odds:
                selected_type = 'over'
                selected_odds = over_amer
            else:
                selected_type = 'under'
                selected_odds = under_amer

            selected_line = f"{player['line']} {category_name.capitalize()}"
            matchup = player.get('matchup', 'N/A')
            game_time = convert_to_est(player.get('gameTime', ''))
            selection_str = f"{full_name}, {selected_type} {selected_line}, {normalize_minus_sign(selected_odds)}, {matchup}, {game_time}"
            selections.append((selected_odds, selection_str))

    # Sort by numerical odds
    selections.sort(key=lambda x: int(normalize_minus_sign(str(x[0]))))
    return [selection[1] for selection in selections]

# MLB stat categories to process
mlb_stat_types = [
    'hits_runs_rbis',
    # 'hits',
    'tbs',
    'singles',
    'walks',
    'SOs',
    'hits_allowed',
    'walks_allowed',
    'era',
    'outs'
]

all_selections = []
for category in mlb_stat_types:
    try:
        selections = process_category(category)
        all_selections.extend(selections)
    except Exception as e:
        print(f"Error processing category '{category}': {e}")

# Sort all selections by odds (3rd CSV field)
all_selections.sort(key=lambda x: int(normalize_minus_sign(x.split(", ")[2])))

# Ensure the 'mlb/selections' folder exists
os.makedirs('mlb/selections', exist_ok=True)

# Write selections to a JSON file
with open('mlb/selections/selections.json', 'w') as file:
    json.dump(all_selections, file, indent=4)

print("All MLB selections written to mlb/selections/selections.json.")
