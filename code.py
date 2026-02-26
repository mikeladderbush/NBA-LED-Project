"""
Adafruit Scoreboard for 64 pixel LED
=======================================================================================
"""

import time
import wifi
import microcontroller
import board
import keypad

from logo_bitmaps import *
from API_Connection import *
from draw_tools import *
from logos import *
from buffer_frame import *
from controller_server import *


# WiFi credentials.
try:
    from secrets import secrets
    WIFI_SSID = secrets["ssid"]
    WIFI_PASSWORD = secrets["password"]
except ImportError:
    print("Cannot locate WiFi credentials in 'secrets.py'.")
    raise

print("Connecting to WiFi...")
try:
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"Connected to {WIFI_SSID}")
    print("IP Address:", wifi.radio.ipv4_address)
except Exception as e:
    print("WiFi connection failed:", e)
    microcontroller.reset()


server, server_state = run_server()

DELAY_SECS = 30
LIVE_POLL_SECS = 20
SCHED_POLL_SECS = 300

# Debug controls
DEBUG = True
DBG_EVERY_SEC = 1.0          # tick debug frequency
DBG_EVERY_API = True         # print each API poll
DBG_WARN_FETCH_SLOW = 2.0    # seconds


# TimeFrame object is used to track a single point in time and the associated game attributes.
class TimeFrame:
    def __init__(self, team: nba_team, home_score, away_score, opponent, clock, game_time, game_status, period):
        self.team = team
        self.home_score = home_score
        self.away_score = away_score
        self.opponent = opponent
        self.clock = clock
        self.game_time = game_time
        self.game_status = game_status
        self.period = period


# Draws the current TimeFrame using the draw_tools methods.
def draw_frame(frame: TimeFrame):
    home = frame.team
    draw_logo(home, 0, 0, 0)
    opp = team_from_string(frame.opponent.lower())
    if opp is not None:
        draw_logo(opp, 0, 0, 1)

    draw_score(frame.home_score, frame.away_score)
    draw_clock(frame.clock)

    draw_columns(background_bitmap, 0, 32, 64, 4)   # type: ignore
    draw_columns(background_bitmap, 32, 32, 64, 3)  # type: ignore
    draw_row_singular(decal_bitmap, 64, 46, 2)      # type: ignore

    draw_quarter(frame.period)

TEAM_ABBRS = [
    "ATL","BKN","BOS","CHA","CHI","CLE","DAL","DEN","DET",
    "GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN",
    "NOP","NYK","OKC","ORL","PHI","PHX","POR","SAC","SAS",
    "TOR","UTA","WAS"
]

ABBR_TO_TEAMKEY = {
    "ATL": hawks,
    "BKN": nets,
    "BOS": celtics,
    "CHA": hornets,
    "CHI": bulls,
    "CLE": cavs,
    "DAL": mavericks,
    "DEN": nuggets,
    "DET": pistons,
    "GSW": warriors,
    "HOU": rockets,
    "IND": pacers,
    "LAC": clippers,
    "LAL": lakers,
    "MEM": grizzlies,
    "MIA": heat,
    "MIL": bucks,
    "MIN": timberwolves,
    "NOP": pelicans,
    "NYK": knicks,
    "OKC": thunder,
    "ORL": magic,
    "PHI": sixers,
    "PHX": suns,
    "POR": trail_blazers,
    "SAC": kings,
    "SAS": spurs,
    "TOR": raptors,
    "UTA": jazz,
    "WAS": wizards,
}

# Main loop for displaying team schedules and active games.
team_name = ""
menu_active = False

# hibernate mode that reactivates when the API request comes in.
server.poll()
hibernate = True

if server_state["power"] == "on":
    hibernate = False
    menu_active = True

while hibernate:
    response = server.poll()
    if server_state["power"] == "on":
        hibernate = False
        menu_active = True
        break
    else:
        hibernate = True

while menu_active:
    server.poll()

    if server_state["team"] != None:
        team_key = server_state["team"]
        if team_key:
            team = ABBR_TO_TEAMKEY[team_key]
            server_state["team"] = None
            break

    if server_state["power"] == "off":
        microcontroller.reset()
    draw_city_menu()

clear_area(letter_bitmap, 0, 0, 64, 64)

last_api_call = 0.0
last_tick = time.monotonic()
last_dbg = 0.0

latest_frame = None
target_secs = None
display_secs = None

home_score = None
away_score = None
opponent_str = None 
clock_str = None
game_time = None
game_status = None 
period = None
in_game = None

