from bs4 import BeautifulSoup
from pprint import pprint

from base_scrapers import BaseScraper, WordPressScraper, CuisineType, MealType
from utils import do_lists_have_common_element, do_list_includes_list

# class NotImplementedError(Exception):
#     pass


class MadeleineOliviaScraper(BaseScraper):
    NAME = "Madeleine Olivia"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://www.madeleineolivia.co.uk/api/search/GeneralSearch?q="
    RECIPE_URL = "https://www.madeleineolivia.co.uk/blog/"

    def __init__(self):
        super().__init__()

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full") -> dict:
        """ Main function, returns recipes which fulfill the conditions """

        ingrs, meal_types = self.prep_args(ingrs, meal_types)

        # gets recipes differently depending on ingredients match
        if ingrs_match == "full":
            recipes = self.get_full_match_recipes(ingrs, meal_types)
        elif ingrs_match == "partial":
            recipes = self.get_partial_match_recipes(ingrs, meal_types)
        else:
            raise Exception(f"`ingrs_match` must be `full` or `partial`, not {ingrs_match}")

        data = self.data_to_dict(recipes)  # add info to dict
        data = self.get_cleaned_data(data)  # clean data
        return data

    def get_data_from_resp(self, web_resp:str=None, ingrs:list=None, meal_types:list=None):
        """ Filters data about recipe and returns useful part - title and link """

        # loop through recipes
        for recipe in web_resp["items"]:

            # skips if meal_types are given but recipe categories do not contain none of the wanted types
            if meal_types is None or do_lists_have_common_element(recipe["categories"], meal_types):
                # print("in")
                title = recipe["title"]
                link = self.RECIPE_URL + recipe['urlId']

                yield self.recipe_data_to_dict(title, link)

    def get_full_match_recipes(self, ingrs:list, meal_types:list=None) -> list:
        """ Returns list of recipes - puts all parameters to url in one go """
        url = self.get_url(ingrs)
        resp = self.get_resp_from_req(url)
        resp = resp.json()

        recipes = []
        for recipe in self.get_data_from_resp(resp, meal_types=meal_types):
            recipes.append(recipe)

        return recipes

    def get_partial_match_recipes(self, ingrs:list, meal_types:list=None) -> list:
        """ Returns list of recipes - makes requests for all ingredients separately """
        recipes = []
        for ingr in ingrs:  # loop through ingredients
            url = self.get_url([ingr])
            resp = self.get_resp_from_req(url)
            resp = resp.json()

            for recipe in self.get_data_from_resp(resp, meal_types=meal_types):
                if recipe not in recipes:
                    recipes.append(recipe)

        return recipes

    # def common_category(self, list_1:list=None, list_2:list=None):
    #     """ Checks if two lists have at least one common element """
    #     if (set(list_1) & set(list_2)):
    #         return True
    #     else:
    #         return False

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", web_url:str=None) -> str:
        """ Returns url ready to be send """
        if web_url is None:
            web_url = self.WEB_URL
        url = web_url

        url = self.add_params_to_url(ingrs, url, param_name="")
        return url

    def prep_args(self, ingrs:list, meal_types:list=None):
        """ Modifies args from users form to url """
        # translates ingredients from polish to english
        ingrs = self.pl_en_translate(ingrs)
        if meal_types:
            # if meal_types are given, translates general forms to this specific website
            meal_types = [self.meal_transl(m_type) for m_type in meal_types if self.meal_transl(m_type) is not None]
        return ingrs, meal_types

    def meal_transl(self, meal_type:str=None) -> list:
        trans = {
            MealType.BREAKFAST: "breakfast",
            MealType.DINNER: "mains",
            MealType.DESSERT: "desserts",
            MealType.SNACKS: "snack",
            MealType.DRINK: "drinks",
            MealType.SAUCE: "dips",
            MealType.SOUP: None,
            MealType.LUNCH: None,
            MealType.TO_BREAD: None,
        }
        return trans[meal_type]

