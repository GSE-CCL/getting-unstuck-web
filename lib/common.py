import markdown
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

    # Disconnect if needed
    try:
        mongo.disconnect(alias="default")
    except:
        pass

    # Load credentials
    if type(credentials_file) == str:
        with open(credentials_file) as f:
            credentials = json.load(f)
    elif type(credentials_file) == dict:
        credentials = credentials_file

    # Return connection
    return mongo.connect(credentials["database"],
                         host=credentials["host"],
                         port=credentials["port"],
                         username=credentials["username"],
                         password=credentials["password"])


def md(text):
    """Converts Markdown to HTML, including Scratchblocks.
    
    Args:
        text (str): the Markdown to convert.

    Returns:
        A string of HTML from the converted Markdown.
    """

    text = text.replace("[sb]", '<code class="sb">')
    text = text.replace("[/sb]", "</code>")

    html = markdown.markdown(text)

    return html