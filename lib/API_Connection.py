"""
Library for connecting to sports APIs for live updates
=======================================================================================

This library utilizes Adafruit libraries to send requests to the NBA API, process the returned JSON data,
format time information, and determine whether a game is current or scheduled for the future. Based on these
decisions, it invokes appropriate functions from the draw_tools library.

Author(s): Michael Ladderbush
"""

import wifi
import socketpool
import ssl
import adafruit_requests
from draw_tools import draw_future_game

# Initialize HTTP request support with SSL.
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

# NBA scoreboard API endpoint URL.
NBA_SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

def fetch_celtics_game():
    try:
        response = requests.get(NBA_SCOREBOARD_URL)
        data = response.json()
        response.close()

        # Retrieve the list of games from the JSON response.
        games = data.get("scoreboard", {}).get("games", [])
        for game in games:
            game_id = game["gameId"]
            home_team = game["homeTeam"]["teamName"]
            away_team = game["awayTeam"]["teamName"]

            # Check if either team is the Celtics.
            if home_team == "Celtics":
                home_score, away_score, clock = get_scoreboard(game_id)
                return home_score, away_score, away_team, clock

            if away_team == "Celtics":
                home_score, away_score, clock = get_scoreboard(game_id)
                return home_score, away_score, home_team, clock

        # Return default values if no Celtics game is found.
        return -1, -1, "unknown", "00:00"

    except Exception as e:
        print("Failed to fetch NBA games:", e)
        return 0, 0, "unknown", "12:00"

def get_current_date():
    TIMEZONE = "America/New_York"
    URL = f"http://worldtimeapi.org/api/timezone/{TIMEZONE}"

    response = requests.get(URL)
    time_data = response.json()
    response.close()

    # Extract the date portion ("YYYY-MM-DD") from the ISO datetime string.
    current_date = time_data["datetime"]
   
    return current_date

def get_next_game():
    formatted_time = get_current_date()
    print(formatted_time)


def accept_IOS_input(str: http_request):
    return http_request


def get_scoreboard(game_id):

    NBA_SCOREBOARD_URL = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

    response = requests.get(NBA_SCOREBOARD_URL)
    data = response.json()
    response.close()

    scoreboard = response["scoreboard"]

    for game in scoreboard["games"]:

        game_clock = game["gameClock"]
        home_team_struct = game["homeTeam"]
        home_team_name = home_team_struct["teamName"]
        away_team_struct = game["awayTeam"]
        away_team_name = away_team_struct["teamName"]

        if home_team_name == "Celtics":
            home_score = home_team_struct["score"]
            away_score = away_team_struct["score"]

        if away_team_name == "Celtics":
            away_score = home_team_struct["score"]
            home_score = away_team_struct["score"]

        if home_score is not None and away_score is not None and game_clock:
            return int(home_score), int(away_score), game_clock

    return 0, 0, "0:00"


