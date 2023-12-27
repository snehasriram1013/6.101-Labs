"""
6.101 Lab 13:
LISP Interpreter Part 2
"""

import doctest

import os
import re
import sys
import traceback
from cmd import Cmd

#!/usr/bin/env python3


sys.setrecursionlimit(20_000)


"""
6.101 Lab 12:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3


sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Class #
############################


class Frame:
    """
    Frame class
    """

    def __init__(self, parent):
        self.parent = parent
        self.bindings = {}

    def define(self, key, val):
        self.bindings[key] = val

    def lookup(self, key):
        if key in self.bindings:
            return self.bindings[key]
        elif self.parent:
            return self.parent.lookup(key)
        else:
            raise SchemeNameError(f"Name {key} not found in frames")


class UserDefined:
    """
    Represents user defined functions
    """

    def __init__(self, args, expression, frame):
        self.frame = frame
        self.expression = expression
        self.parameters = args

    def __call__(self, args):
        if len(args) != len(self.parameters):
            raise SchemeEvaluationError("Incorrect number of arguments")

        call_frame = Frame(self.frame)
        for param, arg in zip(self.parameters, args):
            call_frame.define(param, arg)

        return evaluate(self.expression, call_frame)


class Pair:
    """
    Pair class
    """

    def __init__(self, cn, cr):
        self.car = cn
        self.cdr = cr


class Nil:
    def __eq__(self, other):
        return isinstance(other, Nil)


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    split_by_line = source.splitlines()
    split = [i.replace("(", " ( ").replace(")", " ) ") for i in split_by_line]
    split = [i.split() for i in split]
    ans = []
    for sp_line in split:
        for token in sp_line:
            if token == ";":
                break
            ans.append(token)

    return ans


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    expressions = []
    # all_sub_tokens = []

    def parse_helper(tokens):
        if not tokens:
            return []

        parsed = []
        while tokens:
            token = tokens.pop(0)
            if token == "(":
                expressions.append("(")
                sub_expression = parse_helper(tokens)
                if sub_expression is None:
                    raise SchemeSyntaxError("MIsmatched Input")
                parsed.append(sub_expression)
            elif token == ")":
                expressions.append(")")
                return parsed

            else:
                tok = number_or_symbol(token)
                # all_sub_tokens.append(tok)
                parsed.append(tok)

        return parsed[0]

    new_tokens = tokens[:]
    parsed_expression = parse_helper(new_tokens)

    if parsed_expression is None or expressions.count("(") != expressions.count(")"):
        raise SchemeSyntaxError("Mismatched Input")
    elif len(tokens) > 1 and (len(expressions) == 0 or tokens[-1] != ")"):
        raise SchemeSyntaxError("Mismatched Input")

    return parsed_expression


######################
# Built-in Functions #
######################
product = lambda lst: 1 if len(lst) == 0 else lst[0] * product(lst[1:])
div = lambda lst: 1 if len(lst) < 1 else lst[0] / product(lst[1:])


def less(args):
    """
    less than
    """
    if len(args) <= 1:
        return True
    else:
        return args[0] < args[1] and less(args[1:])


def equal(args):
    """
    lequal to
    """
    if len(args) <= 1:
        return True
    else:
        return args[0] == args[1] and equal(args[1:])


def greater(args):
    """
    greater than
    """
    if len(args) <= 1:
        return True
    else:
        return args[0] > args[1] and greater(args[1:])


def greater_equal(args):
    """
    greater than or equal to
    """
    if len(args) <= 1:
        return True
    else:
        return args[0] >= args[1] and greater_equal(args[1:])


def less_equal(args):
    """
    less than or equal to
    """
    if len(args) <= 1:
        return True
    else:
        return args[0] <= args[1] and less_equal(args[1:])


def fnot(arg):
    """
    not EXP
    """
    if len(arg) != 1:
        raise SchemeEvaluationError("WRONG INPUTS FOR NOT")
    else:
        return not arg[0]


def car(arg):
    """
    returns car of a Pair obj
    """
    if len(arg) != 1 or not isinstance(arg[0], Pair):
        raise SchemeEvaluationError("WRONG INPUTS FOR CAR")
    else:
        return arg[0].car


def cdr(arg):
    """
    returns cdr of a Pair obj
    """
    if len(arg) != 1 or not isinstance(arg[0], Pair):
        raise SchemeEvaluationError("WRONG INPUTS FOR CDR")
    else:
        return arg[0].cdr


def length(link):
    """
    returns length of a Pair obj
    """

    def count_elements(curr):
        if isinstance(curr, Nil):
            return 0
        elif isinstance(curr, Pair):
            if isinstance(curr.car, Pair):  # Check for nested list
                return 1 + count_elements(curr.cdr)
            else:
                return 1 + count_elements(curr.cdr)
        else:
            raise SchemeEvaluationError("Not a proper list")

    return count_elements(link)


def is_list(obj):
    """
    returns if an obj is a list
    """
    while isinstance(obj, Pair):
        obj = obj.cdr
    return obj == Nil()


def list_ref(link, index):
    """
    returns val at an index in a list
    """

    if not isinstance(link, (Pair, Nil)):
        raise SchemeEvaluationError("Not a proper list")

    if link == Nil() and index >= 0 or not isinstance(index, (int)):
        raise SchemeEvaluationError("Index out of range")

    if index == 0:
        return link.car
    return list_ref(link.cdr, index - 1)


def append(lists):
    """
    rappends element to a list
    """

    # Helper function to concatenate pairs
    def concatenate(pair1, pair2):
        if not isinstance(pair1, (Pair, Nil)):
            raise SchemeEvaluationError("Arguments must be pairs")

        # If the first pair is empty, return the second pair
        if isinstance(pair1, Nil):
            return pair2

        # Otherwise, create a new pair by combining the car of the first pair
        # with the result of concatenating the cdr of the first pair with the second pair
        return Pair(pair1.car, concatenate(pair1.cdr, pair2))

    # If no lists are passed, return an empty list
    if not lists:
        return Nil()

    # If exactly one list is passed, return a shallow copy of that list
    if len(lists) == 1:
        if not isinstance(lists[0], (Pair, Nil)):
            raise SchemeEvaluationError("Arguments must be pairs")
        return lists[0]

    # Concatenate multiple lists together
    concatenated = Nil()
    for lst in lists:
        if not isinstance(lst, (Pair, Nil)):
            raise SchemeEvaluationError("Arguments must be pairs")
        concatenated = concatenate(concatenated, lst)

    return concatenated


def map_func(func, link):
    """
    mapping implementation
    """
    if not isinstance(link, (Pair, Nil)):
        raise SchemeEvaluationError("evaluation Error in map")

    if (not link) or (isinstance(link, Nil)):
        return Nil()
    else:
        return Pair(func([link.car]), map_func(func, link.cdr))


def filter_func(func, link):
    """
    filter implementation
    """
    if not isinstance(link, (Pair, Nil)):
        raise SchemeEvaluationError("evaluation Error in filter")
    if (not link) or (isinstance(link, Nil)):
        return Nil()
    else:
        if func([link.car]):
            return Pair(link.car, filter_func(func, link.cdr))
        else:
            return filter_func(func, link.cdr)


def reduce_func(func, lst, init_val):
    """
    reduce implementation
    """
    if not isinstance(lst, (Pair, Nil)):
        raise SchemeEvaluationError("evaluation Error in filter")
    if (not lst) or (isinstance(lst, Nil)):
        return init_val

    if not lst:  # If the list is empty, return the initial value
        return init_val

    # Apply the function to the initial value and the first element
    updated_val = func([init_val, lst.car])

    # Recursively call reduce_func with the updated value and the rest of the list
    return reduce_func(func, lst.cdr, updated_val)


def begin_func(args, frame):
    """
    begin implementation
    """
    if not args:
        raise SchemeEvaluationError("begin: no expressions to evaluate")

    result = None
    for expr in args:
        result = evaluate(expr, frame)  # Perform evaluation of each expression
    return result


def evaluate_file(filename, frame=None):
    """
    evaluate file implementation
    """
    f = open(filename, "r")
    read = f.read()

    exp = parse(tokenize(read))

    return evaluate(exp, frame)


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else args[0] - sum(args[1:]),
    "*": product,
    "/": div,
    "#t": True,
    "#f": False,
    "equal?": equal,
    ">": greater,
    ">=": greater_equal,
    "<": less,
    "<=": less_equal,
    "not": fnot,
    "car": car,
    "cdr": cdr,
    "nil": Nil(),
    "list?": lambda args: is_list(args[0]),
    "length": lambda args: length(args[0]),
    "list-ref": lambda args, index: list_ref(args[0], index),
    "append": append,
    "map": map_func,
    "filter": filter_func,
    "reduce": reduce_func,
    "begin": begin_func,
}

parent_frame = Frame(None)
parent_frame.bindings = scheme_builtins

##############
# Evaluation #
##############


# conditionals dictionary


def evaluate(tree, frame=None):
    """
    evaluate the given S expression/expression in Scheme
    """

    # create new 'global' frame if frame is not given
    if frame is None:
        frame = Frame(parent_frame)

    if isinstance(tree, list):
        if not tree:
            raise SchemeEvaluationError()
        first_elem = tree[0]
        if first_elem == "define":
            if not isinstance(tree[1], list):
                var_name = tree[1]
                expression = evaluate(tree[2], frame)
                frame.define(var_name, expression)
                return expression
            else:
                func_definition = tree[1]
                func_name = func_definition[0]

                params = func_definition[1:]

                lambda_exp = UserDefined(params, tree[2], frame)

                # Evaluate the lambda expression and perform the define operation
                frame.define(func_name, lambda_exp)

                return lambda_exp

        elif first_elem == "lambda":
            # evaluate all of the arguments to the function in the current frame
            lambda_args = tree[1]
            expression = tree[2]
            return UserDefined(lambda_args, expression, frame)

        elif first_elem == "if":
            # the conditionals special forms - create a dictionary to house them perhaps?
            predicate = evaluate(tree[1], frame)
            if predicate is True:
                return evaluate(tree[2], frame)
            else:
                return evaluate(tree[3], frame)

        elif first_elem == "and":
            for ele in tree[1:]:
                if not evaluate(ele, frame):
                    return False
            return True
        elif first_elem == "or":
            for ele in tree[1:]:
                if evaluate(ele, frame):
                    return True
            return False

        elif first_elem == "cons":
            if not (len(tree) == 3):
                raise SchemeEvaluationError("Incorrect Number of Arguments")
            else:
                return Pair(evaluate(tree[1], frame), evaluate(tree[2], frame))

        elif first_elem == "list":

            def create_list(elements):
                if not elements:
                    return Nil()  # Base case: Empty list evaluates to Nil
                else:
                    # Recursively evaluate elements and construct the linked list
                    return Pair(evaluate(elements[0], frame), create_list(elements[1:]))

            # Evaluate the elements within the list and construct the linked list
            return create_list(tree[1:])

        elif first_elem == "list-ref":
            if len(tree) != 3:
                raise SchemeEvaluationError("list-ref requires exactly two arguments")

            list_arg = evaluate(tree[1], frame)
            index_arg = evaluate(tree[2], frame)

            return list_ref(list_arg, index_arg)

        elif first_elem == "map":
            return map_func(evaluate(tree[1], frame), evaluate(tree[2], frame))
        elif first_elem == "filter":
            return filter_func(evaluate(tree[1], frame), evaluate(tree[2], frame))

        elif first_elem == "reduce":
            return reduce_func(
                evaluate(tree[1], frame),
                evaluate(tree[2], frame),
                evaluate(tree[3], frame),
            )

        elif first_elem == "begin":
            return begin_func(tree[1:], frame)
        elif first_elem == "del":
            var = tree[1]
            if var in frame.bindings:
                val = frame.bindings[var]
                del frame.bindings[var]
                return val
            else:
                raise SchemeNameError("Not in local frame")

        elif first_elem == "let":
            all_vars = tree[1]
            body = tree[2]

            # for var in all_vars:
            #     var[1] = evaluate(var[1], frame)

            child = Frame(frame)
            for var in all_vars:
                child.define(var[0], evaluate(var[1], frame))
            return evaluate(body, child)

        elif first_elem == "set!":
            var = tree[1]
            # Evaluate the expression in the current frame
            result = evaluate(tree[2], frame)

            # Find the nearest enclosing frame where the variable is defined
            target_frame = frame
            while target_frame and var not in target_frame.bindings:
                target_frame = target_frame.parent

            if target_frame:
                # Update the binding of the variable in the found frame
                target_frame.bindings[var] = result
            else:
                raise SchemeNameError(
                    f"Variable {var} not found in any enclosing frame"
                )

            return result

        else:
            function_to_call = evaluate(first_elem, frame)
            if callable(function_to_call):
                evaluated_args = [evaluate(arg, frame) for arg in tree[1:]]
                return function_to_call(evaluated_args)
            else:
                raise SchemeEvaluationError("First element is not callable")
    elif isinstance(tree, (float, int)):
        return tree

    return frame.lookup(tree)


def result_and_frame(tree, frame=None):
    if frame is None:
        parent_frame = Frame(None)
        for k, v in scheme_builtins.items():
            parent_frame.define(k, v)
        frame = Frame(parent_frame)
    evaluated = evaluate(tree, frame)
    return evaluated, frame


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    env = parent_frame
    files = sys.argv
    for file in files[1:]:
        # evaluate(parse(tokenize(arg)), env)
        evaluate_file(file, env)

    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(use_frames=True, verbose=True).cmdloop()


