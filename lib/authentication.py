from . import common as common
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
from functools import wraps
import mongoengine as mongo
from mongoengine.queryset.visitor import Q
from werkzeug.security import check_password_hash, generate_password_hash

connect_db = common.connect_db

class User(mongo.Document):
    username = mongo.StringField(required=True, max_length=50, unique=True)
    first_name = mongo.StringField(required=True, max_length=200)
    last_name = mongo.StringField(required=True, max_length=200)
    email = mongo.EmailField(required=True, max_length=200, unique=True)
    password = mongo.StringField(required=True, max_length=1000)
    role = mongo.StringField(default="site_viewer")
    joined = mongo.DateTimeField(default=datetime.now())
    deleted = mongo.BooleanField(default=False)

def admin_required(f):
    """
    Decorate routes to require login with admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if user is None or "role" not in user or user["role"] != "site_admin":
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None or "_id" not in session.get("user"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@admin_required
def register_user(username, email, first_name, last_name, password, role="site_viewer"):
    """Registers a user to our database.
    
    Args:
        username (str): the username
        email (str): the email
        first_name (str): user's first name
        last_name (str): user's last name
        password (str): plaintext password
        role (str): one of site_viewer or site_admin.
            Optional; defaults to site_viewer.
    
    Returns:
        True if user added successfully, else either False or a specific error message
        to pass to the user.
    """
    site_roles = ["site_viewer", "site_admin"]

    if (username is None or username == ""
        or email is None or email == ""
        or password is None or password == ""
        or first_name is None or first_name == ""
        or last_name is None or last_name == ""
        or role not in site_roles):
       return "all fields are required"

    connect_db()
    doc = User(
        username = username,
        email = email,
        first_name = first_name,
        last_name = last_name,
        password = generate_password_hash(password),
        role = role
    )
    try:
        doc.save()
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
    return True

def login_user(username, password):
    """Logs in a user, setting a session cookie to that effect.
    
    Args:
        username (str): either username or email of user.
        password (str): plaintext password of this login attempt.
    Returns:
        True, if able to log in. Else False.
    """
    connect_db()
    account = User.objects(Q(username = username) | Q(email = username), deleted=False).first()
    if account is None or not check_password_hash(account["password"], password):
        return False
    
    account_info = {
        "user_id": str(account["id"]),
        "username": account["username"],
        "first_name": account["first_name"],
        "last_name": account["last_name"],
        "email": account["email"],
        "role": account["role"],
        "joined": account["joined"]
    }
    session["user"] = account_info

    return True

def get_login_info():
    """Returns session login info, if it exists. Else returns False."""
    if "user" in session:
        return session["user"]
    else:
        return False


def session_active():
    """True if there's a user login right now."""
    return "user" in session
