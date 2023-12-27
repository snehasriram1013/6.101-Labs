#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 17:47:59 2023

@author: snehasriram
"""

"""
6.101 Lab 11:
Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


def tokenize(expression):
   exp = expression.replace('(', ' ( ').replace(')', ' ) ')
   return exp.split()
   


def parse(tokens):
    def parse_expression(index):
        token = tokens[index]

        if token == "(":
            left_expression, next_index = parse_expression(index + 1)
            operator = tokens[next_index]
            right_expression, end_index = parse_expression(next_index + 1)
            return (
                create_operation(operator, left_expression, right_expression),
                end_index + 1,
            )

        elif token[0] == "-" and (
            token[1:].isdigit()
            or token.count(".") == 1
            and token[1:].replace(".", "").isdigit()
        ):
            return Num(float(token)), index + 1

        elif token.isdigit() or (
            token.count(".") == 1 and token.replace(".", "").isdigit()
        ):
            return Num(float(token)), index + 1

        elif token.isalpha() and len(token) == 1:
            return Var(token), index + 1

        elif token == "**":
            left_expression, next_index = parse_expression(index - 1)
            right_expression, end_index = parse_expression(index + 1)
            return Pow(left_expression, right_expression), end_index + 1

        else:
            raise ValueError(f"Invalid character in expression: {token}")

    def create_operation(operator, left, right):
        if operator == "+":
            return Add(left, right)
        elif operator == "-":
            return Sub(left, right)
        elif operator == "*":
            return Mul(left, right)
        elif operator == "/":
            return Div(left, right)
        elif operator == "**":
            return Pow(left, right)
        else:
            raise ValueError("Invalid operator")

    parsed_expression, next_index = parse_expression(0)
    return parsed_expression


def expression(input_string):
    print(input_string)
    tokens = tokenize(input_string)
    return parse(tokens)


class Symbol:
    """
    Symbol Class
    """

    precedence = 0

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    def eval(self, mapping):
        left_value = self.left.eval(mapping)
        right_value = self.right.eval(mapping)
        return self.compute(left_value, right_value)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        try:
            left_value = self.left.__eq__(other.left)
            right_value = self.right.__eq__(other.right)
            return left_value and right_value
        except:
            return False

    def deriv(self, variable):
        raise NotImplementedError("Derivative not implemented for this expression.")

    def d(self, variable):
        return self.deriv(variable)


class BinOp(Symbol):
    """
    Binary Operator Class
    """

    operator = ""
    precedence = 0
    wrap_right_at_same_precedence = False
    wrap_left_at_same_precedence = False

    def __init__(self, l, r):
        if isinstance(l, int) or isinstance(l, float):
            self.left = Num(l)
        elif isinstance(l, str):
            self.left = Var(l)
        else:
            self.left = l

        if isinstance(r, int) or isinstance(r, float):
            self.right = Num(r)
        elif isinstance(r, str):
            self.right = Var(r)
        else:
            self.right = r

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + repr(self.left)
            + ", "
            + repr(self.right)
            + ")"
        )

    def __str__(self):
        str_rep_left = str(self.left)
        str_rep_right = str(self.right)

        if self.left.__class__.__name__ in ["Add", "Sub", "Mul", "Div", "Pow"]:
            if self.left.precedence < self.precedence:
                str_rep_left = "(" + str_rep_left + ")"
            elif (
                self.left.precedence == self.precedence
                and self.wrap_left_at_same_precedence
            ):
                str_rep_left = "(" + str_rep_left + ")"
        if self.right.__class__.__name__ in ["Add", "Sub", "Mul", "Div", "Pow"]:
            if self.right.precedence < self.precedence:
                str_rep_right = "(" + str_rep_right + ")"
            if (
                self.wrap_right_at_same_precedence
                and self.right.precedence == self.precedence
            ):
                str_rep_right = "(" + str_rep_right + ")"

        return str_rep_left + " " + self.operator + " " + str_rep_right

    def simplify(self):
        # Return a new instance of the simplified expression
        return self.simplify()

    def deriv(self, variable):
        left_derivative = self.left.d(variable)
        right_derivative = self.right.d(variable)
        return self.compute_derivative(left_derivative, right_derivative)


class Add(BinOp):
    """
    Addition Class
    """

    operator = "+"
    precedence = 1
    wrap_right_at_same_precedence = False
    wrap_left_at_same_precedence = False

    def compute(self, left, right):
        return left + right

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        # Simplification rules for addition
        if isinstance(left_simplified, Num) and isinstance(right_simplified, Num):
            return Num(left_simplified.n + right_simplified.n)

        if isinstance(right_simplified, Num) and right_simplified.n == 0:
            return left_simplified

        if isinstance(left_simplified, Num) and left_simplified.n == 0:
            return right_simplified

        return Add(left_simplified, right_simplified)

    def compute_derivative(self, left_derivative, right_derivative):
        return Add(left_derivative, right_derivative)


