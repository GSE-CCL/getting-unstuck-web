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

# Task management
try:
    with open(f"{SECURE_DIRECTORY}/celery.json") as f:
        CLRY = json.load(f)
except:
    CLRY = {}
