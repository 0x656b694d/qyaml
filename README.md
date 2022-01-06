QYAML - query YAML with YAML with YAML result
=============================================

Walk synchronously through `query` and `doc`, and print the branches of `doc[query]` as a YAML document.
Single result printed as scalar. Multiple — as list.

DocTest setup

    >>> from qyaml import qyaml, print_results
    >>> def query(q): print_results(qyaml(doc, q))

Example input
-------------

    >>> doc = """
    ... dict:
    ...     key1: alpha
    ...     key2: beta
    ... list: [ 42, 73 ]
    ... """

Querying dictionaries
---------------------

    >>> query('dict: key1')
    alpha
    ...

    >>> query('dict: { key1: alpha }')
    alpha
    ...

    >>> query('dict: [key1, key2]')
    - alpha
    - beta

    >>> query('dict')
    key1: alpha
    key2: beta

    >>> query('dict: true')
    - alpha
    - beta

    >>> query('dict: false')
    - key1
    - key2

    >>> print_results(qyaml('', 'missing'))
    False

Querying lists
---------------

    >>> query('list: 1')
    73
    ...

    >>> query('list: [0,1]')
    - 42
    - 73

    >>> query('list')
    - 42
    - 73

    >>> query('list: { 0: 42 }')
    42
    ...

    >>> query('list: true')
    - 42
    - 73

    >>> query('list: { true: 73 }')
    73
    ...

    >>> query('list: { false: 73 }')
    42
    ...

    >>> query('list: { false: 55 }')
    - 42
    - 73

    >>> query('list: { true: 55 }')

    >>> _=print_results(qyaml('[{a: 1, b: 2}, {a: 3, c: 4}]', 'true: { a: 1 }'))
    a: 1
    b: 2

    >>> _=print_results(qyaml('[{a: 1, b: 2}, {c: 3, d: 4}]', 'true: d'))
    c: 3
    d: 4

    >>> _=print_results(qyaml('[{a: 2}, {a: 1, b: 2}, {a: 1, c: 3}]', '{true: {a: 1}, false: c}'))
    a: 1
    b: 2

Combining
---------

    >>> query('[dict: key1, list: 0]')
    - alpha
    - 42

Query characters
----------------

    >>> query('dict: { key1: [0,3,4]}')
    - a
    - h
    - a

Multiple documents or queries
------------------------------

    >>> _=print_results(qyaml("""dict: alpha
    ... ---
    ... dict: beta""", 'dict'))
    - alpha
    - beta

    >>> _=print_results(qyaml('[1, 2]', """0
    ... ---
    ... 1"""))
    - 1
    - 2

Not implemented
---------------

* YAML error formatting.
