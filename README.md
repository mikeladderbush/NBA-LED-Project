# NBA Scoreboard Display

## Overview
The NBA Scoreboard Display is a CircuitPython-based project designed to control an Adafruit Matrix display and present live NBA game updates. The project connects to WiFi, queries the official NBA API for live game data and renders dynamic scoreboard graphics including scores, game time, and scheduled future games.

## Features
- **Live Game Updates:** Automatically retrieves real-time NBA game data.
- **Dynamic Display:** Updates scores, game clocks, and game dates on an LED matrix.
- **Future Game Scheduling:** Displays details of upcoming games based on a predefined schedule when no live game is detected.
- **Custom Graphics Rendering:** Utilizes CircuitPython's `displayio` to render team logos, numbers, and other graphics.
- **Modular Design:** Separates API connections, drawing functions, and application logic for ease of customization and maintenance.

## Customization
- **Team Selection:** Team is able to be selected through the on-board buttons.
- **Display Settings:** Tweak timing intervals, graphic dimensions, and other visual elements in the source code to suit your specific requirements.

## Acknowledgments
- **Adafruit:** For providing hardware, libraries, and tutorials.
- **Community Support:** Thanks to the members of the Adafruit Forums, Stack Overflow, and Reddit.
- **NBA:** For offering public access to game data.

## Future Plans
- **NFL, NHL, MLB:** I hope to add additional support for more leagues.
- **Betting Odds:** Expecting the next addition in the v1.0 release to be betting lines for scheduled games.
- **3-D Printed Enclosure:** Current prototype enclosure is simple and proof of concept.
- **Mobile Support For Team Selection:** Stripped down android application for controlling the display is in early production.


