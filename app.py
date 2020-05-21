import threading
import time
import random
import urllib
from flask import Flask, redirect, render_template, request, session
from ccl_scratch_tools import Parser
from ccl_scratch_tools import Scraper
from ccl_scratch_tools import Visualizer

from lib import common
from lib import scrape
from lib import authentication
from lib.authentication import admin_required, login_required
from draw_blocks import *

CACHE_DIRECTORY = "cache"


app = Flask(__name__)

def twodec(value):
    return f"{value:,.2f}"

app.jinja_env.filters["twodec"] = twodec
app.secret_key = "hithere"

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

    if res:
        res = authentication.login_user(request.form["username"], request.form["password"])
        if res:
            return redirect("/")
        else:
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

# Studios, projects
@app.route("/")
def homepage():
    return render_template("index.html", user=authentication.get_login_info()) 

@app.route("/project/<pid>", methods=["GET"])
def project_id(pid):
    common.connect_db()
    project = scrape.Project.objects(project_id=pid).first()
    studio = scrape.Studio.objects(studio_id=project["studio_id"]).first()

    scraper = Scraper()
    parser = Parser()
    visualizer = Visualizer()

    downloaded_project = scraper.download_project(pid)
    results = parser.blockify(scratch_data=downloaded_project)
    day2_interest = ["event_whenbackdropswitchesto", "event_whenthisspriteclicked", "event_whenstageclicked", "looks_show",  "looks_hide", "sensing_mousedown"]
    blocks_of_interest = ["control_wait", "control_create_clone_of", "control_delete_this_clone", "control_start_as_clone", "control_if", "control_repeat", "control_if_else", "control_repeat_until", "control_forever", "control_wait_until"]
    for interest in day2_interest:
        if interest in results["blocks"].keys():
            sprite = parser.get_sprite(results["blocks"][interest][0], downloaded_project)
            surround = parser.get_surrounding_blocks(results["blocks"][interest][0], downloaded_project, 7)

    print_blocks = generate_scratchblocks(downloaded_project, surround)
    text = block_string(print_blocks)

    # comparison project
    #other_projects = scrape.get_projects_with_block(["control_wait", "control_if_else"], studio_id=project["studio_id"], credentials_file="secure/db.json")
    other_projects = scrape.get_projects_with_block(day2_interest, studio_id=project["studio_id"], credentials_file="secure/db.json")
    project_num = random.randint(0, len(other_projects) - 1)
    other_pid = other_projects[project_num].project_id
    other_user = other_projects[project_num].author
    other_download = scraper.download_project(other_pid)
    other_results = parser.blockify(scratch_data=other_download)
    for interest in day2_interest:
        if interest in other_results["blocks"].keys():
            other_sprite = parser.get_sprite(other_results["blocks"][interest][0], other_download)
            other_surround = parser.get_surrounding_blocks(other_results["blocks"][interest][0], other_download, 11)
    other_blocks = generate_scratchblocks(other_download, other_surround)
    other_text = block_string(other_blocks)

    return render_template("theme.html", project=project, studio=studio, user=authentication.get_login_info(), results=results, sprite=sprite, text=text, comp_user=other_user, comp_pid=other_pid, comp_sprite=other_sprite, comp_text=other_text)

@app.route("/redirect", methods=["GET"])
def redirect_to():
    if request.args.get("username") is not None and request.args.get("username") != "":
        return redirect("/user/{0}".format(urllib.parse.quote(request.args.get("username"))))
    else:
        return render_template("index.html", message="Sorry! I wasn't able to do that.", user=authentication.get_login_info())

@app.route("/studio", methods=["GET", "POST"])
@admin_required
def studio():
    if request.method == "GET":
        return render_template("studio.html", user=authentication.get_login_info())
    else:
        scraper = Scraper()
        sid = scraper.get_id(request.form["studio"])

        if sid is not None:
            scrape.add_studio(sid, cache_directory="cache")
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

@app.route("/challenges", methods=["GET", "POST"])
def get_challenge():
    if request.method == "GET":
        return render_template("submit_challenge.html")
    else:
        scraper = Scraper()
        parser = Parser()
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

if __name__ == "__main__":
    app.run()
