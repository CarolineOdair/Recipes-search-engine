from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

from scrapers_dict import scrapers_
from src.base.utils import MealType, IngrMatch

class ScraperManager:
    def __init__(self):
        self.logger_setup()
        self.scrapers = [scraper() for scraper in scrapers_.values()]

        self.manager_response = {
            "error": {"ingrs": "", "meal_types": "", "ingrs_match": "", "other": ""},
            "msg": "",
            "recipes": [],
            "number_of_recipes": 0,
        }

    def get_recipes(self, *args, **kwargs):
        """ Returns get_recipes function, running the program or raises an exception """
        try:
            return self.perform_get_recipes(*args, **kwargs)
        except Exception:
            logging.exception("")

    def perform_get_recipes(self, *args, **kwargs):
        """ Main function managing scrapers and returning info about found recipes """

        logging.info(f"New search: {kwargs}")

        self.args = args
        can_continue, self.kwargs, self.manager_response = self.params_validation(kwargs=kwargs, manager_response=self.manager_response)

        if not can_continue:
            logging.warning(f"Program can't continue, invalid params. Returned response {self.manager_response}")
            return self.manager_response

        start = datetime.now()
        # recipes = [scraper.get_recipes(*args, **kwargs) for scraper in self.scrapers]
        # print(f"Time taken: {datetime.now()-start}")

        start = datetime.now()

        recipes = self.manage_many_scrapers_at_once(self.scrapers)

        taken_time = round((datetime.now()-start).total_seconds(), 2)
        logging.info(f"Time taken: {taken_time}s")

        self.manager_response["recipes"] = recipes
        self.manager_response["number_of_recipes"] = sum([recipe["n_recipes"] for recipe in recipes])
        return self.manager_response

    def logger_setup(self):
        """ Config of the project's logger """
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

    def params_validation(self, kwargs:dict, manager_response:dict) -> (bool, dict, dict):
        """
        Checks if given params are valid

        Returns:
            [bool] - False if program has to stop, otherwise True
            kwargs [dict] - checked and eventually slightly changed key word arguments
            rv [dict] - manager response
        """
        rv = manager_response

        # ingredients
        are_ingrs_valid, validated_ingrs, rv = self.are_ingrs_valid(kwargs.get("ingrs"), rv)
        are_m_t_valid, validated_meal_types, rv = self.are_meal_types_valid(kwargs.get("meal_types"), rv)
        is_ingrs_match_valid, validated_ingr_match, rv = self.is_ingr_match_valid(kwargs.get("ingrs_match"), rv)


        are_valid = [are_ingrs_valid, are_m_t_valid, is_ingrs_match_valid]
        if not all(are_valid):
            return False, kwargs, rv


        kwargs["ingrs"] = validated_ingrs

        if kwargs.get("meal_types") is not None:
            kwargs["meal_types"] = validated_meal_types

        if kwargs.get("ingrs_match") is not None:
            kwargs["ingrs_match"] = validated_ingr_match

        return True, kwargs, rv

    def are_ingrs_valid(self, ingrs:list, manager_response:dict) -> (bool, list or None, dict):
        """
        Checks if `ingrs` is valid - should be a list of strings

        Returns:
            can_continue [bool] - True if ingrs is valid, otherwise False
            rv_ingrs [list] - validated ingrs
            manager_response [dict] - managers response with added errors or messages
        """
        can_continue = False
        error = ""

        MAX_INGRS = 10

        if ingrs is None:  # if is None
            error = f"`ingrs` is None, must be a list"

        elif not isinstance(ingrs, list):  # if isn't a list
            error = f"`ingrs` is {type(ingrs)}, must be a list"

        elif len(ingrs) == 0:  # if is an empty list
            error = f"`ingrs` is an empty list"

        elif len(ingrs) > MAX_INGRS:  # if is a list of to many elements
            error = f"Too many ingredients: {len(ingrs)}"

        else:  # checks elements of a list
            invalid_ingr = [(ingr, type(ingr)) for ingr in ingrs if not isinstance(ingr, str) or not ingr]

            if len(invalid_ingr) > 0:
                error = f"Not every ingredient is a not empty str, {dict(invalid_ingr)}"
            else:
                can_continue = True

        if error:
            manager_response["error"]["ingrs"] = error

        return can_continue, ingrs, manager_response

    def are_meal_types_valid(self, meal_types:list, manager_response:dict) -> (bool, list or None, dict):
        """
        Checks if meal_types is valid - should be variables of MealTypes class

        Returns:
            [bool] - True if meal_types is valid, otherwise False
            [list or None] - validated meal_types
            manager_response [dict] - managers response with added errors or messages
        """

        real_meal_types = MealType.show_variables()  # list of MealType variables values

        if meal_types is None:  # if is None - user doesn't filter by meal_types
            return True, None, manager_response

        elif not isinstance(meal_types, list):  # if isn't a list
            error = f"`meal_types` is {type(meal_types)}, must be a list"
            manager_response["error"]["meal_types"] = error
            return False, None, manager_response

        elif len(meal_types) == 0:  # if is an empty list
            return True, None, manager_response


        # list of given meal_types which are MealTypes class variables
        validated_types = [meal_type for meal_type in meal_types if meal_type in real_meal_types]
        invalid_types = [meal_type for meal_type in meal_types if meal_type not in validated_types]

        if len(invalid_types) > 0:
            warning_msg = f"Invalid meal_type(s): {' '.join(invalid_types)}"
            manager_response["msg"] = warning_msg
            logging.warning(warning_msg)


        if len(meal_types) != 0 and len(validated_types) == 0:
            # if given meal_types wasn't an empty list but None of meal_types was MealType class variable
            manager_response["error"]["meal_types"] = f"Invalid `meal_types`: {invalid_types}"
            return False, validated_types, manager_response

        # else - if given meal_types wasn't an empty list and some of them (at least one) was MealType class variables
        return True, validated_types, manager_response


    def is_ingr_match_valid(self, ingrs_match:str, manager_response:dict) -> (bool, str or None):
        """ Checks if `ingrs_match` is valid - should be IngrMatch variable value

        Returns:
            can_continue [bool] - True if ingrs_match is valid, otherwise False
            rv_ingrs_match [list or None] - validated meal_types
            manager_response [dict] - managers response with added errors or messages
        """
        can_continue = True
        error = ""

        real_ingrs_match = IngrMatch.show_variables()  # list of IngrMatch variables values

        if ingrs_match is None:  # if is None - user doesn't filter by ingrs_match
            pass

        elif not isinstance(ingrs_match, str):   # if isn't a string
            error = f"`ingrs_match` is {type(ingrs_match)}, must be a string"
            can_continue = False

        elif ingrs_match not in real_ingrs_match:  # if isn't an IngrMatch variable value
            error = f"Invalid `ingrs_match`: '{ingrs_match}'"
            can_continue = False


        if error:
            manager_response["error"]["ingrs_match"] = error

        return can_continue, ingrs_match, manager_response
