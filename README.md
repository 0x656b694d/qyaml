QYAML — query YAML with YAML with YAML result
=============================================

Walk synchronously through `query` and `doc`, and print the list of matching branches of `doc` as a YAML document.

Result is printed to standard output as a list of found matches, including their keys.

Given `file.yaml`:

```yaml
dict:
  first: value1
  second: value2
```

QYAML may be used to query, for example, the value of the `first` key of the `dict` dictionary:

```shell
$ qyaml.py "dict: first" < file.yaml
- dict:
    first: value1
```

The query is itself a YAML document.

The output may be flatten with `fyaml` to only values (default behavior) or preserving the keys with `keys` argument, or format as a JSON string with `json` argument:

```shell
$ cat file.yaml | qyaml.py "dict: first" | fyaml
value1
$ cat file.yaml | qyaml.py "dict: first" | fyaml keys
first: value1
$ cat file.yaml | qyaml.py dict | fyaml json
["value1", "value2"]
$ cat file.yaml | qyaml.py dict | fyaml json keys
[{"first": "value1"}, {"second": "value2"}]
```

Query rules
-----------

| Query\Document  | String      | Number | Boolean |        List                  |   Dictionary      |
|-----------------|-------------|--------|---------|------------------------------|-------------------|
| String (regexp) | regex-match |   -    |    -    | regex-match list elements    | regex-match keys  |
| Number          | `str[i]`    | match  |    -    | `list[i]`                    | -                 |
| Boolean         |      -      |   -    | match   | -                            | b ? values : keys |
| List            | for-each    |   -    |    -    | match `list[i]` for each `q` | search keys       |
| Dictionary      |      -      |   -    |    -    | i: match, bool: filter       | key:value match   |

## Tests and Examples

Run tests with `python -m doctest README.md`.

<details>
    <summary>DocTest setup</summary>

    >>> from qyaml import qyaml, print_results
    >>> qy = qyaml
    >>> def qyaml(d, q): print_results(qy(d, q))

</details>

#### Example input

    >>> doc = """
    ... dict:
    ...     key1: alpha
    ...     key2: beta
    ... list: [ 42, { second: 73 }, 'third' ]
    ... """

### Querying dictionaries

    >>> qyaml(doc, 'dict: key1')
    - dict:
      - key1: alpha

    >>> qyaml(doc, 'dict: { key1: alpha }')
    - dict:
      - key1:
        - alpha

    >>> qyaml(doc, 'dict: [key1, key2]')
    - dict:
      - key1: alpha
      - key2: beta

    >>> qyaml(doc, 'dict: key.')
    - dict:
      - key1: alpha
      - key2: beta

    >>> qyaml(doc, 'dict')
    - dict:
        key1: alpha
        key2: beta

    >>> qyaml(doc, 'dict: true')
    - dict:
      - key1: alpha
      - key2: beta

    >>> qyaml(doc, 'dict: false')
    - dict:
      - key1
      - key2

    >>> qyaml('', 'missing')

### Querying lists

    >>> qyaml(doc, 'list: 1')
    - list:
      - second: 73

    >>> qyaml(doc, '[list: 0, list: 1]')
    - list:
      - 42
    - list:
      - second: 73

    >>> qyaml(doc, 'list: second')
    - list:
      - second: 73

    >>> qyaml(doc, 'list: s.*')
    - list:
      - second: 73

    >>> qyaml('a: [{b: {c: d}},{b: {c: e}}]', 'a: {b: c}')
    - a:
      - b:
        - c: d
      - b:
        - c: e

    >>> qyaml(doc, 'list')
    - list:
      - 42
      - second: 73
      - third

    >>> qyaml(doc, 'list: { 0: 42 }')
    - list:
      - 42

    >>> qyaml(doc, 'list: { 1: second }')
    - list:
      - second: 73

    >>> qyaml(doc, 'list: { true: second }')
    - list:
      - second: 73

    >>> qyaml(doc, 'list: { true: { second: 73 } }')
    - list:
      - second: 73

    >>> qyaml(doc, 'list: { false: 42 }')
    - list:
      - second: 73
      - third

    >>> qyaml(doc, 'list: { false: [ 42, third ] }')
    - list:
      - second: 73

    >>> qyaml(doc, 'list: { true: 55 }')

    >>> qyaml('[["a"], ["a","b"], ["a","c"]]', '{true: a, false: c}')
    - - a
    - - a
      - b

### Combining

    >>> qyaml(doc, '[dict: key1, list: 0]')
    - dict:
      - key1: alpha
    - list:
      - 42

    >>> qyaml("""dict: {list: [
    ...    {key1: value1, key2: value2, key3: value3},
    ...    {key1: value4, key2: value5, key3: value6}
    ... ]}""", 'dict: [list: [key1, key2]]')
    - dict:
      - list:
        - - key1: value1
          - key2: value2
        - - key1: value4
          - key2: value5

### Query characters

    >>> qyaml(doc, 'dict: {key1: [0, 3, 4]}')
    - dict:
      - key1:
        - a
        - h
        - a

### Multiple documents or queries

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
