QYAML — query YAML with YAML with YAML result
=============================================

Walk synchronously through `query` and `doc`, and print the branches of `doc[query]` as a YAML document.

Result is printed as a list.

DocTest setup. Run tests with `python -m doctest README.md`.

    >>> from qyaml import qyaml, print_results
    >>> def query(q): print_results(qyaml(doc, q))

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

    >>> query('dict: key1')
    - alpha

    >>> query('dict: { key1: alpha }')
    - alpha

    >>> query('dict: [key1, key2]')
    - alpha
    - beta

    >>> query('dict')
    - key1: alpha
      key2: beta

    >>> query('dict: true')
    - alpha
    - beta

    >>> query('dict: false')
    - key1
    - key2

`print_results` function returns False if nothing found:

    >>> print_results(qyaml('', 'missing'))
    False

Querying lists
---------------

    >>> query('list: 1')
    - second: 73

    >>> query('list: [0,1]')
    - 42
    - second: 73

    >>> query('list: second')
    - 73

    >>> query('list')
    - - 42
      - second: 73
      - third

    >>> query('list: { 0: 42 }')
    - 42

    >>> query('list: { 1: second }')
    - 73

    >>> query('list: true')
    - 42
    - second: 73
    - third

    >>> query('list: { true: second }')
    - second: 73

    >>> query('list: { true: { second: 73 } }')
    - second: 73

    >>> query('list: { false: 42 }')
    - second: 73
    - third

    >>> query('list: { false: [ 42, third ] }')
    - second: 73

    >>> query('list: { true: 55 }')

    >>> _=print_results(qyaml('[["a"], ["a","b"], ["a","c"]]', '{true: a, false: c}'))
    - - a
    - - a
      - b

Combining
---------

    >>> query('[dict: key1, list: 0]')
    - alpha
    - 42

Query characters
----------------

    >>> query('dict: {key1: [0,3,4]}')
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
