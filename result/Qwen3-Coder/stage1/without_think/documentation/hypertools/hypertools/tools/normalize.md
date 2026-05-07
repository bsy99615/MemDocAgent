# `normalize.py`

## `hypertools.tools.normalize.normalize` · *function*

## Summary:
Normalizes input data using z-score normalization with multiple strategies including across-features, within-features, and row-wise normalization.

## Description:
Applies z-score normalization to input data using different strategies. This function serves as a centralized normalization utility that can handle various data types and normalization approaches. The function is extracted to provide reusable normalization logic across different parts of the hypertools library, allowing consistent preprocessing of data before analysis or visualization.

## Args:
    x (array-like): Input data to normalize, can be a single array or list of arrays
    normalize (str or bool, optional): Normalization strategy to apply. Options are 'across', 'within', 'row', False, or None. Defaults to 'across'.
    internal (bool, optional): If True, returns list of normalized arrays even if single array. Defaults to False.
    format_data (bool, optional): If True, preprocesses input data using format_data function. Defaults to True.

## Returns:
    array or list[array]: Normalized data. Returns a single array if input is single array and internal=False and normalized_x contains only one element, otherwise returns list of normalized arrays. When normalization produces constant features (single unique value), returns zero array for those features.

## Raises:
    AssertionError: When normalize parameter is not one of ['across','within','row', False, None].

## Constraints:
    Preconditions:
        - Input x must be compatible with numpy operations
        - normalize parameter must be one of the allowed values
    Postconditions:
        - Output data has zero mean and unit variance according to selected normalization strategy
        - For constant features (single unique value), returns zero array instead of NaN
        - Return type matches input structure based on internal flag and input size

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start normalize] --> B{normalize in [False,None]?}
    B -- Yes --> C[Return x]
    B -- No --> D{format_data?}
    D -- Yes --> E[Call format_data]
    D -- No --> F[Skip formatting]
    E --> G[Define zscore lambda]
    F --> G
    G --> H{normalize type}
    H -->|across| I[Stack arrays vertically]
    H -->|within| J[Process each array internally]
    H -->|row| K[Process rows individually]
    I --> L[Apply zscore across stacked features]
    J --> L
    K --> L
    L --> M{internal OR len(normalized_x)>1?}
    M -- Yes --> N[Return normalized_x]
    M -- No --> O[Return normalized_x[0]]
```

## Examples:
    # Basic usage with default across normalization
    normalized_data = normalize(data)
    
    # Within-feature normalization
    normalized_data = normalize(data, normalize='within')
    
    # Disable normalization
    raw_data = normalize(data, normalize=False)
    
    # With custom parameters
    normalized_data = normalize(data, normalize='row', internal=True)
``