class Sub(BinOp):
    """
    Subtraction Class
    """

    operator = "-"
    precedence = 1
    wrap_right_at_same_precedence = True
    wrap_left_at_same_precedence = False

    def compute(self, left, right):
        return left - right

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        # Simplification rules for subtraction
        if isinstance(left_simplified, Num) and isinstance(right_simplified, Num):
            return Num(left_simplified.n - right_simplified.n)

        if isinstance(right_simplified, Num) and right_simplified.n == 0:
            return left_simplified

        return Sub(left_simplified, right_simplified)

    def compute_derivative(self, left_derivative, right_derivative):
        return Sub(left_derivative, right_derivative)


class Mul(BinOp):
    """
    Multiplication Class
    """

    operator = "*"
    precedence = 2
    wrap_right_at_same_precedence = False
    wrap_left_at_same_precedence = False

    def compute(self, left, right):
        return left * right

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        # Simplification rules for multiplication
        if isinstance(left_simplified, Num) and isinstance(right_simplified, Num):
            return Num(left_simplified.n * right_simplified.n)

        if isinstance(right_simplified, Num) and right_simplified.n == 0:
            return Num(0)

        if isinstance(left_simplified, Num) and left_simplified.n == 0:
            return Num(0)

        if isinstance(right_simplified, Num) and right_simplified.n == 1:
            return left_simplified

        if isinstance(left_simplified, Num) and left_simplified.n == 1:
            return right_simplified

        # Return a new instance of the simplified expression
        return Mul(left_simplified, right_simplified)

    def compute_derivative(self, left_derivative, right_derivative):
        return Add(Mul(self.left, right_derivative), Mul(self.right, left_derivative))


class Div(BinOp):
    """
    Division Class
    """

    operator = "/"
    precedence = 2
    wrap_right_at_same_precedence = True
    wrap_left_at_same_precedence = False

    def compute(self, left, right):
        return left / right

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        # Simplification rules for division
        if isinstance(left_simplified, Num) and isinstance(right_simplified, Num):
            return Num(left_simplified.n / right_simplified.n)

        if isinstance(left_simplified, Num) and left_simplified.n == 0:
            return Num(0)

        if isinstance(right_simplified, Num) and right_simplified.n == 1:
            return left_simplified

        # Return a new instance of the simplified expression
        return Div(left_simplified, right_simplified)

    def compute_derivative(self, left_derivative, right_derivative):
        numerator = Sub(
            Mul(self.right, left_derivative), Mul(self.left, right_derivative)
        )
        denominator_squared = Mul(self.right, self.right)
        return Div(numerator, denominator_squared)


class Pow(BinOp):
    """
    Exponentiation Class
    """

    operator = "**"
    precedence = 3
    wrap_right_at_same_precedence = False
    wrap_left_at_same_precedence = True  # New attribute for left subexpression

    def compute(self, left, right):
        return left**right

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        # Simplification rules for exponentiation
        if (
            isinstance(left_simplified, Num)
            and left_simplified.n == 0
            and not isinstance(right_simplified, Num)
        ):
            return Num(0)

        # Any expression raised to the power of 0should simplify to 1
        if isinstance(right_simplified, Num) and right_simplified.n == 0:
            return Num(1)
        # Any expression raised to the power 1 should simplify to itself.
        if isinstance(right_simplified, Num) and right_simplified.n == 1:
            return left_simplified

        return Pow(left_simplified, right_simplified)

    def compute_derivative(self, left_derivative, right_derivative):

        if isinstance(self.left, Symbol) and isinstance(self.right, Num):
            return Mul(
                Mul(self.right, self.left ** Sub(self.right, Num(1))), left_derivative
            )
        else:
            raise TypeError("Cannot compute derivative for this expression")


class Var(Symbol):
    """
    Variable Class
    """

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, mapping):
        if self.name in mapping:
            return mapping[self.name]
        else:
            raise NameError(f"Variable '{self.name}' is not defined in the mapping")

    def __eq__(self, other):
        if not isinstance(other, Var):
            return False
        return self.name == other.name

    def deriv(self, variable):
        if self.name == variable:
            return Num(1)
        else:
            return Num(0)

    def simplify(self):
        return self


class Num(Symbol):
    """
    Number Class
    """

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, mapping):
        return self.n

    def __eq__(self, other):
        if not isinstance(other, Num):
            return False
        return self.n == other.n

    def deriv(self, variable):
        return Num(0)

    def simplify(self):
        return self


if __name__ == "__main__":
    doctest.testmod()

    first = Var("x") ** 2

    print(repr(first))
    derivative = first.deriv(Var("x"))
    print(str(derivative))
