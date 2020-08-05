from . import common as common
import json
import logging
import mongoengine as mongo
import pandas as pd

from datetime import datetime
from flask import Blueprint, Flask, redirect, render_template, request, Response, session
from werkzeug.exceptions import NotFound

from . import authentication, schema, scrape, settings

reporting = Blueprint("reports", __name__, template_folder="templates")


@reporting.route("/admin/reports/projects")
@authentication.admin_required
def get_projects():
    """Gets projects as a CSV."""

    level = None if "block_detail" in request.args and request.args[
        "block_detail"] == "all" else 2

    common.connect_db()

    project_reflections = scrape.ProjectReflection.objects()

    try:
        if int(request.args["studio_id"]) > 0:
            projects = json.loads(
                scrape.Project.objects(studio_id=request.args["studio_id"])
                .exclude("id",
                         "cache_expires",
                         "image",
                         "reload_page").to_json())
    except:
        projects = json.loads(scrape.Project.objects()
                              .exclude("id",
                                       "cache_expires",
                                       "image",
                                       "reload_page").to_json())

    for project in projects:
        reflections = project_reflections.filter(
            project_id=project["project_id"]).order_by("-id")

        if reflections.count() > 0:
            reflection = reflections.first()
            project["minutes"] = reflection["minutes"]

            for i, feeling in enumerate(reflection["feelings"]):
                project[f"feeling_{i}"] = feeling

    flattened = pd.json_normalize(projects, max_level=level)

    # Order columns
    cols = [
        "project_id",
        "title",
        "author",
        "description",
        "instructions",
        "studio_id"
    ]

    stats = list()
    for row in flattened:
        if row not in stats and row not in cols:
            stats.append(row)

    cols = cols + sorted(stats)

    response = Response(flattened.to_csv(columns=cols,
                                         index=False),
                        mimetype="text/csv")

    response.headers.set("Content-Disposition",
                         "attachment",
                         filename="projects.csv")

    return response


@reporting.route("/admin/reports/studios")
@authentication.admin_required
def get_studios():
    """Gets studios as a CSV."""

    level = None if "block_detail" in request.args and request.args[
        "block_detail"] == "all" else 2

    common.connect_db()

    try:
        if int(request.args["id"]) > 0:
            studios = json.loads(
                scrape.Studio.objects(
                    studio_id=request.args["id"]).exclude("id").to_json())
    except:
        studios = json.loads(scrape.Studio.objects().exclude("id").to_json())

    flattened = pd.json_normalize(studios, max_level=level)

    # Order columns
    cols = [
        "studio_id",
        "title",
        "description",
        "status",
        "challenge_id.$oid",
        "public_show"
    ]

    stats = list()
    for row in flattened:
        if row not in stats and row not in cols:
            stats.append(row)

    cols = cols + sorted(stats)

    response = Response(flattened.to_csv(na_rep=0,
                                         columns=cols,
                                         index=False),
                        mimetype="text/csv")

    response.headers.set("Content-Disposition",
                         "attachment",
                         filename="studios.csv")

    return response
