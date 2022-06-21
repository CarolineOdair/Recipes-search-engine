from pprint import pprint

from scrapers import *
from scrapers_menager import ScraperMenager

if __name__ == "__main__":

    ingrs = ["pomidory", "tofu"]
    types = ["sniadanie", "danie glowne"]

    sm = ScraperMenager()
    # recipes = sm.get_recipes(ingrs=ingrs, meal_types=types, ingrs_match="partial")
    recipes = sm.get_recipes(ingrs=ingrs, meal_types=types)
    pprint(recipes)
