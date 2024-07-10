6.1010 Spring '23 Lab 11: LISP Interpreter
This project implements a LISP interpreter in Python, covering both Part 1 (basic framework) and Part 2 (extended functionality).

Project Structure
Scheme-related Exceptions:

SchemeError (base class)
SchemeSyntaxError
SchemeNameError
SchemeEvaluationError
Core Classes:

Frame: Represents a frame in the LISP environment.
Function: Represents a LISP function.
Pair: Represents a pair (cons cell) in LISP.
Tokenization and Parsing:

number_or_symbol(value): Converts string to number if possible.
tokenize(source): Splits input string into tokens.
find_matching_parentheses(tokens): Finds matching parentheses.
get_last_parenthesis(tokens): Gets the index of the last closing parenthesis.
parse(tokens): Parses tokens into a LISP expression.
Built-in Functions:

Basic arithmetic: +, -, *, /
Comparison: equal?, >, >=, <, <=
Boolean: #t, #f, not
Pairs and lists: cons, car, cdr, nil, list, list?, length, list-ref, append
Special forms: begin, and, or, if, cond, define, lambda, let, set!
Higher-order functions: map, filter, reduce
File operations: evaluate_file
Evaluation:

result_and_frame(tree, frame=None): Evaluates an expression in a frame.
evaluate(tree, frame=None): Core evaluation function.
repl(verbose=False): Read-Eval-Print Loop for interactive use.
Usage
Running the interpreter:
Bash
python3 lab11.py 
Use code with caution.
content_copy
REPL mode: Enter LISP expressions at the in> prompt.
Running LISP files: Pass filenames as arguments:
Bash
python3 lab11.py my_lisp_file.scm
Use code with caution.
content_copy
Features (Part 2)
Special Forms:

and, or, if, cond: Control flow and conditional evaluation.
define, lambda: Function definition and lambda expressions.
let, set!: Local bindings and variable assignment.
Pairs and Lists: Operations for constructing, accessing, and manipulating pairs and lists.

Higher-Order Functions: map, filter, reduce for functional programming.

File Evaluation: evaluate_file for evaluating LISP code from files.

Examples
Lisp
(define (factorial n)
  (if (<= n 1)
      1
      (* n (factorial (- n 1)))))

(factorial 5) ; Evaluates to 120

(define (map f l)
  (if (null? l)
      nil
      (cons (f (car l)) (map f (cdr l)))))

(map (lambda (x) (* x x)) '(1 2 3 4)) ; Evaluates to (1 4 9 16)
Use code with caution.
content_copy
Key Improvements from Part 1
Added support for special forms, enabling more complex LISP programs.
Implemented pairs and lists, allowing for data structures and recursion.
Introduced higher-order functions for greater expressiveness.
Added file evaluation for running LISP code from external files.