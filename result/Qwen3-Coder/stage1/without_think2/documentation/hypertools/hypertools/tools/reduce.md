# `reduce.py`

## `hypertools.tools.reduce.reduce` · *function*

## Summary:
Reduces the dimensionality of input data using various scikit-learn and custom dimensionality reduction techniques.

## Description:
The `reduce` function provides a unified interface for applying dimensionality reduction techniques to input data. It supports multiple reduction methods including PCA variants, manifold learning algorithms, and UMAP. The function can handle both single and multiple datasets, applying consistent dimensionality reduction across all inputs while preserving their individual structures. It also supports deprecated parameters for backward compatibility and integrates with other preprocessing functions like normalization and alignment.

This function is extracted into its own component to encapsulate the complex logic of parsing different input formats, validating reduction methods, handling edge cases, and coordinating with preprocessing steps. It provides a clean abstraction layer that allows users to specify dimensionality reduction techniques through flexible input parameters while ensuring proper data handling and validation.

## Args:
    x (array-like or list): Input data to be reduced. Can be a single array or list of arrays representing datasets to be reduced together.
    reduce (str, dict, or callable, optional): Dimensionality reduction method to use. Can be a string name of a supported method, a dictionary with 'model' and 'params' keys, or a direct callable. Defaults to 'IncrementalPCA'.
    ndims (int, optional): Number of dimensions to reduce to. If None, uses the default from the selected model. Defaults to None.
    normalize (str or bool, optional): Deprecated normalization parameter. Will be removed in future versions. Defaults to None.
    align (str or bool, optional): Deprecated alignment parameter. Will be removed in future versions. Defaults to None.
    model (str, optional): Deprecated parameter for specifying the model. Use `reduce` instead. Defaults to None.
    model_params (dict, optional): Deprecated parameter for specifying model parameters. Use `reduce` instead. Defaults to None.
    internal (bool, optional): If True, returns list even for single array input. If False, returns single array when input is single. Defaults to False.
    format_data (bool, optional): Whether to apply data formatting before reduction. Defaults to True.

## Returns:
    array or list: Reduced-dimensionality data. Returns a single array when `internal=False` and input is single, otherwise returns a list of reduced arrays.

## Raises:
    ValueError: Raised when invalid reduction method is specified or when dictionary input doesn't contain required keys.

## Constraints:
    Precondition: Input data must be compatible with numpy array operations.
    Precondition: When using string-based reduction methods, the method name must be in the supported models dictionary.
    Precondition: When using callable reduction methods, they must implement `fit_transform` and `n_components` attributes.
    Postcondition: Output arrays will have the same number of rows as input arrays but fewer columns based on the reduction method.
    Postcondition: When `format_data=True`, input data is processed through the format_data function before reduction.

## Side Effects:
    Issues deprecation warnings for `model`, `model_params`, `normalize`, and `align` parameters.
    May call `format_data`, `normalizer`, and `aligner` functions which could involve text processing and data alignment.
    Uses numpy operations for mathematical computations.

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce function] --> B{model or model_params provided?}
    B -- Yes --> C[Show deprecation warning]
    C --> D[Set reduce = {'model': model, 'params': model_params}]
    B -- No --> E[Continue with existing reduce parameter]
    E --> F{reduce is None?}
    F -- Yes --> G[Return original data x]
    F -- No --> H{reduce is str or np.string_?}
    H -- Yes --> I[Set model_name = reduce, model_params = {'n_components': ndims}]
    H -- No --> J{reduce is dict?}
    J -- Yes --> K[Try to extract model_name and model_params from dict]
    K --> L{KeyError?}
    L -- Yes --> M[Raise ValueError about dict format]
    L -- No --> N[Continue with parsed values]
    J -- No --> O[Set model_name = reduce]
    O --> P{model_name is str or np.string_?}
    P -- Yes --> Q[Get model from models dict]
    P -- No --> R[Validate model has required methods]
    R --> S{KeyError or AttributeError?}
    S -- Yes --> T[Raise ValueError about supported models]
    S -- No --> U[Continue with validated model]
    U --> V{Check n_components conflict}
    V --> W{ndims != model_params['n_components']?}
    W -- Yes --> X[Show warning about unequal values]
    X --> Y[Set model_params['n_components'] = ndims]
    W -- No --> Z[Pass through]
    Z --> AA[Apply format_data if enabled]
    AA --> AB{model_params['n_components'] is None or all arrays have <= n_components?}
    AB -- Yes --> AC[Return original data x]
    AB -- No --> AD[Stack data vertically with np.vstack]
    AD --> AE{stacked_x.shape[0] == 1?}
    AE -- Yes --> AF[Show warning about single row]
    AF --> AG[Return zeros array with shape (1, n_components)]
    AE -- No --> AH{stacked_x.shape[0] < n_components?}
    AH -- Yes --> AI[Show warning about insufficient rows]
    AH -- No --> AJ[Continue with normal processing]
    AJ --> AK{normalize is not None?}
    AK -- Yes --> AL[Show deprecation warning]
    AL --> AM[Apply normalizer]
    AK -- No --> AN[Skip normalization]
    AN --> AO{align is not None?}
    AO -- Yes --> AP[Show deprecation warning]
    AP --> AQ[Apply aligner]
    AO -- No --> AR[Skip alignment]
    AR --> AS[Instantiate model with model_params]
    AS --> AT[Apply reduce_list to process data]
    AT --> AU{internal OR len(x_reduced) > 1?}
    AU -- Yes --> AV[Return x_reduced]
    AU -- No --> AW[Return x_reduced[0]]
