from flask import Flask
from flask import request
from flask import render_template
from ccl_scratch_scrape import Scraper

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("index.html") 

@app.route('/', methods=['POST'])
def project_form_post():
    scraper = Scraper()
    project_url = request.form['project_url']
    project_id = scraper.get_id(project_url)
    downloaded_project = scraper.download_project(project_id)


    if project_id != "":
        return "<h1>" + str(project_id) + "</h1> <p>" + str(downloaded_project) + "</p>"


if __name__ == '__main__':
    app.run()