import json
import os
from itertools import combinations
from datetime import datetime

# File path for selections.json (located in the "selections" folder)
selections_file_path = os.path.join("selections", "selections.json")

# Read the selections from the JSON file
with open(selections_file_path, "r") as file:
    selections = json.load(file)

# Record the current time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Save the execution time to time.json
time_data = {"execution_time": current_time}
with open("selections/time.json", "w") as time_file:
    json.dump(time_data, time_file, indent=4)

print(f"Execution time saved to time.json: {current_time}")

# Helper function: Convert American odds to decimal odds
def convert_to_decimal(american_odds):
    if american_odds < 0:
        return 1 + (100 / abs(american_odds))
    else:
        return 1 + (american_odds / 100)

# Helper function: Calculate parlay odds (in American format) for a list of selection strings
def calculate_parlay_odds(odds_list):
    decimal_odds = [convert_to_decimal(int(selection.split()[-1])) for selection in odds_list]
    total_decimal = 1
    for odd in decimal_odds:
        total_decimal *= odd
    if total_decimal < 2:
        parlay_american = -100 / (total_decimal - 1)
    else:
        parlay_american = (total_decimal - 1) * 100
    return round(parlay_american)

# Helper function: Get numeric implied odds as a float
def get_implied_odds_value(american_odds):
    if american_odds > 0:
        probability = 100 / (american_odds + 100)
    else:
        probability = abs(american_odds) / (abs(american_odds) + 100)
    return probability * 100

# Sort the selections by their numeric odds (lowest odds first)
sorted_selections = sorted(selections, key=lambda x: int(x.split()[-1].replace('-', '')))

# Generate all unique 2-leg parlays using combinations
all_2_leg = []
for pair in combinations(sorted_selections, 2):
    legs = list(pair)
    parlay_odds = calculate_parlay_odds(legs)
    implied_value = get_implied_odds_value(parlay_odds)
    vig_odds = implied_value / 1.0698
    edge = implied_value - 33.33
    vig_edge = vig_odds - 33.33
    all_2_leg.append({
        'parlay': legs,
        'parlay_odds': f"{int(parlay_odds)}",
        'implied_odds': f"{implied_value:.2f}%",
        'vig_odds': f"{vig_odds:.2f}%",
        'edge': f"{edge:.2f}%",
        'vig_edge': f"{vig_edge:.2f}%"
    })

# Generate all unique 3-leg parlays
all_3_leg = []
for triplet in combinations(sorted_selections, 3):
    legs = list(triplet)
    parlay_odds = calculate_parlay_odds(legs)
    implied_value = get_implied_odds_value(parlay_odds)
    vig_odds = implied_value / 1.0698
    edge = implied_value - 20
    vig_edge = vig_odds - 20
    all_3_leg.append({
        'parlay': legs,
        'parlay_odds': f"{int(parlay_odds)}",
        'implied_odds': f"{implied_value:.2f}%",
        'vig_odds': f"{vig_odds:.2f}%",
        'edge': f"{edge:.2f}%",
        'vig_edge': f"{vig_edge:.2f}%"
    })

sorted_2_leg = sorted(all_2_leg, key=lambda x: int(x['parlay_odds']))
sorted_3_leg = sorted(all_3_leg, key=lambda x: int(x['parlay_odds']))

def select_parlays(sorted_parlays, max_individual, desired_number):
    usage = {}
    selected = []
    for parlay in sorted_parlays:
        can_add = True
        for sel in parlay['parlay']:
            if usage.get(sel, 0) >= max_individual:
                can_add = False
                break
        if can_add:
            selected.append(parlay)
            for sel in parlay['parlay']:
                usage[sel] = usage.get(sel, 0) + 1
        if len(selected) == desired_number:
            break
    return selected

def select_3_leg_parlays(sorted_parlays, max_individual, max_pair, desired_number):
    usage = {}
    pair_usage = {}
    selected = []
    for parlay in sorted_parlays:
        legs = parlay['parlay']
        can_add = True
        for sel in legs:
            if usage.get(sel, 0) >= max_individual:
                can_add = False
                break
        if not can_add:
            continue
        pairs = [tuple(sorted([legs[i], legs[j]])) for i in range(len(legs)) for j in range(i+1, len(legs))]
        for pair in pairs:
            if pair_usage.get(pair, 0) >= max_pair:
                can_add = False
                break
        if can_add:
            selected.append(parlay)
            for sel in legs:
                usage[sel] = usage.get(sel, 0) + 1
            for pair in pairs:
                pair_usage[pair] = pair_usage.get(pair, 0) + 1
        if len(selected) == desired_number:
            break
    return selected

top_10_2_leg = select_parlays(sorted_2_leg, max_individual=3, desired_number=15)
top_5_3_leg = select_3_leg_parlays(sorted_3_leg, max_individual=3, max_pair=2, desired_number=10)

final_parlays = top_10_2_leg + top_5_3_leg

locks = {'parlays': final_parlays}
output_file_path = "picks.json"
with open(output_file_path, "w") as file:
    json.dump(locks, file, indent=4)

print(f"Top 15 two-leg parlays and top 10 three-leg parlays have been saved to {output_file_path}")
