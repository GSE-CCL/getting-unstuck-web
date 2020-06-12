import mongoengine as mongo
import os
import pytest
from lib import scrape

def test_get_projects_with_block_none(tmp_path, credentials):
    scrape.add_studio(26211962, cache_directory=tmp_path, credentials_file=credentials)
    result = scrape.get_projects_with_block("nonexistent_block", credentials_file=credentials)

    assert len(result) == 0

    db = scrape.connect_db(credentials)
    db.drop_database("test_db")

def test_get_projects_with_block(tmp_path, credentials):
    scrape.add_studio(26211962, cache_directory=tmp_path, credentials_file=credentials)

    while len(scrape.Project.objects(studio_id=26211962)) < 4:
        continue

    result = scrape.get_projects_with_block("control_repeat", credentials_file=credentials)

    assert len(result) >= 1

    db = scrape.connect_db(credentials)
    db.drop_database("test_db")

def test_get_projects_with_block_studio(tmp_path, credentials):
    scrape.add_studio(26211962, cache_directory=tmp_path, credentials_file=credentials)

    while len(scrape.Project.objects(studio_id=26211962)) < 4:
        continue

    result = scrape.get_projects_with_block("control_repeat", studio_id=26211962, credentials_file=credentials)

    assert len(result) >= 1

    db = scrape.connect_db(credentials)
    db.drop_database("test_db")
    