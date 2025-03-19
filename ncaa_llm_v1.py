# %%
# import libraries
import pandas as pd
import numpy as np
import random

import torch
from scipy.stats import logistic, expon

# %%
# Define tournament and simulation stats
class TournamentParameters:
    def __init__(self, rounds, strength_change_factor, 
                 logistics_mu, logistics_sigma, 
                 tournament_input_path, tournament_output_path, tournament_output_friendly_path):
        self.rounds = rounds
        self.strength_change_factor = strength_change_factor
        self.logistics_mu = logistics_mu
        self.logistics_sigma = logistics_sigma
        self.tournament_input_path = tournament_input_path
        self.tournament_output_path = tournament_output_path
        self.tournament_output_friendly_path = tournament_output_friendly_path

# %%
# Simulate individual games
def simulate_game(team1, team2, strength1, strength2):

    # Normalize team strengths
    if strength1 == 0:
        strength1 = 0.000001
    if strength2 == 0:
        strength2 = 0.000001
    strength_norm1 = strength1   / (strength1 + strength2)
    strength_norm2 = strength2 / (strength1 + strength2)

    # Generate random outcome cut off and determine cutoff point for winner
    strength_proportion = strength_norm1 / strength_norm2
    strength_log_transform = np.log10(strength_proportion)
    outcome_cutoff = logistic.cdf(
        strength_log_transform, 
        loc=parameters.logistics_mu, 
        scale=parameters.logistics_sigma
        )
    
    # Adjust strength change factors
    strength_change_bound = 1 - np.exp(-expon.rvs(scale = parameters.strength_change_factor))

    # Determine winner
    outcome = random.random()
    if outcome <= outcome_cutoff:
        winner = team1
        strength_increase = random.uniform(0, (1 - strength1) * strength_change_bound)
        new_strength = strength1 + strength_increase
    else:
        winner = team2
        strength_increase = random.uniform(0, (1 - strength2) * strength_change_bound)
        new_strength = strength2 + strength_increase
    
    return winner, new_strength

# %%
# Simulate each round of the tournament
def simulate_round(current_teams, team_strengths, tournament_progression):
    next_round_teams = []
    next_round_strengths = {}

    # Itemrate through each games in the round
    matchups = []
    for i in range(0, len(current_teams), 2):
        # Determine each matchup and get their strengths
        team1, team2 = current_teams[i], current_teams[i + 1]
        strength1, strength2 = team_strengths[team1], team_strengths[team2]

        # Simulate the game and add results
        winner, new_strength = simulate_game(
            team1, team2, 
            strength1, strength2
            )
        next_round_teams.append(winner)
        next_round_strengths[winner] = new_strength

        matchups.append(
            [team1, team2, 
                strength1, strength2, 
                winner, 
                new_strength]
        )

    # Store match results
    tournament_progression.append(pd.DataFrame(matchups, columns=[
        "Team1", "Team2", 
        "Strength1", "Strength2", 
        "Winner", "NewStrength"])
        )

    # Move to next round
    current_teams = next_round_teams
    team_strengths = next_round_strengths

    return current_teams, team_strengths, tournament_progression

# %%
# Save the tournament results
def save_results(tournament_progression):
    # Convert results into dataframe
    final_results_df = pd.concat(
        tournament_progression, 
        keys=parameters.rounds[:-1]
        )

    # Results in more user friendly format
    final_results_df['Round'] = final_results_df.index
    team_name_mapping = teams.set_index('Team')['Team Name'].to_dict()
    final_results_df[['Team1_name', 'Team2_name', 'Winner_name']] = final_results_df[
        ['Team1', 'Team2', 'Winner']].apply(
            lambda col: col.map(team_name_mapping)
            )
    final_results_tournament = final_results_df[
        ['Team1_name', 
        'Strength1', 'Team2_name', 
        'Strength2', 
        'Winner_name', 'NewStrength']
        ]
    final_results_tournament = final_results_tournament.reset_index(drop=True)

    # Save results to csv
    final_results_df.to_csv(parameters.tournament_output_path, index=False)
    final_results_tournament.to_csv(parameters.tournament_output_friendly_path, index=False)

    return

# %%
# Simulate the tournament
def simulate_tournament(team_strengths):
    current_teams = list(team_strengths.keys())
    tournament_progression = []

    for _ in parameters.rounds[:-1]:
        current_teams, team_strengths, tournament_progression = simulate_round(
            current_teams, 
            team_strengths, 
            tournament_progression
            )

    # Champion
    champion = current_teams[0]
    champion_name = teams.loc[current_teams[0], 'Team Name']
    champion_strength = team_strengths[champion]
    save_results(tournament_progression)

    return tournament_progression, champion, champion_name, champion_strength

# %%
# Run the tournament
# Set tournament parameters
parameters = TournamentParameters(
    rounds = [64, 32, 16, 8, 4, 2, 1],
    strength_change_factor = 0.8,
    logistics_mu = 0,
    logistics_sigma = 0.01,
    tournament_input_path = "/home/azureuser/cloudfiles/code/giggles/team_stats_new.csv",
    tournament_output_path = "/home/azureuser/cloudfiles/code/giggles/tournament_progression.csv",
    tournament_output_friendly_path = "/home/azureuser/cloudfiles/code/giggles/tournament_results.csv"
    )

# Load team data and minmax normalize team strengths
teams = pd.read_csv(parameters.tournament_input_path)
team_strengths = (teams['Strength'] - teams['Strength'].min()) / (teams['Strength'].max() - teams['Strength'].min())

# Simulate the tournament!
tournament_runs = []

for _ in range(16):
    # Each run of tournament
    tournament_progression, champion, champion_name, champion_strength = simulate_tournament(team_strengths)
    print(f"🏆 The champion is {champion_name} (Team {champion}) with a final strength of {champion_strength:.2f}")

    # Convert tournament dataframe to NumPy and then to Tensor
    results_array = pd.concat(tournament_progression).to_numpy(dtype=np.float32)
    results_tensor = torch.tensor(results_array)
    tournament_runs.append(results_tensor)

# Stack all tensors into a single tensor and save tensor
tournament_tensor = torch.stack(tournament_runs)
output_tensor_path = "/home/azureuser/cloudfiles/code/giggles/tournament_tensor.pt"
torch.save(tournament_tensor, output_tensor_path)


