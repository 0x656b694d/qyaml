#!/usr/bin/env python3
"""QYAML - query YAML with YAML.

Example:

    $ echo 'data: { password: superman }' | qyaml 'data: password'
    - superman

See README.md for more examples.
"""

import sys
from types import NoneType
import yaml
import re
from typing import Any, Generator, Tuple


def parse(docs, *queries):
    result, errors = [], []
    for doc in yaml.safe_load_all(docs):
        for query in queries:
            for query_doc in yaml.safe_load_all(query):
                for ok, value in do_query(doc, query_doc):
                    (result if ok else errors).append(value)
    return result, errors if queries and (result or errors) else [(False, queries)]


ResultGenerator = Generator[Tuple[bool, Any], NoneType, NoneType]


def matchfunc(doc, query) -> ResultGenerator:
    """
    >>> [*matchfunc('abc', 'a.c')]
    [(True, 'abc')]
    >>> [*matchfunc('abc', 'a.')]
    [(False, 'a.')]
    """
    yield (True, doc) if re.fullmatch(query, doc) else (False, query)


def eq(doc, query) -> ResultGenerator:
    """
    >>> [*eq(13, 13)]
    [(True, 13)]
    >>> [*eq('abc', 'ab.')]
    [(False, 'ab.')]
    """
    yield (True, doc) if query == doc else (False, query)


def dict_str(doc: dict, query: str) -> ResultGenerator:
    """
    >>> [*dict_str({'key1': 'value1', 'key2': 'value2'}, 'key.')]
    [(True, {'key1': 'value1'}), (True, {'key2': 'value2'})]
    >>> [*dict_str({'key1': 'value1', 'key2': 'value2'}, 'key2')]
    [(True, {'key2': 'value2'})]
    >>> [*dict_str({'key1': 'value1', 'key2': 'value2'}, 'key3')]
    [(False, 'key3')]
    """
    keys = filter(lambda k: re.fullmatch(query, k), doc.keys())
    found = False
    for k in keys:
        found = True
        yield (True, {k: doc[k]})
    if not found:
        yield (False, query)


def dict_bool(doc: dict, query: bool) -> ResultGenerator:
    """
    >>> [*dict_bool({'key1': 'value1', 'key2': 'value2'}, True)]
    [(True, {'key1': 'value1'}), (True, {'key2': 'value2'})]
    >>> [*dict_bool({'key1': 'value1', 'key2': 'value2'}, False)]
    [(True, 'key1'), (True, 'key2')]
    """
    if query:
        for k, v in doc.items():
            yield (True, {k: v})
    else:
        for k in doc.keys():
            yield (True, k)


def list_str(doc: list, query: str) -> ResultGenerator:
    """
    >>> [*list_str(['abc', 'def'], 'abc')]
    [(True, 'abc')]
    >>> [*list_str(['abc', 73], 73)]
    [(True, 73)]
    >>> [*list_str(['abc', {'abc': 'def'}], 'abc')]
    [(True, 'abc'), (True, {'abc': 'def'})]
    >>> [*list_str(['abc', {'abc': 'def'}], 'def')]
    [(False, 'def')]
    """
    found = False
    for d in doc:
        for ok, x in do_query(d, query):
            if ok:
                yield (True, x)
                found = True
    if not found:
        yield (False, query)


def list_list(doc: list, query: list) -> ResultGenerator:
    """
    >>> [*list_list([1,2,3], [1,2,3])]
    [(True, [1]), (True, [2]), (True, [3])]
    >>> [*list_list([1,2,3], [1,2,5])]
    [(True, [1]), (True, [2]), (False, 5)]
    >>> [*list_list([1,2,3], [5])]
    [(False, 5)]
    >>> [*list_list([{'key': 'value'}], ['key'])]
    [(True, [{'key': 'value'}])]
    """
    found = set()
    for d in doc:
        result = []
        for i, q in enumerate(query):
            for ok, x in do_query(d, q):
                if ok:
                    found.add(i)
                    result.append(x)
        if len(result):
            yield (True, result)
    yield from ((False, query[i]) for i in range(len(query)) if not i in found)


def str_list(doc: str, query: list) -> ResultGenerator:
    """
    >>> [*str_list('abcde', [1, 2, 3])]
    [(True, 'b'), (True, 'c'), (True, 'd')]
    """
    for q in query:
        yield from do_query(doc, q)


