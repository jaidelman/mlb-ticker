import board
import busio
import time
import gc
import json
from adafruit_matrixportal.matrixportal import MatrixPortal

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# --- Constants --- #

# Board related variables
FONT = "/5x8.bdf"
SCROLL_SPEED = 0.05

# Request related variables

# --- TODO: CHANGE THIS --- #
URL = secrets['aws-api-url-mlb']
HEADERS = {
    'x-api-key': secrets['x-api-key']
}

# --- MatrixPortal --- #

matrixportal = MatrixPortal(
    status_neopixel=board.NEOPIXEL,
    url=URL,
    headers=HEADERS
)

# --- (X,Y) related constants --- #

SCORE_X_SHIFT = 4
LEFT_X = 32
LEFT_SHADOW_X = LEFT_X + 1
RIGHT_X = 49
RIGHT_SHADOW_X = RIGHT_X + 1

TOP_ROW_HEIGHT = int(
    matrixportal.graphics.display.height * 0.25) - 4
MIDDLE_ROW_HEIGHT = int(
    matrixportal.graphics.display.height * 0.5) - 4
BOTTOM_ROW_HEIGHT = int(
    matrixportal.graphics.display.height * 0.75) - 4

# --- Text Fields --- #

# Team One Score Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_SHADOW_X + SCORE_X_SHIFT, TOP_ROW_HEIGHT)
)

# Team Two Score Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_SHADOW_X + SCORE_X_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Team One Score
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + SCORE_X_SHIFT, TOP_ROW_HEIGHT)
)

# Team Two Score
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + SCORE_X_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Team One Name Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_SHADOW_X, TOP_ROW_HEIGHT)
)

# Team Two Name Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_SHADOW_X, BOTTOM_ROW_HEIGHT)
)

# Team One Name
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, TOP_ROW_HEIGHT)
)

# Team Two Name
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, BOTTOM_ROW_HEIGHT)
)

# Inning
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, TOP_ROW_HEIGHT)
)

# Outs
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, BOTTOM_ROW_HEIGHT)
)
matrixportal.set_text_color("0xFF0000", 9)

# Third
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X, MIDDLE_ROW_HEIGHT + 6)
)
matrixportal.set_text_color("0xFFC72C", 10)

# Second
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + 5, MIDDLE_ROW_HEIGHT)
)
matrixportal.set_text_color("0xFFC72C", 11)

# First
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + 10, MIDDLE_ROW_HEIGHT + 6)
)
matrixportal.set_text_color("0xFFC72C", 12)

# StartTime
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X, MIDDLE_ROW_HEIGHT + 4),
    scrolling=True
)

# --- Functions --- #

# Gets the scores from our API and stores them in a data object
def getScores():
    print("Getting scores")
    gc.collect()
    response = matrixportal.fetch()
    data = json.loads(response)

    return data

def clearScores():
    matrixportal.set_text("", 0)
    matrixportal.set_text("", 1)
    matrixportal.set_text("", 2)
    matrixportal.set_text("", 3)
    matrixportal.set_text("", 4)
    matrixportal.set_text("", 5)
    matrixportal.set_text("", 6)
    matrixportal.set_text("", 7)

def showInning(game):
    clearScores()

    if "inning" in game:
        
        # Set Inning
        battingColor = game["awayColors"]["primary"] if game["isTopInning"] else game["homeColors"]["primary"]
        inning = ("^" + str(game["inning"])) if game["isTopInning"] else ("v" + str(game["inning"]))
        matrixportal.set_text(inning, 8)
        matrixportal.set_text_color(battingColor, 8)

        # Set number of outs
        outs = ""
        for i in range (0, game["outs"]):
            outs += "X"
        matrixportal.set_text(outs, 9)

        # Set baserunners
        first = "X" if game["first"] else "-"
        second = "X" if game["second"] else "-"
        third = "X" if game["third"] else "-"

        matrixportal.set_text(first, 12)
        matrixportal.set_text(second, 11)
        matrixportal.set_text(third, 10)


# Sets the scores on the board
def showScore(game):

    matrixportal.set_text("", 8)
    matrixportal.set_text("", 9)
    matrixportal.set_text("", 10)
    matrixportal.set_text("", 11)
    matrixportal.set_text("", 12)

    # Away Name Shadow
    matrixportal.set_text(game["awayAbbr"], 4)
    matrixportal.set_text_color(game["awayColors"]["alt"], 4)

    # Away Name
    matrixportal.set_text(game["awayAbbr"], 6)
    matrixportal.set_text_color(game["awayColors"]["primary"], 6)

    # Home Name Shadow
    matrixportal.set_text(game["homeAbbr"], 5)
    matrixportal.set_text_color(game["homeColors"]["alt"], 5)

    # Home Name
    matrixportal.set_text(game["homeAbbr"], 7)
    matrixportal.set_text_color(game["homeColors"]["primary"], 7)

    if "awayScore" in game:
        gameStarted = True
        awayScore = game["awayScore"]
        homeScore = game["homeScore"]
    else:
        gameStarted = False
        awayScore = 0
        homeScore = 0

    # Away Score Shadow
    matrixportal.set_text(awayScore, 0)
    matrixportal.set_text_color(game["awayColors"]["alt"], 0)

    # Away Score
    matrixportal.set_text(awayScore, 2)
    matrixportal.set_text_color(game["awayColors"]["primary"], 2)

    # Home Score Shadow
    matrixportal.set_text(homeScore, 1)
    matrixportal.set_text_color(game["homeColors"]["alt"], 1)

    # Home Score
    matrixportal.set_text(homeScore, 3)
    matrixportal.set_text_color(game["homeColors"]["primary"], 3)

    return gameStarted

def showStartTime(game):
    clearScores()

    matrixportal.set_text_color(game["homeColors"]["primary"], 13)
    matrixportal.set_text(game["startTime"], 13)
    matrixportal.scroll_text(SCROLL_SPEED)

# --- Main --- #

GAME_STARTED = False
REFRESH_RATE_DURING_GAMES = 150 # If games are going on, update scores every 2.5 minutes
REFRESH_RATE_OUTSIDE_GAMES = 900 # If there are no games on, wait 15 minutes before checking again
data = None # Store the live data
refresh_time = None # Store time of last refresh
refresh_rate = None # Store refresh rate
i = 0 # Increment counter

while True:

    # If it's the first loop or it's been longer than our refresh rate, get live scores
    if (not refresh_time) or ((time.monotonic() - refresh_time) > refresh_rate):
        data = getScores()
        refresh_rate = REFRESH_RATE_DURING_GAMES if GAME_STARTED else REFRESH_RATE_OUTSIDE_GAMES # Update refresh rate (in case all games ended)
        refresh_time = time.monotonic()
        print("Refreshing in {:.0f} minutes".format(refresh_rate/60))

    # Display our information
    if data is not None:
        index = i # We want to show the score/time twice before switching to the next game
        game = data['body']['payload'][index]

        gameStarted = showScore(game)
        time.sleep(10)

        if gameStarted:
            GAME_STARTED = True
            showInning(game)
            time.sleep(7)
        else:
            showStartTime(game)

        showScore(game)
        time.sleep(10)

        # Increment index
        if i < len(data['body']['payload']) - 1:
            i += 1
        else:
            i = 0
