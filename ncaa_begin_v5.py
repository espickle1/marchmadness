# %%
import numpy as np
import pandas as pd

import torch
import random

# %%
# Load the team information and strengths
teams = pd.read_csv('/home/azureuser/cloudfiles/code/giggles/team_stats.csv')
team_strengths = teams['Strength']

# Number of teams
num_teams = 64

# Store tournament progression
tournament_progression = []

# %%
def simulate_game(team1, team2, strength1, strength2):
    """
    Simulates a game between two teams and returns the winner and updated strengths.
    """
    # Normalize strengths
    strength_norm1 = strength1 / (strength1 + strength2)
    strength_norm2 = strength2 / (strength1 + strength2)

    # Generate random outcome
    outcome = random.random()

    # Determine winner
    if outcome <= strength_norm1:
        winner, new_strength = team1, strength1 + 0.02
    else:
        winner, new_strength = team2, strength2 + 0.02

    return winner, new_strength

# %%
# Tournament rounds: 64 → 32 → 16 → 8 → 4 → 2 → 1
rounds = [64, 32, 16, 8, 4, 2, 1]
current_teams = list(team_strengths.keys())

for rnd in rounds[:-1]:  # Skip the last "champion" round
    next_round_teams = []
    next_round_strengths = {}

    matchups = []
    for i in range(0, len(current_teams), 2):
        team1, team2 = current_teams[i], current_teams[i + 1]
        strength1, strength2 = team_strengths[team1], team_strengths[team2]

        winner, new_strength = simulate_game(team1, team2, strength1, strength2)
        next_round_teams.append(winner)
        next_round_strengths[winner] = new_strength

        matchups.append([team1, team2, strength1, strength2, winner, new_strength])

    # Store match results
    tournament_progression.append(pd.DataFrame(matchups, columns=["Team1", "Team2", "Strength1", "Strength2", "Winner", "NewStrength"]))

    # Move to next round
    current_teams = next_round_teams
    team_strengths = next_round_strengths

# %%
# Champion
champion = current_teams[0]
champion_strength = team_strengths[champion]

print(f"\n🏆 The champion is Team {champion} with a final strength of {champion_strength:.2f}")

# Save results as DataFrame
final_results_df = pd.concat(tournament_progression, keys=rounds[:-1])
final_results_df.to_csv("/home/azureuser/cloudfiles/code/giggles/tournament_progression.csv", index=False)