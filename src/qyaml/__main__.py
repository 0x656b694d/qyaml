#!/usr/bin/env python3

import sys
from .qyaml import print_results, parse


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        print("\nUsage: %s query < doc" %
              sys.argv[0], file=sys.stderr)
        exit(1)

    try:
        ok = print_results(parse(sys.stdin, *sys.argv[1:]))
        exit(0 if ok else 1)
    except Exception as err:
        print("Error:", err, file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
