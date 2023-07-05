#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# "Fuzzing with Grammars" - a chapter of "The Fuzzing Book"
# Web site: https://www.fuzzingbook.org/html/Grammars.html
# Last change: 2023-01-07 15:15:27+01:00
#
# Copyright (c) 2021-2023 CISPA Helmholtz Center for Information Security
# Copyright (c) 2018-2020 Saarland University, authors, and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from typing import List, Dict, Union, Any, Tuple, Optional

from . import Fuzzer
## Representing Grammars in Python
## -------------------------------


Grammar = Dict[str, List[Expansion]]


SimpleGrammar = Dict[str, List[str]]

Option = Dict[str, Any]

Expansion = Union[str, Tuple[str, Option]]




Grammar = Dict[str, List[Expansion]]

EXPR_GRAMMAR: Grammar = {
    "<start>":
        ["<expr>"],

    "<expr>":
        ["<term> + <expr>", "<term> - <expr>", "<term>"],

    "<term>":
        ["<factor> * <term>", "<factor> / <term>", "<factor>"],

    "<factor>":
        ["+<factor>",
         "-<factor>",
         "(<expr>)",
         "<integer>.<integer>",
         "<integer>"],

    "<integer>":
        ["<digit><integer>", "<digit>"],

    "<digit>":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}






START_SYMBOL = "<start>"

import re #regular expressions 

RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')

def nonterminals(expansion):
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return RE_NONTERMINAL.findall(expansion)

def is_nonterminal(s):
    return RE_NONTERMINAL.match(s)





import random

class ExpansionError(Exception):
    pass

def simple_grammar_fuzzer(grammar: Grammar, 
                          start_symbol: str = START_SYMBOL,
                          max_nonterminals: int = 10,
                          max_expansion_trials: int = 100,
                          log: bool = False) -> str:
    """Produce a string from `grammar`.
       `start_symbol`: use a start symbol other than `<start>` (default).
       `max_nonterminals`: the maximum number of nonterminals 
         still left for expansion
       `max_expansion_trials`: maximum # of attempts to produce a string
       `log`: print expansion progress if True"""

    term = start_symbol
    expansion_trials = 0

    while len(nonterminals(term)) > 0:
        symbol_to_expand = random.choice(nonterminals(term))
        expansions = grammar[symbol_to_expand]
        expansion = random.choice(expansions)
        # In later chapters, we allow expansions to be tuples,
        # with the expansion being the first element
        if isinstance(expansion, tuple):
            expansion = expansion[0]

        new_term = term.replace(symbol_to_expand, expansion, 1)

        if len(nonterminals(new_term)) < max_nonterminals:
            term = new_term
            if log:
                print("%-40s" % (symbol_to_expand + " -> " + expansion), term)
            expansion_trials = 0
        else:
            expansion_trials += 1
            if expansion_trials >= max_expansion_trials:
                raise ExpansionError("Cannot expand " + repr(term))

    return term



## Visualizing Grammars as Railroad Diagrams
## -----------------------------------------



from .RailroadDiagrams import NonTerminal, Terminal, Choice, HorizontalChoice, Sequence
from .RailroadDiagrams import show_diagram

if __name__ == '__main__':
    from IPython.display import SVG

def syntax_diagram_symbol(symbol: str) -> Any:
    if is_nonterminal(symbol):
        return NonTerminal(symbol[1:-1])
    else:
        return Terminal(symbol)


def syntax_diagram_expr(expansion: Expansion) -> Any:
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    symbols = [sym for sym in re.split(RE_NONTERMINAL, expansion) if sym != ""]
    if len(symbols) == 0:
        symbols = [""]  # special case: empty expansion

    return Sequence(*[syntax_diagram_symbol(sym) for sym in symbols])


from itertools import zip_longest

