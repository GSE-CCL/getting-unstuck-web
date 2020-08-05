from . import common as common
from datetime import datetime
import mongoengine as mongo
from mongoengine.queryset.visitor import Q

from . import scrape, settings

connect_db = common.connect_db


# Here, some validation functions and the schema as a Mongoengine object.
def valid_comparison_basis(param):
    """Raises a ValidationError if doesn't meet format for comparison_basis."""
    if type(param) != dict:
        raise mongo.ValidationError("comparison_basis is a dict")
    else:
        bases = [
            "__none__",
            "required_text",
            "required_block_categories",
            "required_blocks"
        ]

        if not ("basis" in param and param["basis"] in bases):
            raise mongo.ValidationError("comparison_basis basis key is invalid")
        elif not ("priority" in param):
            raise mongo.ValidationError("comparison_basis priority key is invalid")  # yapf: disable


def valid_required_text(param):
    """Raises a ValidationError if doesn't meet format for required_text."""
    if type(param) != list:
        raise mongo.ValidationError("required_text is a list")
    else:
        for r in param:
            if type(r) != list:
                raise mongo.ValidationError("required_text is a list of lists")
            for item in r:
                if type(item) != str:
                    raise mongo.ValidationError(
                        "required_text is a list of lists of strings")


def valid_required_blocks(param):
    """Raises a ValidationError if doesn't meet format for required_blocks."""
    if type(param) != list:
        raise mongo.ValidationError("required_blocks is a list")
    else:
        for r in param:
            if type(r) != dict:
                raise mongo.ValidationError(
                    "required_blocks is a list of dicts")


# The part of the schema that can be found with blockify results
class Blockify(mongo.EmbeddedDocument):
    comments = mongo.IntField(default=0)
    costumes = mongo.IntField(default=0)
    sounds = mongo.IntField(default=0)
    sprites = mongo.IntField(default=0)
    variables = mongo.IntField(default=0)


# The part of the schema that handles result page text
class ResultText(mongo.EmbeddedDocument):
    explanation = mongo.StringField(max_length=50000, default="")
    concluding_text = mongo.StringField(max_length=50000, default="")
    comparison_reflection_text = mongo.StringField(max_length=50000, default="")
    comparison_framing_text = mongo.StringField(max_length=50000, default="")
    prompt_framing_text = mongo.StringField(max_length=50000, default="")
    stats_framing_text = mongo.StringField(max_length=50000, default="")


# Links have both text and a URL
class Link(mongo.EmbeddedDocument):
    url = mongo.URLField(max_length=2000, required=True)
    text = mongo.StringField(max_length=2000, required=True)


# The schema as a Mongoengine object.
class Challenge(mongo.Document):
    title = mongo.StringField(max_length=200)
    description = mongo.StringField(max_length=5000)
    short_label = mongo.StringField(max_length=100)
    url = mongo.EmbeddedDocumentField(Link)
    text = mongo.EmbeddedDocumentField(ResultText, required=True)
    comparison_basis = mongo.DictField(default={"basis": "__none__", "priority": []},  # yapf: disable
                                       validation=valid_comparison_basis)  # yapf: disable
    min_instructions_length = mongo.IntField(default=0)
    min_description_length = mongo.IntField(default=0)
    min_comments_made = mongo.IntField(default=0)
    min_blockify = mongo.EmbeddedDocumentField(Blockify, required=True)
    required_text = mongo.ListField(default=[[]],
                                    validation=valid_required_text)
    required_text_failure = mongo.StringField(max_length=5000)
    required_block_categories = mongo.DictField(default={})
    required_blocks = mongo.ListField(default=[],
                                      validation=valid_required_blocks)
    required_blocks_failure = mongo.StringField(max_length=5000)
    stats = mongo.ListField(default=[])
    modified = mongo.DateTimeField(default=datetime.now())


