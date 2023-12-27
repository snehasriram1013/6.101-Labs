"""
6.101 Lab 3:
Bacon Number
"""

#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    """


    Parameters
    ----------
    raw_data : a list containing tuples of value, actor1,actor2, movie

    Returns
    -------
    transform_dict : a dictionary representation of the given data
    {actor_id: [set(coworkers), set(movies)]}

    """
    # dictionary with string set key value pair, every
    # actor an actor key has worked with
    transform_dict = {}
    for data in raw_data:
        if data[0] not in transform_dict:
            transform_dict[data[0]] = [set(), set()]
        if data[1] not in transform_dict:
            transform_dict[data[1]] = [set(), set()]
        transform_dict[data[0]][0].add(data[1])
        transform_dict[data[1]][0].add(data[0])
        transform_dict[data[0]][1].add(data[2])
        transform_dict[data[1]][1].add(data[2])
    return transform_dict


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Takes in the transformed data representation, actor_id_1, and actor_id_2,
    and returns if actor1 has worked with actor2

    """
    if actor_id_1 in transformed_data[actor_id_2][0] or actor_id_1 == actor_id_2:
        return True
    return False


def actors_with_bacon_number(transformed_data, n):
    """
    Checks for all actors in dataset, and returns a set of all actors who
    have a bacon number of n
    """
    bacon_num = set()
    for data in transformed_data:
        if (len(bacon_path(transformed_data, data)) - 1) == n:
            bacon_num.add(data)
    return bacon_num


def generalized_path_finder(transformed_data, start, end):
    """
    Generalizes the bfs(path finding) process to be used with many different
    inputs and outputs. Takes in a transformed dataset, a node to start at, a
    node to end at, and a type of data it is working with(actor or movie)

    """
    if start == end:
        return (start,)

    def worked_with(actor):
        return transformed_data[actor][0]

    agenda = [(start,)]
    visited = {start}

    while agenda:
        path = agenda.pop(0)
        actor = path[-1]

        for coworker in worked_with(actor):
            if coworker not in visited:
                new_path = path + (coworker,)
                if coworker == end:
                    return new_path
                visited.add(coworker)
                agenda.append(new_path)


def bacon_path(transformed_data, actor_id):
    """
    Finds the shortest path between Kevin Bacon and the given actor, if there
    is one. Otherwise, returns none
    """
    return generalized_path_finder(transformed_data, 4724, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Finds the shortest path between given actor 1 and given actor 2, if there
    is one. Otherwise, returns none
    """
    return generalized_path_finder(transformed_data, actor_id_1, actor_id_2)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Finds the shortest path between any actor that passes the goal test
    and the given actor, if there is one. Otherwise, returns null
    """
    if goal_test_function(actor_id_1):
        return [actor_id_1]

    agenda = [(actor_id_1,)]
    visited = {actor_id_1}

    while agenda:
        path = agenda.pop(0)
        actor = path[-1]

        for coworker in transformed_data[actor][0]:
            if coworker not in visited:
                new_path = path + (coworker,)
                if goal_test_function(coworker):
                    return list(new_path)
                visited.add(coworker)
                agenda.append(new_path)


def actors_connecting_films(transformed_data, film1, film2):
    """
    This function takes three arguments:
        The database to be used (the same structure as before), and
        Two film ID numbers;
    and it returns the shortest possible list of actor ID
    numbers (in order) that connect those two films.
    """
    eligible = []
    for data in transformed_data:
        if film1 in transformed_data[data][1]:
            eligible.append(data)

    def goal_test(actor):
        return film2 in transformed_data[actor][1]

    paths = []
    for ele in eligible:
        paths.append(actor_path(transformed_data, ele, goal_test))
    min_val = min([len(x) for x in paths])
    return [i for i in paths if len(i) == min_val][0]


if __name__ == "__main__":
    with open("resources/large.pickle", "rb") as f:
        large = pickle.load(f)

    with open("resources/names.pickle", "rb") as f:
        namesdict = pickle.load(f)

    with open("resources/tiny.pickle", "rb") as f:
        tinypickle = pickle.load(f)

    with open("resources/movies.pickle", "rb") as f:
        moviesdict = pickle.load(f)

    largedb = transform_data(large)

    # According to the large.pickle database, what is the minimal path of actors
    # from Harald Krassnitzer to Katherine LaNasa? Enter your answer as a Python
    # list of actor names below:
    largedb = transform_data(large)
    path = actor_to_actor_path(
        largedb, namesdict["Harald Krassnitzer"], namesdict["Katherine LaNasa"]
    )
    flipped_names = dict(zip(namesdict.values(), namesdict.keys()))
    namespath = [flipped_names[i] for i in path]
    print(namespath)

    # Movie Paths
    movies = []
    path_movie_actors = actor_to_actor_path(
        largedb, namesdict["Ice Cube"], namesdict["Sven Batinic"]
    )
    for i in range(len(path_movie_actors) - 1):
        for x in large:
            if (
                path_movie_actors[i] == x[0] and path_movie_actors[i + 1] == x[1]
            ) or (
                path_movie_actors[i + 1] == x[0] and path_movie_actors[i] == x[1]
            ):
                movies.append(x[2])
    flipped_movies = dict(zip(moviesdict.values(), moviesdict.keys()))
    moviespath = [flipped_movies[i] for i in movies]
    print(moviespath)
    
    x = actor_to_actor_path(largedb, namesdict["Zendaya"], namesdict["Tom Holland"])
    names_of_people = [flipped_names[i] for i in x]
    print(names_of_people)
