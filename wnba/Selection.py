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

# Function to process a given WNBA stat category
def process_category(category_name):
    lines_file   = f'wnba/lines/{category_name}_lines.json'
    options_file = f'wnba/options/{category_name}_options.json'
    
    if not os.path.exists(lines_file) or not os.path.exists(options_file):
        print(f"Skipping {category_name}: Missing data file.")
        return []
    
    with open(lines_file,   'r', encoding='utf-8') as f:
        lines_data = json.load(f)
    with open(options_file, 'r', encoding='utf-8') as f:
        options_data = json.load(f)
    
    selections = []
    for player in lines_data:
        if player['name'] in options_data:
            over_odds  = int(normalize_minus_sign(player['over']['american']))
            under_odds = int(normalize_minus_sign(player['under']['american']))
            
            if over_odds < under_odds:
                choice_type = 'over'
                choice_odds = player['over']['american']
            else:
                choice_type = 'under'
                choice_odds = player['under']['american']
            
            line_text = f"{player['line']} {category_name.capitalize()}"
            matchup   = player.get('matchup', 'N/A')
            game_time = convert_to_est(player.get('gameTime', ''))
            
            selection_str = (
                f"{player['name']}, "
                f"{choice_type} {line_text}, "
                f"{normalize_minus_sign(choice_odds)}, "
                f"{matchup}, {game_time}"
            )
            selections.append((int(normalize_minus_sign(choice_odds)), selection_str))
    
    # sort by numeric odds
    selections.sort(key=lambda x: x[0])
    return [s[1] for s in selections]

# WNBA stat categories to process
wnba_stat_types = [
    'points',
    'threes',
    'rebounds',
    'pra',
    'assists'
]

all_selections = []
for category in wnba_stat_types:
    try:
        all_selections.extend(process_category(category))
    except Exception as e:
        print(f"Error processing category '{category}': {e}")

# Also sort the full list by odds embedded in the string
all_selections.sort(key=lambda s: int(normalize_minus_sign(s.split(", ")[2])))

# Ensure the 'wnba/selections' folder exists
os.makedirs('wnba/selections', exist_ok=True)

# Write selections to JSON
with open('wnba/selections/selections.json', 'w', encoding='utf-8') as f:
    json.dump(all_selections, f, indent=4, ensure_ascii=False)

print("All WNBA selections written to wnba/selections/selections.json.")
