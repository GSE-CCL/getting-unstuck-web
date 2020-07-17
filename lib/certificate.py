import pdfkit
import mongoengine as mongo
import celery.decorators
import logging
from jinja2 import Template
import os
from . import common as common
from . import scrape, settings


connect_db = common.connect_db


def convert_cert(template, username, projectnum, cache_directory=settings.CACHE_DIRECTORY):   
    """ Converts template to the certificate pdf with inputs.

    Args:
        template (str): the certificate template provided as a string directed to a html page.
        username (str): username to add to the certificate.
        projectnum (int): the number of projects completed by the user, should be 10 or fewer.
        cache_directory (str): will save this certificate into the cache directory specified.
            Defaults to settings.CACHE_DIRECTORY.

    Returns:
        Bool: True or False depending on the success of the certificate conversion.

    """
    
    # Set formatting parameters for the look of the certificate
    options = {
        "orientation": "Landscape",
        "page-size": "Letter",
        "margin-top": "0",
        "margin-right": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "encoding": "UTF-8",
        "no-outline": None
    }

    # Location of the css file
    css = "lib/assets/certificate.css"

    # Use of jinja and pdfkit to build the certificate pdf
    jinja2_template_string = open(f"lib/assets/{template}", "rb").read()
    template = Template(jinja2_template_string.decode("utf-8"))

    html_template_string = template.render(name=username, projectnum=projectnum)

    pdfkit.from_string(html_template_string, f"{cache_directory}/{username}.pdf", options=options, css=css)
    
    return True


@celery.decorators.task
def generate_certs(usernames, 
                    credentials_file=settings.DEFAULT_CREDENTIALS_FILE,
                    cache_directory=settings.CACHE_DIRECTORY):
    """Initiates the generation of all Getting Unstuck certificates.

    Args:
        usernames (array-like): list of usernames to create and scrape certificates for.
        credentials_file (str): path to the database credentials file.   
        cache_directory (str): if set, will save this certificate into the cache directory specified.

    Returns: 
        None.
    """
    
    logging.info("attempting to generate certificates")
    connect_db(credentials_file=credentials_file)

    # Get schema IDs, and add to a reusable query that will get all the projects that have one of the schemas
    schema_ids = scrape.Studio.objects(public_show=True).values_list("challenge_id")
    query = []
    for schema_id in schema_ids:
        query.append({f"validation.{schema_id}": {"$exists": True}})
    projects = scrape.Project.objects(__raw__={"$or": query})

    # Loop through each username to generate certificate
    for username in usernames:
        # Get number of projects completed
        author_count = projects.filter(author=author).count()
        if author_count > 10:
            logging.info("certificate for {} has more than 10 projects! reset to 10".format(username))
            author_count = 10

        # Generate certificate
        cert_download = convert_cert("pdf.html", username, author_count, cache_directory)
        
        if not cert_download:
            logging.info("certificate download failed for {}".format(username))
    
    logging.info("certificate generation completed!"
