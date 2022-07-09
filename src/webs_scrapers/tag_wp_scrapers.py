from src.base.base_scrapers import TagsSearchingWordPressScraper
from src.base import CuisineType, MealType, IngrMatch  # classes
from src.base import do_list_includes_list, list_el_merged_with_plus  # methods


class OhMyVeggiesScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'ohmyveggies.com'.
    """
    NAME = "Oh My Veggies"
    DIET = CuisineType.VEGETARIAN
    WEB_URL = "https://ohmyveggies.com"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def prep_data_to_get_tags(self, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> (list, list):
        """ The last change of params before putting them into url. Returns (ingrs, meal_types)"""
        ingrs_ = self.pl_en_translate(ingrs)
        return ingrs_, meal_types

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class FlyMeToTheSpoonScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'flymetothespoon.com'.
    """
    NAME = "Fly me to the spoon"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://flymetothespoon.com"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    # categories to be excluded
    EXCLUDE_CATEGORY_ID = 703  # 'mieso'
    # category showing that post is a recipe
    RECIPE_CATEGORY_ID = 259  # 'przepisy'
    # category showing that post is perceived as vegan
    VEGAN_CATEGORY_ID = 651  # 'weganskie'
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories_exclude={EXCLUDE_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Excludes the post if there's no 'recipe' and 'vegan' category """
        must_include_categories = [self.RECIPE_CATEGORY_ID, self.VEGAN_CATEGORY_ID]
        if not do_list_includes_list(recipe["categories"], must_include_categories):
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class ZielonySrodekScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'zielonysrodek.pl'.
    """
    NAME = "zielony środek"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://zielonysrodek.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    # category showing that post is a recipe
    RECIPE_CATEGORY_ID = 4  # 'przepis'
    # category showing that post is perceived as vegan
    VEGAN_CATEGORY_ID = 85  # 'weganskie'
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Excludes the post if there's no 'recipe' and 'vegan' category """

        must_include_categories = [self.RECIPE_CATEGORY_ID, self.VEGAN_CATEGORY_ID]
        if not do_list_includes_list(recipe["categories"], must_include_categories):
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class OlgaSmileScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'olgasmile.com'.
    """
    NAME = "Olga Smile"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://olgasmile.com"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    EXCLUDED_CATEGORIES_ID = [28, 4382]  # 'mieso-wedliny-ryby-owoce-morza', 'jajka'
    VEGAN_RECIPE_CATEGORY_ID = 156  # 'dieta-weganska'
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
                            f"{list_el_merged_with_plus(EXCLUDED_CATEGORIES_ID)}"

    def __init__(self):
        super().__init__()

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Excludes the post if there's no 'vegan' category """

        if self.VEGAN_RECIPE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class BeFitBeStrongScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'befitbestrong.pl'.
    """
    NAME = "Be Fit Be Strong"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://befitbestrong.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    EXCLUDED_CATEGORIES_ID = [49, 447]  # 'mieso-i-ryby', owoce-morza
    VEGAN_RECIPE_CATEGORY_ID = 2  # 'weganskie'
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
                            f"{list_el_merged_with_plus(EXCLUDED_CATEGORIES_ID)}"

    def __init__(self):
        super().__init__()

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Excludes the post if there's no 'vegan' category """

        if self.VEGAN_RECIPE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class WarzywizmScraper(TagsSearchingWordPressScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'warzywizm.pl'.
    """
    NAME = "Warzywizm"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://warzywizm.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.TO_BREAD: [259],  # 'do-chleba'
            MealType.DINNER: [367, 256],  # 'kolacja', 'obiad-lunch'
            MealType.LUNCH: [256],  # 'obiad-lunch'
            MealType.DESSERT: [264],  # 'slodkosci'
            MealType.BREAKFAST: [258],  # 'sniadanie'
            MealType.SOUP: [261],  # 'zupy'
            MealType.DRINK: None,
            MealType.SNACKS: None,
        }
        return trans.get(meal_type)

class ZenWKuchniScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'zenwkuchni.com'.
    """
    NAME = "Zen w kuchni"
    DIET = CuisineType.VEGETARIAN
    WEB_URL = "https://zenwkuchni.com"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    EXCLUDED_CATEGORY_ID = 92  # 'lifestyle'
    MUST_INCLUDE_CATEGORY_ID = 66  # 'weganskie'
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories_exclude={EXCLUDED_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Excludes the post if there's no must include category """

        if self.MUST_INCLUDE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.DESSERT: [5, 16, 9],  # 'ciasta', 'ciasteczka', 'desery', 'desery', 'lody', 'muffinki-i-babeczki', 'tarty-na-slodko'
            MealType.TO_BREAD: [10],  # 'do-chleba'
            MealType.DRINK: [136],  # 'napoje'
            MealType.DINNER: [7, 11],  # 'obiady', 'salatki'
            MealType.SNACKS: [174],  # 'przystawki'
            MealType.LUNCH: [11],  # 'salatki'
            MealType.BREAKFAST: [6],  # 'sniadania'
            MealType.SOUP: [8],  # 'zupy'
        }
        return trans.get(meal_type)

class WilkuchniaScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'wilkuchnia.pl' website.
    """
    NAME = "WILKUCHNIA"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://wilkuchnia.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    EXCLUDED_CATEGORIES_IDS = [273, 274]  # 'mieso', 'ryby'
    MUST_INCLUDE_CATEGORY_ID = 299  # 'weganskie'
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories_exclude=" \
                            f"{list_el_merged_with_plus(EXCLUDED_CATEGORIES_IDS)}"

    def __init__(self):
        super().__init__()

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Excludes the post if there's no must include category in recipe's categories """

        if self.MUST_INCLUDE_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.DESSERT: [258, 259, 260, 262],  # 'fit-slodycze', 'ciasta', 'ciasteczka', 'desery'
            MealType.TO_BREAD: [267, 282],  # 'kanapki', 'pasty'
            MealType.DRINK: [279],  # 'napoje'
            MealType.DINNER: [254],  # 'obiad'
            MealType.SNACKS: [304],  # 'przekaski'
            MealType.LUNCH: [268],  # 'salatki'
            MealType.BREAKFAST: [253],  # 'sniadanie'
            MealType.SOUP: [275],  # 'zupy'
        }
        return trans.get(meal_type)

class ErVeganScraper(TagsSearchingWordPressScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'ervegan.com'.
    """
    NAME = "erVegan"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://ervegan.com"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class WegepediaScraper(TagsSearchingWordPressScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'wegepedia.pl'.
    """
    NAME = "Wegepedia"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://wegepedia.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class HealthyOmnomnomScraper(TagsSearchingWordPressScraper):
    """
    Searches for recipes with given ingredients and for specified (or not) meal on 'healthyomnomnom.pl'.
    """
    NAME = "Healthy Omnomnom"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://healthyomnomnom.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/recipes-tags?slug="

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/recipe?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&recipes-tags="
        self.meal_type_param = "&recipes-categories="

        self.tags_name = "recipes-tags"

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class HealthyLivingJamesScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'healthylivingjames.co.uk'.
    """
    NAME = "Healthy Living James"
    DIET = CuisineType.REGULAR
    WEB_URL = "https://healthylivingjames.co.uk"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    EXCLUDE_CATEGORY_ID = 1392
    VEGAN_CATEGORY_ID = 1393
    REQUEST_URL = WEB_URL + f"/wp-json/wp/v2/posts?per_page=100&categories_exclude={EXCLUDE_CATEGORY_ID}"

    def __init__(self):
        super().__init__()

    def finally_change_data_to_url(self, ingrs:list, meal_types:list, *args, **kwargs) -> (list, list):
        """ Translates ingredients from polish to english """
        ingrs = self.pl_en_translate(ingrs)
        return ingrs, meal_types

    def condition_excluding_recipe(self, recipe:str) -> bool:
        """ Checks if recipe should be excluded """
        if self.VEGAN_CATEGORY_ID not in recipe["categories"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
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
        return trans.get(meal_type)

class VegeMiScraper(TagsSearchingWordPressScraper):
    """
    Searches for recipes with given ingredients on 'vegemi.pl'.
    """
    NAME = "VegeMi"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://vegemi.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def exclude_by_params(self, ingrs:list=None, meal_types:list=None, ingrs_match:str=IngrMatch.FULL,
                          *args, **kwargs) -> bool:
        """ Reject entire seek if there's `meal_types` given """
        if meal_types is not None:
            return True
        return False

class VeganRichaScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'veganricha.com'.
    """
    NAME = "Vegan Richa"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://www.veganricha.com"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    VEGAN_RECIPE_TAG_ID = 60  # 'weganskie' tag - shows that recipe is vegan
    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def prep_data_to_get_tags(self, ingrs:list=None, meal_types:list=None, *args, **kwargs) -> (list, list):
        """ The last change of params before putting them into url. Returns (ingrs, meal_types)"""
        ingrs_ = self.pl_en_translate(ingrs)
        return ingrs_, meal_types

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.BREAKFAST: [51, 65, 295],  # 'breakfast', 'pancake', 'savory-breakfast'
            MealType.DESSERT: [71, 209, 6, 80],  # 'cake', 'cookie', 'dessert', 'indian-sweet'
            MealType.DINNER: [9375, 15, 20],  # 'indian-curries', 'main-course', 'salad'
            MealType.SNACKS: [29, 11],  # 'indian-snacks', 'snack'
            MealType.LUNCH: [20],  # 'salad'
            MealType.TO_BREAD: [23],  # 'sandwich'
            MealType.SOUP: [44],  # 'soup'
            MealType.DRINK: None,
            MealType.SAUCE: None,
        }
        return trans.get(meal_type)

class SalaterkaScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'salaterka.pl'.
    """
    NAME = "Salaterka"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://salaterka.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/salaterka-ingredients?slug="

    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/salaterka-recipe?per_page=100"

    def __init__(self):
        super().__init__()

        self.ingr_param = "&salaterka-ingredients="
        self.meal_type_param = "&salaterka-meal-type="

        self.tags_name = "salaterka-ingredients"

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.DESSERT: [238, 190, 179, 145, 461],  # 'batony-kule-energetyczne', 'ciastka-ciasta-babeczki',
            # 'krem-budyn-kisiel-pianka', 'lody', 'tofurnik-jagielnik'
            MealType.DINNER: [339, 370, 242, 471, 224, 249, 208, 173],  # 'dania-gulaszowe', 'kotlety', 'salatki',
            # 'stir-fry-z-patelni', 'surowki', 'tofucznica-leczo', 'z-makaronem', 'z-piekarnika-grillowe',
            MealType.DRINK: [152, 305],  # 'koktajle-napoje', 'soki'
            MealType.BREAKFAST: [207, 102, 249],  # 'nalesniki', 'owsianki-gryczanki-jaglanki-2', 'tofucznica-leczo
            MealType.TO_BREAD: [345],  # 'pasty-hummusy'
            MealType.LUNCH: [425, 242],  # 'rolki', 'salatki'
            MealType.SAUCE: [172],  # 'sosy-i-dodatki'
            MealType.SOUP: [160],  # 'zupy'
            MealType.SNACKS: None,
        }
        return trans.get(meal_type)

class RozkosznyScraper(TagsSearchingWordPressScraper):
    """
    Searches for vegan recipes with given ingredients and for specified (or not) meal on 'rozkoszny.pl'.
    """
    NAME = "Vegan Richa"
    DIET = CuisineType.VEGAN
    WEB_URL = "https://www.rozkoszny.pl"

    TAG_URL = WEB_URL + "/wp-json/wp/v2/tags?slug="

    VEGAN_RECIPE_TAG_ID = 60  # 'weganskie' tag - shows that recipe is vegan
    REQUEST_URL = WEB_URL + "/wp-json/wp/v2/posts?per_page=100"

    def __init__(self):
        super().__init__()

    def web_recipe_exclusion_con(self, recipe=None, ingrs:list=None, meal_types:list=None,
                                 ingrs_match:str=IngrMatch.FULL) -> bool:
        """ Checks if recipe should be excluded """
        if self.VEGAN_RECIPE_TAG_ID not in recipe["tags"]:
            return True
        return False

    def meal_type_trans(self, meal_type:str=None) -> list or None:
        trans = {
            MealType.BREAKFAST: [1330, 70],  # 'breakfast', 'na-sniadanie'
            MealType.DESSERT: [1324, 28],  # 'desserts', 'na-deser'
            MealType.TO_BREAD: [181],  # 'do-chleba'
            MealType.LUNCH: [79, 1328],  # 'do-lunchboxa', 'lunchbox-en'
            MealType.DINNER: [1332, 41],  # 'main-course', 'na-obiad'
            MealType.SNACKS: None,
            MealType.SOUP: None,
            MealType.DRINK: None,
            MealType.SAUCE: None,
        }
        return trans.get(meal_type)
