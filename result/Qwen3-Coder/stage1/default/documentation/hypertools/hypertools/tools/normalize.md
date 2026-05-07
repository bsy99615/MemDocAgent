# `normalize.py`

## `hypertools.tools.normalize.normalize` · *function*

## Summary:
Normalizes input data using various z-score normalization strategies including across-all, within-dataset, and row-wise normalization.

## Description:
This function applies z-score normalization to input data using different strategies depending on the normalize parameter. It's designed to handle mixed data types (numerical and text) by optionally formatting the data first. The function supports multiple normalization approaches: across-all datasets, within-each-dataset, and row-wise normalization. This logic is extracted into a separate function to provide reusable normalization capabilities across different parts of the hypertools library.

## Args:
    x (array-like or list): Input data to normalize. Can be a single array or list of arrays.
    normalize (str or bool, optional): Normalization strategy. Options are 'across', 'within', 'row', False, or None. Defaults to 'across'.
    internal (bool, optional): If True, returns list even for single dataset. If False and single dataset, returns array directly. Defaults to False.
    format_data (bool, optional): If True, formats the data before normalization using the format_data function. Defaults to True.

## Returns:
    array or list: Normalized data. Returns a single array if internal=False and single dataset, otherwise returns a list of normalized arrays.

## Raises:
    AssertionError: If normalize parameter is not one of ['across','within','row', False, None].

## Constraints:
    Preconditions:
    - Input x should be array-like or list of array-like objects
    - normalize parameter must be one of ['across','within','row', False, None]
    - When normalize is 'across', all datasets must have compatible shapes for stacking
    
    Postconditions:
    - Output data has mean=0 and std=1 for the respective normalization type
    - Return type depends on internal flag and input size

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start normalize] --> B{normalize in [False,None]?}
    B -- Yes --> C[Return x unchanged]
    B -- No --> D{format_data?}
    D -- Yes --> E[Call format_data(x, ppca=True)]
    D -- No --> F[Skip formatting]
    E --> G[Define zscore lambda]
    F --> G
    G --> H{normalize type}
    H -->|across| I[Stack all datasets vertically]
    H -->|within| J[Normalize within each dataset]
    H -->|row| K[Normalize each row]
    I --> L[Apply zscore to stacked data]
    J --> L
    K --> L
    L --> M{internal OR len>1?}
    M -- Yes --> N[Return normalized_x list]
    M -- No --> O[Return normalized_x[0]]
```

## Examples:
```python
# Basic usage with default across normalization
data = [[1, 2, 3], [4, 5, 6]]
normalized = normalize(data)

# Within-dataset normalization
normalized = normalize(data, normalize='within')

# Row-wise normalization
normalized = normalize(data, normalize='row')

# No normalization
normalized = normalize(data, normalize=None)
```

