# -*- coding: utf-8 -*-

import pandas as pd
import random
from itertools import combinations

def score_group(group, tee_data):
    """
    Calculates a homogeneity score for a group based on tee boxes.
    More players with the same tee box = higher score.
    """
    if len(group) <= 1: return 0

    tees = [tee_data[player] for player in group]
    # Count how many pairs in the group share the same tee
    score = sum(1 for a, b in combinations(tees, 2) if a == b)
    return score

def is_valid_group(group, avoid_rules):
    """
    Checks if a group violates any 'Avoid' constraints.
    avoid_rules is a dict: {player: [list of players to avoid]}
    """
    for player in group:
        if player in avoid_rules:
            # If anyone they are supposed to avoid is in the same group, it's invalid
            if any(avoid_player in group for avoid_player in avoid_rules[player]):
                return False
    return True

def generate_optimal_pairings(df, group_sizes=None, iterations=5000, prioritize_tees=True):
    """
    Generates random groupings, filters out those that break the rules,
    and returns the one that best satisfies the tee box preferences.
    """
    # 1. Extract Data
    players = df['Player'].tolist()
    tee_data = dict(zip(df['Player'], df['Tee']))

    # Build avoid rules dictionary
    avoid_rules = {}
    for _, row in df.iterrows():
        if pd.notna(row.get('Avoid')):
            avoids = [name.strip() for name in str(row['Avoid']).split(',')]
            avoid_rules[row['Player']] = avoids

    total_players = len(players)

    # 2. Handle Group Sizes
    if group_sizes is None:
        full_groups = total_players // 4
        remainder = total_players % 4
        group_sizes = [4] * full_groups
        if remainder > 0:
            group_sizes.append(remainder)

    if sum(group_sizes) != total_players:
        raise ValueError(f"Group sizes {group_sizes} do not sum to total players ({total_players})")

    # 3. Stochastic Search
    best_layout = None
    best_score = -1

    for _ in range(iterations):
        shuffled = players.copy()
        random.shuffle(shuffled)

        # Chunk into groups
        current_layout = []
        start = 0
        for size in group_sizes:
            current_layout.append(shuffled[start:start+size])
            start += size

        # Hard Constraint Check: Do any groups violate the avoid rules?
        if not all(is_valid_group(g, avoid_rules) for g in current_layout):
            continue # Skip this permutation, it's invalid

        # Soft Constraint Check: Score the layout based on tee boxes
        if prioritize_tees:
            layout_score = sum(score_group(g, tee_data) for g in current_layout)
        else:
            # If not prioritizing tees, the first valid random layout is a winner
            layout_score = 1

        # Update best
        if layout_score > best_score:
            best_score = layout_score
            best_layout = current_layout

        # Early exit if we hit a perfectly homogenous layout (optional optimization)
        # For a standard 12 player (3x4) setup, max score per foursome is 6. Max total = 18.
        if prioritize_tees and best_score >= sum(len(g)*(len(g)-1)/2 for g in current_layout):
            break

    if best_layout is None:
        raise RuntimeError("Could not find a valid grouping. Your 'Avoid' constraints might be too strict!")

    return best_layout, best_score


    # --- Execution ---
if __name__ == "__main__":
    # Make sure the filename matches exactly what you uploaded
    try:
        df = pd.read_excel('roster.xlsx')
    except FileNotFoundError:
        print("Error: Could not find 'roster.xlsx'. Make sure it is uploaded to the Colab session storage!")
        exit()

    # Filter for only active players
    active_df = df[df['Playing'] == 1]

    try:
        # Toggles:
        CUSTOM_SIZES = None # e.g., [4, 4, 4] or None for standard foursomes
        PRIORITIZE_TEES = True

        # 3. Run the optimization function
        final_groups, score = generate_optimal_pairings(
            active_df,
            group_sizes=CUSTOM_SIZES,
            prioritize_tees=PRIORITIZE_TEES
        )

        # Print the results
        print("\n THIS WEEK'S TEE TIMES \n")
        for i, group in enumerate(final_groups, 1):
            # Fetch tee boxes for display
            group_with_tees = [f"{p} ({df.loc[df['Player']==p, 'Tee'].values[0]})" for p in group]
            print(f"Group {i}: {', '.join(group_with_tees)}")

    except Exception as e:
        print(f"Error: {e}")
