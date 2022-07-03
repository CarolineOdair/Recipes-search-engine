from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

from scrapers_dict import scrapers_
from src.base.utils import MealType, IngrMatch

class ScraperManager:
    def __init__(self):
        self.logger_setup()
        self.scrapers = [scraper() for scraper in scrapers_.values()]

        self.manager_resp = {
            "error": {"ingrs": "", "meal_types": "", "ingrs_match": "", "other": ""},
            "msg": "",
            "recipes": [],
            "number_of_recipes": 0,
        }

    def get_recipes(self, *args, **kwargs):
        logging.info(f"New search: {kwargs}")

        self.args = args
        can_continue, self.kwargs = self.params_validation(kwargs)

        if not can_continue:
            logging.warning(f"Program can't continue, invalid params. Returned response {self.manager_resp}")
            return self.manager_resp

        # start = datetime.now()
        # recipes = [scraper.get_recipes(*args, **kwargs) for scraper in self.scrapers]
        # print(f"Time taken: {datetime.now()-start}")

        start = datetime.now()

        recipes = self.manage_many_scrapers_at_once(self.scrapers)

        taken_time = round((datetime.now()-start).total_seconds(), 2)
        logging.info(f"Time taken: {taken_time}s")

        self.manager_resp["recipes"] = recipes
        self.manager_resp["number_of_recipes"] = sum([recipe["n_recipes"] for recipe in recipes])
        return self.manager_resp

    def logger_setup(self):
        logging.basicConfig(level=logging.INFO,
                            filename='sample.log',
                            filemode='a',
                            format='[%(asctime)s] %(process)d [%(levelname)s] | %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    def manage_many_scrapers_at_once(self, scrapers=None):
        """ The function is responsible for multithreading """
        recipes = []

        def make_request(scraper):
            args = self.args
            kwargs = self.kwargs
            web_recipes = scraper.get_recipes(*args, **kwargs)
            recipes.append(web_recipes)

        def make_all_requests(scrapers) -> None:
            with ThreadPoolExecutor(max_workers=30) as executor:
                executor.map(make_request, scrapers)

        make_all_requests(scrapers)

        return recipes

    def params_validation(self, kwargs:dict) -> (bool, dict):
        """
        Checks if given params are valid

        Returns:
            [bool] - False if program has to stop, otherwise True
            kwargs [dict] - checked and eventually slightly changed key word arguments
        """

        # ingredients
        are_ingrs, val_ingrs = self.are_ingrs_valid(kwargs.get("ingrs"))
        are_m_t, val_meal_types = self.are_meal_types_valid(kwargs.get("meal_types"))
        is_ingrs_match, val_ingr_match = self.is_ingr_match_valid(kwargs.get("ingrs_match"))

        are_valid = [are_ingrs, are_m_t, is_ingrs_match]
        if not all(are_valid):
            return False, kwargs


        kwargs["ingrs"] = val_ingrs

        if kwargs.get("meal_types") is not None:
            kwargs["meal_types"] = val_meal_types

        # if kwargs.get("meal_types") is None:
            # kwargs["ingrs_match"]
        if kwargs.get("ingrs_match") is not None:
            kwargs["ingrs_match"] = val_ingr_match

        return True, kwargs

    def are_ingrs_valid(self, ingrs:list) -> bool:
        """ Checks if `ingrs` is valid - should be a list of strings """
        var = "ingrs"
        MAX_INGRS = 10

        if ingrs is None:  # if is None
            self.manager_resp["error"][var] = f"`{var}` is None, must be a list"
            return False, None

        elif not isinstance(ingrs, list):  # if isn't a list
            self.manager_resp["error"][var] = f"`{var}` is {type(ingrs)}, must be a list"
            return False, None

        elif isinstance(ingrs, list) and len(ingrs) == 0:  # if is an empty list
            self.manager_resp["error"][var] = f"`{var}` is an empty list"
            return False, None

        elif isinstance(ingrs, list) and len(ingrs) > MAX_INGRS:  # if is a list of to many elements
            self.manager_resp["error"][var] = f"Too many ingredients: {len(ingrs)}"
            return False, None

        else:  # checks elements of a list
            checked_ingrs = []
            for ingr in ingrs:
                if isinstance(ingr, str):  # if is a string
                    checked_ingrs.append(ingr)
                else:  # if isn't a string
                    self.manager_resp["error"][var] = f"Not every ingredient is a str, {type(ingr)} has occurred."
                    return False, None
            return True, checked_ingrs

    def are_meal_types_valid(self, meal_types:list) -> (bool, list or None):
        """ Checks if meal_types is valid - should be variables of MealTypes class """

        var = "meal_types"
        real_meal_types = MealType.show_variables()  # list of MealType variables values

        if meal_types is None:  # if is None - user doesn't filter by meal_types
            return True, None

        elif not isinstance(meal_types, list):  # if isn't a list
            self.manager_resp["error"][var] = f"`{var}` is {type(meal_types)}, must be a list"
            return False, None

        elif len(meal_types) == 0:  # if is an empty list
            return True, None

        # list of given meal_types which are MealTypes class variables
        validated_types = [m_type for m_type in meal_types if m_type in real_meal_types]

        if len(meal_types) != 0 and len(validated_types) == 0:
            # if given meal_types wasn't an empty list but None of meal_types was MealType class variable
            self.manager_resp["error"][var] = f"Invalid `{var}`: {meal_types}"
            # logging.warning(f"None of meal_types ({meal_types}) is valid meal type")
            return False, []

        else:
            # else - if given meal_types wasn't an empty list and some of them (at least one) was MealType class variables
            return True, validated_types


    def is_ingr_match_valid(self, ingrs_match:str) -> (bool, str or None):
        """ Checks if `ingrs_match` is valid - should be IngrMatch variable value """

        var = "ingrs_match"
        real_ingrs_match = IngrMatch.show_variables()  # list of IngrMatch variables values

        if ingrs_match is None:  # if is None - user doesn't filter by ingrs_match
            return True, None

        elif not isinstance(ingrs_match, str):   # if isn't a string
            self.manager_resp["error"][var] = f"`{var}` is {type(ingrs_match)}, must be a string"
            return False, None

        elif ingrs_match not in real_ingrs_match:  # if isn't an IngrMatch variable value
            self.manager_resp["error"][var] = f"Invalid `{var}`: '{ingrs_match}'"
            return False, None

        else:
            return True, ingrs_match
