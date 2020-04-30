from ccl_scratch_tools import Parser, Scraper
from datetime import datetime, timedelta
from flask_socketio import emit
from math import inf
import json
import mongoengine as mongo
import os
import threading

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
    studio_id = mongo.IntField(default=0)
    cache_expires = mongo.DateTimeField(default=datetime.now() + timedelta(days=30))

class Studio(mongo.Document):
    studio_id = mongo.IntField(required=True, unique=True)
    title = mongo.StringField(required=True, max_length=200)
    description = mongo.StringField(max_length=5000)
    status = mongo.StringField(max_length=100, default="complete")
    stats = mongo.DictField()

def connect_db(credentials_file="secure/db.json"):
    """Connects to MongoDB using credentials.
    
    Args:
        credentials_file (str): path to the credentials file,
            or the Python dictionary containing the contents thereof.

    Returns:
        A MongoEngine connection instance.
    """
    
    if type(credentials_file) == str:
        with open(credentials_file) as f:
            credentials = json.load(f)
    elif type(credentials_file) == dict:
        credentials = credentials_file

    return mongo.connect(credentials["database"],
                         host=credentials["host"],
                         port=credentials["port"],
                         username=credentials["username"],
                         password=credentials["password"])

def get_projects_with_block(opcode, project_id=0, studio_id=0, credentials_file="secure/db.json"):
    """Finds projects with given opcode.
    
    Args:
        opcode (str): the Scratch opcode for the block type.
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

def add_project(project_id, studio_id=0, cache_directory=None, credentials_file="secure/db.json"):
    """Inserts a project into the database after scraping it. Updates existing database entries.
    
    Args:
        project_id (int): the ID of the project to scrape.
        studio_id (int): the studio ID with which this project should be associated.
        cache_directory (str): if set, will save this project
            JSON into the cache directory specified.
        credentials_file (str): path to the database credentials file.
    
    Returns:
        True, if a new insertion. False, if updated a record. False if Scratch 2.

    Raises:
        IOError: if couldn't write the JSON file to the given cache_directory.
    """

    # Gather information about the project
    scraper = Scraper()
    scratch_data = scraper.download_project(project_id)
    metadata = scraper.get_project_meta(project_id)

    # Save to cache if needed
    if cache_directory is not None:
        with open("{0}/{1}.json".format(cache_directory, project_id), "w") as f:
            try:
                json.dump(scratch_data, f)
            except:
                raise IOError("Couldn't write the JSON file to directory {0}".format(cache_directory))

    # Parse the project using the parser class
    parser = Parser()
    stats = parser.blockify(scratch_data = scratch_data)
    if not stats:
        return False

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
        doc.stats = stats

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

    return not preexisting

def add_studio(studio_id, cache_directory=None, credentials_file="secure/db.json"):
    """Scrapes a studio and inserts it into the database.
    
    Args:
        studio_id (int): the ID of the studio to scrape.
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
        connect_db(credentials_file=credentials_file)

        preexisting = Studio.objects(studio_id=studio_id).first()
        if preexisting:
            # Update a few fields
            doc = preexisting
            doc.title = studio_info["title"]
            doc.description = studio_info["description"]
            doc.status = "in_progress"
        else:
            # New studio altogether
            doc = Studio(
                studio_id = studio_id,
                title = studio_info["title"],
                description = studio_info["description"],
                status = "in_progress"
            )
        doc.save()

        # Start a new thread so we can return a webpage
        def add_projects():
            # Add all the projects
            project_ids = scraper.get_projects_in_studio(studio_id)
            for project in project_ids:
                add_project(project, studio_id=studio_id, cache_directory=cache_directory, credentials_file=credentials_file)

            stats = get_studio_stats(studio_id, credentials_file=credentials_file)

            preexisting = Studio.objects(studio_id=studio_id).first()
            preexisting.status = "complete"
            preexisting.stats = stats
            preexisting.save()
        
        studio_thread = threading.Thread(target=add_projects)
        studio_thread.start()

def get_studio_stats(studio_id, credentials_file="secure/db.json"):
    """Returns a dictionary of statistics about a studio.
    
    Args:
        studio_id (int): the ID of the studio to scrape.
        credentials_file (str): path to the database credentials file.
    
    Returns:
        A dictionary of statistics, including mean, min, and max.
    """
    
    connect_db(credentials_file=credentials_file)
    projects = Project.objects(studio_id=studio_id)
    
    stats = {
        "mean": {
            "description": 0,
            "instructions": 0,
            "comments": 0,
            "blocks": {},
            "block_categories": {},
            "costumes": 0,
            "sounds": 0,
            "variables": 0,
            "number_projects": len(projects)
        },
        "min": {
            "description": 0,
            "instructions": 0,
            "comments": 0,
            "blocks": {},
            "block_categories": {},
            "costumes": 0,
            "sounds": 0,
            "variables": 0,
            "number_projects": len(projects)
        },
        "max": {
            "description": 0,
            "instructions": 0,
            "comments": 0,
            "blocks": {},
            "block_categories": {},
            "costumes": 0,
            "sounds": 0,
            "variables": 0,
            "number_projects": len(projects)
        }
    }

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
    
    for key in stats["mean"]:
        if key not in no_direct_average:
            stats["mean"][key] /= len(projects)
    for block in stats["mean"]["blocks"]:
        stats["mean"]["blocks"][block] /= len(projects)
    for cat in stats["mean"]["block_categories"]:
        stats["mean"]["block_categories"][cat] /= len(projects)

    return stats