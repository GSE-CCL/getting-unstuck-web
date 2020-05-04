from . import common as common
from . import authentication as authentication
import mongoengine as mongo

connect_db = common.connect_db

VALID_ADMIN_PAGES = ["users"]

def get_info(page):
    """Gets the relevant information that would be used on a given admin page.
    
    Args:
        page (str): name of the admin page.
    
    Returns:
        A dictionary mapping keys of information to whatever that information is.
            Empty dictionary if not a valid admin page name.
            Purposely broad so as to be abstract-ish.
    """
    info = dict()
    if page in VALID_ADMIN_PAGES:
        if page == "users":
            connect_db()
            info["users"] = authentication.User.objects(deleted=False).exclude("password")

    return info

def set_info(page, form):
    """Makes server-side changes as needed, and returns updated field(s) as needed.
    
    Args:
        page (str): name of the admin page.
        form (dict): the form data being passed in from the client.

    Returns:
        If successful, returns True. If not successful, returns False.
    """
    if page not in VALID_ADMIN_PAGES:
        return False
    
    if page == "users":
        connect_db()
        try:
            doc = authentication.User.objects(username=form["identifier"]).first()

            if form["action"] == "edit":
                doc.username = form["username"]
                doc.first_name = form["first_name"]
                doc.last_name = form["last_name"]
                doc.email = form["email"]
                doc.role = form["role"]
            elif form["action"] == "delete":
                doc.deleted = True
            
            doc.save()

            return True
        except:
            return False