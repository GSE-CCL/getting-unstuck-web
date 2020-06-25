import json

PROJECT_DIRECTORY = "c:/users/jarch/code/getting-unstuck-web"
PROJECT_CACHE_LENGTH = 60 * 60 * 24 * 7

CONVERT_URL = "https://scratch-convert.herokuapp.com/convert"
CACHE_DIRECTORY = "cache"
SITE = {
    "title": "Getting Unstuck"
}

# Task management
with open("secure/celery.json") as f:
    CLRY = json.load(f)
