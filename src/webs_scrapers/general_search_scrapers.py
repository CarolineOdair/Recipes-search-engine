from src.base.base_scrapers.base_general_search_scraper import GeneralSearchScraper
from src.base.utils import CuisineType, MealType  # classes
from src.base.utils import do_lists_have_common_element  # functions


class MadeleineOliviaScraper(GeneralSearchScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'madeleineolivia.co.uk'.
    """
    NAME = "Madeleine Olivia"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://madeleineolivia.co.uk"
    ENG_WEB = True

    REQUEST_URL = WEB_URL + "/api/search/GeneralSearch?q="
    RECIPE_URL = WEB_URL + "/blog/"

    def __init__(self):
        super().__init__()

    def get_data_from_response(self, web_response:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Filters data about recipe and returns useful part - title and link """

        # loop through recipes
        for recipe in web_response["items"]:

            # skips if meal_types are given but recipe categories do not contain none of the wanted types
            if meal_types is None or do_lists_have_common_element(recipe["categories"], meal_types):
                title = recipe["title"]
                link = self.RECIPE_URL + recipe['urlId']

                yield self.recipe_data_to_dict(title, link)

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.BREAKFAST: ["breakfast"],
            MealType.DINNER: ["mains"],
            MealType.DESSERT: ["desserts"],
            MealType.SNACKS: ["snack"],
            MealType.DRINK: ["drinks"],
            MealType.SAUCE: ["dips"],
            MealType.SOUP: None,
            MealType.LUNCH: None,
            MealType.TO_BREAD: None,
        }
        return trans.get(meal_type)

class MinaRomeScraper(GeneralSearchScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'mina-rome.com'.
    """
    NAME = "Mina Rome"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://mina-rome.com"
    ENG_WEB = True

    REQUEST_URL = WEB_URL + "/api/search/GeneralSearch?q="

    def __init__(self):
        super().__init__()

    def get_data_from_response(self, web_response:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Filters data about recipe and returns useful part - title and link """

        # loop through recipes
        for recipe in web_response["items"]:

            # skips if meal_types are given but recipe categories do not contain none of the wanted types
            if meal_types is None or do_lists_have_common_element(recipe["categories"], meal_types):
                title = recipe["title"]
                link = self.WEB_URL + recipe['itemUrl']

                yield self.recipe_data_to_dict(title, link)

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.BREAKFAST: ["Breakfast"],
            MealType.DINNER: ["Main-dish"],
            MealType.DESSERT: ["Desserts", "Treats"],
            MealType.SNACKS: ["Snacks"],
            MealType.DRINK: ["Drinks"],
            MealType.SAUCE: None,
            MealType.SOUP: None,
            MealType.LUNCH: None,
            MealType.TO_BREAD: None,
        }
        return trans.get(meal_type)