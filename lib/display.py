from . import common as common
from datetime import datetime
from flask import Flask, redirect, render_template, request, session
import mongoengine as mongo
import random

from ccl_scratch_tools import Parser
from ccl_scratch_tools import Scraper
from ccl_scratch_tools import Visualizer

from . import scrape


def get_code_excerpt(project, schema):
    """Gets a relevant code excerpt from a project based on the schema.
    
    Args:
        project (dict): the project's Mongoengine representation.
        schema (dict): the schema's Mongoengine representation.
    
    Returns:
        A string of Scratchblocks syntax. Blank if couldn't find an example.
    """

    # Account for possible different formats depending on where called from
    if "min_instructions_length" not in project["validation"]:
        project["validation"] = project["validation"][schema["id"]]

    # Start work generating blocks
    blocks = list()
    
    # Find blocks if basis is required text
    if schema["comparison_basis"]["basis"] == "required_text":
        option = project["validation"]["required_text"][schema["comparison_basis"]["priority"]]
        if option > -1:
            text = schema["required_text"][schema["comparison_basis"]["priority"]][option].lower()

            # Add to the block list those blocks that have the appropriate text
            for i, key in enumerate(project["stats"]["block_text"]["text"]):
                if text in key.lower():
                    blocks += project["stats"]["block_text"]["blocks"][i]

    # Find blocks if basis is categories
    elif schema["comparison_basis"]["basis"] == "required_block_categories":
        if project["validation"]["required_block_categories"][schema["comparison_basis"]["priority"]]:
            for block in project["stats"]["blocks"]:
                if block.index(schema["comparison_basis"]["priority"]) == 0:
                    blocks += project["stats"]["blocks"][block]

    # Find blocks if basis is blocks
    elif schema["comparison_basis"]["basis"] == "required_blocks":
        if True in project["validation"]["required_blocks"]:
            rbo = project["validation"]["required_blocks"].index(True)
            blocks = project["stats"]["blocks"][schema["comparison_basis"]["priority"][rbo]]
    
    # Choose what to feature
    if len(blocks) > 0:
        parser = Parser()
        visualizer = Visualizer()

        block = random.choice(blocks)
        scratch_data = scrape.get_project_from_cache(project["project_id"])
        blocks = parser.get_surrounding_blocks(block, scratch_data, 7, True)
        target, _ = parser.get_target(block, scratch_data)

        return visualizer.generate_script(blocks[0], target["blocks"], blocks, True)
    else:
        return ""
                    
    
def get_comparisons(project, schema, count, credentials_file="secure/db.json"):
    """Gets comparison projects based on the schema.
    
    Args:
        project (dict): the Mongoengine representation of the project.
        schema (dict): the Mongoengine representation of the project.
        count (int): the number of projects to return.

    Returns:
        A list of projects, as stored in the database, to use as examples.
    """

    # Get the full set of projects to choose from
    if schema["comparison_basis"]["basis"] == "__none__":
        projects = scrape.Project.objects(studio_id=project["studio_id"])

    # Find projects that meet the priority text requirement
    elif schema["comparison_basis"]["basis"] == "required_text":
        query = {
            "studio_id": project["studio_id"],
            "project_id": {"$ne": project["project_id"]},
            "validation.{}.required_text.{}".format(schema["id"], schema["comparison_basis"]["priority"]): {"$gte": 0}
        }

        projects = scrape.Project.objects(__raw__=query)

    # Find projects that meet the priority category requirement
    elif schema["comparison_basis"]["basis"] == "required_block_categories":
        projects = scrape.get_projects_with_category(schema["comparison_basis"]["priority"],
                                                     schema["required_block_categories"][schema["comparison_basis"]["basis"]],
                                                     project["project_id"],
                                                     project["studio_id"],
                                                     credentials_file)
    
    # Find projects that meet a block requirement
    elif schema["comparison_basis"]["basis"] == "required_blocks":
        query = {
            "studio_id": project["studio_id"],
            "project_id": {"$ne": project["project_id"]},
            "validation.{}.required_blocks".format(schema["id"]): True
        }

        projects = scrape.Project.objects(__raw__=query)

    # Choose random projects
    ids = random.sample(range(len(projects)), min(len(projects), count))
    result = list()
    for i in ids:
        result.append(projects[i].to_mongo().to_dict())
    
    return result