class JadlonomiaScraper(BaseScraper):
    NAME = "Jadłonomia"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://www.jadlonomia.com/przepisy/?ajax=1"

    def __init__(self):
        super().__init__()

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full") -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        # translates meal_types to website friendly version (e.x. `sniadanie` to `sniadania`)
        if meal_types:
            meal_types = [self.get_meal_types_trans(m_type) for m_type in meal_types]

        url = self.get_url(ingrs, meal_types, ingrs_match)  # constructs url
        resp = self.get_resp_from_req(url).text  # gets html

        recipes = []  # add scrapped recipes to list
        for recipe in self.get_data_from_resp(resp):
            recipes.append(recipe)

        data = self.data_to_dict(recipes)  # add info to dict
        data = self.get_cleaned_data(data)  # clean data
        return data

    def get_url(self, ingrs:list, meal_type:list=None, ingrs_match:str="full", web_url:str=None) -> str:
        """ Returns url ready to be send """

        if web_url is None:
            web_url = self.WEB_URL
        url = web_url

        url = self.add_params_to_url(params=ingrs, url=url, param_name="&skladnik=", connector=self.conn(ingrs_match))
        url = self.add_params_to_url(params=meal_type, url=url, param_name="&rodzaj_dania=", connector=self.conn("partial"))
        return url

    def conn(self, match):
        """ Based on `match` returns proper connector to connect the values in the url """
        if match == "full":
            return "+"  # means "and"
        return ","  # means "or"

    def get_data_from_resp(self, web_resp:str=None, ingrs:list=None, meal_types:list=None):
        """ Filters response and returns only useful information about recipes - title and link """
        soup = BeautifulSoup(web_resp, self.HTML_PARSER)
        recipe_grid = soup.find(class_="clear row")
        articles = recipe_grid.find_all(class_="text absolute")

        for article in articles:
            link = article.h2.a["href"]
            title = article.h2.a.text

            yield self.recipe_data_to_dict(title, link)

    def get_meal_types_trans(self, meal_type:str) -> str:
        trans = {
            MealType.BREAKFAST: "sniadania",
            MealType.SOUP: "zupy",
            MealType.DINNER: "dania-glowne",
            MealType.LUNCH: "lunche-do-pracy",
            MealType.TO_BREAD: "do-chleba",
            MealType.DESSERT: "ciasta-i-desery",
            MealType.DRINK: "napoje",
            MealType.SAUCE: "sosy-i-dodatki"
            }
        return trans[meal_type]

class WegepediaScraper(WordPressScraper):
    """ Searches posts using 'search' arg and filters meal_types using 'tags' arg """
    NAME = "Wegepedia"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://wegepedia.pl/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&tags="

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.BREAKFAST: [41, 43],  # 'placki', 'do-kanapek'
            MealType.SOUP: [31],  # 'zupy'
            MealType.DINNER: [32, 59, 61],  # 'dania-glowne', 'kotlety-pulpety', 'makarony'
            MealType.LUNCH: [39],  # 'do-pracy'
            MealType.TO_BREAD: [43],  # 'do-kanapek'
            MealType.DESSERT: [44, 45, 33],  # 'ciasta', 'ciastka', 'desery'
            MealType.SNACKS: [55],  # 'przekaski'
            MealType.DRINK: [28],  # 'napoje'
            MealType.SAUCE: [35],  # 'sosy-i-dipy'
        }
        return trans[meal_type]

class HealthyOmnomnomScraper(WordPressScraper):
    """ Searches recipes using 'search' arg and filters meal_types using 'recipes-categories' arg """
    NAME = "Healthy Omnomnom"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://healthyomnomnom.pl/wp-json/wp/v2/recipe?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&recipes-categories="

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DINNER: [99],  # 'obiady-i-kolacje'
            MealType.LUNCH: [98],  # 'lunche'
            MealType.DESSERT: [100],  # 'przekaski-i-desery'
            MealType.BREAKFAST: [97],  # 'sniadania'
            MealType.SNACKS: [100],  # 'przekaski-i-desery'
            MealType.TO_BREAD: None,
            MealType.SOUP: None,
            MealType.DRINK: None,
            MealType.SAUCE: None,
        }
        return trans[meal_type]

