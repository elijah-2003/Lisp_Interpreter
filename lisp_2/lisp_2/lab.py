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

    def __delitem__(self, val):
        try:
            del self.mappings[val]
        except:
            raise SchemeEvaluationError

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

    def get_parent_from_key(self, key):
        if isinstance(key, str):
            try:
                self.mappings[key]
                return self
            except:
                if self.parent == None:
                    raise SchemeNameError
                return self.parent.get_parent_from_key(key)
        else:
            return key


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


class Pair:
    def __init__(self, car, cdr) -> None:
        self.car = car
        self.cdr = cdr

    def get_car(self):
        return self.car

    def get_cdr(self):
        return self.cdr

    def __len__(self):
        # Scheme error cases
        if self.cdr != None and not isinstance(self.cdr, Pair):
            raise SchemeEvaluationError
        if not isinstance(self.cdr, Pair):
            return 1
        return 1 + len(self.cdr)

    def __str__(self):
        def recursive_str(self):
            if self.cdr == None:
                return [self.car]
            return [self.car] + recursive_str(self.cdr)

        return str(recursive_str(self))

    def __getitem__(self, index):
        if index == 0:
            return self.car
        if isinstance(self.cdr, Pair):
            return self.cdr[index - 1]
        raise SchemeEvaluationError

    def get_pair(self, index):
        if index == 0:
            return self
        if isinstance(self.cdr, Pair):
            return self.cdr.get_pair(index - 1)
        raise SchemeEvaluationError

    def deep_copy(self):
        if not isinstance(self.cdr, Pair):
            return Pair(self.car, self.cdr)
        return Pair(self.car, self.cdr.deep_copy())

    def append(self, args):
        self_copy = self.deep_copy()
        for arg in args:
            if arg is None:
                continue
            if not isinstance(arg, Pair):
                raise SchemeEvaluationError
            if not arg.is_list():
                raise SchemeEvaluationError
            self_copy.get_pair(len(self_copy) - 1).cdr = arg.deep_copy()
        return self_copy

    def is_list(self):
        try:
            last = self.get_pair(len(self) - 1)
        except:
            return False
        if last.cdr == None:
            return True
        return False


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


def equal(args):
    for i, arg_1 in enumerate(args):
        for arg_2 in args[i + 1 :]:
            if arg_1 != arg_2:
                return False
    return True


def decreasing(args):
    for i, arg_1 in enumerate(args):
        for arg_2 in args[i + 1 :]:
            if arg_1 <= arg_2:
                return False
    return True


def nonincreasing(args):
    for i, arg_1 in enumerate(args):
        for arg_2 in args[i + 1 :]:
            if arg_1 < arg_2:
                return False
    return True


def increasing(args):
    for i, arg_1 in enumerate(args):
        for arg_2 in args[i + 1 :]:
            if arg_1 >= arg_2:
                return False
    return True


def nondecreasing(args):
    for i, arg_1 in enumerate(args):
        for arg_2 in args[i + 1 :]:
            if arg_1 > arg_2:
                return False
    return True


def not_(args):
    if len(args) != 1:
        raise SchemeEvaluationError
    return not args[0]


def cons(args):
    if len(args) != 2:
        raise SchemeEvaluationError
    return Pair(args[0], args[1])


def car(args):
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].get_car()


def cdr(args):
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].get_cdr()


def make_list(args):
    if len(args) == 0:
        return None
    return cons([args[0], make_list(args[1:])])


def length(args):
    if not args:
        raise SchemeEvaluationError
    if args[0] is None:
        return 0
    if not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return len(args[0])


def get_index(args):
    if not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0][args[1]]


def append(args):
    if len(args) == 0:
        return None
    if args[0] is None:
        for i, arg in enumerate(args[1:]):
            if isinstance(arg, Pair):
                print(args)
                return arg.append(args[1:][i + 1 :])
        return None
    if not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].append(args[1:])


