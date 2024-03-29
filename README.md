# MLB-Ticker
The purpose of this project is to display live MLB scores on an Adafruit 16x32 LED Matrix.

https://user-images.githubusercontent.com/32146689/137643542-bd93167e-6e26-427c-b6b9-d9f3a67ad3c5.mp4

# How To Read The Scoreboard
When the scoreboard is displaying it's game state it shows the following:

```
^#     2
XXX  3   1
```

^#: This represents which inning the game is in. It will show '^' for the top of the inning, and 'v' for the bottom. When the scores are displayed, the home team is always on the bottom (The home team bats in the top of the inning, and the away team bats in the bottom of the inning).

X: This section represents the number of outs, with one 'X' for each out so far in the half inning

1,2,3: Each of these positions represents a base; 1st, 2nd, and 3rd. If there is a '_' in that position, then there is nobody on that base, while if there is an 'X' in that position there is a runner on that base.



# Hardware
I used [Adafruit's 16x32 LED Matrix](https://www.adafruit.com/product/420), their [MatrixPortal](https://www.adafruit.com/product/4745) and a USB C power supply

# Software

## Code.py
The code is written in Python using Adafruit and CircuitPython's libraries to control the LED Board. The board automatically runs the `code.py` file on startup. The API call to get the live scores returns a very large JSON which doesn't fit in the board's memory. Because of this, I created a REST API using AWS to return only the necessary data. The code checks whether there are any games in progress and refreshes the scores every 2.5 minutes if there are. If there are not, it will check every fifteen minutes to see if any games have started

## Lambda.py
`lambda.py` is the code I wrote for the lambda function running on AWS to gets live scores from MLB's stats API. I set it up through API Gateway to be triggered by an API call. The API requires authentication through an API key. The URL and API-KEY of this API are not included in this project but should be stored in a `secrets.py` file for `code.py` to successfully make the request

## teamColors.py
This file contains a bunch of hex color codes. Each team is assigned a primary color and alternate color which is used to display their abbreviation and score. The LED Matrix can not support certain shades, some colors were being displayed incorrectly (some reds looked very pink) and some colors aren't able to be displayed at all (gray, black, etc...). Because of this I created a list of color's hex codes that I tested on the board to make sure they look good and used those to make up the team colors.
