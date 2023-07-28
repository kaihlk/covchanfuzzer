#GeneratorGrammarFuzzer.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# "Fuzzing with Generators" - a chapter of "The Fuzzing Book"
# Web site: https://www.fuzzingbook.org/html/GeneratorGrammarFuzzer.html
# Last change: 2023-01-07 15:16:47+01:00
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

# Fuzzing with Generators
# =======================


## Example: Test a Credit Card System
## ----------------------------------


from typing import Callable, Set, List, Dict, Optional, Iterator, Any, Union, Tuple, cast

from .Fuzzer import Fuzzer

from .Grammars import EXPR_GRAMMAR, is_valid_grammar, is_nonterminal, extend_grammar
from .Grammars import opts, exp_opt, exp_string, crange, Grammar, Expansion

from .GrammarFuzzer import DerivationTree

CHARGE_GRAMMAR: Grammar = {
    "<start>": ["Charge <amount> to my credit card <credit-card-number>"],
    "<amount>": ["$<float>"],
    "<float>": ["<integer>.<digit><digit>"],
    "<integer>": ["<digit>", "<integer><digit>"],
    "<digit>": crange('0', '9'),

    "<credit-card-number>": ["<digits>"],
    "<digits>": ["<digit-block><digit-block><digit-block><digit-block>"],
    "<digit-block>": ["<digit><digit><digit><digit>"],
}


from .GrammarFuzzer import GrammarFuzzer, all_terminals

## Attaching Functions to Expansions
## ---------------------------------


### Functions Called Before Expansion

import random

def high_charge() -> float:
    return random.randint(10000000, 90000000) / 100.0

CHARGE_GRAMMAR.update({
    "<float>": [("<integer>.<digit><digit>", opts(pre=high_charge))],
})

def apply_twice(function, x):
    return function(function(x))

CHARGE_GRAMMAR.update({
    "<float>": [("<integer>.<digit><digit>",
                 opts(pre=lambda: random.randint(10000000, 90000000) / 100.0))]
})

### Functions Called After Expansion


CHARGE_GRAMMAR.update({
    "<credit-card-number>": [("<digits>", opts(post=lambda digits: check_credit_card(digits)))]
})

CHARGE_GRAMMAR.update({
    "<credit-card-number>": [("<digits>", opts(post=lambda digits: fix_credit_card(digits)))]
})

def luhn_checksum(s: str) -> int:
    """Compute Luhn's check digit over a string of digits"""
    LUHN_ODD_LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7,
                       9)  # sum_of_digits (index * 2)

    evens = sum(int(p) for p in s[-1::-2])
    odds = sum(LUHN_ODD_LOOKUP[int(p)] for p in s[-2::-2])
    return (evens + odds) % 10

def valid_luhn_checksum(s: str) -> bool:
    """Check whether the last digit is Luhn's checksum over the earlier digits"""
    return luhn_checksum(s[:-1]) == int(s[-1])

def fix_luhn_checksum(s: str) -> str:
    """Return the given string of digits, with a fixed check digit"""
    return s[:-1] + repr(luhn_checksum(s[:-1]))

## A Class for Integrating Constraints
## -----------------------------------


class GeneratorGrammarFuzzer(GrammarFuzzer):
    def supported_opts(self) -> Set[str]:
        return super().supported_opts() | {"pre", "post", "order"}

def exp_pre_expansion_function(expansion: Expansion) -> Optional[Callable]:
    """Return the specified pre-expansion function, or None if unspecified"""
    return exp_opt(expansion, 'pre')

def exp_post_expansion_function(expansion: Expansion) -> Optional[Callable]:
    """Return the specified post-expansion function, or None if unspecified"""
    return exp_opt(expansion, 'post')

## Generating Elements before Expansion
## ------------------------------------


import inspect

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def process_chosen_children(self, children: List[DerivationTree],
                                expansion: Expansion) -> List[DerivationTree]:
        function = exp_pre_expansion_function(expansion)
        if function is None:
            return children

        assert callable(function)
        if inspect.isgeneratorfunction(function):
            # See "generators", below
            result = self.run_generator(expansion, function)
        else:
            result = function()

        if self.log:
            print(repr(function) + "()", "=", repr(result))
        return self.apply_result(result, children)

    def run_generator(self, expansion: Expansion, function: Callable):
        ...

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def apply_result(self, result: Any,
                     children: List[DerivationTree]) -> List[DerivationTree]:
        if isinstance(result, str):
            children = [(result, [])]
        elif isinstance(result, list):
            symbol_indexes = [i for i, c in enumerate(children)
                              if is_nonterminal(c[0])]

            for index, value in enumerate(result):
                if value is not None:
                    child_index = symbol_indexes[index]
                    if not isinstance(value, str):
                        value = repr(value)
                    if self.log:
                        print(
                            "Replacing", all_terminals(
                                children[child_index]), "by", value)

                    # children[child_index] = (value, [])
                    child_symbol, _ = children[child_index]
                    children[child_index] = (child_symbol, [(value, [])])
        elif result is None:
            pass
        elif isinstance(result, bool):
            pass
        else:
            if self.log:
                print("Replacing", "".join(
                    [all_terminals(c) for c in children]), "by", result)

            children = [(repr(result), [])]

        return children

