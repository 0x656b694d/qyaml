QYAML - query YAML with YAML with YAML result
=============================================

Walk synchronously through `query` and `doc`, and print the branches of `doc[query]` as a YAML document.
Single result printed as scalar. Multiple — as list.

DocTest setup

    >>> from qyaml import qyaml, print_results
    >>> def query(q): print_results(qyaml(doc, q))

Example input
-------------

    >>> doc = '{ dict: { key1: "alpha", key2: "beta" }, list: [ 42, 73 ] }'

Querying dictionaries
---------------------

    >>> query('dict: key1')
    alpha
    ...

    >>> query('dict: { key1: alpha }')
    true
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
    true
    ...

    >>> query('list: true')
    - 42
    - 73

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

Errors
------

    >>> query('missing')
    Traceback (most recent call last):
    ...
    Exception: ['missing']

Multiple documents or queries
------------------------------

    >>> print_results(qyaml("""dict: alpha
    ... ---
    ... dict: beta""", 'dict'))
    - alpha
    - beta

    >>> print_results(qyaml('[1, 2]', """0
    ... ---
    ... 1"""))
    - 1
    - 2
