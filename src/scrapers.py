from bs4 import BeautifulSoup
import requests

from base_scrapers import BaseScraper, WordPressScraper, TagsSearchingWordPressScraper
from utils import do_lists_have_common_element, do_list_includes_list, list_el_merged_with_plus
from utils import CuisineType, MealType


class MadeleineOliviaScraper(BaseScraper):
    NAME = "Madeleine Olivia"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://www.madeleineolivia.co.uk/api/search/GeneralSearch?q="
    RECIPE_URL = "https://www.madeleineolivia.co.uk/blog/"

    def __init__(self):
        super().__init__()

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """

        ingrs, meal_types = self.prep_args(ingrs, meal_types)

        # gets recipes differently depending on ingredients match
        if ingrs_match == "full":
            recipes = self.get_full_match_recipes(ingrs, meal_types)
        elif ingrs_match == "partial":
            recipes = self.get_partial_match_recipes(ingrs, meal_types)
        else:
            raise Exception(f"`ingrs_match` must be `full` or `partial`, not {ingrs_match}")

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # clean data
        return data

    def get_data_from_resp(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs):
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

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", web_url:str=None, *args, **kwargs) -> str:
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
    # JadlonomiaScraper was the first one I was doing and after some time I've realised that
    # Jadlonomia.com also uses wp-json, so it would be much better if the scraper have inherited from WordPressScraper
    NAME = "Jadłonomia"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://www.jadlonomia.com/przepisy/?ajax=1"

    def __init__(self):
        super().__init__()

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """
        # translates meal_types to website friendly version (e.x. `sniadanie` to `sniadania`)
        if meal_types:
            meal_types = [self.get_meal_types_trans(m_type) for m_type in meal_types]

        url = self.get_url(ingrs, meal_types, ingrs_match)  # constructs url
        resp = self.get_resp_from_req(url).text  # gets html

        recipes = []  # add scrapped recipes to list
        for recipe in self.get_data_from_resp(resp):
            recipes.append(recipe)

        data = self.data_to_dict(recipes)  # add data to dict
        data = self.clean_data(data)  # clean data
        return data

    def get_url(self, ingrs:list, meal_type:list=None, ingrs_match:str="full", web_url:str=None, *args, **kwargs) -> str:
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

    def get_data_from_resp(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs):
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

    def finally_change_data_to_url(self, ingrs:list, meal_types:list, *args, **kwargs):
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

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> bool:
        """ Reject entire seek if there's `meal_types` given """
        if meal_types is not None:
            return True
        return False

class OhMyVeggiesScraper(TagsSearchingWordPressScraper):
    """ Searches posts using ingredients' tags and meal_types using 'categories' arg """
    NAME = "Oh My Veggies"
    DIET = CuisineType.VEGETARIAN

    TAG_URL = "https://ohmyveggies.com/wp-json/wp/v2/tags?slug="  # url to get ingredient's tag

    WEB_URL = "https://ohmyveggies.com/wp-json/wp/v2/posts?per_page=100"  # url to get recipes

    def __init__(self):
        super().__init__()

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

    def prep_data_to_get_tags(self, ingrs:list=None, meal_types:list=None, *args, **kwargs):
        """ The last change of params before putting them into url. Returns (ingrs, meal_types)"""
        ingrs_ = self.pl_en_translate(ingrs)
        return ingrs_, meal_types

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
    WEB_URL = f"https://upieczona.pl/wp-json/wp/v2/posts?per_page=100&categories={VEGAN_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> bool:
        """ Checks if the request should be made - if `meal_types` is given but doesn't contain MealType.DESSERT,
        request shouldn't be made """
        if meal_types is None:
            return False
        elif MealType.DESSERT not in meal_types:
            return True
        return False

    def get_meal_types_translated(self, meal_types:list, *args, **kwargs) -> list:
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

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str="full", *args, **kwargs) -> bool:
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
    # categories 'without ...' - check if they are in recipe's categories
    VEGAN_CATEGORIES_IDS = [33, 130, 32]  # 'bez-jajka', 'bez-miesa', 'bez-nabialu'
    # category showing that post is a recipe
    RECIPE_CAT_ID = 133  # 'przepisy-blw'
    WEB_URL = f"https://alaantkoweblw.pl/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
              f"{list_el_merged_with_plus(EXCLUDE_CATEGORIES_IDS)}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&search="
        self.meal_type_param = "&categories="

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str="full", *args, **kwargs) -> bool:
        """ Excludes the post if there's no 'recipe' and 'vegan' category """
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

