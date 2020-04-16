from flask import Flask
from flask import request
from flask import render_template
from blockify import * 
from ccl_scratch_tools import Parser 
from ccl_scratch_tools import Scraper


app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("index.html") 

@app.route('/', methods=['POST'])
def project_form_post():
    scraper = Scraper()
    parser = Parser()
    project_url = request.form['project_url']
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



if __name__ == '__main__':
    app.run()