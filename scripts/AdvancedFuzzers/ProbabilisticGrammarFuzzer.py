#ProbabilisticGrammarFuzzer.py
# -*- coding: utf-8 -*-

# "Probabilistic Grammar Fuzzing" - a chapter of "The Fuzzing Book"
# Web site: https://www.fuzzingbook.org/html/ProbabilisticGrammarFuzzer.html
# Last change: 2023-01-07 15:16:35+01:00
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


# Probabilistic Grammar Fuzzing
# =============================


## Specifying Probabilities
## ------------------------


from .Fuzzer import Fuzzer

from .GrammarFuzzer import GrammarFuzzer, all_terminals, display_tree, DerivationTree

from .Grammars import is_valid_grammar, EXPR_GRAMMAR, START_SYMBOL, crange
from .Grammars import opts, exp_string, exp_opt, set_opts
from .Grammars import Grammar, Expansion

from typing import List, Dict, Set, Optional, cast, Any, Tuple

PROBABILISTIC_EXPR_GRAMMAR: Grammar = {
    "<start>":
        ["<expr>"],

    "<expr>":
        [("<term> + <expr>", opts(prob=0.1)),
         ("<term> - <expr>", opts(prob=0.2)),
         "<term>"],

    "<term>":
        [("<factor> * <term>", opts(prob=0.1)),
         ("<factor> / <term>", opts(prob=0.1)),
         "<factor>"
         ],

    "<factor>":
        ["+<factor>", "-<factor>", "(<expr>)",
            "<leadinteger>", "<leadinteger>.<integer>"],

    "<leadinteger>":
        ["<leaddigit><integer>", "<leaddigit>"],

    # Benford's law: frequency distribution of leading digits
    "<leaddigit>":
        [("1", opts(prob=0.301)),
         ("2", opts(prob=0.176)),
         ("3", opts(prob=0.125)),
         ("4", opts(prob=0.097)),
         ("5", opts(prob=0.079)),
         ("6", opts(prob=0.067)),
         ("7", opts(prob=0.058)),
         ("8", opts(prob=0.051)),
         ("9", opts(prob=0.046)),
         ],

    # Remaining digits are equally distributed
    "<integer>":
        ["<digit><integer>", "<digit>"],

    "<digit>":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
}



def exp_prob(expansion: Expansion) -> float:
    """Return the options of an expansion"""
    return exp_opt(expansion, 'prob')


from .GrammarCoverageFuzzer import GrammarCoverageFuzzer  # minor dependency

## Computing Probabilities
## -----------------------

### Distributing Probabilities


def exp_probabilities(expansions: List[Expansion],
                      nonterminal: str ="<symbol>") \
        -> Dict[Expansion, float]:
    probabilities = [exp_prob(expansion) for expansion in expansions]
    prob_dist = prob_distribution(probabilities, nonterminal)  # type: ignore

    prob_mapping: Dict[Expansion, float] = {}
    for i in range(len(expansions)):
        expansion = exp_string(expansions[i])
        prob_mapping[expansion] = prob_dist[i]

    return prob_mapping

def prob_distribution(probabilities: List[Optional[float]],
                      nonterminal: str = "<symbol>"):
    epsilon = 0.00001

    number_of_unspecified_probabilities = probabilities.count(None)
    if number_of_unspecified_probabilities == 0:
        sum_probabilities = cast(float, sum(probabilities))
        assert abs(sum_probabilities - 1.0) < epsilon, \
            nonterminal + ": sum of probabilities must be 1.0"
        return probabilities

    sum_of_specified_probabilities = 0.0
    for p in probabilities:
        if p is not None:
            sum_of_specified_probabilities += p
    assert 0 <= sum_of_specified_probabilities <= 1.0, \
        nonterminal + ": sum of specified probabilities must be between 0.0 and 1.0"

    default_probability = ((1.0 - sum_of_specified_probabilities)
                           / number_of_unspecified_probabilities)
    all_probabilities = []
    for p in probabilities:
        if p is None:
            p = default_probability
        all_probabilities.append(p)

    assert abs(sum(all_probabilities) - 1.0) < epsilon
    return all_probabilities

