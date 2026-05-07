# `normalize.py`

## `hypertools.tools.normalize.normalize` · *function*

## Summary:
Applies z-score normalization to data arrays using various normalization strategies including across-features, within-features, and row-wise normalization.

## Description:
This function performs z-score normalization on input data arrays using different strategies. It can normalize data across all features, within each feature independently, or row-wise. The function supports preprocessing of input data and handles edge cases such as zero variance features. Note: There is a bug in the implementation where `formatter` is referenced instead of `format_data` - this will cause a runtime error.

## Args:
    x (array-like): Input data to be normalized, can be a single array or list of arrays
    normalize (str or bool, optional): Normalization strategy to apply. Options are 'across', 'within', 'row', False, or None. Defaults to 'across'.
    internal (bool, optional): If True, returns list of normalized arrays even if only one array was input. Defaults to False.
    format_data (bool, optional): If True, preprocesses input data using format_data function before normalization. Defaults to True.

## Returns:
    array or list[array]: Normalized data. Returns a single array if only one input array and internal=False, otherwise returns a list of normalized arrays.

## Raises:
    AssertionError: When normalize parameter is not one of ['across','within','row', False, None].

## Constraints:
    Preconditions:
    - Input x must be compatible with numpy array operations
    - normalize parameter must be one of the allowed values
    
    Postconditions:
    - Output arrays have mean≈0 and std≈1 for the respective normalization dimension
    - If format_data=True, input is preprocessed using format_data function
    - For constant features (single unique value), normalized values are all zeros

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start normalize] --> B{normalize in [False,None]?}
    B -- Yes --> C[Return x unchanged]
    B -- No --> D{format_data?}
    D -- Yes --> E[Apply format_data to x]
    D -- No --> F[Skip formatting]
    E --> G[Define zscore lambda]
    F --> G
    G --> H{normalize type}
    H -->|across| I[Stack arrays vertically]
    H -->|within| J[Process each array separately]
    H -->|row| K[Process rows separately]
    I --> L[Apply zscore across stacked data]
    J --> L
    K --> L
    L --> M{internal OR len>1?}
    M -- Yes --> N[Return list of normalized arrays]
    M -- No --> O[Return first normalized array]
```

## Examples:
```python
# Basic usage with default 'across' normalization
data = [[1, 2, 3], [4, 5, 6]]
normalized = normalize(data)

# Using 'within' normalization (normalizes each feature independently)
normalized = normalize(data, normalize='within')

# Using 'row' normalization (normalizes each row independently)
normalized = normalize(data, normalize='row')

# Disable formatting and normalization
result = normalize(data, format_data=False, normalize=None)

# Force returning list even with single array
single_array = normalize(data, internal=True)

# Edge case: constant feature (will result in zeros)
constant_data = [[1, 1, 1], [1, 1, 1]]
normalized = normalize(constant_data, normalize='within')
```