class VegeneratBiegowyScraper(WordPressScraper):
    """ Searches posts using 'search' arg and filters meal_types using 'categories' arg """
    NAME = "Vegenerat-biegowy"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://vegenerat-biegowy.pl/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DINNER: [3],  # 'danie-glowne'
            MealType.DRINK: [10],  # 'koktajle'
            MealType.TO_BREAD: [8],  # 'kolacja'
            MealType.DESSERT: [6],  # 'slodkosci'
            MealType.SNACKS: [4],  # 'przekąska'
            MealType.BREAKFAST: [7],  # 'sniadanie'
            MealType.SOUP: [5],  # 'zupa'
            MealType.LUNCH: [8],  # 'kolacja'
            MealType.SAUCE: None,
        }
        return trans[meal_type]

class ErVeganScraper(WordPressScraper):
    """ Searches posts using 'search' arg and filters meal_types using 'categories' arg """
    NAME = "erVegan"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://ervegan.com/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.BREAKFAST: [487, 489, 163],  # 'sniadania_na_slodko', 'sniadania_na_slono', 'snd'
            MealType.DINNER: [107],  # 'dania-glowne'
            MealType.DRINK: [122],  # 'napoje'
            MealType.DESSERT: [102, 97],  # 'sweet', 'slodkie'
            MealType.SNACKS: [15],  # 'przekaski'
            MealType.SOUP: [136],  # 'zupy'
            MealType.LUNCH: [340],  # 'erbox'
            MealType.TO_BREAD: None,
            MealType.SAUCE: None,
        }
        return trans[meal_type]

class HealthyLivingJamesScraper(WordPressScraper):
    """ Searches posts using 'search' arg, filters meal_types using 'categories' arg and excludes non-vegan category """
    NAME = "Healthy Living James"
    DIET = CuisineType.REGULAR

    EXCLUDE_CATEGORY_ID = 1392
    VEGAN_CATEGORY_ID = 1393
    WEB_URL = f"https://healthylivingjames.co.uk/wp-json/wp/v2/posts?per_page=100&categories_exclude={EXCLUDE_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def finally_change_data_to_url(self, ingrs:list, meal_types:list):
        """ Translates ingredients from polish to english """
        ingrs = self.pl_en_translate(ingrs)
        return ingrs, meal_types

    def condition_excluding_recipe(self, recipe:str) -> bool:
        """ Checks if recipe should be excluded """
        if self.VEGAN_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DINNER: [6, 1322, 1396, 1321, 1319],  # 'dinner', 'pasta', 'salads', '15-minute-dinners', 'autumn-dinner-recipes'
            MealType.BREAKFAST: [1],  # 'breakfast'
            MealType.DESSERT: [1401, 7],  # 'chocolate', 'dessert'
            MealType.SAUCE: [11],  # 'dips-sauces'
            MealType.DRINK: [9],  # 'drinks'
            MealType.LUNCH: [5, 1396],  # 'lunch', 'salads'
            MealType.SNACKS: [13],  # 'snacks'
            MealType.SOUP: None,
            MealType.TO_BREAD: None,
        }
        return trans[meal_type]

class AgaMaSmakaScraper(WordPressScraper):
    """ Searches posts using 'search' arg and filters meal_types using 'categories' arg """
    NAME = "Aga ma Smaka"
    DIET = CuisineType.VEGETARIAN

    WEB_URL = "https://agamasmaka.pl/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DRINK: [13],  # 'do-picia'
            MealType.DINNER: [38, 30, 35],  # 'drugie-dania', 'obiady', 'salatki-surowki'
            MealType.LUNCH: [32],  # 'na-wynos-na-wycieczke'
            MealType.SNACKS: [34],  # 'przekaski-przystawki'
            MealType.TO_BREAD: [35],  # 'salatki-surowki'
            MealType.BREAKFAST: [29],  # 'sniadania'
            MealType.DESSERT: [16],  # 'zdrowe-slodkosci'
            MealType.SOUP: [37],  # 'zupy'
            MealType.SAUCE: None,
        }
        return trans[meal_type]

class VegeMiScraper(WordPressScraper):
    """
    Searches posts using 'search' arg.
    Website doesn't have division into meal types categories
    so get_recipes function with meal_types argument will always returns data as if 0 recipes were found
    """
    NAME = "VegeMi"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://www.vegemi.pl/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str="full") -> bool:
        """ Reject entire seek if there's `meal_types` given """
        if meal_types is not None:
            return True
        return False

