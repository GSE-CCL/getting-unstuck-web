import json


# Site globals
CONVERT_URL = "https://scratch-convert.herokuapp.com/convert"
SITE = {
    "title": "Getting Unstuck"
}

# Directories
CACHE_DIRECTORY = "cache"
SECURE_DIRECTORY = "secure"

# Task management
with open(f"{SECURE_DIRECTORY}/celery.json") as f:
    CLRY = json.load(f)
