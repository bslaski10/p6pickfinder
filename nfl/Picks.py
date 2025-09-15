import json
import os
from itertools import combinations

# File path for selections.json (located in the "selections" folder under nfl/)
selections_file_path = os.path.join("nfl/selections", "selections.json")

# Read the selections from the JSON file
with open(selections_file_path, "r") as file:
    selections = json.load(file)

# Helper function: Convert American odds to decimal odds
def convert_to_decimal(american_odds):
    if american_odds < 0:
        return 1 + (100 / abs(american_odds))
    else:
        return 1 + (american_odds / 100)

# Function to normalize minus signs in odds strings
def normalize_minus_sign(odds_str):
    return odds_str.replace('−', '-').replace('âˆ’', '-').replace('\u00e2\u02c6\u2019', '-')

# Helper function: Calculate parlay odds (in American format) for a list of selection strings
def calculate_parlay_odds(odds_list):
    decimal_odds = [convert_to_decimal(int(normalize_minus_sign(selection.split(", ")[2]))) for selection in odds_list]
    total_decimal = 1
    for odd in decimal_odds:
        total_decimal *= odd
    if total_decimal < 2:
        parlay_american = -100 / (total_decimal - 1)
    else:
        parlay_american = (total_decimal - 1) * 100
    return round(parlay_american)

# New helper function: Get numeric implied odds as a float (percentage value with 5.66% vig applied)
def get_implied_odds_value(american_odds):
    if american_odds > 0:
        raw_prob = 100 / (american_odds + 100)
    else:
        raw_prob = abs(american_odds) / (abs(american_odds) + 100)
    return (raw_prob / 1.0566) * 100

# Sort the selections by their numeric odds (lowest odds first)
sorted_selections = sorted(selections, key=lambda x: int(normalize_minus_sign(x.split(", ")[2])))

# -----------------------------
# Generate Parlays
# -----------------------------

# Generate all unique 2-leg parlays using combinations
all_2_leg = []
for pair in combinations(sorted_selections, 2):
    legs = list(pair)

    leg_probs = [get_implied_odds_value(int(normalize_minus_sign(sel.split(", ")[2]))) / 100 for sel in legs]
    combined_prob = leg_probs[0] * leg_probs[1]

    implied_payout = 3.3
    vig_payout = 3.0

    implied_edge = ((implied_payout * combined_prob) - 1) * 100
    vig_edge = ((vig_payout * combined_prob) - 1) * 100

    all_2_leg.append({
        'parlay': legs,
        'parlay_odds': f"{calculate_parlay_odds(legs)}",
        'implied_odds': f"{combined_prob * 100:.2f}%",
        'vig_odds': f"{combined_prob * 100:.2f}%",
        'edge': f"{implied_edge:.2f}%",
        'vig_edge': f"{vig_edge:.2f}%"
    })

# Generate all unique 3-leg parlays
all_3_leg = []
for triplet in combinations(sorted_selections, 3):
    legs = list(triplet)

    leg_probs = [get_implied_odds_value(int(normalize_minus_sign(sel.split(", ")[2]))) / 100 for sel in legs]
    combined_prob = leg_probs[0] * leg_probs[1] * leg_probs[2]

    implied_payout = 6.6
    vig_payout = 6.0

    implied_edge = ((implied_payout * combined_prob) - 1) * 100
    vig_edge = ((vig_payout * combined_prob) - 1) * 100

    all_3_leg.append({
        'parlay': legs,
        'parlay_odds': f"{calculate_parlay_odds(legs)}",
        'implied_odds': f"{combined_prob * 100:.2f}%",
        'vig_odds': f"{combined_prob * 100:.2f}%",
        'edge': f"{implied_edge:.2f}%",
        'vig_edge': f"{vig_edge:.2f}%"
    })

# Sort each category by the calculated parlay odds (lowest first)
sorted_2_leg = sorted(all_2_leg, key=lambda x: int(x['parlay_odds']))
sorted_3_leg = sorted(all_3_leg, key=lambda x: int(x['parlay_odds']))

# -----------------------------
# Selection Functions with Usage Constraints
# -----------------------------

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

# -----------------------------
# Select Top Parlays with Constraints
# -----------------------------

top_10_2_leg = select_parlays(sorted_2_leg, max_individual=3, desired_number=15)
top_5_3_leg = select_3_leg_parlays(sorted_3_leg, max_individual=3, max_pair=2, desired_number=12)

# Combine the chosen parlays
final_parlays = top_10_2_leg + top_5_3_leg

# -----------------------------
# Save to picks.json
# -----------------------------

locks = {'parlays': final_parlays}
output_file_path = "nfl/picks.json"
with open(output_file_path, "w") as file:
    json.dump(locks, file, indent=4)

print(f"Top 15 two-leg parlays and top 10 three-leg parlays have been saved to {output_file_path}")
