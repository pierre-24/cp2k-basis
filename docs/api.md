# REST API reference

## On the `elements` option

Every time the option `elements` can be used,
+ you can use a list of comma separated atomic symbols, e.g., `C,H,N,O`,
+ but also ranges, e.g., `H,C-O`, and
+ Z numbers can be used instead of symbols, e,g., `H,6-8`.

Elements are limited to Z ≤ 92, i.e., hydrogen to uranium.
If you want to perform calculations outside this range, you probably have other problems on your plate than finding a basis set ;)

## `/api/<type>/<name>/data`

Obtain data.

`<type>` can be:

+ `basis` to obtain basis set `<name>` (e.g., `/api/basis/SZV-MOLOPT-GTH/data`). 
+ `pseudopotentials` to obtain pseudopotential `<name>` (e.g. `/api/pseudopotentials/GTH-BLYP/data`).

Options are:

| Option     | Argument | Description                                                                                     |
|------------|----------|-------------------------------------------------------------------------------------------------|
| `elements` | String   | Restrict the output to a subset of elements. If some elements are not present, a 404 is raised. |



The output is in JSON, and contains the following data:

```js
response = {
  "query": {
    "name": "<name>",
    // ... other options
  },
  "result": "requested data in CP2K format."
}
```

## `/api/<type>/<name>/metadata`

Obtain metadata on a basis set (`<type>` is `basis`) or GTH potential (`<type>` is `pseudopotentials`).

There is no option.

The output is in JSON, and contains the following data:

```js
response = {
  "query": {
    "name": "<name>"
  },
  "result": {
      "description": "a textual description",
      "elements": [...], // elements for which it is available
      "references": [...], // list of URL to papers or other sources
      "source": "https://URL" // original file from which it was gathered.
  }
}
```

Other metadata might be added in the future.