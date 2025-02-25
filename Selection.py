import json
import os

# Function to normalize the minus sign to a regular hyphen
def normalize_minus_sign(odds):
    # Normalize the various representations of minus signs to a regular '-'
    return odds.replace('−', '-').replace('âˆ’', '-').replace('\u00e2\u02c6\u2019', '-')

# Function to process a given category (stat type)
def process_category(category_name):
    # Load the lines file for the category (e.g., assists_lines.json, points_lines.json, etc.)
    with open(f'lines/{category_name}_lines.json', 'r') as file:
        lines_data = json.load(file)

    # Load the options file for the category (e.g., assists_options.json, points_options.json, etc.)
    with open(f'options/{category_name}_options.json', 'r') as file:
        options_data = json.load(file)

    # Prepare the selections list
    selections = []

    # Iterate through each player entry in the lines JSON file
    for player in lines_data:
        # Only process if the player's name exists in the options data for the category
        if player['name'] in options_data:
            # Normalize and convert the American odds for "over" and "under" to integers
            over_odds = int(normalize_minus_sign(player['over']['american']))
            under_odds = int(normalize_minus_sign(player['under']['american']))

            # Determine which odds are lower (selecting over or under accordingly)
            if over_odds < under_odds:
                selected_type = 'over'
                selected_odds = player['over']['american']
                selected_line = f"{player['line']} {category_name.capitalize()}"
            else:
                selected_type = 'under'
                selected_odds = player['under']['american']
                selected_line = f"{player['line']} {category_name.capitalize()}"

            # Format the selection with normalized odds
            selection = f"{player['name']}, {selected_type} {selected_line}, {normalize_minus_sign(selected_odds)}"
            selections.append((selected_odds, selection))

    # Sort selections based on the odds (converted to integer for proper numerical sorting)
    selections.sort(key=lambda x: int(normalize_minus_sign(x[0])))

    # Extract the formatted selection strings from the sorted list
    sorted_selections = [selection[1] for selection in selections]

    # Ensure the 'selections' folder exists
    os.makedirs('selections', exist_ok=True)

    # Write the sorted selections to a JSON file (e.g., assists_selections.json)
    output_file = f'selections/{category_name}_selections.json'
    with open(output_file, 'w') as file:
        json.dump(sorted_selections, file, indent=4)

    return sorted_selections

# List of all stat types (categories) to process
stat_types = [
    'points', 'rebounds', 'pra', 'assists', 'threes', 
    'steals', 'pa', 'pr', 'ar', 'turnovers', 'blocks', 'sb'
]

# Process each category and combine all selections
all_selections = []
for category in stat_types:
    try:
        selections = process_category(category)
        all_selections.extend(selections)
    except Exception as e:
        print(f"Error processing category '{category}': {e}")

# Sort the combined selections by the odds (from lowest to highest)
all_selections.sort(key=lambda x: int(normalize_minus_sign(x.split(", ")[-1])))

# Save the combined and sorted selections to selections.json
with open('selections/selections.json', 'w') as file:
    json.dump(all_selections, file, indent=4)

print("All selections written to selections/selections.json.")