class FlyMeToTheSpoonScraper(TagsSearchingWordPressScraper):
    """ Searches posts using ingredients' tags and meal_types using 'categories' arg """
    NAME = "Fly me to the spoon"
    DIET = CuisineType.REGULAR

    TAG_URL = "https://flymetothespoon.com/wp-json/wp/v2/tags?slug="

    # categories to be excluded
    EXCLUDE_CATEGORY_ID = 703  # 'mieso'
    # category showing that post is a recipe
    RECIPE_CATEGORY_ID = 259  # 'przepisy'
    # category showing that post is perceived as vegan
    VEGAN_CATEGORY_ID = 651  # 'weganskie'
    WEB_URL = f"https://flymetothespoon.com/wp-json/wp/v2/posts?per_page=100&categories_exclude={EXCLUDE_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs):
        """ Excludes the post if there's no 'recipe' and 'vegan' category """
        must_include_categories = [self.RECIPE_CATEGORY_ID, self.VEGAN_CATEGORY_ID]
        if not do_list_includes_list(recipe["categories"], must_include_categories):
            return True
        return False

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.SOUP: [711],  # 'zupy'
            MealType.BREAKFAST: [673, 1177],  # 'sniadania', 'placuszki-na-slodko'
            MealType.DINNER: [659, 804],  # 'dania-glowne', 'makarony'
            MealType.DESSERT: [663, 263],  # 'desery', 'na-slodko'
            MealType.DRINK: [1165],  # 'napoje'
            MealType.LUNCH: [661],  # 'salatki-i-przekaski'
            MealType.SNACKS: [661],  # 'salatki-i-przekaski'
            MealType.TO_BREAD: None,
        }
        return trans[meal_type]

class ZielonySrodekScraper(TagsSearchingWordPressScraper):
    """ Searches posts using ingredients' tags and meal_types using 'categories' arg """
    NAME = "zielony środek"
    DIET = CuisineType.REGULAR

    TAG_URL = "https://zielonysrodek.pl/wp-json/wp/v2/tags?slug="

    # category showing that post is a recipe
    RECIPE_CATEGORY_ID = 4  # 'przepis'
    # category showing that post is perceived as vegan
    VEGAN_CATEGORY_ID = 85  # 'weganskie'
    WEB_URL = f"https://zielonysrodek.pl/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs):
        """ Excludes the post if there's no 'recipe' and 'vegan' category """
        must_include_categories = [self.RECIPE_CATEGORY_ID, self.VEGAN_CATEGORY_ID]
        if not do_list_includes_list(recipe["categories"], must_include_categories):
            return True
        return False

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DESSERT: [199, 106],  # 'ciastka', 'slodycze'
            MealType.DRINK: [105],  # 'napoje'
            MealType.LUNCH: [174, 53],  # 'placki-i-kotleciki', 'salatki'
            MealType.DINNER: [23, 53],  # 'dania-glowne', 'salatki'
            MealType.SNACKS: [36],  # 'przekaski'
            MealType.BREAKFAST: [14],  # 'sniadania'
            MealType.SOUP: [31],  # 'zupy'
            MealType.TO_BREAD: None,
        }
        return trans[meal_type]

