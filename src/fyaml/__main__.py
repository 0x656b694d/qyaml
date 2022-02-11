#!/usr/bin/env python3

import sys
from .fyaml import print_results, flatten, Args


def main():
    print_results(flatten(sys.stdin, Args(sys.argv)))


if __name__ == '__main__':
    sys.exit(main())
