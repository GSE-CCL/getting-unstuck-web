import json
import threading
import time
import urllib
from flask import Flask, redirect, render_template, request, session
from ccl_scratch_tools import Parser
from ccl_scratch_tools import Scraper

from lib import common
from lib import scrape
from lib import authentication
from lib import admin
from lib.authentication import admin_required, login_required

CACHE_DIRECTORY = "cache"

app = Flask(__name__)

def twodec(value):
    return f"{value:,.2f}"

app.jinja_env.filters["twodec"] = twodec
app.secret_key = "hithere"

# Helper routes
@app.route("/redirect", methods=["GET"])
def redirect_to():
    if request.args.get("username") is not None and request.args.get("username") != "":
        return redirect("/user/{0}".format(urllib.parse.quote(request.args.get("username"))))
    else:
        return render_template("index.html", message="Sorry! I wasn't able to do that.", user=authentication.get_login_info())

# Authentication
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else:
        if (request.form["username"] is None
            or request.form["username"] == ""
            or request.form["password"] is None
            or request.form["password"] == ""):
            return render_template("login.html", message="All fields are required!")
        
        res = authentication.login_user(request.form["username"], request.form["password"])
        if res:
            return redirect("/")
        else:
            return render_template("login.html", message="Couldn't log in with that username/password combination!")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return render_template("login.html", message="Successfully logged out.")

@app.route("/register", methods=["POST"])
def register():
    res = authentication.register_user(
        request.form["username"],
        request.form["email"],
        request.form["first_name"],
        request.form["last_name"],
        request.form["password"],
        request.form["user_role"]
    )

    if type(res) == bool and res:
        return redirect("/login")
    else:
        return render_template("index.html", message="One or several of your inputs were invalid.")

# For when the site is brand new
@app.route("/setup", methods=["GET"])
def setup():
    common.connect_db()
    if len(authentication.User.objects()) == 0:
        session["user"] = {"role": "site_admin"}
        return render_template("setup.html")
    else:
        return redirect("/")

# Admin pages
@app.route("/admin")
@admin_required
def admin_index():
    return render_template("admin/index.html", valid_admin_pages=admin.VALID_ADMIN_PAGES, user=authentication.get_login_info())

@app.route("/admin/<page>", methods=["GET", "POST"])
@admin_required
def admin_page(page):
    if page in admin.VALID_ADMIN_PAGES:
        if request.method == "GET":
            info = admin.get_info(page)
            return render_template("admin/{0}.html".format(page), info=info, user=authentication.get_login_info())
        else:
            result = admin.set_info(page, request.form)
            return json.dumps(result)
    else:
        return redirect("/admin")

@app.route("/admin/schema/add", methods=["GET", "POST"])
@admin_required
def add_schema():
    parser = Parser()
    if request.method == "GET":
        blocks = parser.block_data
        block_list = list()
        block_dict = dict()
        for cat in blocks:
            block_list += blocks[cat].keys()
            for block in blocks[cat]:
                block_dict[blocks[cat][block].lower().replace(" ", "")] = block
        return render_template("add_schema.html", blocks=blocks, block_dict=block_dict, block_list=block_list, categories=list(blocks.keys()), user=authentication.get_login_info())
    else:
        # TODO
        return redirect("/")

# Studios, projects, users, challenges
@app.route("/")
def homepage():
    return render_template("index.html", user=authentication.get_login_info()) 

@app.route("/project/<pid>", methods=["GET"])
def project_id(pid):
    common.connect_db()
    project = scrape.Project.objects(project_id=pid).first()
    studio = scrape.Studio.objects(studio_id=project["studio_id"]).first()

    return render_template("project.html", project=project, studio=studio, user=authentication.get_login_info())

@app.route("/studio", methods=["GET", "POST"])
@admin_required
def studio():
    if request.method == "GET":
        return render_template("studio.html", user=authentication.get_login_info())
    else:
        scraper = Scraper()
        sid = scraper.get_id(request.form["studio"])

        if sid is not None:
            scrape.add_studio(sid, cache_directory=CACHE_DIRECTORY)
            return redirect("/studio/{0}".format(sid))
        else:
            return render_template("studio.html", message="Please enter a valid studio ID or URL.", user=authentication.get_login_info())

@app.route("/studio/<sid>")
def studio_id(sid):
    if sid == "":
        return redirect("/studio")

    common.connect_db()
    studio = scrape.Studio.objects(studio_id = sid).first()
    projects = list(scrape.Project.objects(studio_id = sid))

    message = None
    if studio["status"] == "in_progress":
        message = "This studio is currently in the process of being downloaded and analyzed. <a href=''>Refresh page.</a>"

    return render_template("studio_id.html", projects=projects, studio=studio, message=message, user=authentication.get_login_info())

@app.route("/user/<username>")
def user_id(username):
    common.connect_db()
    projects = list(scrape.Project.objects(author = username))
    studios = dict()
    for project in projects:
        if project["studio_id"] not in studios:
            studios[project["studio_id"]] = scrape.Studio.objects(studio_id = project["studio_id"]).first()

    return render_template("username.html", projects=projects, studios=studios, username=username, user=authentication.get_login_info())

if __name__ == "__main__":
    app.run()
