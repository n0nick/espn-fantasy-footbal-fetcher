from espn_api.football import League
import csv
import json
import os
from datetime import datetime

# Read environment variables for league configuration
LEAGUE_ID = os.getenv('LEAGUE_ID')
ESPN_S2 = os.getenv('ESPN_S2')
SWID = os.getenv('SWID')
SEASON = 2024

if not LEAGUE_ID or not ESPN_S2 or not SWID:
    raise ValueError("LEAGUE_ID, ESPN_S2, and SWID must be set as environment variables.")

# Initialize the league
league = League(league_id=LEAGUE_ID, year=SEASON, espn_s2=ESPN_S2, swid=SWID)

# Fetch and save league standings
def fetch_standings():
    standings = []
    for team in league.teams:
        owners = [owner.get('firstName', 'Unknown') + " " + owner.get('lastName', '') for owner in team.owners]
        standings.append({
            "Team Name": team.team_name,
            "Owners": ", ".join(owners),
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
            current_week = league.current_week
            actual_points = player.stats.get(current_week, {}).get('points', 0)
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
                "Actual Points (Week)": actual_points,
            })
    save_to_csv(rosters, 'rosters.csv')
    save_to_json(rosters, 'rosters.json')
    return rosters

# Fetch and save full game logs for all players
def fetch_player_game_logs():
    game_logs = []
    for team in league.teams:
        for player in team.roster:
            if player.stats:
                for week, stats in player.stats.items():
                    game_logs.append({
                        "Team Name": team.team_name,
                        "Player Name": player.name,
                        "Week": week,
                        "Points": stats.get('points', 0),
                        "Projected Points": stats.get('projected_points', 0),
                        "Receiving Yards": stats.get('breakdown', {}).get('receivingYards', 0),
                        "Rushing Yards": stats.get('breakdown', {}).get('rushingYards', 0),
                        "Touchdowns": stats.get('breakdown', {}).get('receivingTouchdowns', 0) + stats.get('breakdown', {}).get('rushingTouchdowns', 0),
                    })
    save_to_csv(game_logs, 'player_game_logs.csv')
    save_to_json(game_logs, 'player_game_logs.json')
    return game_logs

# Fetch and save matchup schedule
def fetch_matchup_schedule():
    matchup_schedule = []
    total_weeks = league.settings.reg_season_count
    for week in range(1, total_weeks + 1):
        for matchup in league.scoreboard(week=week):
            matchup_schedule.append({
                "Week": week,
                "Home Team": matchup.home_team.team_name if matchup.home_team else "BYE",
                "Home Score": matchup.home_score if matchup.home_team else 0,
                "Away Team": matchup.away_team.team_name if matchup.away_team else "BYE",
                "Away Score": matchup.away_score if matchup.away_team else 0,
                "Winner": (
                    matchup.home_team.team_name if matchup.home_score > matchup.away_score else matchup.away_team.team_name
                ) if matchup.home_team and matchup.away_team else "N/A",
            })
    save_to_csv(matchup_schedule, 'matchup_schedule.csv')
    save_to_json(matchup_schedule, 'matchup_schedule.json')
    return matchup_schedule

# Fetch and save current matchups
def fetch_matchups():
    matchups = []
    for matchup in league.scoreboard():
        matchups.append({
            "Home Team": matchup.home_team.team_name,
            "Home Score": matchup.home_score,
            "Away Team": matchup.away_team.team_name,
            "Away Score": matchup.away_score,
            "Actual Points (Home)": matchup.home_score,  # Actual points for the home team
            "Actual Points (Away)": matchup.away_score,  # Actual points for the away team
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
            "Ownership %": player.percent_owned,
        })
    save_to_csv(waiver_players, 'waiver_wire.csv')
    save_to_json(waiver_players, 'waiver_wire.json')
    return waiver_players

# Fetch and save transaction history
def fetch_transactions():
    transactions = []
    for transaction in league.recent_activity():
        for action in transaction.actions:
            team = action[0]
            action_type = action[1]
            player = action[2]
            transactions.append({
                "Date": datetime.fromtimestamp(transaction.date / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "Team Name": team.team_name,
                "Action": action_type,
                "Player Name": player.name if hasattr(player, 'name') else str(player),
                "Waiver Rank": team.waiver_rank,
                "Acquisitions": team.acquisitions,
                "Drops": team.drops,
                "Trades": team.trades,
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

    print("Fetching full game logs...")
    fetch_player_game_logs()

    print("Fetching matchup schedule...")
    fetch_matchup_schedule()

    print("Fetching current matchups...")
    fetch_matchups()

    print("Fetching waiver wire data...")
    fetch_waiver_wire()

    print("Fetching transaction history...")
    fetch_transactions()

    print("Data saved! Check your directory for the output files.")

if __name__ == "__main__":
    main()
