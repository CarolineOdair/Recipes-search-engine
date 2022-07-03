def do_lists_have_common_element(list_1:list, list_2:list) -> bool:
    """ Checks if two lists have at least one common element """
    if (set(list_1) & set(list_2)):
        return True
    else:
        return False

def do_list_includes_list(including_list:list, included_list:list) -> bool:
    """ Returns True if common part of lists is equal to `wanted_tags` """
    check = all(item in including_list for item in included_list)
    return check

def list_el_merged_with_plus(list_to_merge:list) -> str:
    """ Merges list of ints/floats/strings with '+' """
    return '+'.join([str(category_id) for category_id in list_to_merge])

REQUEST_FAILED_MSG = "Request failed"
EXCEPTION_LOG_MSG = "Exception has occurred:"

class IngrMatch:
    FULL = "full"
    PART = "partial"

    @classmethod
    def show_variables(self):
        return [value for name, value in vars(self).items() if name.isupper()]

class CuisineType:
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    REGULAR = "with meat"

class MealType:
    BREAKFAST = "sniadanie"
    SOUP = "zupy"
    DINNER = "danie glowne"
    LUNCH = "lunch"
    TO_BREAD = "do chleba"
    DESSERT = "desery"
    DRINK = "napoje"
    SAUCE = "sosy"
    SNACKS = "przekaski"

    @classmethod
    def show_variables(self):
        return [value for name, value in vars(self).items() if name.isupper()]