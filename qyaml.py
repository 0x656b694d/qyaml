#!/usr/bin/env python3

import sys
import yaml

help = """
usage: %s <yaml query>

Walk synchronously through query and doc, and print the branches of doc[query]

Example input document:

    object:
        key1: value1
        key2: value2
    array:
    - value3
    - value4

Example queries:

>> "object: key1"
value1

>> "object: [key1, key2]"
value1
value2

>> "object"
{ 'key1': 'value1', 'key2': 'value2' }

>> "object: true"
value1
value2

>> "object: false"
key1
key2

>> "array: 1"
value4

>> "array: [0,1]"
value3
value4

>> "array"
[ 'value3', 'value4' ]

>> "array: true"
value3
value4

>> "[object: key1, array: 0]"
value1
value3

>> "null"
{'object': {'key1': 'value1', 'key2': 'value2'}, 'array': ['value3', 'value4']}

"""


def do_query(doc, query):
    if isinstance(query, str) or type(query) == int:
        yield doc[query]
    elif isinstance(query, list):
        for n in query:
            yield from do_query(doc, n)
    elif isinstance(query, dict):
        for n in query:
            yield from do_query(doc[n], query[n])
    elif type(query) == bool:
        if query and isinstance(doc, dict):
            for k in doc: yield doc[k]
        else:
            for k in doc: yield k
    elif query == None:
        yield doc

def main():
    if len(sys.argv) != 2:
        print(help % sys.argv[0], file=sys.stderr)
        exit(1)

    for doc in yaml.safe_load_all(sys.stdin):
        for query in yaml.safe_load_all(sys.argv[1]):
            for value in do_query(doc, query):
                print(value)


if __name__ == '__main__':
    main()
