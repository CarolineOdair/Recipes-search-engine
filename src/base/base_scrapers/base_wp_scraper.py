from bs4 import BeautifulSoup

from src.base.base_scrapers.base_scraper import BaseScraper
from src.base.utils import IngrMatch, REQUEST_FAILED_MSG


class WordPressScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

        self.url_delimiter = "+"
        self.elements_connector = "+"

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions"""
        if self.exclude_by_params(ingrs, meal_types, ingrs_match):
            return self.data_to_dict([])

        ingrs_copy = ingrs.copy()
        meal_types_copy = self.meal_types_copy(meal_types)

        meal_types_ = self.get_meal_types_translated(meal_types)
        ingrs_, meal_types_ = self.finally_change_data_to_url(ingrs, meal_types_)

        if self.exclude_before_url(ingrs_, ingrs_copy, meal_types_, meal_types_copy, ingrs_match):
            return self.data_to_dict([])

        if ingrs_match == IngrMatch.FULL:
            recipes = self.get_full_match_recipes(ingrs, meal_types_)
        elif ingrs_match == IngrMatch.PART:
            recipes = self.get_partial_match_recipes(ingrs, meal_types_)
        else:
            raise ValueError(f"`ingrs_match` must be '{IngrMatch.FULL}' or '{IngrMatch.PART}', not '{ingrs_match}'")

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # universal cleaning
        data = self.get_cleaned_data(data)  # cleaning specified for website
        return data

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> bool:
        """ Checks if parameters fulfill the conditions which will exclude entire request. """
        return False

    def finally_change_data_to_url(self, ingrs:list, meal_types:list, *args, **kwargs) -> (list, list):
        """ Finally changes data that have to be parameters put in the url """
        return ingrs, meal_types

    def exclude_before_url(self, ingrs:list=None, ingrs_copy:list=None, meal_types:list=None,
                           meal_types_copy:list=None, ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Just before creating url checks if request should be omitted """
        if meal_types_copy is not None and len(meal_types) == 0:
            return True
        return False

    def get_full_match_recipes(self, ingrs:list, meal_types:list) -> list:
        """ Returns list of recipes with full ingredients match """
        url = self.get_url(ingrs, meal_types)
        response = self.get_response_from_request(url)

        if response == REQUEST_FAILED_MSG:
            return []

        response = response.json()

        recipes = []
        for recipe in response:
            valid_recipe = self.get_recipe_from_response(recipe, ingrs, meal_types, ingrs_match=IngrMatch.FULL)
            if valid_recipe:
                recipes.append(valid_recipe)
        return recipes

    def get_recipe_from_response(self, recipe, ingrs, meal_types, check_in_soup:bool=True, ingrs_match:str=IngrMatch.FULL) -> dict:
        """ Takes recipe and users search properties like ingredients, meal_types and ingrs_match
        and return recipe's title and link """
        add = True
        if self.exclude_one_recipe(recipe, ingrs, meal_types, ingrs_match):
            add = False

        elif check_in_soup:
            soup = BeautifulSoup(recipe["content"]["rendered"], features="html.parser")
            soup = soup.get_text().lower()
            for ingr in ingrs:
                if ingr.lower() not in soup:
                    add = False

        if add:
            title = recipe["title"]["rendered"]
            link = recipe["link"]
            return self.recipe_data_to_dict(title, link)
        return None

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> bool:
        """ Checks if condition which exclude the recipe is fulfilled.
        Returns `True` if it is, otherwise returns `False` """
        return False

    def get_partial_match_recipes(self, ingrs:list, meal_types:list) -> list:
        """ Returns recipes when ingrs_match is partial """
        recipes = []
        for ingr in ingrs:
            url = self.get_url([ingr], meal_types)
            response = self.get_response_from_request(url)

            if response == REQUEST_FAILED_MSG:
                return []

            response = response.json()

            for recipe in response:
                valid_recipe = self.get_recipe_from_response(recipe, ingrs, meal_types, ingrs_match=IngrMatch.PART)
                if valid_recipe and valid_recipe not in recipes:
                    recipes.append(valid_recipe)
        return recipes

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Returns url ready to be sent """
        if web_url is None:
            web_url = self.REQUEST_URL
        url = web_url

        url = self.add_params_to_url(ingrs, url=url, param_name=self.ingr_param,
                                     phrase_connector=self.url_delimiter, delimiter=self.elements_connector)
        url = self.add_params_to_url(meal_types, url=url, param_name=self.meal_type_param,
                                     delimiter=self.elements_connector)
        return url

    def meal_type_trans(self, group_type:str=None) -> list:
        """ Converts universally written meal_types to website's specific format """
        raise NotImplementedError()