class OhMyVeggiesScraper(WordPressScraper):
    """ Searches posts using ingredients' tags (firstly gets them by making request(s))
    and meal_types using 'categories' arg """
    NAME = "Oh My Veggies"
    DIET = CuisineType.VEGETARIAN

    TAG_URL = "https://ohmyveggies.com/wp-json/wp/v2/tags?slug="  # url to get ingredient's tag
    WEB_URL = "https://ohmyveggies.com/wp-json/wp/v2/posts?per_page=100"  # url to get recipes

    def __init__(self):
        super().__init__()

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full") -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        ingrs_copy = ingrs.copy()  # to check if every ingredient has its tag

        meal_types_ = self.get_meal_types_translated(meal_types)
        ingrs_, meal_types_ = self.finally_change_data_to_url(ingrs, meal_types_)

        # if user wants full ingredients' match but not all of them have the tags
        if ingrs_match == "full" and len(ingrs_copy) != len(ingrs_):
            return self.data_to_dict([])

        recipes = self.get_recipes_from_params(ingrs_, meal_types_, ingrs_match)

        data = self.data_to_dict(recipes)
        return data

    def get_recipes_from_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str="full"):
        """ Makes request, filters data and returns list of recipes """
        url = self.get_url(ingrs, meal_types)
        resp = self.get_resp_from_req(url)
        resp = resp.json()

        recipes = []

        ingrs = [int(ingr) for ingr in ingrs]  # `ingrs` is a list of ints - ingredients' tags
        for recipe in resp:  # loop through items in website's response
            valid_recipe = self.get_recipe_from_resp(recipe, ingrs, meal_types, ingrs_match=ingrs_match, check_in_soup=False)

            # if recipe is excluded for some reason, `get_recipe_from_resp` returns None and it needs to be omitted
            if valid_recipe:
                recipes.append(valid_recipe)

        return recipes

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str="full") -> bool:
        """ Checks if current recipe should be excluded - it should if `ingrs_match` is 'full',
        but recipe do not have all wanted ingredients in its ingredients. """
        if ingrs_match == "full":
            if not do_list_includes_list(recipe["tags"], ingrs):
                return True
            return False
        elif ingrs_match == "partial":
            return False
        else:
            raise Exception(f"`ingrs_match` must be 'full' or 'partial', not {ingrs_match}")

    def finally_change_data_to_url(self, ingrs:list, meal_types:list) -> (list, list):
        """ The last change of params before putting them into url """
        ingrs_ = self.pl_en_translate(ingrs)
        ingrs_tags = self.get_ingrs_tags(ingrs_, self.TAG_URL)
        return ingrs_tags, meal_types

    def get_ingrs_tags(self, ingrs:list, url:str):
        """ Gets list of strings and url and returns list of their tags """
        url = self.add_params_to_url(params=ingrs, url=url, connector="+", word_conn="-")
        resp = self.get_resp_from_req(url)
        resp = resp.json()
        tags = [(tag["id"]) for tag in resp]
        return tags

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DESSERT: [8084, 8533],  # 'vegan-desserts', 'vegan-pies-and-pastries'
            MealType.DRINK: [8085],  # `vegan-drinks`
            MealType.DINNER: [8099, 9309, 8370],  # 'vegan-salads', 'vegan-pasta-recipes', 'vegan-dinner-recipes'
            MealType.LUNCH: [8099, 8376, 8093],  # 'vegan-salads', 'vegan-lunch-recipes', 'vegan-sandwiches-wraps'
            MealType.SAUCE: [8087],  # 'vegan-sauces-condiments'
            MealType.SNACKS: [8089],  # 'vegan-snacks'
            MealType.BREAKFAST: [8083, 8093],  # 'vegan-breakfast-recipes', 'vegan-sandwiches-wraps'
            MealType.SOUP: [8091],  # 'vegan-soups'
            MealType.TO_BREAD: None,
        }
        return trans[meal_type]

