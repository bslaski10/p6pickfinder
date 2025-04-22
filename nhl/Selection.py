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
        # Clean the string to avoid ValueError
        cleaned_time = utc_time_str.replace("Z", "+00:00").replace(".0000000", ".000000")
        utc_time = datetime.fromisoformat(cleaned_time)

        # Convert to Eastern Time
        est_zone = pytz.timezone("US/Eastern")
        est_time = utc_time.astimezone(est_zone)

        return est_time.strftime("%I:%M %p").lstrip("0")  # Format as h:mm AM/PM
    except Exception as e:
        print(f"[Time Conversion Error] Could not parse: {utc_time_str} — {e}")
        return ""

# Function to process a given NHL stat category
def process_category(category_name):
    lines_file = f'nhl/lines/{category_name}_lines.json'
    options_file = f'nhl/options/{category_name}_options.json'
    
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
            
            # Extract matchup from the event data
            matchup = player.get('matchup', 'N/A')
            
            # Convert game time to EST
            game_time = convert_to_est(player.get('gameTime', ''))
            
            # Build the selection string
            selection_str = f"{player['name']}, {selected_type} {selected_line}, {normalize_minus_sign(selected_odds)}, {matchup}, {game_time}"
            selections.append((selected_odds, selection_str))
    
    selections.sort(key=lambda x: int(normalize_minus_sign(x[0])))
    return [selection[1] for selection in selections]

# NHL stat categories to process
nhl_stat_types = ['shots_on_goal', 'points', 'assists', 'blocks', 'saves']

all_selections = []
for category in nhl_stat_types:
    try:
        selections = process_category(category)
        all_selections.extend(selections)
    except Exception as e:
        print(f"Error processing category '{category}': {e}")

all_selections.sort(key=lambda x: int(normalize_minus_sign(x.split(", ")[2])))

os.makedirs('nhl/selections', exist_ok=True)
with open('nhl/selections/selections.json', 'w') as file:
    json.dump(all_selections, file, indent=4)

print("All NHL selections written to nhl/selections/selections.json.")
