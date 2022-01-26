QYAML — query YAML with YAML with YAML result
=============================================

Walk synchronously through `query` and `doc`, and print the branches of `doc[query]` as a YAML document.

Result is printed to standard output as a list of found matches. The output may be formatted with `fyaml` to flatten the list (default behavior) or keep the keys with `keys` argument, or format as a JSON string with `json` argument:

    $ cat file.yaml | qyaml key | fyaml
    value

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
    - key1: alpha

    >>> qyaml(doc, 'dict: { key1: alpha }')
    - alpha

    >>> qyaml(doc, 'dict: [key1, key2]')
    - key1: alpha
    - key2: beta

    >>> qyaml(doc, 'dict')
    - dict:
        key1: alpha
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

    >>> qyaml(doc, '[list: 0, list: 1]')
    - 42
    - second: 73

    >>> qyaml(doc, 'list: second')
    - second: 73

    >>> qyaml('a: [{b: {c: d}},{b: {c: e}}]', 'a: {b: c}')
    - c: d
    - c: e

    >>> qyaml(doc, 'list')
    - list:
      - 42
      - second: 73
      - third

    >>> qyaml(doc, 'list: { 0: 42 }')
    - 42

    >>> qyaml(doc, 'list: { 1: second }')
    - second: 73

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
    - key1: alpha
    - 42

    >>> qyaml("""dict: {list: [
    ...    {key1: value1, key2: value2, key3: value3},
    ...    {key1: value4, key2: value5, key3: value6}
    ... ]}""", 'dict: [list: [key1, key2]]')
    - key1: value1
    - key2: value2
    - key1: value4
    - key2: value5

Query characters
----------------

    >>> qyaml(doc, 'dict: {key1: [0, 3, 4]}')
    - a
    - h
    - a

Multiple documents or queries
------------------------------

    >>> qyaml("""dict: alpha
    ... ---
    ... dict: beta""", 'dict')
    - dict: alpha
    - dict: beta

    >>> qyaml('[1, 2]', """0
    ... ---
    ... 1""")
    - 1
    - 2
