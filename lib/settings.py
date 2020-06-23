import json

CONVERT_URL = "https://scratch-convert.herokuapp.com/convert"
CACHE_DIRECTORY = "cache"
SITE = {
    "title": "Getting Unstuck"
}

# Task management
with open("secure/celery.json") as f:
    CLRY = json.load(f)
