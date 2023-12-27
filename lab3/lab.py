"""
6.101 Lab 6:
Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def flatten_list(input_list):
    flat = []
    for ele in input_list:
        if not isinstance(ele, list):
            flat.append(ele)
        else:
            flat.extend(flatten_list(ele))
    return flat


def make_recipe_book(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    compounds = {}
    for r in recipes:
        if r[0] == "compound" and r[1] not in compounds:
            compounds[r[1]] = [r[2]]
        elif r[0] == "compound" and r[1] in compounds:
            compounds[r[1]].append(r[2])
    return compounds


def make_atomic_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    atomics = {}
    for r in recipes:
        if r[0] == "atomic" and r[1] not in atomics:
            atomics[r[1]] = r[2]
    return atomics


def low(rec, atomic, food_item):
    """
    helper function for the lowest cost method, recursively finds the lowest cost of
    the lowest cost recipe given a given food item
    """
    if food_item in atomic:
        return atomic[food_item]
    else:
        min_cost = float("inf")

        if food_item in rec:
            for components in rec[food_item]:
                component_cost = 0
                for component, quantity in components:
                    component_cost += low(rec, atomic, component) * quantity
                min_cost = min(min_cost, component_cost)
        return min_cost


def lowest_cost(recipes, food_item, forbidden=()):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    rec = make_recipe_book(recipes)
    atomic = make_atomic_costs(recipes)
    if len(forbidden) > 0:
        for cannot in forbidden:
            if cannot in rec:
                del rec[cannot]
            if cannot in atomic:
                del atomic[cannot]
    ans = low(rec, atomic, food_item)
    # if food_item not in database, return none
    if food_item not in rec and food_item not in atomic:
        return None
    elif ans == float("inf"):
        return None
    else:
        return ans


def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    ans_dict = {}
    for ing in flat_recipe:
        ans_dict[ing] = flat_recipe[ing] * n
    return ans_dict


def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    ans_d = {}
    for recipe in flat_recipes:
        for ing in recipe:
            if ing in ans_d:
                ans_d[ing] += recipe[ing]
            else:
                ans_d[ing] = recipe[ing]
    return ans_d


def helper(rec, atomic, food_item):
    """
    helper function for the cheapest flat recipe function, recursively finds
    the lowest cost recipe for the given function
    """
    # pseudocode
    # get all atomic food items needed to create a specific recipe
    # kinda like lowest cost, implements lowest cost function, but
    # also keeps track of ingredients

    # initial dictionary things
    # base case
    if food_item in atomic:
        return {food_item: 1}, atomic[food_item]
    # recursive case
    else:
        # min_cost
        min_cost = float("inf")
        # best_recipe
        best_rec = {}
        # if food_item in rec
        if food_item in rec:
            # for methods(components), checks which method is better in rec[food_item]
            for components in rec[food_item]:
                component_cost = 0
                recipe = {}
                for component, quantity in components:
                    component_cost += helper(rec, atomic, component)[1] * quantity
                    comp_rec = helper(rec, atomic, component)[0]
                    for ing, atom_quant in comp_rec.items():
                        if ing not in recipe:
                            recipe[ing] = quantity * atom_quant
                        else:
                            recipe[ing] += quantity * atom_quant
                if component_cost < min_cost:
                    best_rec = recipe
                    min_cost = component_cost

        return best_rec, min_cost


def cheapest_flat_recipe(recipes, food_item, forbidden=()):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    rec = make_recipe_book(recipes)
    atomic = make_atomic_costs(recipes)

    if len(forbidden) > 0:
        for f in forbidden:
            if f in rec:
                del rec[f]
            if f in atomic:
                del atomic[f]
    ans = helper(rec, atomic, food_item)[0]
    if ans == {}:
        return None

    return ans


def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    # base case
    if len(flat_recipes) == 0:
        return [{}]

    first = flat_recipes[0]
    rest = flat_recipes[1:]
    rest_combinations = ingredient_mixes(rest)

    combinations = []
    for d in first:
        for x in rest_combinations:
            ansD = {}
            for key, value in d.items():
                ansD[key] = value
            for k, v in x.items():
                if k in ansD:
                    ansD[k] += v
                else:
                    ansD[k] = v
            combinations.append(ansD)
    return combinations


def all_flat_recipes_helper(rec, atomic, food_item):
    # base case

    if food_item in atomic:
        return [{food_item: 1}]
    # recursive case
    else:
        # all recipes possible for one ingredient
        all_possible = []
        if food_item in rec:
            for ingredient_list in rec[food_item]:
                print(ingredient_list)
                sectioned_rec = []
                for mini_ingredient, quantity in ingredient_list:
                    # recursive call?
                    mini_recipe = all_flat_recipes_helper(rec, atomic, mini_ingredient)

                    recipe_ing = [scale_recipe(mini, quantity) for mini in mini_recipe]
                    sectioned_rec.append(recipe_ing)

                all_possible.extend(ingredient_mixes(sectioned_rec))
        return all_possible


def all_flat_recipes(recipes, food_item, forbidden=()):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """

    rec = make_recipe_book(recipes)
    atomic = make_atomic_costs(recipes)

    if len(forbidden) > 0:
        for f in forbidden:
            if f in rec:
                del rec[f]
            if f in atomic:
                del atomic[f]
    combo_dicts = all_flat_recipes_helper(rec, atomic, food_item)

    return combo_dicts


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
    cookie_recipes = [
        ("compound", "cookie sandwich", [("cookie", 2), ("ice cream scoop", 3)]),
        ("compound", "cookie", [("chocolate chips", 3)]),
        ("compound", "cookie", [("sugar", 10)]),
        ("atomic", "chocolate chips", 200),
        ("atomic", "sugar", 5),
        ("compound", "ice cream scoop", [("vanilla ice cream", 1)]),
        ("compound", "ice cream scoop", [("chocolate ice cream", 1)]),
        ("atomic", "vanilla ice cream", 20),
        ("atomic", "chocolate ice cream", 30),
    ]
    cake_recipes = [{"cake": 1}, {"gluten free cake": 1}]
    icing_recipes = [{"vanilla icing": 1}, {"cream cheese icing": 1}]
    topping_recipes = [{"sprinkles": 20}]
    all_flat = all_flat_recipes(
        cookie_recipes, "cookie sandwich", ("sugar", "chocolate ice cream")
    )

    print(all_flat)
