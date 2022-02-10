# Tests and Examples

Run tests with `python -m doctest tests/doctests.md`.

<details>
    <summary>DocTest setup</summary>

    >>> from src.qyaml.qyaml import qyaml, print_results
    >>> qy = qyaml
    >>> def qyaml(d, q): print_results(qy(d, q))

</details>

## Example input

    >>> doc = """
    ... dict:
    ...   key1: alpha
    ...   key2: beta
    ... list: [ 42, { second: 73 }, 'third' ]
    ... """

## Querying dictionaries

    >>> qyaml(doc, 'dict: key1')
    - dict:
        key1: alpha

    >>> qyaml(doc, 'dict: { key1: alpha }')
    - dict:
        key1: alpha

    >>> qyaml(doc, 'dict: [key1, key2]')
    - dict:
        key1: alpha
    - dict:
        key2: beta

    >>> qyaml(doc, 'dict: key.')
    - dict:
        key1: alpha
    - dict:
        key2: beta

    >>> qyaml(doc, 'dict')
    - dict:
        key1: alpha
        key2: beta

    >>> qyaml(doc, 'dict: true')
    - dict:
        key1: alpha
    - dict:
        key2: beta

    >>> qyaml(doc, 'dict: false')
    - dict: key1
    - dict: key2

    >>> qyaml('', 'missing')

    >>> qyaml("""---
    ... key1:
    ...   value: good
    ...   criterium: one
    ... key2:
    ...   value: bad
    ...   criterium: two
    ... key3:
    ...   value: good too
    ...   criterium: none
    ... """, '"key.": [criterium: "n?one", value]')
    - key1:
        criterium: one
    - key1:
        value: good
    - key3:
        criterium: none
    - key3:
        value: good too

## Querying lists

    >>> qyaml(doc, 'list: 1')
    - list:
        second: 73

    >>> qyaml(doc, '[list: 0, list: 1]')
    - list: 42
    - list:
        second: 73

    >>> qyaml(doc, 'list: second')
    - list:
        second: 73

    >>> qyaml(doc, 'list: s.*')
    - list:
        second: 73

    >>> qyaml('a: [{b: {c: d}},{b: {c: e}}]', 'a: {b: c}')
    - a:
        b:
          c: d
    - a:
        b:
          c: e

    >>> qyaml(doc, 'list')
    - list:
      - 42
      - second: 73
      - third

    >>> qyaml(doc, 'list: { 0: 42 }')
    - list: 42

    >>> qyaml(doc, 'list: { 1: second }')
    - list:
        second: 73

    >>> qyaml(doc, 'list: { true: second }')
    - list:
        second: 73

    >>> qyaml(doc, 'list: { true: { second: 73 } }')
    - list:
        second: 73

    >>> qyaml(doc, 'list: { false: 42 }')
    - list:
        second: 73
    - list: third

    >>> qyaml(doc, 'list: { false: [ 42, third ] }')
    - list:
        second: 73

    >>> qyaml(doc, 'list: { true: 55 }')

    >>> qyaml('[["a"], ["a","b"], ["a","c"]]', '{true: a, false: c}')
    - - a
    - - a
      - b

## Combining

    >>> qyaml(doc, '[dict: key1, list: 0]')
    - dict:
        key1: alpha
    - list: 42

    >>> qyaml("""dict: {list: [
    ...    {key1: value1, key2: value2, key3: value3},
    ...    {key1: value4, key2: value5, key3: value6}
    ... ]}""", 'dict: [list: [key1, key2]]')
    - dict:
        list:
        - key1: value1
        - key2: value2
    - dict:
        list:
        - key1: value4
        - key2: value5

## Query characters

    >>> qyaml(doc, 'dict: {key1: [0, 3, 4]}')
    - dict:
        key1: a
    - dict:
        key1: h
    - dict:
        key1: a

## Multiple documents or queries

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
