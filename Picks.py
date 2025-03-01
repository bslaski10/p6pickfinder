import json
import os
from itertools import combinations

# File path for selections.json (located in the "selections" folder)
selections_file_path = os.path.join("selections", "selections.json")

# Read the selections from the JSON file
with open(selections_file_path, "r") as file:
    selections = json.load(file)

# Helper function: Convert American odds to decimal odds
def convert_to_decimal(american_odds):
    # For negative American odds, use: 1 + (100 / abs(odds))
    # For positive odds, use: 1 + (odds / 100)
    if american_odds < 0:
        return 1 + (100 / abs(american_odds))
    else:
        return 1 + (american_odds / 100)

# Function to normalize minus signs in odds strings
def normalize_minus_sign(odds_str):
    return odds_str.replace('−', '-').replace('âˆ’', '-').replace('\u00e2\u02c6\u2019', '-')

# Helper function: Calculate parlay odds (in American format) for a list of selection strings
def calculate_parlay_odds(odds_list):
    # Convert each selection's American odds (assumed to be the 3rd element when splitting by ", ") to decimal odds.
    decimal_odds = [convert_to_decimal(int(normalize_minus_sign(selection.split(", ")[2]))) for selection in odds_list]
    total_decimal = 1
    for odd in decimal_odds:
        total_decimal *= odd
    # Convert total decimal odds back to American odds:
    if total_decimal < 2:
        parlay_american = -100 / (total_decimal - 1)
    else:
        parlay_american = (total_decimal - 1) * 100
    return round(parlay_american)

# Helper function: Calculate implied odds (as a percentage string) from American odds.
def calculate_implied_odds(american_odds):
    # For positive odds: implied probability = 100/(odds+100)
    # For negative odds: implied probability = abs(odds)/(abs(odds)+100)
    if american_odds > 0:
        probability = 100 / (american_odds + 100)
    else:
        probability = abs(american_odds) / (abs(american_odds) + 100)
    return f"{probability * 100:.2f}%"

# New helper function: Get numeric implied odds as a float (percentage value)
def get_implied_odds_value(american_odds):
    if american_odds > 0:
        probability = 100 / (american_odds + 100)
    else:
        probability = abs(american_odds) / (abs(american_odds) + 100)
    return probability * 100

# Sort the selections by their numeric odds (lowest odds first)
# (Assumes selection string format: "Name, type, odds, matchup, game time")
sorted_selections = sorted(selections, key=lambda x: int(normalize_minus_sign(x.split(", ")[2])))

# -----------------------------
# Generate Parlays
# -----------------------------

# Generate all unique 2-leg parlays using combinations
all_2_leg = []
for pair in combinations(sorted_selections, 2):
    legs = list(pair)
    parlay_odds = calculate_parlay_odds(legs)
    implied_value = get_implied_odds_value(parlay_odds)
    vig_odds = implied_value / 1.0698
    edge = implied_value - 33.33  # For 2-leg parlays, subtract 33.33
    vig_edge = vig_odds - 33.33  # vig_edge for 2-leg parlays
    all_2_leg.append({
        'parlay': legs,
        'parlay_odds': f"{int(parlay_odds)}",
        'implied_odds': f"{implied_value:.2f}%",
        'vig_odds': f"{vig_odds:.2f}%",
        'edge': f"{edge:.2f}%",
        'vig_edge': f"{vig_edge:.2f}%"  # Include vig_edge in the result
    })

# Generate all unique 3-leg parlays
all_3_leg = []
for triplet in combinations(sorted_selections, 3):
    legs = list(triplet)
    parlay_odds = calculate_parlay_odds(legs)
    implied_value = get_implied_odds_value(parlay_odds)
    vig_odds = implied_value / 1.0698
    edge = implied_value - 20  # For 3-leg parlays, subtract 20
    vig_edge = vig_odds - 20  # vig_edge for 3-leg parlays
    all_3_leg.append({
        'parlay': legs,
        'parlay_odds': f"{int(parlay_odds)}",
        'implied_odds': f"{implied_value:.2f}%",
        'vig_odds': f"{vig_odds:.2f}%",
        'edge': f"{edge:.2f}%",
        'vig_edge': f"{vig_edge:.2f}%"  # Include vig_edge in the result
    })

# Sort each category by the calculated parlay odds (lowest first)
sorted_2_leg = sorted(all_2_leg, key=lambda x: int(x['parlay_odds']))
sorted_3_leg = sorted(all_3_leg, key=lambda x: int(x['parlay_odds']))

# -----------------------------
# Selection Functions with Usage Constraints
# -----------------------------

def select_parlays(sorted_parlays, max_individual, desired_number):
    """
    For 2-leg parlays: ensures no individual selection (full line) is used more than max_individual times.
    """
    usage = {}  # counts individual selection usage
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
    """
    For 3-leg parlays:
      - No individual selection may appear more than max_individual times.
      - Any given pair of selections (order insensitive) may appear together in at most max_pair parlays.
    """
    usage = {}       # individual usage counts
    pair_usage = {}  # counts for each pair (represented as a sorted tuple)
    selected = []
    for parlay in sorted_parlays:
        legs = parlay['parlay']
        can_add = True
        # Check individual usage
        for sel in legs:
            if usage.get(sel, 0) >= max_individual:
                can_add = False
                break
        if not can_add:
            continue
        # Get all pairs from this 3-leg parlay
        pairs = [tuple(sorted([legs[i], legs[j]])) for i in range(len(legs)) for j in range(i+1, len(legs))]
        for pair in pairs:
            if pair_usage.get(pair, 0) >= max_pair:
                can_add = False
                break
        if can_add:
            selected.append(parlay)
            # Update individual usage
            for sel in legs:
                usage[sel] = usage.get(sel, 0) + 1
            # Update pair usage
            for pair in pairs:
                pair_usage[pair] = pair_usage.get(pair, 0) + 1
        if len(selected) == desired_number:
            break
    return selected

# -----------------------------
# Select Top Parlays with Constraints
# -----------------------------

# For 2-leg parlays, allow each selection up to 3 times.
top_10_2_leg = select_parlays(sorted_2_leg, max_individual=3, desired_number=15)

# For 3-leg parlays, allow each selection up to 3 times and any pair together up to 2 times.
top_5_3_leg = select_3_leg_parlays(sorted_3_leg, max_individual=3, max_pair=2, desired_number=12)

# Combine the chosen parlays
final_parlays = top_10_2_leg + top_5_3_leg

# -----------------------------
# Save to picks.json
# -----------------------------

locks = {'parlays': final_parlays}
output_file_path = "picks.json"
with open(output_file_path, "w") as file:
    json.dump(locks, file, indent=4)

print(f"Top 15 two-leg parlays and top 10 three-leg parlays have been saved to {output_file_path}")
