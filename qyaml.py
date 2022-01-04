#!/usr/bin/env python3

import sys
import yaml
from os import path
from enum import Enum


def qyaml(doc, query):
    # Run tests with python -m doctest README.md
    errors, result = [], []
    for doc in yaml.safe_load_all(doc):
        for query in yaml.safe_load_all(query):
            for ok, value in do_query(doc, query):
                (result if ok else errors).append(value)
    return result, errors


def do_query(doc, query):
    td, tq = type(doc), type(query)
    if doc == None:
        yield (False, query)
    elif tq == str:
        if td == str:
            yield (True, True) if query == doc else (False, query)
        elif query not in doc:
            yield (False, query)
        else:
            yield (True, doc[query])
    elif tq == int or tq == float:
        if td == int or td == float:
            yield (True, True) if query == doc else (False, query)
        elif query < 0 or query > len(doc):
            yield (False, query)
        else:
            yield (True, doc[query])
    elif tq == list:
        for n in query:
            yield from do_query(doc, n)
    elif tq == dict:
        for n in query:
            yield from do_query(doc[n], query[n])
    elif tq == bool:
        if query and td == dict:
            for k in doc:
                yield (True, doc[k])
        else:
            for k in doc:
                yield (True, k)


def print_results(results):
    result, errors = results

    if len(result) > 0:
        yaml.safe_dump(result if len(result) >
                       1 else result[0], stream=sys.stdout)

    if len(errors) > 0:
        raise Exception(errors)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: %s query < doc\n" % sys.argv[0], file=sys.stderr)
        with open(path.join(path.dirname(sys.argv[0]), "README.md")) as help:
            print(help.read(), file=sys.stderr)
        exit(1)

    try:
        print_results(qyaml(sys.stdin, sys.argv[1]))
    except Exception as err:
        print("Errors:", err, file=sys.stderr)
        exit(1)
