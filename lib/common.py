from ccl_scratch_tools import Parser
import json
import markdown
import mongoengine as mongo
from lib import settings


def connect_db(credentials_file=settings.DEFAULT_CREDENTIALS_FILE,
               alias="default"):
    """Connects to MongoDB using credentials.
    
    Args:
        credentials_file (str): path to the credentials file,
            or the Python dictionary containing the contents thereof.
        alias (str): alias for the connection.

    Returns:
        A MongoEngine connection instance.
    """

    # Disconnect if needed
    try:
        mongo.disconnect(alias=alias)
    except:
        pass

    credentials = get_credentials(credentials_file)

    # Return connection
    return mongo.connect(credentials["database"],
                         host=credentials["host"],
                         port=credentials["port"],
                         username=credentials["username"],
                         password=credentials["password"])


def get_credentials(credentials_file):
    """Gets credentials into a dict.
    
    Args:
        credentials_file (str): path to the credentials file,
            or the Python dictionary containing the contents thereof.

    Returns:
        credentials (dict): the credentials as a dictionary.
    """

    if type(credentials_file) == dict:
        return credentials_file
    elif type(credentials_file) == str:
        try:
            with open(credentials_file) as f:
                return json.load(f)
        except:
            return dict()


def md(text):
    """Converts Markdown to HTML, including Scratchblocks.
    
    Args:
        text (str): the Markdown to convert.

    Returns:
        A string of HTML from the converted Markdown.
    """

    text = text.replace("[sb]", '<code class="sb">')
    text = text.replace("[/sb]", "</code>")
    text = text.replace("[_sb]", '<code class="_sb">')
    text = text.replace("[/_sb]", "</code>")

    html = markdown.markdown(text)

    return html


# Jinja filters
def twodec(value):
    return f"{value:,.2f}"


def indexOf(lst, value):
    try:
        return lst.index(value)
    except ValueError:
        return -1


def pluralize(item):
    if type(item) == list:
        return "s" if len(item) != 1 else ""
    else:
        return "s" if int(item) != 1 else ""


def human_block(opcode):
    return Parser().get_block_name(opcode)


def get_selected(stat):
    selected = set()
    if "/blocks" in stat or "/block_categories" in stat:
        s = stat.split("/")
        selected.add("/".join(s[0:2]))
        selected.add(s[1])
        selected.add(s[-1])
    else:
        selected.add(stat)

    return selected
