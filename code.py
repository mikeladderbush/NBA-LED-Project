"""
Adafruit Scoreboard for 64 pixel LED

=======================================================================================

This program controls an Adafruit Matrix to generate scoreboard graphics based on live NBA schedules.
Credit for the underlying techniques goes to the Adafruit forums, StackOverflow, and Reddit.
The program connects to local WiFi (with plans for future configurability) and queries the official NBA scores API,
which returns details for today's games. Currently, the program is configured to display data for the Celtics;
a future version will allow selection of any team. If the team is not currently playing, the next game is determined
using a hardcoded schedule and compared to real time. Once the conditions are met and the data is confirmed,
the information is passed to functions within the draw_tools library. This library bridges the application logic and
the display by using displayio to define a matrix, and by creating bitmaps, palettes, and patterns that are rendered
on the display.

* Author(s): Michael Ladderbush, citations and credits pending.
"""

import time  # Standard library module for managing time delays.
import wifi  # CircuitPython module for WiFi connectivity.
import microcontroller  # Provides microcontroller-specific functions.
from logo_bitmaps import *  # Import logo bitmap definitions.
from API_Connection import *  # Import API connection functions.
from draw_tools import *  # Import drawing functions.
from logos import *  # Import logo definitions.

# Load WiFi credentials from the secrets file.
try:
    from secrets import secrets
    WIFI_SSID = secrets["ssid"]
    WIFI_PASSWORD = secrets["password"]
except ImportError:
    print("Cannot locate WiFi credentials in 'secrets.py'.")
    raise

# Connect to WiFi.
print("Connecting to WiFi...")
try:
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"Connected to {WIFI_SSID}")
    print("IP Address:", wifi.radio.ipv4_address)
except Exception as e:
    print("WiFi connection failed:", e)
    microcontroller.reset()

# Initialize API call timer to 1 second to avoid spamming the endpoint when no game is live.
last_api_call = time.monotonic()
API_UPDATE_INTERVAL = 1
team = "Pacers"
team_name = pacers

# Main loop: fetch API data, update scores/clock, and refresh display graphics.
while True:
    # Check if the API update interval has elapsed.
    if time.monotonic() - last_api_call > API_UPDATE_INTERVAL:
        last_api_call = time.monotonic()
        current_time = get_current_time()

        try:
            # Try to fetch live game data
            home_score, away_score, opponent, clock, game_time = fetch_game(team)  # type: ignore

            if game_time and game_time <= current_time:
                draw_logo(team_name, 0, 0, 0)
                opponent = team_from_string(opponent.lower())
                draw_logo(opponent, 0, 0, 1)
                draw_score(away_score, home_score)  # type: ignore
                draw_clock(clock)  # type: ignore
                API_UPDATE_INTERVAL = 1  # Live game, update frequently
            else:
                raise ValueError("No live game found or game hasn't started yet.")

        except Exception as e:
            print("Falling back to next scheduled game:", e)
            get_next_game(team)  # type: ignore
            API_UPDATE_INTERVAL = 300  # Idle mode, update less frequently


    # Update background and overlay graphics.
    draw_columns(background_bitmap, 0, 32, 64, 4)  # type: ignore
    draw_columns(background_bitmap, 32, 32, 64, 3)  # type: ignore
    draw_row_singular(decal_bitmap, 64, 46, 2)  # type: ignore

    # Refresh the display.
    display.refresh()  # type: ignore
