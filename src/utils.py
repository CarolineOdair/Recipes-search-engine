def do_lists_have_common_element(list_1:list, list_2:list):
    """ Checks if two lists have at least one common element """
    if (set(list_1) & set(list_2)):
        return True
    else:
        return False

def do_list_includes_list(including_list:list, included_list:list):
    """ Returns True if common part of lists is equal to `wanted_tags` """
    check = all(item in including_list for item in included_list)
    return check

class NotImplementedError(Exception):
    pass

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