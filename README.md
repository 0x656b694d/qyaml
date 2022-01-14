QYAML — query YAML with YAML with YAML result
=============================================

Walk synchronously through `query` and `doc`, and print the branches of `doc[query]` as a YAML document.

Result is printed as a list.

DocTest setup. Run tests with `python -m doctest README.md`.

    >>> from qyaml import qyaml, print_results
    >>> qy = qyaml
    >>> def qyaml(d, q): print_results(qy(d, q))

Example input
-------------

    >>> doc = """
    ... dict:
    ...     key1: alpha
    ...     key2: beta
    ... list: [ 42, { second: 73 }, 'third' ]
    ... """

Querying dictionaries
---------------------

    >>> qyaml(doc, 'dict: key1')
    - alpha

    >>> qyaml(doc, 'dict: { key1: alpha }')
    - alpha

    >>> qyaml(doc, 'dict: [key1, key2]')
    - alpha
    - beta

    >>> qyaml(doc, 'dict')
    - key1: alpha
      key2: beta

    >>> qyaml(doc, 'dict: true')
    - alpha
    - beta

    >>> qyaml(doc, 'dict: false')
    - key1
    - key2

    >>> qyaml('', 'missing')

Querying lists
---------------

    >>> qyaml(doc, 'list: 1')
    - second: 73

    >>> qyaml(doc, 'list: [0, 1]')
    - 42
    - second: 73

    >>> qyaml(doc, 'list: second')
    - 73

    >>> qyaml('a: [{b: {c: d}},{b: {c: e}}]', 'a: {b: c}')
    - d
    - e

    >>> qyaml(doc, 'list')
    - - 42
      - second: 73
      - third

    >>> qyaml(doc, 'list: { 0: 42 }')
    - 42

    >>> qyaml(doc, 'list: { 1: second }')
    - 73

    >>> qyaml(doc, 'list: { true: second }')
    - second: 73

    >>> qyaml(doc, 'list: { true: { second: 73 } }')
    - second: 73

    >>> qyaml(doc, 'list: { false: 42 }')
    - second: 73
    - third

    >>> qyaml(doc, 'list: { false: [ 42, third ] }')
    - second: 73

    >>> qyaml(doc, 'list: { true: 55 }')

    >>> qyaml('[["a"], ["a","b"], ["a","c"]]', '{true: a, false: c}')
    - - a
    - - a
      - b

Combining
---------

    >>> qyaml(doc, '[dict: key1, list: 0]')
    - alpha
    - 42

Query characters
----------------

    >>> qyaml(doc, 'dict: {key1: [0,3,4]}')
    - a
    - h
    - a

Multiple documents or queries
------------------------------

    >>> qyaml("""dict: alpha
    ... ---
    ... dict: beta""", 'dict')
    - alpha
    - beta

    >>> qyaml('[1, 2]', """0
    ... ---
    ... 1""")
    - 1
    - 2
