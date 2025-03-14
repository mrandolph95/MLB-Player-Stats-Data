import requests
import pandas as pd
import datetime as dt
import yaml
import time

"""## Extract, Process, and Transform the Data"""



with open("mlb_config.yaml", "r") as file:
    userdata = yaml.safe_load(file)

MLB_API = userdata.get('MLB_API')


Dodgers_Team_ID = 1
Dodgers_Team_Key = "LAD"

"""### Dodgers Team Roster"""


class DodgersRoster:
    def __init__(self, api_key):
        self.api_key = MLB_API

    def get_roster(self):
        roster_url = f"https://api.sportsdata.io/v3/mlb/scores/json/PlayersBasic/LAD?key={self.api_key}"
        roster_response = requests.get(roster_url)
        roster_data = roster_response.json()

        dodgers_players = []

        for player in roster_data:
            dodgers_players.append({
                "Status": player["Status"],
                "Player ID": player["PlayerID"],
                "First Name": player["FirstName"],
                "Last Name": player["LastName"],
                "Birth Date": player["BirthDate"],
                "Birth Country": player["BirthCountry"],
                "Height": player["Height"],
                "Weight": player["Weight"],
                "Jersey": player["Jersey"],
                "Position": player["Position"],
                "Bat Hand": player["BatHand"],
                "Throw Hand": player["ThrowHand"]
            })

        return self.modify_roster(dodgers_players)

    def modify_roster(self, dodgers_players):
        dodgers_players = pd.DataFrame(dodgers_players)

        dodgers_players["Birth Date"] = pd.to_datetime(dodgers_players["Birth Date"])
        today = dt.date.today()

        # Generate age of the players
        dodgers_players["Age"] = dodgers_players["Birth Date"].apply(
            lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)) if pd.notnull(x) else pd.NA
        ).astype("Int64")

        # Convert Jersey number from float to integer
        dodgers_players["Jersey"] = dodgers_players["Jersey"].astype("Int64")

        dodgers_players.rename(columns={"Jersey": "Jersey Number"}, inplace=True)

        # Convert the players height from inches to feet
        dodgers_players["Height"] = dodgers_players["Height"].apply(
            lambda x: f"{x // 12}'{x % 12}\"" if pd.notnull(x) else pd.NA
        )

        # Drop players from the dataset who are not active
        dodgers_players = dodgers_players[dodgers_players["Status"] == "Active"]

        # Reorder columns
        dodgers_players = dodgers_players[
            ["Status", "Player ID", "First Name", "Last Name", "Age", "Birth Country", "Height", "Weight", "Jersey Number", "Position", "Bat Hand", "Throw Hand"]
        ]

        return dodgers_players

dodgers_roster = DodgersRoster(api_key=MLB_API)
dodgers_players = dodgers_roster.get_roster()

print(dodgers_players.head())



"""### Dodgers Games Played in 2024"""


class DodgersGames:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_games(self):
        last_season_url = f"https://api.sportsdata.io/v3/mlb/scores/json/Games/2024?key={self.api_key}"
        last_season_response = requests.get(last_season_url)
        last_season_data = last_season_response.json()

        dodgers_last_season = []

        for game_stats in last_season_data:
            dodgers_last_season.append({
                "Game ID": game_stats["GameID"],
                "Game Date": game_stats["GameEndDateTime"],
                "Pitching Team ID": game_stats["CurrentPitchingTeamID"],
                "Hitting Team ID": game_stats["CurrentHittingTeamID"],
                "Low Temp": game_stats["ForecastTempLow"],
                "High Temp": game_stats["ForecastTempHigh"],
                "Wind Chill": game_stats["ForecastWindChill"],
                "Wind Speed": game_stats["ForecastWindSpeed"],
                "Wind Direction": game_stats["ForecastWindDirection"]
            })

        return self.modify_games(dodgers_last_season)

    def modify_games(self, dodgers_last_season):
        dodgers_last_season = pd.DataFrame(dodgers_last_season)

        # Use Dodgers_Team_ID defined elsewhere
        global Dodgers_Team_ID  # Ensure it is accessible if defined elsewhere in your environment

        # Filter the DataFrame for games involving the Dodgers
        dodgers_last_season = dodgers_last_season[
            (dodgers_last_season["Pitching Team ID"] == Dodgers_Team_ID) |
            (dodgers_last_season["Hitting Team ID"] == Dodgers_Team_ID)
        ]

        # Format the Game Date
        dodgers_last_season["Game Date"] = pd.to_datetime(dodgers_last_season["Game Date"]).dt.strftime("%m-%d-%Y")

        # Convert weather data columns to integer
        dodgers_last_season[["Low Temp", "High Temp", "Wind Chill", "Wind Speed", "Wind Direction"]] = dodgers_last_season[[
            "Low Temp", "High Temp", "Wind Chill", "Wind Speed", "Wind Direction"]].astype(int)

        # Reset index
        dodgers_last_season = dodgers_last_season.reset_index(drop=True)

        return dodgers_last_season

games_played = DodgersGames(api_key=MLB_API)
dodgers_last_season = games_played.get_games()

print(dodgers_last_season.head())


"""### Box Scores"""


