"""
Library for interpreting logic and presenting it on the display using Adafruit libraries
=======================================================================================

Author(s): Michael Ladderbush
"""

from adafruit_matrixportal.matrix import Matrix
import displayio
import board
import time
from logo_bitmaps import *
from logos import *
from buffer_frame import *
import re

class nba_team:
    def __init__(self, team_name, bitmap, palette, pattern):
        self.team_name = team_name
        self.bitmap = bitmap
        self.palette = palette
        self.pattern = pattern

# Eastern Conference teams
hawks = nba_team("Hawks", hawks_logo_bitmap, hawks_logo_palette, hawks_pattern)
celtics = nba_team("Celtics", celtics_logo_bitmap, celtics_logo_palette, celtics_pattern)
nets = nba_team("Nets", nets_logo_bitmap, nets_logo_palette, nets_pattern)
hornets = nba_team("Hornets", hornets_logo_bitmap, hornets_logo_palette, hornets_pattern)
bulls = nba_team("Bulls", bulls_logo_bitmap, bulls_logo_palette, bulls_pattern)
cavs = nba_team("Cavs", cavs_logo_bitmap, cavs_logo_palette, cavs_pattern)
pistons = nba_team("Pistons", pistons_logo_bitmap, pistons_logo_palette, pistons_pattern)
pacers = nba_team("Pacers", pacers_logo_bitmap, pacers_logo_palette, pacers_pattern)
heat = nba_team("Heat", heat_logo_bitmap, heat_logo_palette, heat_pattern)
bucks = nba_team("Bucks", bucks_logo_bitmap, bucks_logo_palette, bucks_pattern)
knicks = nba_team("Knicks", knicks_logo_bitmap, knicks_logo_palette, knicks_pattern)
magic = nba_team("Magic", magic_logo_bitmap, magic_logo_palette, magic_pattern)
sixers = nba_team("Sixers", sixers_logo_bitmap, sixers_logo_palette, sixers_pattern)
raptors = nba_team("Raptors", raptors_logo_bitmap, raptors_logo_palette, raptors_pattern)
wizards = nba_team("Wizards", wizards_logo_bitmap, wizards_logo_palette, wizards_pattern)

# Western Conference teams
mavericks = nba_team("Mavericks", mavericks_logo_bitmap, mavericks_logo_palette, mavericks_pattern)
nuggets = nba_team("Nuggets", nuggets_logo_bitmap, nuggets_logo_palette, nuggets_pattern)
warriors = nba_team("Warriors", warriors_logo_bitmap, warriors_logo_palette, warriors_pattern)
rockets = nba_team("Rockets", rockets_logo_bitmap, rockets_logo_palette, rockets_pattern)
clippers = nba_team("Clippers", clippers_logo_bitmap, clippers_logo_palette, clippers_pattern)
lakers = nba_team("Lakers", lakers_logo_bitmap, lakers_logo_palette, lakers_pattern)
grizzlies = nba_team("Grizzlies", grizzlies_logo_bitmap, grizzlies_logo_palette, grizzlies_pattern)
timberwolves = nba_team("Timberwolves", timberwolves_logo_bitmap, timberwolves_logo_palette, timberwolves_pattern)
pelicans = nba_team("Pelicans", pelicans_logo_bitmap, pelicans_logo_palette, pelicans_pattern)
thunder = nba_team("Thunder", thunder_logo_bitmap, thunder_logo_palette, thunder_pattern)
suns = nba_team("Suns", suns_logo_bitmap, suns_logo_palette, suns_pattern)
trail_blazers = nba_team("Trail_blazers", trail_blazers_logo_bitmap, trail_blazers_logo_palette, trail_blazers_pattern)
kings = nba_team("Kings", kings_logo_bitmap, kings_logo_palette, kings_pattern)
spurs = nba_team("Spurs", spurs_logo_bitmap, spurs_logo_palette, spurs_pattern)
jazz = nba_team("Jazz", jazz_logo_bitmap, jazz_logo_palette, jazz_pattern)

