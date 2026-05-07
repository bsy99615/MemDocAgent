# `reduce.py`

## `hypertools.tools.reduce.reduce` · *function*

*No documentation generated.*

## `hypertools.tools.reduce.reduce_list` · *function*

## Summary:
Applies dimensionality reduction to a list of arrays using a specified model while preserving the original structure.

## Description:
This function performs dimensionality reduction on multiple arrays by stacking them vertically, applying the provided model's fit_transform method, and then splitting the results back into individual arrays. It serves as a utility for applying the same dimensionality reduction technique consistently across multiple datasets while maintaining their structural relationship.

## Args:
    x (list): A list of numpy arrays to be reduced in dimensionality. All arrays should have the same number of columns (features).
    model: A scikit-learn compatible dimensionality reduction model with fit_transform method.

## Returns:
    list: A list of reduced-dimension arrays, where each array corresponds to the dimensionality reduction of the respective input array. When input contains multiple arrays, returns a list of reduced arrays; when input contains a single array, returns a list containing that single reduced array.

## Raises:
    None explicitly raised

## Constraints:
    - Input x must be a list of numpy arrays
    - All arrays in x should have the same number of columns (features) for proper vertical stacking
    - Model must have a fit_transform method
    - Arrays in x should be compatible with the model's expected input format

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input x list of arrays] --> B[Calculate split points based on array lengths]
    B --> C[Stack arrays vertically using np.vstack]
    C --> D[Apply model.fit_transform to stacked data]
    D --> E[Split result back into arrays using np.vsplit]
    E --> F{len(x) > 1?}
    F -->|Yes| G[Return list of split arrays]
    F -->|No| H[Return single array in list]
```

## Examples:
    # Example usage with PCA
    from sklearn.decomposition import PCA
    data = [np.random.rand(100, 5), np.random.rand(150, 5)]
    pca_model = PCA(n_components=2)
    reduced_data = reduce_list(data, pca_model)
    # Returns list of two arrays, each with shape (n_samples, 2)
    
    # Example with single array
    single_data = [np.random.rand(100, 5)]
    reduced_single = reduce_list(single_data, pca_model)
    # Returns list containing one array with shape (100, 2)