class DodgersBoxScores:

  def __init__(self, api_key):
    self.api_key = api_key

  def get_box_scores(self):
    all_box_scores = []

    for index, row in dodgers_last_season.iterrows():
      game_id = row['Game ID']
      box_scores_url = f"https://api.sportsdata.io/v3/mlb/stats/json/BoxScoreFinal/{game_id}?key={self.api_key}"

      box_scores_response = requests.get(box_scores_url)

      if box_scores_response.status_code == 200:
          box_scores_data = box_scores_response.json()
          all_box_scores.append(box_scores_data)

      time.sleep(1)

    return self.modify_box_scores(all_box_scores)

  def modify_box_scores(self, all_box_scores):

    team_box_scores = []

    for box_scores_data in all_box_scores:
      if "PlayerGames" in box_scores_data:
          player_games = box_scores_data["PlayerGames"]

          for box_scores in player_games:
            team_box_scores.append({
                "Game ID": box_scores.get("GameID"),
                "Player ID": box_scores.get("PlayerID"),
                "Name": box_scores.get("Name"),
                "At Bats": box_scores.get("AtBats"),
                "Hits": box_scores.get("Hits"),
                "Home Runs": box_scores.get("HomeRuns"),
                "RBI": box_scores.get("RunsBattedIn"),
                "Walks": box_scores.get("Walks"),
                "Strikeouts": box_scores.get("Strikeouts"),
                "Doubles": box_scores.get("Doubles"),
                "Triples": box_scores.get("Triples"),
                "Earned Runs": box_scores.get("PitchingEarnedRuns"),
                "Innings Pitched": box_scores.get("InningsPitchedFull"),
                "Pitching Strikeouts": box_scores.get("PitchingStrikeouts"),
                "Pitching Walks": box_scores.get("PitchingWalks")
              })


    box_scores = pd.DataFrame(team_box_scores)

    return box_scores

box_scores = DodgersBoxScores(api_key=MLB_API)
box_scores = box_scores.get_box_scores()
dodgers_box_scores = box_scores.merge(dodgers_players[["Player ID"]], on="Player ID", how="inner")

print(dodgers_box_scores.head())

"""## Calculate Player Stats"""


class PlayerStatsCalculator:

    def __init__(self, df):
        self.df = df
        self.dodgers_player_stats = self.group_players()

    def group_players(self):
        # Group by Player ID and aggregate stats
        return self.df.groupby("Player ID").agg({
            "At Bats": "sum",
            "Hits": "sum",
            "Home Runs": "sum",
            "RBI": "sum",
            "Walks": "sum",
            "Strikeouts": "sum",
            "Doubles": "sum",
            "Triples": "sum",
            "Earned Runs": "sum",
            "Innings Pitched": "sum",
            "Pitching Strikeouts": "sum",
            "Pitching Walks": "sum"
        }).reset_index()

    def calculate_stats(self):
        # Handling division by zero gracefully
        self.dodgers_player_stats["Batting Average"] = (
            self.dodgers_player_stats["Hits"] / self.dodgers_player_stats["At Bats"]
        ).fillna(0).replace([float('inf'), float('-inf')], 0).round(3)

        # Calculate Slugging Percentage
        self.dodgers_player_stats["Slugging Percentage"] = (
            (self.dodgers_player_stats["Hits"] - self.dodgers_player_stats["Doubles"] -
             self.dodgers_player_stats["Triples"] - self.dodgers_player_stats["Home Runs"]) +
            (2 * self.dodgers_player_stats["Doubles"]) +
            (3 * self.dodgers_player_stats["Triples"]) +
            (4 * self.dodgers_player_stats["Home Runs"])
        ) / self.dodgers_player_stats["At Bats"]
        self.dodgers_player_stats["Slugging Percentage"] = (
            self.dodgers_player_stats["Slugging Percentage"]
        ).fillna(0).replace([float('inf'), float('-inf')], 0).round(3)

        # Calculate On-Base Percentage
        self.dodgers_player_stats["On-Base Percentage"] = (
            (self.dodgers_player_stats["Hits"] + self.dodgers_player_stats["Walks"]) /
            (self.dodgers_player_stats["At Bats"] + self.dodgers_player_stats["Walks"])
        ).fillna(0).replace([float('inf'), float('-inf')], 0).round(3)

        # Calculate OPS
        self.dodgers_player_stats["OPS"] = (
            self.dodgers_player_stats["On-Base Percentage"] + self.dodgers_player_stats["Slugging Percentage"]
        )

        # Calculate ERA for pitchers
        self.dodgers_player_stats["ERA"] = (
            (self.dodgers_player_stats["Earned Runs"] * 9) / self.dodgers_player_stats["Innings Pitched"]
        ).fillna(0).replace([float('inf'), float('-inf')], 0).round(2)

        # Returning the final stats
        return self.dodgers_player_stats

calculator = PlayerStatsCalculator(dodgers_box_scores)
dodgers_players_stats = calculator.calculate_stats()

print(dodgers_players_stats.head())


"""## Add Data to Database"""


import psycopg2
from sqlalchemy import create_engine

with open("postgre_config.yaml", "r") as file:
    usernamedata = yaml.safe_load(file)

username = usernamedata.get('username')
password = usernamedata.get('password')
host = usernamedata.get('host')

connection_string = f'postgresql+psycopg2://{username}:{password}@{host}:5432/mlb_data'
engine = create_engine(connection_string)

dodgers_players.to_sql("LA_Dodgers_Roster", engine, if_exists='replace', index=False)
dodgers_last_season.to_sql("LA_Dodgers_Games_Played_2024", engine, if_exists='replace', index=False)
dodgers_box_scores.to_sql("LA_Dodgers_Box_Scores", engine, if_exists='replace', index=False)
dodgers_players_stats.to_sql("LA_Dodgers_Team_Stats", engine, if_exists='replace', index=False)

