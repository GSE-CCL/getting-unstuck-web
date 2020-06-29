from . import common as common
from . import schema as schema
from . import display as display
from .settings import CONVERT_URL, PROJECT_DIRECTORY
from ccl_scratch_tools import Parser, Scraper
from datetime import datetime, timedelta
from math import inf
import celery.decorators
import jinja2
import json
import logging
import mongoengine as mongo
import nltk.tokenize
import os
import random
import requests
import threading


connect_db = common.connect_db

class Comment(mongo.Document):
    comment_id = mongo.IntField(required=True)
    project_id = mongo.IntField(required=True)
    date = mongo.DateTimeField(required=True)
    author = mongo.StringField(required=True, max_length=50)
    recipient = mongo.StringField(required=True, max_length=50)
    content = mongo.StringField(required=True, max_length=10000)

class Project(mongo.Document):
    project_id = mongo.IntField(required=True, unique=True)
    title = mongo.StringField(required=True, max_length=200)
    description = mongo.StringField(required=True, max_length=5000)
    instructions = mongo.StringField(required=True, max_length=5000)
    author = mongo.StringField(required=True, max_length=50)
    stats = mongo.DictField(required=True)
    history = mongo.DictField(required=True)
    remix = mongo.DictField(required=True)
    validation = mongo.DictField(default=dict())
    studio_id = mongo.IntField(default=0)
    cache_expires = mongo.DateTimeField(default=datetime.now() + timedelta(days=30))

class Studio(mongo.Document):
    studio_id = mongo.IntField(required=True, unique=True)
    title = mongo.StringField(required=True, max_length=200)
    description = mongo.StringField(max_length=5000)
    status = mongo.StringField(max_length=100, default="complete")
    stats = mongo.DictField()
    challenge_id = mongo.ObjectIdField()
    public_show = mongo.BooleanField(default=False)


def get_project(project_id, cache_directory=None, credentials_file="secure/db.json"):
    """Retrieves a project from database and cache (if available).
    
    Args:
        project_id (int): the ID of the project to retrieve.
        cache_directory (str): if set, will get the project in JSON form.
        credentials_file (str): path to the database credentials file.
        
    Returns:
        A tuple, the first element being the database object as a dictionary, the second the Scratch project as a dictionary.

    Raises:
        ArgumentError, if project_id can't be cast to an integer.
    """

    connect_db(credentials_file=credentials_file)

    # Make sure project_id is an integer
    try:
        project_id = int(project_id)
    except:
        raise ArgumentError("project_id must be castable to an integer.")

    # Get project from database
    try:
        db = Project.objects(project_id=project_id).first().to_mongo().to_dict()
    except:
        db = dict()

    # Get project from cache
    if cache_directory is not None:
        scratch_data = get_project_from_cache(project_id, cache_directory=cache_directory)
        if scratch_data == {} and "studio_id" in db:
            add_project(project_id, studio_id=db["studio_id"], cache_directory=cache_directory, credentials_file=credentials_file)
            scratch_data = get_project_from_cache(project_id, cache_directory=cache_directory)

    return db, scratch_data


def get_project_from_cache(project_id, cache_directory="cache"):
    """Retrieves a project from the cache.
    
    Args:
        project_id (int): the ID of the project to retrieve.
        cache_directory (str): if set, will get the project in JSON form.
    
    Returns:
        The project as a dictionary. Empty if unavailable.
    """

    try:
        with open("{0}/projects/{1}.json".format(cache_directory, project_id)) as f:
            scratch_data = json.load(f)
    except:
        scratch_data = dict()

    return scratch_data

  
def get_projects_with_block(opcode, project_id=0, studio_id=0, credentials_file="secure/db.json"):
    """Finds projects with given opcode.
    
    Args:
        opcode (str): Scratch opcodes for the block type.
        project_id (int): exclude this project from the search.
        studio_id (int): limit to projects in this studio.
        credentials_file (str): path to the database credentials file.
    Returns:
        A list of projects, as stored in the database, with that opcode.
    """
    
    parser = Parser()
    connect_db(credentials_file=credentials_file)
   
    opcode_present = list()
    if parser.get_block_name(opcode) is not None:
        query = {
            "stats.blocks.{0}".format(opcode): {"$exists": True},
            "project_id": {"$ne": project_id}
        }
        if studio_id != 0:
            query["studio_id"] = studio_id

        opcode_present = Project.objects(__raw__ = query)

    return list(opcode_present)


