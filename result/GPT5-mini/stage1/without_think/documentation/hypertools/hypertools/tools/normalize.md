# `normalize.py`

## `hypertools.tools.normalize.normalize` · *function*

## Summary:
Standardizes one or more 2D numeric datasets by computing z-scores either across all datasets, within each dataset, or across each row, and returns either a list of normalized arrays or a single normalized array depending on the inputs and the internal flag.

## Description:
- Known callers:
    - No direct callers were present in the provided memory snapshot.
    - Typical callers: preprocessing stages of analysis or visualization pipelines that require features to be standardized before dimensionality-reduction, clustering, or plotting (e.g., before PCA/t-SNE or multi-dataset comparison).
    - Typical trigger: invoked when a user or pipeline requests feature standardization and specifies the scope ('across', 'within', or 'row').

- Why this is a separate function:
    - Consolidates three related normalization strategies (global column-wise, per-dataset column-wise, and per-row) and consistent zero-variance handling in one reusable location.
    - Centralizes optional data formatting (via a formatter) and consistent return-shape logic (list vs. single array) so callers do not duplicate these rules.

## Args:
    x (iterable or list-like or array-like):
        - Expected after optional formatting: a list-like sequence of 2D numeric numpy arrays with shapes [n_samples_i, n_features].
        - If format_data is True, x may be any input accepted by the module-level formatter callable; the formatter must return the described list-of-2D-arrays.
        - Note: for normalize='across', all arrays must have the same number of columns (n_features) because the function vertically stacks arrays.

    normalize (str|bool|None, default 'across'):
        - Allowed values: 'across', 'within', 'row', False, None.
        - Behavior:
            - 'across': compute column-wise z-scores using global means/stds computed from all datasets concatenated (vstack).
            - 'within': compute column-wise z-scores within each dataset separately.
            - 'row': compute z-scores across columns for each row independently.
            - False or None: skip normalization and immediately return x unchanged (formatter is not called in this branch).

    internal (bool, default False):
        - If True: always return a list of numpy.ndarray objects (one per dataset).
        - If False: and the normalized result is exactly one dataset (length-1 list), return the single numpy.ndarray rather than a length-1 list.

    format_data (bool, default True):
        - If True: call the module-level formatter as formatter(x, ppca=True) to coerce x into the expected list-of-2D-arrays before normalization.
        - If False: assume x is already in the expected format.
        - Important: if normalize is False or None, the function returns early and the formatter is not invoked.

## Returns:
    - If normalize in [False, None]:
        - Returns the original x object unchanged (identity preserved).
    - Otherwise:
        - Returns either:
            - A list of numpy.ndarray objects (one per input dataset), or
            - A single numpy.ndarray if internal is False and there is exactly one dataset after optional formatting.
    - Each returned array has the same shape as the corresponding input array, with values z-scored according to the selected mode.
    - For any column or row detected as constant (no variation), that column/row in the output is replaced by zeros of the same shape and dtype as produced by numpy.zeros(...).

## Raises:
    - AssertionError:
        - If normalize is not one of the allowed values. Exact message from the code: "scale_type must be across, within, row or none."
    - NameError / UnboundLocalError:
        - If the module-level globals expected by the function are not present (the function body references 'np' and 'formatter'); callers should ensure these names are bound in the module scope before calling.
    - IndexError:
        - If the formatted or provided x is an empty sequence (length 0), normalized_x will be empty and the function will attempt to return normalized_x[0] when internal is False, raising IndexError.
    - ValueError / TypeError / other exceptions from:
        - The formatter callable (if format_data is True).
        - Numpy operations (e.g., incompatible shapes when stacking, or non-numeric data).
    - Any such exceptions propagate unchanged.

## Constraints:
- Preconditions:
    - Module-level expectations (implementation must satisfy these):
        - A numeric namespace must be available at global name 'np' such that np.mean(...) and np.std(...) are callable (this is how the function computes means and standard deviations).
        - A callable global named 'formatter' must be available when format_data is True; it will be invoked as formatter(x, ppca=True) and must return a list-like sequence of 2D numpy arrays.
        - The input arrays (after formatting) must be 2D numeric arrays. For normalize=='across', all arrays must have the same number of columns.
    - Zero-variance detection:
        - The code detects constant vectors using len(set(y)) > 1. If this expression is False (i.e., set(y) has length 1), the code returns zeros for that vector. Note that using set(y) requires elements to be hashable; unusual element types may raise TypeError.

