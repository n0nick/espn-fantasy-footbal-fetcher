
# ESPN Fantasy Football Data Fetcher

This script fetches data from ESPN Fantasy Football leagues and outputs it in CSV
or JSON format. It allows you to export league standings, team rosters, player
game logs, waiver wire data, matchup schedules, transactions, and more.

## Installation

1. Clone the Repository

   ```sh
   git clone https://github.com/n0nick/espn-fantasy-football-fetcher.git
   cd espn-fantasy-football-fetcher
   ```

2. Create a Python Virtual Environment

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Dependencies

   ```sh
   pip3 install -r requirements.txt
   ```

## Environment Variables

Set the following environment variables for your league configuration:

- `LEAGUE_ID`: Your league's ID.
- `ESPN_S2`: The `espn_s2` cookie value from your ESPN session.
- `SWID`: The `swid` cookie value from your ESPN session.

See https://github.com/cwendt94/espn-api/discussions/150 for advice on acquiring
`ESPN_S2` and `SWID`.

### Example:

```sh
export LEAGUE_ID=123456
export ESPN_S2="your-espn-s2-cookie"
export SWID="{your-swid-cookie}"
```

## Usage

### Basic Command

```bash
python3 fetcher.py --export-all
```

### Available Flags

#### Output Options

| Flag       | Description                                      | Default |
| ---------- | ------------------------------------------------ | ------- |
| `--format` | Specify output format: `csv` or `json`.          | `csv`   |
| `--out`    | Specify output directory for the exported files. | `dist/` |

#### Export Options

| Flag                        | Description                                           |
| --------------------------- | ----------------------------------------------------- |
| `--export-all`              | Fetch all available data (combines all export flags). |
| `--export-standings`        | Fetch league standings.                               |
| `--export-rosters`          | Fetch team rosters.                                   |
| `--export-game-logs`        | Fetch game logs for all players.                      |
| `--export-transactions`     | Fetch transaction history.                            |
| `--export-matchup-schedule` | Fetch the full league matchup schedule.               |
| `--export-matchups`         | Fetch matchups for the current week.                  |
| `--export-waiver`           | Fetch waiver wire data for available players.         |

### Examples

```sh
# Export Everything (Default Directory)
python3 fetcher.py --export-all

# Export Data in JSON Format
python3 fetcher.py --export-all --format json

# Export Specific Files
python3 fetcher.py --export-standings --export-waiver --format csv --out exports/

# View Help
python3 fetcher.py --help
```

## Output Files

The script generates the following files in the specified output directory:

| File                        | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| `standings.csv/json`        | League standings, including team names, records, and points. |
| `rosters.csv/json`          | Team rosters, including player stats and projections.        |
| `game_logs.csv/json`        | Weekly game stats for all players.                           |
| `matchup_schedule.csv/json` | Full schedule with team matchups by week.                    |
| `matchups.csv/json`         | Current week’s matchups and scores.                          |
| `transactions.csv/json`     | Recent transactions in the league (e.g., adds, drops).       |
| `waiver_wire.csv/json`      | List of available players on the waiver wire.                |

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