def syntax_diagram_alt(alt: List[Expansion]) -> Any:
    max_len = 5
    alt_len = len(alt)
    if alt_len > max_len:
        iter_len = alt_len // max_len
        alts = list(zip_longest(*[alt[i::iter_len] for i in range(iter_len)]))
        exprs = [[syntax_diagram_expr(expr) for expr in alt
                  if expr is not None] for alt in alts]
        choices = [Choice(len(expr) // 2, *expr) for expr in exprs]
        return HorizontalChoice(*choices)
    else:
        return Choice(alt_len // 2, *[syntax_diagram_expr(expr) for expr in alt])

if __name__ == '__main__':
    SVG(show_diagram(syntax_diagram_alt(EXPR_GRAMMAR['<digit>'])))

def syntax_diagram(grammar: Grammar) -> None:
    from IPython.display import SVG, display

    for key in grammar:
        print("%s" % key[1:-1])
        display(SVG(show_diagram(syntax_diagram_alt(grammar[key]))))



### A URL Grammar





URL_GRAMMAR: Grammar = {
    "<start>":
        ["<url>"],
    "<url>":
        ["<scheme>://<authority><path><query>"],
    "<scheme>":
        ["http", "https", "ftp", "ftps"],
    "<authority>":
        ["<host>", "<host>:<port>", "<userinfo>@<host>", "<userinfo>@<host>:<port>"],
    "<host>":  # Just a few
        ["cispa.saarland", "www.google.com", "fuzzingbook.com"],
    "<port>":
        ["80", "8080", "<nat>"],
    "<nat>":
        ["<digit>", "<digit><digit>"],
    "<digit>":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    "<userinfo>":  # Just one
        ["user:password"],
    "<path>":  # Just a few
        ["", "/", "/<id>"],
    "<id>":  # Just a few
        ["abc", "def", "x<digit><digit>"],
    "<query>":
        ["", "?<params>"],
    "<params>":
        ["<param>", "<param>&<params>"],
    "<param>":  # Just a few
        ["<id>=<id>", "<id>=<nat>"],
}


    syntax_diagram(URL_GRAMMAR)

#Example Grammar as seeds
from typing import Set


from MutationFuzzer import MutationFuzzer  # minor dependency

    number_of_seeds = 10
    seeds = [
        simple_grammar_fuzzer(
            grammar=URL_GRAMMAR,
            max_nonterminals=10) for i in range(number_of_seeds)]
    seeds

    m = MutationFuzzer(seeds)


## A Grammar Toolbox
### Escapes



if __name__ == '__main__':
    simple_nonterminal_grammar: Grammar = {
        "<start>": ["<nonterminal>"],
        "<nonterminal>": ["<left-angle><identifier><right-angle>"],
        "<left-angle>": ["<"],
        "<right-angle>": [">"],
        "<identifier>": ["id"]  # for now
    }

### Extending Grammars

import copy

def extend_grammar(grammar: Grammar, extension: Grammar = {}) -> Grammar:
    new_grammar = copy.deepcopy(grammar)
    new_grammar.update(extension)
    return new_grammar

### Character Classes


import string

def srange(characters: str) -> List[Expansion]:
    """Construct a list with all characters in the string"""
    return [c for c in characters]

def crange(character_start: str, character_end: str) -> List[Expansion]:
    return [chr(i)
            for i in range(ord(character_start), ord(character_end) + 1)]

### Grammar Shortcuts

if __name__ == '__main__':
    
    nonterminal_ebnf_grammar = extend_grammar(nonterminal_grammar,
                                              {
                                                  "<identifier>": ["<idchar>+"]
                                              }
                                              )

EXPR_EBNF_GRAMMAR: Grammar = {
    "<start>":
        ["<expr>"],

    "<expr>":
        ["<term> + <expr>", "<term> - <expr>", "<term>"],

    "<term>":
        ["<factor> * <term>", "<factor> / <term>", "<factor>"],

    "<factor>":
        ["<sign>?<factor>", "(<expr>)", "<integer>(.<integer>)?"],

    "<sign>":
        ["+", "-"],

    "<integer>":
        ["<digit>+"],

    "<digit>":
        srange(string.digits)
}

#### Excursion: Implementing `convert_ebnf_grammar()`

if __name__ == '__main__':
    print('\n#### Excursion: Implementing `convert_ebnf_grammar()`')



##### Creating New Symbols

if __name__ == '__main__':
    print('\n##### Creating New Symbols')



def new_symbol(grammar: Grammar, symbol_name: str = "<symbol>") -> str:
    """Return a new symbol for `grammar` based on `symbol_name`"""
    if symbol_name not in grammar:
        return symbol_name

    count = 1
    while True:
        tentative_symbol_name = symbol_name[:-1] + "-" + repr(count) + ">"
        if tentative_symbol_name not in grammar:
            return tentative_symbol_name
        count += 1

if __name__ == '__main__':
    assert new_symbol(EXPR_EBNF_GRAMMAR, '<expr>') == '<expr-1>'

##### Expanding Parenthesized Expressions

if __name__ == '__main__':
    print('\n##### Expanding Parenthesized Expressions')



RE_PARENTHESIZED_EXPR = re.compile(r'\([^()]*\)[?+*]')

def parenthesized_expressions(expansion: Expansion) -> List[str]:
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return re.findall(RE_PARENTHESIZED_EXPR, expansion)

if __name__ == '__main__':
    assert parenthesized_expressions("(<foo>)* (<foo><bar>)+ (+<foo>)? <integer>(.<integer>)?") == [
        '(<foo>)*', '(<foo><bar>)+', '(+<foo>)?', '(.<integer>)?']

def convert_ebnf_parentheses(ebnf_grammar: Grammar) -> Grammar:
    """Convert a grammar in extended BNF to BNF"""
    grammar = extend_grammar(ebnf_grammar)
    for nonterminal in ebnf_grammar:
        expansions = ebnf_grammar[nonterminal]

        for i in range(len(expansions)):
            expansion = expansions[i]
            if not isinstance(expansion, str):
                expansion = expansion[0]

            while True:
                parenthesized_exprs = parenthesized_expressions(expansion)
                if len(parenthesized_exprs) == 0:
                    break

                for expr in parenthesized_exprs:
                    operator = expr[-1:]
                    contents = expr[1:-2]

                    new_sym = new_symbol(grammar)

                    exp = grammar[nonterminal][i]
                    opts = None
                    if isinstance(exp, tuple):
                        (exp, opts) = exp
                    assert isinstance(exp, str)

                    expansion = exp.replace(expr, new_sym + operator, 1)
                    if opts:
                        grammar[nonterminal][i] = (expansion, opts)
                    else:
                        grammar[nonterminal][i] = expansion

                    grammar[new_sym] = [contents]

    return grammar

if __name__ == '__main__':
    convert_ebnf_parentheses({"<number>": ["<integer>(.<integer>)?"]})

if __name__ == '__main__':
    convert_ebnf_parentheses({"<foo>": ["((<foo>)?)+"]})

##### Expanding Operators

if __name__ == '__main__':
    print('\n##### Expanding Operators')



RE_EXTENDED_NONTERMINAL = re.compile(r'(<[^<> ]*>[?+*])')

def extended_nonterminals(expansion: Expansion) -> List[str]:
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return re.findall(RE_EXTENDED_NONTERMINAL, expansion)

if __name__ == '__main__':
    assert extended_nonterminals(
        "<foo>* <bar>+ <elem>? <none>") == ['<foo>*', '<bar>+', '<elem>?']

def convert_ebnf_operators(ebnf_grammar: Grammar) -> Grammar:
    """Convert a grammar in extended BNF to BNF"""
    grammar = extend_grammar(ebnf_grammar)
    for nonterminal in ebnf_grammar:
        expansions = ebnf_grammar[nonterminal]

        for i in range(len(expansions)):
            expansion = expansions[i]
            extended_symbols = extended_nonterminals(expansion)

            for extended_symbol in extended_symbols:
                operator = extended_symbol[-1:]
                original_symbol = extended_symbol[:-1]
                assert original_symbol in ebnf_grammar, \
                    f"{original_symbol} is not defined in grammar"

                new_sym = new_symbol(grammar, original_symbol)

                exp = grammar[nonterminal][i]
                opts = None
                if isinstance(exp, tuple):
                    (exp, opts) = exp
                assert isinstance(exp, str)

                new_exp = exp.replace(extended_symbol, new_sym, 1)
                if opts:
                    grammar[nonterminal][i] = (new_exp, opts)
                else:
                    grammar[nonterminal][i] = new_exp

                if operator == '?':
                    grammar[new_sym] = ["", original_symbol]
                elif operator == '*':
                    grammar[new_sym] = ["", original_symbol + new_sym]
                elif operator == '+':
                    grammar[new_sym] = [
                        original_symbol, original_symbol + new_sym]

    return grammar

if __name__ == '__main__':
    convert_ebnf_operators({"<integer>": ["<digit>+"], "<digit>": ["0"]})

##### All Together

if __name__ == '__main__':
    print('\n##### All Together')



def convert_ebnf_grammar(ebnf_grammar: Grammar) -> Grammar:
    return convert_ebnf_operators(convert_ebnf_parentheses(ebnf_grammar))

#### End of Excursion

if __name__ == '__main__':
    print('\n#### End of Excursion')



if __name__ == '__main__':
    convert_ebnf_grammar({"<authority>": ["(<userinfo>@)?<host>(:<port>)?"]})

if __name__ == '__main__':
    expr_grammar = convert_ebnf_grammar(EXPR_EBNF_GRAMMAR)
    expr_grammar

### Grammar Extensions

if __name__ == '__main__':
    print('\n### Grammar Extensions')



#### Excursion: Implementing `opts()`

if __name__ == '__main__':
    print('\n#### Excursion: Implementing `opts()`')



def opts(**kwargs: Any) -> Dict[str, Any]:
    return kwargs

if __name__ == '__main__':
    opts(min_depth=10)

def exp_string(expansion: Expansion) -> str:
    """Return the string to be expanded"""
    if isinstance(expansion, str):
        return expansion
    return expansion[0]

if __name__ == '__main__':
    exp_string(("<term> + <expr>", opts(min_depth=10)))

def exp_opts(expansion: Expansion) -> Dict[str, Any]:
    """Return the options of an expansion.  If options are not defined, return {}"""
    if isinstance(expansion, str):
        return {}
    return expansion[1]

def exp_opt(expansion: Expansion, attribute: str) -> Any:
    """Return the given attribution of an expansion.
    If attribute is not defined, return None"""
    return exp_opts(expansion).get(attribute, None)

if __name__ == '__main__':
    exp_opts(("<term> + <expr>", opts(min_depth=10)))

if __name__ == '__main__':
    exp_opt(("<term> - <expr>", opts(max_depth=2)), 'max_depth')

def set_opts(grammar: Grammar, symbol: str, expansion: Expansion, 
             opts: Option = {}) -> None:
    """Set the options of the given expansion of grammar[symbol] to opts"""
    expansions = grammar[symbol]
    for i, exp in enumerate(expansions):
        if exp_string(exp) != exp_string(expansion):
            continue

        new_opts = exp_opts(exp)
        if opts == {} or new_opts == {}:
            new_opts = opts
        else:
            for key in opts:
                new_opts[key] = opts[key]

        if new_opts == {}:
            grammar[symbol][i] = exp_string(exp)
        else:
            grammar[symbol][i] = (exp_string(exp), new_opts)

        return

    raise KeyError(
        "no expansion " +
        repr(symbol) +
        " -> " +
        repr(
            exp_string(expansion)))

#### End of Excursion

if __name__ == '__main__':
    print('\n#### End of Excursion')



## Checking Grammars
## -----------------

if __name__ == '__main__':
    print('\n## Checking Grammars')



### Excursion: Implementing `is_valid_grammar()`

if __name__ == '__main__':
    print('\n### Excursion: Implementing `is_valid_grammar()`')



import sys

def def_used_nonterminals(grammar: Grammar, start_symbol: 
                          str = START_SYMBOL) -> Tuple[Optional[Set[str]], 
                                                       Optional[Set[str]]]:
    """Return a pair (`defined_nonterminals`, `used_nonterminals`) in `grammar`.
    In case of error, return (`None`, `None`)."""

    defined_nonterminals = set()
    used_nonterminals = {start_symbol}

    for defined_nonterminal in grammar:
        defined_nonterminals.add(defined_nonterminal)
        expansions = grammar[defined_nonterminal]
        if not isinstance(expansions, list):
            print(repr(defined_nonterminal) + ": expansion is not a list",
                  file=sys.stderr)
            return None, None

        if len(expansions) == 0:
            print(repr(defined_nonterminal) + ": expansion list empty",
                  file=sys.stderr)
            return None, None

        for expansion in expansions:
            if isinstance(expansion, tuple):
                expansion = expansion[0]
            if not isinstance(expansion, str):
                print(repr(defined_nonterminal) + ": "
                      + repr(expansion) + ": not a string",
                      file=sys.stderr)
                return None, None

            for used_nonterminal in nonterminals(expansion):
                used_nonterminals.add(used_nonterminal)

    return defined_nonterminals, used_nonterminals

def reachable_nonterminals(grammar: Grammar,
                           start_symbol: str = START_SYMBOL) -> Set[str]:
    reachable = set()

    def _find_reachable_nonterminals(grammar, symbol):
        nonlocal reachable
        reachable.add(symbol)
        for expansion in grammar.get(symbol, []):
            for nonterminal in nonterminals(expansion):
                if nonterminal not in reachable:
                    _find_reachable_nonterminals(grammar, nonterminal)

    _find_reachable_nonterminals(grammar, start_symbol)
    return reachable

def unreachable_nonterminals(grammar: Grammar,
                             start_symbol=START_SYMBOL) -> Set[str]:
    return grammar.keys() - reachable_nonterminals(grammar, start_symbol)

def opts_used(grammar: Grammar) -> Set[str]:
    used_opts = set()
    for symbol in grammar:
        for expansion in grammar[symbol]:
            used_opts |= set(exp_opts(expansion).keys())
    return used_opts

def is_valid_grammar(grammar: Grammar,
                     start_symbol: str = START_SYMBOL, 
                     supported_opts: Set[str] = set()) -> bool:
    """Check if the given `grammar` is valid.
       `start_symbol`: optional start symbol (default: `<start>`)
       `supported_opts`: options supported (default: none)"""

    defined_nonterminals, used_nonterminals = \
        def_used_nonterminals(grammar, start_symbol)
    if defined_nonterminals is None or used_nonterminals is None:
        return False

    # Do not complain about '<start>' being not used,
    # even if start_symbol is different
    if START_SYMBOL in grammar:
        used_nonterminals.add(START_SYMBOL)

    for unused_nonterminal in defined_nonterminals - used_nonterminals:
        print(repr(unused_nonterminal) + ": defined, but not used",
              file=sys.stderr)
    for undefined_nonterminal in used_nonterminals - defined_nonterminals:
        print(repr(undefined_nonterminal) + ": used, but not defined",
              file=sys.stderr)

    # Symbols must be reachable either from <start> or given start symbol
    unreachable = unreachable_nonterminals(grammar, start_symbol)
    msg_start_symbol = start_symbol

    if START_SYMBOL in grammar:
        unreachable = unreachable - \
            reachable_nonterminals(grammar, START_SYMBOL)
        if start_symbol != START_SYMBOL:
            msg_start_symbol += " or " + START_SYMBOL

    for unreachable_nonterminal in unreachable:
        print(repr(unreachable_nonterminal) + ": unreachable from " + msg_start_symbol,
              file=sys.stderr)

    used_but_not_supported_opts = set()
    if len(supported_opts) > 0:
        used_but_not_supported_opts = opts_used(
            grammar).difference(supported_opts)
        for opt in used_but_not_supported_opts:
            print(
                "warning: option " +
                repr(opt) +
                " is not supported",
                file=sys.stderr)

    return used_nonterminals == defined_nonterminals and len(unreachable) == 0

### End of Excursion

if __name__ == '__main__':
    print('\n### End of Excursion')



if __name__ == '__main__':
    assert is_valid_grammar(EXPR_GRAMMAR)
    assert is_valid_grammar(CGI_GRAMMAR)
    assert is_valid_grammar(URL_GRAMMAR)

if __name__ == '__main__':
    assert is_valid_grammar(EXPR_EBNF_GRAMMAR)

if __name__ == '__main__':
    assert not is_valid_grammar({"<start>": ["<x>"], "<y>": ["1"]})  # type: ignore

if __name__ == '__main__':
    assert not is_valid_grammar({"<start>": "123"})  # type: ignore

if __name__ == '__main__':
    assert not is_valid_grammar({"<start>": []})  # type: ignore

if __name__ == '__main__':
    assert not is_valid_grammar({"<start>": [1, 2, 3]})  # type: ignore

## Synopsis
## --------

if __name__ == '__main__':
    print('\n## Synopsis')



US_PHONE_GRAMMAR: Grammar = {
    "<start>": ["<phone-number>"],
    "<phone-number>": ["(<area>)<exchange>-<line>"],
    "<area>": ["<lead-digit><digit><digit>"],
    "<exchange>": ["<lead-digit><digit><digit>"],
    "<line>": ["<digit><digit><digit><digit>"],
    "<lead-digit>": ["2", "3", "4", "5", "6", "7", "8", "9"],
    "<digit>": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}

assert is_valid_grammar(US_PHONE_GRAMMAR)

if __name__ == '__main__':
    [simple_grammar_fuzzer(US_PHONE_GRAMMAR) for i in range(5)]

## Lessons Learned
## ---------------

if __name__ == '__main__':
    print('\n## Lessons Learned')



## Next Steps
## ----------

if __name__ == '__main__':
    print('\n## Next Steps')



## Background
## ----------

if __name__ == '__main__':
    print('\n## Background')



## Exercises
## ---------

if __name__ == '__main__':
    print('\n## Exercises')



### Exercise 1: A JSON Grammar

if __name__ == '__main__':
    print('\n### Exercise 1: A JSON Grammar')



CHARACTERS_WITHOUT_QUOTE = (string.digits
                            + string.ascii_letters
                            + string.punctuation.replace('"', '').replace('\\', '')
                            + ' ')

JSON_EBNF_GRAMMAR: Grammar = {
    "<start>": ["<json>"],

    "<json>": ["<element>"],

    "<element>": ["<ws><value><ws>"],

    "<value>": ["<object>", "<array>", "<string>", "<number>",
                "true", "false", "null", "'; DROP TABLE STUDENTS"],

    "<object>": ["{<ws>}", "{<members>}"],

    "<members>": ["<member>(,<members>)*"],

    "<member>": ["<ws><string><ws>:<element>"],

    "<array>": ["[<ws>]", "[<elements>]"],

    "<elements>": ["<element>(,<elements>)*"],

    "<element>": ["<ws><value><ws>"],

    "<string>": ['"' + "<characters>" + '"'],
    
    "<characters>": ["<character>*"],

    "<character>": srange(CHARACTERS_WITHOUT_QUOTE),

    "<number>": ["<int><frac><exp>"],

    "<int>": ["<digit>", "<onenine><digits>", "-<digit>", "-<onenine><digits>"],

    "<digits>": ["<digit>+"],

    "<digit>": ['0', "<onenine>"],

    "<onenine>": crange('1', '9'),

    "<frac>": ["", ".<digits>"],

    "<exp>": ["", "E<sign><digits>", "e<sign><digits>"],

    "<sign>": ["", '+', '-'],

    # "<ws>": srange(string.whitespace)

    "<ws>": [" "]
}

assert is_valid_grammar(JSON_EBNF_GRAMMAR)

JSON_GRAMMAR = convert_ebnf_grammar(JSON_EBNF_GRAMMAR)

from .ExpectError import ExpectError

if __name__ == '__main__':
    for i in range(50):
        with ExpectError():
            print(simple_grammar_fuzzer(JSON_GRAMMAR, '<object>'))

### Exercise 2: Finding Bugs

if __name__ == '__main__':
    print('\n### Exercise 2: Finding Bugs')



from .ExpectError import ExpectError, ExpectTimeout

if __name__ == '__main__':
    with ExpectError():
        simple_grammar_fuzzer(nonterminal_grammar, log=True)

if __name__ == '__main__':
    with ExpectTimeout(1):
        for i in range(10):
            print(simple_grammar_fuzzer(expr_grammar))

### Exercise 3: Grammars with Regular Expressions

if __name__ == '__main__':
    print('\n### Exercise 3: Grammars with Regular Expressions')



#### Part 1: Convert regular expressions

if __name__ == '__main__':
    print('\n#### Part 1: Convert regular expressions')



#### Part 2: Identify and expand regular expressions

if __name__ == '__main__':
    print('\n#### Part 2: Identify and expand regular expressions')



### Exercise 4: Defining Grammars as Functions (Advanced)

if __name__ == '__main__':
    print('\n### Exercise 4: Defining Grammars as Functions (Advanced)')



def expression_grammar_fn():
    start = "<expr>"
    expr = "<term> + <expr>" | "<term> - <expr>"
    term = "<factor> * <term>" | "<factor> / <term>" | "<factor>"
    factor = "+<factor>" | "-<factor>" | "(<expr>)" | "<integer>.<integer>" | "<integer>"
    integer = "<digit><integer>" | "<digit>"
    digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'

if __name__ == '__main__':
    with ExpectError():
        expression_grammar_fn()

import ast
import inspect

if __name__ == '__main__':
    source = inspect.getsource(expression_grammar_fn)
    source

if __name__ == '__main__':
    tree = ast.parse(source)

def get_alternatives(op, to_expr=lambda o: o.s):
    if isinstance(op, ast.BinOp) and isinstance(op.op, ast.BitOr):
        return get_alternatives(op.left, to_expr) + [to_expr(op.right)]
    return [to_expr(op)]

def funct_parser(tree, to_expr=lambda o: o.s):
    return {assign.targets[0].id: get_alternatives(assign.value, to_expr)
            for assign in tree.body[0].body}

if __name__ == '__main__':
    grammar = funct_parser(tree)
    for symbol in grammar:
        print(symbol, "::=", grammar[symbol])

#### Part 1 (a): One Single Function

if __name__ == '__main__':
    print('\n#### Part 1 (a): One Single Function')



def define_grammar(fn, to_expr=lambda o: o.s):
    source = inspect.getsource(fn)
    tree = ast.parse(source)
    grammar = funct_parser(tree, to_expr)
    return grammar

if __name__ == '__main__':
    define_grammar(expression_grammar_fn)

#### Part 1 (b): Alternative representations

if __name__ == '__main__':
    print('\n#### Part 1 (b): Alternative representations')



def define_name(o):
    return o.id if isinstance(o, ast.Name) else o.s

def define_expr(op):
    if isinstance(op, ast.BinOp) and isinstance(op.op, ast.Add):
        return (*define_expr(op.left), define_name(op.right))
    return (define_name(op),)

def define_ex_grammar(fn):
    return define_grammar(fn, define_expr)

#### Part 2: Extended Grammars

if __name__ == '__main__':
    print('\n#### Part 2: Extended Grammars')



def identifier_grammar_fn():
    identifier = idchar * (1,)
