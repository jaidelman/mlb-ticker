import json
import requests
import teamColors
import time
import dateutil.parser
from dateutil import tz
from datetime import date


def lambda_handler(event, context):
    url = "http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1"
    headers = {
        "User-Agent ": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "*/*",
        "Accept-ranges": "bytes",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "http://statsapi.mlb.com/"
    }
    response = requests.get(url=url, params=headers).json()

    payload = {}
    games = []

    for game in response['dates'][0]['games']:
        link = 'http://statsapi.mlb.com' + game['link']
        stats = requests.get(url=link, params=headers).json()

        gameStatus = stats['gameData']['status']['abstractGameState']

        awayAbbr = stats['gameData']['teams']['away']['abbreviation']
        homeAbbr = stats['gameData']['teams']['home']['abbreviation']
        awayColors = teamColors.colors[awayAbbr]
        homeColors = teamColors.colors[homeAbbr]

        if gameStatus == "Live" or gameStatus == "Final":
            awayScore = stats['liveData']['linescore']['teams']['away']['runs']
            homeScore = stats['liveData']['linescore']['teams']['home']['runs']

            inning = stats['liveData']['linescore']['currentInning']
            isTopInning = stats['liveData']['linescore']['isTopInning']
            outs = stats['liveData']['linescore']['outs']
            
            first = True if 'first' in stats['liveData']['linescore']['offense'] else False
            second = True if 'second' in stats['liveData']['linescore']['offense'] else False
            third = True if 'third' in stats['liveData']['linescore']['offense'] else False

            obj = {
                'awayAbbr': awayAbbr,
                'homeAbbr': homeAbbr,
                'awayScore': awayScore,
                'homeScore': homeScore,
                'inning': inning,
                'isTopInning': isTopInning,
                'outs': outs,
                'first': first,
                'second': second,
                'third': third,
                'awayColors': awayColors,
                'homeColors': homeColors
            }
        else:
            startTime = dateutil.parser.parse(game['gameDate']).astimezone(tz.gettz('America/New_York')).strftime("%I:%M %p")

            obj = {
                'awayAbbr': awayAbbr,
                'homeAbbr': homeAbbr,
                'awayColors': awayColors,
                'homeColors': homeColors,
                'startTime': startTime
            }

        games.append(obj)

    payload['payload'] = games

    return {
        'statusCode': 200,
        'body': payload
    }
