#!/usr/bin/env python3

import sys
import yaml
from os import path


def qyaml(doc, query):
    # Run tests with python -m doctest README.md
    result, errors = [], []
    for doc in yaml.safe_load_all(doc):
        for query in yaml.safe_load_all(query):
            for ok, value in do_query(doc, query):
                (result if ok else errors).append(value)
    return result, errors if query and (result or errors) else [(False, query)]


def do_query(doc, query):
    td, tq, err = type(doc), type(query), (False, query)
    if doc is None and query is not None:
        yield err
    elif tq == bool and td == bool or tq == str and td == str or tq in [int, float] and td in [int, float]:
        yield (True, doc) if query == doc else err
    elif tq == str:
        yield (True, doc[query]) if query in doc else err
    elif tq in [int, float]:
        yield (True, doc[query]) if td == dict and query in doc or td in [list, str] and 0 <= query < len(doc) else err
    elif tq == bool:
        for v in doc.values() if query and td == dict else doc:
            yield (True, v)
    elif tq == list:
        for n in query:
            yield from do_query(doc, n)
    elif tq == dict:
        if td == dict:
            for k, v in query.items():
                yield from do_query(doc.get(k), v)
        elif td == list:
            for d in doc:
                results = None
                for k, v in query.items():
                    if results is None:
                        results = True
                    if type(k) in [bool, int]:
                        if not all(ok == k if type(k) == bool else ok for ok, _ in do_query(d, v)):
                            results = False
                    else:
                        yield err
                if results:
                    yield (True, d)
        else:
            yield err
    else:
        yield err


def print_results(results):
    r, err = results
    if len(r):
        yaml.safe_dump(r if len(r) > 1 else r[0], stream=sys.stdout)
    return len(err) == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: %s query < doc\n" % sys.argv[0], file=sys.stderr)
        with open(path.join(path.dirname(path.realpath(__file__)), "README.md")) as help:
            print(help.read(), file=sys.stderr)
        exit(1)

    try:
        exit(0 if print_results(
            qyaml(sys.stdin, "\n---\n".join(sys.argv[1:]))) else 1)
    except Exception as err:
        print("Error:", err, file=sys.stderr)
        exit(1)