class UpieczonaScraper(WordPressScraper):
    """ Searches posts using 'search' arg and filters meal_types using 'categories' arg.
    The website has only desserts recipes so another MealTypes and excluded """
    NAME = "Upieczona"
    DIET = CuisineType.VEGETARIAN

    VEGAN_CATEGORY_ID = 54
    WEB_URL = f"http://upieczona.pl/wp-json/wp/v2/posts?per_page=100&categories={VEGAN_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str="full") -> bool:
        """ Checks if the request should be made - if `meal_types` is given but doesn't contain MealType.DESSERT,
        request shouldn't be made """
        if meal_types is None:
            return False
        elif MealType.DESSERT not in meal_types:
            return True
        return False

    def get_meal_types_translated(self, meal_types:list) -> list:
        """ Returns 'None' because contrarily to the most WordPress websites in the project
        this one doesn't have division on meal types """
        return None

class LittleHungryLadyScraper(WordPressScraper):
    """ Searches posts using 'search' arg, filters meal_types using 'tags' arg and
    excludes the post if it is not a vegan recipe """
    NAME = "Little Hungry Lady"
    DIET = CuisineType.REGULAR

    RECIPE_CATEGORY_ID = 911
    VEGAN_CATEGORY_ID = 1150
    WEB_URL = f"https://www.littlehungrylady.pl/wp-json/wp/v2/posts?per_page=100&categories={VEGAN_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&tag="

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str="full") -> bool:
        """ Excludes the post if there's no 'recipe' category """
        if self.RECIPE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.BREAKFAST: [1079],  # 'sniadanie'
            MealType.LUNCH: [1118, 1228],  # 'kolacja', 'salatka'
            MealType.DESSERT: [1101, 1239],  # 'deser', 'ciastka'
            MealType.DINNER: [1128],  # 'obiad'
            MealType.DRINK: [1175],  # 'napoj'
            MealType.SOUP: [1139],  # 'zupa'
            MealType.TO_BREAD: None,
            MealType.SNACKS: None,
            MealType.SAUCE: None,
        }
        return trans[meal_type]

class AlaantkoweblwScraper(WordPressScraper):
    """ Searches posts using 'search' arg, filters meal_types using 'categories' arg and excludes non-vegan category """
    NAME = "alaantkoweBLW"
    DIET = CuisineType.REGULAR

    # categories to be excluded
    EXCLUDE_CATEGORIES_IDS = [5, 9, 51]  # 'mieso', 'jajka', 'ryba'
    # categories 'without ...' - check if they are in categories
    VEGAN_CATEGORIES_IDS = [33, 130, 32]  # 'bez-jajka', 'bez-miesa', 'bez-nabialu'
    # category showing that post is a recipe
    RECIPE_CAT_ID = 133  # 'przepisy-blw'
    WEB_URL = f"https://alaantkoweblw.pl/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
              f"{'+'.join([str(category_id) for category_id in EXCLUDE_CATEGORIES_IDS])}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str="full") -> bool:
        if self.RECIPE_CAT_ID not in recipe["categories"]:
            return True
        if not do_list_includes_list(recipe["categories"], self.VEGAN_CATEGORIES_IDS):
            return True
        return False

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DESSERT: [48, 7, 8, 232, 166, 139],  # 'babeczki-i-muffinki', 'ciasta-i-ciastka', 'inne-slodkosci', 'lody', 'tort', 'zdrowe-slodycze'
            MealType.DRINK: [67, 42],  # 'co-do-picia', 'do-picia'
            MealType.DINNER: [45, 38, 4, 49, 46],  # 'dania-z-makaronem', 'kolacja', 'obiad', 'pierogi-i-kluski', 'zapiekanki'
            MealType.SNACKS: [147, 31],  # 'gofry', 'podwieczorek'
            MealType.TO_BREAD: [48, 39],  # 'kolacja', 'na-chleb'
            MealType.LUNCH: [16],  # 'na-wynos'
            MealType.BREAKFAST: [52, 47, 14],  # 'nalesniki', 'placki', 'sniadanie'
            MealType.SOUP: [22],  # 'zupy'
            MealType.SAUCE: None,
        }
        return trans[meal_type]
