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
    def __init__(self, team_name, home_score, away_score, opponent, clock, game_time, game_status, period):
        self.team_name = team_name
        self.home_score = home_score
        self.away_score = away_score
        self.opponent = opponent
        self.clock = clock
        self.game_time = game_time
        self.game_status = game_status
        self.period = period



# Draws the current TimeFrame using the draw_tools methods.
def draw_frame(frame: TimeFrame):
    draw_logo(frame.team_name, 0, 0, 0)

    opp = team_from_string(frame.opponent.lower())
    if opp is not None:
        draw_logo(opp, 0, 0, 1)

    draw_score(frame.home_score, frame.away_score)
    draw_clock(frame.clock)

    draw_columns(background_bitmap, 0, 32, 64, 4)   # type: ignore
    draw_columns(background_bitmap, 32, 32, 64, 3)  # type: ignore
    draw_row_singular(decal_bitmap, 64, 46, 2)      # type: ignore

    draw_quarter(frame.period)



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



# On-board buttons handle the selection of team to view.
keys = keypad.Keys(
    (board.BUTTON_UP, board.BUTTON_DOWN),
    value_when_pressed=False,
    pull=True
)
BTN_UP = 0
BTN_DN = 1

pressed = set() 

TEAM_ABBRS = [
    "ATL","BKN","BOS","CHA","CHI","CLE","DAL","DEN","DET",
    "GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN",
    "NOP","NYK","OKC","ORL","PHI","PHX","POR","SAC","SAS",
    "TOR","UTA","WAS"
]

ABBR_TO_TEAMKEY = {
    "ATL": "Hawks",
    "BKN": "Nets",
    "BOS": "Celtics",
    "CHA": "Hornets",
    "CHI": "Bulls",
    "CLE": "Cavaliers",
    "DAL": "Mavericks",
    "DEN": "Nuggets",
    "DET": "Pistons",
    "GSW": "Warriors",
    "HOU": "Rockets",
    "IND": "Pacers",
    "LAC": "Clippers",
    "LAL": "Lakers",
    "MEM": "Grizzlies",
    "MIA": "Heat",
    "MIL": "Bucks",
    "MIN": "Timberwolves",
    "NOP": "Pelicans",
    "NYK": "Knicks",
    "OKC": "Thunder",
    "ORL": "Magic",
    "PHI": "Sixers",
    "PHX": "Suns",
    "POR": "Blazers",
    "SAC": "Kings",
    "SAS": "Spurs",
    "TOR": "Raptors",
    "UTA": "Jazz",
    "WAS": "Wizards",
}



# Main loop for displaying team schedules and active games.
team = ""
team_obj = None

menu_active = True
menu_idx = 0
prev_menu_idx = None

while menu_active:
    event = keys.events.get()
    if event:
        print("EVENT key_number=", event.key_number, "pressed=", event.pressed)

        if event.pressed and event.key_number == BTN_DN:
            menu_idx = (menu_idx + 1) % len(TEAM_ABBRS)

        elif event.pressed and event.key_number == BTN_UP:
            abbr = TEAM_ABBRS[menu_idx]
            team_key = ABBR_TO_TEAMKEY.get(abbr)
            print("UP select abbr=", abbr, "team_key=", team_key)

            if team_key:
                team = team_key
                team_obj = team_from_string(team)

            print("team_obj is", "OK" if team_obj else "None")

            # IMPORTANT: break even if team_obj None for debugging
            menu_active = False
            break

    draw_city_menu()
    draw_selector(menu_idx)

clear_area(letter_bitmap, 0, 0, 64, 64)

last_api_call = 0.0
last_tick = time.monotonic()
last_dbg = 0.0

latest_frame = None
target_secs = None
display_secs = None

next_tick = time.monotonic() + 1.0

# Initial fetch
t0 = time.monotonic()
home_score, away_score, opponent_str, clock_str, game_time, game_status, period = fetch_game(team)
t1 = time.monotonic()

date_str, time_str, next_team_full, next_opp_full = get_next_game(team)

latest_frame = TimeFrame(team_obj, home_score, away_score, opponent_str, clock_str, game_time, game_status, period)
target_secs = clock_str_to_secs(clock_str)

if target_secs is not None:
    display_secs = target_secs

in_game = (game_status != 1)
if not in_game:
    print("Falling back to next scheduled game:")

if DEBUG:
    print("INIT fetch_game() seconds:", round(t1 - t0, 3))
    print("INIT clock_str:", clock_str, "target_secs:", target_secs, "display_secs:", display_secs, "status:", game_status)

while True:
    now = time.monotonic()

    if in_game:
        # Poll API occasionally
        if now - last_api_call > LIVE_POLL_SECS:
            fetch_start = time.monotonic()
            home_score, away_score, opponent_str, clock_str, game_time, game_status, period = fetch_game(team)
            fetch_end = time.monotonic()
            fetch_dt = fetch_end - fetch_start

            latest_frame = TimeFrame(team_obj, home_score, away_score, opponent_str, clock_str, game_time, game_status, period)
            last_api_call = now

            api_secs = clock_str_to_secs(clock_str)
            if api_secs is not None:
                old_target = target_secs
                target_secs = api_secs
                if display_secs is None:
                    display_secs = target_secs + DELAY_SECS

                if DEBUG and DBG_EVERY_API:
                    print(
                        "API poll dt=", round(fetch_dt, 3),
                        "clock_str=", clock_str,
                        "target=", target_secs,
                        "old_target=", old_target,
                        "display=", display_secs,
                        "hold_at=", (target_secs),
                    )

            if DEBUG and fetch_dt > DBG_WARN_FETCH_SLOW:
                print("WARN: fetch_game() slow/hung-ish:", round(fetch_dt, 3), "seconds")

            if game_status == 1:
                in_game = False
                date_str, time_str, next_team_full, next_opp_full = get_next_game(team)

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

        if DEBUG and (now - last_dbg) >= DBG_EVERY_SEC and display_secs is not None and target_secs is not None:
            hold_at = target_secs
            state = "COUNT" if display_secs > hold_at else "HOLD"
            print("TICK", state, "display=", display_secs, "target=", target_secs, "hold_at=", hold_at)
            last_dbg = now

        if latest_frame is not None and display_secs is not None:
            latest_frame.clock = secs_to_mmss(display_secs)
            draw_frame(latest_frame)

    else:
        if now - last_api_call > SCHED_POLL_SECS:
            fetch_start = time.monotonic()
            home_score, away_score, opponent_str, clock_str, game_time, game_status, period = fetch_game(team)
            fetch_end = time.monotonic()
            fetch_dt = fetch_end - fetch_start
            last_api_call = now

            if DEBUG:
                print("SCHED poll dt=", round(fetch_dt, 3), "status=", game_status, "clock_str=", clock_str)

            if game_status != 1:
                latest_frame = TimeFrame(team_obj, home_score, away_score, opponent_str, clock_str, game_time, game_status, period)
                target_secs = clock_str_to_secs(clock_str)
                if target_secs is not None:
                    display_secs = target_secs + DELAY_SECS
                last_tick = now
                in_game = True

        draw_future_game(date_str, time_str, next_team_full, next_opp_full)

        draw_columns(background_bitmap, 0, 32, 64, 4)   # type: ignore
        draw_columns(background_bitmap, 32, 32, 64, 3)  # type: ignore
        draw_row_singular(decal_bitmap, 64, 46, 2)      # type: ignore

    time.sleep(0.01)
