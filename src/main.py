from pprint import pprint

from src.webs_scrapers.tag_wp_scrapers import *
from src.webs_scrapers.wp_scrapers import *
from src.webs_scrapers.other_scrapers import *

from scrapers_menager import ScraperMenager

if __name__ == "__main__":

    ingrs = ["pomidory", "tofu"]
    types = ["sniadanie", "danie glowne"]

    sm = ScraperMenager()
    # recipes = sm.get_recipes(ingrs=ingrs, meal_types=types, ingrs_match="partial")
    recipes = sm.get_recipes(ingrs=ingrs, meal_types=types)
    pprint(recipes)
