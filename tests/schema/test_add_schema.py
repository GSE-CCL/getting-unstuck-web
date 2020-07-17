import bson
import mongoengine as mongo
import os
import pytest
from lib import schema


def test_add_schema_defaults(credentials):
    result = schema.add_schema(credentials_file=credentials)
    assert type(result["id"]) == bson.objectid.ObjectId


def test_add_schema_correct(credentials):
    result = schema.add_schema(
        credentials_file=credentials,
        mins={
            "instructions_length": 50,
            "description_length": 50,
            "comments_made": 1
        },
        min_blockify={
            "comments": 3,
            "costumes": 1,
            "sounds": 0,
            "sprites": 1
        },
        required_text=[["hello",
                        "world"]],
        required_block_categories={"motion": 2},
        required_blocks=[{
            "event_whenflagclicked": 1
        }],
        title="Test challenge - add_schema - CORRECT",
        description="This is a challenge created by test_schema_object.py")

    assert type(result) == schema.Challenge
    assert "id" in result
    assert len(schema.Challenge.objects(id=result["id"])) == 1


def test_add_schema_incorrect_rt(credentials):
    result = schema.add_schema(credentials_file=credentials,
                               required_text=[[["an array too far"]]])
    assert result == False


def test_add_schema_incorrect_rc(credentials):
    result = schema.add_schema(credentials_file=credentials,
                               required_block_categories=[])
    assert result == False


def test_schema_object_incorrect_rb(credentials):
    result = schema.add_schema(
        credentials_file=credentials,
        required_blocks={"name": "event_whenflagclicked"})
    assert result == False

    db = schema.connect_db(credentials)
    db.drop_database("test_db")
