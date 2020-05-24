from . import common as common
from . import authentication as authentication
from . import scrape as scrape
from . import schema as schema
from flask import session
import mongoengine as mongo
from werkzeug.security import generate_password_hash

connect_db = common.connect_db

VALID_ADMIN_PAGES = ["schemas", "studios", "users"]

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
        elif page == "studios":
            connect_db()
            info["studios"] = scrape.Studio.objects()
        elif page == "schemas":
            connect_db()
            info["schemas"] = schema.Challenge.objects()

    return info

def set_info(page, form):
    """Makes server-side changes as needed, and returns updated field(s) as needed.
    
    Args:
        page (str): name of the admin page.
        form (dict): the form data being passed in from the client.

    Returns:
        If successful, returns True. If not successful, returns False.
    """
    if page not in VALID_ADMIN_PAGES or "action" not in form:
        return False
    
    if page == "users":
        connect_db()
        if form["action"] == "add":
            return authentication.register_user(form["username"], 
                                                form["email"],
                                                form["first_name"],
                                                form["last_name"],
                                                form["password"],
                                                form["role"])
        try:
            if "identifier" not in form and "username" in form:
                form["identifier"] = form["username"]

            doc = authentication.User.objects(username=form["identifier"]).first()

            if form["action"] == "edit":
                doc.username = form["username"]
                doc.first_name = form["first_name"]
                doc.last_name = form["last_name"]
                doc.email = form["email"]
                doc.role = form["role"]
            elif form["action"] == "delete" and form["identifier"] != session["user"]["username"]:
                doc.deleted = True
            elif form["action"] == "reset_password":
                doc.password = generate_password_hash(form["password"])
            else:
                return False
            
            doc.save()

            return True
        except mongo.errors.NotUniqueError as e:
            e = str(e)
            if "username" in e:
                return "username is already in use"
            elif "email" in e:
                return "email is already in use"
            else:
                return False
        except:
            return False
    elif page == "studios":
        connect_db()
        if form["action"] == "delete":
            try:
                doc = scrape.Studio.objects(studio_id=form["identifier"]).first()
                doc.delete()
                return True
            except:
                return False
    elif page == "schemas":
        connect_db()
        if form["action"] == "delete":
            try:
                doc = schema.Challenge.objects(id=form["identifier"]).first()
                doc.delete()
                return True
            except:
                return False
        elif form["action"] == "edit":
            # Handle title, etc.
            if form["title"].replace(" ", "") == "":
                title = None
            else:
                title = form["title"]
            if form["description"].replace(" ", "") == "":
                description = None
            else:
                description = form["description"]

            # If inserting a new schema
            if form["id"] == "__new__":
                result = schema.add_schema(mins=form["mins"],
                                           min_blockify=form["min_blockify"],
                                           required_text=form["required_text"],
                                           required_block_categories=form["required_block_categories"],
                                           required_blocks=form["required_blocks"],
                                           title=title,
                                           description=description)
                if not result:
                    return False
                else:
                    return True
            else:
                try:
                    doc = schema.Challenge.objects(id = form["id"]).first()
                    doc.title = title
                    doc.description = description
                    doc.min_instructions_length = form["mins"]["instructions_length"]
                    doc.min_description_length = form["mins"]["description_length"]
                    doc.min_comments_made = form["mins"]["comments_made"]
                    doc.min_blockify = schema.Blockify(comments=form["min_blockify"]["comments"],
                                                    costumes=form["min_blockify"]["costumes"],
                                                    sounds=form["min_blockify"]["sounds"],
                                                    sprites=form["min_blockify"]["sprites"],
                                                    variables=form["min_blockify"]["variables"])
                    doc.required_block_categories = form["required_block_categories"]
                    doc.required_blocks = form["required_blocks"]
                    doc.required_text = form["required_text"]

                    doc.save()
                    return True
                except:
                    return False
        else:
            return False
    else:
        return False
