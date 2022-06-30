from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

from scrapers_dict import scrapers_

class ScraperManager:
    def __init__(self):
        self.logger = self.logger_setup()
        self.scrapers = [scraper() for scraper in scrapers_.values()]

        # TODO - meal_types validation in ScraperManager

    def get_recipes(self, *args, **kwargs):
        logging.info(f"New search: {kwargs}")

        # start = datetime.now()
        # recipes = [scraper.get_recipes(*args, **kwargs) for scraper in self.scrapers]
        # print(f"Time taken: {datetime.now()-start}")

        self.args = args
        self.kwargs = kwargs

        start = datetime.now()
        recipes = self.manage_many_scrapers_at_once(self.scrapers)
        print(f"Time taken: {datetime.now()-start}")

        count = sum([recipe["n_recipes"] for recipe in recipes])
        print(count)

        return recipes

    def manage_many_scrapers_at_once(self, scrapers=None):
        """
            No token refreshing here, when token expires just start over
            This method is primarily meant for testing
            It can be used in production, but some adjustments should be made
        """
        recipes = []

        def make_request(scraper):
            args = self.args
            kwargs = self.kwargs
            web_recipes = scraper.get_recipes(*args, **kwargs)
            recipes.append(web_recipes)

        def make_all_requests(scrapers) -> None:
            with ThreadPoolExecutor(max_workers=20) as executor:
                executor.map(make_request, scrapers)

        make_all_requests(scrapers)

        return recipes

    def logger_setup(self):
        logger = logging.basicConfig(level=logging.INFO,
                                     filename='sample.log',
                                     filemode='a',
                                     format='[%(asctime)s] %(process)d [%(levelname)s] | %(message)s',
                                     datefmt='%Y-%m-%d %H:%M:%S')
        return logger