class OlgaSmileScraper(TagsSearchingWordPressScraper):
    """ Searches posts using ingredients' tags and meal_types using 'categories' arg """
    NAME = "Olga Smile"
    DIET = CuisineType.REGULAR

    TAG_URL = "https://olgasmile.com/wp-json/wp/v2/tags?slug="

    # categories to be excluded
    EXCLUDED_CATEGORIES_ID = [28, 4382]  # 'mieso-wedliny-ryby-owoce-morza', 'jajka'
    VEGAN_RECIPE_CATEGORY_ID = 156  # 'dieta-weganska'
    WEB_URL = f"https://olgasmile.com/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
              f"{list_el_merged_with_plus(EXCLUDED_CATEGORIES_ID)}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs):
        """ Excludes the post if there's no 'vegan' category """
        if self.VEGAN_RECIPE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DESSERT: [142, 26, 16, 17],  # 'desery', 'slodkie-desery', 'ciasta-chleby-desery', 'ciasteczka'
            MealType.DRINK: [18],  # 'napoje-drinki-koktajle'
            MealType.LUNCH: [139, 44],  # 'lunch', 'tarty-quiche-fritata'
            MealType.DINNER: [5, 140, 23],  # 'co-na-obiad', 'obiad', 'makaron-w-wielu-odslonach'
            MealType.SNACKS: [36, 93, 92],  # 'przekaski', 'cieple-przekaski-przystawki', 'zimne-przekaski-przystawki'
            MealType.BREAKFAST: [138, 14743, 6769, 14793],  # 'sniadania', 'placki', 'platki-owsiane', 'nalesniki'
            MealType.SOUP: [30],  # 'zupy'
            MealType.TO_BREAD: [48],  # 'pasty-do-chleba'
        }
        return trans[meal_type]

class BeFitBeStrongScraper(TagsSearchingWordPressScraper):
    """ Searches posts using ingredients' tags and meal_types using 'categories' arg """
    NAME = "Be Fit Be Strong"
    DIET = CuisineType.REGULAR

    TAG_URL = "https://befitbestrong.pl/wp-json/wp/v2/tags?slug="

    # categories to be excluded
    EXCLUDED_CATEGORIES_ID = [49, 447]  # 'mieso-i-ryby', owoce-morza
    VEGAN_RECIPE_CATEGORY_ID = 2  # 'weganskie'
    WEB_URL = f"https://befitbestrong.pl/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
              f"{list_el_merged_with_plus(EXCLUDED_CATEGORIES_ID)}"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&tags="
        self.meal_type_param = "&categories="

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None, ingrs_match:str="full", *args, **kwargs):
        """ Excludes the post if there's no 'vegan' category """
        if self.VEGAN_RECIPE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None):
        trans = {
            MealType.DESSERT: [33, 6, 528, 14, 51, 105, 83],  # 'ciasta', 'ciasteczka', 'deserki', 'desery', 'lody', 'muffinki-i-babeczki', 'tarty-na-slodko'
            MealType.DINNER: [427, 142, 82, 536, 22, 90, 56, 443, 529],  # 'domowy-fast-food', 'kluskipierogikopytka',
            # 'makarony', 'nalesniki-na-slono', 'obiady', 'salatki-i-surowki', 'sosydipypesto', 'szybki-obiad', 'szybki-obiad-obiady'
            MealType.LUNCH: [44, 90, 148],  # 'lunchbox', 'salatki-i-surowki', 'tarty-na-slono'
            MealType.DRINK: [75],  # 'napoje'
            MealType.TO_BREAD: [39],  # 'pasty-na-kanapke'
            MealType.BREAKFAST: [41, 525, 532, 42],  # 'placki-i-nalesniki', 'placki-na-slodko', 'placki-na-slono', 'sniadanie'
            MealType.SNACKS: [528, 10, 90, 148],  # 'deserki', 'przekaska', 'salatki-i-surowki', 'tarty-na-slono'
            MealType.SOUP: [24],  # 'zupy'
        }
        return trans[meal_type]

