## This is the code for making predictions for NCAA tournament (or any tournament for that matter)

# Program information
ncaa_tournament_predictions.py: Python script for the prediction code
ncaa_tournament_predictions.ipnyb: Jupyter script version for the code. 
  Should be usable on Google Colab or equivalent.

# Input and output file information
team_stats_new.csv: csv file for tournament information. 
  Team column: Corresponds to team numbers when the tournament is in a simple tree format. 
    (team number 0 to 63 - corresponds to NCAA's team numbers 1 to 64).
  Team strength: It's how good you think the team is!
  Team seed: Tournament seeding. 
tournament_progression.csv and tournament_results.csv:
  tournament_progression.csv: This is the raw output file. It shows matchups, teams, strengths,
    winning team, and adjusted team strength.
  tournament_results.csv: More readable version of tournament_progression.csv.

# Work in progress
Note that outputs of the tournament are saved as tensors. If I have spare time, I might build a 
  simple deep learning artificial neural network to make predictions. It would be very interesting 
  to see how well it would work for Sweet 16 if first two round results are used to refine the
  neural network!