### Support for Python Generators

def iterate():
    t = 0
    while True:
        t = t + 1
        yield t


class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def fuzz_tree(self) -> DerivationTree:
        self.reset_generators()
        return super().fuzz_tree()

    def reset_generators(self) -> None:
        self.generators: Dict[str, Iterator] = {}

    def run_generator(self, expansion: Expansion,
                      function: Callable) -> Iterator:
        key = repr((expansion, function))
        if key not in self.generators:
            self.generators[key] = function()
        generator = self.generators[key]
        return next(generator)

## Checking and Repairing Elements after Expansion
## -----------------------------------------------


class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def fuzz_tree(self) -> DerivationTree:
        while True:
            tree = super().fuzz_tree()
            (symbol, children) = tree
            result, new_children = self.run_post_functions(tree)
            if not isinstance(result, bool) or result:
                return (symbol, new_children)
            self.restart_expansion()

    def restart_expansion(self) -> None:
        # To be overloaded in subclasses
        self.reset_generators()

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    # Return True if all constraints of grammar are satisfied in TREE
    def run_post_functions(self, tree: DerivationTree,
                           depth: Union[int, float] = float("inf")) \
                               -> Tuple[bool, Optional[List[DerivationTree]]]:
        symbol: str = tree[0]
        children: List[DerivationTree] = cast(List[DerivationTree], tree[1])

        if children == []:
            return True, children  # Terminal symbol

        try:
            expansion = self.find_expansion(tree)
        except KeyError:
            # Expansion (no longer) found - ignore
            return True, children

        result = True
        function = exp_post_expansion_function(expansion)
        if function is not None:
            result = self.eval_function(tree, function)
            if isinstance(result, bool) and not result:
                if self.log:
                    print(
                        all_terminals(tree),
                        "did not satisfy",
                        symbol,
                        "constraint")
                return False, children

            children = self.apply_result(result, children)

        if depth > 0:
            for c in children:
                result, _ = self.run_post_functions(c, depth - 1)
                if isinstance(result, bool) and not result:
                    return False, children

        return result, children

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def find_expansion(self, tree):
        symbol, children = tree

        applied_expansion = \
            "".join([child_symbol for child_symbol, _ in children])

        for expansion in self.grammar[symbol]:
            if exp_string(expansion) == applied_expansion:
                return expansion

        raise KeyError(
            symbol +
            ": did not find expansion " +
            repr(applied_expansion))

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def eval_function(self, tree, function):
        symbol, children = tree

        assert callable(function)

        args = []
        for (symbol, exp) in children:
            if exp != [] and exp is not None:
                symbol_value = all_terminals((symbol, exp))
                args.append(symbol_value)

        result = function(*args)
        if self.log:
            print(repr(function) + repr(tuple(args)), "=", repr(result))

        return result


from .ExpectError import ExpectError

def eval_with_exception(s):
    # Use "mute=True" to suppress all messages
    with ExpectError(print_traceback=False):
        return eval(s)
    return False


from .bookutils import HTML

if __name__ == '__main__':
    HTML("<strong>A bold text</strong>")

XML_GRAMMAR: Grammar = {
    "<start>": ["<xml-tree>"],
    "<xml-tree>": ["<<id>><xml-content></<id>>"],
    "<xml-content>": ["Text", "<xml-tree>"],
    "<id>": ["<letter>", "<id><letter>"],
    "<letter>": crange('a', 'z')
}

XML_GRAMMAR.update({
    "<xml-tree>": [("<<id>><xml-content></<id>>",
                    opts(post=lambda id1, content, id2: [None, None, id1])
                    )]
})

### Example: Checksums


## Local Checking and Repairing
## ----------------------------