def get_projects_with_category(category, count=1, project_id=0, studio_id=0, credentials_file="secure/db.json"):
    """Finds projects with given category.
    
    Args:
        category (str): block category name.
        count (int): minimum block count for that category.
        project_id (int): exclude this project from the search.
        studio_id (int): limit to projects in this studio.
        credentials_file (str): path to the database credentials file.
    Returns:
        A QuerySet of projects, as stored in the database, with at least the given count of blocks of the given category.
    """
    
    parser = Parser()
    connect_db(credentials_file=credentials_file)
   
    category_present = list()
    if category in parser.block_data:
        query = {
            "stats.categories.{0}".format(category): {"$gte": count},
            "project_id": {"$ne": project_id}
        }
        if studio_id != 0:
            query["studio_id"] = studio_id

        category_present = Project.objects(__raw__ = query)

    return category_present


def get_studio(studio_id, credentials_file="secure/db.json"):
    """Retrieves a studio from database.
    
    Args:
        studio_id (int): the ID of the studio to retrieve.
        credentials_file (str): path to the database credentials file.
        
    Returns:
        The studio as a dictionary.

    Raises:
        ArgumentError, if studio_id can't be cast to an integer.
    """

    connect_db(credentials_file=credentials_file)

    # Make sure studio_id is an integer
    try:
        studio_id = int(studio_id)
    except:
        raise ArgumentError("studio_id must be castable to an integer.")

    # Get studio from database
    try:
        db = Studio.objects(studio_id=studio_id).first().to_mongo().to_dict()
    except:
        db = dict()

    return db

  