class WeganonScraper(BaseScraper):
    NAME = "Weganon"
    DIET = CuisineType.VEGAN

    WEB_URL = "https://weganon.pl/page/{}/?post_type=post"

    def __init__(self):
        super().__init__()

    def get_recipes(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", *args, **kwargs) -> dict:
        """ Main function, returns recipes which fulfill the conditions """

        if meal_types:
            meal_types = self.get_meal_types_translated(meal_types)

        if ingrs_match == "full":
            recipes = self.get_full_match_recipes(ingrs, meal_types=meal_types)
        elif ingrs_match == "partial":
            recipes = self.get_partial_match_recipes(ingrs, meal_types=meal_types)
        else:
            raise Exception(f"`ingrs_match` must be 'full' or 'partial', not {ingrs_match}")

        data = self.data_to_dict(recipes)
        data = self.clean_data(data)

        return data

    def get_full_match_recipes(self, ingrs:list, meal_types:list=None, *args, **kwargs) -> list:
        """ Return list of recipes which ingredients match fully """
        recipes = []
        for recipe in self.get_match_recipes(ingrs, meal_types):
            if recipe not in recipes:
                recipes.append(recipe)
        return recipes

    def get_partial_match_recipes(self, ingrs:list, meal_types:list=None, *arg, **kwargs):
        """ Return list of recipes which ingredients match partially """
        recipes = []

        for ingr in ingrs:
            for recipe in self.get_match_recipes([ingr], meal_types=meal_types):
                if recipe not in recipes:
                    recipes.append(recipe)

        return recipes

    def get_match_recipes(self, ingrs:list, meal_types:list=None, *arg, **kwargs):
        """ Creates and makes requests and yields recipes which are returns in the requests """
        for url in self.get_url(ingrs, meal_types):
            resp = self.get_resp_from_req(url)
            # loops through next pages: 1st, 2nd, 3rd ect. and stops when ther's no such page (status_code 404 occurs) -
            if resp.status_code == 404:
                break

            for recipe in self.get_data_from_resp(resp.text):
                yield recipe

    def get_data_from_resp(self, web_resp:str=None, ingrs:list=None, meal_types:list=None, *args, **kwargs):
        """ Gets web's response and returns dictionary with recipes' title and link """
        soup = BeautifulSoup(web_resp, self.HTML_PARSER)
        container = soup.find(class_="row")

        recipes_container = container.find_all(class_="fix-special")
        for recipe in recipes_container:
            recipe_info_container = recipe.find(class_="item-title").a
            link = recipe_info_container["href"]
            title = recipe_info_container["title"]

            yield self.recipe_data_to_dict(title=title, link=link)

    def get_resp_from_req(self, url:str, *args, **kwargs) -> str:
        """ Returns websites response (requests.models.Response object) or raise an exception if request failed """
        resp = requests.get(url, headers=self.HEADERS)
        if resp.ok or resp.status_code == 404:
            return resp
        else:
            raise Exception(f"Request failed, code: {resp.status_code}, url {resp.url}")

    def get_url(self, ingrs:list, meal_types:list=None, ingrs_match:str="full", web_url:str=None, *args, **kwargs) -> str:
        """ Return url ready to be sent """
        url = self.WEB_URL
        url = self.add_params_to_url(ingrs, url, param_name="&s=")
        url = self.add_params_to_url(meal_types, url, param_name="&category_name=")

        n_page = 1
        while True:
            yield url.format(n_page)
            n_page += 1

    def meal_type_trans(self, meal_type:str=None) -> list:
        trans = {
            MealType.DESSERT: ["na-slodko"],
            MealType.DINNER: ["dania-obiadowe"],
            MealType.LUNCH:["salatki"],
            MealType.TO_BREAD: ["pasty-do-pieczywa"],
            MealType.SOUP: ["zupy-i-kremy"],
            MealType.BREAKFAST: ["sniadania"],
            MealType.SNACKS: None,
            MealType.DRINK: None,
        }
        if meal_type in trans.keys():
            return trans[meal_type]
        return None
