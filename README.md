# 6.1010 Spring '23 Lab 11: LISP Interpreter

This project implements a LISP interpreter in Python, encompassing both Part 1 (basic framework) and Part 2 (extended functionality).

## Project Structure

### Scheme-related Exceptions
- **SchemeError**: Base class for all scheme-related exceptions.
- **SchemeSyntaxError**: Indicates a syntax error.
- **SchemeNameError**: Indicates an undefined name.
- **SchemeEvaluationError**: Indicates an error during evaluation.

### Core Classes
- **Frame**: Represents a frame in the LISP environment.
- **Function**: Represents a LISP function.
- **Pair**: Represents a pair (cons cell) in LISP.

### Tokenization and Parsing
- `number_or_symbol(value)`: Converts a string to a number if possible.
- `tokenize(source)`: Splits an input string into tokens.
- `find_matching_parentheses(tokens)`: Finds matching parentheses in tokens.
- `get_last_parenthesis(tokens)`: Gets the index of the last closing parenthesis.
- `parse(tokens)`: Parses tokens into a LISP expression.

### Built-in Functions
- **Basic arithmetic**: `+`, `-`, `*`, `/`
- **Comparison**: `equal?`, `>`, `>=`, `<`, `<=`
- **Boolean**: `#t`, `#f`, `not`
- **Pairs and lists**: `cons`, `car`, `cdr`, `nil`, `list`, `list?`, `length`, `list-ref`, `append`
- **Special forms**: `begin`, `and`, `or`, `if`, `cond`, `define`, `lambda`, `let`, `set!`
- **Higher-order functions**: `map`, `filter`, `reduce`
- **File operations**: `evaluate_file`

### Evaluation
- `result_and_frame(tree, frame=None)`: Evaluates an expression in a frame.
- `evaluate(tree, frame=None)`: Core evaluation function.
- `repl(verbose=False)`: Read-Eval-Print Loop for interactive use.

## Usage

### Running the Interpreter
Run the interpreter using:
```bash
python3 lab11.py