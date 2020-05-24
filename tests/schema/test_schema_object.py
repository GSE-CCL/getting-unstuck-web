import mongoengine as mongo
import os
import pytest
from lib import schema

def test_schema_object_defaults(credentials):
    schema.connect_db(credentials)

    min_blockify = schema.Blockify()

    challenge = schema.Challenge(title = "Test challenge - DEFAULTS",
                                 description = "This is a challenge created by test_schema_object.py",
                                 min_blockify=min_blockify)
    challenge.save()

    assert schema.Challenge.objects(title = "Test challenge - DEFAULTS").count() == 1

def test_schema_object_correct(credentials):
    schema.connect_db(credentials)

    min_blockify = schema.Blockify(comments = 3,
                                   costumes = 1,
                                   sounds = 0,
                                   sprites = 1,
                                   variables = 0)
    challenge = schema.Challenge(title = "Test challenge - CORRECT",
                                 description = "This is a challenge created by test_schema_object.py",
                                 min_instructions_length = 50,
                                 min_description_length = 50,
                                 min_comments_made = 1,
                                 min_blockify = min_blockify,
                                 required_text = [["hello", "world"]],
                                 required_block_categories = {"motion": 1},
                                 required_blocks = [{"event_whenflagclicked": 1}])
    challenge.save()

    assert schema.Challenge.objects(title = "Test challenge - CORRECT").count() == 1

def test_schema_object_blank(credentials):
    schema.connect_db(credentials)
    challenge = schema.Challenge()
    with pytest.raises(mongo.ValidationError):
        challenge.save()

def test_schema_object_incorrect_rt(credentials):
    schema.connect_db(credentials)
    challenge = schema.Challenge(min_blockify=schema.Blockify(), required_text=[[["an array too far"]]])
    with pytest.raises(mongo.ValidationError):
        challenge.save()

def test_schema_object_incorrect_rc(credentials):
    schema.connect_db(credentials)
    challenge = schema.Challenge(min_blockify=schema.Blockify(), required_block_categories=[])
    with pytest.raises(mongo.ValidationError):
        challenge.save()

def test_schema_object_incorrect_rb(credentials):
    db = schema.connect_db(credentials)
    challenge = schema.Challenge(min_blockify=schema.Blockify(), required_blocks={"name": "event_whenflagclicked"})
    with pytest.raises(mongo.ValidationError):
        challenge.save()

    db.drop_database("test_db")