class RestartExpansionException(Exception):
    pass

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def expand_tree_once(self, tree: DerivationTree) -> DerivationTree:
        # Apply inherited method.  This also calls `expand_tree_once()` on all
        # subtrees.
        new_tree: DerivationTree = super().expand_tree_once(tree)

        (symbol, children) = new_tree
        if all([exp_post_expansion_function(expansion)
                is None for expansion in self.grammar[symbol]]):
            # No constraints for this symbol
            return new_tree

        if self.any_possible_expansions(tree):
            # Still expanding
            return new_tree

        return self.run_post_functions_locally(new_tree)

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def run_post_functions_locally(self, new_tree: DerivationTree) -> DerivationTree:
        symbol, _ = new_tree

        result, children = self.run_post_functions(new_tree, depth=0)
        if not isinstance(result, bool) or result:
            # No constraints, or constraint satisfied
            # children = self.apply_result(result, children)
            new_tree = (symbol, children)
            return new_tree

        # Replace tree by unexpanded symbol and try again
        if self.log:
            print(
                all_terminals(new_tree),
                "did not satisfy",
                symbol,
                "constraint")

        if self.replacement_attempts_counter > 0:
            if self.log:
                print("Trying another expansion")
            self.replacement_attempts_counter -= 1
            return (symbol, None)

        if self.log:
            print("Starting from scratch")
        raise RestartExpansionException

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def __init__(self, grammar: Grammar, replacement_attempts: int = 10,
                 **kwargs) -> None:
        super().__init__(grammar, **kwargs)
        self.replacement_attempts = replacement_attempts

    def restart_expansion(self) -> None:
        super().restart_expansion()
        self.replacement_attempts_counter = self.replacement_attempts

    def fuzz_tree(self) -> DerivationTree:
        self.replacement_attempts_counter = self.replacement_attempts
        while True:
            try:
                # This is fuzz_tree() as defined above
                tree = super().fuzz_tree()
                return tree
            except RestartExpansionException:
                self.restart_expansion()

if __name__ == '__main__':
    binary_expr_fuzzer = GeneratorGrammarFuzzer(
        binary_expr_grammar, replacement_attempts=100)
    binary_expr_fuzzer.fuzz()

## Definitions and Uses
## --------------------


import string

VAR_GRAMMAR: Grammar = {
    '<start>': ['<statements>'],
    '<statements>': ['<statement>;<statements>', '<statement>'],
    '<statement>': ['<assignment>'],
    '<assignment>': ['<identifier>=<expr>'],
    '<identifier>': ['<word>'],
    '<word>': ['<alpha><word>', '<alpha>'],
    '<alpha>': list(string.ascii_letters),
    '<expr>': ['<term>+<expr>', '<term>-<expr>', '<term>'],
    '<term>': ['<factor>*<term>', '<factor>/<term>', '<factor>'],
    '<factor>':
    ['+<factor>', '-<factor>', '(<expr>)', '<identifier>', '<number>'],
    '<number>': ['<integer>.<integer>', '<integer>'],
    '<integer>': ['<digit><integer>', '<digit>'],
    '<digit>': crange('0', '9')
}


SYMBOL_TABLE: Set[str] = set()

def define_id(id: str) -> None:
    SYMBOL_TABLE.add(id)

def use_id() -> Union[bool, str]:
    if len(SYMBOL_TABLE) == 0:
        return False

    id = random.choice(list(SYMBOL_TABLE))
    return id

def clear_symbol_table() -> None:
    global SYMBOL_TABLE
    SYMBOL_TABLE = set()

CONSTRAINED_VAR_GRAMMAR = extend_grammar(VAR_GRAMMAR)

CONSTRAINED_VAR_GRAMMAR = extend_grammar(CONSTRAINED_VAR_GRAMMAR, {
    "<assignment>": [("<identifier>=<expr>",
                      opts(post=lambda id, expr: define_id(id)))]
})

CONSTRAINED_VAR_GRAMMAR = extend_grammar(CONSTRAINED_VAR_GRAMMAR, {
    "<factor>": ['+<factor>', '-<factor>', '(<expr>)',
                 ("<identifier>", opts(post=lambda _: use_id())),
                 '<number>']
})

CONSTRAINED_VAR_GRAMMAR = extend_grammar(CONSTRAINED_VAR_GRAMMAR, {
    "<start>": [("<statements>", opts(pre=clear_symbol_table))]
})


## Ordering Expansions
## -------------------

def exp_order(expansion):
    """Return the specified expansion ordering, or None if unspecified"""
    return exp_opt(expansion, 'order')

class GeneratorGrammarFuzzer(GeneratorGrammarFuzzer):
    def choose_tree_expansion(self, tree: DerivationTree,
                              expandable_children: List[DerivationTree]) \
                              -> int:
        """Return index of subtree in `expandable_children`
           to be selected for expansion. Defaults to random."""
        (symbol, tree_children) = tree
        assert isinstance(tree_children, list)

        if len(expandable_children) == 1:
            # No choice
            return super().choose_tree_expansion(tree, expandable_children)

        expansion = self.find_expansion(tree)
        given_order = exp_order(expansion)
        if given_order is None:
            # No order specified
            return super().choose_tree_expansion(tree, expandable_children)

        nonterminal_children = [c for c in tree_children if c[1] != []]
        assert len(nonterminal_children) == len(given_order), \
            "Order must have one element for each nonterminal"

        # Find expandable child with lowest ordering
        min_given_order = None
        j = 0
        for k, expandable_child in enumerate(expandable_children):
            while j < len(
                    nonterminal_children) and expandable_child != nonterminal_children[j]:
                j += 1
            assert j < len(nonterminal_children), "Expandable child not found"
            if self.log:
                print("Expandable child #%d %s has order %d" %
                      (k, expandable_child[0], given_order[j]))

            if min_given_order is None or given_order[j] < min_given_order:
                min_given_order = k

        assert min_given_order is not None

        if self.log:
            print("Returning expandable child #%d %s" %
                  (min_given_order, expandable_children[min_given_order][0]))

        return min_given_order