# Helper to assign team with just a name.
def team_from_string(team_name) -> nba_team:
    teams = {
        "Hawks": hawks,
        "Celtics": celtics,
        "Nets": nets,
        "Hornets": hornets,
        "Bulls": bulls,
        "Cavaliers": cavs,
        "Mavericks": mavericks,
        "Nuggets": nuggets,
        "Pistons": pistons,
        "Warriors": warriors,
        "Rockets": rockets,
        "Pacers": pacers,
        "Lakers": lakers,
        "Clippers": clippers,
        "Grizzlies": grizzlies,
        "Heat": heat,
        "Bucks": bucks,
        "Timberwolves": timberwolves,
        "Pelicans": pelicans,
        "Knicks": knicks,
        "Thunder": thunder,
        "Magic": magic,
        "Sixers": sixers,
        "Suns": suns,
        "Blazers": trail_blazers,
        "Kings": kings,
        "Spurs": spurs,
        "Raptors": raptors,
        "Jazz": jazz,
        "Wizards": wizards
    }

    opponent_team = teams.get(team_name)

    return opponent_team

# Draws a pixel on the given bitmap at the specified (x, y) coordinate using the provided color.
def draw_pixel(bitmap, x, y, my_color):
    bitmap[x, y] = my_color

# Draws a horizontal row of pixels on the given bitmap.
# The row starts at the left edge and spans 'length' pixels at the specified y coordinate using the given color.
def draw_row_singular(bitmap, length, y, my_color):
    for x in range(length):
        draw_pixel(bitmap, x, y, my_color)

# Draws multiple horizontal rows on the given bitmap.
# Starting at 'start_loc', 'num_rows' rows are drawn, each spanning 'length' pixels, in the specified color.
def draw_rows(bitmap, start_loc, num_rows, length, my_color):
    for row in range(start_loc, start_loc + num_rows):
        draw_row_singular(bitmap, length, row, my_color)

# Draws a vertical column of pixels on the given bitmap.
# The column spans 'length' pixels at the specified x coordinate using the provided color.
def draw_column_singular(bitmap, length, x, my_color):
    for y in range(length):
        draw_pixel(bitmap, x, y, my_color)

# Draws multiple vertical columns on the given bitmap.
# Starting at 'start_loc', 'num_columns' columns are drawn, each spanning 'length' pixels, in the specified color.
def draw_columns(bitmap, start_loc, num_columns, length, my_color):
    for column in range(start_loc, start_loc + num_columns):
        draw_column_singular(bitmap, length, column, my_color)

# Scales a flat pattern by repeating each pixel value according to the specified scale factor.
# Returns the scaled pattern along with the new width and height.
def scale_pattern(pattern, original_width, original_height, scale):
    new_pattern = []
    for row in range(original_height):
        scaled_row = []
        for column in range(original_width):
            pixel = pattern[row * original_width + column]
            scaled_row.extend([pixel] * scale)
        for value in range(scale):
            new_pattern.extend(scaled_row)
    
    new_width = original_width * scale
    new_height = original_height * scale
    return new_pattern, new_width, new_height

# Draws a sprite on the given bitmap.
# The sprite is defined by its width, height, scale (size), pattern, and palette.
# The pattern is first scaled; then each non-zero value in the scaled pattern is drawn on the bitmap.
def draw_sprite(bitmap, x, y, width, height, size, pattern, palette, bg_index=0, draw_bg=False):
    scaled_pattern, new_width, new_height = scale_pattern(pattern, width, height, size)

    if len(pattern) != width * height:
        raise ValueError("Pattern length doesn't match sprite dimensions")

    for row in range(new_height):
        for col in range(new_width):
            index = row * new_width + col
            pattern_index_value = scaled_pattern[index]

            if pattern_index_value == 0:
                if draw_bg:
                    bitmap[x + col, y + row] = bg_index
                continue
            if pattern_index_value > 0:
                bitmap[x + col, y + row] = pattern_index_value  # Assign index, not hex color
            else:
                raise ValueError(f"Pattern index {pattern_index_value} out of range (0-{bitmap.colors - 1})")

# Draws a cube on the given bitmap by creating a pattern filled with ones and then calling draw_sprite.
def draw_cube(bitmap, x, y, width, height, size, palette):
    cube_pattern = [1] * (width * height)
    draw_sprite(bitmap, x, y, width, height, size, cube_pattern, palette, bg_index=0, draw_bg=True)

