import json

# Site globals
CONVERT_URL = "https://scratch-convert.herokuapp.com/convert"
SITE = {
    "title":
        "Getting Unstuck",
    "description":
        "Getting Unstuck is a program for learning to debug computer programs.",
    "author":
        "Creative Computing Lab at the Harvard Graduate School of Education.",
    "ga":
        "<!-- Global site tag (gtag.js) - Google Analytics --><script async src=\"https://www.googletagmanager.com/gtag/js?id=UA-121701097-1\"></script><script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config', 'UA-121701097-1');</script>",
    "default_prompts_url_text":
        "See the email"
}

# Directories
CACHE_DIRECTORY = "cache"
SECURE_DIRECTORY = "secure"
DEFAULT_CREDENTIALS_FILE = f"{SECURE_DIRECTORY}/db.json"



PROJECT_DIRECTORY = "/Users/phaduong/Documents/getting-unstuck-web"
PROJECT_CACHE_LENGTH = 60 * 60 * 24 * 7

WKPDF_LOCATION = "/usr/local/bin/wkhtmltopdf"

# Task management
try:
    with open(f"{SECURE_DIRECTORY}/celery.json") as f:
        CLRY = json.load(f)
except:
    CLRY = {}

# 301 redirects
REDIRECT_PAGES = {
    "gettingunstuck.gse.harvard.edu": "/",
    "/about.html": "/about",
    "/index.html": "/",
    "/research.html": "/research",
    "/signup.html": "/signup",
    "/strategies.html": "/strategies",
    "/curriculum.html": "/curriculum"
}
