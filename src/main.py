from pprint import pprint

from scrapers_manager import ScraperManager
from base import MealType


if __name__ == "__main__":

    ingrs = ["tofu", "pesto"]
    types = [MealType.DINNER, MealType.LUNCH]

    sm = ScraperManager(precise=False)
    recipes = sm.get_recipes(ingrs=ingrs, types=types)
    pprint(recipes)
