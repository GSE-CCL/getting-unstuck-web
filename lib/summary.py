import celery.decorators
import hashlib
import io
import json
import logging
import math
import requests

from ccl_scratch_tools import Scraper
from pathlib import Path
from PIL import Image

from lib import common, schema, scrape, settings


def get_image_urls(studio_ids=None, credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Gets image URLs from database.
    
    Args:
        studio_ids (array-like): a set of studios from which to gather project images.
            Defaults to None, in which case will get all studios' project images.
        credentials_file (str): path to the database credentials file.

    Returns:
        A set of image URLs.
    """

    common.connect_db(credentials_file)

    if studio_ids is None:
        studio_ids = scrape.Studio.objects(public_show=True).values_list("studio_id")

    projects = set(scrape.Project.objects(studio_id__in=studio_ids).values_list("image"))
    projects.remove(None)

    return projects


def get_stitched(urls, x, y=0, w=24, h=18, solids=False):
    """Stitches together images from a set of URLs.
    
    Args:
        urls (array-like): a set of URLs to images to stitch together.
        x (int): number of columns of the composite image.
        y (int): number of rows of the composite image.
            Defaults to however many needed based on x.
        w (int): width of individual images in composite. Default 24.
        h (int): height of individual images in composite. Default 18.
        solids (bool): whether to include solid color images (e.g., all white or all black).
            Default False.

    Returns:
        PIL.Image of composite image.
    """

    logging.info("Starting stitch with {} images".format(len(urls)))

    # Calculate y automatically if needed.
    if y == 0:
        y = math.ceil(len(urls) / x)

    combined = Image.new("RGB", (w * x, h * y), (255, 255, 255))

    # Add images to composite
    col = 0
    row = 0

    md5 = hashlib.md5()
    md5s = set()
    for url in urls:
        # Get image from Scratch
        r = requests.get(url)

        if r.status_code != 200:
            raise RuntimeError("GET {0} failed with status code {1}".format(url, r.status_code))

        f = io.BytesIO(r.content)
        img = Image.open(f)

        # Resize and paste into combined
        img = img.resize((w, h))

        # Check for solid color images
        colors = img.getcolors()
        if solids or colors is None or len(colors) > 1:
            combined.paste(im=img, box=(col * w, row * h))

            # Counters
            col += 1
            if col == x:
                col = 0
                row += 1
                logging.info(f"Starting row {row} of {y} in composite image.")

    if row + 1 < y:
        combined = combined.crop((0, 0, w * x, h * (row + 1)))

    return combined


@celery.decorators.task
def generate_summary_page(credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Performs all the aggregation required to generate the summary page.
    
    Args:
        credentials_file (str): path to the database credentials file.

    Returns:
        None.
    """

    # Stitch the project images together
    #img = get_stitched(get_image_urls(), 16, w=96, h=72)
    #img.save("{}/summary/projects.jpg".format(settings.CACHE_DIRECTORY), dpi=(72, 72), quality=75)

    # Get the data
    studios = get_ordered_studios()
    studio_ids = [s["studio_id"] for s in studios]
    data = {
        "studios_ordered": [s.to_json() for s in studios],
        "project_counts": [s["stats"]["total"]["number_projects"] for s in studios],
        "nations": get_author_origins(get_unique_authors(studio_ids)),
        "totals": {
            "categories": get_total_categories(studios),
            "unique_authors": len(get_unique_authors(studio_ids)),
            "projects": sum([s["stats"]["total"]["number_projects"] for s in studios]),
            "comments": sum([s["stats"]["total"]["comments_left"] for s in studios]),
            "description": sum([s["stats"]["total"]["description_words"] for s in studios]),
            #"engagement": get_total_engagement(studio_ids)
        }
    }

    if Scraper().make_dir("{}/data".format(settings.CACHE_DIRECTORY)):
        with open("{}/data/summary.json".format(settings.CACHE_DIRECTORY), "w") as f:
            json.dump(data, f)


def get_total_categories(studios):
    """Gets total category counts."""

    categories = dict()
    for studio in studios:
        bc = studio["stats"]["total"]["block_categories"]
        for cat in bc:
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += bc[cat]

    return categories
            

def get_total_engagement(studio_ids):
    """Gets likes and hearts from Scratch API."""

    common.connect_db()
    engagement = scrape.Project.objects(studio_id__in=studio_ids).values_list("engagement")

    stats = {"views": 0, "loves": 0, "favorites": 0}
    for e in engagement:
        stats["views"] += e["views"]
        stats["loves"] += e["loves"]
        stats["favorites"] += e["favorites"]
    
    return stats


def get_unique_authors(studio_ids):
    """Gets the unique authors of projects across studios."""

    authors = set(scrape.Project.objects(studio_id__in=studio_ids).values_list("author"))

    return authors


def get_author_origins(authors):
    """Gets the origin locations of project authors."""

    nations = dict()
    scraper = Scraper()
    for author in authors:
        user = scraper.get_user_info(author)
        if user["profile"]["country"] in nations:
            nations[user["profile"]["country"]] += 1
        else:
            nations[user["profile"]["country"]] = 1

    return nations


def get_ordered_studios():

    common.connect_db()

    # Get studios and schemas
    studios = scrape.Studio.objects(public_show=True)
    studio_ids = studios.values_list("studio_id")

    schema_ids = set(studios.values_list("challenge_id"))
    schema_ids.remove(None)
    schemas = schema.Challenge.objects(id__in=schema_ids).order_by("short_label", "title")  # yapf: disable
    schema_order = [str(v) for v in schemas.values_list("id")]

    # Order studios by schema label and title
    studio_order = [None] * len(studios)
    for studio in studios:
        schema_id = str(studio["challenge_id"])

        if schema_id != "None":
            studio_order[schema_order.index(schema_id)] = studio

    studio_order = [s for s in studio_order if s is not None]

    return studio_order
