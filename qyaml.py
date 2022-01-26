#!/usr/bin/env python3
"""QYAML - query YAML with YAML.

Example:

    $ echo 'data: { password: superman }' | qyaml.py 'data: password'
    - superman

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


def dok_list(doc, query):
    for q in query:
        yield from dok_scalar(doc, q)


def dok_scalar(doc, query):
    return (ok for ok, _ in do_query(doc, query))


def dok(doc, query):
    yield from (dok_list if type(query) == list else dok_scalar)(doc, query)


def do_query(doc, query):
    td, tq, err = type(doc), type(query), (False, query)
    if doc is None and query is not None:
        yield err
    elif tq == bool and td == bool or tq == str and td == str or tq in [int, float] and td in [int, float]:
        yield (True, doc) if query == doc else err
    elif td == dict and tq in [str, int, float]:
        yield (True, {query: doc[query]}) if query in doc else err
    elif td == dict and tq == bool:
        if query:
            for k, v in doc.items():
                yield (True, {k: v})
        else:
            for k in doc.keys():
                yield (True, k)
    elif td == list and tq == str:
        found = False
        for d in doc:
            for ok, x in do_query(d, query):
                if ok:
                    yield (True, x)
                    found = True
        if not found:
            yield err
    elif td == dict and tq in [int, float]:
        yield (True, doc[query]) if query in doc else err
    elif td in [list, str] and tq in [int, float]:
        yield (True, doc[query]) if 0 <= query < len(doc) else err
    elif td == list and tq == list:
        for d in doc:
            result = []
            for q in query:
                for ok, x in do_query(d, q):
                    if ok:
                        result.append(x)
            if len(result): yield (True, result)
    elif td in [dict, str] and tq == list:
        for q in query:
            yield from do_query(doc, q)
    elif td == dict and tq == dict:
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
    elif td == list and tq == dict:
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
                    for ok, x in do_query(d, v):
                        if ok:
                            yield (True, x)
            if only_bool:
                yield (True, d)
            else:
                yield from do_query(d, query)
            i += 1
    else:
        yield err


def print_results(results):
    r, err = results
    if len(r):
        yaml.safe_dump(r, stream=sys.stdout, canonical=False)
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
