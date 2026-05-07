# `analyze.py`

## `hypertools.tools.analyze.analyze` · *function*

## Summary:
Applies a sequence of data preprocessing transformations including normalization, dimensionality reduction, and alignment to input data.

## Description:
This function serves as a pipeline that sequentially applies three data processing operations: normalization, dimensionality reduction, and alignment. It provides a convenient way to chain these operations together with configurable parameters for each transformation step. The function acts as a high-level interface that orchestrates the preprocessing workflow, allowing users to apply multiple transformations in a single call rather than chaining them manually.

## Args:
    data: Input data to be processed, typically a list of arrays or matrices
    normalize (str, optional): Normalization method to apply ('across', 'within', 'row', or None). Defaults to None.
    reduce (str, optional): Reduction method to apply (e.g., 'IncrementalPCA'). Defaults to None.
    ndims (int, optional): Number of dimensions to reduce to. Defaults to None.
    align (str, optional): Alignment method to apply ('hyper', 'SRM', or None). Defaults to None.
    internal (bool): Internal flag for handling special cases in the processing pipeline. Defaults to False.

## Returns:
    Processed data after applying all requested transformations in sequence. When internal=False and there's a single dataset, a single array is returned; otherwise, a list of arrays is returned. The exact format depends on the transformations applied and the internal flag.

## Raises:
    ValueError: If invalid parameters are passed to the underlying transformation functions.

## Constraints:
    Preconditions:
    - Input data should be compatible with the expected formats for normalization, reduction, and alignment operations
    - All parameters must be valid according to the underlying functions' requirements
    
    Postconditions:
    - Data will have been processed through all enabled transformations
    - Return value will be in the appropriate format for downstream processing

## Side Effects:
    - May issue warnings about deprecated parameters or conditions
    - Calls external functions that may perform I/O operations or modify global state
    - Uses various scientific computing libraries (numpy, scipy) that may have side effects

## Control Flow:
```mermaid
flowchart TD
    A[Start analyze()] --> B{normalize specified?}
    B -- Yes --> C[normalizer(data, normalize=normalize, internal=internal)]
    B -- No --> C[data]
    C --> D{reduce specified?}
    D -- Yes --> E[reducer(normalized_data, reduce=reduce, ndims=ndims, internal=internal)]
    D -- No --> E[normalized_data]
    E --> F{align specified?}
    F -- Yes --> G[aligner(reduced_data, align=align)]
    F -- No --> G[reduced_data]
    G --> H[Return result]
```

## Examples:
```python
# Basic usage with no transformations
result = analyze(data)

# Apply normalization only
result = analyze(data, normalize='across')

# Apply normalization and reduction
result = analyze(data, normalize='within', reduce='IncrementalPCA', ndims=10)

# Apply all transformations
result = analyze(data, normalize='across', reduce='IncrementalPCA', ndims=5, align='hyper')
```

