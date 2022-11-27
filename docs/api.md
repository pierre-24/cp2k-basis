# REST API reference

## Preamble

### Request

This API can be used to retrieve two types (`<type>`) of data, either basis sets (`basis`) or pseudopotentials (`pseudopotentials`).
Each of them has a name (`<name>`).

Options are added as query string: `/api/example?option1=value&option2=value`.

### On the `elements` option

Every time the option `elements` can be used,
+ you can use a list of comma separated atomic symbols, e.g., `C,H,N,O`,
+ but also ranges, e.g., `H,C-O`, and
+ Z numbers can be used instead of symbols, e,g., `H,6-8`.

Elements are limited to Z ≤ 92, i.e., hydrogen to uranium.
If you want to perform calculations outside this range, you probably have other problems on your plate than finding a basis set ;)


### Response format

The response is in JSON, and always contains two main fields:

```json
{
  "query": {},
  "result": {}
}
```

`query` contains the request, to which `result` is the answer.

## Routes

### `/api/<type>/<name>/data`

Obtain data in the CP2K format.

Options:

| Option     | Argument | Description                                                                                                                        |
|------------|----------|------------------------------------------------------------------------------------------------------------------------------------|
| `elements` | String   | Restrict the output to a subset of elements. If some elements are not defined for this basis set/pseudopotential, a 404 is raised. |


Output:

| Field      | Name       | Type           | Description                                                             |
|------------|------------|----------------|-------------------------------------------------------------------------|
| `query`    | `name`     | string         | The name you requested                                                  |
| `query`    | `type`     | string         | `BASIS_SET` or `PSEUDOPOTENTIAL`                                        |
| `result`   | `data`     | string         | The resulting basis set or pseudopotential, in CP2K format              |
| `result`   | `elements` | list of string | Elements for which there is data (matches the option `elements` if set) |

### `/api/<type>/<name>/metadata`

Obtain metadata about a basis set or pseudopotential. There is no option.

Output:

| Field    | Name         | Type           | Description                                                  |
|----------|--------------|----------------|--------------------------------------------------------------|
| `query`  | `name`       | string         | The name you requested                                       |
| `query`  | `type`       | string         | `BASIS_SET` or `PSEUDOPOTENTIAL`                             |
| `result` | `elements`   | list of string | Elements for which the basis set/pseudopotential are defined |
| `result` | `references` | list of string | List of URL to articles or repositories                      |
| `result` | `source`     | string         | URL to the file which was used to create the data            |
