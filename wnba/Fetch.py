import json
import os

def extract_stat_with_american_odds(input_file, output_file):
    """
    Reads a JSON file with selections and additional event info.
    For each player, it extracts:
      - the stat line (from "points")
      - the American odds and true odds for the "Over" and "Under" selections
      - the matchup (from the event's "name")
      - the game time (from the event's "startEventDate")
    
    The American odds string is cleaned so that any Unicode minus sign (‐)
    is replaced with a normal hyphen ("-").
    """
    # Load the JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Build a mapping from event id to its details (matchup and game time)
    event_mapping = {}
    for event in data.get("events", []):
        event_id = event.get("id")
        if event_id:
            event_mapping[event_id] = {
                "matchup": event.get("name"),
                "gameTime": event.get("startEventDate")
            }
    
    # Build a mapping from market id to event id.
    for market in data.get("markets", []):
        market_id = market.get("id")
        event_id = market.get("eventId")
        if market_id and event_id:
            # We add the event info directly to the market for lookup.
            market["eventInfo"] = event_mapping.get(event_id, {})
    
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
            american_odds = american_odds.replace("\u2212", "-")
        
        # Lookup event info using the selection's marketId.
        market_id = selection.get("marketId")
        event_info = {}
        for market in data.get("markets", []):
            if market.get("id") == market_id:
                event_info = market.get("eventInfo", {})
                break
        
        # Process each participant.
        for participant in selection.get("participants", []):
            if participant.get("type") != "Player":
                continue
            name = participant.get("name")
            if not name:
                continue
            
            if name not in player_stats:
                player_stats[name] = {}
            
            # Save the stat line.
            if points is not None:
                if "line" in player_stats[name] and player_stats[name]["line"] != points:
                    print(f"Warning: Inconsistent line values for {name}: {player_stats[name]['line']} vs {points}")
                else:
                    player_stats[name]["line"] = points
            
            # Save odds based on whether this selection is Over or Under.
            if label.lower() == "over":
                player_stats[name]["over"] = {"american": american_odds, "trueOdds": true_odds}
            elif label.lower() == "under":
                player_stats[name]["under"] = {"american": american_odds, "trueOdds": true_odds}
            
            # Add matchup and game time (if available) from the event info.
            if event_info:
                player_stats[name]["matchup"] = event_info.get("matchup")
                player_stats[name]["gameTime"] = event_info.get("gameTime")
    
    # Convert the dictionary to a list of dictionaries for output.
    output_list = []
    for name, stats in player_stats.items():
        entry = {"name": name}
        entry.update(stats)
        output_list.append(entry)
    
    # Ensure the 'wnba/lines' folder exists.
    os.makedirs('wnba/lines', exist_ok=True)
    
    # Write the output file inside the 'wnba/lines' folder.
    with open(f'wnba/lines/{output_file}', 'w') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted data for {len(output_list)} players from '{input_file}' to 'wnba/lines/{output_file}'")


# List of all wnba stat types to process.
wnba_stat_types = [
    "points",
    "rebounds",
    "pra",
    "assists",
    "threes",
]

# Automatically run the extraction for each wnba stat file when this module is imported.
for stat in wnba_stat_types:
    input_filename = f"wnba/data/{stat}.json"
    output_filename = f"{stat}_lines.json"
    extract_stat_with_american_odds(input_filename, output_filename)


