from src.base.base_scrapers import WordPressScraper
from src.base import IngrMatch, do_list_includes_list


class TagsSearchingWordPressScraper(WordPressScraper):
    TAG_URL = None
    PRECISE_SEARCH = True

    def __init__(self):
        super().__init__()

        if self.TAG_URL is None:
            raise NotImplementedError("`TAG_URL` is None, must be a string.")

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

        self.tags_name = "tags"

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        if self.exclude_by_params(ingrs, meal_types, ingrs_match):
            return self.data_to_dict([])

        ingrs_copy = ingrs.copy()
        meal_types_copy = self.meal_types_copy(meal_types)

        # ingredients and meal_types changes
        ingrs_, meal_types_ = self.prep_args(ingrs, meal_types)

        if self.exclude_before_url(ingrs_, ingrs_copy, meal_types_, meal_types_copy, ingrs_match):
            return self.data_to_dict([])

        recipes = self.get_recipes_from_params(ingrs_, meal_types_, ingrs_match)

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # universal cleaning
        return data

    def prep_args(self, ingrs:list=None, meal_types:list=None) -> (list, list):
        """ Changes ingredients and meal_types given by user so they can be put into url """

        # MealType to webs categories
        meal_types_ = self.get_meal_types_translated(meal_types)
        # changes data before getting ingredients tags
        ingrs_, meal_type_ = self.prep_data_to_get_tags(ingrs, meal_types_)
        # typically written ingrs to web's tags
        ingrs_ = self.get_ingrs_tags(ingrs_, self.TAG_URL)
        # last change before putting into url
        ingrs_, meal_types_ = self.finally_change_data_to_url(ingrs_, meal_types_)

        return ingrs_, meal_types_

    def exclude_before_url(self, ingrs:list=None, ingrs_copy:list=None, meal_types:list=None,
                           meal_types_copy:list=None, ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Checks if requests should be omitted just before creating url """

        # if none of ingredients has its tag
        if len(ingrs) == 0:
            return True
        # if user specified meal_types but none of them is searchable on the website
        elif meal_types_copy is not None and len(meal_types) == 0:
            return True
        # if user wants full ingredients' match but not all of them have the tags
        if ingrs_match == IngrMatch.FULL and len(ingrs_copy) != len(ingrs):
            return True

        return False

    def prep_data_to_get_tags(self, ingrs:list=None, meal_types:list=None) -> (list, list):
        """ Changes data before getting ingredients tags """
        return ingrs, meal_types

    def get_ingrs_tags(self, ingrs:list, url:str) -> list:
        """ Takes list of strings and url and returns list of their tags """
        url = self.add_params_to_url(params=ingrs, url=url, delimiter="+", phrase_connector="-")
        response = self.get_response_from_request(url)
        response = response.json()
        tags = [(tag["id"]) for tag in response]
        return tags

    def get_recipes_from_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str=IngrMatch.FULL) -> list:
        """ Makes request, filters data and returns list of recipes """
        url = self.get_url(ingrs, meal_types)
        response = self.get_response_from_request(url)
        response = response.json()

        recipes = []

        ingrs = [int(ingr) for ingr in ingrs]  # `ingrs` is a list of ints - ingredients' tags
        for recipe in response:  # loop through items in website's response
            valid_recipe = self.get_recipe_from_response(recipe, ingrs, meal_types, ingrs_match=ingrs_match,
                                                         check_in_soup=False)

            # if recipe is excluded for some reason, `get_recipe_from_response` returns None and it needs to be omitted
            if valid_recipe:
                recipes.append(valid_recipe)

        return recipes

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Checks if current recipe should be excluded - it should if `ingrs_match` is 'full'
        but recipe do not have all wanted ingredients in its ingredients. """
        if self.web_recipe_exclusion_con(recipe, ingrs, meal_types, ingrs_match):
            return True

        if ingrs_match == IngrMatch.FULL:
            if not do_list_includes_list(recipe[self.tags_name], ingrs):
                return True
            return False
        elif ingrs_match == IngrMatch.PART:
            return False
        else:
            raise Exception(f"`ingrs_match` must be '{IngrMatch.FULL}' or '{IngrMatch.PART}', not '{ingrs_match}'")

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Checks if current recipe should be excluded - returns True if it should, otherwise returns False """
        return False
