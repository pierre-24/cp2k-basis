# REST API reference

## `/api/<type>/<name>/data`

Obtain data.

`<type>` can be:

+ `basis` to obtain basis set `<name>` (e.g., `/api/basis/SZV-MOLOPT-GTH/data`). 
+ `pseudopotentials` to obtain pseudopotential `<name>` (e.g. `/api/pseudopotentials/GTH-BLYP/data`).

Options are:

| Option     | Argument | Description                                 |
|------------|----------|---------------------------------------------|
| `elements` | String   | Restrict the output to a subset of elements |

 The output is in JSON, and contains the following data:

```js
response = {
  "query": {
    "name": "<name>",
    // ... other options
  },
  "result": "STRING"
}
```

`response.results` contains the requested data in CP2K format.
