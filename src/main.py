from pprint import pprint

from scrapers_manager import ScraperManager
from base import MealType, IngrMatch


if __name__ == "__main__":

    ingrs = ["tofu", "pesto"]
    types = [MealType.DINNER, MealType.LUNCH]

    sm = ScraperManager(precise=False)
    recipes = sm.get_recipes(ingrs=ingrs, meal_types=types, ingrs_match=IngrMatch.PART)
    pprint(recipes)
