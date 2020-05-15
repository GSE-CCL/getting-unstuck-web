from . import common as common
from datetime import datetime
import mongoengine as mongo
from mongoengine.queryset.visitor import Q

from . import scrape

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
                    if type(item) != str:
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
                    print(item)
                    if type(item) != dict or "name" not in item or "count" not in item or type(item["count"]) != int or type(item["name"]) != str:
                        raise mongo.ValidationError("required_blocks is a list of lists of dicts, each with a name (str) and count (int) key.")
            
# The part of the schema that can be found with blockify results
class Blockify(mongo.EmbeddedDocument):
    comments = mongo.IntField(default=0)
    costumes = mongo.IntField(default=0)
    sounds = mongo.IntField(default=0)
    sprites = mongo.IntField(default=0)
    variables = mongo.IntField(default=0)

# The schema as a Mongoengine object.
class Challenge(mongo.Document):
    title = mongo.StringField(max_length=200)
    description = mongo.StringField(max_length=5000)
    min_instructions_length = mongo.IntField(default=0)
    min_description_length = mongo.IntField(default=0)
    min_comments_made = mongo.IntField(default=0)
    min_blockify = mongo.EmbeddedDocumentField(Blockify, required=True)
    required_text = mongo.ListField(default=[[]], validation=valid_required_text)
    required_block_categories = mongo.ListField(default=[], validation=valid_required_block_categories)
    required_blocks = mongo.ListField(default=[[]], validation=valid_required_blocks)

# Functions to actually work with this schema
def validate_project(schema, project, studio_id):
    """Determines if the project meets the standards of a given schema.
    
    Args:
        schema: The validation schema. Can be given by its ID in the
            database or with a dictionary representing its values.
        project: The project. Given as either the Mongo object or its ID.
        studio_id (int): The studio ID.

    Returns:
        A modified version of the validation schema, revealing whether each requirement was met.
        False if couldn't successfully validate the project.
    """
    stat_types = ["block_comments", "blocks", "categories", "comments", "costumes", "sounds", "variables"]

    # Get the schema in dictionary format
    if type(schema) != dict:
        schema = scrape.Challenge.objects(_id = schema)

    # Get the project in dictionary format
    if type(project) != dict:
        project = scrape.Project.objects(_id = project)

    # Start the result dictionary
    result = dict.fromkeys(schema)
    del result["title"]
    del result["description"]

    # Start off with the blockify comparisons
    for key in schema["min_blockify"]:
        result["min_blockify"][key] = False
        if key in project["stats"] and len(project["stats"][key]) >= schema["min_blockify"][key]:
            result["min_blockify"][key] = True
            
    # Compare left comment counts
    project_ids = scrape.Project.objects(studio_id=studio_id).values_list("project_id")
    comments_left = scrape.Comment.objects(project_id__in=project_ids, author=project["author"]).count_docu()

    result["min_comments_made"] = comments_left >= schema["min_comments_made"]

    # Compare length of instructions and description
    result["min_instructions_length"] = len(project["instructions"]) >= schema["min_instructions_length"]
    result["min_description_length"] = len(project["description"]) >= schema["min_description_length"]

    # Check for required text
    result["required_text"] = [-1] * len(schema["required_text"])
    text_used = " ".join(project["block_text"])
    rt = schema["required_text"]
    for i in range(len(rt)):
        for j in range(len(rt[i])):
            if rt[i][j] in text_used:
                result["required_text"][i] = j
                break

    # Check for required categories
    result["required_block_categories"] = [False] * len(schema["required_block_categories"])
    rc = schema["required_block_categories"]
    for i in range(len(rc)):
        if project["stats"]["categories"][rc[i]["name"]] >= rc[i]["count"]:
            rc[i] = True
            break

    # Check for required blocks
    result["required_blocks"] = [-1] * len(schema["required_blocks"])
    rb = schema["required_blocks"]
    for i in range(len(rb)):
        for j in range(len(rb[i])):
            if rb[i][j]["name"] in project["stats"]["blocks"] \
               and len(project["stats"]["blocks"][rb[i][j]["name"]]) >= rb[i][j]["count"]:
                result[i] = j

    return result
