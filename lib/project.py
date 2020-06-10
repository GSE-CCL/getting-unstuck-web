import json
import os
from ccl_scratch_tools import Parser
from ccl_scratch_tools import Scraper
from ccl_scratch_tools import Visualizer

def display(pid, blocks_interest):
    scraper = Scraper()
    parser = Parser()
    visualizer = Visualizer()

    with open("cache/" + pid + ".json") as cache_project:
        downloaded_project = json.load(cache_project)
    results = parser.blockify(scratch_data=downloaded_project)

    sprite = None
    surround = None

    for interest in blocks_interest:
        if interest in results["blocks"].keys():
            sprite = parser.get_sprite(results["blocks"][interest][0], downloaded_project)
            surround = parser.get_surrounding_blocks(results["blocks"][interest][0], downloaded_project, 7)
    
    if surround is not None and sprite is not None:
        target = parser.get_target(surround[0], downloaded_project)
        text = visualizer.generate_script(surround[0], target[0]["blocks"], surround, text=True)
    else:
        print("sprite surround", surround, sprite)
        text = ""

    return (sprite, text, results)

