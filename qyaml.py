#!/usr/bin/env python3

import sys
import yaml
from os import path


def qyaml(doc, query):
    # Run tests with python -m doctest README.md
    errors, result = [], []
    for doc in yaml.safe_load_all(doc):
        for query in yaml.safe_load_all(query):
            for ok, value in do_query(doc, query):
                (result if ok else errors).append(value)
    return result, errors


def do_query(doc, query):
    td, tq, err = type(doc), type(query), (False, query)
    if doc == None and query != None:
        yield err
    elif tq == str:
        if td == str:
            yield (True, True) if query == doc else err
        else:
            yield (True, doc[query]) if query in doc else err
    elif tq in [int, float]:
        if td in [int, float]:
            yield (True, True) if query == doc else err
        else:
            yield (True, doc[query]) if query >= 0 and query < len(doc) else err
    elif tq == list:
        for n in query:
            yield from do_query(doc, n)
    elif tq == dict:
        for n in query:
            yield from do_query(doc[n], query[n])
    elif tq == bool:
        if td == bool:
            yield (True, True) if query == doc else err
        elif query and td == dict:
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
