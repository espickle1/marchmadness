ESPN API NCAA Basketball Scraper - Complete Guide
====================================================

## Overview

This guide explains how to use the NCAABasketballScraper class to retrieve complete season game logs for NCAA Division I basketball teams, including game-by-game records.

## What You Get

For each team and season, you can retrieve:
- ✓ Complete game-by-game log
- ✓ Final score for each game
- ✓ Win/loss record at time of EACH game
- ✓ Home/Away designation
- ✓ Opponent information
- ✓ Final season record
- ✓ Game dates and status

## Installation & Setup

### Requirements
```bash
pip install requests
pip install pandas  # Optional, for data analysis
```

### Basic Setup
```python
from ncaa_espn_scraper import NCAABasketballScraper

# Create scraper instance
scraper = NCAABasketballScraper(delay=0.5)
# delay: seconds between requests (be respectful to ESPN)
```

## Usage Examples

### 1. Get Season Data for One Team
```python
season_data = scraper.get_team_season("Michigan Wolverines")
scraper.print_season_summary(season_data)
```

Output format:
```
Date       Opponent              Result   Score      Record
2025-11-05 Northern Arizona      W        85-62      1-0
2025-11-08 Marshall              W        92-71      2-0
2025-11-10 Miami                 W        70-65      3-0
...
```

### 2. Access Individual Game Data
```python
games = season_data['games']

# Access first game
first_game = games[0]
print(f"Opponent: {first_game['opponent']}")
print(f"Score: {first_game['our_score']}-{first_game['opponent_score']}")
print(f"Record: {first_game['our_wins']}-{first_game['our_losses']}")
print(f"Home/Away: {first_game['location']}")
```

### 3. Get List of All Teams
```python
all_teams = scraper.get_all_teams()

# Search for a team
for team_name, team_id in all_teams.items():
    if "North Carolina" in team_name:
        print(f"{team_name}: {team_id}")

# Output:
# North Carolina Tar Heels: 25
# North Carolina State Wolfpack: 152
```

### 4. Fetch Multiple Teams
```python
teams_list = [
    "Duke Blue Devils",
    "Arizona Wildcats",
    "UConn Huskies",
    "Gonzaga Bulldogs"
]

results = {}
for team in teams_list:
    results[team] = scraper.get_team_season(team)
    scraper.print_season_summary(results[team])
```

### 5. Export Data to JSON
```python
scraper.export_to_json(season_data, "michigan_2026.json")
```

### 6. Analyze with Pandas (Optional)
```python
import pandas as pd

# Convert games to DataFrame
df = pd.DataFrame(season_data['games'])

# Win percentage
win_pct = (df['result'] == 'W').sum() / len(df)
print(f"Win percentage: {win_pct:.1%}")

# Home vs Away splits
home_df = df[df['location'] == 'Home']
away_df = df[df['location'] == 'Away']

print(f"Home record: {(home_df['result'] == 'W').sum()}-{(home_df['result'] == 'L').sum()}")
print(f"Away record: {(away_df['result'] == 'W').sum()}-{(away_df['result'] == 'L').sum()}")

# Average scoring
df['our_score_int'] = pd.to_numeric(df['our_score'], errors='coerce')
print(f"Points per game: {df['our_score_int'].mean():.1f}")

# Save to CSV
df.to_csv('season_games.csv', index=False)
```

## Data Structure

### Season Data Dictionary
```python
{
    'team_name': 'Michigan Wolverines',
    'team_id': '130',
    'total_games': 38,
    'games': [
        {
            'date': '2025-11-05T00:00Z',
            'event_id': 'abc123...',
            'status': 'STATUS_FINAL',
            'location': 'Home',           # or 'Away'
            'our_team': 'Michigan Wolverines',
            'opponent': 'Northern Arizona',
            'our_score': '85',
            'opponent_score': '62',
            'our_wins': 1,                # Record AT TIME OF GAME
            'our_losses': 0,
            'opponent_wins': 0,
            'opponent_losses': 1,
            'result': 'W'                 # or 'L' or '-' (not played)
        },
        # ... more games
    ]
}
```

