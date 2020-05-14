from . import common as common
from datetime import datetime
import mongoengine as mongo
from mongoengine.queryset.visitor import Q

connect_db = common.connect_db

# Here, some validation functions and the schema as a Mongoengine object.
def valid_required_text(param):
    """Raises a ValidationError if doesn't meet format for required_text."""
    if type(param) != list:
        raise mongo.ValidationError("required_text is a list")
    else:
        for r in param:
            if type(r) != list:
                raise mongo.ValidationError("required_text is a list of lists")
            else:
                for item in r:
                    if type(r) != str:
                        raise mongo.ValidationError("required_text is a list of lists of strings")

def valid_required_block_categories(param):
    """Raises a ValidationError if doesn't meet format for required_block_categories."""
    if type(param) != list:
        raise mongo.ValidationError("required_block_categories is a list")
    else:
        for r in param:
            if type(r) != dict or "name" not in r or "count" not in r or type(r["count"]) != int or type(r["name"]) != str:
                raise mongo.ValidationError("required_block_categories is a list of dicts, each with a name (str) and count (int) key.")
            
def valid_required_blocks(param):
    """Raises a ValidationError if doesn't meet format for required_blocks."""
    if type(param) != list:
        raise mongo.ValidationError("required_blocks is a list")
    else:
        for r in param:
            if type(r) != list:
                raise mongo.ValidationError("required_blocks is a list of lists")
            else:
                for item in r:
                    if type(r) != dict or "name" not in r or "count" not in r or type(r["count"]) != int or type(r["name"]) != str:
                        raise mongo.ValidationError("required_blocks is a list of lists of dicts, each with a name (str) and count (int) key.")
            
# The schema as a Mongoengine object.
class Challenge(mongo.Document):
    title = mongo.StringField(max_length=200)
    description = mongo.StringField(max_length=5000)
    min_instructions_length = mongo.IntField(default=0)
    min_notes_length = mongo.IntField(default=0)
    min_comments_made = mongo.IntField(default=0)
    min_backdrops = mongo.IntField(default=0)
    min_sprites = mongo.IntField(default=0)
    required_text = mongo.ListField(default=[], validation=valid_required_text)
    required_block_categories = mongo.ListField(default=[], validation=valid_required_block_categories)
    required_blocks = mongo.ListField(default=[], validation=valid_required_blocks)

