"""
6.101 Lab 7:
Six Double-Oh Mines
"""
#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mines)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    count = dig_nd(game, (row, col))
    return count


def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, all_visible)


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    two_d_locs = render_2d_locations(game, all_visible)
    str_rep = ""
    for row in range(len(two_d_locs)):
        s = ""
        for col in range(len(two_d_locs[0])):
            s += two_d_locs[row][col]
        str_rep += s
        if row != len(two_d_locs) - 1:
            str_rep += "\n"
    return str_rep


# N-D IMPLEMENTATION


# A function that, given an N-d array and a tuple/list of coordinates, returns the value at those coordinates in the array.
def get_value_at_coordinates(arr, coordinates):
    """
    Get the value at the specified coordinates in the N-dimensional array without 
    mutating the input array
    """

    def recursive_get(array, coords):
        if len(coords) == 0:
            return array
        else:
            current_coord = coords[0]
            if 0 <= current_coord < len(array):
                return recursive_get(array[current_coord], coords[1:])
            else:
                return None

    result = recursive_get(arr, coordinates)
    return result


def recursive_set(arr, coords, value):
    """
    A function that, given an N-d array, a tuple/list of coordinates, and a
    value, replaces the value at those coordinates in the array with the given
    value.
    """
    if len(coords) == 1:
        arr[coords[0]] = value
    else:
        current_coord = coords[0]
        if 0 <= current_coord < len(arr):
            recursive_set(arr[current_coord], coords[1:], value)
    return arr


def make_recursive_arr(dimensions, value):
    """
    A function that, given a list of dimensions and a value, creates a new N-d array
    with those dimensions, where each value in the array is the given value.
    """
    arr = []
    # base case
    if len(dimensions) == 1:
        return [value for i in range(dimensions[0])]
    # recursive case
    else:
        arr.append(
            [make_recursive_arr(dimensions[1:], value) for i in range(dimensions[0])]
        )
    return arr[0]


def victory_check(game):
    """
    Helper function to check the status of the game(victory check)
    """
    num_revealed_mines = 0
    num__not_revealed_squares = 0
    for coord in get_all_coordinates(game["dimensions"]):
        if get_value_at_coordinates(game["board"], coord) == ".":
            if get_value_at_coordinates(game["visible"], coord):
                # if the game visible is True, and the board is '.',
                # add 1 to mines revealed
                num_revealed_mines += 1
        elif not get_value_at_coordinates(game["visible"], coord):
            num__not_revealed_squares += 1

    return (num_revealed_mines, num__not_revealed_squares)


def neighbors(coords, dims, current=()):
    """
    Returns all neighbors of a given coordinate
    """
    n = []

    if len(coords) == 1:
        for i in range(-1, 2):
            new_coord = i + coords[0]
            if 0 <= new_coord < dims[0]:
                n.append(current + (new_coord,))
    else:
        for i in range(-1, 2):
            new_coord = i + coords[0]
            if 0 <= new_coord < dims[0]:
                n += neighbors(coords[1:], dims[1:], current + (new_coord,))
    return [tup for tup in n if tup != coords]



def get_all_coordinates(dim, current_dim=()):
    """
    A function that returns all possible coordinates in a given board
    """
    all_poss = []
    if len(dim) == 1:
        for i in range(dim[0]):
            all_poss.append(current_dim + (i,))
    else:
        for i in range(dim[0]):
            all_poss += get_all_coordinates(dim[1:], current_dim + (i,))
    return all_poss


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    board = make_recursive_arr(dimensions, 0)
    visible = make_recursive_arr(dimensions, False)
    state = "ongoing"
    def check_num_mines(coords, board):
        for mine_coord in mines:
            neighbor = neighbors(mine_coord,dimensions)
            for n in neighbor:
                value = get_value_at_coordinates(board, n)
                if value!=".":
                    board = recursive_set(board, n, value+1)
            board = recursive_set(board, mine_coord, ".")
        return board

    return {
        "dimensions": dimensions,
        "board": check_num_mines(mines, board),
        "visible": visible,
        "state": state,
    }


def dig_helper(game, coordinates):
    """
    helper for the dig_nd function
    """
    value = get_value_at_coordinates(game["board"], coordinates)
    if game["state"] == "defeat" or game["state"] == "victory":
        return 0

    if  value == ".":
        game["visible"] = recursive_set(game["visible"], coordinates, True)
        game["state"] = "defeat"
        return 1

    # if current loc not revealed, reveal it and revealed = 1
    if get_value_at_coordinates(game["visible"], coordinates) != True:
        game["visible"] = recursive_set(game["visible"], coordinates, True)
        revealed = 1
    else:
        return 0
    # check if equal to zero
    if value == 0:
        neighbor = neighbors(coordinates, game["dimensions"])

        for n in neighbor:
            if get_value_at_coordinates(
                game["board"], n
            ) != "." and not get_value_at_coordinates(game["visible"], n):
                revealed += dig_helper(game, n)
    
    return revealed
def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    value = get_value_at_coordinates(game["board"], coordinates)
    if game["state"] == "defeat" or game["state"] == "victory":
        return 0

    if  value == ".":
        game["visible"] = recursive_set(game["visible"], coordinates, True)
        game["state"] = "defeat"
        return 1
    revealed = dig_helper(game, coordinates)
    num_revealed_mines, num_not_revealed_squares = victory_check(game)
    if num_not_revealed_squares > 0:
        game["state"] = "ongoing"
        return revealed
    else:
        game["state"] = "victory"
        return revealed
    return revealed


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    locs = make_recursive_arr(game["dimensions"], 0)
    all_poss = get_all_coordinates(game["dimensions"])
    if all_visible:
        for coord in all_poss:
            value = get_value_at_coordinates(game["board"], coord)
            if value == 0:
                locs = recursive_set(locs, coord, " ")
            else:
                locs = recursive_set(locs, coord, str(value))
    else:
        for coord in all_poss:
            if not get_value_at_coordinates(game["visible"], coord):
                locs = recursive_set(locs, coord, "_")
            else:
                if get_value_at_coordinates(game["board"], coord) == 0:
                    locs = recursive_set(locs, coord, " ")
                else:
                    locs = recursive_set(
                        locs, coord, str(get_value_at_coordinates(game["board"], coord))
                    )
    return locs


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

# Alternatively, can run the doctests JUST for specified function/methods,
# e.g., for render_2d_locations or any other function you might want.  To
# do so, comment out the above line, and uncomment the below line of code.
# This may be useful as you write/debug individual doctests or functions.
# Also, the verbose flag can be set to True to see all test results,
# including those that pass.
#
# doctest.run_docstring_examples(
#    render_2d_locations,
#    globals(),
#    optionflags=_doctest_flags,
#    verbose=False
# )
