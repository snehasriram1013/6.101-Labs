#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 17:54:26 2023

@author: snehasriram
"""


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
    split = [i.replace('(', ' ( ').replace(')',' ) ') for i in split_by_line]
    split = [i.split() for i in split]
    ans = []
    for sp_line in split:
        for token in sp_line:
            if token == ';':
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
    def parse_helper(tokens):
        if not tokens:
            return []

        parsed = []
        while tokens:
            token = tokens.pop(0)
            if token == "(":
                parsed.append(parse_helper(tokens))
            elif token == ")":
                return parsed
            else:
                parsed.append(number_or_symbol(token))

                    

        return parsed[0]
    new_tokens = tokens[:]
    parsed_expression = parse_helper(new_tokens)
    return parsed_expression
    

parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')'])
            
        
