import argparse
import os
from espn_api.football import League
import csv
import json
from datetime import datetime

SEASON = 2024

# Save data to the specified output format
def save_data(data, filename, output_format, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{filename}.{output_format}")
    if output_format == "json":
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    elif output_format == "csv":
        if not data:
            print(f"No data to save for {filename}.")
            return
        keys = data[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    return filepath

# Initialize the league only when needed
def initialize_league():
    league_id = os.getenv('LEAGUE_ID')
    espn_s2 = os.getenv('ESPN_S2')
    swid = os.getenv('SWID')
    if not league_id or not espn_s2 or not swid:
        raise ValueError("LEAGUE_ID, ESPN_S2, and SWID must be set as environment variables.")
    return League(league_id=league_id, year=SEASON, espn_s2=espn_s2, swid=swid)

# Fetch and save league standings
def fetch_standings(league, output_format, output_dir):
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
    save_data(standings, 'standings', output_format, output_dir)

# Fetch and save rosters
def fetch_rosters(league, output_format, output_dir):
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
    save_data(rosters, 'rosters', output_format, output_dir)

# Fetch and save player game logs
def fetch_game_logs(league, output_format, output_dir):
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
    save_data(game_logs, 'player_game_logs', output_format, output_dir)

# Fetch and save matchup schedule
def fetch_matchup_schedule(league, output_format, output_dir):
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
    save_data(matchup_schedule, 'matchup_schedule', output_format, output_dir)

# Fetch and save current matchups
def fetch_matchups(league, output_format, output_dir):
    matchups = []
    for matchup in league.scoreboard():
        matchups.append({
            "Home Team": matchup.home_team.team_name,
            "Home Score": matchup.home_score,
            "Away Team": matchup.away_team.team_name,
            "Away Score": matchup.away_score,
            "Matchup Period": league.current_week,
        })
    save_data(matchups, 'matchups', output_format, output_dir)

# Fetch and save waiver wire players
def fetch_waiver_wire(league, output_format, output_dir):
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
    save_data(waiver_players, 'waiver_wire', output_format, output_dir)

# Fetch and save transaction history
def fetch_transactions(league, output_format, output_dir):
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
    save_data(transactions, 'transactions', output_format, output_dir)

# Main execution
def main():
    parser = argparse.ArgumentParser(description="Fetch ESPN Fantasy Football Data")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Output format: csv or json")
    parser.add_argument("--out", default="dist/", help="Output directory")
    parser.add_argument("--export-all", action="store_true", help="Fetch all data")
    parser.add_argument("--export-standings", action="store_true", help="Fetch standings")
    parser.add_argument("--export-rosters", action="store_true", help="Fetch rosters")
    parser.add_argument("--export-game-logs", action="store_true", help="Fetch player game logs")
    parser.add_argument("--export-transactions", action="store_true", help="Fetch transaction history")
    parser.add_argument("--export-matchup-schedule", action="store_true", help="Fetch matchup schedule")
    parser.add_argument("--export-matchups", action="store_true", help="Fetch current matchups")
    parser.add_argument("--export-waiver", action="store_true", help="Fetch waiver wire data")

    args = parser.parse_args()

    if not any([
        args.export_all,
        args.export_standings,
        args.export_rosters,
        args.export_game_logs,
        args.export_transactions,
        args.export_matchup_schedule,
        args.export_matchups,
        args.export_waiver,
    ]):
        parser.error("No export flag provided. Use --export-all or specific --export-* flags.")

    league = initialize_league()

    if args.export_all or args.export_standings:
        print("Fetching league standings...")
        fetch_standings(league, args.format, args.out)

    if args.export_all or args.export_rosters:
        print("Fetching rosters...")
        fetch_rosters(league, args.format, args.out)

    if args.export_all or args.export_game_logs:
        print("Fetching game logs...")
        fetch_game_logs(league, args.format, args.out)

    if args.export_all or args.export_transactions:
        print("Fetching transactions...")
        fetch_transactions(league, args.format, args.out)

    if args.export_all or args.export_matchup_schedule:
        print("Fetching matchup schedule...")
        fetch_matchup_schedule(league, args.format, args.out)

    if args.export_all or args.export_matchups:
        print("Fetching current matchups...")
        fetch_matchups(league, args.format, args.out)

    if args.export_all or args.export_waiver:
        print("Fetching waiver wire data...")
        fetch_waiver_wire(league, args.format, args.out)

    print(f"Data saved! Check your directory: {args.out}")

if __name__ == "__main__":
    main()