### Checking Probabilities


def is_valid_probabilistic_grammar(grammar: Grammar,
                                   start_symbol: str = START_SYMBOL) -> bool:
    if not is_valid_grammar(grammar, start_symbol):
        return False

    for nonterminal in grammar:
        expansions = grammar[nonterminal]
        _ = exp_probabilities(expansions, nonterminal)

    return True



## Expanding by Probability
## ------------------------



import random

class ProbabilisticGrammarFuzzer(GrammarFuzzer):
    """A grammar-based fuzzer respecting probabilities in grammars."""

    def check_grammar(self) -> None:
        super().check_grammar()
        assert is_valid_probabilistic_grammar(self.grammar)

    def supported_opts(self) -> Set[str]:
        return super().supported_opts() | {'prob'}

class ProbabilisticGrammarFuzzer(ProbabilisticGrammarFuzzer):
    def choose_node_expansion(self, node: DerivationTree,
                              children_alternatives: List[Any]) -> int:
        (symbol, tree) = node
        expansions = self.grammar[symbol]
        probabilities = exp_probabilities(expansions)

        weights: List[float] = []
        for children in children_alternatives:
            expansion = all_terminals((symbol, children))
            children_weight = probabilities[expansion]
            if self.log:
                print(repr(expansion), "p =", children_weight)
            weights.append(children_weight)

        if sum(weights) == 0:
            # No alternative (probably expanding at minimum cost)
            return random.choices(
                range(len(children_alternatives)))[0]
        else:
            return random.choices(
                range(len(children_alternatives)), weights=weights)[0]




## Directed Fuzzing
## ----------------



def set_prob(grammar: Grammar, symbol: str, 
             expansion: Expansion, prob: Optional[float]) -> None:
    """Set the probability of the given expansion of grammar[symbol]"""
    set_opts(grammar, symbol, expansion, opts(prob=prob))



## Probabilities in Context
## ------------------------

def decrange(start: int, end: int) -> List[Expansion]:
    """Return a list with string representations of numbers in the range [start, end)"""
    return [repr(n) for n in range(start, end)]


from .GrammarCoverageFuzzer import duplicate_context  # minor dependency


## Learning Probabilities from Samples
## -----------------------------------



### Counting Expansions


from .Parser import Parser, EarleyParser

IP_ADDRESS_TOKENS = {"<octet>"}  # EarleyParser needs explicit tokens


from .GrammarCoverageFuzzer import expansion_key  # minor dependency

from .Grammars import is_nonterminal

class ExpansionCountMiner:
    def __init__(self, parser: Parser, log: bool = False) -> None:
        assert isinstance(parser, Parser)
        self.grammar = extend_grammar(parser.grammar())
        self.parser = parser
        self.log = log
        self.reset()

class ExpansionCountMiner(ExpansionCountMiner):
    def reset(self) -> None:
        self.expansion_counts: Dict[str, int] = {}

    def add_coverage(self, symbol: str, children: List[DerivationTree]) -> None:
        key = expansion_key(symbol, children)

        if self.log:
            print("Found", key)

        if key not in self.expansion_counts:
            self.expansion_counts[key] = 0
        self.expansion_counts[key] += 1

    def add_tree(self, tree: DerivationTree) -> None:
        (symbol, children) = tree
        if not is_nonterminal(symbol):
            return
        assert children is not None

        direct_children: List[DerivationTree] = [
            (symbol, None) if is_nonterminal(symbol) 
            else (symbol, []) for symbol, c in children]
        self.add_coverage(symbol, direct_children)

        for c in children:
            self.add_tree(c)

class ExpansionCountMiner(ExpansionCountMiner):
    def count_expansions(self, inputs: List[str]) -> None:
        for inp in inputs:
            tree, *_ = self.parser.parse(inp)
            self.add_tree(tree)

    def counts(self) -> Dict[str, int]:
        return self.expansion_counts



### Assigning Probabilities


