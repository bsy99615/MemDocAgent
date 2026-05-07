# `reduce.py`

## `hypertools.tools.reduce.reduce` · *function*

## Summary:
Performs dimensionality reduction on input data using various machine learning models.

## Description:
The `reduce` function applies dimensionality reduction techniques to input data using a variety of supported models including PCA variants, manifold learning algorithms, and UMAP. It handles both single and multi-dimensional datasets, manages data formatting, and provides flexible parameter configuration for different reduction approaches.

This function was extracted to centralize dimensionality reduction logic, allowing reuse across different analysis pipelines while providing a unified interface for various reduction techniques. It encapsulates the complexity of model selection, parameter handling, and data preprocessing.

## Args:

*   `x` (array-like or list of array-likes): Input data to be reduced. Can be a single array or list of arrays.
*   `reduce` (str, dict, or callable, optional): Reduction technique to apply. Can be a string name of a supported model, a dictionary with 'model' and 'params' keys, or a direct model class. Defaults to 'IncrementalPCA'.
*   `ndims` (int, optional): Number of dimensions to reduce to. If None, uses the default from the model.
*   `normalize` (str or None, optional): Normalization method to apply before reduction. Deprecated - use analyze function instead.
*   `align` (str or None, optional): Alignment method to apply before reduction. Deprecated - use analyze function instead.
*   `model` (callable or None, optional): Deprecated parameter - use `reduce` instead.
*   `model_params` (dict or None, optional): Deprecated parameter - use `reduce` instead.
*   `internal` (bool, optional): If True, returns list even for single dataset. Defaults to False.
*   `format_data` (bool, optional): Whether to format input data before processing. Defaults to True.

## Returns:

*   Array or list of arrays: Reduced dimensional data. Returns a list if `internal=True` or if input was a list of arrays, otherwise returns a single array.

## Raises:

*   `ValueError`: If `reduce` parameter is not a supported model name or doesn't have required methods (`n_components`, `fit_transform`), or if dictionary format is incorrect.

## Constraints:

*   Precondition: Input data `x` must be compatible with the selected reduction model.
*   Precondition: If `ndims` is specified, it must be a positive integer or None.
*   Postcondition: Output data will have the specified number of dimensions or fewer, depending on input constraints.

## Side Effects:

*   Issues deprecation warnings when using `model`, `model_params`, `normalize`, or `align` parameters.
*   May modify input data through formatting operations.
*   Uses numpy operations for data manipulation.

## Control Flow:

```mermaid
flowchart TD
    A[Start reduce function] --> B{model or model_params provided?}
    B -- Yes --> C[Show deprecation warning]
    C --> D[Set reduce = {'model': model, 'params': model_params}]
    D --> E{reduce is None?}
    E -- Yes --> F[Return x unchanged]
    E -- No --> G{reduce is str/np.string_?}
    G -- Yes --> H[Set model_name = reduce, model_params = {'n_components': ndims}]
    G -- No --> I{reduce is dict?}
    I -- Yes --> J[Try extract model_name and model_params from dict]
    J --> K{KeyError?}
    K -- Yes --> L[Raise ValueError]
    I -- No --> M[Set model_name = reduce]
    M --> N{model_name is str/np.string_?}
    N -- Yes --> O[Get model from models dict]
    N -- No --> P[Check model has fit_transform and n_components attributes]
    P --> Q{KeyError/AttributeError?}
    Q -- Yes --> R[Raise ValueError]
    O --> S{Has n_components in model_params?}
    S -- Yes --> T{ndims is None OR ndims equals model_params['n_components']?}
    T -- No --> U[Warn about unequal values, set model_params['n_components'] = ndims]
    S -- No --> V[Set model_params['n_components'] = ndims]
    V --> W{format_data?}
    W -- Yes --> X[Format data with formatter]
    X --> Y{model_params['n_components'] is None OR all shapes meet constraint?}
    Y -- Yes --> Z[Return x]
    Y -- No --> AA[Stack data with np.vstack]
    AA --> AB{stacked_x.shape[0] == 1?}
    AB -- Yes --> AC[Warn about single row, return zeros array]
    AB -- No --> AD{stacked_x.shape[0] < model_params['n_components']?}
    AD -- Yes --> AE[Warn about insufficient rows, continue]
    AE --> AF{normalize is not None?}
    AF -- Yes --> AG[Show deprecation warning, normalize data]
    AF -- No --> AH{align is not None?}
    AH -- Yes --> AI[Show deprecation warning, align data]
    AH -- No --> AJ[Instantiate model with model_params]
    AJ --> AK[Apply reduce_list to process data]
    AK --> AL{internal OR len(x_reduced) > 1?}
    AL -- Yes --> AM[Return x_reduced]
    AL -- No --> AN[Return x_reduced[0]]
```

## Examples:

```python
# Basic usage with default IncrementalPCA
reduced_data = reduce(data)

# Using specific reduction method
reduced_data = reduce(data, reduce='PCA', ndims=10)

# Using dictionary format for custom parameters
reduced_data = reduce(data, reduce={'model': 'PCA', 'params': {'n_components': 5}})

# With multiple datasets
reduced_data = reduce([dataset1, dataset2], reduce='IncrementalPCA', ndims=3)
```

## `hypertools.tools.reduce.reduce_list` · *function*

## Summary:
Applies dimensionality reduction to a list of arrays using a provided model and returns results in the same structure.

## Description:
This function performs dimensionality reduction on a list of arrays by stacking them vertically, applying the provided model's fit_transform method, and then splitting the results back into individual arrays. It's designed to handle both single and multiple array inputs consistently.

The function is typically used in data preprocessing pipelines where dimensionality reduction needs to be applied uniformly across multiple datasets while maintaining their structural integrity.

## Args:
    x (list): A list of arrays to be reduced in dimensionality. Each array should be compatible with the model's expected input format.
    model: A dimensionality reduction model that implements fit_transform method (e.g., PCA, UMAP, etc.).

## Returns:
    list: A list of arrays containing the dimensionality-reduced results. If the input contains multiple arrays, each array is returned separately. If the input contains a single array, that array is still returned as a list element.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
    - Input x must be a list of arrays
    - Each array in x should be compatible with the model's expected input dimensions
    - The model must implement a fit_transform method
    
    Postconditions:
    - The returned list contains arrays with the same number of rows as the input arrays
    - The returned arrays have the reduced dimensionality as determined by the model

## Side Effects:
    None explicitly stated.

## Control Flow:
```mermaid
flowchart TD
    A[Input x (list of arrays) and model] --> B[Calculate split points: np.cumsum([len(xi) for xi in x])[:-1]]
    B --> C[Stack arrays vertically: np.vstack(x)]
    C --> D[Apply model.fit_transform to stacked data]
    D --> E[Split result back: np.vsplit(result, split)]
    E --> F{len(x) > 1?}
    F -- Yes --> G[Return [xi for xi in x_r]]
    F -- No --> H[Return [x_r[0]]]
```

## Examples:
    # Example 1: Multiple arrays
    data_list = [np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]])]
    pca_model = PCA(n_components=1)
    result = reduce_list(data_list, pca_model)
    
    # Example 2: Single array
    data_list = [np.array([[1, 2], [3, 4]])]
    pca_model = PCA(n_components=1)
    result = reduce_list(data_list, pca_model)
``