## Common Queries

### Find All Games Where Team Was Undefeated
```python
undefeated_games = [g for g in season_data['games'] 
                    if g['our_losses'] == 0]
print(f"Games while undefeated: {len(undefeated_games)}")
```

### Find Longest Win Streak
```python
games = season_data['games']
max_streak = current_streak = 0

for game in games:
    if game['result'] == 'W':
        current_streak += 1
        max_streak = max(max_streak, current_streak)
    else:
        current_streak = 0

print(f"Longest win streak: {max_streak}")
```

### Compare Records Before/After a Specific Date
```python
import datetime

cutoff_date = datetime.datetime(2026, 1, 1)
before = [g for g in games if datetime.datetime.fromisoformat(g['date']) < cutoff_date]
after = [g for g in games if datetime.datetime.fromisoformat(g['date']) >= cutoff_date]

print(f"Record before Jan 1: {before[-1]['our_wins']}-{before[-1]['our_losses']}")
print(f"Record after Jan 1: {after[-1]['our_wins']}-{after[-1]['our_losses']}")
```

### Find Biggest Wins/Losses
```python
games = season_data['games']

# Convert scores to integers
for g in games:
    if g['our_score'] and g['opponent_score']:
        g['margin'] = int(g['our_score']) - int(g['opponent_score'])

# Biggest win
biggest_win = max(games, key=lambda x: x.get('margin', 0))
print(f"Biggest win: vs {biggest_win['opponent']} by {biggest_win['margin']}")

# Biggest loss
biggest_loss = min(games, key=lambda x: x.get('margin', 0))
print(f"Biggest loss: vs {biggest_loss['opponent']} by {abs(biggest_loss['margin'])}")
```

## Important Notes

### Rate Limiting
- The scraper uses a 0.5-second delay between requests by default
- ESPN's terms don't explicitly forbid scraping, but be respectful
- Adjust delay if needed: `NCAABasketballScraper(delay=1.0)`

### Data Availability
- Current season data is most reliable
- Historical data varies (some years may have incomplete records)
- Games not yet played have status='STATUS_SCHEDULED' and no score

### ESPN API Stability
- ESPN doesn't officially document their API
- Structure is generally stable but could change
- If the scraper breaks, the API response format likely changed

### Team Name Format
- Must use ESPN's official team names
- Examples: "Michigan Wolverines", "Duke Blue Devils", "Arizona Wildcats"
- Use `get_all_teams()` to find correct names

## Troubleshooting

### "Team not found"
```python
# Get list of available teams
teams = scraper.get_all_teams()
for name in sorted(teams.keys()):
    print(name)
# Find the exact name format
```

### Empty game list
- Team may not have data available for that season
- Try checking `season_data['total_games']`
- Verify team name is correct

### No records in game data
- Records sometimes aren't available in ESPN API responses
- This is a limitation of the API, not the scraper
- Try querying a different team or season

### Network timeout
- Increase timeout in `_make_request()`: `timeout=20`
- Increase delay: `NCAABasketballScraper(delay=1.0)`

## Advanced: Custom Analysis

### Create Comparison Report
```python
teams = ["Duke Blue Devils", "Michigan Wolverines", "Arizona Wildcats"]
comparison = {}

for team in teams:
    season = scraper.get_team_season(team)
    games = season['games']
    
    if games:
        final = games[-1]
        wins = final['our_wins']
        losses = final['our_losses']
        
        comparison[team] = {
            'record': f"{wins}-{losses}",
            'games_played': len(games),
            'avg_score': sum(int(g['our_score']) for g in games if g['our_score']) / len(games)
        }

for team, stats in comparison.items():
    print(f"{team}: {stats['record']} ({stats['avg_score']:.1f} ppg)")
```

## License & Disclaimer

- This scraper accesses publicly available ESPN data
- Use responsibly and respect rate limits
- ESPN's terms of service may restrict commercial use
- Not affiliated with ESPN or the NCAA
