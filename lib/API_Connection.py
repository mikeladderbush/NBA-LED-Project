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
import time
import json
import adafruit_requests
from draw_tools import draw_future_game

# Initialize HTTP request support with SSL.
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

# NBA scoreboard API endpoint URL.
NBA_SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

def fetch_game(team):
    try:
        response = requests.get(NBA_SCOREBOARD_URL)
        data = response.json()
        response.close()
        print(data)

        # Retrieve the list of games from the JSON response.
        games = data.get("scoreboard", {}).get("games", [])
        for game in games:
            game_time = game["gameStatusText"]
            game_id = game["gameId"]
            home_team = game["homeTeam"]["teamName"]
            away_team = game["awayTeam"]["teamName"]

            # Check if either team is the correct team.
            if home_team == team:
                home_score, away_score, clock = get_scoreboard(game_id, team)
                return home_score, away_score, away_team, clock, game_time

            if away_team == team:
                home_score, away_score, clock = get_scoreboard(game_id, team)
                return home_score, away_score, home_team, clock, game_time

        # Return default values if no game is found.
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

    # Extract date in format YYYY-MM-DD
    datetime_str = time_data.get("datetime", "")  # e.g. "2025-05-08T14:15:22.123456-04:00"
    date_str = datetime_str.split("T")[0]  # Just the "2025-05-08" part

    return date_str

def get_current_time():
    TIMEZONE = "America/New_York"
    URL = f"http://worldtimeapi.org/api/timezone/{TIMEZONE}"

    response = requests.get(URL)
    time_data = response.json()
    response.close()

    time_str_data = time_data.get("datetime","")
    time_str = time_str_data.split(":")[0] + ":" + time_str_data.split(":")[1]
    
    return time_str

import time

def convert_utc_to_est(utc_datetime):
    # Get offset from worldtimeapi
    tz_url = "http://worldtimeapi.org/api/timezone/America/New_York"
    tz_response = requests.get(tz_url)
    tz_data = tz_response.json()
    tz_response.close()

    utc_offset = tz_data.get("utc_offset", "-04:00")  # e.g. "-04:00"
    offset_sign = 1 if utc_offset[0] == "+" else -1
    offset_hours = int(utc_offset[1:3])
    offset_minutes = int(utc_offset[4:6])

    try:
        # Example: "2025-06-01T00:00:00.000Z"
        date_part, time_part = utc_datetime.replace("Z", "").split("T")
        time_clean = time_part.split(".")[0]  # Strip off milliseconds
        year, month, day = map(int, date_part.split("-"))
        hour, minute, second = map(int, time_clean.split(":"))
    except Exception as e:
        print("Datetime parse error:", e)
        return "TBD", "Time TBD"

    try:
        utc_struct = time.struct_time((year, month, day, hour, minute, second, 0, 0, 0))
        utc_epoch = time.mktime(utc_struct)
        offset_seconds = offset_sign * (offset_hours * 3600 + offset_minutes * 60)
        local_epoch = utc_epoch + offset_seconds
        local_time = time.localtime(local_epoch)
    except Exception as e:
        print("Epoch conversion error:", e)
        return "TBD", "Time TBD"

    hour_12 = local_time.tm_hour % 12 or 12
    am_pm = "AM" if local_time.tm_hour < 12 else "PM"
    time_str = f"{hour_12}:{local_time.tm_min:02d} {am_pm}"
    date_str = f"{local_time.tm_year:04}-{local_time.tm_mon:02}-{local_time.tm_mday:02}"

    return date_str, time_str



def get_next_game(team):

    teams = {
        "Hawks": 1,
        "Celtics": 2,
        "Nets": 3,
        "Hornets": 4,
        "Bulls": 5,
        "Cavaliers": 6,
        "Mavericks": 7,
        "Nuggets": 8,
        "Pistons": 9,
        "Warriors": 10,
        "Rockets": 11,
        "Pacers": 12,
        "Lakers": 13,
        "Clippers": 14,
        "Grizzlies": 15,
        "Heat": 16,
        "Bucks": 17,
        "Timberwolves": 18,
        "Pelicans": 19,
        "Knicks": 20,
        "Thunder": 21,
        "Magic": 22,
        "76ers": 23,
        "Suns": 24,
        "Blazers": 25,
        "Kings": 26,
        "Spurs": 27,
        "Raptors": 28,
        "Jazz": 29,
        "Wizards": 30
    }

    team_id = teams.get(team)
    start_date = get_current_date()
    print(start_date)


    url = (
        "https://api.balldontlie.io/v1/games"
        f"?team_ids[]={team_id}&start_date={start_date}"
    )

    headers = {
        "Authorization": "Bearer 7b02b2a9-0b96-4f6f-9ab1-1b14f14abb9f"
    }

    try:
        response = requests.get(url, headers=headers)
        raw_text = response.text
        response.close()
        print(raw_text)

        if not raw_text:
            print("Empty response from server.")
            return

        try:
            data = json.loads(raw_text)
        except Exception as e:
            print("JSON parse error:", e)
            print("Response was:", raw_text[:200])
            return

        if not isinstance(data, dict):
            print("Data is not a dict.")
            return

        games = data.get("data")
        if not isinstance(games, list):
            print("Unexpected 'data' structure:", games)
            return

        if len(games) == 0:
            print("No upcoming games found.")
            return

        game = games[0]

        home_id = game["home_team"]["id"]
        away_id = game["visitor_team"]["id"]
        opponent = game["visitor_team"]
        opp_name = opponent["full_name"]
        team = game["home_team"]
        team_name = team["full_name"]

        utc_dt = game.get("datetime")
        if utc_dt and "T" in utc_dt:
            date_str, time_str = convert_utc_to_est(utc_dt)
        else:
            date_str = game.get("date", "TBD")
            time_str = "Time TBD"

        print(f"Next game is {opp_name} on {date_str} at {time_str}")
        draw_future_game(date_str, time_str, team_name, opp_name)

    except Exception as e:
        print("Failed to retrieve next game:", e)

def get_scoreboard(game_id, team_id):

    NBA_SCOREBOARD_URL = f"https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

    response = requests.get(NBA_SCOREBOARD_URL)
    data = response.json()
    response.close()

    games = data.get("scoreboard", {}).get("games", [])
    for game in games:
        game_id = game["gameId"]
        game_clock = game["gameClock"]
        home_team_struct = game["homeTeam"]
        home_team_name = home_team_struct["teamName"]
        away_team_struct = game["awayTeam"]
        away_team_name = away_team_struct["teamName"]

        if home_team_name == team_id:
            home_score = home_team_struct["score"]
            away_score = away_team_struct["score"]

        if away_team_name == team_id:
            away_score = home_team_struct["score"]
            home_score = away_team_struct["score"]

        if home_score is not None and away_score is not None and game_clock:
            return int(home_score), int(away_score), game_clock

    return 0, 0, "0:00"


