QYAML — simple YAML query engine
================================

Walk synchronously through query and document, and print selected branches of the latter.

Usage:

```sh
qyaml.py "query" < doc.yaml
```

*Example input document*:

```yaml
object:
    key1: value1
    key2: value2
array:
- value3
- value4
```

*Example queries and results*:

`object: key1`

```yaml
value1
```

`object: [key1, key2]`

```yaml
value1
value2
```

`object`

```yaml
{ 'key1': 'value1', 'key2': 'value2' }
```

`object: true`

```yaml
value1
value2
```

`object: false`

```yaml
key1
key2
```

`array: 1`

```yaml
value4
```

`array: [0,1]`

```yaml
value3
value4
```

`array`

```yaml
[ 'value3', 'value4' ]
```

`array: true`

```yaml
value3
value4
```

`[object: key1, array: 0]`

```yaml
value1
value3
```

`null`

```yaml
{'object': {'key1': 'value1', 'key2': 'value2'}, 'array': ['value3', 'value4']}
```
