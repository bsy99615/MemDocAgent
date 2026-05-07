# `reduce.py`

## `hypertools.tools.reduce.reduce` · *function*

## Summary:
Performs dimensionality reduction on data using various machine learning models, supporting both single and multiple dataset processing with flexible configuration options.

## Description:
The reduce function serves as a unified interface for applying dimensionality reduction techniques to data arrays. It accepts multiple input formats for specifying the reduction method and handles both single datasets and collections of datasets. The function integrates preprocessing steps like data formatting and supports deprecated alignment and normalization operations while providing modern configuration through the reduce parameter.

This function is typically called in data analysis pipelines when reducing feature dimensions of datasets for visualization, compression, or downstream processing. It's designed to work with sklearn decomposition methods, manifold learning algorithms, and UMAP for dimensionality reduction.

## Args:
    x (list or array-like): Input data to be reduced. Can be a single array or list of arrays representing one or more datasets.
    reduce (str, dict, or callable, optional): Specifies the reduction method. Can be a string name of a supported model (like 'PCA', 'UMAP'), a dictionary with 'model' and 'params' keys, or a direct model class. Defaults to 'IncrementalPCA'.
    ndims (int, optional): Number of dimensions to reduce to. If None, uses the default from the model. Defaults to None.
    normalize (str or None, optional): Deprecated normalization method. Defaults to None.
    align (str or None, optional): Deprecated alignment method. Defaults to None.
    model (str or None, optional): Deprecated parameter for specifying the model. Defaults to None.
    model_params (dict or None, optional): Deprecated parameter for specifying model parameters. Defaults to None.
    internal (bool, optional): If True, returns list format even for single datasets. Defaults to False.
    format_data (bool, optional): Whether to apply data formatting. Defaults to True.

## Returns:
    list or array-like: Reduced dimensional data. Returns a list when internal=True or when multiple datasets are processed, otherwise returns a single array. In special cases with insufficient data, returns appropriately sized zero arrays.

## Raises:
    ValueError: Raised when invalid model specifications are provided (missing keys in dict format, unsupported model names) or when model validation fails.

## Constraints:
    Preconditions:
    - Input data x must be array-like or list of arrays
    - If using string model names, they must be valid keys in the models dictionary (which maps string names to model classes)
    - Model classes must implement fit_transform and n_components attributes
    - When passing a dictionary, it must contain 'model' and 'params' keys
    
    Postconditions:
    - Output data has reduced dimensions according to specified parameters
    - Data structure preserved (single array or list of arrays)
    - Appropriate warnings issued for edge cases

## Side Effects:
    - Issues deprecation warnings for normalize and align parameters
    - Issues deprecation warnings for model and model_params parameters
    - May modify input data through formatting operations
    - Issues warnings for edge cases like insufficient data rows

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce function] --> B{model_params provided?}
    B -->|Yes| C[Show deprecation warning]
    B -->|No| D[Continue]
    D --> E{reduce is None?}
    E -->|Yes| F[Return x unchanged]
    E -->|No| G{reduce is str/string?}
    G -->|Yes| H[Set model_name = reduce]
    H --> I[Set model_params = {'n_components': ndims}]
    G -->|No| J{reduce is dict?}
    J -->|Yes| K[Try extract model_name and model_params from dict]
    K --> L{KeyError?}
    L -->|Yes| M[Raise ValueError]
    L -->|No| N[Continue]
    J -->|No| O[Set model_name = reduce]
    O --> P{model_name is str?}
    P -->|Yes| Q[Look up model in models dict]
    P -->|No| R[Validate model has required methods]
    R --> S{Valid model?}
    S -->|No| T[Raise ValueError]
    S -->|Yes| U[Continue]
    U --> V{Check n_components conflict}
    V --> W[Handle ndims vs n_components mismatch]
    W --> X[Update model_params]
    X --> Y{format_data enabled?}
    Y -->|Yes| Z[Apply formatter]
    Z --> AA[Check if reduction needed]
    AA --> AB{Reduction not needed?}
    AB -->|Yes| AC[Return x]
    AB -->|No| AD[Stack data with np.vstack]
    AD --> AE{Single row data?}
    AE -->|Yes| AF[Warn and return zeros array]
    AE -->|No| AG{Rows < ndims?}
    AG -->|Yes| AH[Warn and reduce to rows count]
    AH --> AI[Apply normalize if set]
    AI --> AJ[Apply align if set]
    AJ --> AK[Instantiate model with params]
    AK --> AL[Call reduce_list function]
    AL --> AM{internal or multiple datasets?}
    AM -->|Yes| AN[Return x_reduced list]
    AM -->|No| AO[Return x_reduced[0]]
```

## Examples:
```python
import numpy as np
from hypertools.tools.reduce import reduce

# Basic usage with default IncrementalPCA
data = np.random.rand(100, 10)
reduced = reduce(data, ndims=5)
print(reduced.shape)  # (100, 5)

# Using different model
reduced_pca = reduce(data, reduce='PCA', ndims=3)

# With multiple datasets
data_list = [np.random.rand(50, 10), np.random.rand(30, 10)]
reduced_multi = reduce(data_list, reduce='PCA', ndims=5)

# Using dictionary specification
custom_reduce = {'model': 'PCA', 'params': {'n_components': 3, 'whiten': True}}
reduced_custom = reduce(data, reduce=custom_reduce)

# Using internal flag to force list return
single_result = reduce(data, reduce='PCA', ndims=3, internal=True)
```

## `hypertools.tools.reduce.reduce_list` · *function*

## Summary:
Applies dimensionality reduction to a list of data arrays using a specified model and returns results in the same structure.

## Description:
This function performs dimensionality reduction on multiple data arrays simultaneously by stacking them, applying the transformation model, and then splitting the results back into individual arrays. It's designed to handle batch processing of multiple datasets while maintaining their structural relationship.

The function is typically called within the dimensionality reduction pipeline when processing multiple data segments that need to be transformed consistently using the same model.

## Args:
    x (list): A list of numpy arrays to be reduced in dimensionality. Each array represents a dataset segment.
    model: A fitted sklearn or umap dimensionality reduction model that implements fit_transform method.

## Returns:
    list: A list of transformed arrays with the same structure as input. When input contains multiple arrays, returns a list of transformed arrays. When input contains a single array, returns a list containing that single transformed array.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
    - Input `x` must be a list of numpy arrays
    - All arrays in `x` should have compatible dimensions for stacking
    - Model must implement the fit_transform method
    
    Postconditions:
    - Output list contains arrays with reduced dimensions
    - Structure of output matches input structure

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input x (list of arrays)] --> B[Calculate split points]
    B --> C[Stack arrays with np.vstack]
    C --> D[Apply model.fit_transform]
    D --> E[Split result with np.vsplit]
    E --> F{len(x) > 1?}
    F -->|Yes| G[Return [xi for xi in x_r]]
    F -->|No| H[Return [x_r[0]]]
```

## Examples:
```python
# Basic usage with PCA
from sklearn.decomposition import PCA
import numpy as np

# Multiple datasets
data = [np.random.rand(100, 10), np.random.rand(50, 10)]
pca_model = PCA(n_components=5)
reduced_data = reduce_list(data, pca_model)
print(len(reduced_data))  # Output: 2
print(reduced_data[0].shape)  # Output: (100, 5)

# Single dataset
single_data = [np.random.rand(100, 10)]
reduced_single = reduce_list(single_data, pca_model)
print(len(reduced_single))  # Output: 1
print(reduced_single[0].shape)  # Output: (100, 5)
```

