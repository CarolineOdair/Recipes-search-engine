from pprint import pprint

from scrapers_manager import ScraperManager


if __name__ == "__main__":

    ingrs = ["tofu", "pesto"]
    types = ["danie glowne", "sniadanie"]

    sm = ScraperManager()
    # recipes = sm.get_recipes(ingrs=ingrs, meal_types=types, ingrs_match="partial")
    recipes = sm.get_recipes(ingrs=ingrs, meal_types=types)
    pprint(recipes)
