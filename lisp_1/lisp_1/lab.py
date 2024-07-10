"""
6.1010 Spring '23 Lab 11: LISP Interpreter Part 1
"""
#!/usr/bin/env python3

import sys
import doctest

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


class Frame:
    def __init__(self):
        self.mappings = {}
        self.parent = None
        self.name = "default"

    def __getitem__(self, key):
        if isinstance(key, str):
            try:
                return self.mappings[key]
            except:
                if self.parent == None:
                    raise SchemeNameError
                return self.parent[key]
        else:
            return key

    def __setitem__(self, key, val):
        self.mappings[key] = val

    def __contains__(self, val):
        if val in self.mappings:
            return True
        else:
            if self.parent != None:
                return val in self.parent
            else:
                return False

    def set_parent(self, val):
        self.parent = val

    def get_parent(self):
        return self.parent

    def set_map(self, val):
        self.mappings = val

    def get_map(self):
        return self.mappings

    def set_name(self, val):
        self.name = val

    def get_name(self):
        return self.name


class Function:
    def __init__(self, frame, expression, args) -> None:
        self.args = args
        self.expression = expression
        self.frame = frame

    def __call__(self, args):
        if len(args) != len(self.args):
            raise SchemeEvaluationError
        calling_frame = Frame()
        calling_frame.set_parent(self.frame)
        for arg_1, arg_2 in zip(self.args, args):
            calling_frame[arg_1] = arg_2
        return evaluate(self.expression, calling_frame)


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
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    token = list(source)
    new_token = []
    temp_str = ""
    next_line = False
    for entry in token:
        if entry == "\n":
            next_line = False
            if temp_str != "":
                new_token.append(temp_str)
            temp_str = ""
            continue
        if next_line:
            continue
        if entry == "(":
            if temp_str != "":
                new_token.append(temp_str)
            temp_str = ""
            new_token.append(entry)
            continue
        if entry == ")":
            if temp_str != "":
                new_token.append(temp_str)
            temp_str = ""
            new_token.append(entry)
            continue
        if entry == ";":
            next_line = True
            continue
        if entry != " ":
            temp_str += entry
            continue
        if temp_str != "":
            new_token.append(temp_str)
            temp_str = ""
    if temp_str != "":
        new_token.append(temp_str)
    return new_token


def find_matching_parentheses(tokens):
    stack = []
    matches = {}

    for i, token in enumerate(tokens):
        if token == "(":
            stack.append(i)
        elif token == ")":
            if len(stack) == 0:
                raise SchemeSyntaxError
            else:
                matches[stack.pop()] = i

    if len(stack) > 0:
        raise SchemeSyntaxError

    return matches


def get_last_parenthesis(tokens):
    matchings = find_matching_parentheses(tokens)
    if not matchings:
        raise SchemeSyntaxError
    return matchings[min(matchings)]


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if len(tokens) == 1 and tokens[0] != "(" and tokens[0] != ")":
        return number_or_symbol(tokens[0])
    if get_last_parenthesis(tokens) != len(tokens) - 1:
        raise SchemeSyntaxError

    def parse_expression(index):
        if index >= len(tokens):
            return []
        if tokens[index] == "(":
            group = []
            other_paren_index = find_matching_parentheses(tokens)[index]
            return [group + parse_expression(index + 1)] + parse_expression(
                other_paren_index + 1
            )
        if tokens[index] == ")":
            return []

        return [number_or_symbol(tokens[index])] + parse_expression(index + 1)

    parsed_expression = parse_expression(0)
    return parsed_expression[0]


######################
# Built-in Functions #
######################


def multiply(args):
    if not args:
        return 1
    return args[0] * multiply(args[1:])


def divide(args):
    return args[0] / multiply(args[1:])


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide,
}


#############
# Evaluation
##############


def result_and_frame(tree, frame=None):
    if frame == None:
        frame = Frame()
        frame.set_map(scheme_builtins.copy())

    return (evaluate(tree, frame), frame)


def evaluate(tree, frame=None, f_defined=False):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame == None:
        frame = Frame()
        frame.set_map(scheme_builtins.copy())
    if not isinstance(tree, list):
        return frame[tree]
    else:  # If Input is a list
        if not tree:
            raise SchemeEvaluationError
        if tree[0] == "define":
            name = tree[1]
            if isinstance(name, list):
                equivalence = ["define", name[0], ["lambda", name[1:], tree[2]]]
                val = evaluate(equivalence, frame)
                return val
            val = evaluate(tree[2], frame)
            frame[name] = val
            return val
        if tree[0] == "lambda":
            args = tree[1]
            expression = tree[2]
            return Function(frame, expression, args)
        func = evaluate(tree[0], frame)
        if not callable(func):
            raise SchemeEvaluationError
        args = tree[1:]
        args = [evaluate(arg, frame) for arg in args]
        return func(args)


def repl(verbose=False):
    """
    Read in a single line of user input, evaluate the expression, and print
    out the result. Repeat until user inputs "QUIT"

    Arguments:
        verbose: optional argument, if True will display tokens and parsed
            expression in addition to more detailed error output.
    """
    import traceback

    _, frame = result_and_frame(["+"])  # make a global frame
    while True:
        input_str = input("in> ")
        if input_str == "QUIT":
            return
        try:
            token_list = tokenize(input_str)
            if verbose:
                print("tokens>", token_list)
            expression = parse(token_list)
            if verbose:
                print("expression>", expression)
            output, frame = result_and_frame(expression, frame)
            print("  out>", output)
        except SchemeError as e:
            if verbose:
                traceback.print_tb(e.__traceback__)
            print("Error>", repr(e))


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    # repl(True)
    # print(type(sum))
    frame = Frame()
    frame.set_map(scheme_builtins)
    print(
        "1:",
        result_and_frame(
            ["define", "addN", ["lambda", ["n"], ["lambda", ["i"], ["+", "i", "n"]]]],
            frame,
        ),
    )
    print("2:", result_and_frame(["define", "add7", ["addN", 7]], frame))
    print("5:", result_and_frame(["add7", [["addN", 3], 3]]), frame)
    # print(evaluate(["add7", 30], frame))
    # print("2:",result_and_frame(['define', 'add7', ['addN', 7]], frame))
    # print("3:",result_and_frame(['add7', 2], frame))
    # print("4:",result_and_frame(['add7', [['addN', 3], [['addN', 19], 8]]], frame))
    # func_call = result_and_frame(['define', 'square', ['lambda', ['x'], ['*', 'x', 'x']]])
    # print(func_call[0])
    # print(func_call[1].get_map())
    # print(result_and_frame(['square', 21], func_call[1]))
    #
    pass