# Draws a triangle on the given bitmap.
# The triangle can be rendered with two different reflections, controlled by the 'reflection' parameter.
def draw_triangle(bitmap, x, y, width, height, size, reflection, palette):
    triangle_pattern = []
    if reflection == 0:
        for row in range(height):
            pixels = (row + 1) * width // height
            if pixels < 1:
                pixels = 1
            row_pattern = [1] * pixels + [0] * (width - pixels)
            triangle_pattern.extend(row_pattern)
        
        draw_sprite(bitmap, x, y, width, height, triangle_pattern, palette, bg_index=0, draw_bg=True)
    if reflection == 1:
        for row in range(height):
            pixels = (row + 1) * width // height
            if pixels < 1:
                pixels = 1
            row_pattern = [0] * (width - pixels) + [1] * pixels
            triangle_pattern.extend(row_pattern)
        
        draw_sprite(bitmap, x, y, width, height, size, triangle_pattern, palette, bg_index=0, draw_bg=True)

# Draws a number on the display by mapping the digit to its corresponding drawing function.
def draw_number(number, x, y, size):
    def get_number(number):
        return {
            1: lambda: draw_one(x, y, size),
            2: lambda: draw_two(x, y, size),
            3: lambda: draw_three(x, y, size),
            4: lambda: draw_four(x, y, size),
            5: lambda: draw_five(x, y, size),
            6: lambda: draw_six(x, y, size),
            7: lambda: draw_seven(x, y, size),
            8: lambda: draw_eight(x, y, size),
            9: lambda: draw_nine(x, y, size)
        }.get(number, lambda: draw_zero(x, y, size))()
    
    get_number(number)

