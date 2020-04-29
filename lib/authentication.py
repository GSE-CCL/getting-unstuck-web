from flask import Flask, redirect, render_template, request, session
from functools import wraps

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
        if session.get("user") is None or "id" not in session.get("user"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
