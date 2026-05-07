# `reduce.py`

## `hypertools.tools.reduce.reduce` · *function*

## Summary:
Performs dimensionality reduction on data using various algorithms including PCA, ICA, UMAP, and others.

## Description:
The reduce function applies dimensionality reduction techniques to input data, supporting both built-in algorithms and custom models. It handles multiple data arrays by stacking them together for consistent transformation while preserving their original structure in the output. The function provides flexibility in specifying reduction methods through string names, dictionaries, or direct model instances.

This logic is extracted into its own function to encapsulate the complexity of handling different reduction algorithms, parameter validation, data formatting, and post-processing while providing a unified interface for dimensionality reduction operations throughout the hypertools library.

## Args:
    x: Input data to be reduced. Can be a single array or list of arrays.
    reduce (str or dict or object): Reduction technique to apply. Can be:
        - String name of a supported algorithm (e.g., 'PCA', 'UMAP', 'IncrementalPCA') 
        - Dictionary with 'model' and 'params' keys for custom configurations
        - Direct instance of a reduction model with fit_transform method
        Defaults to 'IncrementalPCA'
    ndims (int, optional): Number of dimensions to reduce to. If None, uses default behavior.
    normalize (str or None, optional): Deprecated normalization method. Will be removed in future versions.
    align (str or None, optional): Deprecated alignment method. Will be removed in future versions.
    model (str or None, optional): Deprecated parameter. Use 'reduce' instead.
    model_params (dict or None, optional): Deprecated parameter. Use 'reduce' instead.
    internal (bool): If True, returns list even for single array input. If False, returns single array when appropriate.
    format_data (bool): If True, applies data formatting before reduction.

## Returns:
    Array or list of arrays: Reduced dimensional data. Returns a list when multiple arrays are input or when internal=True. Returns a single array when internal=False and single array input.

## Raises:
    ValueError: If reduce parameter is not a supported option or doesn't have required methods, or if dictionary format is incorrect.
    KeyError: If dictionary passed to reduce lacks required keys.

## Constraints:
    Preconditions:
    - Input data must be compatible for vertical stacking with np.vstack
    - If using string-based model specification, model name must be available in internal models registry
    - If using custom model, it must have fit_transform and n_components attributes
    - Data arrays must have compatible shapes for stacking
    
    Postconditions:
    - Output maintains the structural relationship of input data chunks
    - Dimensionality reduction is applied consistently across all data
    - Appropriate warning messages are issued for edge cases

## Side Effects:
    - Issues deprecation warnings for normalize and align parameters
    - Issues deprecation warnings for model and model_params parameters
    - May modify input data through formatting operations when format_data=True

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce] --> B{model or model_params provided?}
    B -- Yes --> C[Warn about deprecation]
    C --> D[Set reduce to dict format]
    B -- No --> E[Continue with reduce parameter]
    E --> F{reduce is None?}
    F -- Yes --> G[Return x unchanged]
    F -- No --> H{reduce is str/string?}
    H -- Yes --> I[Set model_name, set model_params]
    H -- No --> J{reduce is dict?}
    J -- Yes --> K[Extract model_name, model_params from dict]
    J -- No --> L[Set model_name to reduce directly]
    L --> M{model_name is str?}
    M -- Yes --> N[Get model from models registry]
    M -- No --> O[Validate custom model has required methods]
    O --> P[Handle n_components conflict]
    P --> Q[Format data if requested]
    Q --> R{ndims is None or all arrays small enough?}
    R -- Yes --> S[Return formatted data]
    R -- No --> T[Stack data with np.vstack]
    T --> U{stacked_x.shape[0] == 1?}
    U -- Yes --> V[Warn and return zeros array]
    U -- No --> W{stacked_x.shape[0] < n_components?}
    W -- Yes --> X[Warn about insufficient rows]
    X --> Y[Apply normalize if provided]
    Y --> Z[Apply align if provided]
    Z --> AA[Instantiate model with params]
    AA --> AB[Apply reduce_list to transform data]
    AB --> AC{internal or multiple arrays?}
    AC -- Yes --> AD[Return list of reduced arrays]
    AC -- No --> AE[Return first array from list]
```

## Examples:
```python
# Basic usage with default IncrementalPCA
data = [[1, 2, 3], [4, 5, 6]]
reduced_data = reduce(data)

# Using specific algorithm
reduced_data = reduce(data, reduce='PCA', ndims=2)

# Using dictionary configuration
config = {'model': 'UMAP', 'params': {'n_components': 2}}
reduced_data = reduce(data, reduce=config)

# With multiple data arrays
data_list = [np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]])]
reduced_list = reduce(data_list, reduce='PCA', ndims=1)
```

## `hypertools.tools.reduce.reduce_list` · *function*

## Summary:
Applies a dimensionality reduction or transformation model to a list of data arrays while preserving their original structure.

## Description:
This function takes a list of data arrays and applies a fitted model's transform operation to them collectively, then splits the results back into the original array structure. It's designed to handle multiple data chunks that need to be processed together but maintained as separate entities afterward.

The function is typically used in data preprocessing pipelines where dimensionality reduction needs to be applied consistently across multiple datasets or data chunks that were originally separate but need to be transformed together for alignment purposes.

## Args:
    x (list): A list of arrays/data that will be stacked and transformed together
    model: A fitted transformation model with a `fit_transform` method (e.g., PCA, UMAP, etc.)

## Returns:
    list: A list of transformed arrays, where each array corresponds to the transformed version of the original input arrays. If the input contains multiple arrays, returns a list of transformed arrays; if a single array, returns a list containing that single transformed array.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - Input `x` must be a list of arrays that can be vertically stacked using `np.vstack`
    - Model must have a `fit_transform` method that accepts stacked data and returns appropriately shaped output
    - All arrays in `x` should be compatible for vertical stacking
    
    Postconditions:
    - Output list contains transformed arrays matching the shape and structure of input arrays
    - If input contains multiple arrays, output list contains multiple transformed arrays
    - If input contains single array, output list contains single transformed array

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce_list] --> B{len(x) > 1?}
    B -- Yes --> C[Calculate split points]
    C --> D[Stack arrays with np.vstack]
    D --> E[Apply model.fit_transform]
    E --> F[Split result with np.vsplit]
    F --> G[Return list of split arrays]
    B -- No --> H[Calculate split points]
    H --> I[Stack arrays with np.vstack]
    I --> J[Apply model.fit_transform]
    J --> K[Return single transformed array in list]
```

## Examples:
```python
# Example 1: Multiple data arrays
data_chunks = [np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]])]
pca_model = PCA(n_components=1)
result = reduce_list(data_chunks, pca_model)
# Returns list of transformed arrays, one for each input chunk

# Example 2: Single data array
single_array = np.array([[1, 2], [3, 4]])
pca_model = PCA(n_components=1)
result = reduce_list([single_array], pca_model)
# Returns list containing single transformed array
```

