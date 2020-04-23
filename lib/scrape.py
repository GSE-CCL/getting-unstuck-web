from ccl_scratch_tools import Parser, Scraper
from datetime import datetime, timedelta
import json
import mongoengine as mongo
import os

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

class Comment(mongo.Document):
    comment_id = mongo.IntField(required=True)
    project_id = mongo.IntField(required=True)
    date = mongo.DateTimeField(required=True)
    author = mongo.StringField(required=True, max_length=50)
    recipient = mongo.StringField(required=True, max_length=50)
    content = mongo.StringField(required=True, max_length=10000)

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
        True, if a new insertion. False, if updated a record.

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
    
    # Get project IDs
    scraper = Scraper()
    project_ids = scraper.get_projects_in_studio(studio_id)

    # Add all the projects
    for project in project_ids:
        add_project(project, studio_id=studio_id, cache_directory=cache_directory, credentials_file=credentials_file)
