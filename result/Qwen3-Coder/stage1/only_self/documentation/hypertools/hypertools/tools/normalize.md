# `normalize.py`

## `hypertools.tools.normalize.normalize` · *function*

## Summary:
Normalizes input data using various z-score normalization strategies across different dimensions.

## Description:
Applies z-score normalization to input data using different strategies depending on the normalize parameter. This function serves as a centralized normalization utility that can normalize data either across all samples, within each sample, or row-wise. The function is designed to handle mixed data types through optional preprocessing and supports returning either single or multiple normalized datasets.

## Args:
    x (array-like): Input data to be normalized, can be a single array or list of arrays
    normalize (str or bool, optional): Normalization strategy to apply. Options are 'across', 'within', 'row', False, or None. Defaults to 'across'.
    internal (bool, optional): If True, returns list of normalized arrays even if only one array. If False, returns single array when input is single. Defaults to False.
    format_data (bool, optional): If True, preprocesses input data using format_data function before normalization. Defaults to True.

## Returns:
    array or list[array]: Normalized data. Returns a single array when internal=False and input is single, or a list of arrays when internal=True or multiple inputs are provided.

## Raises:
    AssertionError: When normalize parameter is not one of ['across','within','row', False, None].

## Constraints:
    Preconditions:
        - Input x must be compatible with numpy array operations
        - normalize parameter must be one of the allowed values
        - When normalize is 'across', all input arrays must have compatible shapes for stacking
    
    Postconditions:
        - Output data has zero mean and unit variance according to the selected normalization strategy
        - Return type matches the internal parameter specification

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start normalize] --> B{normalize in [False,None]?}
    B -- Yes --> C[Return x]
    B -- No --> D{format_data?}
    D -- Yes --> E[Apply format_data function]
    D -- No --> F[Skip formatting]
    E --> G[Define zscore lambda function]
    F --> G
    G --> H{normalize type}
    H -->|across| I[Stack all arrays vertically]
    H -->|within| J[Normalize within each array]
    H -->|row| K[Normalize row-wise]
    I --> L[Apply zscore across stacked data]
    J --> L
    K --> L
    L --> M{internal OR len>1?}
    M -- Yes --> N[Return list of normalized arrays]
    M -- No --> O[Return first normalized array]
```

## Examples:
    # Basic usage with default across normalization
    normalized_data = normalize(data)
    
    # Normalize within each array
    normalized_data = normalize(data, normalize='within')
    
    # Return list even for single array
    normalized_list = normalize(data, internal=True)
    
    # Skip data formatting
    normalized_data = normalize(data, format_data=False)
``

