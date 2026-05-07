# `normalize.py`

## `hypertools.tools.normalize.normalize` · *function*

## Summary:
Normalizes input data using z-score standardization across specified dimensions.

## Description:
This function applies z-score normalization to input data, allowing for different normalization strategies including across all samples, within each sample, or row-wise. It serves as a preprocessing utility for preparing data for downstream analysis such as dimensionality reduction or clustering.

The function is extracted into its own component to encapsulate the normalization logic and provide reusable normalization capabilities across different parts of the hypertools framework. This promotes code reuse and maintains clean separation of concerns by keeping data preprocessing logic distinct from core analytical operations.

## Args:
    x (array-like): Input data to be normalized, can be a single array or list of arrays
    normalize (str or bool, optional): Normalization strategy. Options are 'across', 'within', 'row', False, or None. Defaults to 'across'.
    internal (bool, optional): Flag indicating if the function is being called internally. When True, returns list even for single array. Defaults to False.
    format_data (bool, optional): Whether to apply data formatting before normalization. When True, processes input through format_data function. Defaults to True.

## Returns:
    array or list: Normalized data. Returns single array if internal=False and single input, otherwise returns list of normalized arrays.

## Raises:
    AssertionError: If normalize parameter is not one of ['across','within','row', False, None].

## Constraints:
    Preconditions:
        - Input x must be compatible with numpy array operations
        - normalize parameter must be one of the allowed values
    Postconditions:
        - Output data has zero mean and unit variance according to the chosen normalization strategy
        - If format_data=True, input is processed through format_data function before normalization

## Side Effects:
    - May call format_data function which could involve text processing and data alignment
    - Uses numpy operations for mathematical computations
    - May issue warnings about missing data when using PPCA

## Control Flow:
```mermaid
flowchart TD
    A[Start normalize] --> B{normalize in [False,None]?}
    B -- Yes --> C[Return x]
    B -- No --> D{format_data?}
    D -- Yes --> E[Call format_data]
    D -- No --> F[Skip format_data]
    E --> F
    F --> G{normalize type}
    G -->|across| H[Stack arrays vertically]
    G -->|within| I[Process each array separately]
    G -->|row| J[Process rows separately]
    H --> K[Apply zscore across stacked data]
    I --> K
    J --> K
    K --> L{internal OR len>1?}
    L -- Yes --> M[Return list]
    L -- No --> N[Return first element]
```

## Examples:
```python
# Basic usage with default 'across' normalization
data = [[1, 2, 3], [4, 5, 6]]
normalized = normalize(data)

# Using 'within' normalization
normalized = normalize(data, normalize='within')

# Disabling data formatting
normalized = normalize(data, format_data=False)

# Internal usage returning list
normalized_list = normalize(data, internal=True)
```

