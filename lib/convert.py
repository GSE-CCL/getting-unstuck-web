import pdfkit
from jinja2 import Template
import os

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
    print("CURRENT", os.getcwd(), "ok", "/lib/" + template)
    jinja2_template_string = open("lib/" + template,'rb').read()

    template = Template(jinja2_template_string.decode("utf-8"))

    html_template_string = template.render(name= username, projectnum = projectnum)
    print(html_template_string)
    pdfkit.from_string(html_template_string, username + '.pdf', options=options, css=css)
    return True