def evaluate_file(text, frame=None):
    file = open(text, mode="r")
    to_text = file.read()
    print("I'm read:", to_text)
    token = tokenize(to_text)
    parsed = parse(token)
    return evaluate(parsed, frame)


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide,
    "equal?": equal,
    ">": decreasing,
    ">=": nonincreasing,
    "<": increasing,
    "<=": nondecreasing,
    "#f": False,
    "#t": True,
    "not": not_,
    "cons": cons,
    "car": car,
    "cdr": cdr,
    "nil": None,
    "list": make_list,
    "list?": lambda l: len(l) == 1
    and (l[0] is None or (isinstance(l[0], Pair) and l[0].is_list())),
    "length": length,
    "list-ref": get_index,
    "append": append,
    "begin": lambda i: i[-1],
}


#############
# Evaluation
##############


def result_and_frame(tree, frame=None):
    if frame == None:
        frame = Frame()
        built_in_frame = Frame()
        built_in_frame.set_map(scheme_builtins.copy())
        frame.set_parent(built_in_frame)

    return (evaluate(tree, frame), frame)


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame == None:
        frame = Frame()
        built_in_frame = Frame()
        built_in_frame.set_map(scheme_builtins.copy())
        frame.set_parent(built_in_frame)
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
        if tree[0] == "and":
            for expression in tree[1:]:
                if not evaluate(expression, frame):
                    return False
            return True
        if tree[0] == "or":
            for expression in tree[1:]:
                if evaluate(expression, frame):
                    return True
            return False
        if tree[0] == "if":
            pred = tree[1]
            true_exp = tree[2]
            false_exp = tree[3]
            if evaluate(pred, frame):
                return evaluate(true_exp, frame)
            else:
                return evaluate(false_exp, frame)
        if tree[0] == "map":
            equivalence = ["list"]
            func = evaluate(tree[1], frame)
            if not callable(func):
                raise SchemeEvaluationError
            list_ = evaluate(tree[2], frame)
            if list_ is None:
                return None
            if not isinstance(list_, Pair):
                raise SchemeEvaluationError
            for index in range(len(list_)):
                equivalence += [func([list_[index]])]
            return evaluate(equivalence, frame)
        if tree[0] == "filter":
            equivalence = ["list"]
            func = evaluate(tree[1], frame)
            if not callable(func):
                raise SchemeEvaluationError
            list_ = evaluate(tree[2], frame)
            if list_ is None:
                return None
            if not isinstance(list_, Pair):
                raise SchemeEvaluationError
            for index in range(len(list_)):
                if func([list_[index]]):
                    equivalence += [list_[index]]
            return evaluate(equivalence, frame)
        if tree[0] == "reduce":
            equivalence = ["list"]
            func = evaluate(tree[1], frame)
            if not callable(func):
                raise SchemeEvaluationError
            list_ = evaluate(tree[2], frame)
            val = evaluate(tree[3], frame)
            if list_ is None:
                return val
            if not isinstance(list_, Pair):
                raise SchemeEvaluationError
            for index in range(len(list_)):
                val = func([val, list_[index]])
            return val
        if tree[0] == "del":
            try:
                val = frame.mappings[tree[1]]
            except:
                raise SchemeNameError
            del frame[tree[1]]
            return val
        if tree[0] == "let":
            new_frame = Frame()
            new_frame.set_parent(frame)
            temp_assignments = tree[1]
            for var, val in temp_assignments:
                evaluated = evaluate(val, frame)
                new_frame[var] = evaluated
            return evaluate(*tree[2:], new_frame)
        if tree[0] == "set!":
            parent = frame.get_parent_from_key(tree[1])
            parent[tree[1]] = evaluate(tree[2], frame)
            return parent[tree[1]]

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
    for arg in sys.argv[1:]:
        evaluate(arg, frame)
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
    # print(len(new_l))
    repl(True)
    # l = ["cons",9,["cons", 8, ["cons", 7, "nil"]]]
    # new_l = evaluate(l)
    # print(new_l.deep_copy())

    # print(type(sum))
