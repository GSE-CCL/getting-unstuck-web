import pdfkit
import mongoengine as mongo
from jinja2 import Template
import os
from lib import scrape
from lib import common
from . import common as common
from . import schema, scrape, settings

def convert_cert(template, username, projectnum):   
    options = {
    'orientation': 'Landscape',
    'page-size': 'Letter',
    'margin-top': '0',
    'margin-right': '0',
    'margin-bottom': '0',
    'margin-left': '0',
    'encoding': "UTF-8",
    'no-outline': None
    }

    css = "lib/certificate.css"
    jinja2_template_string = open("lib/" + template,'rb').read()

    template = Template(jinja2_template_string.decode("utf-8"))

    html_template_string = template.render(name= username, projectnum = projectnum)

    pdfkit.from_string(html_template_string, "certificates/" + username + '.pdf', options=options, css=css)
    
    return True

def download_certs(usernames):
    common.connect_db()
    for username in usernames:
        project_num = scrape.Project.objects(author = username).count()
        cert_download = convert_cert("pdf.html", username, project_num)

        if not cert_download:
            print("certificate download unsuccessful for: ", username)
    return True