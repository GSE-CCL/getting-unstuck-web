import threading
import time
import urllib
from flask import Flask, redirect, render_template, request, session
from ccl_scratch_tools import Parser
from ccl_scratch_tools import Scraper

from lib import scrape
from lib.authentication import admin_required, login_required

app = Flask(__name__)

# TODO: Authentication

# Studios, projects
@app.route("/")
def homepage():
    return render_template("index.html") 

@app.route("/", methods=["POST"])
def project_form_post():
    scraper = Scraper()
    parser = Parser()
    project_url = request.form["project_url"]
    project_id = scraper.get_id(project_url)
    downloaded_project = scraper.download_project(project_id)
    results = blockify(downloaded_project)
    block_names = convert_block_names(downloaded_project)

    child = parser.get_child_blocks(results["blocks"]["event_whenflagclicked"][0], downloaded_project)

    sprite = parser.get_sprite(results["blocks"]["event_whenflagclicked"][0], downloaded_project)

    surround = parser.get_surrounding_blocks(results["blocks"]["event_whenflagclicked"][0], downloaded_project)
    block_list = []
    for b in surround:
        info = parser.get_block(b, downloaded_project)
        block_list.append(parser.get_block_name(info["opcode"]))

    if project_id != "":
        return render_template("results.html", username=project_id, data=downloaded_project, results=results, block_names=block_names, child=child, sprite=sprite, surround=block_list)

@app.route("/project/<pid>", methods=["GET"])
def project_id(pid):
    scrape.connect_db()
    project = scrape.Project.objects(project_id=pid).first()
    studio = scrape.Studio.objects(studio_id=project["studio_id"]).first()

    return render_template("project.html", project=project, studio=studio)

@app.route("/redirect", methods=["GET"])
def redirect_to():
    if request.args.get("username") is not None and request.args.get("username") != "":
        return redirect("/user/{0}".format(urllib.parse.quote(request.args.get("username"))))
    else:
        return render_template("index.html", message="Sorry! I wasn't able to do that.")

@app.route("/studio", methods=["GET", "POST"])
#@admin_required
def studio():
    if request.method == "GET":
        return render_template("studio.html")
    else:
        scraper = Scraper()
        sid = scraper.get_id(request.form["studio"])

        if sid is not None:
            scrape.add_studio(sid)
            return redirect("/studio/{0}".format(sid))
        else:
            return render_template("studio.html", message="Please enter a valid studio ID or URL.")

@app.route("/studio/<sid>")
def studio_id(sid):
    if sid == "":
        return redirect("/studio")

    scrape.connect_db()
    studio = scrape.Studio.objects(studio_id = sid).first()
    projects = list(scrape.Project.objects(studio_id = sid))

    message = None
    if studio["status"] == "in_progress":
        message = "This studio is currently in the process of being downloaded and analyzed. <a href=''>Refresh page.</a>"

    return render_template("studio_id.html", projects=projects, studio=studio, message=message)

@app.route("/user/<username>")
def user_id(username):
    scrape.connect_db()
    projects = list(scrape.Project.objects(author = username))
    studios = dict()
    for project in projects:
        if project["studio_id"] not in studios:
            studios[project["studio_id"]] = scrape.Studio.objects(studio_id = project["studio_id"]).first()

    return render_template("username.html", projects=projects, studios=studios, username=username)

if __name__ == "__main__":
    app.run()
