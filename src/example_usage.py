“””
Simple Example: How to Use the NCAA Basketball Scraper

This example shows basic usage patterns for retrieving team season data.
“””

from ncaa_espn_scraper import NCAABasketballScraper
import pandas as pd  # Optional: for data analysis

# ============================================================================

# BASIC USAGE

# ============================================================================

# 1. Initialize the scraper

scraper = NCAABasketballScraper(delay=0.5)  # 0.5 second delay between requests

# 2. Get season data for a single team

print(“Getting Michigan’s season data…”)
michigan_season = scraper.get_team_season(“Michigan Wolverines”)

# 3. Print formatted summary

scraper.print_season_summary(michigan_season)

# 4. Export to JSON for later analysis

scraper.export_to_json(michigan_season, “michigan_2026.json”)

# ============================================================================

# MULTIPLE TEAMS

# ============================================================================

teams_to_fetch = [
“Michigan Wolverines”,
“Duke Blue Devils”,
“Arizona Wildcats”
]

all_seasons = {}
for team_name in teams_to_fetch:
print(f”\nFetching {team_name}…”)
season_data = scraper.get_team_season(team_name)
all_seasons[team_name] = season_data
scraper.print_season_summary(season_data)

# ============================================================================

# ACCESSING SPECIFIC GAME DATA

# ============================================================================

if michigan_season.get(‘games’):
games = michigan_season[‘games’]

```
# Get first game of season
first_game = games[0]
print(f"\nFirst game: {first_game['our_team']} vs {first_game['opponent']}")
print(f"Score: {first_game['our_score']}-{first_game['opponent_score']}")
print(f"Record at time: {first_game['our_wins']}-{first_game['our_losses']}")

# Get last game of season
last_game = games[-1]
print(f"\nLast game: {last_game['our_team']} vs {last_game['opponent']}")
print(f"Final Record: {last_game['our_wins']}-{last_game['our_losses']}")

# Count wins and losses
wins = sum(1 for g in games if g.get('result') == 'W')
losses = sum(1 for g in games if g.get('result') == 'L')
print(f"\nSeason Record: {wins}-{losses}")
```

# ============================================================================

# WORKING WITH PANDAS (Optional)

# ============================================================================

try:
import pandas as pd

```
if michigan_season.get('games'):
    # Convert to DataFrame for easy analysis
    df = pd.DataFrame(michigan_season['games'])
    
    # Summary statistics
    print("\n" + "="*80)
    print("STATISTICAL SUMMARY")
    print("="*80)
    
    # Wins vs Losses
    result_counts = df['result'].value_counts()
    print(f"\nWins: {result_counts.get('W', 0)}")
    print(f"Losses: {result_counts.get('L', 0)}")
    
    # Average score
    df['our_score_int'] = pd.to_numeric(df['our_score'], errors='coerce')
    df['opponent_score_int'] = pd.to_numeric(df['opponent_score'], errors='coerce')
    
    print(f"\nAverage points scored: {df['our_score_int'].mean():.1f}")
    print(f"Average points allowed: {df['opponent_score_int'].mean():.1f}")
    
    # Home vs Away record
    home_record = df[df['location'] == 'Home']
    away_record = df[df['location'] == 'Away']
    
    home_wins = (home_record['result'] == 'W').sum()
    away_wins = (away_record['result'] == 'W').sum()
    
    print(f"\nHome record: {home_wins}-{len(home_record) - home_wins}")
    print(f"Away record: {away_wins}-{len(away_record) - away_wins}")
    
    # Save to CSV
    df.to_csv('michigan_games.csv', index=False)
    print("\nData exported to michigan_games.csv")
```

except ImportError:
print(”\nNote: Install pandas for advanced analysis:”)
print(“pip install pandas”)

# ============================================================================

# ERROR HANDLING

# ============================================================================

# If team name is incorrect, check available teams

if not michigan_season:
print(“Team not found. Getting list of available teams…”)
teams = scraper.get_all_teams()
print(“Available teams:”)
for team_name in sorted(teams.keys())[:10]:  # Show first 10
print(f”  - {team_name}”)