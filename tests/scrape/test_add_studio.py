import mongoengine as mongo
import os
import pytest
from lib import scrape


def test_add_studio_nonexistent(tmp_path, credentials):
    scrape.add_studio(0,
                      cache_directory=tmp_path,
                      credentials_file=credentials)

    # Check file system
    files = os.listdir(tmp_path)
    assert len(files) == 0

    # Now check database
    db = mongo.connect(credentials["database"],
                       host=credentials["host"],
                       port=credentials["port"],
                       username=credentials["username"],
                       password=credentials["password"])

    assert len(scrape.Project.objects) == 0
    assert len(scrape.Comment.objects) == 0
    assert len(scrape.Studio.objects) == 0


def test_add_studio(tmp_path, credentials):
    scrape.add_studio.delay(26211962,
                            cache_directory=str(tmp_path),
                            credentials_file=credentials)

    count = 0
    while count < 4:
        try:
            count = len(os.listdir(tmp_path / "projects"))
        except:
            pass

    # Check file system
    files = os.listdir(tmp_path / "projects")
    assert "383948531.json" in files
    assert "383948574.json" in files

    # Now check database
    db = mongo.connect(credentials["database"],
                       host=credentials["host"],
                       port=credentials["port"],
                       username=credentials["username"],
                       password=credentials["password"])

    while len(scrape.Project.objects(studio_id=26211962)) < 4:
        continue

    assert len(scrape.Project.objects(project_id=383948531)) == 1
    assert len(scrape.Project.objects(title="Test_Full")) == 1
    assert len(scrape.Project.objects(author="jsarchibald")) >= 2
    assert len(scrape.Project.objects(studio_id=26211962)) >= 2

    while len(scrape.Comment.objects()) < 3:
        continue

    assert len(scrape.Comment.objects(project_id=383948574)) >= 3
    assert len(scrape.Comment.objects(content="I love this project!")) >= 1

    assert len(scrape.Studio.objects(studio_id=26211962)) == 1
    assert len(scrape.Studio.objects(title="Test_Studio")) == 1

    db.drop_database("test_db")