```

## Examples:
```python
import numpy as np
from hypertools.tools.reduce import reduce

# Basic usage with default IncrementalPCA
data = np.random.rand(100, 50)
reduced_data = reduce(data, ndims=10)

# Using different reduction method
reduced_data = reduce(data, reduce='PCA', ndims=5)

# Using dictionary specification
reduced_data = reduce(data, reduce={'model': 'UMAP', 'params': {'n_components': 3}}, ndims=3)

# Multiple datasets
data_list = [np.random.rand(100, 50), np.random.rand(150, 50)]
reduced_data = reduce(data_list, reduce='PCA', ndims=10)

# With internal flag
reduced_data = reduce(data, ndims=5, internal=True)
```

## `hypertools.tools.reduce.reduce_list` · *function*

## Summary:
Applies dimensionality reduction to a list of data arrays while preserving their individual structures.

## Description:
The `reduce_list` function takes a list of data arrays and applies a dimensionality reduction model to them collectively, then splits the results back into individual arrays. This enables consistent dimensionality reduction across multiple datasets while maintaining their separate identities. The function is particularly useful when working with datasets that need to be processed together for alignment or joint analysis but should remain as distinct entities afterward.

This function is extracted into its own component to encapsulate the common pattern of applying a single dimensionality reduction model to multiple data arrays. It provides a clean abstraction for dimensionality reduction workflows where data needs to be processed as a unified dataset but maintained as separate entities afterward.

## Args:
    x (list): List of numpy arrays to be reduced in dimensionality. Each array should have the same number of columns (features) but potentially different numbers of rows (samples). The function preserves the row count of each array in the output.
    model: A scikit-learn style dimensionality reduction model that implements the `fit_transform` method (e.g., PCA, TSNE, UMAP). The model is fitted on the concatenated data and applied to transform all data.

## Returns:
    list: A list of reduced-dimensionality arrays, each corresponding to the input arrays in the same order. Each output array will have the same number of rows as the corresponding input array but fewer columns (features) determined by the model. When a single array is provided, a list containing that single array is returned.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Precondition: All arrays in the input list `x` must have the same number of columns (features).
    Precondition: The `model` parameter must implement the `fit_transform` method.
    Postcondition: The output list will contain arrays with the same number of rows as the corresponding input arrays.
    Postcondition: The total number of rows in output arrays will equal the total number of rows in input arrays.

## Side Effects:
    None - This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce_list] --> B[Calculate split points from array lengths]
    B --> C[Concatenate all arrays vertically using np.vstack]
    C --> D[Apply model.fit_transform to concatenated data]
    D --> E[Split transformed data back using np.vsplit at calculated points]
    E --> F{len(x) > 1?}
    F -- Yes --> G[Return list of split arrays]
    F -- No --> H[Return first (only) array wrapped in list]
```

## Examples:
```python
import numpy as np
from sklearn.decomposition import PCA
from hypertools.tools.reduce import reduce_list

# Basic usage with PCA
data = [np.random.rand(100, 50), np.random.rand(150, 50)]
pca_model = PCA(n_components=10)
reduced_data = reduce_list(data, pca_model)
# Returns list of two arrays, each with 100 and 150 rows respectively, but 10 columns

# Usage with UMAP
from umap import UMAP
umap_model = UMAP(n_components=5)
reduced_data = reduce_list(data, umap_model)
# Returns list of two arrays, each with 100 and 150 rows respectively, but 5 columns

# Single array case
single_array = [np.random.rand(100, 50)]
reduced_single = reduce_list(single_array, pca_model)
# Returns list containing one array with same shape characteristics
```

