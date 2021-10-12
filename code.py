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
SCROLL_SPEED = 0.04

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

X_SCORE_SHIFT = 3
TEAM_ONE_X = 32
TEAM_ONE_SHADOW_X = TEAM_ONE_X + 1
TEAM_TWO_X = 49
TEAM_TWO_SHADOW_X = TEAM_TWO_X + 1

TOP_ROW_HEIGHT = int(
    matrixportal.graphics.display.height * 0.25) - 5
MIDDLE_ROW_HEIGHT = int(
    matrixportal.graphics.display.height * 0.5) - 5
BOTTOM_ROW_HEIGHT = int(
    matrixportal.graphics.display.height * 0.75) - 4

# --- Text Fields --- #

# Team One Score Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_ONE_SHADOW_X + X_SCORE_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Team Two Score Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_TWO_SHADOW_X + X_SCORE_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Team One Score
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_ONE_X + X_SCORE_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Team Two Score
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_TWO_X + X_SCORE_SHIFT, BOTTOM_ROW_HEIGHT)
)

# Team One Name Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_ONE_SHADOW_X, TOP_ROW_HEIGHT)
)

# Team Two Name Shadow
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_TWO_SHADOW_X, TOP_ROW_HEIGHT)
)

# Team One Name
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_ONE_X, TOP_ROW_HEIGHT)
)

# Team Two Name
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_TWO_X, TOP_ROW_HEIGHT)
)

# Inning
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_ONE_X, TOP_ROW_HEIGHT)
)
matrixportal.set_text_color("0xFFFFFF", 8)

# Outs
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_ONE_X, BOTTOM_ROW_HEIGHT)
)
matrixportal.set_text_color("0xFF0000", 9)

# First
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_TWO_X, MIDDLE_ROW_HEIGHT + 7)
)
matrixportal.set_text_color("0xFFC72C", 10)

# Second
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_TWO_X + 5, MIDDLE_ROW_HEIGHT + 1)
)
matrixportal.set_text_color("0xFFC72C", 11)

# Third
matrixportal.add_text(
    text_font=FONT,
    text_position=(TEAM_TWO_X + 10, MIDDLE_ROW_HEIGHT + 7)
)
matrixportal.set_text_color("0xFFC72C", 12)

# --- Functions --- #

# Gets the scores from our API and stores them in a data object
def getScores():
    print("Getting scores")
    gc.collect()
    response = matrixportal.fetch()
    data = json.loads(response)

    return data

def showInning(game):
    matrixportal.set_text("", 0)
    matrixportal.set_text("", 1)
    matrixportal.set_text("", 2)
    matrixportal.set_text("", 3)
    matrixportal.set_text("", 4)
    matrixportal.set_text("", 5)
    matrixportal.set_text("", 6)
    matrixportal.set_text("", 7)
    
    if "inning" in game:
        inning = ("^" + str(game["inning"])) if game["isTopInning"] else ("v" + str(game["inning"]))
        matrixportal.set_text(inning, 8)
        
        outs = ""
        for i in range (0, game["outs"]):
            outs += "X"
        
        matrixportal.set_text(outs, 9)
        
        first = "x" if game["first"] else "o"
        second = "x" if game["second"] else "o"
        third = "x" if game["third"] else "o"
        
        matrixportal.set_text(first, 10)
        matrixportal.set_text(second, 11)
        matrixportal.set_text(third, 12)
    
    
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
        awayScore = game["awayScore"]
        homeScore = game["homeScore"]
    else:
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

# --- Main --- #

REFRESH_RATE_DURING_GAMES = 900 # If games are going on, update scores every 15 minutes
REFRESH_RATE_OUTSIDE_GAMES = 1800 # If there are no games on, wait half an hour before checking again
data = None # Store the live data
refresh_time = None # Store time of last refresh
refresh_rate = None # Store refresh rate
i = 0 # Increment counter

while True:
    
    # If it's the first loop or it's been longer than our refresh rate, get live scores
    if (not refresh_time) or ((time.monotonic() - refresh_time) > refresh_rate):
        data = getScores()
        refresh_rate = REFRESH_RATE_DURING_GAMES # Update refresh rate (in case all games ended)
        refresh_time = time.monotonic()
        print("Refreshing in {:.0f} minutes".format(refresh_rate/60))
    
    # Display our information
    if data is not None:
        index = int(i) # We want to show the score/time twice before switching to the next game
        game = data['body']['payload'][index]
        showScore(game)
        time.sleep(3)
        
        showInning(game)
        time.sleep(3)
        
        showScore(game)
        time.sleep(3)
        
        # Increment index
        if i < len(data['body']['payload']) - 1:
            i += 1
        else:
            i = 0