class ProbabilisticGrammarMiner(ExpansionCountMiner):
    def set_probabilities(self, counts: Dict[str, int]):
        for symbol in self.grammar:
            self.set_expansion_probabilities(symbol, counts)

    def set_expansion_probabilities(self, symbol: str, counts: Dict[str, int]):
        expansions = self.grammar[symbol]
        if len(expansions) == 1:
            set_prob(self.grammar, symbol, expansions[0], None)
            return

        expansion_counts = [
            counts.get(
                expansion_key(
                    symbol,
                    expansion),
                0) for expansion in expansions]
        total = sum(expansion_counts)
        for i, expansion in enumerate(expansions):
            p = expansion_counts[i] / total if total > 0 else None
            # if self.log:
            #     print("Setting", expansion_key(symbol, expansion), p)
            set_prob(self.grammar, symbol, expansion, p)

class ProbabilisticGrammarMiner(ProbabilisticGrammarMiner):
    def mine_probabilistic_grammar(self, inputs: List[str]) -> Grammar:
        self.count_expansions(inputs)
        self.set_probabilities(self.counts())
        return self.grammar



### Testing Common Features


URL_SAMPLE: List[str] = [
    "https://user:password@cispa.saarland:80/",
    "https://fuzzingbook.com?def=56&x89=3&x46=48&def=def",
    "https://cispa.saarland:80/def?def=7&x23=abc",
    "https://fuzzingbook.com:80/",
    "https://fuzzingbook.com:80/abc?def=abc&abc=x14&def=abc&abc=2&def=38",
    "ftps://fuzzingbook.com/x87",
    "https://user:password@fuzzingbook.com:6?def=54&x44=abc",
    "http://fuzzingbook.com:80?x33=25&def=8",
    "http://fuzzingbook.com:8080/def",
]

URL_TOKENS: Set[str] = {"<scheme>", "<userinfo>", "<host>", "<port>", "<id>"}


### Testing Uncommon Features


import copy

def invert_expansion(expansion: List[Expansion]) -> List[Expansion]:
    def sort_by_prob(x: Tuple[int, float]) -> float:
        index, prob = x
        return prob if prob is not None else 0.0

    inverted_expansion: List[Expansion] = copy.deepcopy(expansion)
    indexes_and_probs = [(index, exp_prob(alternative))
                         for index, alternative in enumerate(expansion)]
    indexes_and_probs.sort(key=sort_by_prob)
    indexes = [i for (i, _) in indexes_and_probs]

    for j in range(len(indexes)):
        k = len(indexes) - 1 - j
        # print(indexes[j], "gets", indexes[k])
        inverted_expansion[indexes[j]][1]['prob'] = expansion[indexes[k]][1]['prob']  # type: ignore

    return inverted_expansion

def invert_probs(grammar: Grammar) -> Grammar:
    inverted_grammar = extend_grammar(grammar)
    for symbol in grammar:
        inverted_grammar[symbol] = invert_expansion(grammar[symbol])
    return inverted_grammar

### Learning Probabilities from Input Slices


from .Coverage import Coverage, cgi_decode
from .Grammars import CGI_GRAMMAR


## Detecting Unnatural Numbers
## ---------------------------


### Exercise 1: Probabilistic Fuzzing with Coverage


class ProbabilisticGrammarCoverageFuzzer(
        GrammarCoverageFuzzer, ProbabilisticGrammarFuzzer):
    # Choose uncovered expansions first
    def choose_node_expansion(self, node, children_alternatives):
        return GrammarCoverageFuzzer.choose_node_expansion(
            self, node, children_alternatives)

    # Among uncovered expansions, pick by (relative) probability
    def choose_uncovered_node_expansion(self, node, children_alternatives):
        return ProbabilisticGrammarFuzzer.choose_node_expansion(
            self, node, children_alternatives)

    # For covered nodes, pick by probability, too
    def choose_covered_node_expansion(self, node, children_alternatives):
        return ProbabilisticGrammarFuzzer.choose_node_expansion(
            self, node, children_alternatives)
