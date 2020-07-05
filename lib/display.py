from . import common as common
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
import json
import logging
import mongoengine as mongo
import random

from ccl_scratch_tools import Parser, Scraper, Visualizer
from werkzeug.exceptions import NotFound

from . import schema, scrape, settings


def get_code_excerpt(project, sc, include_orphans=False):
    """Gets a relevant code excerpt from a project based on the schema.
    
    Args:
        project (dict): the project's Mongoengine representation.
        schema (dict): the schema's Mongoengine representation.
        include_orphans (bool): whether to include orphan blocks. Defaults to False.
    
    Returns:
        A tuple -- first, a string of Scratchblocks syntax, then info about the relevant sprite.
        
        Both will be blank if couldn't find an example.
    """

    # Account for possible different formats depending on where called from
    if "min_instructions_length" not in project["validation"]:
        project["validation"] = project["validation"][sc["id"]]

    # Start work generating blocks
    blocks = list()
    
    # Find blocks if basis is required text
    if sc["comparison_basis"]["basis"] == "required_text":
        option = project["validation"]["required_text"][sc["comparison_basis"]["priority"]]
        if option > -1:
            text = sc["required_text"][sc["comparison_basis"]["priority"]][option].lower()

            # Add to the block list those blocks that have the appropriate text
            for i, key in enumerate(project["stats"]["block_text"]["text"]):
                if text in key.lower():
                    blocks += project["stats"]["block_text"]["blocks"][i]

    # Find blocks if basis is categories
    elif sc["comparison_basis"]["basis"] == "required_block_categories":
        if project["validation"]["required_block_categories"][sc["comparison_basis"]["priority"]]:
            for block in project["stats"]["blocks"]:
                if block.index(sc["comparison_basis"]["priority"]) == 0:
                    blocks += project["stats"]["blocks"][block]

    # Find blocks if basis is blocks
    elif sc["comparison_basis"]["basis"] == "required_blocks":
        if True in project["validation"]["required_blocks"]:
            rbo = project["validation"]["required_blocks"].index(True)
            blocks = project["stats"]["blocks"][sc["comparison_basis"]["priority"][rbo]]
    
    # Exclude orphan blocks
    if not include_orphans and "orphan_blocks" in project["stats"]:
        for block in project["stats"]["orphan_blocks"]:
            if block in blocks:
                blocks.remove(block)

    # Choose what to feature
    if len(blocks) > 0:
        parser = Parser()
        visualizer = Visualizer()

        block = random.choice(blocks)
        scratch_data = scrape.get_project_from_cache(project["project_id"])
        blocks = parser.get_surrounding_blocks(block, scratch_data, 7, True)
        target = parser.get_target(block, scratch_data)

        if type(target) != bool:
            target = target[0]

        try:
            code = visualizer.generate_script(blocks[0], target["blocks"], blocks, True)
        except:
            logging.warn("Failed to generate a script using blocks [{}] in project {}".format(", ".join("blocks"), project["project_id"]))
            code = ""

        sprite = parser.get_sprite(block, scratch_data)

        return code, sprite
    else:
        return "", ""
                    
    
