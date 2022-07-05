from pprint import pprint

from src.webs_scrapers.all_scrapers import *

from scrapers_manager import ScraperManager

if __name__ == "__main__":

    ingrs = ["mak", "placki", ""]
    types = ["sniadanie", "asf", 325]

    sm = ScraperManager()
    # recipes = sm.get_recipes(ingrs=ingrs, meal_types=types, ingrs_match="partial")
    recipes = sm.get_recipes(ingrs=ingrs, meal_types=types)
    pprint(recipes)
