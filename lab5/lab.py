#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 23:12:22 2023

@author: snehasriram
"""

"""
6.1010 Lab 4: 
Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return level_description


def victory_check(game):
    """
    checks a given gamestate to see if the user has won the game
    """
    targets = 0
    comps = 0
    win = 0
    for r in range(len(game)):
        for c in range(len(game[0])):
            if "target" in game[r][c]:
                targets += 1
            if "computer" in game[r][c]:
                comps += 1
            if "target" in game[r][c] and "computer" in game[r][c]:
                win += 1
    return targets == win and targets == comps and not (targets == 0 and comps == 0)


def self_loc(game_state):
    """
    finds and returns a (row, col) tuple of the location of the player on the board
    """
    for r in range(len(game_state)):
        for c in range(len(game_state[0])):
            if "player" in game_state[r][c]:
                return (r, c)


def check_wall_and_bounds(game_state, newr, newc):
    """
    checks the given (row, col) values for if the position is on the board and
    if the position is a wall
    """
    return (
        0 <= newr < len(game_state)
        and 0 <= newc < len(game_state[0])
        and ("wall" not in game_state[newr][newc])
    )


def check_computer(game_state, new_r, new_c, direction):
    """
    checks the position one past the given (row,col) position for there
    being a computer-computer pair next to each other on the board,
    or a wall-computer pair, in which case nothing on the board can move
    """
    comp_r, comp_c = (
        new_r + direction_vector[direction][0],
        new_c + direction_vector[direction][1],
    )

    return not (
        ("computer" in game_state[comp_r][comp_c])
        and ("computer" in game_state[new_r][new_c])
    ) and not (
        ("wall" in game_state[comp_r][comp_c])
        and ("computer" in game_state[new_r][new_c])
    )


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """

    def move_self(game_state):
        """
        moves the player on the board in accordance to the game's rules
        """
        if direction is None:
            return
        old_loc = self_loc(game_state)
        new_r, new_c = (
            old_loc[0] + direction_vector[direction][0],
            old_loc[1] + direction_vector[direction][1],
        )
        if check_wall_and_bounds(game, new_r, new_c) and check_computer(
            game, new_r, new_c, direction
        ):
            if "target" in game_state[old_loc[0]][old_loc[1]]:
                game_state[old_loc[0]][old_loc[1]] = ("target",)
            else:
                game_state[old_loc[0]][old_loc[1]] = tuple()
            if "target" in game_state[new_r][new_c]:
                game_state[new_r][new_c] = ("player", "target")
            else:
                game_state[new_r][new_c] = ("player",)

    def move_computer(game_state):
        """
        moves the computer on the board in accordance to how the player moved,
        and the rules of the game
        """
        if direction is None:
            return

        old_loc = self_loc(game_state)
        new_r, new_c = (
            old_loc[0] + direction_vector[direction][0],
            old_loc[1] + direction_vector[direction][1],
        )
        comp_r, comp_c = (
            new_r + direction_vector[direction][0],
            new_c + direction_vector[direction][1],
        )
        if check_wall_and_bounds(game_state, new_r, new_c):
            if "computer" in game[new_r][new_c]:
                if check_wall_and_bounds(game, comp_r, comp_c) and (
                    "computer" not in game[comp_r][comp_c]
                ):
                    if "target" in game_state[comp_r][comp_c]:
                        game_state[comp_r][comp_c] = ("target", "computer")
                    else:
                        game_state[comp_r][comp_c] = ("computer",)

    def play():
        """
        plays the game and returns a copy of the played gamestate
        """

        def deepcopy_nested_list(input_list):
            if isinstance(input_list, list):
                return list(deepcopy_nested_list(item) for item in input_list)
            else:
                return input_list

        game_state = deepcopy_nested_list(game)
        move_computer(game_state)
        move_self(game_state)
        return game_state

    return play()


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    x = [[list(ele) for ele in sub] for sub in game]

    return list(list(i) for i in x)


def make_game_state(game_state):
    """
    turns the gamestate into a hashable type to be used in the BFS algorithm
    in the solver
    """
    x = [[tuple(ele) for ele in sub] for sub in game_state]

    return tuple(tuple(i) for i in x)


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """

    def get_dir(state, neighbor):
        """
        given a game_state and its neighbor, returns a direction that the board moved

        """
        for d in direction_vector:
            if (
                self_loc(neighbor)[0] - self_loc(state)[1] == direction_vector[d][0]
                and self_loc(neighbor)[1] - self_loc(state)[1] == direction_vector[d][1]
            ):
                return d

    def goal_test(game_state):
        """
        checks if the game has been won at that gamestate

        """
        return victory_check(game_state)

    def find_neighbors(game_state):
        """
        finds all possible moves that can be made by the player in one movement
        """
        all_moves = []
        for d in direction_vector:
            all_moves.append(step_game(dump_game(game_state), d))
        print(all_moves)
        return [make_game_state(i) for i in all_moves]

    def path_finder(neighbors_func, start, goal_test):
        """
        Generalizes the bfs(path finding) process to be used with many different
        inputs and outputs. Takes in a neighbors function, a state to start at, and a
        goal_test to end at

        """
        if goal_test(start):
            return (start,)

        agenda = [(make_game_state(start),)]
        visited = {make_game_state(start)}

        while agenda:
            path = agenda.pop(0)
            terminal_state = path[-1]

            for neighbor in neighbors_func(terminal_state):
                if neighbor not in visited:
                    new_path = path + (neighbor,)
                    if goal_test(dump_game(neighbor)):
                        return new_path
                    visited.add(neighbor)
                    agenda.append(new_path)

    path = path_finder(find_neighbors, game, goal_test)

    dirs = []
    if path:
        for i in range(len(path) - 1):
            dirs.append(get_dir(path[i], path[i + 1]))
        return dirs
    return None


if __name__ == "__main__":
    level = [[["player"], [], []], [["target"], ["computer"], []]]

    def finder(game_state):
        all_moves = []
        for d in direction_vector:
            all_moves.append(step_game(dump_game(game_state), d))
        print(all_moves)

    one = new_game(level)
    solved = finder(one)

    # print(solved)
