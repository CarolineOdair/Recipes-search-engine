from src.base.base_scrapers.base_wp_scraper import WordPressScraper
from src.base.utils import CuisineType, MealType, IngrMatch  # classes
from src.base.utils import do_list_includes_list, list_el_merged_with_plus  # functions


class VegeneratBiegowyScraper(WordPressScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'vegenerat-biegowy.pl'.
    """
    NAME = "Vegenerat-biegowy"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://vegenerat-biegowy.pl"

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class AgaMaSmakaScraper(WordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'agamasmaka.pl'.
    """
    NAME = "Aga ma Smaka"
    DIET = CuisineType.VEGETARIAN
    WEB_URL = "https://agamasmaka.pl"

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class UpieczonaScraper(WordPressScraper):
    """
    Searches for vegan recipes with given ingredients on 'upieczona.pl'.
    """
    NAME = "Upieczona"
    DIET = CuisineType.VEGETARIAN
    WEB_URL = "http://www.upieczona.pl"

    VEGAN_CATEGORY_ID = 54
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories={VEGAN_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> bool:
        """ Checks if the request should be made - if `meal_types` is given but doesn't contain MealType.DESSERT,
        request shouldn't be made """
        if meal_types is None:
            return False
        elif MealType.DESSERT not in meal_types:
            return True
        return False

    def get_meal_types_translated(self, meal_types:list, *args, **kwargs) -> None:
        """ Returns 'None' because contrarily to the most WordPress websites in the project
        this one doesn't have division on meal types """
        return None

class LittleHungryLadyScraper(WordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'littlehungrylady.pl'.
    """
    NAME = "Little Hungry Lady"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://littlehungrylady.pl"

    RECIPE_CATEGORY_ID = 911
    VEGAN_CATEGORY_ID = 1150
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories={VEGAN_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

        self.meal_type_param = "&tag="

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> bool:
        """ Excludes the post if there's no 'recipe' category """
        if self.RECIPE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class AlaantkoweblwScraper(WordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'alaantkoweblw.pl'.
    """
    NAME = "alaantkoweBLW"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://alaantkoweblw.pl"

    # categories to be excluded
    EXCLUDE_CATEGORIES_IDS = [5, 9, 51]  # 'mieso', 'jajka', 'ryba'
    # categories 'without ...' - check if they are in recipe's categories
    VEGAN_CATEGORIES_IDS = [33, 130, 32]  # 'bez-jajka', 'bez-miesa', 'bez-nabialu'
    # category showing that post is a recipe
    RECIPE_CAT_ID = 133  # 'przepisy-blw'
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
              f"{list_el_merged_with_plus(EXCLUDE_CATEGORIES_IDS)}"

    def __init__(self):
        super().__init__()

    def exclude_one_recipe(self, recipe:str, ingrs=None, meal_types=None, ingrs_match:str=IngrMatch.FULL, *args, **kwargs) -> bool:
        """ Excludes the post if there's no 'recipe' and 'vegan' category """
        if self.RECIPE_CAT_ID not in recipe["categories"]:
            return True
        if not do_list_includes_list(recipe["categories"], self.VEGAN_CATEGORIES_IDS):
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)