# Draws a colon on the display using a predefined pattern.
def draw_colon(x, y, size):
    pattern = (
        0, 0, 0,
        0, 2, 0,
        0, 0, 0,
        0, 2, 0,
        0, 0, 0,
    )

    draw_sprite(decal_bitmap, x, y, 3, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws a dash on the display using a predefined pattern.
def draw_dash(x, y, size):
    pattern = (
        0, 0, 0,
        0, 0, 2,
        0, 2, 0,
        2, 0, 0,
        0, 0, 0,
    )

    draw_sprite(decal_bitmap, x, y, 3, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws a hyphen on the display.
def draw_hyphen(x, y, size):
    pattern = (
        0, 0, 0,
        0, 0, 0,
        0, 2, 2,
        0, 0, 0,
        0, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 3, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '0' on the display using a predefined pattern.
def draw_zero(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 0, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '1' on the display using a predefined pattern.
def draw_one(x, y, size):
    pattern = (
        0, 0, 2, 0,
        0, 2, 2, 0,
        0, 0, 2, 0,
        0, 0, 2, 0,
        0, 2, 2, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '2' on the display using a predefined pattern.
def draw_two(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 0, 0, 2,
        0, 2, 2, 2,
        0, 2, 0, 0,
        0, 2, 2, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '3' on the display using a predefined pattern.
def draw_three(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 0, 0, 2,
        0, 0, 2, 2,
        0, 0, 0, 2,
        0, 2, 2, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '4' on the display using a predefined pattern.
def draw_four(x, y, size):
    pattern = (
        0, 2, 0, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
        0, 0, 0, 2,
        0, 0, 0, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '5' on the display using a predefined pattern.
def draw_five(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 2, 0, 0,
        0, 2, 2, 2,
        0, 0, 0, 2,
        0, 2, 2, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '6' on the display using a predefined pattern.
def draw_six(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 2, 0, 0,
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '7' on the display using a predefined pattern.
def draw_seven(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 0, 0, 2,
        0, 0, 2, 0,
        0, 0, 2, 0,
        0, 0, 2, 0,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '8' on the display using a predefined pattern.
def draw_eight(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the digit '9' on the display using a predefined pattern.
def draw_nine(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
        0, 0, 0, 2,
        0, 0, 0, 2,
    )

    draw_sprite(decal_bitmap, x, y, 4, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

# Draws the letter 'A' on the display using a predefined pattern.
def draw_A(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 0, 2,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_a(x, y, size):
    pattern = (
        0, 2, 2, 0,
        0, 0, 2, 0,
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 2, 2, 2,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_B(x, y, size):
    pattern = (
        2, 2, 0, 0,
        2, 0, 2, 0,
        2, 2, 0, 0,
        2, 0, 2, 0,
        2, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_C(x, y, size):
    pattern = (
        2, 2, 2, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 2, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_D(x, y, size):
    pattern = (
        2, 2, 0, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_d(x, y, size):
    pattern = (
        0, 0, 2, 0,
        0, 0, 2, 0,
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 2, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_E(x, y, size):
    pattern = (
        2, 2, 2, 0,
        2, 0, 0, 0,
        2, 2, 2, 0,
        2, 0, 0, 0,
        2, 2, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_f(x, y, size):
    pattern = (
        0, 2, 2, 0,
        0, 2, 0, 0,
        2, 2, 2, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_G(x, y, size):
    pattern = (
        0, 2, 2, 0,
        2, 0, 0, 0,
        2, 0, 2, 2,
        2, 0, 0, 2,
        0, 2, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_H(x, y, size):
    pattern = (
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_h(x, y, size):
    pattern = (
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_I(x, y, size):
    pattern = (
        2, 2, 2, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
        2, 2, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_K(x, y, size):
    pattern = (
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 2, 0, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_L(x, y, size):
    pattern = (
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 2, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_l(x, y, size):
    pattern = (
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_M(x, y, size):
    pattern = (
        2, 0, 0, 0, 2,
        2, 2, 0, 2, 2,
        2, 0, 2, 0, 2,
        2, 0, 0, 0, 2,
        2, 0, 0, 0, 2,
    )

    draw_sprite(letter_bitmap, x, y, 5, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_N(x, y, size):
    pattern = (
        2, 0, 0, 2,
        2, 2, 0, 2,
        2, 2, 2, 2,
        2, 0, 2, 2,
        2, 0, 0, 2,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_n(x, y, size):
    pattern = (
        0, 0, 0, 0,
        0, 0, 0, 0,
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_O(x, y, size):
    pattern = (
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 2, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_P(x, y, size):
    pattern = (
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 2, 2, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_p(x, y, size):
    pattern = (
        0, 2, 2, 2,
        0, 2, 0, 2,
        0, 2, 2, 2,
        0, 2, 0, 0,
        0, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_r(x, y, size):
    pattern = (
        0, 0, 0, 0,
        0, 0, 0, 0,
        2, 2, 0, 0,
        2, 0, 0, 0,
        2, 0, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_R(x, y, size):
    pattern = (
        2, 2, 2, 0,
        2, 0, 2, 0,
        2, 2, 0, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_S(x, y, size):
    pattern = (
        0, 2, 2, 0,
        2, 0, 0, 0,
        2, 2, 0, 0,
        0, 0, 2, 0,
        2, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_s(x, y, size):
    pattern = (
        0, 0, 0, 0,
        0, 2, 0, 0,
        2, 0, 0, 0,
        0, 2, 0, 0,
        2, 0, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_T(x, y, size):
    pattern = (
        2, 2, 2, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_t(x, y, size):
    pattern = (
        0, 2, 0, 0,
        0, 2, 0, 0,
        2, 2, 2, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_U(x, y, size):
    pattern = (
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
        0, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)    

def draw_W(x, y, size):
    pattern = (
        2, 0, 0, 0, 2,
        2, 0, 0, 0, 2,
        2, 0, 2, 0, 2,
        2, 0, 2, 0, 2,
        0, 2, 0, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 5, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_X(x, y, size):
    pattern = (
        2, 0, 2, 0,
        2, 0, 2, 0,
        0, 2, 0, 0,
        2, 0, 2, 0,
        2, 0, 2, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)

def draw_Y(x, y, size):
    pattern = (
        2, 0, 2, 0,
        2, 0, 2, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
        0, 2, 0, 0,
    )

    draw_sprite(letter_bitmap, x, y, 4, 5, size, pattern, letter_palette, bg_index=0, draw_bg=True)   

# Draws the team logos on the display.
# The 'home_or_away' parameter determines the logo position on the bitmap.
def draw_logo(team, x, y, home_or_away):

    width = 32
    height = 32
    size = 1

    if home_or_away == 0:
        draw_sprite(team.bitmap, x, y, width, height, size, team.pattern, team.palette, bg_index=0, draw_bg=True)
    if home_or_away == 1:
        draw_sprite(team.bitmap, x + 32, y, width, height, size, team.pattern, team.palette, bg_index=0, draw_bg=True)

# Draws the game score on the display.
# The score is split into hundreds, tens, and ones and drawn separately.
def draw_score(home_score, away_score):
    # Home team
    home_score_hundreds = (home_score // 100) % 10
    home_score_tens = (home_score // 10) % 10
    home_score_ones = home_score % 10


    if home_score_hundreds > 0:
        draw_number(home_score_hundreds, 0, 48, 2)
        draw_number(home_score_tens, 8, 48, 2)
        draw_number(home_score_ones, 16, 48, 2)
    else:
        draw_number(home_score_tens, 8, 48, 2)
        draw_number(home_score_ones, 16, 48, 2)

    # Away team
    away_score_hundreds = (away_score // 100) % 10
    away_score_tens = (away_score // 10) % 10
    away_score_ones = away_score % 10

    if away_score_hundreds > 0:
        draw_number(away_score_hundreds, 37, 48, 2)
        draw_number(away_score_tens, 45, 48, 2)
        draw_number(away_score_ones, 53, 48, 2)

    else:
        draw_number(away_score_tens, 45, 48, 2)
        draw_number(away_score_ones, 53, 48, 2)

def draw_quarter(quarter):
    if quarter == 1:
        draw_one(25, 48, 1)
        draw_s(30, 48, 1)
        draw_t(33, 48, 1)
    elif quarter == 2:
        draw_two(25, 48, 1)
        draw_n(30, 48, 1)
        draw_d(33, 48, 1)
    elif quarter == 3:
        draw_three(25, 48, 1)
        draw_r(30, 48, 1)
        draw_d(33, 48, 1)
    elif quarter == 4:
        draw_four(25, 48, 1)
        draw_t(30, 48, 1)
        draw_h(33, 48, 1)
    elif quarter == "Half":
        draw_H(28, 48, 1)
        draw_T(32, 48, 1)


def format_clock(clock_str):
    if not clock_str:
        return "00:00"

    match = re.match(r"PT(?:(\d+)M)?(?:(\d+)(?:\.\d+)?S)?", clock_str)
    if match:
        minutes = int(match.group(1) or 0)
        seconds = int(match.group(2) or 0)
        return f"{minutes:02d}:{seconds:02d}"

    return clock_str  # Assume it's already in MM:SS or HH:MM format


def draw_clock(clock_str):
    if not isinstance(clock_str, str) or not clock_str:
        clock_str = "12:00"  # Default fallback
    
    # Case 1: Format is PT-style (NBA game clock)
    if "PT" in clock_str:
        clock_str = format_clock(clock_str)

    # Case 2: Convert "HH:MM UTC" or "HH:MM" (24-hour format) to AM/PM
    if "UTC" in clock_str:
        try:
            clock_str = clock_str.replace(" UTC", "")
            hour, minute = map(int, clock_str.split(":"))
            am_pm = "AM" if hour < 12 else "PM"
            hour = hour % 12
            if hour == 0:
                hour = 12
            clock_str = f"{hour:02d}:{minute:02d} {am_pm}"
        except ValueError as e:
            print("UTC/24-hour time parse error:", e)
            clock_str = "12:00 PM"

    # Case 3: AM/PM Clock
    if "AM" in clock_str or "PM" in clock_str:
        try:
            time, am_pm = clock_str.split()
            hours, minutes = map(int, time.split(":"))

            draw_number(hours // 10, 9, 34, 2) if hours >= 10 else None
            draw_number(hours % 10, 13, 34, 2)
            draw_colon(21, 34, 2)
            draw_number(minutes // 10, 24, 34, 2)
            draw_number(minutes % 10, 32, 34, 2)

            if am_pm == "AM":
                draw_a(40, 39, 1)
            else:
                draw_p(40, 39, 1)
        except ValueError as e:
            print("AM/PM time format error:", e)

    # Case 4: MM:SS Game Clock
    else:
        try:
            # Normalize clock_str if it starts with colon (e.g., ":06.0")
            if clock_str.startswith(":"):
                clock_str = "0" + clock_str
            # Truncate fractional seconds if present
            if "." in clock_str:
                clock_str = clock_str.split(".")[0]

            minutes, seconds = map(int, clock_str.split(":"))
            if minutes >= 10:
                draw_number(minutes // 10, 12, 34, 2)
            draw_number(minutes % 10, 20, 34, 2)
            draw_colon(28, 34, 2)
            draw_number(seconds // 10, 32, 34, 2)
            draw_number(seconds % 10, 40, 34, 2)
        except ValueError as e:
            print("MM:SS time format error:", e)
            # Draw fallback clock
            draw_number(1, 9, 34, 2)
            draw_number(2, 13, 34, 2)
            draw_colon(21, 34, 2)
            draw_number(0, 24, 34, 2)
            draw_number(0, 32, 34, 2)


# Draws the game date on the display.
# The game date is converted into individual digits and separated by dashes.
def draw_date(game_date):
    try:
        year_str, month_str, day_str = game_date.split("-")

        year = int(year_str[-2:])
        month = int(month_str)
        day = int(day_str)

        game_month_tens = month // 10
        game_month_ones = month % 10
        game_day_tens = day // 10
        game_day_ones = day % 10
        game_year_tens = year // 10
        game_year_ones = year % 10

        if game_month_tens > 0:
            draw_number(game_month_tens, 1, 50, 2)
        draw_number(game_month_ones, 7, 50, 2)
        draw_dash(17, 53, 1)

        if game_day_tens > 0:
            draw_number(game_day_tens, 20, 50, 2)
        draw_number(game_day_ones, 28, 50, 2)
        draw_dash(39, 53, 1)

        if game_year_tens > 0:
            draw_number(game_year_tens, 43, 50, 2)
        draw_number(game_year_ones, 51, 50, 2)


    except Exception as e:
        print("draw_date format error:", e)

def draw_future_game(game_date, game_time, team, game_opponent):
    teams = {
        "Atlanta Hawks": hawks,
        "Boston Celtics": celtics,
        "Brooklyn Nets": nets,
        "Charlotte Hornets": hornets,
        "Chicago Bulls": bulls,
        "Cleveland Cavaliers": cavs,
        "Dallas Mavericks": mavericks,
        "Denver Nuggets": nuggets,
        "Detroit Pistons": pistons,
        "Golden State Warriors": warriors,
        "Houston Rockets": rockets,
        "Indiana Pacers": pacers,
        "Los Angeles Lakers": lakers,
        "Los Angeles Clippers": clippers,
        "Memphis Grizzlies": grizzlies,
        "Miami Heat": heat,
        "Milwaukee Bucks": bucks,
        "Minnesota Timberwolves": timberwolves,
        "New Orleans Pelicans": pelicans,
        "New York Knicks": knicks,
        "Oklahoma City Thunder": thunder,
        "Orlando Magic": magic,
        "Philadelphia 76ers": sixers,
        "Phoenix Suns": suns,
        "Portland Trail Blazers": trail_blazers,
        "Sacramento Kings": kings,
        "San Antonio Spurs": spurs,
        "Toronto Raptors": raptors,
        "Utah Jazz": jazz,
        "Washington Wizards": wizards
    }

    this_team = teams.get(team)
    opponent_team = teams.get(game_opponent)

    if opponent_team is None:
        print("Unknown opponent:", game_opponent)
        return

    draw_logo(this_team, 0, 0, 0)
    draw_logo(opponent_team, 0, 0, 1)
    draw_date(game_date)
    draw_clock(game_time)


def draw_city_menu():
    # ATL
    draw_A(2, 0, 1)
    draw_T(7, 0, 1)
    draw_L(11, 0, 1)

    # BKN
    draw_B(3, 7, 1)
    draw_K(7, 7, 1)
    draw_N(11, 7, 1)

    # BOS
    draw_B(3, 14, 1)
    draw_O(7, 14, 1)
    draw_S(11, 14, 1)

    # CHA
    draw_C(3, 21, 1)
    draw_H(7, 21, 1)
    draw_A(10, 21, 1)

    # CHI
    draw_C(3, 28, 1)
    draw_H(7, 28, 1)
    draw_I(11, 28, 1)

    # CLE
    draw_C(3, 35, 1)
    draw_L(7, 35, 1)
    draw_E(11, 35, 1)

    # DAL
    draw_D(3, 42, 1)
    draw_A(6, 42, 1)
    draw_L(11, 42, 1)

    # DEN
    draw_D(3, 49, 1)
    draw_E(7, 49, 1)
    draw_N(11, 49, 1)

    # DET
    draw_D(3, 56, 1)
    draw_E(7, 56, 1)
    draw_T(11, 56, 1)

    # GSW
    draw_G(18, 0, 1)
    draw_S(22, 0, 1)
    draw_W(25, 0, 1)

    # HOU
    draw_H(18, 7, 1)
    draw_O(22, 7, 1)
    draw_U(26, 7, 1)

    # IND
    draw_I(18, 14, 1)
    draw_N(22, 14, 1)
    draw_D(27, 14, 1)

    # LAC
    draw_L(18, 21, 1)
    draw_A(21, 21, 1)
    draw_C(26, 21, 1)

    # LAL
    draw_L(18, 28, 1)
    draw_A(21, 28, 1)
    draw_L(26, 28, 1)

    # MEM
    draw_M(18, 35, 1)
    draw_E(23, 35, 1)
    draw_M(27, 35, 1)

    # MIA
    draw_M(18, 42, 1)
    draw_I(23, 42, 1)
    draw_A(27, 42, 1)

    # MIL
    draw_M(18, 49, 1)
    draw_I(23, 49, 1)
    draw_L(27, 49, 1)

    # MIN
    draw_M(18, 56, 1)
    draw_I(23, 56, 1)
    draw_N(27, 56, 1)

    # NOP
    draw_N(36, 0, 1)
    draw_O(41, 0, 1)
    draw_P(45, 0, 1)

    # NYK
    draw_N(36, 7, 1)
    draw_Y(40, 7, 1)
    draw_K(44, 7, 1)

    # OKC
    draw_O(36, 14, 1)
    draw_K(40, 14, 1)
    draw_C(44, 14, 1)

    # ORL
    draw_O(36, 21, 1)
    draw_R(40, 21, 1)
    draw_L(44, 21, 1)

    # PHI
    draw_P(36, 28, 1)
    draw_H(40, 28, 1)
    draw_I(44, 28, 1)

    # PHX
    draw_P(36, 35, 1)
    draw_H(40, 35, 1)
    draw_X(44, 35, 1)

    # POR
    draw_P(36, 42, 1)
    draw_O(40, 42, 1)
    draw_R(44, 42, 1)

    # SAC
    draw_S(36, 49, 1)
    draw_A(39, 49, 1)
    draw_C(44, 49, 1)

    # SAS
    draw_S(36, 56, 1)
    draw_A(39, 56, 1)
    draw_S(44, 56, 1)

    # TOR
    draw_T(50, 0, 1)
    draw_O(54, 0, 1)
    draw_R(58, 0, 1)

    # UTA
    draw_U(50, 7, 1)
    draw_T(54, 7, 1)
    draw_A(57, 7, 1)

    # WAS
    draw_W(50, 14, 1)
    draw_A(55, 14, 1)
    draw_S(60, 14, 1)
    
def clear_hyphen(x, y, size):
    # Same sprite footprint as draw_hyphen: 3x5.
    # All zeros + draw_bg=True forces the background index into that region.
    pattern = (
        0, 0,
        0, 0,
        0, 0,
        0, 0,
        0, 0,
    )
    draw_sprite(letter_bitmap, x, y, 2, 5, size, pattern, decal_palette, bg_index=0, draw_bg=True)

def draw_selector(menu_idx: int):
    y_step = 7
    COL_X = [0, 16, 34, 48]
    COL_ROWS = [9, 9, 9, 3]  # matches your menu layout

    # 1) Clear every possible selector location
    idx = 0
    for col, rows in enumerate(COL_ROWS):
        x = COL_X[col]
        for row in range(rows):
            y = row * y_step
            clear_hyphen(x, y, 1)
            idx += 1

    # 2) Draw the active selector
    if menu_idx < 9:
        col = 0
        row = menu_idx
    elif menu_idx < 18:
        col = 1
        row = menu_idx - 9
    elif menu_idx < 27:
        col = 2
        row = menu_idx - 18
    else:
        col = 3
        row = menu_idx - 27  # 0..2

    x = COL_X[col]
    y = row * y_step
    draw_hyphen(x, y, 1)

def clear_area(bitmap, x0, y0, w, h, bg=0):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            bitmap[x, y] = bg