def add_comments(project_id, username, credentials_file="secure/db.json"):
    """Inserts a project's comments into the database. These are public comments on the project itself, not code comments.
    
    Args:
        project_id (int): the ID of the project whose comments we're scraping.
        username (str): the username of the user who created the project.
        credentials_file (str): path to the database credentials file.

    Returns:
        None.
    """
    
    # DB connection
    connect_db(credentials_file=credentials_file)

    # Scrape comments
    scraper = Scraper()
    comments = scraper.get_project_comments(project_id)

    for comment in comments:
        preexisting = Comment.objects(project_id=project_id, comment_id=comment["id"]).first()

        if not preexisting:
            timestamp = datetime.strptime(comment["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            doc = Comment(
                comment_id = comment["id"],
                project_id = project_id,
                date = timestamp,
                author = comment["username"],
                recipient = username,
                content = comment["comment"]
            )
            doc.save()

    logging.debug("successfully scraped comments for project {}".format(project_id))


def add_project(project_id, studio_id=0, cache_directory=None, credentials_file="secure/db.json"):
    """Inserts a project into the database after scraping it. Updates existing database entries.
    
    Args:
        project_id (int): the ID of the project to scrape.
        studio_id (int): the studio ID with which this project should be associated.
        cache_directory (str): if set, will save this project
            JSON into the cache directory specified.
        credentials_file (str): path to the database credentials file.
    
    Returns:
        True, if a new insertion or if updated a record. False if Scratch 2.

    Raises:
        IOError: if couldn't write the JSON file to the given cache_directory.
    """

    # Gather information about the project
    scraper = Scraper()
    scratch_data = scraper.download_project(project_id)
    metadata = scraper.get_project_meta(project_id)

    # Convert to SB3 if possible
    parser = Parser()

    if not parser.is_scratch3(scratch_data) and CONVERT_URL != "":
        try:
            r = requests.post(CONVERT_URL, json=scratch_data)
            scratch_data = json.loads(r.json())
        except:
            pass

    # Save to cache if needed
    if cache_directory is not None:
        if scraper.make_dir(f"{cache_directory}/projects"):
            with open("{0}/projects/{1}.json".format(cache_directory, project_id), "w") as f:
                try:
                    json.dump(scratch_data, f)
                except:
                    raise IOError("Couldn't write the JSON file to directory {0}".format(cache_directory))

    # Parse the project using the parser class
    try:
        if parser.is_scratch3(scratch_data):
            stats = parser.blockify(scratch_data = scratch_data)
            if stats["blocks"] == False or stats["categories"] == False:
                stats = False
        else:
            stats = False
    except:
        stats = False

    if not stats:
        logging.warning("Couldn't get statistics for project {}".format(project_id))
        return False

    # Change block_text's form
    text_new = {"text": [], "blocks": []}
    for text in stats["block_text"]:
        text_new["text"].append(text)
        text_new["blocks"].append(stats["block_text"][text])
    stats["block_text"] = text_new

    # Check database for existing project with project_id
    connect_db(credentials_file=credentials_file)
    preexisting = Project.objects(project_id=project_id).first()

    if preexisting:
        # Update a few fields
        doc = preexisting
        doc.title = metadata["title"]
        doc.description = metadata["description"]
        doc.instructions = metadata["instructions"]
        doc.history = metadata["history"]
        doc.remix = metadata["remix"]
        doc.stats = stats

        if studio_id > 0:
            doc.studio_id = studio_id

        if cache_directory is not None:
            doc.cache_expires = datetime.now() + timedelta(days=30)
    else:
        # Create a new record
        doc = Project(
            project_id = project_id,
            title = metadata["title"],
            description = metadata["description"],
            instructions = metadata["instructions"],
            author = metadata["author"]["username"],
            history = metadata["history"],
            remix = metadata["remix"],
            studio_id = studio_id,
            stats = stats
        )

    doc.save()
    add_comments(project_id, metadata["author"]["username"], credentials_file=credentials_file)

    # Validate against studio's schema, if available
    if studio_id > 0:
        challenge = Studio.objects(studio_id=studio_id).only("challenge_id").first()
        if challenge is not None and challenge["challenge_id"] is not None:
            validation = schema.validate_project(challenge["challenge_id"], project_id, studio_id, credentials_file=credentials_file)
            del validation["_id"]
            doc.validation[str(challenge["challenge_id"])] = validation
            doc.save()

    logging.debug("successfully scraped project {}".format(project_id))

    return True


@celery.decorators.task
def add_studio(studio_id, schema=None, show=False, cache_directory=None, credentials_file="secure/db.json"):
    """Scrapes a studio and inserts it into the database.
    
    Args:
        studio_id (int): the ID of the studio to scrape.
        schema (str): the object ID of the schema associated with this studio.
        show (bool): whether to show the studio on the public Challenges page.
        cache_directory (str): if set, will save this project
            JSON into the cache directory specified.
        credentials_file (str): path to the database credentials file.
    
    Returns:
        None.

    Raises:
        IOError: if couldn't write the JSON file to the given cache_directory.
    """
    
    # Load scraper class
    scraper = Scraper()

    # Add individual studio to DB    
    studio_info = scraper.get_studio_meta(studio_id)
    if studio_info is not None:
        logging.info("attempting to scrape studio {}".format(studio_id))
        connect_db(credentials_file=credentials_file)

        preexisting = Studio.objects(studio_id=studio_id).first()
        if preexisting:
            # Update a few fields
            doc = preexisting
            doc.title = studio_info["title"]
            doc.description = studio_info["description"]
            doc.status = "in_progress"
            
            if show is not None:
                doc.public_show = show
        else:
            # New studio altogether
            doc = Studio(
                studio_id = studio_id,
                title = studio_info["title"],
                description = studio_info["description"],
                status = "in_progress",
                public_show = show
            )
    
        if schema is not None:
            doc.challenge_id = schema

        doc.save()

        # Add all the projects
        project_ids = scraper.get_projects_in_studio(studio_id)
        for i, project in enumerate(project_ids):
            add_project(project, studio_id=studio_id, cache_directory=cache_directory, credentials_file=credentials_file)
            if i % 10 == 0:
                logging.info("completed {}/{} projects in studio {}".format(i, len(project_ids), studio_id))

        stats = get_studio_stats(studio_id, credentials_file=credentials_file)

        preexisting = Studio.objects(studio_id=studio_id).first()
        if preexisting is not None:
            preexisting.status = "complete"
            preexisting.stats = stats
            preexisting.save()

        logging.info("successfully scraped studio {}".format(studio_id))


def get_default_studio_stats():
    """Returns the default studio stats dictionary."""

    return {
        "mean": {
            "description": 0,
            "instructions": 0,
            "comments": 0,
            "blocks": {},
            "block_categories": {},
            "costumes": 0,
            "sounds": 0,
            "variables": 0
        },
        "min": {
            "description": 0,
            "instructions": 0,
            "comments": 0,
            "blocks": {},
            "block_categories": {},
            "costumes": 0,
            "sounds": 0,
            "variables": 0
        },
        "max": {
            "description": 0,
            "instructions": 0,
            "comments": 0,
            "blocks": {},
            "block_categories": {},
            "costumes": 0,
            "sounds": 0,
            "variables": 0
        },
        "total": {
            "description_words": 0,
            "instructions_words": 0,
            "blocks": {},
            "block_count": 0,
            "block_categories": {},
            "comments_left": 0,
            "costumes": 0,
            "sounds": 0,
            "variables": 0,
            "number_projects": 0
        }
    }


def get_studio_stats(studio_id, credentials_file="secure/db.json"):
    """Returns a dictionary of statistics about a studio.
    
    Args:
        studio_id (int): the ID of the studio to scrape.
        credentials_file (str): path to the database credentials file.
    
    Returns:
        A dictionary of statistics, including mean, min, and max.
    """

    logging.info("calculating statistics for studio {}".format(studio_id))
    
    connect_db(credentials_file=credentials_file)
    projects = Project.objects(studio_id=studio_id)
    
    stats = get_default_studio_stats()
    for key in stats:
        stats[key]["number_projects"] = len(projects)

    # Calculate mean values
    no_direct_average = ["blocks", "block_categories", "number_projects"]
    top_level = ["description", "instructions"]
    for project in projects:
        for key in stats["mean"]:
            if key not in no_direct_average:
                if key in top_level:
                    stats["mean"][key] += len(project[key])
                    stats["min"][key] = min(stats["min"][key], len(project[key]))
                    stats["max"][key] = max(stats["max"][key], len(project[key]))
                else:
                    stats["mean"][key] += len(project["stats"][key])
                    stats["min"][key] = min(stats["min"][key], len(project["stats"][key]))
                    stats["max"][key] = max(stats["max"][key], len(project["stats"][key]))

        for block in project["stats"]["blocks"]:
            if block not in stats["mean"]["blocks"]:
                stats["mean"]["blocks"][block] = 0
                stats["min"]["blocks"][block] = inf
                stats["max"]["blocks"][block] = - inf

            stats["mean"]["blocks"][block] += len(project["stats"]["blocks"][block])
            stats["min"]["blocks"][block] = min(stats["min"]["blocks"][block], len(project["stats"]["blocks"][block]))
            stats["max"]["blocks"][block] = max(stats["max"]["blocks"][block], len(project["stats"]["blocks"][block]))
        for cat in project["stats"]["categories"]:
            if cat not in stats["mean"]["block_categories"]:
                stats["mean"]["block_categories"][cat] = 0
                stats["min"]["block_categories"][cat] = inf
                stats["max"]["block_categories"][cat] = - inf

            stats["mean"]["block_categories"][cat] += project["stats"]["categories"][cat]
            stats["min"]["block_categories"][cat] = min(stats["min"]["block_categories"][cat], project["stats"]["categories"][cat])
            stats["max"]["block_categories"][cat] = max(stats["max"]["block_categories"][cat], project["stats"]["categories"][cat])
    
    # Handle means, totals for top-level keys
    for key in stats["mean"]:
        if key not in no_direct_average:
            if key in stats["total"]:
                stats["total"][key] = stats["mean"][key]
            if len(projects) > 0:
                stats["mean"][key] /= len(projects)

    # Handle means, totals for blocks
    for block in stats["mean"]["blocks"]:
        stats["total"]["blocks"][block] = stats["mean"]["blocks"][block]
        stats["total"]["block_count"] += stats["mean"]["blocks"][block]
        if len(projects) > 0:
            stats["mean"]["blocks"][block] /= len(projects)

    # Handle means, totals for block categories
    for cat in stats["mean"]["block_categories"]:
        stats["total"]["block_categories"][cat] = stats["mean"]["block_categories"][cat]
        if len(projects) > 0:
            stats["mean"]["block_categories"][cat] /= len(projects)

    # Get total comments left on projects
    pids = projects.all().values_list("project_id")
    stats["total"]["comments_left"] = Comment.objects(project_id__in=pids).count()

    # Get total words left in instructions and descriptions
    for project in projects:
        stats["total"]["description_words"] += len(nltk.tokenize.word_tokenize(project["description"]))
        stats["total"]["instructions_words"] += len(nltk.tokenize.word_tokenize(project["instructions"]))


    return stats
