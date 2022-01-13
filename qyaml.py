#!/usr/bin/env python3
"""QYAML - query YAML with YAML.

Example:

    $ echo 'data: { password: superman }' | qyaml.py 'data: password'
    superman
    ...

See README.md for more examples.
"""

import sys
import yaml


def qyaml(docs, queries):
    result, errors = [], []
    for doc in yaml.safe_load_all(docs):
        for query in yaml.safe_load_all(queries):
            for ok, value in do_query(doc, query):
                (result if ok else errors).append(value)
    return result, errors if queries and (result or errors) else [(False, queries)]


def do_query(doc, query):
    td, tq, err = type(doc), type(query), (False, query)
    if doc is None and query is not None:
        yield err
    elif tq == bool and td == bool or tq == str and td == str or tq in [int, float] and td in [int, float]:
        yield (True, doc) if query == doc else err
    elif tq == str and td == dict:
        yield (True, doc[query]) if query in doc else err
    elif tq == str and td == list:
        found = False
        for d in doc:
            for ok, x in do_query(d, query):
                if ok:
                    yield (True, x)
                    found = True
        if not found:
            yield err
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
            i = 0
            for d in doc:
                results = None
                for k, v in query.items():
                    if type(k) == int and k == i:
                        for ok, x in do_query(d, v):
                            if ok:
                                yield (True, x)
                            else:
                                results = False
                    elif type(k) == bool:
                        if results is None:
                            results = True
                        if type(v) == list:
                            for v0 in v:
                                if not all(ok == k for ok, _ in do_query(d, v0)):
                                    results = False
                                    break
                        elif not all(ok == k for ok, _ in do_query(d, v)):
                            results = False
                    else:
                        yield err
                if results:
                    yield (True, d)
                i += 1
        else:
            yield err
    else:
        yield err


def print_results(results):
    r, err = results
    if len(r):
        yaml.safe_dump(r, stream=sys.stdout)
    return len(err) == 0


if __name__ == '__main__':
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
