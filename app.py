import json
import logging
import markdown
import os
import threading
import time
import traceback
import random
import urllib
from flask import Flask, redirect, render_template, request, session
from flask_caching import Cache
from ccl_scratch_tools import Parser
from ccl_scratch_tools import Scraper
from ccl_scratch_tools import Visualizer
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError, NotFound

from lib import common
from lib import errors
from lib import schema
from lib import scrape
from lib import tasks
from lib import authentication
from lib import admin
from lib import display
from lib.authentication import admin_required, login_required
from lib.settings import CACHE_DIRECTORY, CLRY, PROJECT_CACHE_LENGTH, REDIRECT_PAGES, SITE


app = Flask(__name__)

try:
    celery = tasks.make_celery(CLRY["name"], CLRY["result_backend"], CLRY["broker_url"], app)
except:
    logging.warn("Couldn't load celery.")

parser = Parser()

app.jinja_env.filters["twodec"] = common.twodec
app.jinja_env.filters["indexOf"] = common.indexOf
app.jinja_env.filters["pluralize"] = common.pluralize
app.jinja_env.filters["human_block"] = common.human_block
app.jinja_env.filters["get_selected"] = common.get_selected
app.secret_key = os.urandom(24)
app.url_map.strict_slashes = False

app.config["CACHE_TYPE"] = "lib.cache.MongoCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 1200

cache = Cache(app)

# Pass things to all templates
@app.context_processor
def inject_vars():
    return dict(user=authentication.get_login_info(), valid_admin_pages=admin.VALID_ADMIN_PAGES, SITE=SITE)

# Helper routes
@app.route("/redirect", methods=["GET"])
def redirect_to():
    if request.args.get("username") is not None and request.args.get("username") != "":
        return redirect("/user/{0}".format(urllib.parse.quote(request.args.get("username"))))
    else:
        return render_template("index.html", message="Sorry! I wasn't able to do that.")

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
            return redirect("/admin")
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
    return render_template("admin/index.html")

@app.route("/admin/<page>", methods=["GET", "POST"])
@admin_required
def admin_page(page):
    if page in admin.VALID_ADMIN_PAGES:
        if request.method == "GET":
            info = admin.get_info(page)
            return render_template("admin/{0}.html".format(page), info=info)
        else:
            if request.is_json:
                form = request.get_json()
            else:
                form = request.form
            result = admin.set_info(page, form)

            if "redirect" in request.form:
                if request.form["redirect"] in admin.VALID_REDIRECTS:
                    return redirect(request.form["redirect"])

            return json.dumps(result)
    else:
        return redirect("/admin")

@app.route("/admin/error/<eid>")
@admin_required
def error_page(eid):
    error = errors.get_error(eid)
    if not error:
        return redirect("/admin/errors")
    else:
        issue = {
            "title": "{} error when loading {}".format(error["error_code"], urllib.parse.urlparse(error["url"]).path),
            "body": "**[Replicate here]({})**\n\nWhen accessing `{}`, there's a {} error. The traceback says:\n\n```python\n{}\n```".format(error["url"], urllib.parse.urlparse(error["url"]).path, error["error_code"], error["traceback"])
        }
        
        return render_template("admin/error.html", error=error, issue=issue)

def schema_editor(id):
    data = {
        "min_instructions_length": 0,
        "min_description_length": 0,
        "min_comments_made": 0,
        "min_blockify": {
            "comments": 0,
            "costumes": 0,
            "sounds": 0,
            "sprites": 0,
            "variables": 0
        },
        "required_text": [],
        "required_block_categories": {},
        "required_blocks": [],
        "stats": [],
        "text": {},
        "comparison_basis": {"basis": "__none__", "priority": None}
    }

    if id != "__new__":
        common.connect_db()
        try:
            data = schema.Challenge.objects(id = id).first().to_mongo()
        except AttributeError:
            raise NotFound()

    blocks = parser.block_data
    block_list = list()
    block_dict = dict()

    for cat in blocks:
        block_list += blocks[cat].keys()

        for block in blocks[cat]:
            block_dict[blocks[cat][block].lower().replace(" ", "")] = block

    return render_template("admin/edit_schema.html", blocks=blocks, block_dict=block_dict, block_list=block_list, categories=list(blocks.keys()), data=data, schema_id=id, stats=scrape.get_default_studio_stats())

@app.route("/admin/schemas/edit", methods=["GET"])
@admin_required
def add_schema():
    return schema_editor("__new__")

@app.route("/admin/schemas/edit/<id>", methods=["GET"])
@admin_required
def edit_schema(id):
    return schema_editor(id)

# Studios, projects, users, challenges
@app.route("/participation")
def index():
    return render_template("index.html")

@app.route("/md", methods=["POST"])
def md():
    text = request.form["text"]
    if text is not None:
        ret = {
            "html": common.md(text),
            "js": "/static/js/sb.js"
        }

        return json.dumps(ret)
    return "False"

@app.route("/project/d", methods=["POST"])
def project_download():
    if request.form["sid"] is None or request.form["pid"] is None:
        return "False"
    sid = request.form["sid"]
    pid = request.form["pid"]

    scraper = Scraper()
    try:
        pid = int(pid)
    except:
        return "False"
    
    if pid in scraper.get_projects_in_studio(sid):
        return str(scrape.add_project(pid, sid, CACHE_DIRECTORY))
    else:
        return "False"


