#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# "Parsing Inputs" - a chapter of "The Fuzzing Book"
# Web site: https://www.fuzzingbook.org/html/Parser.html
# Last change: 2023-01-07 15:16:26+01:00
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

# Parsing Inputs
# ==============

from typing import Dict, List, Tuple, Collection, Set, Iterable, Generator, cast

from .Fuzzer import Fuzzer  # minor dependency

from .Grammars import EXPR_GRAMMAR, START_SYMBOL, RE_NONTERMINAL
from .Grammars import is_valid_grammar, syntax_diagram, Grammar

from .GrammarFuzzer import GrammarFuzzer, display_tree, tree_to_string, dot_escape
from .GrammarFuzzer import DerivationTree

from .ExpectError import ExpectError

from .Timer import Timer

## Why Parsing for Fuzzing?
## ------------------------


def process_inventory(inventory):
    res = []
    for vehicle in inventory.split('\n'):
        ret = process_vehicle(vehicle)
        res.extend(ret)
    return '\n'.join(res)

def process_vehicle(vehicle):
    year, kind, company, model, *_ = vehicle.split(',')
    if kind == 'van':
        return process_van(year, company, model)

    elif kind == 'car':
        return process_car(year, company, model)

    else:
        raise Exception('Invalid entry')

def process_van(year, company, model):
    res = ["We have a %s %s van from %s vintage." % (company, model, year)]
    iyear = int(year)
    if iyear > 2010:
        res.append("It is a recent model!")
    else:
        res.append("It is an old but reliable model!")
    return res

def process_car(year, company, model):
    res = ["We have a %s %s car from %s vintage." % (company, model, year)]
    iyear = int(year)
    if iyear > 2016:
        res.append("It is a recent model!")
    else:
        res.append("It is an old but reliable model!")
    return res


import string

CSV_GRAMMAR: Grammar = {
    '<start>': ['<csvline>'],
    '<csvline>': ['<items>'],
    '<items>': ['<item>,<items>', '<item>'],
    '<item>': ['<letters>'],
    '<letters>': ['<letter><letters>', '<letter>'],
    '<letter>': list(string.ascii_letters + string.digits + string.punctuation + ' \t\n')
}


import copy

import random

