import mongoengine as mongo
import json

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
