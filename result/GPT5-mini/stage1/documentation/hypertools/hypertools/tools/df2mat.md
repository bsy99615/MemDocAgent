# `df2mat.py`

## `hypertools.tools.df2mat.df2mat` · *function*

## Summary:
Transforms a DataFrame with mixed dtypes into a 2D numpy array by keeping non-object columns and one-hot (dummy) encoding columns with dtype 'object'; optionally returns the list of resulting column identifiers that map to the array columns.

## Description:
This helper converts a pandas DataFrame into a matrix suitable for numeric algorithms or plotting by:
- Selecting object-typed columns (dtype == 'object') and expanding each into multiple one-hot columns using pandas.get_dummies with a prefix equal to the original column name.
- Selecting the remaining (non-object) columns and joining the generated dummy columns onto them.
- Returning the DataFrame's underlying numpy array (df_num.values) and optionally the column identifiers.

Known callers:
- No direct callers were found in the provided repository scan. Typical usage is immediately before a numeric processing or visualization step that requires a numeric matrix (e.g., dimensionality reduction, clustering, plotting).

Rationale for extraction:
- Encapsulates the mixed-to-numeric conversion logic so downstream code can rely on a consistent array + labels contract.
- Avoids repeating dtype checks and dummy-encoding patterns across the codebase, centralizing choices such as prefixing and column ordering.

## Args:
    data (pandas.DataFrame or DataFrame-like):
        - The input table of shape (n_rows, n_columns).
        - Must support: select_dtypes(include=[...]) and select_dtypes(exclude=[...]), .columns, .values, and DataFrame.join.
        - Typical: pandas.DataFrame.
    return_labels (bool, optional):
        - If False (default), only the numpy.ndarray is returned.
        - If True, a tuple (array, labels) is returned where labels is a Python list describing each column of array in order.

Interdependencies:
    - When return_labels is True, the labels list length always equals the second dimension (number of columns) of the returned array.

## Returns:
    If return_labels is False:
        numpy.ndarray of shape (n_rows, n_features)
        - The rows correspond to the input DataFrame rows (same order).
        - n_features equals the number of non-object columns plus the total number of dummy columns produced.
        - The dtype of the numpy array is derived from the combined DataFrame; if the combined columns include mixed (non-numeric) dtypes, the returned ndarray may have dtype=object rather than a numeric dtype.
        - Edge-case returns:
            * If the DataFrame has n_rows >= 0 but results in zero columns, returns an ndarray with shape (n_rows, 0).
            * If input has zero rows, returns ndarray with shape (0, n_features).
    If return_labels is True:
        tuple (numpy.ndarray, list)
        - list contains identifiers from list(df_num.columns.values) in the same order as array columns.
        - Each label element equals the column identifier value from the DataFrame columns index (not necessarily a string — may be int, tuple, etc.).

## Raises:
    NameError:
        - If `pd` is not defined in the module namespace at runtime, the call to pd.get_dummies(...) will raise NameError. In the provided file-level imports `import pandas` is present (no alias), so calling df2mat as-is will raise NameError unless `pd` is defined elsewhere or the function is modified to call pandas.get_dummies.
    AttributeError / TypeError:
        - If `data` does not implement required attributes/methods (select_dtypes, columns, values, join), attribute access or method calls will raise AttributeError or TypeError.
    pandas exceptions:
        - pandas.get_dummies may raise ValueError/TypeError for invalid input; such exceptions propagate.
    No other custom exceptions are raised by this function.

## Constraints:
Preconditions:
    - `data` must be DataFrame-like and index-aligned for correct join behavior.
    - The runtime must have pandas.get_dummies accessible under the name used in the function (see NameError above).
Postconditions:
    - Returned array has n_rows equal to number of rows in `data`.
    - If labels are returned, len(labels) equals array.shape[1] and labels[i] corresponds to the i-th column of the array.
    - The input DataFrame is not mutated in-place (joins create new objects).
