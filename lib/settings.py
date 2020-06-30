import json


# Site globals
CONVERT_URL = "https://scratch-convert.herokuapp.com/convert"
SITE = {
    "title": "Getting Unstuck"
}

# Directories
CACHE_DIRECTORY = "cache"
SECURE_DIRECTORY = "secure"
DEFAULT_CREDENTIALS_FILE = f"{SECURE_DIRECTORY}/db.json"

PROJECT_DIRECTORY = "c:/users/jarch/code/getting-unstuck-web"
PROJECT_CACHE_LENGTH = 60 * 60 * 24 * 7

# Task management
try:
    with open(f"{SECURE_DIRECTORY}/celery.json") as f:
        CLRY = json.load(f)
except:
    CLRY = {}
