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
    
    # Convert string to datetime object
    utc_time = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
    
    # Define time zones
    utc_zone = pytz.utc
    est_zone = pytz.timezone("US/Eastern")

    # Convert to EST
    est_time = utc_time.astimezone(est_zone)

    # Format time in "h:mm am/pm" format
    return est_time.strftime("%I:%M %p").lstrip("0")  # Remove leading zero from hour

# Function to format the matchup to remove city names and only show team names
def format_matchup(matchup):
    if not matchup:
        return ""
    
    # Split matchup into two teams
    teams = matchup.split(" @ ")
    if len(teams) != 2:
        return matchup  # Return original if unexpected format

    # Extract only the last word (team name) from each
    team1 = teams[0].split()[-1]  # Last word of the first team
    team2 = teams[1].split()[-1]  # Last word of the second team

    return f"{team1} @ {team2}"

# Function to process a given category (stat type)
def process_category(category_name):
    with open(f'lines/{category_name}_lines.json', 'r') as file:
        lines_data = json.load(file)

    with open(f'options/{category_name}_options.json', 'r') as file:
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

            # Get formatted matchup and EST game time
            matchup = format_matchup(player.get('matchup', ''))
            game_time = convert_to_est(player.get('gameTime', ''))

            # Format selection string
            selection_str = f"{player['name']}, {selected_type} {selected_line}, {normalize_minus_sign(selected_odds)}, {matchup}, {game_time}"
            selections.append((selected_odds, selection_str))

    selections.sort(key=lambda x: int(normalize_minus_sign(x[0])))
    sorted_selections = [selection[1] for selection in selections]

    os.makedirs('selections', exist_ok=True)
    output_file = f'selections/{category_name}_selections.json'
    with open(output_file, 'w') as file:
        json.dump(sorted_selections, file, indent=4)

    return sorted_selections

# List of all stat types (categories) to process
stat_types = ['points', 'rebounds', 'pra', 'assists', 'threes', 'steals', 'pa', 'pr', 'ar', 'turnovers', 'blocks', 'sb']

all_selections = []
for category in stat_types:
    try:
        selections = process_category(category)
        all_selections.extend(selections)
    except Exception as e:
        print(f"Error processing category '{category}': {e}")

all_selections.sort(key=lambda x: int(normalize_minus_sign(x.split(", ")[2])))

with open('selections/selections.json', 'w') as file:
    json.dump(all_selections, file, indent=4)

print("All selections written to selections/selections.json.")
