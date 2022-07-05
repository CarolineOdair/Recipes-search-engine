from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

from scrapers_dict import scrapers_
from src.base.params_validator import ParamsValidator

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

        validator = ParamsValidator()
        can_continue, self.kwargs, self.manager_response = validator.validation(params=kwargs, response=self.manager_response)

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
