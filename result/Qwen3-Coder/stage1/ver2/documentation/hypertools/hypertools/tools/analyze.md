# `analyze.py`

## `hypertools.tools.analyze.analyze` · *function*

## Summary:
Applies a sequential pipeline of data normalization, dimensionality reduction, and alignment transformations to input data.

## Description:
This function serves as a high-level interface that chains together three fundamental data processing operations: normalization, dimensionality reduction, and alignment. It provides a convenient way to apply these transformations in sequence to prepare data for analysis or visualization. The function accepts parameters for each transformation step and passes them appropriately to the underlying processing functions.

The function is designed to be a unified entry point that combines the functionality of separate normalization, reduction, and alignment operations, making it easier to apply multiple transformations without manually chaining them together. It follows the pattern: normalize → reduce → align.

## Args:
    data: Input data to be processed. Typically a list of numpy arrays representing datasets.
    normalize (str or bool or None, optional): Normalization method to apply. Can be 'across', 'within', 'row', False, or None. Defaults to None.
    reduce (str or dict or None, optional): Reduction method to apply. Can be a string identifier or dictionary specifying the model and parameters. Defaults to None.
    ndims (int, optional): Target number of dimensions for reduction. Required when reduce is specified. Defaults to None.
    align (str or bool or dict, optional): Alignment method to apply. Can be 'hyper', 'SRM', True, False, or None. Defaults to None.
    internal (bool, optional): Internal flag that controls return behavior for single vs multiple datasets. Passed to normalize and reduce functions but not to align function. Defaults to False.

## Returns:
    list or array: Processed data after applying normalization, reduction, and alignment in sequence. The exact return type depends on the input data structure and the internal flag.

## Raises:
    ValueError: If invalid parameters are passed to the underlying functions.
    KeyError: If dictionary parameters are missing required keys.
    AssertionError: If normalization type is not one of the allowed values ('across', 'within', 'row', False, None).

## Constraints:
    Precondition: Input data must be compatible with the underlying processing functions (typically lists of numpy arrays)
    Precondition: When using reduction, ndims parameter should be specified appropriately
    Postcondition: Data will be processed through normalization, reduction, and alignment in sequence

## Side Effects:
    Issues warnings via Python warnings module for deprecated parameters in underlying functions
    May modify data shapes through dimensionality reduction operations
    May issue warnings for potential overfitting conditions in alignment operations

## Control Flow:
```mermaid
flowchart TD
    A[Start analyze function] --> B{Normalize enabled?}
    B -- Yes --> C[Call normalizer(data, normalize=normalize, internal=internal)]
    B -- No --> D[Skip normalization]
    C --> E[Call reducer(..., reduce=reduce, ndims=ndims, internal=internal)]
    D --> E
    E --> F{Align enabled?}
    F -- Yes --> G[Call aligner(..., align=align)]
    F -- No --> H[Return result]
    G --> H
    H --> I[Return final processed data]
```

## Examples:
```python
# Basic usage with no transformations
result = analyze(data)

# Apply normalization only
result = analyze(data, normalize='across')

# Apply reduction only
result = analyze(data, reduce='IncrementalPCA', ndims=10)

# Apply all transformations
result = analyze(data, normalize='across', reduce='IncrementalPCA', ndims=10, align='hyper')

# Using dictionary-based reduction specification
result = analyze(data, reduce={'model': 'IncrementalPCA', 'params': {'n_components': 5}}, align='SRM')

# Using internal flag for special handling
result = analyze(data, normalize='within', reduce='PCA', ndims=5, internal=True)
```