@app.route("/project/f/<pid>", methods=["POST"])
def project_feedback(pid):
    if ("_gu_uid" in request.cookies
        and "feelings" in request.json
        and "minutes" in request.json):
        try:
            common.connect_db()
            reflection = scrape.ProjectReflection(project_id = pid,
                                                  gu_uid = request.cookies.get("_gu_uid"),
                                                  minutes = int(request.json["minutes"]),
                                                  feelings = request.json["feelings"])
            reflection.save()
            return "True"
        except:
            return "False"
    else:
        return "False"


@app.route("/project/o/<pid>")
def feedback_owner(pid):
    try:
        common.connect_db()
        reflection = scrape.ProjectReflection.objects(project_id=pid).order_by("-timestamp").first()
        return reflection["gu_uid"]
    except:
        return ""


@app.route("/project/r/<pid>")
def reload_project(pid):
    try:
        pid = int(pid)
    except:
        pid = 0

    scrape.set_reload_page(pid)
    return redirect("/project/{}".format(pid))


@app.route("/project/<pid>/view", methods=["GET"])
@cache.cached(timeout=PROJECT_CACHE_LENGTH, forced_update=scrape.get_reload_project)
def project__id(pid):
    return display.get_project_page(pid, CACHE_DIRECTORY)


@app.route("/project/<pid>", methods=["GET"])
def project_id(pid):
    return render_template("project_loader.html")


@app.route("/studio", methods=["GET", "POST"])
@admin_required
def studio():
    if request.method == "GET":
        common.connect_db()
        return render_template("studio.html", schemas=list(schema.Challenge.objects().order_by("-modified")))
    else:
        scraper = Scraper()
        sid = scraper.get_id(request.form["studio"])

        s = None
        if request.form["schema"] != "__none__":
            s = request.form["schema"]

        if sid is not None:
            scrape.add_studio.delay(sid, schema=s, show=("show" in request.form), cache_directory=CACHE_DIRECTORY)
            return redirect("/studio/{0}".format(sid))
        else:
            return render_template("studio.html", message="Please enter a valid studio ID or URL.")

@app.route("/studio/<sid>")
def studio_id(sid):
    if sid == "":
        return redirect("/prompts")

    common.connect_db()
    studio = scrape.Studio.objects(studio_id = sid).first()

    if studio is None:
        return redirect("/prompts")

    projects = list(scrape.Project.objects(studio_id = sid))
    info = {"authors": list(), "project_ids": list(), "titles": list()}

    for project in projects:
        info["authors"].append(project["author"].lower())
        info["project_ids"].append(project["project_id"])
        info["titles"].append(project["title"].lower())

    message = None
    if studio["status"] == "in_progress" or studio["status"] is None:
        message = "This studio is currently in the process of being downloaded and analyzed. <a href=''>Refresh page.</a>"

    return render_template("studio_id.html", info=info, projects=projects, studio=studio, message=message)

@app.route("/user/<username>")
def user_id(username):
    common.connect_db()
    projects = list(scrape.Project.objects(author = username.lower()))
    studios = dict()

    keep_projects = list()
    for i, project in enumerate(projects):
        if project["studio_id"] not in studios:
            studio = scrape.Studio.objects(studio_id = project["studio_id"]).first()
            
            if studio is not None:
                studios[project["studio_id"]] = studio
                keep_projects.append(project)
        else:
            keep_projects.append(project)

    return render_template("username.html", projects=keep_projects, studios=studios, username=username)

@app.route("/prompts", methods=["GET"])
def prompts():
    common.connect_db()
    studios = list(scrape.Studio.objects(public_show=True))
    schema_ids = set()
    for studio in studios:
        if "challenge_id" not in studio:
            studios.remove(studio)
            break

        schema_ids.add(studio["challenge_id"])

    schemas = schema.Challenge.objects(id__in=schema_ids).order_by("short_label", "title")
    id_order = list(schemas.values_list("id"))

    for i in range(len(id_order)):
        id_order[i] = str(id_order[i])

    schemas = schemas.as_pymongo()

    new_schemas = dict()
    for sc in schemas:
        new_schemas[str(sc["_id"])] = sc
    
    # Order the studios
    ordered_studios = [None] * len(studios)
    for studio in studios:
        studio["challenge_id"] = str(studio["challenge_id"])

        try:
            ordered_studios[id_order.index(studio["challenge_id"])] = studio
        except ValueError:
            pass

    return render_template("prompts.html",
                           challenges=ordered_studios,
                           schemas=new_schemas)

@app.route("/summary", methods=["GET"])
def summarize():
    return render_template("summary.html")

# Static pages -- About, Strategies, Signup, Research
@app.route("/")
@cache.cached()
def homepage():
    return render_template("home.html", section="home") 

@app.route("/about", methods=["GET"])
@cache.cached()
def about():
    return render_template("about.html")

@app.route("/strategies", methods=["GET"])
@cache.cached()
def strategies():
    return render_template("strategies.html")

@app.route("/signup", methods=["GET", "POST"])
@cache.cached()
def signup():
    return render_template("signup.html")

@app.route("/research", methods=["GET"])
@cache.cached()
def research():
    return render_template("research.html")


# Error pages
@app.route("/ie")
@cache.cached()
def ie():
    return render_template("ie.html")


def error(e):
    """Handle errors."""

    if e.code == 404 and request.path in REDIRECT_PAGES:
        return redirect(REDIRECT_PAGES[request.path], code=301)

    status = "closed" if e.code == 404 else "open"
    saved = errors.add_error(e.code, request.url, traceback.format_exc(), status)

    if not isinstance(e, HTTPException):
        e = InternalServerError()

    scratch = "when i receive [error {} v]\nsay [Oh no!]\nswitch costume to (sad :\( v)".format(e.code)

    return render_template("error.html", error=e, scratch=scratch, saved=saved)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(error)


if __name__ == "__main__":
    app.run()
