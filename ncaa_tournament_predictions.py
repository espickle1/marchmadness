# %%
# import libraries
import pandas as pd
import numpy as np
import random
from scipy.stats import logistic

# %%
# Define tournament and simulation stats
class TournamentParameters:
    def __init__(self, rounds, strength_change, logistics_mu, logistics_sigma, tournament_output_path, tournament_output_friendly_path):
        self.rounds = rounds
        self.strength_change = strength_change
        self.logistics_mu = logistics_mu
        self.logistics_sigma = logistics_sigma
        self.tournament_output_path = tournament_output_path
        self.tournament_output_friendly_path = tournament_output_friendly_path

# %%
# Simulate individual games
def simulate_game(team1, team2, strength1, strength2):

    # Normalize team strengths
    strength_norm1 = strength1 / (strength1 + strength2) + 0.00001
    strength_norm2 = strength2 / (strength1 + strength2) + 0.00001

    # Calculate strength proportions
    strength_proportion_1 = abs(strength_norm1 - strength_norm2) / strength_norm1
    strength_proportion_2 = abs(strength_norm1 - strength_norm2) / strength_norm2

    # Generate random outcome cut off and determine cutoff point for winner
    strength_proportion = strength_norm1 / strength_norm2
    strength_log_transform = np.log10(strength_proportion)
    outcome_cutoff = logistic.cdf(
        strength_log_transform, 
        loc=parameters.logistics_mu, 
        scale=parameters.logistics_sigma
        )
    strength_change_game = random.uniform(0, parameters.strength_change)

    # Determine winner
    outcome = random.random()
    if outcome <= outcome_cutoff:
        winner = team1
        new_strength = strength1 + (strength_proportion_1 * strength_change_game * strength1)
    else:
        winner = team2
        new_strength = strength2 + (strength_proportion_2 * strength_change_game * strength2)
    
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
    tournament_progression.append(pd.DataFrame
                                (matchups, 
                                columns=[
                                    "Team1", "Team2", 
                                    "Strength1", "Strength2", 
                                    "Winner", 
                                    "NewStrength"]))

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
        'Winner_name', 
        'NewStrength']
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

# Load team data, set tournament parameters, and minmax normalize team strengths
teams = pd.read_csv('/home/azureuser/cloudfiles/code/giggles/team_stats_new.csv')
parameters = TournamentParameters(
    rounds = [64, 32, 16, 8, 4, 2, 1],
    strength_change = 0.2,
    logistics_mu = 0,
    logistics_sigma = 0.1,
    tournament_output_path = "/home/azureuser/cloudfiles/code/giggles/tournament_progression.csv",
    tournament_output_friendly_path = "/home/azureuser/cloudfiles/code/giggles/tournament_results.csv"
    )
team_strengths = (teams['Strength'] - teams['Strength'].min()) / (teams['Strength'].max() - teams['Strength'].min())

# Simulate the tournament!
tournament_progression, champion, champion_name, champion_strength = simulate_tournament(team_strengths)
print(f"\n🏆 The champion is {champion_name} (Team {champion}) with a final strength of {champion_strength:.2f}")


