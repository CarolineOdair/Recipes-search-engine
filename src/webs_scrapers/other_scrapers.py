import logging

from bs4 import BeautifulSoup

from src.base.base_scrapers import BaseScraper
from src.base import CuisineType, MealType, IngrMatch  # classes
from src.base import REQUEST_FAILED_MSG, EXCEPTION_LOG_MSG  # strings


class JadlonomiaScraper(BaseScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'www.jadlonomia.com'.
    """
    # JadlonomiaScraper was the first one I was doing and after some time I've realised that
    # Jadlonomia.com also uses wp-json, so it would be much better if the scraper have inherited from WordPressScraper
    PRECISE_SEARCH = True

    NAME = "Jadłonomia"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://www.jadlonomia.com"

    REQUEST_URL = WEB_URL + "/przepisy/?ajax=1"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&skladnik="
        self.meal_type_param = "&rodzaj_dania="

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        meal_types_copy = self.meal_types_copy(meal_types)

        # translates meal_types to website friendly version (e.x. 'sniadanie' to 'sniadania')
        meal_types = self.get_meal_types_translated(meal_types)

        if meal_types_copy is not None and len(meal_types) == 0:
            return self.data_to_dict([])

        url = self.get_url(ingrs, meal_types, ingrs_match)  # constructs url
        response = self.get_response_from_request(url)  # gets html

        if response == REQUEST_FAILED_MSG:
            return self.data_to_dict([])

        response = response.text

        recipes = []  # add scrapped recipes to list
        for recipe in self.get_data_from_response(response):
            recipes.append(recipe)

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # clean data
        return data

    def get_url(self, ingrs:list, meal_type:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Returns url ready to be send """

        if web_url is None:
            web_url = self.REQUEST_URL
        url = web_url

        url = self.add_params_to_url(params=ingrs, url=url, param_name=self.ingr_param, delimiter=self.get_delimiter(ingrs_match))
        url = self.add_params_to_url(params=meal_type, url=url, param_name=self.meal_type_param, delimiter=self.get_delimiter(IngrMatch.PART))
        return url

    def get_delimiter(self, match:str) -> str:
        """ Based on `match` returns proper delimiter to connect the values in the url """
        if match == IngrMatch.FULL:
            return "+"  # means "and"
        return ","  # means "or"

    def get_data_from_response(self, web_response:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Filters response and returns only useful information about recipes - title and link """
        soup = BeautifulSoup(web_response, self.HTML_PARSER)
        try:
            recipe_grid = soup.find(class_="clear row")
            articles = recipe_grid.find_all(class_="text absolute")

            for article in articles:
                link = article.h2.a["href"]
                title = article.h2.a.text

                yield self.recipe_data_to_dict(title, link)
        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.BREAKFAST: ["sniadania"],
            MealType.SOUP: ["zupy"],
            MealType.DINNER: ["dania-glowne"],
            MealType.LUNCH: ["lunche-do-pracy"],
            MealType.TO_BREAD: ["do-chleba"],
            MealType.DESSERT: ["ciasta-i-desery"],
            MealType.DRINK: ["napoje"],
            MealType.SAUCE: ["sosy-i-dodatki"],
            }
        return trans.get(meal_type)

class WeganonScraper(BaseScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'weganon.pl'.
    """
    PRECISE_SEARCH = False

    NAME = "Weganon"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://weganon.pl"

    REQUEST_URL = WEB_URL + "/page/{}/?post_type=post"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&s="
        self.meal_type_param = "&category_name="

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        meal_types_copy = self.meal_types_copy(meal_types)

        meal_types = self.get_meal_types_translated(meal_types)

        if meal_types_copy is not None and len(meal_types) == 0:
            return self.data_to_dict([])

        if ingrs_match == IngrMatch.FULL:
            recipes = self.get_full_match_recipes(ingrs, meal_types=meal_types)
        elif ingrs_match == IngrMatch.PART:
            recipes = self.get_partial_match_recipes(ingrs, meal_types=meal_types)
        else:
            raise Exception(f"`ingrs_match` must be '{IngrMatch.FULL}' or '{IngrMatch.PART}', not '{ingrs_match}'")

        data = self.data_to_dict(recipes)
        data = self.clean_data(data)

        return data

    def get_full_match_recipes(self, ingrs:list, meal_types:list=None) -> list:
        """ Return list of recipes which ingredients match fully """
        recipes = []
        for recipe in self.get_match_recipes(ingrs, meal_types):
            if recipe not in recipes:
                recipes.append(recipe)
        return recipes

    def get_partial_match_recipes(self, ingrs:list, meal_types:list=None) -> list:
        """ Return list of recipes which ingredients match partially """
        recipes = []

        for ingr in ingrs:
            for recipe in self.get_match_recipes([ingr], meal_types=meal_types):
                if recipe not in recipes:
                    recipes.append(recipe)

        return recipes

    def get_match_recipes(self, ingrs:list, meal_types:list=None) -> dict:
        """ Creates and makes requests and yields recipes which are returns in the requests """
        for url in self.get_url(ingrs, meal_types):

            response = self.get_response_from_request_with_404(url)
            # loops through next pages: 1st, 2nd, 3rd so on and stops when ther's no such page (status_code 404 occurs) -
            if response.status_code == 404:
                break

            for recipe in self.get_data_from_response(response.text):
                yield recipe

    def get_data_from_response(self, web_response:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Gets web's response and returns dictionary with recipes' title and link """
        soup = BeautifulSoup(web_response, self.HTML_PARSER)
        try:
            container = soup.find(class_="row")

            recipes_container = container.find_all(class_="fix-special")
            for recipe in recipes_container:
                recipe_info_container = recipe.find(class_="item-title").a
                link = recipe_info_container["href"]
                title = recipe_info_container["title"]

                yield self.recipe_data_to_dict(title=title, link=link)
        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Return url ready to be sent """
        url = self.REQUEST_URL
        url = self.add_params_to_url(ingrs, url, param_name=self.ingr_param)
        url = self.add_params_to_url(meal_types, url, param_name=self.meal_type_param)

        n_page = 1
        while True:
            if n_page > self.MAX_N_PAGES:
                break
            yield url.format(n_page)
            n_page += 1

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.DESSERT: ["na-slodko"],
            MealType.DINNER: ["dania-obiadowe"],
            MealType.LUNCH:["salatki"],
            MealType.TO_BREAD: ["pasty-do-pieczywa"],
            MealType.SOUP: ["zupy-i-kremy"],
            MealType.BREAKFAST: ["sniadania"],
        }
        return trans.get(meal_type)

class VeganbandaScraper(BaseScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'veganbanda.pl'.
    """
    PRECISE_SEARCH = True

    NAME = "veganbanda"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://veganbanda.pl"

    NOT_FOUND_RECIPES_MSG = "Przepraszam, brak pasujących wyników wyszukiwania."

    REQUEST_URL = WEB_URL + "/page/{}/?s=&post_type=recipe"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&recipe-tag="
        self.meal_type_param = "&course="

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        meal_types_copy = self.meal_types_copy(meal_types)

        meal_types = self.get_meal_types_translated(meal_types)

        if meal_types_copy is not None and len(meal_types) == 0:
            return self.data_to_dict([])

        recipes = self.get_match_recipes(ingrs, meal_types, ingrs_match, self.REQUEST_URL)

        data = self.data_to_dict(recipes)
        data = self.clean_data(data)
        return data

    def get_match_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None) -> list:
        """ Creates url, makes requests and returns list of recipes """
        recipes = []

        try:
            for url in self.get_url(ingrs, meal_types,ingrs_match, web_url):

                response = self.get_response_from_request_with_404(url)
                # loops through pages: 1st, 2nd, 3rd and so on and when there's no more (response with status code 404 occurs), stops
                if response.status_code == 404:
                    break
                if self.NOT_FOUND_RECIPES_MSG in response.text:
                    break

                for recipe in self.get_data_from_response(response.text):
                    if recipe not in recipes:
                        recipes.append(recipe)

        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

        return recipes

    def get_data_from_response(self, web_response:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Gets websites response and yields recipes """
        soup = BeautifulSoup(web_response, self.HTML_PARSER)
        try:
            container = soup.find(class_="recipe-grid")
            recipes_containers = container.find_all(class_="item-content")

            for recipe in recipes_containers:
                recipe_info_container = recipe.find(class_="item-title")

                title = recipe_info_container.text
                link = recipe_info_container.a["href"]

                yield self.recipe_data_to_dict(title=title, link=link)
        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Return url ready to be sent """
        url = self.REQUEST_URL
        url = self.add_params_to_url(ingrs, url, param_name=self.ingr_param, delimiter=self.get_delimiter(ingrs_match))
        url = self.add_params_to_url(meal_types, url, param_name=self.meal_type_param)

        n_page = 1
        while True:
            if n_page > self.MAX_N_PAGES:
                break
            yield url.format(n_page)
            n_page += 1

    def get_delimiter(self, ingrs_match:str=IngrMatch.FULL) -> str:
        """ Depending on ingrs_match returns character which should connect elements in the url """
        if ingrs_match == IngrMatch.PART:
            return ","
        return "+"

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.TO_BREAD: ["dokanapek"],
            MealType.DRINK: ["napoje"],
            MealType.DINNER: ["daniaglowne", "vege-grill"],
            MealType.SNACKS: ["przekaski"],
            MealType.LUNCH: ["do-szkoly-do-pracy"],
            MealType.BREAKFAST: ["sniadania"],
            MealType.SOUP: ["zupy"],
        }
        return trans.get(meal_type)

class EkspresjaSmakuScraper(BaseScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'ekspresjasmaku.com'.
    """
    PRECISE_SEARCH = False

    NAME = "Ekspresja Smaku"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://ekspresjasmaku.com"

    NOT_FOUND_RECIPES_MSG = "Szukana fraza nie została znaleziona, spróbuj ponownie"

    MUST_INCLUDE_CATEGORY = "Wegańskie"
    REQUEST_URL = WEB_URL + "/page/{}/?s"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&tag="
        self.meal_type_param = "&cat="

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        meal_types_copy = self.meal_types_copy(meal_types)

        meal_types = self.get_meal_types_translated(meal_types)

        if meal_types_copy is not None and len(meal_types) == 0:
            return self.data_to_dict([])

        recipes = self.get_match_recipes(ingrs, meal_types, ingrs_match, self.REQUEST_URL)

        data = self.data_to_dict(recipes)
        data = self.clean_data(data)
        return data

    def get_match_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL,
                          web_url:str=None) -> list:
        """ Creates url, makes requests and returns list of recipes """
        recipes = []

        try:
            for url in self.get_url(ingrs, meal_types,ingrs_match, web_url):

                response = self.get_response_from_request_with_404(url)
                # loops through pages: 1st, 2nd, 3rd and so on and when there's no more (response with status code 404 occurs), stops
                if response.status_code == 404:
                    break
                if self.NOT_FOUND_RECIPES_MSG in response.text:
                    break

                for recipe in self.get_data_from_response(response.text):
                    if recipe not in recipes:
                        recipes.append(recipe)

        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

        return recipes

    def get_data_from_response(self, web_response:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Gets websites response and yields recipes """
        soup = BeautifulSoup(web_response, self.HTML_PARSER)

        try:
            container = soup.find(class_="sp-grid col3")
            recipes_containers = container.find_all(class_="post-header")

            for recipe in recipes_containers:
                title_link_container = recipe.find(class_="entry-title")
                title = title_link_container.text
                link = title_link_container.a["href"]

                categories = recipe.find(class_="cat").text
                if self.MUST_INCLUDE_CATEGORY in categories:
                    yield self.recipe_data_to_dict(title=title, link=link)

        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Return url ready to be sent """
        url = self.REQUEST_URL
        url = self.add_params_to_url(ingrs, url, param_name=self.ingr_param, delimiter=self.get_delimiter(ingrs_match))
        url = self.add_params_to_url(meal_types, url, param_name=self.meal_type_param)

        n_page = 1
        while True:
            if n_page > self.MAX_N_PAGES:
                break
            yield url.format(n_page)
            n_page += 1

    def get_delimiter(self, ingrs_match:str=IngrMatch.FULL) -> str:
        """ Depending on ingrs_match returns character which should connect elements in the url """
        if ingrs_match == IngrMatch.PART:
            return ","
        return "+"

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.TO_BREAD: [202],  # 'do-chleba'
            MealType.DRINK: [201],  # 'smoothies'
            MealType.DINNER: [93, 94, 200],  # 'obiad', 'kolacja', 'salatki-i-surowki'
            MealType.LUNCH: [197],  # 'lunch'
            MealType.BREAKFAST: [92],  # 'sniadanie'
            MealType.SOUP: [199],  # 'zupy'
            MealType.DESSERT: [108, 203],  # 'desery', 'ciasta'
        }
        return trans.get(meal_type)

class WegannerdScraper(BaseScraper):
    """
    Searches for recipes with given ingredients on 'wegannerd.com'.
    """
    PRECISE_SEARCH = False

    NAME = "wegan nerd"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://www.wegannerd.com"

    NOT_FOUND_RECIPES_MSG = "Brak postów spełniających kryteria wyszukiwania:"

    REQUEST_URL = WEB_URL + "/search?max-results=40"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&q="

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        if meal_types is not None:
            return self.data_to_dict([])

        if ingrs_match == IngrMatch.FULL:
            recipes = self.get_full_match_recipes(ingrs)
        elif ingrs_match == IngrMatch.PART:
            recipes = self.get_partial_match_recipes(ingrs)
        else:
            return self.data_to_dict([])

        data = self.data_to_dict(recipes)
        data = self.clean_data(data)
        return data

    def get_partial_match_recipes(self, ingrs:list) -> list:
        """ Return list of recipes which ingredients match partially """
        recipes = []

        for ingr in ingrs:
            for recipe in self.get_match_recipes([ingr]):
                if recipe not in recipes:
                    recipes.append(recipe)

        return recipes

    def get_full_match_recipes(self, ingrs:list) -> list:
        """ Return list of recipes which ingredients match fully """
        recipes = []
        for recipe in self.get_match_recipes(ingrs):
            if recipe not in recipes:
                recipes.append(recipe)

        return recipes

    def get_match_recipes(self, ingrs:list) -> dict:
        """ Creates url, makes request and yields recipes """
        url = self.get_url(ingrs)
        response = self.get_response_from_request(url)

        for recipe in self.get_data_from_response(response.text):
            yield recipe

    def get_data_from_response(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Gets websites response, makes html scraping and yields recipes """
        soup = BeautifulSoup(web_resp, self.HTML_PARSER)
        try:
            container = soup.find(id="Blog1")
            recipe_containers = container.find_all(class_="post-title entry-title")

            for recipe in recipe_containers:
                title = recipe.text.strip()
                link = recipe.a["href"]

                yield self.recipe_data_to_dict(title=title, link=link)

        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Return url ready to be sent """
        if web_url is None:
            web_url = self.REQUEST_URL

        web_url = self.add_params_to_url(ingrs, param_name=self.ingr_param, delimiter="+", url=web_url)

        return web_url

class TrueTasteHuntersScraper(BaseScraper):
    """
    Searches for recipes with given ingredients on 'truetastehunters.com'.
    """
    PRECISE_SEARCH = True

    NAME = "true taste hunters"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://www.truetastehunters.com"

    NOT_FOUND_RECIPES_MSG = "Nie znaleziono wyników"

    REQUEST_URL = WEB_URL + "/search?max-results=50"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&q="

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        if meal_types is not None:
            return self.data_to_dict([])

        if ingrs_match == IngrMatch.FULL:
            recipes = self.get_full_match_recipes(ingrs)
        elif ingrs_match == IngrMatch.PART:
            recipes = self.get_partial_match_recipes(ingrs)
        else:
            return self.data_to_dict([])

        data = self.data_to_dict(recipes)
        data = self.clean_data(data)
        return data

    def get_partial_match_recipes(self, ingrs:list) -> list:
        """ Return list of recipes which ingredients match partially """
        recipes = []

        for ingr in ingrs:
            for recipe in self.get_match_recipes([ingr]):
                if recipe not in recipes:
                    recipes.append(recipe)

        return recipes

    def get_full_match_recipes(self, ingrs:list) -> list:
        """ Return list of recipes which ingredients match fully """
        recipes = []
        for recipe in self.get_match_recipes(ingrs):
            if recipe not in recipes:
                recipes.append(recipe)

        return recipes

    def get_match_recipes(self, ingrs:list) -> dict:
        """ Creates url, makes request and yields recipes """
        url = self.get_url(ingrs)
        response = self.get_response_from_request(url)

        for recipe in self.get_data_from_response(response.text):
            if not self.do_exclude_recipe(recipe):
                yield recipe

    def get_data_from_response(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Gets websites response, makes html scraping and yields recipes """
        soup = BeautifulSoup(web_resp, self.HTML_PARSER)
        try:
            container = soup.find(id="Blog1")
            recipe_containers = container.find_all(class_="post-title entry-title")

            for recipe in recipe_containers:
                title = recipe.text.strip()
                link = recipe.a["href"]

                yield self.recipe_data_to_dict(title=title, link=link)

        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

    def do_exclude_recipe(self, recipe_dict:dict) -> bool:
        """ Returns True if recipe should be excluded, otherwise False """
        EXCLUDE_PHRASES = ["Stary Browar", "Starego Browaru", "Starym Browarze", "Starym Browarem"]
        # there are some articles, not recipes, so not what is needed. The articles have in name different forms of
        # 'Stary Browar', restaurant, I guess. So every recipe having in title 'Stary Browar' or its form will be excluded

        for phrase in EXCLUDE_PHRASES:
            if phrase in recipe_dict["title"]:
                return True

        return False

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Return url ready to be sent """
        if web_url is None:
            web_url = self.REQUEST_URL

        web_url = self.add_params_to_url(ingrs, param_name=self.ingr_param, delimiter="+", url=web_url)

        return web_url

class WegankaScraper(BaseScraper):
    """
    Searches for recipes with given ingredients on 'weganka.com'.
    """
    PRECISE_SEARCH = False

    NAME = "wegAnka"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://www.weganka.com"

    NOT_FOUND_RECIPES_MSG = "Nie znaleziono wyników"

    REQUEST_URL = WEB_URL + "/search?max-results=50"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&q="

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """

        if meal_types is not None:
            return self.data_to_dict([])

        if ingrs_match == IngrMatch.FULL:
            recipes = self.get_full_match_recipes(ingrs)
        elif ingrs_match == IngrMatch.PART:
            recipes = self.get_partial_match_recipes(ingrs)
        else:
            return self.data_to_dict([])

        data = self.data_to_dict(recipes)
        data = self.clean_data(data)

        return data

    def get_full_match_recipes(self, ingrs:list) -> list:
        """ Return list of recipes which ingredients match fully """
        recipes = []

        for recipe in self.get_match_recipes(ingrs):
            if recipe not in recipes:
                recipes.append(recipe)

        return recipes

    def get_partial_match_recipes(self, ingrs:list) -> list:
        """ Return list of recipes which ingredients match partially """
        recipes = []

        for ingr in ingrs:
            for recipe in self.get_match_recipes([ingr]):
                if recipe not in recipes:
                    recipes.append(recipe)

        return recipes

    def get_match_recipes(self, ingrs:list) -> dict:
        """ Creates url, makes request and yields recipes """
        url = self.get_url(ingrs)
        response = self.get_response_from_request(url)

        for recipe in self.get_data_from_response(response.text):
            yield recipe

    def get_data_from_response(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> dict:
        """ Gets websites response, makes html scraping and yields recipes """
        soup = BeautifulSoup(web_resp, self.HTML_PARSER)
        try:
            container = soup.find(class_="blog-posts hfeed container")

            containers = container.find_all(class_="post-title entry-title")
            for recipe in containers:
                title = recipe.text.strip()
                link = recipe.a["href"]
                yield self.recipe_data_to_dict(title=title, link=link)

        except Exception:
            logging.exception(EXCEPTION_LOG_MSG)

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Return url ready to be sent """
        if web_url is None:
            web_url = self.REQUEST_URL

        web_url = self.add_params_to_url(params=ingrs, param_name=self.ingr_param, delimiter="+", url=web_url)

        return web_url
