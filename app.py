import json
import markdown
import os
import threading
import time
import random
import urllib
from flask import Flask, redirect, render_template, request, session
from ccl_scratch_tools import Parser
from ccl_scratch_tools import Scraper
from ccl_scratch_tools import Visualizer

from lib import common
from lib import schema
from lib import scrape
from lib import authentication
from lib import admin
from lib.authentication import admin_required, login_required
from lib.settings import CACHE_DIRECTORY


app = Flask(__name__)
parser = Parser()

def twodec(value):
    return f"{value:,.2f}"

def indexOf(lst, value):
    return lst.index(value)

def pluralize(item):
    if type(item) == list:
        return "s" if len(item) != 1 else ""
    else:
        return "s" if int(item) != 1 else ""

def human_block(opcode):
    return parser.get_block_name(opcode)

app.jinja_env.filters["twodec"] = twodec
app.jinja_env.filters["indexOf"] = indexOf
app.jinja_env.filters["pluralize"] = pluralize
app.jinja_env.filters["human_block"] = human_block
app.secret_key = os.urandom(24)
app.url_map.strict_slashes = False

# Pass things to all templates
@app.context_processor
def inject_vars():
    return dict(user=authentication.get_login_info(), valid_admin_pages=admin.VALID_ADMIN_PAGES)

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
            return json.dumps(result)
    else:
        return redirect("/admin")

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
        "text": {},
        "comparison_basis": {"basis": "__none__", "priority": None}
    }
    if id != "__new__":
        common.connect_db()
        data = schema.Challenge.objects(id = id).first().to_mongo()

    blocks = parser.block_data
    block_list = list()
    block_dict = dict()
    for cat in blocks:
        block_list += blocks[cat].keys()
        for block in blocks[cat]:
            block_dict[blocks[cat][block].lower().replace(" ", "")] = block
    return render_template("admin/edit_schema.html", blocks=blocks, block_dict=block_dict, block_list=block_list, categories=list(blocks.keys()), data=data, schema_id=id)

@app.route("/admin/schemas/edit", methods=["GET"])
@admin_required
def add_schema():
    return schema_editor("__new__")

@app.route("/admin/schemas/edit/<id>", methods=["GET"])
@admin_required
def edit_schema(id):
    return schema_editor(id)

# Studios, projects, users, challenges
@app.route("/")
def homepage():
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

@app.route("/project/<pid>", methods=["GET"])
def project_id(pid):
    project, scratch_data = scrape.get_project(pid, CACHE_DIRECTORY)
    studio = scrape.get_studio(project["studio_id"])
    sc = schema.get_schema(studio["challenge_id"])

    err = False
    if str(studio["challenge_id"]) in project["validation"]:
        project["validation"] = project["validation"][str(studio["challenge_id"])]
    else:
        err = True

    if project == {} or scratch_data == {} or studio == {} or err:
        return "Uh oh!"

    scraper = Scraper()
    visualizer = Visualizer()

    prompt = {
        "title": sc["title"] if sc["title"] is not None else studio["title"],
        "description": sc["description"] if sc["description"] is not None else studio["description"]
    }

    sc["explanation"] = common.md(sc["explanation"])
    
    
    return render_template("project_new.html", prompt=prompt, project=project, studio=studio, schema=sc)

    return "ok"
    #return render_template("project.html", project=project, studio=studio, results=results, sprite=sprite, text=text, comp_user=other_user, comp_pid=other_pid, comp_sprite=other_sprite, comp_text=other_text)

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
            scrape.add_studio(sid, schema=s, show=("show" in request.form), cache_directory=CACHE_DIRECTORY)
            return redirect("/studio/{0}".format(sid))
        else:
            return render_template("studio.html", message="Please enter a valid studio ID or URL.")

@app.route("/studio/<sid>")
def studio_id(sid):
    if sid == "":
        return redirect("/prompts")

    common.connect_db()
    studio = scrape.Studio.objects(studio_id = sid).first()
    projects = list(scrape.Project.objects(studio_id = sid))
    info = {"authors": list(), "project_ids": list(), "titles": list()}

    for project in projects:
        info["authors"].append(project["author"].lower())
        info["project_ids"].append(project["project_id"])
        info["titles"].append(project["title"].lower())

    message = None
    if studio["status"] == "in_progress":
        message = "This studio is currently in the process of being downloaded and analyzed. <a href=''>Refresh page.</a>"

    return render_template("studio_id.html", info=info, projects=projects, studio=studio, message=message)

@app.route("/user/<username>")
def user_id(username):
    common.connect_db()
    projects = list(scrape.Project.objects(author = username))
    studios = dict()
    for project in projects:
        if project["studio_id"] not in studios:
            studios[project["studio_id"]] = scrape.Studio.objects(studio_id = project["studio_id"]).first()

    return render_template("username.html", projects=projects, studios=studios, username=username)

@app.route("/prompts", methods=["GET"])
def prompts():
    common.connect_db()
    studios = list(scrape.Studio.objects(public_show=True))
    schemas = dict()
    for studio in studios:
        if "challenge_id" not in studio:
            studios.remove(studio)
            break
        schemas[studio["challenge_id"]] = schema.Challenge.objects(id=studio["challenge_id"]).first().to_mongo().to_dict()

    return render_template("prompts.html",
                           challenges=studios,
                           schemas=schemas)

@app.route("/challenges-amy", methods=["GET", "POST"])
def get_challenge():
    if request.method == "GET":
        return render_template("submit_challenge.html")
    else:
        scraper = Scraper()
        project_url = request.form['project-url']
        project_id = scraper.get_id(project_url)
        downloaded_project = scraper.download_project(project_id)
        results = parser.blockify(scratch_data=downloaded_project)

        block_of_interest = "operator_random"

        child = parser.get_child_blocks(results["blocks"][block_of_interest][0], downloaded_project)
        sprite = parser.get_sprite(results["blocks"][block_of_interest][0], downloaded_project)
        surround = parser.get_surrounding_blocks(results["blocks"][block_of_interest][0], downloaded_project, 7)

        block_list = []
        text = ""
        for b in surround:
            info = parser.get_block(b, downloaded_project)
            blockname = parser.get_block_name(info["opcode"])
            inputs = info["inputs"]
            text += blockname
            if inputs:
                for each in inputs:
                    if each == "MESSAGE":
                        text += " [" + inputs[each][1][1] +"]"
                    elif each == "SECS" or each == "DURATION" or each == "FROM" or each == "TO":
                        text += " (" + inputs[each][1][1] + ")"

            text += "\n"

            block_list.append((blockname, info))

        if project_id != "":
            return render_template("results.html", username=project_id, data=downloaded_project, results=results, child=child, sprite=sprite, surround=block_list, text=text)

            
        return render_template("results.html")

@app.route("/summary", methods=["GET"])
def summarize():
    return render_template("summary.html")

# Static pages -- About, Strategies
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/strategies", methods=["GET"])
def strategies():
    return render_template("strategies.html")

if __name__ == "__main__":
    app.run()