# Functions to actually work with this schema
def add_schema(mins={},
               min_blockify={},
               required_text=[],
               required_block_categories={},
               required_blocks=[],
               required_blocks_failure=None,
               required_text_failure=None,
               comparison_basis={"basis": "__none__", "priority": []},  # yapf: disable
               stats=[],
               short_label=None,
               title=None,
               description=None,
               url=None,
               text={},
               credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Adds a new challenge schema to the database. No arguments are required; but passing in no arguments is pretty useless.
    
    Args:
        mins (dict): a dictionary mapping meta names from the set
            {"instructions_length", "description_length", "comments_made"} to minimum values.
        min_blockify (dict): a dictionary mapping blockify names from the set
            {"comments", "costumes", "sounds", "sprites", "variables"} to minimum counts.
        required_text (list): a list of lists. If thought about as a list of shape (i, j),
            then required_text[i][j] is one option, along with required_text[i][j + 1] etc.,
            to satisfy required_text[i]. All required_text[i] must be satisfied to pass overall.
        required_block_categories (dict): a dict, mapping category name to minimum count
            for respective category.
        required_blocks (list): a list of dicts. Each dict maps opcode to minimum count.
            To satisfy overall requirement, at least one requirement in each dict must be
            satisfied. (That is, the list functions as "AND"; the dict functions as "OR".)
        require_blocks_failure (str): the failure message to show if block requirement isn't met.
        require_text_failure (str): the failure message to show if text requirement isn't met.
        comparison_basis (str): determines what to base code excerpts on. Must be from set of
            {"__none__", "required_text", "required_blocks", "required_block_categories"}
        stats (list): a list of studio-wide stats to feature on the project results page.
            Separate category and stat with a slash, e.g. max/comments.
        short_label (str): the short label descriptor of the prompt.
        title (str): the title of the prompt.
        description (str): the description of the prompt.
        url (dict): the URL the prompts page will feature. Is a dictionary with keys "url" and "text".
        text (dict): a dictionary mapping results page text items from the set
            {"explanation", "concluding_text", "comparison_reflection_text", "comparison_framing_text", "prompt_framing_text", "stats_framing_text"}
        credentials_file (str): path to the database credentials file.
    Returns:
        The object ID of the new challenge schema in the database. False if the arguments
        violate the validation schema.
    """

    connect_db(credentials_file)

    # Minimum blockify object
    new_min_blockify = Blockify()
    if type(min_blockify) == dict:
        if "comments" in min_blockify:
            new_min_blockify.comments = min_blockify["comments"]
        if "costumes" in min_blockify:
            new_min_blockify.costumes = min_blockify["costumes"]
        if "sounds" in min_blockify:
            new_min_blockify.sounds = min_blockify["sounds"]
        if "sprites" in min_blockify:
            new_min_blockify.sprites = min_blockify["sprites"]
        if "variables" in min_blockify:
            new_min_blockify.variables = min_blockify["variables"]

    # Text object
    result_text = ResultText()
    if type(text) == dict:
        if "explanation" in text:
            result_text.explanation = text["explanation"]
        if "concluding_text" in text:
            result_text.concluding_text = text["concluding_text"]
        if "comparison_reflection_text" in text:
            result_text.comparison_reflection_text = text[
                "comparison_reflection_text"]
        if "comparison_framing_text" in text:
            result_text.comparison_framing_text = text[
                "comparison_framing_text"]
        if "prompt_framing_text" in text:
            result_text.prompt_framing_text = text["prompt_framing_text"]

    # Required blocks
    try:
        for i in range(len(required_blocks)):
            for key in required_blocks[i]:
                required_blocks[i][key] = int(required_blocks[i][key])
    except:
        return False

    # URL object
    if url is not None:
        url = Link(url=url["url"], text=url["text"])

    # Challenge object
    challenge = Challenge(short_label=short_label,
                          title=title,
                          description=description,
                          url=url,
                          comparison_basis=comparison_basis,
                          stats=stats,
                          text=result_text,
                          min_blockify=new_min_blockify,
                          required_text=required_text,
                          required_block_categories=required_block_categories,
                          required_blocks=required_blocks,
                          required_blocks_failure=required_blocks_failure,
                          required_text_failure=required_text_failure)

    if type(mins) == dict:
        if "instructions_length" in mins:
            challenge.min_instructions_length = mins["instructions_length"]
        if "description_length" in mins:
            challenge.min_description_length = mins["description_length"]
        if "comments_made" in mins:
            challenge.min_comments_made = mins["comments_made"]

    try:
        return challenge.save()
    except:
        return False


def get_schema(schema_id, credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Gets a schema from the database.
    
    Args:
        schema_id (str): the ID of the schema.
        credentials_file (str): path to the database credentials file.
    
    Returns:
        A dictionary representation of the schema.
    """

    # Get the schema
    connect_db(credentials_file=credentials_file)
    try:
        schema = Challenge.objects(id=schema_id).first().to_mongo().to_dict()
        schema["id"] = str(schema["_id"])
    except:
        schema = dict()

    return schema


def validate_project(schema,
                     project,
                     studio_id,
                     credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Determines if the project meets the standards of a given schema.
    
    Args:
        schema: The validation schema. Can be given by its ID in the
            database or with a dictionary representing its values.
        project: The project. Given as either the Mongo object or the project_id.
        studio_id (int): The studio ID.
        credentials_file (str): path to the database credentials file.

    Returns:
        A modified version of the validation schema, revealing whether each requirement was met.
        False if couldn't successfully validate the project, as when there's no valid schema.
    """

    stat_types = [
        "block_comments",
        "blocks",
        "categories",
        "comments",
        "costumes",
        "sounds",
        "variables"
    ]
    delete_keys = [
        "description",
        "text",
        "modified",
        "required_text_failure",
        "required_blocks_failure",
        "title",
        "short_label",
        "comparison_basis"
    ]

    connect_db(credentials_file=credentials_file)

    # Get the schema in dictionary format
    if type(schema) != dict:
        schema = Challenge.objects(id=schema).first().to_mongo().to_dict()

    if schema is None:
        return False

    # Get the project in dictionary format
    if type(project) != dict:
        project = scrape.Project.objects(
            project_id=project).first().to_mongo().to_dict()

    # Start the result dictionary
    result = dict.fromkeys(schema)
    for d in delete_keys:
        if d in result:
            del result[d]

    if "title" in result:
        del result["title"]
    if "description" in result:
        del result["description"]

    # Overall schema was met variable
    result["met"] = True

    # Start off with the blockify comparisons
    bc = schema["min_blockify"]
    result["min_blockify"] = dict.fromkeys(bc)
    for key in schema["min_blockify"]:
        if key in project["stats"] and len(project["stats"][key]) >= schema["min_blockify"][key]:  # yapf: disable
            result["min_blockify"][key] = True
        else:
            result["min_blockify"][key] = False
            result["met"] = False

    # Compare left comment counts
    project_ids = scrape.Project.objects(studio_id=studio_id).values_list("project_id")  # yapf: disable
    comments_left = scrape.Comment.objects(project_id__in=project_ids,
                                           author=project["author"]).count()

    result["min_comments_made"] = comments_left >= schema["min_comments_made"]

    # Compare length of instructions and description
    result["min_instructions_length"] = len(
        project["instructions"]) >= schema["min_instructions_length"]
    result["min_description_length"] = len(
        project["description"]) >= schema["min_description_length"]

    # Check for required text
    result["required_text"] = [-1] * len(schema["required_text"])
    text_used = " ".join(project["stats"]["block_text"]["text"]).lower()
    rt = schema["required_text"]
    for i in range(len(rt)):
        for j in range(len(rt[i])):
            if rt[i][j].lower() in text_used:
                result["required_text"][i] = j
                break

    # Check for required categories
    rc = schema["required_block_categories"]
    result["required_block_categories"] = dict.fromkeys(rc)
    for category in rc:
        if project["stats"]["categories"][category] >= rc[category]:
            result["required_block_categories"][category] = True
        else:
            result["required_block_categories"][category] = False
            result["met"] = False

    # Check for required blocks
    result["required_blocks"] = [True] * len(schema["required_blocks"])
    rb = schema["required_blocks"]
    for opt in range(len(rb)):
        for opcode in rb[opt]:
            # yapf: disable
            if (not (opcode in project["stats"]["blocks"]
                     and len(project["stats"]["blocks"][opcode]) >= rb[opt][opcode])):
                result["required_blocks"][opt] = False
                break
            # yapf: enable

    # Is the schema met overall?
    result["met"] = (result["met"] and result["min_comments_made"]
                     and result["min_instructions_length"]
                     and result["min_description_length"]
                     and -1 not in result["required_text"]
                     and True in result["required_blocks"])

    return result