## All Together
## ------------

### Generators and Probabilistic Fuzzing

if __name__ == '__main__':
    print('\n### Generators and Probabilistic Fuzzing')



from .ProbabilisticGrammarFuzzer import ProbabilisticGrammarFuzzer  # minor dependency

from .bookutils import inheritance_conflicts

if __name__ == '__main__':
    inheritance_conflicts(ProbabilisticGrammarFuzzer, GeneratorGrammarFuzzer)

class ProbabilisticGeneratorGrammarFuzzer(GeneratorGrammarFuzzer,
                                          ProbabilisticGrammarFuzzer):
    """Join the features of `GeneratorGrammarFuzzer` 
    and `ProbabilisticGrammarFuzzer`"""

    def supported_opts(self) -> Set[str]:
        return (super(GeneratorGrammarFuzzer, self).supported_opts() |
                super(ProbabilisticGrammarFuzzer, self).supported_opts())

    def __init__(self, grammar: Grammar, *, replacement_attempts: int = 10,
                 **kwargs):
        """Constructor.
        `replacement_attempts` - see `GeneratorGrammarFuzzer` constructor.
        All other keywords go into `ProbabilisticGrammarFuzzer`.
        """
        super(GeneratorGrammarFuzzer, self).__init__(
                grammar,
                replacement_attempts=replacement_attempts)
        super(ProbabilisticGrammarFuzzer, self).__init__(grammar, **kwargs)

CONSTRAINED_VAR_GRAMMAR.update({
    '<word>': [('<alpha><word>', opts(prob=0.9)),
               '<alpha>'],
})

# Generators and Grammar Coverage
# ===============================


from .ProbabilisticGrammarFuzzer import ProbabilisticGrammarCoverageFuzzer  # minor dependency

from .GrammarCoverageFuzzer import GrammarCoverageFuzzer  # minor dependency


import copy

class ProbabilisticGeneratorGrammarCoverageFuzzer(GeneratorGrammarFuzzer,
                                                  ProbabilisticGrammarCoverageFuzzer):
    """Join the features of `GeneratorGrammarFuzzer` 
    and `ProbabilisticGrammarCoverageFuzzer`"""

    def supported_opts(self) -> Set[str]:
        return (super(GeneratorGrammarFuzzer, self).supported_opts() |
                super(ProbabilisticGrammarCoverageFuzzer, self).supported_opts())

    def __init__(self, grammar: Grammar, *,
                 replacement_attempts: int = 10, **kwargs) -> None:
        """Constructor.
        `replacement_attempts` - see `GeneratorGrammarFuzzer` constructor.
        All other keywords go into `ProbabilisticGrammarFuzzer`.
        """
        super(GeneratorGrammarFuzzer, self).__init__(
                grammar,
                replacement_attempts)
        super(ProbabilisticGrammarCoverageFuzzer, self).__init__(
                grammar,
                **kwargs)

class ProbabilisticGeneratorGrammarCoverageFuzzer(
        ProbabilisticGeneratorGrammarCoverageFuzzer):

    def fuzz_tree(self) -> DerivationTree:
        self.orig_covered_expansions = copy.deepcopy(self.covered_expansions)
        tree = super().fuzz_tree()
        self.covered_expansions = self.orig_covered_expansions
        self.add_tree_coverage(tree)
        return tree

    def add_tree_coverage(self, tree: DerivationTree) -> None:
        (symbol, children) = tree
        assert isinstance(children, list)
        if len(children) > 0:
            flat_children: List[DerivationTree] = [
                (child_symbol, None)
                for (child_symbol, _) in children
            ]
            self.add_coverage(symbol, flat_children)
            for c in children:
                self.add_tree_coverage(c)

class ProbabilisticGeneratorGrammarCoverageFuzzer(
        ProbabilisticGeneratorGrammarCoverageFuzzer):

    def restart_expansion(self) -> None:
        super().restart_expansion()
        self.covered_expansions = self.orig_covered_expansions

class PGGCFuzzer(ProbabilisticGeneratorGrammarCoverageFuzzer):
    """The one grammar-based fuzzer that supports all fuzzingbook features"""
    pass