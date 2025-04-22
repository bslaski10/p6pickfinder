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
    
    selections = []
    
    for player in lines_data:
        if player['name'] in options_data:
            over_odds = int(normalize_minus_sign(player['over']['american']))
            under_odds = int(normalize_minus_sign(player['under']['american']))
            
            if over_odds < under_odds:
                selected_type = 'over'
                selected_odds = player['over']['american']
                selected_line = f"{player['line']} {category_name.capitalize()}"
            else:
                selected_type = 'under'
                selected_odds = player['under']['american']
                selected_line = f"{player['line']} {category_name.capitalize()}"
            
            # Include matchup in the selection string
            matchup = player.get('matchup', 'N/A')
            game_time = convert_to_est(player.get('gameTime', ''))
            selection_str = f"{player['name']}, {selected_type} {selected_line}, {normalize_minus_sign(selected_odds)}, {matchup}, {game_time}"
            selections.append((selected_odds, selection_str))
    
    selections.sort(key=lambda x: int(normalize_minus_sign(x[0])))
    return [selection[1] for selection in selections]

# MLB stat categories to process
mlb_stat_types = [
    'hits_runs_rbis', 
    'hits', 
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

# Sort all selections by odds
all_selections.sort(key=lambda x: int(normalize_minus_sign(x.split(", ")[2])))

# Ensure the 'mlb/selections' folder exists
os.makedirs('mlb/selections', exist_ok=True)

# Write selections to a JSON file
with open('mlb/selections/selections.json', 'w') as file:
    json.dump(all_selections, file, indent=4)

print("All MLB selections written to mlb/selections/selections.json.")
