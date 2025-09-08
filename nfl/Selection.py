import json
import os
from datetime import datetime
import pytz

def normalize_minus_sign(odds: str) -> str:
    return odds.replace('−', '-').replace('âˆ’', '-').replace('\u00e2\u02c6\u2019', '-')

def convert_to_est(utc_time_str: str) -> str:
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

_SUFFIXES = {"Jr", "Jr.", "Sr", "Sr.", "II", "III", "IV", "V"}

def full_to_initial_last(full_name: str) -> str:
    if not full_name:
        return ""
    name = full_name.replace(",", " ").strip()
    parts = [p for p in name.split() if p]
    if not parts:
        return ""
    first = parts[0]
    tail = parts[1:]
    while tail and tail[-1] in _SUFFIXES:
        tail.pop()
    last_block = " ".join(tail).strip() or first
    return f"{first[0]}." + f" {last_block}"

def normalize_name_key(s: str) -> str:
    return " ".join(s.replace(".", "").split()).lower()

def process_category(category_name: str):
    lines_file = f'nfl/lines/{category_name}_lines.json'
    options_file = f'nfl/options/{category_name}_options.json'

    if not os.path.exists(lines_file) or not os.path.exists(options_file):
        print(f"Skipping {category_name}: Missing data file.")
        return []

    with open(lines_file, 'r') as file:
        lines_data = json.load(file)

    with open(options_file, 'r') as file:
        options_data = json.load(file)

    if isinstance(options_data, list):
        options_norm = set(normalize_name_key(x) for x in options_data if isinstance(x, str))
    else:
        try:
            options_norm = set(normalize_name_key(str(x)) for x in options_data)
        except Exception:
            options_norm = set()

    selections = []

    for player in lines_data:
        full_name = player.get('name', '').strip()
        if not full_name:
            continue

        cand_full = normalize_name_key(full_name)
        cand_init_last = normalize_name_key(full_to_initial_last(full_name))

        if (cand_full in options_norm) or (cand_init_last in options_norm):
            over_amer = normalize_minus_sign(str(player['over']['american']))
            under_amer = normalize_minus_sign(str(player['under']['american']))
            try:
                over_odds = int(over_amer)
                under_odds = int(under_amer)
            except ValueError:
                continue

            if over_odds < under_odds:
                selected_type = 'over'
                selected_odds = over_amer
            else:
                selected_type = 'under'
                selected_odds = under_amer

            selected_line = f"{player['line']} {category_name.replace('_', ' ').capitalize()}"
            matchup = player.get('matchup', 'N/A')
            game_time = convert_to_est(player.get('gameTime', ''))
            selection_str = f"{full_name}, {selected_type} {selected_line}, {normalize_minus_sign(selected_odds)}, {matchup}, {game_time}"
            selections.append((selected_odds, selection_str))

    selections.sort(key=lambda x: int(normalize_minus_sign(str(x[0]))))
    return [selection[1] for selection in selections]

nfl_stat_types = [
    "passing_yards",
    "rushing_yards",
    "receiving_yards",
    "passing_TDs",
    "receptions",
    "completions",
    "passing_attempts",
    "rushing_attempts",
    "interceptions",
    "kicking_points",
    "tackles",
    "tackles+assists",
    "field_goals"
]

all_selections = []
for category in nfl_stat_types:
    try:
        selections = process_category(category)
        all_selections.extend(selections)
    except Exception as e:
        print(f"Error processing category '{category}': {e}")

all_selections.sort(key=lambda x: int(normalize_minus_sign(x.split(", ")[2])))

os.makedirs('nfl/selections', exist_ok=True)
with open('nfl/selections/selections.json', 'w') as file:
    json.dump(all_selections, file, indent=4)

print("All NFL selections written to nfl/selections/selections.json.")
