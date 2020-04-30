import json
import os
import pytest
import sys

from ccl_scratch_tools import Scraper, Parser

sys.path.insert(0, os.path.abspath("../"))

@pytest.fixture
def parser():
    return Parser()

@pytest.fixture
def scraper():
    return Scraper()

@pytest.fixture
def credentials():
    with open("fixtures/secure/db.json") as f:
        return json.load(f)
