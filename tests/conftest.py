import json
import os
import pytest
import sys

from ccl_scratch_tools import Scraper, Parser
from lib import common

#sys.path.insert(0, os.path.abspath("../"))


@pytest.fixture
def parser():
    return Parser()


@pytest.fixture
def scraper():
    return Scraper()


@pytest.fixture
def credentials():
    with open("tests/fixtures/secure/db.json") as f:
        return json.load(f)


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    with open("tests/fixtures/secure/db.json") as f:
        creds = json.load(f)

    db = common.connect_db(creds)
    db.drop_database("test_db")
