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
import adafruit_ntp
from draw_tools import draw_future_game

# Initialize HTTP request support with SSL.
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

BUFFER_SECS = 180

# NBA scoreboard API endpoint URL.
NBA_SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"

TEST_SCOREBOARD_URL_INIT = "http://192.168.1.165:5000/fake_clock_init"
TEST_SCOREBOARD_URL = "http://192.168.1.165:5000/fake_clock"

# Uses Adafruits NTP to get the current hours and minutes and returns them in the proper string format.
def get_current_time():
    try:
        # struct_time(tm_year=2025, tm_mon=12, tm_mday=19, tm_hour=23, tm_min=1, tm_sec=11, tm_wday=4, tm_yday=353, tm_isdst=-1)
        ntp = adafruit_ntp.NTP(pool, tz_offset=-5, socket_timeout=20)
        hours = ntp.datetime.tm_hour
        mins = ntp.datetime.tm_min
    except Exception as e:
        print("Failed to get current time", e)

    return f"{hours}:{mins}"


# Uses Adafruits NTP to ge tthe current date and returns it in string format.
def get_current_date():
    try:
        # struct_time(tm_year=2025, tm_mon=12, tm_mday=19, tm_hour=23, tm_min=1, tm_sec=11, tm_wday=4, tm_yday=353, tm_isdst=-1)
        ntp = adafruit_ntp.NTP(pool, tz_offset=-5, socket_timeout=20)
        year = int(ntp.datetime.tm_year)
        mon = int(ntp.datetime.tm_mon)
        day = int(ntp.datetime.tm_mday)
    except Exception as e:
        print("Failed to get current date", e)

    return f"{year:04d}-{mon:02d}-{day:02d}"


# Takes in the UTC time string and converts it into an Eastern Standard Time string.
def convert_utc_est(time_str):

    parts = time_str.split(":")
    hours = parts[0]
    minutes = parts[1]
    hours_int = int(hours)
    hours_int = (hours_int - 5) % 12
    hours = str(hours_int)

    est_time_str = hours + ":" + minutes

    return est_time_str



# This method uses the team object provided by the main method to parse and compare the scoreboard provided by the NBA API. 
# The JSON provided by the NBA API is checked and the necessary team attributes are returned. 
def fetch_game(team):
    try:
        # ONE request only
        response = requests.get(NBA_SCOREBOARD_URL)
        data = response.json()
        response.close()

        games = data.get("scoreboard", {}).get("games", [])
        for game in games:

            home = game.get("homeTeam", {})
            away = game.get("awayTeam", {})
            home_team = home.get("teamName")
            away_team = away.get("teamName")

            if team == home_team or team == away_team:
                print("Requested team passed to fetch: ", team)
                game_time = game.get("gameStatusText", "")
                game_status = game.get("gameStatus", 0)
                game_clock = game.get("gameClock", "")

                # scores as ints
                home_score_raw = home.get("score", 0) or 0
                away_score_raw = away.get("score", 0) or 0
                home_score_raw = int(home_score_raw)
                away_score_raw = int(away_score_raw)

                period = int(game.get("period", 0) or 0)

                # If requested team is home
                if home_team == team:
                    return home_score_raw, away_score_raw, away_team, game_clock, game_time, game_status, period

                # If requested team is away (swap so "home_score" is always your team)
                if away_team == team:
                    return away_score_raw, home_score_raw, home_team, game_clock, game_time, game_status, period

    except Exception as e:
        print("Failed to fetch NBA games:", e)
        return -1, -1, "unknown", "", "Scheduled", 1, 1



# Uses the team object to find the next game on the schedule using the NBA API.
def get_next_game(team):

    print("Getting next game on schedule for the following team: ", team)

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
        "Clippers": 13,
        "Lakers": 14,
        "Grizzlies": 15,
        "Heat": 16,
        "Bucks": 17,
        "Timberwolves": 18,
        "Pelicans": 19,
        "Knicks": 20,
        "Thunder": 21,
        "Magic": 22,
        "Sixers": 23,
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

    print("team_id", team_id)
    print("start_date", start_date)


    url = (
        "https://api.balldontlie.io/v1/games"
        f"?team_ids[]={team_id}&start_date={start_date}"
    )

    headers = {
        "Authorization": "Bearer 7b02b2a9-0b96-4f6f-9ab1-1b14f14abb9f"
    }

    attempts = 0

    print("attempting API get")

    while attempts < 5:
        try:
            response = requests.get(url, headers=headers)
            raw_text = response.text
            response.close()


            if not raw_text:
                print("Empty response from server.")
                return None, None, None, None

            try:
                data = json.loads(raw_text)
            except Exception as e:
                print("JSON parse error:", e)
                print("Response was:", raw_text[:200])
                return None, None, None, None

            if not isinstance(data, dict):
                print("Data is not a dict.")
                return None, None, None, None

            games = data.get("data")
            if not isinstance(games, list):
                print("Unexpected 'data' structure:", games)
                return None, None, None, None

            if len(games) == 0:
                print("No upcoming games found.")
                return None, None, None, None

            game = games[0]

            home_id = game["home_team"]["id"]
            away_id = game["visitor_team"]["id"]
            opponent = game["visitor_team"]
            opp_name = opponent["full_name"]
            team = game["home_team"]
            team_name = team["full_name"]
            date_str = game["date"]
            time_str = game["datetime"]
            
            #"2025-01-05T23:00:00.000Z"
            time_str = time_str[11:16]
            time_str = convert_utc_est(time_str)

            return date_str, time_str, team_name, opp_name

        except Exception as e:
            attempts += 1
            time.sleep(0.1)



# Converts a whole integer of seconds into a clock format minutes and seconds string.
def secs_to_mmss(total_seconds):
    if total_seconds < 0:
        total_seconds = 0
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"



# Clock simulator that takes in a clock string and adjusts it to accept delays.
def clock_str_to_secs(clock_str):
    if not clock_str:
        return None
    
    if clock_str.startswith("PT"):
        s = clock_str[2:]
        minutes = 0
        seconds = 0

        if "M" in s:
            m_part, rest = s.split("M", 1)
            if m_part:
                try:
                    minutes = int(m_part)
                except ValueError:
                    minutes = 0

        else:
            rest = s

        if "S" in rest:
            s_part = rest.split("S", 1)[0]
            if s_part:
                try:
                    seconds = int(float(s_part))
                except ValueError:
                    seconds = 0
        
        return minutes * 60 + seconds
    
    if ":" in clock_str:
        parts = clock_str.split(":")
        parts = [part.split(" ", 1)[0] for part in parts]
        print(parts)
        if len(parts) == 2:
            try:
                minutes = int(parts[0] or 0)
                sec_part = parts[1].split(".")[0]
                seconds = int(sec_part or 0)
                return minutes * 60 + seconds
            except ValueError:
                return None
        
            
    return None