def dict_dict(doc: dict, query: dict) -> ResultGenerator:
    """
    >>> [*dict_dict({'key1': 'value1', 'key2': 'value2'},
    ... {'key1': 'value1', 'key2': 'value3'})]
    [(True, {'key1': 'value1'}), (False, {'key2': 'value3'})]
    >>> [*dict_dict({'key1': {'value1': 'value2'}},
    ... {'key.': 'value1'})]
    [(True, {'key1': {'value1': 'value2'}})]
    """
    for k, v in query.items():
        keys = filter(lambda kk: re.fullmatch(k, kk)
                      if type(k) == str else k, doc.keys())
        for dk in keys:
            result = {}
            for ok, x in do_query(doc.get(dk), v):
                if ok:
                    if dk in result:
                        yield (True, result)
                        result = {}
                    result[dk] = x
                else:
                    yield (False, {dk: v})
            if result:
                yield (True, result)


def dok_list(doc, query: list):
    for q in query:
        yield from dok_scalar(doc, q)


def dok_scalar(doc, query):
    return (ok for ok, _ in do_query(doc, query))


def dok(doc, query):
    yield from (dok_list if type(query) == list else dok_scalar)(doc, query)


def list_dict(doc: list, query: dict) -> ResultGenerator:
    """
    >>> [*list_dict(['one', 'two', 'three'], {True: '.*e'})]
    [(True, 'one'), (True, 'three')]
    >>> [*list_dict(['one', 'two', 'three'], {True: '.*e', 0: 'one'})]
    [(True, 'one'), (False, {True: '.*e', 0: 'one'}), (False, {True: '.*e', 0: 'one'})]
    """
    f = {}
    for k, v in query.items():
        if type(k) == bool:
            f[k] = v
            if (not k) in f:
                break
    for i, d in enumerate(doc):
        if True in f and not all(dok(d, f[True])) or False in f and any(dok(d, f[False])):
            continue
        only_bool = True
        for k, v in query.items():
            if type(k) == bool:
                continue
            only_bool = False
            if type(k) == int and k == i:
                yield from ((True, x) for ok, x in do_query(d, v) if ok)
        if only_bool:
            yield (True, d)
        else:
            yield from do_query(d, query)


def dict_list(doc: dict, query: list) -> ResultGenerator:
    """
    >>> [*dict_list({'key1': 'value1', 'key2': {'key22': 'value2'}}, ['key1', {'key2': 'key22'}, 'key3'])]
    [(True, {'key1': 'value1'}), (True, {'key2': {'key22': 'value2'}}), (False, 'key3')]
    >>> [*dict_list({'key1': 'value1', 'key2': {'key22': 'value2'}}, ['key.'])]
    [(True, {'key1': 'value1'}), (True, {'key2': {'key22': 'value2'}})]
    """
    found = set()
    for i, q in enumerate(query):
        for ok, x in do_query(doc, q):
            if ok:
                found.add(i)
                yield (True, x)
            else:
                break
        else:
            continue
        break
    yield from ((False, query[i]) for i in range(len(query)) if not i in found)


def x_index(doc, query) -> ResultGenerator:
    yield (True, doc[query]) if 0 <= query < len(doc) else (False, query)


def x_key(doc, query) -> ResultGenerator:
    yield (True, {query: doc[query]}) if query in doc else (False, query)


MATCHING_RULES: dict[str, dict[str, ResultGenerator]] = {
    None: {None: eq},
    str: {str: matchfunc, int: x_index, list: str_list},
    int: {int: eq, float: eq},
    float: {int: eq, float: eq},
    bool: {bool: eq},
    list: {str: list_str, int: x_index, float: x_index, list: list_list, dict: list_dict},
    dict: {str: dict_str, int: x_key, float: x_key,
           bool: dict_bool, list: dict_list, dict: dict_dict}
}


def do_query(doc, query):
    rule = MATCHING_RULES.get(type(doc))
    while rule is not None:
        rule = rule.get(type(query))
        if rule is not None:
            yield from rule(doc, query)
            break
    else:
        yield (False, query)


def print_results(results):
    r, err = results
    if len(r):
        yaml.safe_dump(r, stream=sys.stdout, canonical=False)
    return len(err) == 0
