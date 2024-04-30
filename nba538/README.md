# NBA Game and Player Statistics Scraper

This project scrapes NBA game and player statistics data from the Basketball Reference website. It retrieves data for a specified range of years and teams, and saves the data as CSV files in a structured directory format.

## Features

- Scrapes NBA game data including dates, teams, scores, box score links, and more.
- Scrapes individual player statistics for each game, including basic and advanced stats.
- Saves data in a structured directory format organized by year and team.
- Supports data retrieval for multiple NBA seasons and teams.

## Requirements

- Python 3.x
- Required libraries: `requests`, `beautifulsoup4`, `pandas`

## Installation

Clone the repository:
```bash
git clone https://github.com/your-username/nba-stats-scraper.git
Install the required libraries:

bash
Copy code
pip install -r requirements.txt
Usage
Open the scraper.py file in a text editor.
Modify the start_year, end_year, and nba_teams variables according to your requirements:
start_year: The starting year for data retrieval (inclusive)
end_year: The ending year for data retrieval (inclusive)
nba_teams: A list of NBA team abbreviations to scrape data for
Run the script:
bash
Copy code
python scraper.py
The script will start scraping data for the specified years and teams. Progress messages will be displayed in the console.
Once the scraping process is complete, the data will be saved as CSV files in the following directory structure:
plaintext
Copy code
year/
  team/
    team_year_games.csv
    game_date/
      player_stats.csv
year: The year of the NBA season
team: The abbreviation of the NBA team
team_year_games.csv: CSV file containing game data for the team in the specified year
game_date: The date of the specific game
player_stats.csv: CSV file containing player statistics for the specific game
Data Structure
The scraped data is saved in two types of CSV files:

team_year_games.csv
Contains game-level data for a team in a specific year
Columns: Game, Date, Start Time, Network, Visitor/Neutral, Visitor Points, Home/Neutral, Home Points, Box Score Link, Arena, Game Result, Overtime, Team Points, Opponent Points, Wins, Losses, Game Streak, Notes
player_stats.csv
Contains player statistics for a specific game
Columns: Team, Player, MP, FG, FGA, FG%, 3P, 3PA, 3P%, FT, FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, +/-, TS%, eFG%, 3PAr, FTr, ORB%, DRB%, TRB%, AST%, STL%, BLK%, TOV%, USG%, ORtg, DRtg, BPM


player_stats.csv:

Contains player statistics for a specific game
Columns: Team, Player, MP, FG, FGA, FG%, 3P, 3PA, 3P%, FT, FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, +/-, TS%, eFG%, 3PAr, FTr, ORB%, DRB%, TRB%, AST%, STL%, BLK%, TOV%, USG%, ORtg, DRtg, BPM
