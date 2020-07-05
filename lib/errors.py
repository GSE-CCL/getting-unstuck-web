from . import common as common
from . import settings
from datetime import datetime
import mongoengine as mongo


connect_db = common.connect_db

class Error(mongo.Document):
    error_code = mongo.IntField(required=True)
    url = mongo.URLField()
    traceback = mongo.StringField(max_length=100000)
    status = mongo.StringField(default="open")
    timestamp = mongo.DateTimeField(default=datetime.now())


def add_error(error_code, url, traceback, status="open", credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Adds an error to database, returning the ID of the error as saved.
    
    Args:
        error_code (int): the error code.
        url (str): the URL where this error occurred.
        traceback (str): the traceback.
        status (str): the status of the error, from {open, closed}. Defaults to "open."
        credentials_file (str): the path to the credentials file.

    Returns:
        The MongoDB document ID of this error, as a string.
    """

    connect_db(credentials_file)

    err = Error(error_code = error_code, url = url, traceback = traceback, status = status)
    e = err.save()
    return str(e["id"])


def get_error(eid, credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Gets an error from the database.
    
    Args:
        eid (str): the error ID.
        credentials_file (str): the path to the credentials file.
    
    Returns:
        errors.Error if found, else False.
    """

    connect_db(credentials_file)

    try:
        return Error.objects(id=eid).first()
    except:
        return False
