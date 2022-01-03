#!/usr/bin/env python3

import sys
import yaml
import json

def qyaml(doc, query):
    # Run tests with python -m doctest qyaml.py
    """Walk synchronously through query and doc, and print the branches of doc[query].

Example input:
    >>> doc = '{ dict: { key1: "value1", key2: "value2" }, array: [ "value3", "value4" ] }'

Querying dictionaries:
    >>> qyaml(doc, 'dict: key1')
    value1
    ...
    <BLANKLINE>

    >>> qyaml(doc, 'dict: [key1, key2]')
    value1
    ...
    <BLANKLINE>
    value2
    ...
    <BLANKLINE>

    >>> qyaml(doc, 'dict')
    key1: value1
    key2: value2
    <BLANKLINE>

    >>> qyaml(doc, 'dict: true')
    value1
    ...
    <BLANKLINE>
    value2
    ...
    <BLANKLINE>

    >>> qyaml(doc, 'dict: false')
    key1
    key2

Querying arrays:
    >>> qyaml(doc, 'array: 1')
    value4
    ...
    <BLANKLINE>

    >>> qyaml(doc, 'array: [0,1]')
    value3
    ...
    <BLANKLINE>
    value4
    ...
    <BLANKLINE>

    >>> qyaml(doc, 'array')
    - value3
    - value4
    <BLANKLINE>

    >>> qyaml(doc, 'array: true')
    value3
    value4

Combining:
    >>> qyaml(doc, '[dict: key1, array: 0]')
    value1
    ...
    <BLANKLINE>
    value3
    ...
    <BLANKLINE>

Printing as JSON:
    >>> qyaml(doc, 'null')
    {"dict": {"key1": "value1", "key2": "value2"}, "array": ["value3", "value4"]}

    >>> qyaml(doc, 'dict: null')
    {"key1": "value1", "key2": "value2"}

Query characters:
    >>> qyaml(doc, 'dict: { key1: [4,0,1]}')
    e
    ...
    <BLANKLINE>
    v
    ...
    <BLANKLINE>
    a
    ...
    <BLANKLINE>

Errors:
    >>> qyaml(doc, 'missing')
    Traceback (most recent call last):
    ...
    Exception: missing

Multiple documents:
    >>> mdoc = 'dict: value1\\n---\\ndict: value2'
    >>> qyaml(mdoc, 'dict')
    value1
    ...
    <BLANKLINE>
    value2
    ...
    <BLANKLINE>

    >>> qyaml('[1, 2]', '0\\n---\\n1')
    1
    ...
    <BLANKLINE>
    2
    ...
    <BLANKLINE>
    """
    for doc in yaml.safe_load_all(doc):
        for query in yaml.safe_load_all(query):
            for value in do_query(doc, query):
                print(value)


def do_query(doc, query):
    if doc == None:
        raise Exception(query)
    if isinstance(query, str):
        if query not in doc:
            raise Exception(query)
        yield yaml.safe_dump(doc[query])
    elif type(query) == int:
        if query < 0 or query > len(doc):
            raise Exception(query)
        yield yaml.safe_dump(doc[query])
    elif isinstance(query, list):
        for n in query:
            yield from do_query(doc, n)
    elif isinstance(query, dict):
        for n in query:
            yield from do_query(doc[n], query[n])
    elif type(query) == bool:
        if query and isinstance(doc, dict):
            for k in doc:
                yield yaml.safe_dump(doc[k])
        else:
            for k in doc:
                yield k
    elif query == None:
        yield json.dumps(doc)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: %s query < doc\n" % sys.argv[0], file=sys.stderr)
        print(qyaml.__doc__, file=sys.stderr)
        exit(1)
    try:
        qyaml(sys.stdin, sys.argv[1])
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        exit(1)
