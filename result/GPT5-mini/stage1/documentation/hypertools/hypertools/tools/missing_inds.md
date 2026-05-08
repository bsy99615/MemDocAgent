# `missing_inds.py`

## `hypertools.tools.missing_inds.missing_inds` · *function*

## Summary:
Detects positions of NaN (missing) values in one or more arrays and returns, for each input array, either None when no NaNs are present or a 1-D numpy integer array of row indices where NaNs occur. If a single array is provided, the function returns that single result rather than a list.

## Description:
This function scans array-like inputs and reports the row indices that contain NaN values. It is intended for preprocessing pipelines that need to locate missing entries prior to imputation, dimensionality reduction, alignment, or visualization.

Literal-source note:
- The original source code uses the identifier "formatter" to perform input formatting and "np" for numpy operations, while the file imports are "format_data" and "numpy". As written, the original function will raise NameError unless "formatter" and "np" are defined elsewhere or the code is corrected to call format_data and import numpy as np. The documentation below describes the precise behavior of the literal implementation and also documents the intended/corrected usage for reimplementation.

Known callers / typical pipeline stage:
- No direct callers were found in scanned memory. Typical usage is within data-preparation or validation stages where inputs (raw arrays, dataframes, or higher-level data objects) are converted and inspected for missing values before downstream steps (e.g., PPCA, alignment, imputation).

Why this is a separate function:
- Encapsulates missing-value detection logic for reuse and simpler testing.
- Keeps formatting and missing-index detection responsibilities separated (formatting → format_data; detection → this function).
- Provides a compact return format (None or index array) that downstream code can branch on.

## Args:
    x (array-like or list[array-like]):
        - Either a single numpy-compatible array-like or an iterable (typically a list) of such arrays.
        - If format_data=True, x may be higher-level inputs that format_data can transform (dataframes, text, geo objects, etc.). format_data will coerce non-list single inputs into a list before returning.
    format_data (bool, default=True):
        - If True, the function (as intended) should call format_data(x, ppca=False) to produce a list of numpy arrays to inspect.
        - If False, x is expected to already be an iterable of numpy-compatible arrays.
        - Interdependency: when True, behavior and shapes depend on the semantics of format_data. format_data may also perform PPCA-related checks when called in other contexts; here it is called with ppca=False.

## Returns:
    - If the post-formatted input contains multiple arrays:
        list[None | numpy.ndarray[int]]
            - For each input array arr (in the same order), returns:
                * None if arr contains no NaNs (determined by numpy.argwhere(numpy.isnan(arr)).size == 0).
                * A 1-D numpy integer array constructed as numpy.argwhere(numpy.isnan(arr))[:, 0] containing the row indices where NaNs were found.
            - Important: the integer arrays may contain duplicate row indices when multiple NaN entries occur in the same row because numpy.argwhere reports each NaN coordinate and the code selects the first coordinate (row index) of each hit.
    - If the post-formatted input contains exactly one array:
        None | numpy.ndarray[int]
            - The single element (None or a 1-D numpy integer array) itself is returned (not wrapped in a list).
    - Edge-case: if the formatted list of arrays is empty, the literal source attempts to return inds[0] and will therefore raise IndexError (see Raises). Callers should avoid passing inputs that format to an empty list.

## Raises:
    - IndexError:
        * Condition: when the formatted/used input yields zero arrays (i.e., inds == []), the final code branch returns inds[0], which raises IndexError.
    - NameError (as in the literal source):
        * Condition: if the identifiers used in the function are not defined in the module's scope (the source uses "formatter" and "np" while the imports show "format_data" and "numpy"), a NameError will occur at runtime unless the implementation is corrected or those names are provided.
    - Propagated exceptions from format_data:
        * Condition: when format_data=True, any exception raised by format_data(x, ppca=False) will propagate.
    - TypeError / ValueError from numpy operations:
        * Condition: if an arr element is of a type not supported by numpy.isnan or numpy.argwhere (e.g., arbitrary objects), numpy may raise TypeError or ValueError.

## Constraints:
    Preconditions:
        - For correct operation, the implementation should import numpy as np (or adjust the code to use the imported name) and should call format_data(x, ppca=False) when format_data is True.
        - After optional formatting, the input must be an iterable of array-like objects where numpy.isnan and numpy.argwhere are meaningful (numeric arrays or arrays coercible to numeric).
        - Avoid passing inputs expected to format to an empty list; if empty inputs are possible, callers should handle them before calling this function.

    Postconditions:
        - The function returns for each input array either None (no NaNs) or a numpy 1-D integer array of row indices (potentially with duplicates).
        - For a single input array, the function returns the single result (None or ndarray); for multiple inputs, returns a list of results matching input order.

## Side Effects:
    - Calls format_data(x, ppca=False) if format_data=True. format_data may allocate data and transform formats but should not perform I/O itself.
    - No I/O (files, network, stdout) or global-state mutation is performed by this function itself.
    - No external service calls are made.

## Control Flow:
flowchart TD
    A[Start] --> B{format_data True?}
    B -- Yes --> C[Call format_data(x, ppca=False) -> formatted_list]
    B -- No --> D[Set formatted_list = x (assumed iterable)]
    C --> E[inds = []]
    D --> E
    E --> F[For each arr in formatted_list]
    F --> G[Compute mask = np.isnan(arr)]
    G --> H[coords = np.argwhere(mask)]
    H --> I{coords.size == 0}
    I -- True --> J[inds.append(None)]
    I -- False --> K[idxs = coords[:,0]; inds.append(idxs)]
    J --> L[Continue loop]
    K --> L
    L --> M{len(inds) > 1?}
    M -- True --> N[Return inds (list)]
    M -- False --> O[Return inds[0] (single element)  // may raise IndexError if inds==[]]
    N --> P[End]
    O --> P

## Implementation notes and reimplementation checklist:
    - Import numpy with a canonical alias: import numpy as np
    - Call format_data(x, ppca=False) when format_data is True; the code in memory provides format_data which returns a list of numpy arrays for many input types.
    - For each arr in the resulting list:
        * Use np.isnan(arr) to produce a boolean mask of NaNs.
        * Use np.argwhere(mask) to get coordinates of True entries. For N-D arrays, argwhere returns coordinates per NaN; selecting [:,0] yields the first coordinate (commonly the row index).
        * If argwhere yields size 0, treat as no NaNs and return None for that array.
    - Preserve the behavior of returning a bare value for a single input and a list for multiple inputs to match original semantics.
    - If you want to avoid duplicates in returned indices, apply np.unique(idxs) before appending to inds.

## Examples:

Example 1 — single 1-D array with NaNs:
    import numpy as np
    data = np.array([1.0, np.nan, 3.0, np.nan])
    missing = missing_inds(data, format_data=False)
    # missing -> array([1, 3])

Example 2 — list of 2-D arrays:
    import numpy as np
    a = np.array([[1.0], [np.nan], [3.0]])
    b = np.array([[np.nan, 2.0], [4.0, 5.0], [6.0, np.nan]])
    missing = missing_inds([a, b], format_data=False)
    # missing -> [array([1]), array([0, 2])]

Example 3 — empty formatted input (shows literal-source failure mode):
    # If format_data(x, ppca=False) returns [] (empty list), the literal function will attempt to return inds[0]
    # and will raise IndexError. Guard against empty inputs:
    formatted = format_data(x, ppca=False)
    if len(formatted) == 0:
        handle_empty_case()
    else:
        missing = missing_inds(x, format_data=True)

