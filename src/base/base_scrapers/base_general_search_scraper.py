from src.base import IngrMatch, REQUEST_FAILED_MSG
from src.base.base_scrapers import BaseScraper


class GeneralSearchScraper(BaseScraper):

    ENG_WEB = False
    PRECISE_SEARCH = True

    def __init__(self):
        super().__init__()

        self.ingr_param = ""

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        meal_types_copy = self.meal_types_copy(meal_types)

        ingrs, meal_types = self.prep_args(ingrs, meal_types)

        if meal_types_copy is not None and len(meal_types) == 0:
            return self.data_to_dict([])

        # gets recipes differently depending on ingredients match
        if ingrs_match == IngrMatch.FULL:
            recipes = self.get_full_match_recipes(ingrs, meal_types)
        elif ingrs_match == IngrMatch.PART:
            recipes = self.get_partial_match_recipes(ingrs, meal_types)
        else:
            raise Exception(f"`ingrs_match` must be '{IngrMatch.FULL}' or '{IngrMatch.PART}', not '{ingrs_match}'")

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # clean data
        return data

    def get_data_from_response(self, web_response:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Filters data about recipe and returns useful part - title and link """
        raise NotImplementedError()

    def get_full_match_recipes(self, ingrs:list, meal_types:list=None) -> list:
        """ Returns list of recipes - puts all parameters to url in one go """
        url = self.get_url(ingrs)
        response = self.get_response_from_request(url)

        if response == REQUEST_FAILED_MSG:
            return []

        response = response.json()

        recipes = []
        for recipe in self.get_data_from_response(response, meal_types=meal_types):
            recipes.append(recipe)

        return recipes

    def get_partial_match_recipes(self, ingrs:list, meal_types:list=None) -> list:
        """ Returns list of recipes - makes requests for all ingredients separately """
        recipes = []
        for ingr in ingrs:  # loop through ingredients
            url = self.get_url([ingr])
            response = self.get_response_from_request(url)

            if response == REQUEST_FAILED_MSG:
                return []

            response = response.json()

            for recipe in self.get_data_from_response(response, meal_types=meal_types):
                if recipe not in recipes:
                    recipes.append(recipe)

        return recipes

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Returns url ready to be send """
        if web_url is None:
            web_url = self.REQUEST_URL
        url = web_url

        url = self.add_params_to_url(ingrs, url, param_name=self.ingr_param)
        return url

    def prep_args(self, ingrs:list, meal_types:list=None) -> (list, list):
        """ Modifies args from users form to url """
        if self.ENG_WEB:
            # translates ingredients from polish to english
            ingrs = self.pl_en_translate(ingrs)
        # if meal_types are given, translates general forms to this specific website
        meal_types = self.get_meal_types_translated(meal_types)
        return ingrs, meal_types