date_str = None
time_str = None
next_team_full = None
next_opp_full = None

next_tick = time.monotonic() + 1.0

# Initial fetch
t0 = time.monotonic()
print("break-point: 1")
try:
    if team == sixers:
        team.team_name = "76ers"
    home_score, away_score, opponent_str, clock_str, game_time, game_status, period = fetch_game(team.team_name)
    print("break-point: 2")
    t1 = time.monotonic()
    print("Fetched game, values gathered: ", home_score, away_score, opponent_str, clock_str, game_time, game_status, period)
    latest_frame = TimeFrame(team, home_score, away_score, opponent_str, clock_str, game_time, game_status, period)
    print(latest_frame.team.team_name)
    target_secs = clock_str_to_secs(clock_str)
except Exception as e:
    print("Live fetch had no games", e)

if target_secs is not None:
    display_secs = target_secs

if latest_frame == None:
    print("Falling back to next scheduled game:")
    date_str, time_str, next_team_full, next_opp_full = get_next_game(team.team_name)
    in_game = False
else:
    if latest_frame.game_status > 1:
        in_game = True

while True:

    server.poll()        
    now = time.monotonic()

    if in_game:
        print("In game poll")
        # Poll API occasionally
        if now - last_api_call > LIVE_POLL_SECS:
            if server_state["power"] == "off":
                microcontroller.reset()
            if latest_frame.team == sixers:
                latest_frame.team.team_name = "76ers"
            fetch_start = time.monotonic()
            home_score, away_score, opponent_str, clock_str, game_time, game_status, period = fetch_game(latest_frame.team.team_name)
            fetch_end = time.monotonic()
            fetch_dt = fetch_end - fetch_start

            latest_frame = TimeFrame(team, home_score, away_score, opponent_str, clock_str, game_time, game_status, period)
            last_api_call = now

            api_secs = clock_str_to_secs(clock_str)
            if api_secs is not None:
                old_target = target_secs
                target_secs = api_secs
                if display_secs is None:
                    display_secs = target_secs + DELAY_SECS

            if game_status < 1:
                in_game = False
                date_str, time_str, next_team_full, next_opp_full = get_next_game(latest_frame.team.team_name)

        # Local 1Hz tick
        if display_secs is not None and target_secs is not None:
            # If behind the scheduled tick time, only decrement by 1 per loop iteration.
            if now >= next_tick:
                if display_secs > (target_secs):
                    display_secs -= 1
                next_tick += 1.0

                # If we were stalled for a long time, don't try to "burn down" multiple seconds instantly.
                # Instead, re-anchor next_tick close to now to prevent burst skipping.
                if next_tick < now - 0.25:
                    next_tick = now + 0.75

        if latest_frame is not None and display_secs is not None:
            latest_frame.clock = secs_to_mmss(display_secs)
            draw_frame(latest_frame)

    else:
        print("Out of game poll")
        if now - last_api_call > SCHED_POLL_SECS:
            if server_state["power"] == "off":
                microcontroller.reset()
            try:
                fetch_start = time.monotonic()
                home_score, away_score, opponent_str, clock_str, game_time, game_status, period = fetch_game(team.team_name)
                fetch_end = time.monotonic()
                fetch_dt = fetch_end - fetch_start
                last_api_call = now

                if game_status >= 1:
                    latest_frame = TimeFrame(team.team_name, home_score, away_score, opponent_str, clock_str, game_time, game_status, period)
                    target_secs = clock_str_to_secs(clock_str)
                    if target_secs is not None:
                        display_secs = target_secs + DELAY_SECS
                    last_tick = now
                    in_game = True
            except Exception as e:
                print("Live fetch had no games", e)
                
        print("Future game loop")
        # game_time_as_secs = clock_str_to_secs(game_time)
        # print(game_time_as_secs)
        # if game_time_as_secs - now == 60:
        #    countdown = True
        # else:
        countdown = False
        draw_delay = 5000

        while draw_delay > 0:
            server.poll()
            if date_str == None:
                date_str, time_str, next_team_full, next_opp_full = get_next_game(latest_frame.team)
            draw_future_game(date_str, time_str, next_team_full, next_opp_full, countdown)
            draw_delay -= 1
            if server_state["power"] == "off":
                microcontroller.reset()

        draw_columns(background_bitmap, 0, 32, 64, 4)   # type: ignore
        draw_columns(background_bitmap, 32, 32, 64, 3)  # type: ignore
        draw_row_singular(decal_bitmap, 64, 46, 2)      # type: ignore