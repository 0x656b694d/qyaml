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
$ qyaml "dict: first" < file.yaml
- dict:
    first: value1
```

The query is itself a YAML document.

The output may be flatten with `fyaml` to only values (default behavior) or preserving the keys with `keys` argument, or format as a JSON string with `json` argument:

```shell
$ cat file.yaml | qyaml "dict: first" | fyaml
value1

$ cat file.yaml | qyaml "dict: first" | fyaml keys
first: value1

$ cat file.yaml | qyaml dict | fyaml json
["value1", "value2"]

$ cat file.yaml | qyaml dict | fyaml json keys
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

