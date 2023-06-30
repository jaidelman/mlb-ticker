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

# Away Score Shadow
AWAY_SCORE_SHADOW = 0
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_SHADOW_X + SCORE_X_SHIFT, TOP_ROW_HEIGHT)
)

# Home Score Shadow
HOME_SCORE_SHADOW = 1
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_SHADOW_X + SCORE_X_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Away Score
AWAY_SCORE = 2
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + SCORE_X_SHIFT, TOP_ROW_HEIGHT)
)

# Home Score
HOME_SCORE = 3
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + SCORE_X_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Away Name Shadow
AWAY_NAME_SHADOW = 4
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_SHADOW_X, TOP_ROW_HEIGHT)
)

# Home Name Shadow
HOME_NAME_SHADOW = 5
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_SHADOW_X, BOTTOM_ROW_HEIGHT)
)

# Away Name
AWAY_NAME = 6
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, TOP_ROW_HEIGHT)
)

# Home Name
HOME_NAME = 7
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, BOTTOM_ROW_HEIGHT)
)

# Inning
INNING = 8
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, TOP_ROW_HEIGHT)
)

# Outs
OUTS = 9
matrixportal.add_text(
    text_font=FONT,
    text_position=(LEFT_X, BOTTOM_ROW_HEIGHT)
)
matrixportal.set_text_color("0xFF0000", OUTS)

# Third base
THIRD_BASE = 10
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X, MIDDLE_ROW_HEIGHT + 6)
)
matrixportal.set_text_color("0xFFC72C", THIRD_BASE)

# Second base
SECOND_BASE = 11
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + 5, MIDDLE_ROW_HEIGHT)
)
matrixportal.set_text_color("0xFFC72C", SECOND_BASE)

# First base
FIRST_BASE = 12
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X + 10, MIDDLE_ROW_HEIGHT + 6)
)
matrixportal.set_text_color("0xFFC72C", FIRST_BASE)

# Start time
START_TIME = 13
matrixportal.add_text(
    text_font=FONT,
    text_position=(RIGHT_X, MIDDLE_ROW_HEIGHT + 4),
    scrolling=True
)

# --- Functions --- #

# Gets the scores from our API and stores them in a data object
def getScores():
    print("Getting scores")
    print(gc.mem_free())
    gc.collect()
    print(gc.mem_free())
    response = matrixportal.fetch()
    data = json.loads(response)

    return data

def clearScores():
    # Clear the scores off the board
    matrixportal.set_text("", AWAY_SCORE_SHADOW)
    matrixportal.set_text("", HOME_SCORE_SHADOW)
    matrixportal.set_text("", AWAY_SCORE)
    matrixportal.set_text("", HOME_SCORE)
    matrixportal.set_text("", AWAY_NAME)
    matrixportal.set_text("", HOME_NAME)
    matrixportal.set_text("", AWAY_NAME_SHADOW)
    matrixportal.set_text("", HOME_NAME_SHADOW)

def showInning(game):
    clearScores()

    if "inning" in game:

        # Set Inning
        battingColor = game["awayColors"]["primary"] if game["isTopInning"] else game["homeColors"]["primary"]
        inning = ("^" + str(game["inning"])) if game["isTopInning"] else ("v" + str(game["inning"]))
        matrixportal.set_text(inning, INNING)
        matrixportal.set_text_color(battingColor, INNING)

        # Set number of outs
        outs = ""
        for i in range (0, game["outs"]):
            outs += "X"
        matrixportal.set_text(outs, OUTS)

        # Set baserunners
        first = "X" if game["first"] else "-"
        second = "X" if game["second"] else "-"
        third = "X" if game["third"] else "-"

        matrixportal.set_text(first, FIRST_BASE)
        matrixportal.set_text(second, SECOND_BASE)
        matrixportal.set_text(third, THIRD_BASE)


# Sets the scores on the board
def showScore(game):
    # Clear the board
    matrixportal.set_text("", INNING)
    matrixportal.set_text("", OUTS)
    matrixportal.set_text("", THIRD_BASE)
    matrixportal.set_text("", SECOND_BASE)
    matrixportal.set_text("", FIRST_BASE)

    # Away Name Shadow
    matrixportal.set_text(game["awayAbbr"], AWAY_NAME_SHADOW)
    matrixportal.set_text_color(game["awayColors"]["alt"], AWAY_NAME_SHADOW)

    # Away Name
    matrixportal.set_text(game["awayAbbr"], AWAY_NAME)
    matrixportal.set_text_color(game["awayColors"]["primary"], AWAY_NAME)

    # Home Name Shadow
    matrixportal.set_text(game["homeAbbr"], HOME_NAME_SHADOW)
    matrixportal.set_text_color(game["homeColors"]["alt"], HOME_NAME_SHADOW)

    # Home Name
    matrixportal.set_text(game["homeAbbr"], HOME_NAME)
    matrixportal.set_text_color(game["homeColors"]["primary"], HOME_NAME)

    if "awayScore" in game:
        gameStarted = True
        awayScore = game["awayScore"]
        homeScore = game["homeScore"]
    else:
        gameStarted = False
        awayScore = 0
        homeScore = 0

    # Away Score Shadow
    matrixportal.set_text(awayScore, AWAY_SCORE_SHADOW)
    matrixportal.set_text_color(game["awayColors"]["alt"], AWAY_SCORE_SHADOW)

    # Away Score
    matrixportal.set_text(awayScore, AWAY_SCORE)
    matrixportal.set_text_color(game["awayColors"]["primary"], AWAY_SCORE)

    # Home Score Shadow
    matrixportal.set_text(homeScore, HOME_SCORE_SHADOW)
    matrixportal.set_text_color(game["homeColors"]["alt"], HOME_SCORE_SHADOW)

    # Home Score
    matrixportal.set_text(homeScore, HOME_SCORE)
    matrixportal.set_text_color(game["homeColors"]["primary"], HOME_SCORE)

    return gameStarted
    
def showFinal(game):
    clearScores()
    
    winnerColors = game["homeColors"]["primary"] if game['homeScore'] > game['awayScore'] else game["awayColors"]["primary"]
    matrixportal.set_text_color(winnerColors, START_TIME)
    matrixportal.set_text("FINAL", START_TIME)
    matrixportal.scroll_text(SCROLL_SPEED)

def showStartTime(game):
    clearScores()

    matrixportal.set_text_color(game["homeColors"]["primary"], START_TIME)
    matrixportal.set_text(game["startTime"], START_TIME)
    matrixportal.scroll_text(SCROLL_SPEED)

# --- Main --- #

GAME_STARTED = True
REFRESH_RATE_DURING_GAMES = 150 # If games are going on, update scores every 2.5 minutes
REFRESH_RATE_OUTSIDE_GAMES = 900 # If there are no games on, wait 15 minutes before checking again
data = None # Store the live data
refresh_time = None # Store time of last refresh
refresh_rate = None # Store refresh rate
i = 0 # Increment counter

while True:

    # If it's the first loop or it's been longer than our refresh rate, get live scores
    if (not refresh_time) or ((time.monotonic() - refresh_time) > refresh_rate):
        del data
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
            
            if not game['isFinal']:
                showInning(game)
                time.sleep(7)
            else:
                showFinal(game)
        else:
            showStartTime(game)

        showScore(game)
        time.sleep(10)

        # Increment index
        if i < len(data['body']['payload']) - 1:
            i += 1
        else:
            i = 0
