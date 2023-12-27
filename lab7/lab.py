"""
6.101 Lab 8:
SAT Solver
"""

#!/usr/bin/env python3

import sys
import typing

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS

# HELPERS


# updating a formula based on a new assignment
def update_formula(formula, assignment):
    """
    updates a formula based on a new assignment
    """
    name, val = assignment
    updated = []
    for clause in formula:
        if assignment in clause:
            continue
        else:
            mini_clause = []
            for unit in clause:
                if unit != (name, not val):
                    mini_clause.append(unit)
            if mini_clause:
                updated.append(mini_clause)
            else:
                return None

    return updated



def satisfying_assignment(formula):
    """
    returns the satisfying cnf assignment for the board
    """
    if formula is None:
        return None

    if len(formula) == 0:
        return {}  # Return the satisfying assignment

    if any(len(clause) == 0 for clause in formula):
        return None  # The formula is unsatisfiable

    units = set([tuple(clause) for clause in formula if len(clause) == 1])

    unit_assignments = {}
    if units:
        for unit in units:
            first, value = unit[0]  # Get the first unit clause
            new_formula = update_formula(formula, (first, value))
            if new_formula is not None and len(new_formula) > 0:
                unit_assignments[first] = value
            elif new_formula is None:
                return None
            elif len(new_formula) == 0:
                unit_assignments[first] = value
                return unit_assignments
            formula = new_formula

    first, value = formula[0][0]
    new_formula = update_formula(formula, (first, value))

    result = satisfying_assignment(new_formula)
    if result is not None:
        result[first] = value
        return result | unit_assignments
    # backtrack if the earlier thing didn't work
    new_formula = update_formula(formula, (first, not value))
    result = satisfying_assignment(new_formula)
    if result is not None:
        result[first] = not value
        return result | unit_assignments


def row_col_clause_generation(row, col, val, n):
    """
    generates clauses for the at most one type of number in a row condition
    """
    clauses = []

    for i in range(n):
        for j in range(i + 1, n):
            clauses.append([((row, i, val), False), ((row, j, val), False)])
            clauses.append([((i, col, val), False), ((j, col, val), False)])

    return clauses


def subgrid_clause_generation(subgrid_size, n):
    """
    generates the at least one value in each cell of the board clauses
    """
    subgrid_clauses = []

    # Iterate through each subgrid
    for row_start in range(0, n, subgrid_size):
        for col_start in range(0, n, subgrid_size):
            for num in range(1, n + 1):
                subgrid_clause = []
                for i in range(subgrid_size):
                    for j in range(subgrid_size):
                        r = row_start + i
                        c = col_start + j
                        subgrid_clause.append(((r, c, num), True))
                subgrid_clauses.append(subgrid_clause)

    return subgrid_clauses


def subgrid_clause_val_generation(subgrid_size, n, val):
    """
    generates at most one value in each cell of the board clauses
    """
    subgrid_val_clauses = []

    # Iterate through each subgrid
    for row_start in range(0, n, subgrid_size):
        for col_start in range(0, n, subgrid_size):
            subgrid_clause = []
            for i in range(subgrid_size):
                for j in range(subgrid_size):
                    r = row_start + i
                    c = col_start + j
                    for x in range(subgrid_size):
                        for y in range(subgrid_size):
                            if not ((r == row_start + x) and (c == col_start + y)):
                                subgrid_clause.append(
                                    [
                                        ((r, c, val), False),
                                        ((row_start + x, col_start + y, val), False),
                                    ]
                                )

            subgrid_val_clauses.extend(subgrid_clause)

    return subgrid_val_clauses


def cell_clause_generation(row, col, n):
    """
    generates at most 1 value in each cell of the board clauses
    """
    # pairs of values for every value in board
    cell_clauses = []
    for num in range(1, n):
        for num_two in range(num + 1, n + 1):
            cell_clauses.append(
                [((row, col, num), False), ((row, col, num_two), False)]
            )
    return cell_clauses


def sudoku_board_to_sat_formula(sudoku_board):
    """
    turn a given n*n 2d array to a cnf formula as described in the lab writeup,
    to be able to use the sat solver on to find a satisfiable sudoku board

    """
    n = len(sudoku_board)  # Size of the Sudoku board
    cnf = []

    def var(i, j, k, negated=False):
        return ((i, j, k), negated)

    for row in range(n):
        for col in range(n):
            # Fill in the initial values
            if sudoku_board[row][col] != 0:
                cnf.append([((row, col, sudoku_board[row][col]), True)])
            # Cell constraint - Each cell must have exactly one number
            cnf.append([((row, col, num), True) for num in range(1, n + 1)])
            # at most cell constraint
            cnf.extend(cell_clause_generation(row, col, n))
            # Row constraint - Each number must appear at least once in each row
            cnf.append(
                [((row, c, num), True) for c in range(n) for num in range(1, n + 1)]
            )
            # Column constraint - Each number must appear at least once in each column
            cnf.append(
                [((r, col, num), True) for r in range(n) for num in range(1, n + 1)]
            )
            # at most row clause and at most col clause
            for val in range(1, n + 1):
                cnf.extend(row_col_clause_generation(row, col, val, n))
    # all the subgrid things
    cnf.extend(subgrid_clause_generation(int(n**0.5), n))
    for val in range(1, n + 1):
        cnf.extend(subgrid_clause_val_generation(int(n**0.5), n, val))

    return cnf


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    if assignments is None:
        return None
    board = [[0 for _ in range(n)] for _ in range(n)]

    for (i, j, k), value in assignments.items():
        if assignments[(i, j, k)] is not False:
            board[i][j] = k
    return board


if __name__ == "__main__":
    rules = [
        [("a", True), ("b", True)],
        [("a", False), ("b", False), ("c", True)],
        [("b", True), ("c", True)],
        [("b", True), ("c", False)],
    ]

    grid3 = [
        [0, 0, 1, 0, 0, 9, 0, 0, 3],
        [0, 8, 0, 0, 2, 0, 0, 9, 0],
        [9, 0, 0, 1, 0, 0, 8, 0, 0],
        [1, 0, 0, 5, 0, 0, 4, 0, 0],
        [0, 7, 0, 0, 3, 0, 0, 5, 0],
        [0, 0, 6, 0, 0, 4, 0, 0, 7],
        [0, 0, 8, 0, 0, 5, 0, 0, 6],
        [0, 3, 0, 0, 7, 0, 0, 4, 0],
        [2, 0, 0, 3, 0, 0, 9, 0, 0],
    ]

    sudoku = sudoku_board_to_sat_formula(grid3)

    check = satisfying_assignment(sudoku)

    returned_board = assignments_to_sudoku_board(check, 4)
    print(returned_board)
