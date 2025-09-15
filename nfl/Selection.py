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

# --- Name normalization helpers (ignore Jr/Sr/etc) ---

_SUFFIXES = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "v"}

def _strip_punct(s: str) -> str:
    # remove periods/commas/apostrophes; normalize spaces
    return " ".join(
        s.replace(".", " ")
         .replace(",", " ")
         .replace("’", "")
         .replace("'", "")
         .split()
    )

def _split_first_last(name: str):
    """
    Returns (first, last_block) from a name string after punctuation cleanup.
    Accepts 'First Last' and 'Last First' when a comma existed originally.
    """
    raw = name.strip()
    if "," in raw:
        # Preserve info about comma positioning before we strip punctuation
        parts = [p for p in raw.split(",") if p.strip()]
        if len(parts) >= 2:
            last_raw = parts[0].strip()
            first_raw = parts[1].strip()
            cleaned = _strip_punct(f"{first_raw} {last_raw}")
            toks = cleaned.split()
            if len(toks) >= 2:
                return toks[0], " ".join(toks[1:])
    # Default path: assume 'First ... Last'
    cleaned = _strip_punct(raw)
    toks = cleaned.split()
    if not toks:
        return "", ""
    if len(toks) == 1:
        return toks[0], ""
    return toks[0], " ".join(toks[1:])

def _drop_suffixes(first: str, last_block: str):
    # Remove any suffix tokens at the end of last_block
    if not last_block:
        return first, last_block
    toks = last_block.split()
    while toks and toks[-1].lower() in _SUFFIXES:
        toks.pop()
    return first, " ".join(toks)

def _name_variants_ignore_suffixes(full_name: str):
    """
    Given any name string, produce a set of normalized keys that IGNORE suffixes,
    compare in lowercase, and allow 'First Last' and 'F Last' matches.
    """
    if not full_name:
        return set()
    # Keep a copy to detect comma style before stripping
    first, last_block = _split_first_last(full_name)
    first, last_block = _drop_suffixes(first, last_block)

    # If no last name, still provide the single token
    variants = set()
    if not first and not last_block:
        return variants

    def norm(s: str) -> str:
        # remove periods/commas/apostrophes (already handled) just lowercase + collapse spaces
        return " ".join(s.split()).lower()

    if last_block:
        variants.add(norm(f"{first} {last_block}"))          # "First Last"
        variants.add(norm(f"{first[:1]} {last_block}"))      # "F Last"
        variants.add(norm(f"{first[:1]}. {last_block}"))     # "F. Last"
    else:
        variants.add(norm(first))

    return variants

# Backward compatible helper you had (kept, but now unused by matching)
def full_to_initial_last(full_name: str) -> str:
    if not full_name:
        return ""
    name = full_name.replace(",", " ").strip()
    parts = [p for p in name.split() if p]
    if not parts:
        return ""
    first = parts[0]
    tail = parts[1:]
    # drop suffixes from tail
    while tail and tail[-1].rstrip(".").lower() in _SUFFIXES:
        tail.pop()
    last_block = " ".join(tail).strip() or first
    return f"{first[0]}." + f" {last_block}"

def normalize_name_key(s: str) -> str:
    # Keep for simple cases; our main matching uses _name_variants_ignore_suffixes
    return " ".join(_strip_punct(s).split()).lower()

# --- Core processing ---

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

    # Build a set of ALL normalized variants from options (ignoring suffixes)
    options_norm = set()
    if isinstance(options_data, list):
        for x in options_data:
            if isinstance(x, str):
                options_norm |= _name_variants_ignore_suffixes(x)
            elif x is not None:
                options_norm |= _name_variants_ignore_suffixes(str(x))
    else:
        # dict or other iterable – best effort
        try:
            for x in options_data:
                options_norm |= _name_variants_ignore_suffixes(str(x))
        except Exception:
            pass

    selections = []

    for player in lines_data:
        full_name = (player.get('name') or '').strip()
        if not full_name:
            continue

        player_keys = _name_variants_ignore_suffixes(full_name)

        # Match if ANY variant intersects with options set
        if not player_keys or player_keys.isdisjoint(options_norm):
            continue

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
