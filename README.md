## NCAA tournament prediction code!
This is the code for making predictions for NCAA tournament (or any tournament for that matter).

### Results are determined through:
  1. Pull strengths for Teams A and B.
  2. Get a ratio of teams' strengths.
  3. Take logarith of the ratio (this will range from negative to positive infinity).
  4. Create logistic distribution and see the corresponding value (from 0 to 1). This is determines how likely a Team A would beat Team B (I call it cutoff).
  5. Pull a random value (uniformly distributed from 0 to 1).
  6. When random value is less than the cutoff, Team A wins. Greater, Team B wins.
  7. Update winning team's team strength by adding the adjusted factor: \
     * new_strength = random.uniform(0, (1 - strength1) * strength_change_bound)\
     where strength_change_bound = 1 - np.exp(-expon.rvs(scale = parameters.strength_change_factor))
  9. Change the bracket with the winning team and new team strength.

### Program information
* ncaa_tournament_predictions.py: Python script for the prediction code \
* ncaa_tournament_predictions.ipnyb: Jupyter script version for the code. Should be usable on Google Colab or equivalent.

### Input and output file information
* team_stats_new.csv: csv file for tournament information. \
  * Team column: Corresponds to team numbers when the tournament is in a simple tree format. (team number 0 to 63 - corresponds to NCAA's team numbers 1 to 64).
  * Team strength: It's how good you think the team is!
  * Team seed: Tournament seeding. 
* tournament_progression.csv and tournament_results.csv:
  * tournament_progression.csv: This is the raw output file. It shows matchups, teams, strengths, winning team, and adjusted team strength.
  * tournament_results.csv: More readable version of tournament_progression.csv.
