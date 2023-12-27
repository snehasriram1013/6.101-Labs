import sys
import doctest

import os
import re
import sys
import traceback
from cmd import Cmd
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

    # when to raise an error
    # types of malformed input
    # parentheses are not matched
    # values before first parentheses
    # values after last parentheses
    # function not first
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
    elif len(tokens) > 1 and (len(expressions) == 0 or tokens[-1]!= ")"):
        raise SchemeSyntaxError("Mismatched Input")

    return parsed_expression




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
            raise SchemeNameError("Name not found in frames")


######################
# Built-in Functions #
######################
product = lambda lst: 1 if len(lst) == 0 else lst[0] * product(lst[1:])
div = lambda lst: 1 if len(lst) < 1 else lst[0] / product(lst[1:])

scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else args[0] - sum(args[1:]),
    "*": product,
    "/": div,
}

parent_frame = Frame(None)
parent_frame.bindings = scheme_builtins

##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    evaluate the given S expression/expression in Scheme
    """
    #create new 'global' frame if frame is not given
    if frame is None:
        frame = Frame(parent_frame)
    #if we are given a str, it is either a symbol or a name of a func
    if isinstance(tree, str):
        if frame.lookup(tree):
            return frame.lookup(tree)
        else:
            raise SchemeNameError(f"Variable '{tree}' not found")
    
    elif isinstance(tree, (float, int)):
        return tree
    
    elif isinstance(tree, list):
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
                
                lambda_exp = UserDefined(params, tree[2] , frame)
                
                # Evaluate the lambda expression and perform the define operation
                frame.define(func_name, lambda_exp)
                
                return lambda_exp

        elif first_elem == "lambda":
            # evaluate all of the arguments to the function in the current frame
            lambda_args = tree[1]
            expression = tree[2]
            return UserDefined(lambda_args, expression, frame)

        else:
            function_to_call = evaluate(first_elem, frame)
            if callable(function_to_call):
                evaluated_args = [evaluate(arg, frame) for arg in tree[1:]]
                return function_to_call(evaluated_args)
            else:
                raise SchemeEvaluationError("First element is not callable")


    else:
        raise SchemeEvaluationError("Invalid expression type")



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


def result_and_frame(tree, frame=None):
    if frame is None:
        parent_frame = Frame(None)
        for k, v in scheme_builtins.items():
            parent_frame.define(k, v)
        frame = Frame(parent_frame)
    evaluated = evaluate(tree, frame)
    return evaluated, frame


########
# REPL #
########


try:
    import readline
except:
    readline = None


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.  Not guaranteed to work in all cases, but maybe in most?
    """
    plat = sys.platform
    supported_platform = plat != "Pocket PC" and (
        plat != "win32" or "ANSICON" in os.environ
    )
    # IDLE does not support colors
    if "idlelib" in sys.modules:
        return False
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


class SchemeREPL(Cmd):
    """
    Class that implements a Read-Evaluate-Print Loop for our Scheme
    interpreter.
    """

    history_file = os.path.join(os.path.expanduser("~"), ".6101_scheme_history")

    if supports_color():
        prompt = "\033[96min>\033[0m "
        value_msg = "  out> \033[92m\033[1m%r\033[0m"
        error_msg = "  \033[91mEXCEPTION!! %s\033[0m"
    else:
        prompt = "in> "
        value_msg = "  out> %r"
        error_msg = "  EXCEPTION!! %s"

    keywords = {
        "define",
        "lambda",
        "if",
        "equal?",
        "<",
        "<=",
        ">",
        ">=",
        "and",
        "or",
        "del",
        "let",
        "set!",
        "+",
        "-",
        "*",
        "/",
        "#t",
        "#f",
        "not",
        "nil",
        "cons",
        "list",
        "cat",
        "cdr",
        "list-ref",
        "length",
        "append",
        "begin",
    }

    def __init__(self, use_frames=False, verbose=False):
        self.verbose = verbose
        self.use_frames = use_frames
        self.global_frame = None
        Cmd.__init__(self)

    def preloop(self):
        if readline and os.path.isfile(self.history_file):
            readline.read_history_file(self.history_file)

    def postloop(self):
        if readline:
            readline.set_history_length(10_000)
            readline.write_history_file(self.history_file)

    def completedefault(self, text, line, begidx, endidx):
        try:
            bound_vars = set(self.global_frame)
        except:
            bound_vars = set()
        return sorted(i for i in (self.keywords | bound_vars) if i.startswith(text))

    def onecmd(self, line):
        if line in {"EOF", "quit", "QUIT"}:
            print()
            print("bye bye!")
            return True

        elif not line.strip():
            return False

        try:
            token_list = tokenize(line)
            if self.verbose:
                print("tokens>", token_list)
            expression = parse(token_list)
            if self.verbose:
                print("expression>", expression)
            if self.use_frames:
                output, self.global_frame = result_and_frame(
                    *(
                        (expression, self.global_frame)
                        if self.global_frame is not None
                        else (expression,)
                    )
                )
            else:
                output = evaluate(expression)
            print(self.value_msg % output)
        except SchemeError as e:
            if self.verbose:
                traceback.print_tb(e.__traceback__)
                print(self.error_msg.replace("%s", "%r") % e)
            else:
                print(self.error_msg % e)

        return False

    completenames = completedefault

    def cmdloop(self, intro=None):
        while True:
            try:
                Cmd.cmdloop(self, intro=None)
                break
            except KeyboardInterrupt:
                print("^C")


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    SchemeREPL(use_frames=False, verbose=True).cmdloop()
    x = tokenize("(foo (bar 3.14))")
    print(x)
