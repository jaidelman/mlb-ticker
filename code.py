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

# --- Functions --- #

# Gets the scores from our API and stores them in a data object
def getScores():
    print("Getting scores")
    gc.collect()
    response = matrixportal.fetch()
    data = json.loads(response)

    return data
    
# Sets the scores on the board, returns if the game has started or not
def setScore(game):
    
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
        index = int(i/2) # We want to show the score/time twice before switching to the next game
        game = data['body']['payload'][index]
        setScore(game)
        time.sleep(2)
        
        # Increment index
        if i < len(data['body']['payload'])*2 - 1:
            i += 1
        else:
            i = 0
