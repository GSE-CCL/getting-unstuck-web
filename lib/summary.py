import celery.decorators
import hashlib
import io
import json
import logging
import math
import requests

from ccl_scratch_tools import Scraper
from datetime import datetime
from pathlib import Path
from PIL import Image

from lib import common, schema, scrape, settings


@celery.decorators.task
def generate_summary_page(credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Performs all the aggregation required to generate the summary page.
    
    Args:
        credentials_file (str): path to the database credentials file.

    Returns:
        None.
    """

    logging.info("starting to aggregate summary statistics")

    # Stitch the project images together
    img = get_stitched(get_image_urls(), 16, w=96, h=72)
    img.save("{}/data/projects.jpg".format(settings.CACHE_DIRECTORY),
             dpi=(72, 72),  # disable: yapf
             quality=75)

    logging.info("project image stitch saved, starting on data gathering")

    # Get the data
    now = datetime.now()
    studios = get_ordered_studios()
    studio_ids = [s["studio_id"] for s in studios]
    engagement = get_total_engagement(studio_ids)
    data = {
        "project_counts": [
            s["stats"]["total"]["number_projects"] for s in studios
        ],
        "nations": get_author_origins(get_unique_authors(studio_ids)),
        "totals": {
            "block_count":
                sum([s["stats"]["total"]["block_count"] for s in studios]),
            "categories":
                get_total_categories(studios),
            "comments":
                sum([s["stats"]["total"]["comments_left"] for s in studios]),
            "description":
                sum([s["stats"]["total"]["description_words"]
                     for s in studios]),
            "hearts_stars":
                engagement["loves"] + engagement["favorites"],
            "projects":
                sum([s["stats"]["total"]["number_projects"] for s in studios]),
            "unique_authors":
                len(get_unique_authors(studio_ids))
        },
        "updated": now.strftime("%A, %B %d, %Y")
    }

    with open("{}/lib/data/summary.json".format(settings.PROJECT_DIRECTORY)) as f:  # yapf: disable
        static = json.load(f)
        data["static"] = static["statistics"]

    if Scraper().make_dir("{}/data".format(settings.CACHE_DIRECTORY)):
        with open("{}/data/summary.json".format(settings.CACHE_DIRECTORY), "w") as f:  # yapf: disable
            json.dump(data, f)

    logging.info("completed aggregating summary statistics")
    return True


def get_author_origins(authors):
    """Gets the origin locations of project authors.
    
    Args:
        authors (array-like): a set of authors for whom origin locations are to be counted.

    Returns:
        A dictionary mapping countries to number of authors from there.
    """

    nations = dict()
    scraper = Scraper()
    for author in authors:
        user = scraper.get_user_info(author)
        if user["profile"]["country"] in nations:
            nations[user["profile"]["country"]] += 1
        else:
            nations[user["profile"]["country"]] = 1

    return nations


def get_image_urls(studio_ids=None,
                   credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
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
        studio_ids = scrape.Studio.objects(
            public_show=True).values_list("studio_id")

    projects = set(
        scrape.Project.objects(studio_id__in=studio_ids).values_list("image"))

    try:
        projects.remove(None)
    except:
        pass

    return projects


def get_ordered_studios(credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Gets the studios ordered by short label and title.
    
    Args:
        credentials_file (str): path to the database credentials file.
    Returns:
        An ordered list of studios. Studios without schemas will be excluded.
    """

    common.connect_db(credentials_file)

    # Get studios and schemas
    studios = scrape.Studio.objects(public_show=True)
    studio_ids = studios.values_list("studio_id")

    schema_ids = set(studios.values_list("challenge_id"))

    try:
        schema_ids.remove(None)
    except:
        pass

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

    logging.info("starting stitch with {} images".format(len(urls)))

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
            logging.warn("GET {0} failed with status code {1}"
                         .format(url, r.status_code))  # yapf: disable

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


def get_total_categories(studios):
    """Gets total category counts.
    
    Args:
        studios (array-like): a list of studios, either as MongoDB representations
            or as dictionaries.

    Returns:
        A dictionary mapping each category to a total block count.
    """

    categories = dict()
    for studio in studios:
        bc = studio["stats"]["total"]["block_categories"]
        for cat in bc:
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += bc[cat]

    return categories


def get_total_engagement(studio_ids,
                         credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Gets engagement for projects within a studio.
    
    Args:
        studio_ids (array-like): a list of studio IDs for which to retrieve project engagement.
        credentials_file (str): path to the database credentials file.

    Returns:
        A dictionary mapping {views, loves, favorites} to integers representing the total counts
        in the studios chosen.
    """

    common.connect_db(credentials_file)
    engagement = scrape.Project.objects(
        studio_id__in=studio_ids).values_list("engagement")

    stats = {"views": 0, "loves": 0, "favorites": 0}
    for e in engagement:
        stats["views"] += e["views"]
        stats["loves"] += e["loves"]
        stats["favorites"] += e["favorites"]

    return stats


def get_unique_authors(studio_ids,
                       credentials_file=settings.DEFAULT_CREDENTIALS_FILE):
    """Gets the unique authors of projects across studios.
    
    Args:
        studio_ids (array-like): the list of studio IDs for studios for which a
            set of unique authors is desired.
        credentials_file (str): path to the database credentials file.

    Returns:
        A set of unique authors of projects.
    """

    common.connect_db(credentials_file)
    authors = set(
        scrape.Project.objects(studio_id__in=studio_ids).values_list("author"))

    return authors