class PooledGrammarFuzzer(GrammarFuzzer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._node_cache = {}

    def update_cache(self, key, values):
        self._node_cache[key] = values

    def expand_node_randomly(self, node):
        (symbol, children) = node
        assert children is None
        if symbol in self._node_cache:
            if random.randint(0, 1) == 1:
                return super().expand_node_randomly(node)
            return copy.deepcopy(random.choice(self._node_cache[symbol]))
        return super().expand_node_randomly(node)


## Using a Parser
## --------------

## An Ad Hoc Parser
## ----------------



def simple_parse_csv(mystring: str) -> DerivationTree:
    children: List[DerivationTree] = []
    tree = (START_SYMBOL, children)
    for i, line in enumerate(mystring.split('\n')):
        children.append(("record %d" % i, [(cell, [])
                                           for cell in line.split(',')]))
    return tree

def lr_graph(dot):
    dot.attr('node', shape='plain')
    dot.graph_attr['rankdir'] = 'LR'


def highlight_node(predicate):
    def hl_node(dot, nid, symbol, ann):
        if predicate(dot, nid, symbol, ann):
            dot.node(repr(nid), dot_escape(symbol), fontcolor='red')
        else:
            dot.node(repr(nid), dot_escape(symbol))
    return hl_node

def hl_predicate(_d, nid, _s, _a): return nid in bad_nodes

def parse_quote(string, i):
    v = string[i + 1:].find('"')
    return v + i + 1 if v >= 0 else -1

def find_comma(string, i):
    slen = len(string)
    while i < slen:
        if string[i] == '"':
            i = parse_quote(string, i)
            if i == -1:
                return -1
        if string[i] == ',':
            return i
        i += 1
    return -1

def comma_split(string):
    slen = len(string)
    i = 0
    while i < slen:
        c = find_comma(string, i)
        if c == -1:
            yield string[i:]
            return
        else:
            yield string[i:c]
        i = c + 1

def parse_csv(mystring):
    children = []
    tree = (START_SYMBOL, children)
    for i, line in enumerate(mystring.split('\n')):
        children.append(("record %d" % i, [(cell, [])
                                           for cell in comma_split(line)]))
    return tree



#It is here that formal parsers shine. The main idea is that, any given set of strings belong to a language, and these languages can be specified by their grammars (as we saw in the chapter on grammars). The great thing about grammars is that they can be composed. That is, one can introduce finer and finer details into an internal structure without affecting the external structure, and similarly, one can change the external structure without much impact on the internal structure.
## Grammars in Parsing
## -------------------

#### Ambiguity


## A Parser Class
## --------------


class Parser:
    """Base class for parsing."""

    def __init__(self, grammar: Grammar, *,
                 start_symbol: str = START_SYMBOL,
                 log: bool = False,
                 coalesce: bool = True,
                 tokens: Set[str] = set()) -> None:
        """Constructor.
           `grammar` is the grammar to be used for parsing.
           Keyword arguments:
           `start_symbol` is the start symbol (default: '<start>').
           `log` enables logging (default: False).
           `coalesce` defines if tokens should be coalesced (default: True).
           `tokens`, if set, is a set of tokens to be used."""
        self._grammar = grammar
        self._start_symbol = start_symbol
        self.log = log
        self.coalesce_tokens = coalesce
        self.tokens = tokens

    def grammar(self) -> Grammar:
        """Return the grammar of this parser."""
        return self._grammar

    def start_symbol(self) -> str:
        """Return the start symbol of this parser."""
        return self._start_symbol

    def parse_prefix(self, text: str) -> Tuple[int, Iterable[DerivationTree]]:
        """Return pair (cursor, forest) for longest prefix of text. 
           To be defined in subclasses."""
        raise NotImplementedError

    def parse(self, text: str) -> Iterable[DerivationTree]:
        """Parse `text` using the grammar. 
           Return an iterable of parse trees."""
        cursor, forest = self.parse_prefix(text)
        if cursor < len(text):
            raise SyntaxError("at " + repr(text[cursor:]))
        return [self.prune_tree(tree) for tree in forest]

    def parse_on(self, text: str, start_symbol: str) -> Generator:
        old_start = self._start_symbol
        try:
            self._start_symbol = start_symbol
            yield from self.parse(text)
        finally:
            self._start_symbol = old_start

    def coalesce(self, children: List[DerivationTree]) -> List[DerivationTree]:
        last = ''
        new_lst: List[DerivationTree] = []
        for cn, cc in children:
            if cn not in self._grammar:
                last += cn
            else:
                if last:
                    new_lst.append((last, []))
                    last = ''
                new_lst.append((cn, cc))
        if last:
            new_lst.append((last, []))
        return new_lst

    def prune_tree(self, tree: DerivationTree) -> DerivationTree:
        name, children = tree
        assert isinstance(children, list)

        if self.coalesce_tokens:
            children = self.coalesce(cast(List[DerivationTree], children))
        if name in self.tokens:
            return (name, [(tree_to_string(tree), [])])
        else:
            return (name, [self.prune_tree(c) for c in children])

### Excursion: Canonical Grammars


CanonicalGrammar = Dict[str, List[List[str]]]

import re

def single_char_tokens(grammar: Grammar) -> Dict[str, List[List[Collection[str]]]]:
    g_ = {}
    for key in grammar:
        rules_ = []
        for rule in grammar[key]:
            rule_ = []
            for token in rule:
                if token in grammar:
                    rule_.append(token)
                else:
                    rule_.extend(token)
            rules_.append(rule_)
        g_[key] = rules_
    return g_

def canonical(grammar: Grammar) -> CanonicalGrammar:
    def split(expansion):
        if isinstance(expansion, tuple):
            expansion = expansion[0]

        return [token for token in re.split(
            RE_NONTERMINAL, expansion) if token]

    return {
        k: [split(expression) for expression in alternatives]
        for k, alternatives in grammar.items()
    }

CE_GRAMMAR: CanonicalGrammar = canonical(EXPR_GRAMMAR)
CE_GRAMMAR

def recurse_grammar(grammar, key, order):
    rules = sorted(grammar[key])
    old_len = len(order)
    for rule in rules:
        for token in rule:
            if token not in grammar: continue
            if token not in order:
                order.append(token)
    new = order[old_len:]
    for ckey in new:
        recurse_grammar(grammar, ckey, order)

def show_grammar(grammar, start_symbol=START_SYMBOL):
    order = [start_symbol]
    recurse_grammar(grammar, start_symbol, order)
    return {k: sorted(grammar[k]) for k in order}


def non_canonical(grammar):
    new_grammar = {}
    for k in grammar:
        rules = grammar[k]
        new_rules = []
        for rule in rules:
            new_rules.append(''.join(rule))
        new_grammar[k] = new_rules
    return new_grammar


class Parser(Parser):
    def __init__(self, grammar, **kwargs):
        self._start_symbol = kwargs.get('start_symbol', START_SYMBOL)
        self.log = kwargs.get('log', False)
        self.tokens = kwargs.get('tokens', set())
        self.coalesce_tokens = kwargs.get('coalesce', True)
        canonical_grammar = kwargs.get('canonical', False)
        if canonical_grammar:
            self.cgrammar = single_char_tokens(grammar)
            self._grammar = non_canonical(grammar)
        else:
            self._grammar = dict(grammar)
            self.cgrammar = single_char_tokens(canonical(grammar))
        # we do not require a single rule for the start symbol
        if len(grammar.get(self._start_symbol, [])) != 1:
            self.cgrammar['<>'] = [[self._start_symbol]]

class Parser(Parser):
    def prune_tree(self, tree):
        name, children = tree
        if name == '<>':
            assert len(children) == 1
            return self.prune_tree(children[0])
        if self.coalesce_tokens:
            children = self.coalesce(children)
        if name in self.tokens:
            return (name, [(tree_to_string(tree), [])])
        else:
            return (name, [self.prune_tree(c) for c in children])


## Parsing Expression Grammars
## ---------------------------


PEG1 = {
    '<start>': ['a', 'b']
}

PEG2 = {
    '<start>': ['ab', 'abc']
}

### The Packrat Parser for Predicate Expression Grammars


class PEGParser(Parser):
    def parse_prefix(self, text):
        cursor, tree = self.unify_key(self.start_symbol(), text, 0)
        return cursor, [tree]

### Excursion: Implementing `PEGParser`


#### Unify Key



class PEGParser(PEGParser):
    """Packrat parser for Parsing Expression Grammars (PEGs)."""

    def unify_key(self, key, text, at=0):
        if self.log:
            print("unify_key: %s with %s" % (repr(key), repr(text[at:])))
        if key not in self.cgrammar:
            if text[at:].startswith(key):
                return at + len(key), (key, [])
            else:
                return at, None
        for rule in self.cgrammar[key]:
            to, res = self.unify_rule(rule, text, at)
            if res is not None:
                return (to, (key, res))
        return 0, None



class PEGParser(PEGParser):
    def unify_rule(self, rule, text, at):
        if self.log:
            print('unify_rule: %s with %s' % (repr(rule), repr(text[at:])))
        results = []
        for token in rule:
            at, res = self.unify_key(token, text, at)
            if res is None:
                return at, None
            results.append(res)
        return at, results

from functools import lru_cache

class PEGParser(PEGParser):
    @lru_cache(maxsize=None)
    def unify_key(self, key, text, at=0):
        if key not in self.cgrammar:
            if text[at:].startswith(key):
                return at + len(key), (key, [])
            else:
                return at, None
        for rule in self.cgrammar[key]:
            to, res = self.unify_rule(rule, text, at)
            if res is not None:
                return (to, (key, res))
        return 0, None


## Parsing Context-Free Grammars


### The Earley Parser




SAMPLE_GRAMMAR: Grammar = {
    '<start>': ['<A><B>'],
    '<A>': ['a<B>c', 'a<A>'],
    '<B>': ['b<C>', '<D>'],
    '<C>': ['c'],
    '<D>': ['d']
}
C_SAMPLE_GRAMMAR = canonical(SAMPLE_GRAMMAR)


#### Columns


class Column:
    def __init__(self, index, letter):
        self.index, self.letter = index, letter
        self.states, self._unique = [], {}

    def __str__(self):
        return "%s chart[%d]\n%s" % (self.letter, self.index, "\n".join(
            str(state) for state in self.states if state.finished()))

class Column(Column):
    def add(self, state):
        if state in self._unique:
            return self._unique[state]
        self._unique[state] = state
        self.states.append(state)
        state.e_col = self
        return self._unique[state]

#### Items

class Item:
    def __init__(self, name, expr, dot):
        self.name, self.expr, self.dot = name, expr, dot

class Item(Item):
    def finished(self):
        return self.dot >= len(self.expr)

    def advance(self):
        return Item(self.name, self.expr, self.dot + 1)

    def at_dot(self):
        return self.expr[self.dot] if self.dot < len(self.expr) else None

#### States


class State(Item):
    def __init__(self, name, expr, dot, s_col, e_col=None):
        super().__init__(name, expr, dot)
        self.s_col, self.e_col = s_col, e_col

    def __str__(self):
        def idx(var):
            return var.index if var else -1

        return self.name + ':= ' + ' '.join([
            str(p)
            for p in [*self.expr[:self.dot], '|', *self.expr[self.dot:]]
        ]) + "(%d,%d)" % (idx(self.s_col), idx(self.e_col))

    def copy(self):
        return State(self.name, self.expr, self.dot, self.s_col, self.e_col)

    def _t(self):
        return (self.name, self.expr, self.dot, self.s_col.index)

    def __hash__(self):
        return hash(self._t())

    def __eq__(self, other):
        return self._t() == other._t()

    def advance(self):
        return State(self.name, self.expr, self.dot + 1, self.s_col)


#### The Parsing Algorithm

class EarleyParser(Parser):
    """Earley Parser. This parser can parse any context-free grammar."""

    def __init__(self, grammar: Grammar, **kwargs) -> None:
        super().__init__(grammar, **kwargs)
        self.chart: List = []  # for type checking

    def chart_parse(self, words, start):
        alt = tuple(*self.cgrammar[start])
        chart = [Column(i, tok) for i, tok in enumerate([None, *words])]
        chart[0].add(State(start, alt, 0, chart[0]))
        return self.fill_chart(chart)

#### Predicting States


class EarleyParser(EarleyParser):
    def predict(self, col, sym, state):
        for alt in self.cgrammar[sym]:
            col.add(State(sym, tuple(alt), 0, col))


#### Scanning Tokens


class EarleyParser(EarleyParser):
    def scan(self, col, state, letter):
        if letter == col.letter:
            col.add(state.advance())


#### Completing Processing

class EarleyParser(EarleyParser):
    def complete(self, col, state):
        return self.earley_complete(col, state)

    def earley_complete(self, col, state):
        parent_states = [
            st for st in state.s_col.states if st.at_dot() == state.name
        ]
        for st in parent_states:
            col.add(st.advance())


#### Filling the Chart

if __name__ == '__main__':
    print('\n#### Filling the Chart')



class EarleyParser(EarleyParser):
    def fill_chart(self, chart):
        for i, col in enumerate(chart):
            for state in col.states:
                if state.finished():
                    self.complete(col, state)
                else:
                    sym = state.at_dot()
                    if sym in self.cgrammar:
                        self.predict(col, sym, state)
                    else:
                        if i + 1 >= len(chart):
                            continue
                        self.scan(chart[i + 1], state, sym)
            if self.log:
                print(col, '\n')
        return chart

if __name__ == '__main__':
    ep = EarleyParser(SAMPLE_GRAMMAR, log=True)
    columns = ep.chart_parse('adcd', START_SYMBOL)

if __name__ == '__main__':
    last_col = columns[-1]
    for state in last_col.states:
        if state.name == '<start>':
            print(state)

#### The Parse Method


class EarleyParser(EarleyParser):
    def parse_prefix(self, text):
        self.table = self.chart_parse(text, self.start_symbol())
        for col in reversed(self.table):
            states = [
                st for st in col.states if st.name == self.start_symbol()
            ]
            if states:
                return col.index, states
        return -1, []


class EarleyParser(EarleyParser):
    def parse(self, text):
        cursor, states = self.parse_prefix(text)
        start = next((s for s in states if s.finished()), None)

        if cursor < len(text) or not start:
            raise SyntaxError("at " + repr(text[cursor:]))

        forest = self.parse_forest(self.table, start)
        for tree in self.extract_trees(forest):
            yield self.prune_tree(tree)

#### Parsing Paths


class EarleyParser(EarleyParser):
    def parse_paths(self, named_expr, chart, frm, til):
        def paths(state, start, k, e):
            if not e:
                return [[(state, k)]] if start == frm else []
            else:
                return [[(state, k)] + r
                        for r in self.parse_paths(e, chart, frm, start)]

        *expr, var = named_expr
        starts = None
        if var not in self.cgrammar:
            starts = ([(var, til - len(var),
                        't')] if til > 0 and chart[til].letter == var else [])
        else:
            starts = [(s, s.s_col.index, 'n') for s in chart[til].states
                      if s.finished() and s.name == var]

        return [p for s, start, k in starts for p in paths(s, start, k, expr)]


#### Parsing Forests

class EarleyParser(EarleyParser):
    def forest(self, s, kind, chart):
        return self.parse_forest(chart, s) if kind == 'n' else (s, [])

    def parse_forest(self, chart, state):
        pathexprs = self.parse_paths(state.expr, chart, state.s_col.index,
                                     state.e_col.index) if state.expr else []
        return state.name, [[(v, k, chart) for v, k in reversed(pathexpr)]
                            for pathexpr in pathexprs]

#### Extracting Trees


class EarleyParser(EarleyParser):
    def extract_a_tree(self, forest_node):
        name, paths = forest_node
        if not paths:
            return (name, [])
        return (name, [self.extract_a_tree(self.forest(*p)) for p in paths[0]])

    def extract_trees(self, forest):
        yield self.extract_a_tree(forest)

A3_GRAMMAR: Grammar = {
    "<start>": ["<bexpr>"],
    "<bexpr>": [
        "<aexpr><gt><aexpr>", "<aexpr><lt><aexpr>", "<aexpr>=<aexpr>",
        "<bexpr>=<bexpr>", "<bexpr>&<bexpr>", "<bexpr>|<bexpr>", "(<bexrp>)"
    ],
    "<aexpr>":
    ["<aexpr>+<aexpr>", "<aexpr>-<aexpr>", "(<aexpr>)", "<integer>"],
    "<integer>": ["<digit><integer>", "<digit>"],
    "<digit>": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    "<lt>": ['<'],
    "<gt>": ['>']
}

#### Ambiguous Parsing

import itertools as I

class EarleyParser(EarleyParser):
    def extract_trees(self, forest_node):
        name, paths = forest_node
        if not paths:
            yield (name, [])

        for path in paths:
            ptrees = [self.extract_trees(self.forest(*p)) for p in path]
            for p in I.product(*ptrees):
                yield (name, p)

#### The Aycock Epsilon Fix



E_GRAMMAR_1: Grammar = {
    '<start>': ['<A>', '<B>'],
    '<A>': ['a', ''],
    '<B>': ['b']
}

EPSILON = ''
E_GRAMMAR: Grammar = {
    '<start>': ['<S>'],
    '<S>': ['<A><A><A><A>'],
    '<A>': ['a', '<E>'],
    '<E>': [EPSILON]
}


##### Fixpoint

def fixpoint(f):
    def helper(arg):
        while True:
            sarg = str(arg)
            arg_ = f(arg)
            if str(arg_) == sarg:
                return arg
            arg = arg_

    return helper

def my_sqrt(x):
    @fixpoint
    def _my_sqrt(approx):
        return (approx + x / approx) / 2

    return _my_sqrt(1)

if __name__ == '__main__':
    my_sqrt(2)

##### Nullable

def rules(grammar):
    return [(key, choice)
            for key, choices in grammar.items()
            for choice in choices]

def terminals(grammar):
    return set(token
               for key, choice in rules(grammar)
               for token in choice if token not in grammar)

def nullable_expr(expr, nullables):
    return all(token in nullables for token in expr)

def nullable(grammar):
    productions = rules(grammar)

    @fixpoint
    def nullable_(nullables):
        for A, expr in productions:
            if nullable_expr(expr, nullables):
                nullables |= {A}
        return (nullables)

    return nullable_({EPSILON})


class EarleyParser(EarleyParser):
    def __init__(self, grammar, **kwargs):
        super().__init__(grammar, **kwargs)
        self.epsilon = nullable(self.cgrammar)

    def predict(self, col, sym, state):
        for alt in self.cgrammar[sym]:
            col.add(State(sym, tuple(alt), 0, col))
        if sym in self.epsilon:
            col.add(state.advance())


DIRECTLY_SELF_REFERRING: Grammar = {
    '<start>': ['<query>'],
    '<query>': ['select <expr> from a'],
    "<expr>": ["<expr>", "a"],
}
INDIRECTLY_SELF_REFERRING: Grammar = {
    '<start>': ['<query>'],
    '<query>': ['select <expr> from a'],
    "<expr>": ["<aexpr>", "a"],
    "<aexpr>": ["<expr>"],
}

#### Tree Extractor


class SimpleExtractor:
    def __init__(self, parser, text):
        self.parser = parser
        cursor, states = parser.parse_prefix(text)
        start = next((s for s in states if s.finished()), None)
        if cursor < len(text) or not start:
            raise SyntaxError("at " + repr(cursor))
        self.my_forest = parser.parse_forest(parser.table, start)

    def extract_a_node(self, forest_node):
        name, paths = forest_node
        if not paths:
            return ((name, 0, 1), []), (name, [])
        cur_path, i, length = self.choose_path(paths)
        child_nodes = []
        pos_nodes = []
        for s, kind, chart in cur_path:
            f = self.parser.forest(s, kind, chart)
            postree, ntree = self.extract_a_node(f)
            child_nodes.append(ntree)
            pos_nodes.append(postree)

        return ((name, i, length), pos_nodes), (name, child_nodes)

    def choose_path(self, arr):
        length = len(arr)
        i = random.randrange(length)
        return arr[i], i, length

    def extract_a_tree(self):
        pos_tree, parse_tree = self.extract_a_node(self.my_forest)
        return self.parser.prune_tree(parse_tree)


class ChoiceNode:
    def __init__(self, parent, total):
        self._p, self._chosen = parent, 0
        self._total, self.next = total, None

    def chosen(self):
        assert not self.finished()
        return self._chosen

    def __str__(self):
        return '%d(%s/%s %s)' % (self._i, str(self._chosen),
                                 str(self._total), str(self.next))

    def __repr__(self):
        return repr((self._i, self._chosen, self._total))

    def increment(self):
        # as soon as we increment, next becomes invalid
        self.next = None
        self._chosen += 1
        if self.finished():
            if self._p is None:
                return None
            return self._p.increment()
        return self

    def finished(self):
        return self._chosen >= self._total

class EnhancedExtractor(SimpleExtractor):
    def __init__(self, parser, text):
        super().__init__(parser, text)
        self.choices = ChoiceNode(None, 1)

class EnhancedExtractor(EnhancedExtractor):
    def choose_path(self, arr, choices):
        arr_len = len(arr)
        if choices.next is not None:
            if choices.next.finished():
                return None, None, None, choices.next
        else:
            choices.next = ChoiceNode(choices, arr_len)
        next_choice = choices.next.chosen()
        choices = choices.next
        return arr[next_choice], next_choice, arr_len, choices

class EnhancedExtractor(EnhancedExtractor):
    def extract_a_node(self, forest_node, seen, choices):
        name, paths = forest_node
        if not paths:
            return (name, []), choices

        cur_path, _i, _l, new_choices = self.choose_path(paths, choices)
        if cur_path is None:
            return None, new_choices
        child_nodes = []
        for s, kind, chart in cur_path:
            if kind == 't':
                child_nodes.append((s, []))
                continue
            nid = (s.name, s.s_col.index, s.e_col.index)
            if nid in seen:
                return None, new_choices
            f = self.parser.forest(s, kind, chart)
            ntree, newer_choices = self.extract_a_node(f, seen | {nid}, new_choices)
            if ntree is None:
                return None, newer_choices
            child_nodes.append(ntree)
            new_choices = newer_choices
        return (name, child_nodes), new_choices

class EnhancedExtractor(EnhancedExtractor):
    def extract_a_tree(self):
        while not self.choices.finished():
            parse_tree, choices = self.extract_a_node(self.my_forest, set(), self.choices)
            choices.increment()
            if parse_tree is not None:
                return self.parser.prune_tree(parse_tree)
        return None


#### More Earley Parsing

### Excursion: Testing the Parsers

if __name__ == '__main__':
    print('\n### Excursion: Testing the Parsers')



def prod_line_grammar(nonterminals, terminals):
    g = {
        '<start>': ['<symbols>'],
        '<symbols>': ['<symbol><symbols>', '<symbol>'],
        '<symbol>': ['<nonterminals>', '<terminals>'],
        '<nonterminals>': ['<lt><alpha><gt>'],
        '<lt>': ['<'],
        '<gt>': ['>'],
        '<alpha>': nonterminals,
        '<terminals>': terminals
    }

    if not nonterminals:
        g['<nonterminals>'] = ['']
        del g['<lt>']
        del g['<alpha>']
        del g['<gt>']

    return g



def make_rule(nonterminals, terminals, num_alts):
    prod_grammar = prod_line_grammar(nonterminals, terminals)

    gf = GrammarFuzzer(prod_grammar, min_nonterminals=3, max_nonterminals=5)
    name = "<%s>" % ''.join(random.choices(string.ascii_uppercase, k=3))

    return (name, [gf.fuzz() for _ in range(num_alts)])


from .Grammars import unreachable_nonterminals

def make_grammar(num_symbols=3, num_alts=3):
    terminals = list(string.ascii_lowercase)
    grammar = {}
    name = None
    for _ in range(num_symbols):
        nonterminals = [k[1:-1] for k in grammar.keys()]
        name, expansions = \
            make_rule(nonterminals, terminals, num_alts)
        grammar[name] = expansions

    grammar[START_SYMBOL] = [name]

    # Remove unused parts
    for nonterminal in unreachable_nonterminals(grammar):
        del grammar[nonterminal]

    assert is_valid_grammar(grammar)

    return grammar




class PackratParser(Parser):
    def parse_prefix(self, text):
        txt, res = self.unify_key(self.start_symbol(), text)
        return len(txt), [res]

    def parse(self, text):
        remain, res = self.parse_prefix(text)
        if remain:
            raise SyntaxError("at " + res)
        return res

    def unify_rule(self, rule, text):
        results = []
        for token in rule:
            text, res = self.unify_key(token, text)
            if res is None:
                return text, None
            results.append(res)
        return text, results

    def unify_key(self, key, text):
        if key not in self.cgrammar:
            if text.startswith(key):
                return text[len(key):], (key, [])
            else:
                return text, None
        for rule in self.cgrammar[key]:
            text_, res = self.unify_rule(rule, text)
            if res:
                return (text_, (key, res))
        return text, None





class LeoParser(EarleyParser):
    def complete(self, col, state):
        return self.leo_complete(col, state)

    def leo_complete(self, col, state):
        detred = self.deterministic_reduction(state)
        if detred:
            col.add(detred.copy())
        else:
            self.earley_complete(col, state)

    def deterministic_reduction(self, state):
        raise NotImplementedError

class Column(Column):
    def __init__(self, index, letter):
        self.index, self.letter = index, letter
        self.states, self._unique, self.transitives = [], {}, {}

    def add_transitive(self, key, state):
        assert key not in self.transitives
        self.transitives[key] = state
        return self.transitives[key]

class LeoParser(LeoParser):
    def uniq_postdot(self, st_A):
        col_s1 = st_A.s_col
        parent_states = [
            s for s in col_s1.states if s.expr and s.at_dot() == st_A.name
        ]
        if len(parent_states) > 1:
            return None
        matching_st_B = [s for s in parent_states if s.dot == len(s.expr) - 1]
        return matching_st_B[0] if matching_st_B else None



class LeoParser(LeoParser):
    def get_top(self, state_A):
        st_B_inc = self.uniq_postdot(state_A)
        if not st_B_inc:
            return None
        
        t_name = st_B_inc.name
        if t_name in st_B_inc.e_col.transitives:
            return st_B_inc.e_col.transitives[t_name]

        st_B = st_B_inc.advance()

        top = self.get_top(st_B) or st_B
        return st_B_inc.e_col.add_transitive(t_name, top)

class LeoParser(LeoParser):
    def deterministic_reduction(self, state):
        return self.get_top(state)


class Column(Column):
    def add_transitive(self, key, state):
        assert key not in self.transitives
        self.transitives[key] = TState(state.name, state.expr, state.dot,
                                       state.s_col, state.e_col)
        return self.transitives[key]

class State(State):
    def back(self):
        return TState(self.name, self.expr, self.dot - 1, self.s_col, self.e_col)

class TState(State):
    def copy(self):
        return TState(self.name, self.expr, self.dot, self.s_col, self.e_col)

class LeoParser(LeoParser):
    def __init__(self, grammar, **kwargs):
        super().__init__(grammar, **kwargs)
        self._postdots = {}

class LeoParser(LeoParser):
    def uniq_postdot(self, st_A):
        col_s1 = st_A.s_col
        parent_states = [
            s for s in col_s1.states if s.expr and s.at_dot() == st_A.name
        ]
        if len(parent_states) > 1:
            return None
        matching_st_B = [s for s in parent_states if s.dot == len(s.expr) - 1]
        if matching_st_B:
            self._postdots[matching_st_B[0]._t()] = st_A
            return matching_st_B[0]
        return None
      

class LeoParser(LeoParser):
    def expand_tstate(self, state, e):
        if state._t() not in self._postdots:
            return
        c_C = self._postdots[state._t()]
        e.add(c_C.advance())
        self.expand_tstate(c_C.back(), e)

class LeoParser(LeoParser):
    def rearrange(self, table):
        f_table = [Column(c.index, c.letter) for c in table]
        for col in table:
            for s in col.states:
                f_table[s.s_col.index].states.append(s)
        return f_table



class LeoParser(LeoParser):
    def parse(self, text):
        cursor, states = self.parse_prefix(text)
        start = next((s for s in states if s.finished()), None)
        if cursor < len(text) or not start:
            raise SyntaxError("at " + repr(text[cursor:]))

        self.r_table = self.rearrange(self.table)
        forest = self.extract_trees(self.parse_forest(self.table, start))
        for tree in forest:
            yield self.prune_tree(tree)

class LeoParser(LeoParser):
    def parse_forest(self, chart, state):
        if isinstance(state, TState):
            self.expand_tstate(state.back(), state.e_col)
        
        return super().parse_forest(chart, state)


class FilteredLeoParser(LeoParser):
    def forest(self, s, kind, seen, chart):
        return self.parse_forest(chart, s, seen) if kind == 'n' else (s, [])

    def parse_forest(self, chart, state, seen=None):
        if isinstance(state, TState):
            self.expand_tstate(state.back(), state.e_col)

        def was_seen(chain, s):
            if isinstance(s, str):
                return False
            if len(s.expr) > 1:
                return False
            return s in chain

        if len(state.expr) > 1:  # things get reset if we have a non loop
            seen = set()
        elif seen is None:  # initialization
            seen = {state}

        pathexprs = self.parse_paths(state.expr, chart, state.s_col.index,
                                     state.e_col.index) if state.expr else []
        return state.name, [[(s, k, seen | {s}, chart)
                             for s, k in reversed(pathexpr)
                             if not was_seen(seen, s)] for pathexpr in pathexprs]




class IterativeEarleyParser(EarleyParser):
    def parse_paths(self, named_expr_, chart, frm, til_):
        return_paths = []
        path_build_stack = [(named_expr_, til_, [])]

        def iter_paths(path_prefix, path, start, k, e):
            x = path_prefix + [(path, k)]
            if not e:
                return_paths.extend([x] if start == frm else [])
            else:
                path_build_stack.append((e, start, x))

        while path_build_stack:
            named_expr, til, path_prefix = path_build_stack.pop()
            *expr, var = named_expr

            starts = None
            if var not in self.cgrammar:
                starts = ([(var, til - len(var), 't')]
                          if til > 0 and chart[til].letter == var else [])
            else:
                starts = [(s, s.s_col.index, 'n') for s in chart[til].states
                          if s.finished() and s.name == var]

            for s, start, k in starts:
                iter_paths(path_prefix, s, start, k, expr)

        return return_paths

class IterativeEarleyParser(IterativeEarleyParser):
    def choose_a_node_to_explore(self, node_paths, level_count):
        first, *rest = node_paths
        return first

    def extract_a_tree(self, forest_node_):
        start_node = (forest_node_[0], [])
        tree_build_stack = [(forest_node_, start_node[-1], 0)]

        while tree_build_stack:
            forest_node, tree, level_count = tree_build_stack.pop()
            name, paths = forest_node

            if not paths:
                tree.append((name, []))
            else:
                new_tree = []
                current_node = self.choose_a_node_to_explore(paths, level_count)
                for p in reversed(current_node):
                    new_forest_node = self.forest(*p)
                    tree_build_stack.append((new_forest_node, new_tree, level_count + 1))
                tree.append((name, new_tree))

        return start_node

class IterativeEarleyParser(IterativeEarleyParser):
    def extract_trees(self, forest):
        yield self.extract_a_tree(forest)



def firstset(grammar, nullable):
    first = {i: {i} for i in terminals(grammar)}
    for k in grammar:
        first[k] = {EPSILON} if k in nullable else set()
    return firstset_((rules(grammar), first, nullable))[1]

def first_expr(expr, first, nullable):
    tokens = set()
    for token in expr:
        tokens |= first[token]
        if token not in nullable:
            break
    return tokens

@fixpoint
def firstset_(arg):
    (rules, first, epsilon) = arg
    for A, expression in rules:
        first[A] |= first_expr(expression, first, epsilon)
    return (rules, first, epsilon)

EOF = '\0'

def followset(grammar, start):
    follow = {i: set() for i in grammar}
    follow[start] = {EOF}

    epsilon = nullable(grammar)
    first = firstset(grammar, epsilon)
    return followset_((grammar, epsilon, first, follow))[-1]

@fixpoint
def followset_(arg):
    grammar, epsilon, first, follow = arg
    for A, expression in rules(grammar):
        f_B = follow[A]
        for t in reversed(expression):
            if t in grammar:
                follow[t] |= f_B
            f_B = f_B | first[t] if t in epsilon else (first[t] - {EPSILON})

    return (grammar, epsilon, first, follow)



class LL1Parser(Parser):
    def parse_table(self):
        self.my_rules = rules(self.cgrammar)
        self.table = ...          # fill in here to produce

    def rules(self):
        for i, rule in enumerate(self.my_rules):
            print(i, rule)

    def show_table(self):
        ts = list(sorted(terminals(self.cgrammar)))
        print('Rule Name\t| %s' % ' | '.join(t for t in ts))
        for k in self.table:
            pr = self.table[k]
            actions = list(str(pr[t]) if t in pr else ' ' for t in ts)
            print('%s  \t| %s' % (k, ' | '.join(actions)))


class LL1Parser(LL1Parser):
    def predict(self, rulepair, first, follow, epsilon):
        A, rule = rulepair
        rf = first_expr(rule, first, epsilon)
        if nullable_expr(rule, epsilon):
            rf |= follow[A]
        return rf

    def parse_table(self):
        self.my_rules = rules(self.cgrammar)
        epsilon = nullable(self.cgrammar)
        first = firstset(self.cgrammar, epsilon)
        # inefficient, can combine the three.
        follow = followset(self.cgrammar, self.start_symbol())

        ptable = [(i, self.predict(rule, first, follow, epsilon))
                  for i, rule in enumerate(self.my_rules)]

        parse_tbl = {k: {} for k in self.cgrammar}

        for i, pvals in ptable:
            (k, expr) = self.my_rules[i]
            parse_tbl[k].update({v: i for v in pvals})

        self.table = parse_tbl


class LL1Parser(LL1Parser):
    def parse_helper(self, stack, inplst):
        inp, *inplst = inplst
        exprs = []
        while stack:
            val, *stack = stack
            if isinstance(val, tuple):
                exprs.append(val)
            elif val not in self.cgrammar:  # terminal
                assert val == inp
                exprs.append(val)
                inp, *inplst = inplst or [None]
            else:
                if inp is not None:
                    i = self.table[val][inp]
                    _, rhs = self.my_rules[i]
                    stack = rhs + [(val, len(rhs))] + stack
        return self.linear_to_tree(exprs)

    def parse(self, inp):
        self.parse_table()
        k, _ = self.my_rules[0]
        stack = [k]
        return self.parse_helper(stack, inp)

    def linear_to_tree(self, arr):
        stack = []
        while arr:
            elt = arr.pop(0)
            if not isinstance(elt, tuple):
                stack.append((elt, []))
            else:
                # get the last n
                sym, n = elt
                elts = stack[-n:] if n > 0 else []
                stack = stack[0:len(stack) - n]
                stack.append((sym, elts))
        assert len(stack) == 1
        return stack[0]
