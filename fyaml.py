#!/usr/bin/env python3

import sys
import yaml
import json


def print_results(docs, args):
    for d in fyaml(docs, args):
        print(d)


def fyaml(docs, args):
    if args.json:
        result = []
        for doc in yaml.safe_load_all(docs):
            result.extend(format(doc, args))
        yield json.dumps(result)
    else:
        for doc in yaml.safe_load_all(docs):
            yield from format(doc, args)


def format(doc, args):
    dt = type(doc)
    if dt == dict:
        for p in doc.items():
            yield from format(p, args)
    elif dt == list:
        for p in doc:
            yield from format(p, args)
    elif dt == tuple:
        k, v = doc
        if args.keys and type(v) in [int, float, str, bool]:
            yield {k: v} if args.json else "{}: {}".format(k, v)
        else:
            yield from format(v, args)
    elif dt in [int, float, str, bool]:
        yield doc


class Args(object):
    def __init__(self, argv) -> None:
        self.keys = "keys" in argv
        self.json = "json" in argv


if __name__ == '__main__':
    print_results(sys.stdin, Args(sys.argv))
