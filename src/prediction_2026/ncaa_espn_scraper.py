"""
NCAA Basketball Season Game Log Scraper using ESPN API
Retrieves complete season game data including records at time of each game
"""

import requests
import json
from typing import List, Dict, Optional
import time

class NCAABasketballScraper:
    """Scrape NCAA basketball data from ESPN API"""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/college-basketball"
    
    def __init__(self, delay: float = 0.5):
        """
        Initialize scraper
        Args:
            delay: Delay between requests (seconds) to be respectful to ESPN
        """
        self.delay = delay
        self.session = requests.Session()
        # Set User-Agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """
        Make HTTP request with error handling
        
        Args:
            url: URL to request
            
        Returns:
            JSON response as dict, or None if request fails
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(self.delay)  # Rate limiting
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_all_teams(self) -> Dict[str, str]:
        """
        Retrieve all NCAA basketball teams and their ESPN IDs
        
        Returns:
            Dict mapping team names to ESPN team IDs
        """
        print("Fetching all teams...")
        url = f"{self.BASE_URL}/teams"
        data = self._make_request(url)
        
        if not data or 'sports' not in data:
            print("Failed to fetch teams")
            return {}
        
        teams = {}
        for team in data['sports'][0]['leagues'][0]['teams']:
            team_name = team['team']['name']
            team_id = team['team']['id']
            teams[team_name] = team_id
        
        print(f"Found {len(teams)} teams")
        return teams
    
    def get_team_schedule(self, team_id: str) -> Optional[Dict]:
        """
        Retrieve complete schedule/game log for a team
        
        Args:
            team_id: ESPN team ID
            
        Returns:
            Dict containing team info and all games
        """
        url = f"{self.BASE_URL}/teams/{team_id}/schedule"
        return self._make_request(url)
    
    def get_box_score(self, event_id: str) -> Optional[Dict]:
        """
        Retrieve detailed box score for a specific game
        
        Args:
            event_id: ESPN event ID
            
        Returns:
            Dict containing detailed game statistics
        """
        url = f"{self.BASE_URL}/summary/{event_id}"
        return self._make_request(url)
    
    def parse_game_log(self, schedule_data: Dict) -> List[Dict]:
        """
        Parse schedule data into a list of games with relevant information
        
        Args:
            schedule_data: Raw schedule data from ESPN API
            
        Returns:
            List of games with parsed information
        """
        if not schedule_data or 'events' not in schedule_data:
            return []
        
        games = []
        team_info = schedule_data.get('team', {})
        team_name = team_info.get('displayName', 'Unknown')
        
        for event in schedule_data['events']:
            game = {}
            
            # Basic game info
            game['date'] = event.get('date', '')
            game['event_id'] = event.get('id', '')
            game['status'] = event.get('status', {}).get('type', '')
            
            # Get competitions (usually 1 per game)
            competitions = event.get('competitions', [])
            if competitions:
                comp = competitions[0]
                
                # Get teams
                teams = comp.get('competitors', [])
                if len(teams) == 2:
                    home_team = teams[0]
                    away_team = teams[1]
                    
                    # Determine if our team is home or away
                    if team_name in home_team.get('team', {}).get('displayName', ''):
                        our_team = home_team
                        opponent = away_team
                        game['location'] = 'Home'
                    else:
                        our_team = away_team
                        opponent = home_team
                        game['location'] = 'Away'
                    
                    # Team records at time of game
                    game['our_team'] = our_team.get('team', {}).get('displayName', '')
                    game['opponent'] = opponent.get('team', {}).get('displayName', '')
                    game['our_score'] = our_team.get('score', '')
                    game['opponent_score'] = opponent.get('score', '')
                    
                    # Records (if available)
                    our_record = our_team.get('records', [])
                    opp_record = opponent.get('records', [])
                    
                    if our_record:
                        game['our_wins'] = our_record[0].get('wins', '')
                        game['our_losses'] = our_record[0].get('losses', '')
                    
                    if opp_record:
                        game['opponent_wins'] = opp_record[0].get('wins', '')
                        game['opponent_losses'] = opp_record[0].get('losses', '')
                    
                    # Result
                    if game['status'] == 'STATUS_FINAL':
                        game['result'] = 'W' if int(our_team.get('score', 0)) > int(opponent.get('score', 0)) else 'L'
                    else:
                        game['result'] = '-'  # Game not played yet
                
                games.append(game)
        
        return games
    
    def get_team_season(self, team_name: str) -> Dict:
        """
        Retrieve complete season data for a team
        
        Args:
            team_name: Full team name (e.g., "Michigan Wolverines")
            
        Returns:
            Dict with team season info and all games
        """
        # Get teams list
        teams = self.get_all_teams()
        
        if team_name not in teams:
            print(f"Team '{team_name}' not found")
            return {}
        
        team_id = teams[team_name]
        print(f"\nFetching schedule for {team_name} (ID: {team_id})...")
        
        schedule_data = self.get_team_schedule(team_id)
        if not schedule_data:
            return {}
        
        games = self.parse_game_log(schedule_data)
        
        return {
            'team_name': team_name,
            'team_id': team_id,
            'games': games,
            'total_games': len(games)
        }
    
    def print_season_summary(self, season_data: Dict) -> None:
        """
        Print formatted season summary
        
        Args:
            season_data: Season data from get_team_season()
        """
        if not season_data:
            return
        
        print(f"\n{'='*80}")
        print(f"SEASON SUMMARY: {season_data['team_name']}")
        print(f"{'='*80}\n")
        
        games = season_data.get('games', [])
        
        print(f"{'Date':<12} {'Opponent':<25} {'Result':<8} {'Score':<10} {'Record':<10}")
        print("-" * 80)
        
        for game in games:
            date = game.get('date', '')[:10]  # YYYY-MM-DD format
            opponent = game.get('opponent', '')[:24]
            result = game.get('result', '-')
            score = f"{game.get('our_score', '')}-{game.get('opponent_score', '')}"
            
            # Build record string
            wins = game.get('our_wins', '?')
            losses = game.get('our_losses', '?')
            record = f"{wins}-{losses}"
            
            print(f"{date:<12} {opponent:<25} {result:<8} {score:<10} {record:<10}")
        
        print("-" * 80)
        
        # Final record
        if games:
            final_game = games[-1]
            final_wins = final_game.get('our_wins', '?')
            final_losses = final_game.get('our_losses', '?')
            print(f"\nFinal Record: {final_wins}-{final_losses}")
    
    def export_to_json(self, season_data: Dict, filename: str) -> None:
        """
        Export season data to JSON file
        
        Args:
            season_data: Season data from get_team_season()
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(season_data, f, indent=2)
        print(f"\nData exported to {filename}")


# Example usage
if __name__ == "__main__":
    # Initialize scraper
    scraper = NCAABasketballScraper(delay=0.5)
    
    # Get season data for Michigan
    season_data = scraper.get_team_season("Michigan Wolverines")
    
    # Print formatted summary
    scraper.print_season_summary(season_data)
    
    # Export to JSON
    if season_data:
        scraper.export_to_json(season_data, "michigan_season.json")
    
    # You can also query multiple teams
    print("\n" + "="*80)
    print("To get data for other teams, modify the team name:")
    print("="*80)
    print("""
    # Examples:
    season_data = scraper.get_team_season("Duke Blue Devils")
    season_data = scraper.get_team_season("Arizona Wildcats")
    season_data = scraper.get_team_season("UConn Huskies")
    """)
