import json
import os

def extract_stat_with_american_odds(input_file, output_file):
    """
    Reads a JSON file with a list of selections and extracts for each player:
      - the stat line (from "points")
      - the American odds and true odds for the "Over" selection
      - the American odds and true odds for the "Under" selection

    The American odds string is cleaned so that any Unicode minus sign (‐)
    is replaced with a normal hyphen ("-").
    """
    # Load the JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Dictionary to accumulate each player's stats.
    player_stats = {}
    
    # Process each selection.
    for selection in data.get("selections", []):
        points = selection.get("points")
        label = selection.get("label", "").strip()  # Expect "Over" or "Under"
        true_odds = selection.get("trueOdds")
        display_odds = selection.get("displayOdds", {})
        american_odds = display_odds.get("american")
        if american_odds is not None:
            # Replace the Unicode minus sign (U+2212) with a normal hyphen.
            american_odds = american_odds.replace("\u2212", "-")
        
        # Process each participant.
        for participant in selection.get("participants", []):
            if participant.get("type") != "Player":
                continue
            name = participant.get("name")
            if not name:
                continue
            
            if name not in player_stats:
                player_stats[name] = {}
            
            # Save the stat line (points).
            if points is not None:
                if "line" in player_stats[name] and player_stats[name]["line"] != points:
                    print(f"Warning: Inconsistent line values for {name}: "
                          f"{player_stats[name]['line']} vs {points}")
                else:
                    player_stats[name]["line"] = points
            
            # Save the odds based on whether this selection is Over or Under.
            if label.lower() == "over":
                player_stats[name]["over"] = {"american": american_odds, "trueOdds": true_odds}
            elif label.lower() == "under":
                player_stats[name]["under"] = {"american": american_odds, "trueOdds": true_odds}
    
    # Convert the dictionary to a list of dictionaries for output.
    output_list = []
    for name, stats in player_stats.items():
        entry = {"name": name}
        if "line" in stats:
            entry["line"] = stats["line"]
        if "over" in stats:
            entry["over"] = stats["over"]
        if "under" in stats:
            entry["under"] = stats["under"]
        output_list.append(entry)
    
    # Ensure the 'lines' folder exists
    os.makedirs('lines', exist_ok=True)
    
    # Write the output file inside the 'lines' folder
    with open(f'lines/{output_file}', 'w') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted data for {len(output_list)} players from '{input_file}' to 'lines/{output_file}'.")

# List of all stat types to process
stat_types = [
    "points",
    "rebounds",
    "pra",
    "assists",
    "threes",
    "steals",
    "pa",
    "pr",
    "ar",
    "turnovers",
    "blocks",
    "sb"
]

# Automatically run the extraction for each stat file when this module is imported
for stat in stat_types:
    input_filename = f"data/{stat}.json"
    output_filename = f"{stat}_lines.json"
    extract_stat_with_american_odds(input_filename, output_filename)
