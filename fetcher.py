from espn_api.football import League
import csv
import json
from datetime import datetime

# Replace with your ESPN Fantasy credentials
LEAGUE_ID = 'YOUR_LEAGUE_ID'
SEASON = 2024
ESPN_S2 = 'YOUR_ESPN_S2_COOKIE'
SWID = 'YOUR_SWID_COOKIE'

# Initialize the league
league = League(league_id=LEAGUE_ID, year=SEASON, espn_s2=ESPN_S2, swid=SWID)

# Fetch and save league standings
def fetch_standings():
    standings = []
    for team in league.teams:
        # Extract owner names from the list of dictionaries
        owners = [owner.get('firstName', 'Unknown') + " " + owner.get('lastName', '') for owner in team.owners]
        standings.append({
            "Team Name": team.team_name,
            "Owners": ", ".join(owners),  # Join owner names into a single string
            "Wins": team.wins,
            "Losses": team.losses,
            "Points For": team.points_for,
            "Points Against": team.points_against,
            "Streak": team.streak_length,
        })
    save_to_csv(standings, 'standings.csv')
    save_to_json(standings, 'standings.json')
    return standings

# Fetch and save rosters
def fetch_rosters():
    rosters = []
    for team in league.teams:
        for player in team.roster:
            # Fetch actual points for the current week, if available
            current_week = league.current_week
            actual_points = player.stats.get(current_week, {}).get('points', 0)  # Defaults to 0 if no data

            rosters.append({
                "Team Name": team.team_name,
                "Player Name": player.name,
                "Position": player.position,
                "Lineup Slot": player.lineupSlot,
                "Team": player.proTeam,
                "Status": player.injuryStatus,
                "Total Points (Season)": player.total_points,
                "Average Points (Season)": player.avg_points,
                "Projected Points (Week)": player.projected_avg_points,
                "Actual Points (Week)": actual_points,  # New actual points data
            })
    save_to_csv(rosters, 'rosters.csv')
    save_to_json(rosters, 'rosters.json')
    return rosters

# Fetch and save matchups for the current week
def fetch_matchups():
    matchups = []
    for matchup in league.scoreboard():
        matchups.append({
            "Home Team": matchup.home_team.team_name,
            "Home Score": matchup.home_score,
            "Away Team": matchup.away_team.team_name,
            "Away Score": matchup.away_score,
            "Matchup Period": league.current_week,
        })
    save_to_csv(matchups, 'matchups.csv')
    save_to_json(matchups, 'matchups.json')
    return matchups

# Fetch and save waiver wire players
def fetch_waiver_wire():
    waiver_players = []
    for player in league.free_agents():
        waiver_players.append({
            "Player Name": player.name,
            "Position": player.position,
            "Team": player.proTeam,
            "Status": player.injuryStatus,
            "Projected Points": player.projected_avg_points,
            "Actual Points": player.points,
            "Ownership %": player.percent_owned,
        })
    save_to_csv(waiver_players, 'waiver_wire.csv')
    save_to_json(waiver_players, 'waiver_wire.json')
    return waiver_players

# Fetch and save transaction history
def fetch_transactions():
    transactions = []
    for transaction in league.recent_activity():
        transactions.append({
            "Type": transaction.type,
            "Player Name": transaction.playerName,
            "Team": transaction.proTeam,
            "From Team": transaction.fromTeam,
            "To Team": transaction.toTeam,
            "Timestamp": datetime.fromtimestamp(transaction.date / 1000).strftime('%Y-%m-%d %H:%M:%S'),
        })
    save_to_csv(transactions, 'transactions.csv')
    save_to_json(transactions, 'transactions.json')
    return transactions

# Save data to CSV
def save_to_csv(data, filename):
    if not data:
        print(f"No data to save for {filename}.")
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Save data to JSON
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Main execution
def main():
    print("Fetching league standings...")
    fetch_standings()
    
    print("Fetching rosters...")
    fetch_rosters()
    
    print("Fetching current matchups...")
    fetch_matchups()
    
    print("Fetching waiver wire data...")
    fetch_waiver_wire()
    
    print("Fetching transaction history...")
    fetch_transactions()
    
    print("Data saved! Check your directory for the output files.")

if __name__ == "__main__":
    main()
