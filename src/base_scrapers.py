import html
import requests

from bs4 import BeautifulSoup
from googletrans import Translator

from utils import do_list_includes_list

class BaseScraper:
    NAME = None
    DIET = None
    WEB_URL = None

    def __init__(self):
        if self.WEB_URL is None:
            raise Exception("`WEB_URL` is None, must be a string.")
        if self.DIET is None:
            raise NotImplementedError("`DIET` is None, must be MealTypes class property ")

        self.HTML_PARSER = "html.parser"
        self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
                        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                        'Accept': 'application/json'}

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        raise NotImplementedError()

    def get_data_from_resp(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs):
        """ Returns data from website's response """
        raise NotImplementedError()

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", web_url:str=None, *args, **kwargs) -> str:
        """ Returns url ready to be send to the website """
        return web_url

    def add_ingrs_to_url(self, ingrs:list, url:str, connector:str=",", word_conn:str="-", *args, **kwargs) -> str:
        """ Adds ingredients' parameter to url """
        return url

    def add_meal_type_to_url(self, meal_types:list, url:str, connector:str=",", *args, **kwargs) -> str:
        """ Adds meal types' parameter to url """
        return url

    def add_params_to_url(self, params:list, url:str, connector:str=",", param_name:str=None, word_conn:str="-", *args, **kwargs) -> str:
        """ Adds parameters to the url """
        if params is not None:
            if param_name:
                url += param_name
            for index, param in enumerate(params):
                if index != 0:
                    url += connector
                param = str(param).replace(" ", word_conn)
                url += param
        return url

    def get_meal_types_translated(self, meal_types:list, *args, **kwargs) -> list:
        if meal_types:
            rv = []
            for group_type in meal_types:
                m_type = self.meal_type_trans(group_type)
                if m_type is not None:
                    rv.extend(m_type)
            return rv
        else:
            return meal_types

    def get_resp_from_req(self, url:str, *args, **kwargs) -> str:
        """ Returns websites response (requests.models.Response object) or raise an exception if request failed """
        resp = requests.get(url, headers=self.HEADERS)
        if resp.ok and len(resp.text) != 0:
            return resp
        elif resp.ok and len(resp.text) == 0:
            return []
        else:
            raise Exception(f"Request failed, code: {resp.status_code}, url {resp.url}")

    def get_resp_from_req_with_404(self, url:str, *args, **kwargs) -> str:
        """ Returns websites response (requests.models.Response object) and 404 or raise an exception if request failed """
        resp = requests.get(url, headers=self.HEADERS)
        if resp.ok or resp.status_code == 404:
            return resp
        else:
            raise Exception(f"Request failed, code: {resp.status_code}, url {resp.url}")

    def recipe_data_to_dict(self, title:str=None, link:str=None) -> dict:
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
        return data

    def meal_type_trans(self, meal_type:str=None) -> list:
        raise NotImplementedError()

    def get_cleaned_data(self, data:dict, *args, **kwargs):
        """ Cleans data from unwanted characters """
        return data

    def pl_en_translate(self, words:list) -> list:
        """ Translates list of ingredients from polish to english """
        translator = Translator()
        translation = [translator.translate(word).text.lower() for word in words]
        return translation

    def more_title_cleaning(self, title:str=None, *args, **kwargs):
        """ Modifies title in final data """
        return title

    def more_link_cleaning(self, link:str=None, *args, **kwargs):
        """ Modifies title in final data """
        return link

class WordPressScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

        self.words_url_connector = "+"
        self.elements_url_connector = "+"

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions"""

        if self.exclude_by_params(ingrs, meal_types, ingrs_match):
            return self.data_to_dict([])

        meal_types_ = self.get_meal_types_translated(meal_types)
        ingrs, meal_types_ = self.finally_change_data_to_url(ingrs, meal_types_)

        if ingrs_match == "full":
            recipes = self.get_full_match_recipes(ingrs, meal_types_)
        elif ingrs_match == "partial":
            recipes = self.get_partial_match_recipes(ingrs, meal_types_)
        else:
            raise ValueError(f"`ingrs_match` must be 'full' or 'partial', not '{ingrs_match}'")

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # universal cleaning
        data = self.get_cleaned_data(data)  # cleaning specified for website
        return data

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> bool:
        """ Checks if parameters fulfill the conditions which will exclude entire request. """
        return False

    def finally_change_data_to_url(self, ingrs:list, meal_types:list, *args, **kwargs) -> (list, list):
        """ Finally changes data that have to be parameters put in the url """
        return ingrs, meal_types

    def get_full_match_recipes(self, ingrs:list, meal_types:list, *args, **kwargs) -> list:
        """ Returns list of recipes with full ingredients match """
        url = self.get_url(ingrs, meal_types)
        resp = self.get_resp_from_req(url)
        resp = resp.json()

        recipes = []
        for recipe in resp:
            valid_recipe = self.get_recipe_from_resp(recipe, ingrs, meal_types, ingrs_match="full")
            if valid_recipe:
                recipes.append(valid_recipe)
        return recipes

    def get_recipe_from_resp(self, recipe, ingrs, meal_types, check_in_soup:bool=True, ingrs_match:str="full", *args, **kwargs) -> dict:
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

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str="full", *args, **kwargs) -> bool:
        """ Checks if condition which exclude the recipe is fulfilled.
        Returns `True` if it is, otherwise returns `False` """
        return False

    def get_partial_match_recipes(self, ingrs:list, meal_types:list, *args, **kwargs) -> list:
        recipes = []
        for ingr in ingrs:
            url = self.get_url([ingr], meal_types)
            resp = self.get_resp_from_req(url)
            resp = resp.json()

            for recipe in resp:
                valid_recipe = self.get_recipe_from_resp(recipe, ingrs, meal_types, ingrs_match="partial")
                if valid_recipe and valid_recipe not in recipes:
                    recipes.append(valid_recipe)
        return recipes

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", web_url:str=None, *args, **kwargs) -> str:
        if web_url is None:
            web_url = self.WEB_URL
        url = web_url

        url = self.add_params_to_url(ingrs, url=url, param_name=self.ingr_param,
                                     word_conn=self.words_url_connector, connector=self.elements_url_connector)
        url = self.add_meal_type_to_url(meal_types, url=url, connector=self.elements_url_connector)
        print(url)
        return url

    def add_meal_type_to_url(self, meal_types:list, url:str, connector:str="+", *args, **kwargs) -> str:
        if meal_types is not None and self.meal_type_param is not None:
            url += self.meal_type_param
            if type(meal_types) == int:
                url += str(meal_types)

            elif type(meal_types) == list:
                for index, tag in enumerate(meal_types):
                    if index != 0:
                        url += connector
                    url += str(tag)
        return url

    def add_ingrs_to_url(self, ingrs:list, url:str, connector:str=",", word_conn:str="-", *args, **kwargs) -> str:
        url += "&search="
        for index, ingr in enumerate(ingrs):
            if index != 0:
                url += connector
            ingr = ingr.replace(" ", word_conn)
            url += ingr
        return url

    def meal_type_trans(self, group_type:str=None):
        raise NotImplementedError()

class TagsSearchingWordPressScraper(WordPressScraper):
    TAG_URL = None

    def __init__(self):
        super().__init__()

        if self.TAG_URL is None:
            raise NotImplementedError("`TAG_URL` is None, must be a string.")

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        ingrs_copy = ingrs.copy()  # to check if every ingredient has its tag

        # ingredients and meal_types changes
        ingrs_, meal_types_ = self.prep_args(ingrs, meal_types)

        # if user wants full ingredients' match but not all of them have the tags
        if ingrs_match == "full" and len(ingrs_copy) != len(ingrs_):
            return self.data_to_dict([])

        recipes = self.get_recipes_from_params(ingrs_, meal_types_, ingrs_match)

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # universal cleaning
        data = self.get_cleaned_data(data)  # cleaning specified for website
        return data

    def prep_args(self, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> (list, list):
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

    def prep_data_to_get_tags(self, ingrs:list=None, meal_types:list=None, *args, **kwargs):
        """ Changes data before getting ingredients tags """
        return ingrs, meal_types

    def get_ingrs_tags(self, ingrs:list, url:str, *args, **kwargs):
        """ Takes list of strings and url and returns list of their tags """
        url = self.add_params_to_url(params=ingrs, url=url, connector="+", word_conn="-")
        resp = self.get_resp_from_req(url)
        resp = resp.json()
        tags = [(tag["id"]) for tag in resp]
        return tags

    def get_recipes_from_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs):
        """ Makes request, filters data and returns list of recipes """
        url = self.get_url(ingrs, meal_types)
        resp = self.get_resp_from_req(url)
        resp = resp.json()

        recipes = []

        ingrs = [int(ingr) for ingr in ingrs]  # `ingrs` is a list of ints - ingredients' tags
        for recipe in resp:  # loop through items in website's response
            valid_recipe = self.get_recipe_from_resp(recipe, ingrs, meal_types, ingrs_match=ingrs_match,
                                                     check_in_soup=False)

            # if recipe is excluded for some reason, `get_recipe_from_resp` returns None and it needs to be omitted
            if valid_recipe:
                recipes.append(valid_recipe)

        return recipes

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str="full", *args, **kwargs) -> bool:
        """ Checks if current recipe should be excluded - it should if `ingrs_match` is 'full'
        but recipe do not have all wanted ingredients in its ingredients. """
        if self.web_recipe_exclusion_con(recipe, ingrs, meal_types, ingrs_match):
            return True

        if ingrs_match == "full":
            if not do_list_includes_list(recipe["tags"], ingrs):
                return True
            return False
        elif ingrs_match == "partial":
            return False
        else:
            raise Exception(f"`ingrs_match` must be 'full' or 'partial', not {ingrs_match}")

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs):
        """ Checks if current recipe should be excluded - returns True if it should, otherwise returns False """
        return False
