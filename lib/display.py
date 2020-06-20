from . import common as common
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
import mongoengine as mongo
import random

from ccl_scratch_tools import Parser, Scraper, Visualizer

from . import schema, scrape


def get_code_excerpt(project, sc):
    """Gets a relevant code excerpt from a project based on the schema.
    
    Args:
        project (dict): the project's Mongoengine representation.
        schema (dict): the schema's Mongoengine representation.
    
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
    
    # Choose what to feature
    if len(blocks) > 0:
        parser = Parser()
        visualizer = Visualizer()

        block = random.choice(blocks)
        scratch_data = scrape.get_project_from_cache(project["project_id"])
        blocks = parser.get_surrounding_blocks(block, scratch_data, 7, True)
        target, _ = parser.get_target(block, scratch_data)

        code = visualizer.generate_script(blocks[0], target["blocks"], blocks, True)
        sprite = parser.get_sprite(block, scratch_data)

        return code, sprite
    else:
        return "", ""
                    
    
def get_comparisons(project, sc, count, credentials_file="secure/db.json"):
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


def get_project_page(pid, cache_directory="cache"):
    """Get a project page rendered in HTML given a project ID.
    
    Args:
        pid (str): project ID.
        cache_directory (str): the directory where cached projects are stored.
        
    Returns:
        A string containing the HTML for the page.
    """

    # Load in the project db, project JSON, studio info, and schema
    project, scratch_data = scrape.get_project(pid, cache_directory)
    studio = scrape.get_studio(project["studio_id"])
    sc = schema.get_schema(studio["challenge_id"])

    # Determine whether there's an error here
    err = False
    if str(studio["challenge_id"]) in project["validation"]:
        project["validation"] = project["validation"][str(studio["challenge_id"])]
    else:
        err = True

    # Show error page
    if project == {} or scratch_data == {} or studio == {} or err:
        return "Uh oh!"

    # Prepare helper tools
    scraper = Scraper()
    visualizer = Visualizer()

    # One prompt variable to take the logic out of the templating language
    prompt = {
        "title": sc["title"] if sc["title"] is not None else studio["title"],
        "description": sc["description"] if "description" in sc else studio["description"]
    }

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

    return render_template("project.html", prompt=prompt, project=project, studio=studio, schema=sc, excerpts=excerpts)
