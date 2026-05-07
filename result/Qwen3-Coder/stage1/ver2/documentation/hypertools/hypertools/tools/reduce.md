# `reduce.py`

## `hypertools.tools.reduce.reduce` · *function*

*No documentation generated.*

## `hypertools.tools.reduce.reduce_list` · *function*

## Summary:
Applies dimensionality reduction to a list of arrays using a specified model and returns the transformed arrays while preserving their original structure.

## Description:
This function performs dimensionality reduction on a list of input arrays using the provided model. It vertically concatenates all arrays into a single matrix, applies the dimensionality reduction transformation via the model's `fit_transform` method, then splits the result back into separate arrays according to the original sizes. This enables consistent processing of multiple arrays while maintaining their individual structures.

The function handles both single and multiple array inputs gracefully, ensuring consistent return format regardless of input size. This abstraction allows dimensionality reduction operations to be applied uniformly across varying array structures.

## Args:
    x (list): A list of arrays (typically numpy arrays) to be reduced in dimensionality
    model: A dimensionality reduction model with a `fit_transform` method (e.g., PCA, UMAP, etc.)

## Returns:
    list: A list of transformed arrays with the same number of elements as the input list `x`. Each array has been reduced to the dimensionality specified by the model.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - Input `x` must be a list of arrays that can be vertically stacked using `np.vstack`
    - Model must have a `fit_transform` method that accepts a 2D array and returns a 2D array
    - All arrays in `x` should be compatible for vertical stacking
    
    Postconditions:
    - Output list contains arrays with the same number of elements as input list `x`
    - Each returned array has been transformed by the provided model
    - The total number of rows in output arrays equals the total number of rows in input arrays

## Side Effects:
    None explicitly stated

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce_list(x, model)] --> B[Calculate split points: split = cumsum([len(xi) for xi in x])[:-1]]
    B --> C[Stack arrays vertically: stacked = vstack(x)]
    C --> D[Transform with model: transformed = model.fit_transform(stacked)]
    D --> E[Split transformed result: x_r = vsplit(transformed, split)]
    E --> F{len(x) > 1?}
    F -- Yes --> G[Return [xi for xi in x_r]]
    F -- No --> H[Return [x_r[0]]]
    G --> I[End]
    H --> I
```

## Examples:
    # Example 1: Multiple arrays
    arrays = [np.array([[1, 2], [3, 4]]), np.array([[5, 6]])]
    pca_model = PCA(n_components=1)
    result = reduce_list(arrays, pca_model)
    # Returns list of transformed arrays with same structure as input
    
    # Example 2: Single array
    arrays = [np.array([[1, 2], [3, 4]])]
    pca_model = PCA(n_components=1)
    result = reduce_list(arrays, pca_model)
    # Returns list containing single transformed array

