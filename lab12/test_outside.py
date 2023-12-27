#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 13:48:25 2023

@author: snehasriram
"""

product = lambda lst: 1 if len(lst) == 0 else lst[0] * product(lst[1:])
div = lambda lst: 1 if len(lst) < 1 else lst[0] / product(lst[1:])
equals = lambda args:  True if args[0]==equals(args[1:]) else False
greater = lambda args:  True if args[0] > greater(args[1:]) else False
greater_equal = lambda args:  True if args[0] >= greater_equal(args[1:]) else False
less = lambda args:  True if args[0] < less(args[1:]) else False
less_equal = lambda args:  True if args[0] <= less_equal(args[1:]) else False


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else args[0] - sum(args[1:]),
    "*": product,
    "/": div,
    "#t": True,
    "#f": False,
    "equals?": equals,
    ">": greater,
    ">=": greater_equal,
    "<": less,
    "<=": less_equal,
    
}


print(scheme_builtins["#t"])