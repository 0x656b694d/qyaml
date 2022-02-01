#!/usr/bin/env python3
"""QYAML - query YAML with YAML.

Example:

    $ echo 'data: { password: superman }' | qyaml.py 'data: password'
    - superman

See README.md for more examples.
"""

import sys
from types import NoneType
import yaml
import re
from typing import Any, Generator, Tuple


def qyaml(docs, queries):
    result, errors = [], []
    for doc in yaml.safe_load_all(docs):
        for query in yaml.safe_load_all(queries):
            for ok, value in do_query(doc, query):
                (result if ok else errors).append(value)
    return result, errors if queries and (result or errors) else [(False, queries)]


ResultGenerator = Generator[Tuple[bool, Any], NoneType, NoneType]


def matchfunc(doc, query) -> ResultGenerator:
    yield (True, doc) if re.fullmatch(query, doc) else (False, query)


def eq(doc, query) -> ResultGenerator:
    yield (True, doc) if query == doc else (False, query)


def dict_str(doc: dict, query: str) -> ResultGenerator:
    keys = filter(lambda k: re.fullmatch(query, k), doc.keys())
    if keys:
        yield from ((True, {k: doc[k]}) for k in keys)
    else:
        yield (False, query)


def dict_bool(doc: dict, query: bool) -> ResultGenerator:
    if query:
        for k, v in doc.items():
            yield (True, {k: v})
    else:
        for k in doc.keys():
            yield (True, k)


def list_str(doc: list, query: str) -> ResultGenerator:
    found = False
    for d in doc:
        for ok, x in do_query(d, query):
            if ok:
                yield (True, x)
                found = True
    if not found:
        yield (False, query)


def list_list(doc: list, query: list) -> ResultGenerator:
    for d in doc:
        result = []
        for q in query:
            for ok, x in do_query(d, q):
                if ok:
                    result.append(x)
        if len(result):
            yield (True, result)


def for_q_in_query(doc, query) -> ResultGenerator:
    for q in query:
        yield from do_query(doc, q)


def dict_dict(doc: dict, query: dict) -> ResultGenerator:
    result = {}
    for k, v in query.items():
        for ok, x in do_query(doc.get(k), v):
            if ok:
                if k in result:
                    result[k].append(x)
                else:
                    result[k] = [x]
    if len(result):
        yield (True, result)


def dok_list(doc, query: list):
    for q in query:
        yield from dok_scalar(doc, q)


def dok_scalar(doc, query):
    return (ok for ok, _ in do_query(doc, query))


def dok(doc, query):
    yield from (dok_list if type(query) == list else dok_scalar)(doc, query)


def list_dict(doc: list, query: dict) -> ResultGenerator:
    f = {}
    for k, v in query.items():
        if type(k) == bool:
            f[k] = v
            if (not k) in f:
                break
    i = 0
    for d in doc:
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
        i += 1


def x_index(doc, query) -> ResultGenerator:
    yield (True, doc[query]) if 0 <= query < len(doc) else (False, query)


def x_key(doc, query) -> ResultGenerator:
    yield (True, {query: doc[query]}) if query in doc else (False, query)


MATCHING_RULES: dict[str, dict[str, ResultGenerator]] = {
    None: {None: eq},
    str: {str: matchfunc, int: x_index, list: for_q_in_query},
    int: {int: eq, float: eq},
    float: {int: eq, float: eq},
    bool: {bool: eq},
    list: {str: list_str, int: x_index, float: x_index, list: list_list, dict: list_dict},
    dict: {str: dict_str, int: x_key, float: x_key,
           bool: dict_bool, list: for_q_in_query, dict: dict_dict}
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


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        print("\nUsage: %s query < doc" %
              sys.argv[0], file=sys.stderr)
        exit(1)

    try:
        ok = print_results(qyaml(sys.stdin, "\n---\n".join(sys.argv[1:])))
        exit(0 if ok else 1)
    except Exception as err:
        print("Error:", err, file=sys.stderr)
        exit(1)