Guaranteed behavior:
    - Only columns whose pandas dtype is exactly 'object' are expanded into dummy columns. Columns with dtype 'category', datetime-like, boolean, or other non-'object' dtypes are included unchanged in df_num (i.e., they are not one-hot encoded by this function).

## Side Effects:
    - No external I/O or network interactions.
    - Allocates intermediate pandas DataFrames and numpy arrays in memory.
    - Does not mutate the caller's DataFrame in-place.

## Control Flow:
flowchart TD
    Start --> SelectTypes
    SelectTypes[df_str = data.select_dtypes(include=['object'])
                df_num = data.select_dtypes(exclude=['object'])]
    SelectTypes --> ForEachObjCol
    ForEachObjCol{for colname in df_str.columns}
    ForEachObjCol --> CreateDummies
    CreateDummies[pd.get_dummies(data[colname], prefix=colname)]
    CreateDummies --> Join
    Join[df_num = df_num.join(dummies)]
    Join --> ForEachObjCol
    ForEachObjCol -->|no more| BuildOutput
    BuildOutput[plot_data = df_num.values
               labels = list(df_num.columns.values)]
    BuildOutput --> ReturnDecision
    ReturnDecision{return_labels?}
    ReturnDecision -->|True| ReturnTuple
    ReturnDecision -->|False| ReturnArray
    ReturnTuple[return (plot_data, labels)] --> End
    ReturnArray[return plot_data] --> End

## Examples:
Note: examples assume pandas imported as alias pd (import pandas as pd) or the function is modified to call pandas.get_dummies directly.

Example 1 — Basic usage:
    import pandas as pd
    df = pd.DataFrame({
        'age': [21, 35, 40],
        'city': ['NY', 'SF', 'NY'],
        'score': [0.1, 0.8, 0.4]
    })
    arr = df2mat(df)
    # arr.shape -> (3, n_features)
    # To get labels:
    arr, labels = df2mat(df, return_labels=True)
    # labels might be: ['age', 'score', 'city_NY', 'city_SF']

Example 2 — Missing values in object columns:
    df2 = pd.DataFrame({'color': ['red', None, 'blue'], 'val':[1,2,3]})
    arr, labels = df2mat(df2, return_labels=True)
    # pandas.get_dummies by default does not create an explicit NaN dummy column:
    # the row with None will have zeros in the created color_* columns.

Example 3 — Categorical dtype not one-hot encoded:
    df3 = pd.DataFrame({'cat': pd.Series(['a','b','a'], dtype='category'), 'x':[1,2,3]})
    arr, labels = df2mat(df3, return_labels=True)
    # Because select_dtypes(include=['object']) ignores 'category' dtype,
    # 'cat' remains in df_num unchanged (not one-hot encoded). The returned array may contain non-numeric dtypes.

Example 4 — Empty DataFrame:
    empty = pd.DataFrame(columns=[])
    arr = df2mat(empty)
    # arr.shape -> (0, 0) or (n_rows, 0) depending on input rows/columns.

Example 5 — Fix for NameError: ensure pandas alias
    # Either ensure pandas is available as pd:
    import pandas as pd
    # or change the function call to use pandas.get_dummies(...) if pandas is imported without alias.

## Reimplementation hints:
    - Use data.select_dtypes(include=['object']) to locate object-typed columns.
    - Use data.select_dtypes(exclude=['object']) for the remainder.
    - For each object column, call pandas.get_dummies(data[column], prefix=column) and join onto df_num (index alignment preserves row order).
    - After joining all dummies, obtain the matrix via df_num.values and labels via list(df_num.columns.values).
    - Be explicit with imports: prefer `import pandas as pd` or call `pandas.get_dummies(...)` to avoid NameError.
    - If you require strict numeric output, consider applying data-type coercion (e.g., pandas.to_numeric with errors='coerce' or selecting numeric dtypes via select_dtypes(include=[numpy.number])) before returning.

