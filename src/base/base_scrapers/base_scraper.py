import html
import logging
import requests

from googletrans import Translator

from src.base import IngrMatch, REQUEST_FAILED_MSG


class BaseScraper:
    NAME = None
    DIET = None
    WEB_URL = None
    REQUEST_URL = None

    MAX_N_PAGES = 4  # while looping through pages (/page/n_page/...) MAX_N_PAGES is max n_page value
    TIMEOUT = 10

    def __init__(self):
        if self.WEB_URL is None:
            raise Exception("`WEB_URL` is None, must be a string.")
        if self.REQUEST_URL is None:
            raise Exception("`REQUEST_URL` is None, must be a string.")
        if self.DIET is None:
            raise NotImplementedError("`DIET` is None, must be MealTypes class property ")

        self.HTML_PARSER = "html.parser"
        self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                        'Accept': 'application/json'}

    def __str__(self):
        return f"{self.NAME}"

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL) -> dict:
        """
        Main function, calls function returning recipes which
        fulfill the conditions or an empty website's dictionary
        """
        try:
            return self.perform_get_recipes(ingrs, meal_types, ingrs_match)
        except Exception:
            logging.error(f"Problem with: {self}")
            return self.data_to_dict([])

    def perform_get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> dict:
        """ Main function to be programmed, returns recipes which fulfill the conditions """
        raise NotImplementedError()

    def get_data_from_response(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs):
        """ Returns data from website's response """
        raise NotImplementedError()

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, web_url:str=None, *args, **kwargs) -> str:
        """ Returns url ready to be send to the website """
        return web_url

    def add_params_to_url(self, params:list, url:str, delimiter:str= ",", param_name:str=None, phrase_connector:str= "-") -> str:
        """ Adds parameters to the url """
        if params is not None:
            if param_name:
                url += param_name
            for index, param in enumerate(params):
                if index != 0:
                    url += delimiter
                param = str(param).replace(" ", phrase_connector)
                url += param
        return url

    def meal_types_copy(self, meal_types:list=None) -> list:
        """ Returns meal_types copy or None if meal_types is None """
        if isinstance(meal_types, list):
            return meal_types.copy()
        return None

    def get_meal_types_translated(self, meal_types:list, *args, **kwargs) -> list:
        """ Changes universally written meal_types to the website's specific form """
        if meal_types:
            rv = []
            for group_type in meal_types:
                m_type = self.meal_type_trans(group_type)
                if m_type is not None:
                    rv.extend(m_type)
            return rv
        else:
            return meal_types

    def get_response_from_request(self, url:str) -> requests.models.Response:
        """
        Returns websites response (requests.models.Response object)
        or raise an exception if request failed
        """
        response = requests.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)

        if response.ok and len(response.text) != 0:
            self.add_request_log("debug", response, url=self.WEB_URL)
            return response

        else:
            self.add_request_log("warning", response)
            return REQUEST_FAILED_MSG
            # raise Exception(f"Request failed, code: {response.status_code}, url {response.url}")

    def get_response_from_request_with_404(self, url:str) -> requests.models.Response:
        """
        Returns websites "ok" and 404 response (requests.models.Response object)
        or raise an exception if request failed
        """
        response = requests.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)

        if response.ok or response.status_code == 404:
            self.add_request_log("debug", response, url=self.WEB_URL)
            return response

        else:
            self.add_request_log("warning", response)
            return REQUEST_FAILED_MSG
            # raise Exception(f"Request failed, code: {response.status_code}, url {response.url}")

    def recipe_data_to_dict(self, title:str, link:str) -> dict:
        """ Returns dict with info about a recipe """
        return {"title": title, "link": link}

    def data_to_dict(self, recipes) -> dict:
        """ Returns dict with info about a web and search """
        return {"web_name": self.NAME,
                "cuisine_type": self.DIET,
                "recipes": recipes,
                "n_recipes": len(recipes)}

    def clean_data(self, data:dict) -> dict:
        """ Cleans titles from characters encoded with html """
        replace = {"\xa0": " ", "<em>": "", "</em>": ""}
        if data["recipes"]:
            for recipe in data["recipes"]:

                for (key, val) in replace.items():
                    recipe["title"] = recipe["title"].replace(key, val)
                recipe["title"] = html.unescape(recipe["title"])
                recipe["title"] = recipe["title"].strip()

                recipe["title"] = self.more_title_cleaning(recipe["title"])
                recipe["link"] = self.more_link_cleaning(recipe["link"])
        return data

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        """
        Should be a dictionary:
            key - MealTypes variable
            value - list of names [str] or ids [int] which represent the category on the website

        Exemplar:

        trans = {
            MealType.TO_BREAD: [1],
            MealType.DRINK: [2],
            MealType.DINNER: [3, 4],
            MealType.LUNCH: [5],
            MealType.BREAKFAST: [6],
            MealType.SOUP: [7],
            MealType.DESSERT: [8, 9, 10],
            MealType.SNACKS: None,
        }
        return trans.get(meal_type)
        """

        raise NotImplementedError()

    def pl_en_translate(self, words:list) -> list:
        """ Translates list of ingredients from polish to english """
        translator = Translator()
        translation = [translator.translate(word, src="pl", dest="en").text.lower() for word in words]
        return translation

    def more_title_cleaning(self, title:str=None) -> str:
        """ Modifies title in final data """
        return title

    def more_link_cleaning(self, link:str=None) -> str:
        """ Modifies title in final data """
        return link

    def add_request_log(self, levelname:str="info", response:requests.models.Response=None,
                        url:str=None) -> None:
        """ Adds logs to logger """

        if levelname == "debug":
            logging.debug(f"{response.status_code}, {response.elapsed.total_seconds()}, {url}")
        elif levelname == "warning":
            logging.warning(f"{response.status_code}, {response.elapsed.total_seconds()}, {response.url}")
        else:
            logging.info(f"{response}, {url}")