- Postconditions:
    - When normalization is performed:
        - All outputs are numpy.ndarray instances with the same shapes as the corresponding inputs.
        - Columns or rows found to be constant are replaced by zeros (numpy.zeros) preserving shape.
    - When normalize in [False, None]:
        - The returned value is exactly the original x (no formatting, no normalization).

## Side Effects:
    - No file, network, or standard I/O operations.
    - The function calls the module-level formatter and uses numpy routines; any side effects those callables produce will propagate.
    - The function does not intentionally mutate the input arrays; it builds and returns new numpy arrays. However, if the formatter returns views into the original input data, callers must be aware that those views might alias original objects.

## Implementation details relevant to callers and reimplementers:
    - The z-score helper used is:
        - If len(set(y)) > 1 then (y - np.mean(X)) / np.std(X)
        - Else return np.zeros(y.shape)
      where X is the array used to compute the mean/std (either the stacked global columns or a per-dataset column or a row), and y is the data vector to be standardized.
    - The code uses numpy.std with its default ddof=0 (population standard deviation).
    - For 'across', the datasets are concatenated with numpy.vstack(x) before computing per-column statistics; mismatched column counts will cause an exception.
    - The function's current source references 'np' and 'formatter' but the file-level imports provided earlier were 'import numpy' and 'from format_data import format_data'. This name mismatch can raise NameError unless the module also defines aliases such as "np = numpy" and "formatter = format_data" (or equivalent). Callers and implementers should ensure the module-level names expected by the function are present.

## Control Flow:
flowchart TD
    A[Start] --> B{normalize in [False, None]?}
    B -- Yes --> C[Return x unchanged (identity)]
    B -- No --> D{format_data True?}
    D -- Yes --> E[Call formatter(x, ppca=True) -> x (list of 2D arrays)]
    D -- No --> F[Assume x is already list of 2D arrays]
    E --> G[Define zscore(X,y): if len(set(y))>1 -> (y-mean(X))/std(X) else zeros_like(y)]
    F --> G
    G --> H{normalize == 'across'?}
    H -- Yes --> I[Stack arrays to x_stacked; for each column j compute stats using x_stacked[:,j]; apply to each dataset column j]
    H -- No --> J{normalize == 'within'?}
    J -- Yes --> K[For each dataset, for each column j compute stats using that dataset's column]
    J -- No --> L{normalize == 'row'?}
    L -- Yes --> M[For each dataset, for each row j compute stats using that row's elements]
    M --> N[normalized_x is list of arrays]
    K --> N
    I --> N
    N --> O{internal True or len(normalized_x)>1?}
    O -- Yes --> P[Return list normalized_x]
    O -- No --> Q[Return normalized_x[0] (may raise IndexError if list is empty)]

## Examples:
- Global column normalization across two datasets:
    - Precondition: two numpy 2D arrays with identical number of columns.
    - Behavior: compute global mean/std per column from vstack of both arrays, then z-score each dataset column with those statistics.
    - Return: a list of two numpy arrays (unless internal=False and exactly one dataset).

- Single-dataset column normalization:
    - If x is a single 2D array and format_data will coerce it to [array], call normalize(x, normalize='within', internal=False).
    - Return: the single normalized numpy array (not wrapped in list) because internal=False and there's only one dataset.

- Row-wise normalization and constant-row handling:
    - For any row where all values are equal, the function produces zeros for that row in the output.

- Error case — empty input:
    - If the formatter returns an empty list (or x is an empty list and format_data is False), calling normalize(..., internal=False) will raise IndexError when trying to access normalized_x[0]. Guard against empty inputs or set internal=True.

- Defensive usage pattern:
    - Ensure module globals exist:
        - If the module does not already bind np and formatter, callers can do:
            - np = numpy
            - formatter = format_data
      so that this normalize implementation will run without NameError.