def get_comparisons(project, sc, count, credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Gets comparison projects based on the schema.
    
    Args:
        project (dict): the Mongoengine representation of the project.
        sc (dict): the Mongoengine representation of the schema.
        count (int): the number of projects to return.

    Returns:
        A list of projects, as stored in the database, to use as examples.
    """

    # Get the full set of projects to choose from
    if sc["comparison_basis"]["basis"] == "__none__":
        projects = scrape.Project.objects(studio_id=project["studio_id"])

    # Find projects that meet the priority text requirement
    elif sc["comparison_basis"]["basis"] == "required_text":
        query = {
            "studio_id": project["studio_id"],
            "project_id": {"$ne": project["project_id"]},
            "validation.{}.required_text.{}".format(sc["id"], sc["comparison_basis"]["priority"]): {"$gte": 0}
        }

        projects = scrape.Project.objects(__raw__=query)

    # Find projects that meet the priority category requirement
    elif sc["comparison_basis"]["basis"] == "required_block_categories":
        projects = scrape.get_projects_with_category(sc["comparison_basis"]["priority"],
                                                     sc["required_block_categories"][sc["comparison_basis"]["basis"]],
                                                     project["project_id"],
                                                     project["studio_id"],
                                                     credentials_file)
    
    # Find projects that meet a block requirement
    elif sc["comparison_basis"]["basis"] == "required_blocks":
        query = {
            "studio_id": project["studio_id"],
            "project_id": {"$ne": project["project_id"]},
            "validation.{}.required_blocks".format(sc["id"]): True
        }

        projects = scrape.Project.objects(__raw__=query)

    # Choose random projects
    ids = random.sample(range(len(projects)), min(len(projects), count))
    result = list()
    for i in ids:
        result.append(projects[i].to_mongo().to_dict())
    
    return result


def get_feels(feels=f"{settings.PROJECT_DIRECTORY}/lib/data/feels.json", randomize=False, alphabetize=False):
    """Get the emotions (feels, for the younger among us) that a user can choose to describe their experience.
    
    Args:
        feels (str): the file path to feels.json, from which the feels are loaded.
        randomize (bool): whether to randomize the order of feels. Default is False.
        alphabetize (bool): whether to alphabetize by text. Default is False. Will override randomize.

    Returns:
        A list of feelings the end user may feel. False if problem loading file.
    """

    try:
        with open(feels) as f:
            feelings = json.load(f)

        if randomize:
            random.shuffle(feelings)

        if alphabetize:
            feelings = sorted(feelings, key = lambda f: f["text"]) 

        return feelings
    except:
        return False


def get_project_page(pid, cache_directory=settings.CACHE_DIRECTORY):
    """Get a project page rendered in HTML given a project ID.
    
    Args:
        pid (str): project ID.
        cache_directory (str): the directory where cached projects are stored.
        
    Returns:
        A string containing the HTML for the page.
    """

    # Load in the project db, project JSON, studio info, and schema
    project, scratch_data = scrape.get_project(pid, cache_directory)

    if len(project) == 0 or len(scratch_data) == 0:
        message = "We couldn&rsquo;t find your project! Try finding it by going to Prompts, \
                   then Find Project for the day you&rsquo;re looking for."
        return render_template("project_loader.html", message=message)

    studio = scrape.get_studio(project["studio_id"])

    if "challenge_id" in studio:
        sc = schema.get_schema(studio["challenge_id"])

        # Determine whether there's an error here
        err = False
        if str(studio["challenge_id"]) in project["validation"]:
            project["validation"] = project["validation"][str(studio["challenge_id"])]
        else:
            err = True

        # Show error page
        if project == {} or scratch_data == {} or studio == {} or sc == {} or err:
            raise NotFound()

        # Prepare helper tools
        scraper = Scraper()
        visualizer = Visualizer()

        # Convert Markdown to HTML with Scratchblocks
        for key in sc["text"]:
            sc["text"][key] = common.md(sc["text"][key])

        # Get the code excerpt for the projects to be shown
        excerpts = dict()
        examples = get_comparisons(project, sc, 5) + [project]
        for example in examples:
            code, sprite = get_code_excerpt(example, sc)
            excerpts[example["project_id"]] = {
                "author": example["author"],
                "code": code,
                "sprite": sprite
            }
    else:
        sc = dict()
        excerpts = dict()

    # One prompt variable to take the logic out of the templating language
    prompt = {
        "title": sc["title"] if "title" in sc and sc["title"] is not None else studio["title"] if "title" in studio else None,
        "description": sc["description"] if "description" in sc else studio["description"]
    }

    # Choose stats to show
    studio["stats"] = get_studio_stats(sc, studio)

    # Get the feels
    feels = get_feels(randomize=True)

    return render_template("project.html", prompt=prompt, project=project, studio=studio, schema=sc, excerpts=excerpts, feels=feels)


def get_studio_stats(sc, studio):
    """Gets the studio stats based on schema requirements.
    
    Args:
        sc (dict): the schema.
        studio (dict): the studio.

    Returns:
        A list of dicts, each with keys "name" and "value" to describe each statistic.
    """

    parser = Parser()

    stats = list()
    for stat in sc["stats"]:
        obj = studio["stats"]
        s = {"name": list(), "value": 0}

        keys = stat.split("/")
        append = ""
        for i, key in enumerate(keys):
            # Make sure this stat actually exists in studio.stats, else discard
            if key in obj:
                obj = obj[key]
            else:
                s = dict()
                break

            # Get the human-readable block name as needed
            if i > 0 and keys[i - 1] == "blocks":
                key = parser.get_block_name(key)

            # Make block and category names boldface
            if append == "blocks":
                key = "<strong>{}</strong>".format(key)
            
            # Should we append blocks to the name string?
            if key == "blocks" or key == "block_categories":
                append = "blocks"
            else:
                s["name"].append(key.replace("_", " "))

        # If studio doesn't have the stat requested
        if s == {}:
            break
        
        if append != "":
            s["name"].append(append)
        
        s["name"] = " ".join(s["name"])
        s["value"] = obj

        stats.append(s)

    return stats
