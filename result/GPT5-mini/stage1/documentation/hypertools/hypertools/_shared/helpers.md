# `helpers.py`

## `hypertools._shared.helpers.center` · *function*

## Summary:
Centers a list of numeric arrays by subtracting the column-wise mean (computed across all rows of every array) from each input array, returning a new list of centered arrays with the same shapes.

## Description:
Computes a single global column-wise mean vector from the vertically concatenated rows of the provided list of array-like objects, then subtracts that mean from each element in the list. This produces a set of arrays whose combined column-wise mean is approximately zero (subject to floating-point rounding).

Known callers within the provided context:
- No direct callers were discovered in the provided file-level context. Common callers in preprocessing pipelines include routines that prepare collections of observations for dimensionality reduction (PCA, t-SNE), clustering, or visualization, where centering across all observations is required.

Why this is a separate helper:
- The operation (stack all inputs → compute global column mean → subtract from each element) is a distinct, reusable preprocessing step. Encapsulating it avoids duplicating stacking/mean/subtraction logic, centralizes the assertion that the top-level container must be a list, and clarifies the precondition that constituent arrays must be stack-compatible.

## Args:
    x (list): Required. A Python list (must be exactly of type list) whose elements are numeric array-like objects (typically numpy.ndarray).
        - Each element should be 1-D or 2-D numeric arrays representing rows/observations; commonly each element has shape (n_i, d).
        - All elements must share the same number of columns d so numpy.vstack(x) succeeds.
        - The function asserts type(x) is list. Passing a tuple, generator, or numpy.ndarray instead of a list will raise AssertionError.
        - If elements are not numeric or cannot be converted to numeric arrays, numpy will raise TypeError when computing mean or during subtraction.

## Returns:
    list[numpy.ndarray]: A list with the same length as the input list. For each input element i, the corresponding output is i - mean_vector where mean_vector is the column-wise mean computed across np.vstack(x).
    - Each returned element has the same shape as its input element.
    - Dtype follows numpy broadcasting/casting rules (e.g., integer inputs may be promoted to float when subtracting a float mean).

## Raises:
    AssertionError: If type(x) is not exactly list. The assertion message is "Input data to center must be list".
    ValueError: Raised by numpy.vstack when:
        - x is empty (numpy.vstack([]) raises ValueError: need at least one array to stack).
        - Elements have incompatible shapes (different number of columns).
    TypeError: Raised by numpy operations if elements contain non-numeric data or cannot be interpreted as numeric arrays.
    MemoryError or other numpy exceptions: May propagate for extremely large inputs when stacking.

## Constraints:
Preconditions:
    - Caller must provide a Python list (not tuple or other sequence types).
    - The list must be non-empty and its elements must be compatible for vertical stacking (same column dimension).
    - Elements should be numeric (integers or floats) so mean and subtraction are defined.

Postconditions:
    - The returned list has the same number of elements and corresponding shapes as the input list.
    - The column-wise mean of np.vstack(returned_list) will be a vector of values close to zero (floating-point rounding may leave small residuals).

## Side Effects:
    - No file, network, or stdout I/O.
    - Does not mutate the input arrays: numpy arithmetic yields new arrays, so callers' inputs remain unchanged.
    - No global state or external resources are modified.

## Control Flow:
flowchart TD
    Start([Start]) --> IsList{type(x) is list?}
    IsList -- No --> AssertFail[Raise AssertionError with message "Input data to center must be list"]
    IsList -- Yes --> Stack[Call x_stacked = np.vstack(x)]
    Stack --> ComputeMean[Compute mean_vector = np.mean(x_stacked, axis=0)]
    ComputeMean --> ForEach[For each element i in x compute centered = i - mean_vector]
    ForEach --> Collect[Collect centered arrays into list]
    Collect --> Return[Return list of centered arrays]
    Return --> End([End])

## Examples:
1) Concrete numeric example (fully worked):
    - Input:
        x = [
            array([[1.0, 2.0],
                   [3.0, 4.0]]),    # shape (2, 2)
            array([[5.0, 6.0],
                   [7.0, 8.0]])     # shape (2, 2)
        ]
    - Stacked rows: np.vstack(x) => [[1,2],[3,4],[5,6],[7,8]]
    - Column-wise mean: mean_vector = [4.0, 5.0]
    - Output (each element minus mean_vector):
        [
            array([[-3.0, -3.0],
                   [-1.0, -1.0]]),
            array([[1.0, 1.0],
                   [3.0, 3.0]])
        ]
    - The column-wise mean of the concatenated outputs is [0.0, 0.0].

2) Error examples and how to avoid them:
    - Non-list input:
        Passing a numpy array or tuple will raise AssertionError. Convert sequences to a list first: call center(list_of_arrays) or center(list(x)).
    - Empty list:
        center([]) will raise ValueError from np.vstack; check that the list is non-empty before calling.
    - Incompatible shapes:
        center([array([[1,2]]), array([[1,2,3]])]) will raise ValueError from np.vstack; ensure all elements share the same column count.

3) Practical recommendations:
    - If you accept multiple sequence types upstream, normalize inputs before calling:
        safe_x = list(map(np.asarray, x))
        centered = center(safe_x)
    - For very large datasets where stacking all rows at once is memory-prohibitive, compute the global mean incrementally (accumulate column sums and counts) rather than using np.vstack, then subtract the computed mean from each block.

Notes:
    - This function favors clarity and simplicity (stack-and-subtract). If callers require more flexible input types or memory-efficient processing, perform input normalization or implement an incremental centering routine before calling.

## `hypertools._shared.helpers.scale` · *function*

## Summary:
Linearly rescales all numeric values across a list of array-like datasets so the global minimum maps to -1 and the global maximum maps to +1, returning a list of scaled numpy arrays preserving each input's shape.

## Description:
This helper computes a single global affine transform from the combined values of all inputs, then applies it element-wise to each input. It:
- Stacks the input list with numpy.vstack to compute a global minimum (m1) and global range (m2).
- Defines the transform f(value) = 2 * ((value - m1) / m2) - 1.
- Returns a list where each entry is the transformed version of the corresponding input.

Typical usage context:
- Intended as a private/shared preprocessing utility used by plotting and analysis pipelines that require consistent scaling across multiple datasets (so that color, size, or coordinate ranges are comparable).
- Known callers could not be retrieved during documentation generation; treat it as a small internal helper.

Why this is a separate function:
- Ensures a single global min/max are used across multiple datasets, avoiding duplicated logic.
- Encapsulates stacking, scalar extraction, and broadcasting-safe application of the transform, keeping callers simpler.

## Args:
    x (list): Required. A Python list (exact type check: type(x) is list) of array-like numeric items.
        - Each element must be convertible to a numeric numpy.ndarray.
        - Elements must be stack-compatible for numpy.vstack (commonly all elements have same number of columns/features; rows can differ).
        - Note: passing a tuple or other sequence type will fail the type assertion; the function requires a list.

## Returns:
    list[numpy.ndarray]: A list of numpy.ndarray objects with the same per-element shapes as the inputs. Numeric values are returned as floating-point values (division yields float dtype).
    - Normal outcome: if global range m2 > 0, the minimum over all returned values will be approximately -1 and the maximum approximately +1 (subject to floating-point rounding).
    - Zero-range edge case: if m2 == 0 (all values equal), the division computes 0/0 and the function produces NaN values (numpy produces NaNs for 0/0). The function does not handle this case internally.

## Raises:
    AssertionError:
        - Raised if the input is not exactly a Python list.
        - Exact message: "Input data to scale must be list"
    Any exception raised by numpy.vstack:
        - e.g., ValueError or TypeError if inputs are not stackable or not numeric — these propagate from numpy.
    No explicit DivisionByZero exception is raised by this function; numpy will produce runtime warnings and NaNs/infs when dividing by zero.

## Constraints:
    Preconditions:
        - Caller must supply a Python list of array-like numeric items.
        - Items must be compatible with numpy.vstack.
    Postconditions:
        - Returns a list with the same number of elements and per-element shapes as the input.
        - If m2 > 0, outputs are scaled to the interval [-1, 1] across the union of all input values.
        - If m2 == 0, outputs contain NaNs (due to 0/0); no correction is applied.

## Side Effects:
    - No file, network, or stdout IO.
    - No mutation of the original input list objects (operations create new numpy arrays).
    - May emit numpy runtime warnings (e.g., divide-by-zero) depending on numpy's error settings.

## Control Flow:
flowchart TD
    A[Start: receive x] --> B{type(x) is list?}
    B -- No --> C[AssertionError: "Input data to scale must be list"]
    B -- Yes --> D[Compute x_stacked = numpy.vstack(x)]
    D --> E[m1 = numpy.min(x_stacked)]
    E --> F[m2 = numpy.max(x_stacked - m1)]
    F --> G{m2 == 0?}
    G -- Yes --> H[Compute f -> division 0/0 -> NaN values (numpy)]
    G -- No --> I[Compute f(value) = 2*((value - m1)/m2) - 1]
    H --> J[Return list of arrays containing NaNs]
    I --> J[Return list of scaled arrays]

## Examples:
Example 1 — Typical multi-array inputs (concrete, runnable):
    import numpy as np
    a = np.array([[0, 1],
                  [2, 3]])
    b = np.array([[4, 5]])
    x = [a, b]
    out = scale(x)
    # Computation:
    # global min m1 = 0, global max = 5, m2 = 5
    # transform: f(v) = 2*(v/5) - 1
    # out[0] -> array([[-1. , -0.6],
    #                   [-0.2,  0.2]])
    # out[1] -> array([[0.6, 1. ]])

Example 2 — Constant-valued inputs (zero range demonstrates behavior and recommended handling):
    import numpy as np
    a = np.array([1.0, 1.0])
    b = np.array([1.0])
    x = [a, b]
    out = scale(x)
    # Since all values equal, m1 = m2 = 1 -> m2 - m1 == 0 and division yields 0/0
    # out will contain arrays filled with numpy.nan

Recommended caller-safe pattern to avoid NaNs:
    import numpy as np
    stacked = np.vstack(x)
    rng = np.max(stacked) - np.min(stacked)
    if rng == 0:
        # choose desired behavior; example: return zeros in same shapes
        safe_out = [np.zeros_like(arr, dtype=float) for arr in x]
    else:
        safe_out = scale(x)

Implementation hints:
- Use numpy.vstack to compute a scalar global min and max.
- Compute m1 = numpy.min(x_stacked) and m2 = numpy.max(x_stacked - m1) (equivalent to max - min).
- Apply numpy.divide(x - m1, m2) to ensure element-wise floating division.
- Return a Python list of numpy arrays rather than a single stacked array so callers keep original per-dataset structure.

## `hypertools._shared.helpers.group_by_category` · *function*

## Summary:
Converts an iterable of categorical labels into 0-based integer category indices by (optionally flattening one list level), computing the sorted unique categories, and mapping each label to its index in that sorted unique list.

## Description:
This helper normalizes categorical labels into integer indices that are suitable for indexing colors, markers, or grouping buckets in plotting and preprocessing pipelines. It implements two small responsibilities: optional one-level flattening when list elements are present, and producing a deterministic mapping from category value to integer index using Python's sorted() order of the unique values.

Known callers within the provided snapshot:
- No direct callers were found in the provided snapshot. In a typical codebase, it is used by visualization and metadata-handling code that needs numeric indices for categorical metadata (e.g., mapping class names to color palette indices before plotting).

Why this is a separate function:
- It centralizes consistent behavior (one-level flattening policy and sorted-unique ordering) so that multiple callers need not duplicate flattening, uniqueness, and indexing logic. It also encapsulates the choice of ordering (sorted order) so callers can rely on deterministic index assignments.

## Args:
    vals (iterable):
        - An iterable of category labels. Elements must be hashable (so they can be put into a set) and mutually comparable (so sorted() can order them).
        - Allowed shapes:
            * Flat iterable, e.g., ['a', 'b', 'a'] or [1, 2, 1]
            * One-level nested list, e.g., [['a', 'b'], ['a']] — the function detects the presence of list elements and will flatten one level.
        - Important: The function performs multiple passes over vals (an any(...) check and later iterations). Therefore vals must be a reusable iterable (e.g., list, tuple) or the caller must convert single-pass iterables/generators to a sequence before calling.

    Interdependencies:
        - If any element is an instance of Python list (checked with isinstance(i, list)), the function flattens vals by concatenating those sublists. Other sequence types (tuples, sets, numpy arrays) do not trigger the automatic flattening.

## Returns:
    list[int]: A list of integers corresponding to the (possibly flattened) input order. Each integer is the 0-based index of the label within the sorted list of unique labels.
    - Empty input yields [].
    - If input was nested and flattened, the return list matches the flattened element order.
    - Indices are in the contiguous range [0, K-1], where K is the number of unique categories.

## Raises:
    TypeError:
        - If vals is not iterable, attempting to iterate will raise TypeError.
        - If any element is unhashable (e.g., a dict or an unflattened list), set(vals) will raise a TypeError.
        - If elements are not mutually comparable (for example, mixing str and int in Python 3), sorted(set(vals)) may raise TypeError.
        - If vals is a one-shot iterator/generator, the initial any(...) check will consume elements and later iterations will be empty or incomplete; this manifests as incorrect results rather than a specific TypeError — callers should avoid passing one-shot iterators.

    Note: The function itself does not explicitly raise specialized exceptions; all exceptions stem from the built-in operations it uses (iteration, set construction, sorting, and list.index).

## Constraints:
Preconditions:
    - vals must be iterable and support multiple iterations (or be converted to a list/tuple before calling).
    - Elements must be hashable (for set construction).
    - Elements should be comparable with each other so sorted() can determine an order.
    - One-level flattening applies only when elements are list instances.

Postconditions:
    - The returned list length equals the length of vals after optional one-level flattening.
    - Category-to-index mapping is deterministic and based on the sorted order of unique values.
    - No external state is modified.

## Side Effects:
    - None: no I/O, no external state mutation, no network or filesystem access.
    - Memory allocation: temporary lists and a set are created; memory cost is O(n + k) where n is the (flattened) number of items and k is the number of unique items.

## Performance notes:
    - Time complexity:
        * Building the set of unique values: O(n) on average (hashing).
        * Sorting unique values: O(k log k), where k is number of unique values.
        * Mapping each value with sorted_unique.index(val): each index lookup is O(k), so worst-case mapping step is O(n * k).
      For large n and k, repeated list.index lookups can be expensive. If performance is critical, callers should build a dict mapping value -> index from sorted_unique to achieve O(n) mapping time.

## Control Flow:
flowchart TD
    Start --> IsIterable{Is vals iterable?}
    IsIterable -- No --> RaiseTypeError[TypeError from iteration]
    IsIterable -- Yes --> AnyListCheck{any(isinstance(i, list) for i in vals)}
    AnyListCheck -- True --> Flatten[Flatten one list level: vals = concat sublists]
    AnyListCheck -- False --> KeepOriginal[Use vals as-is]
    Flatten --> BuildSet
    KeepOriginal --> BuildSet
    BuildSet[unique_set = set(vals); sorted_unique = sorted(unique_set)]
    BuildSet --> Map[For each val in vals: get sorted_unique.index(val)]
    Map --> Return[Return list of indices]
    Return --> End

## Examples:
- Basic usage:
    Input: ['b', 'a', 'b']
    Behavior: sorted unique -> ['a', 'b']
    Output: [1, 0, 1]

- Numeric labels:
    Input: [10, 2, 10, 3]
    Behavior: sorted unique -> [2, 3, 10]
    Output: [2, 0, 2, 1]

- One-level nested lists (flattened automatically):
    Input: [['red', 'blue'], ['red']]
    Flattened: ['red', 'blue', 'red']
    sorted unique -> ['blue', 'red']
    Output: [1, 0, 1]

- Generator (pitfall) — do NOT pass a generator directly:
    Problematic input: (x for x in ['a', 'b', 'a'])
    Why problematic: The any(...) check will consume the generator; subsequent iterations will be empty and produce an incorrect result (likely []).
    Correct usage: Convert to a list first:
        vals_list = list(my_generator)
        indices = group_by_category(vals_list)

- Handling unhashable items:
    Input: ['a', {'x': 1}]
    Behavior: set(vals) raises TypeError because dict is unhashable; callers should pre-process such items to a hashable form (e.g., convert dicts to tuples) before calling or catch the TypeError.

Guidance and alternatives:
    - If you need to preserve first-seen ordering rather than sorted ordering, build the unique-order list yourself (e.g., using an OrderedDict or seen set in order of appearance) and map values to indices from that list rather than relying on this function.
    - For large inputs where performance matters, replace the final list.index-based mapping with a dict lookup:
        * sorted_unique = sorted(set(vals))
        * index_map = {v: i for i, v in enumerate(sorted_unique)}
        * return [index_map[v] for v in vals]

## `hypertools._shared.helpers.vals2colors` · *function*

## Summary:
Converts a sequence (or a list-of-sequences) of numeric values into an equal-length list of RGB color tuples sampled from a seaborn colormap.

## Description:
This helper maps numeric values to colors by binning values into `res` evenly spaced intervals spanning the observed value range and selecting the corresponding color from a seaborn color palette. Typical callers pass a column/vector of numeric scalars (e.g., data labels, scalar time values, cluster indices) to obtain an RGB color for each element for plotting.

Known callers:
- No specific call sites were provided in the supplied context. Callers in visualization code typically call this function when they need to color data points by a continuous or ordinal numeric variable before plotting.

Why this is a separate function:
- Encapsulates the common task of mapping numeric scalars to RGB tuples (palette creation, binning, and mapping) so callers do not duplicate the palette/ranking logic. It enforces the boundary of converting numeric arrays/lists to normalized color tuples suitable for plotting libraries.

## Args:
    vals (iterable[float] | iterable[iterable[float]]):
        Iterable of numeric values (e.g., list, numpy array). If the iterable contains at least one element that is a Python list, the function will flatten one level by concatenating the sublists (i.e., it treats the input as a list-of-lists and flattens it to a single list).
        - Allowed values: numeric types (ints/floats) only.
        - Not allowed: non-iterable objects (will raise TypeError when iterated); empty iterables (will raise a ValueError when min/max is computed).
    cmap (str | matplotlib colormap-like), optional:
        Name of the colormap to use (string accepted by seaborn.color_palette) or any argument supported by seaborn.color_palette. Defaults to 'GnBu'.
    res (int), optional:
        Number of discrete color samples to generate from the colormap (number of bins). Must be a positive integer. Defaults to 100.

Interdependencies:
- The length of the returned color list equals the length of the (possibly flattened) `vals`.
- The function expects that the module namespace provides `np` (NumPy) and `sns` (Seaborn) names; these must be available as aliases to numpy and seaborn respectively.

## Returns:
    list[tuple[float, float, float]]:
        A list of RGB color tuples (three floats in the range [0.0, 1.0]) of the same length as the (optionally flattened) input values. Each tuple corresponds to the color assigned to the input value by binning the numeric value into one of `res` intervals across the range [min(vals), max(vals)+1].
        Edge/variant return values:
        - If an input value is below the first bin edge, np.digitize will place it in bin 0, which after subtracting 1 becomes -1; indexing the palette with -1 returns the last color in the palette (this behavior is inherited from numpy indexing and is not explicitly guarded against).
        - Values greater than the last bin edge are placed into the last bin index, yielding the last palette color as expected.

## Raises:
    TypeError:
        If `vals` is not iterable (iteration attempt in the initial comprehension will raise TypeError).
    ValueError:
        If `vals` is empty or if NumPy's min/max operations fail (e.g., empty iterable leads to "zero-size array to reduction operation minimum which has no identity").
    Other exceptions from numpy/seaborn:
        If `vals` contains non-numeric types, NumPy operations (np.min, np.max, np.digitize) may raise TypeError or ValueError depending on the types.

## Constraints:
Preconditions:
- `vals` must be an iterable of numeric values or an iterable containing Python lists of numeric values (when flattening is desired).
- `res` must be a positive integer.
- The module namespace must contain the symbols `np` (NumPy) and `sns` (Seaborn) so that calls to `np.array`, `np.digitize`, and `sns.color_palette` succeed.

Postconditions:
- The function returns a list of RGB tuples of length equal to the length of the (possibly flattened) `vals`.
- The returned colors are sampled from the specified colormap and correspond monotonically to the binned ordering of `vals`.

## Side Effects:
- None: the function does not perform I/O, does not mutate its inputs, and does not update global state. It calls external library functions (NumPy and Seaborn) but does not persist or print any results.

## Control Flow:
flowchart TD
    Start --> IsIterable{"Can iterate vals?"}
    IsIterable -- No --> RaiseTypeError[TypeError raised by iteration]
    IsIterable -- Yes --> ContainsList?{any(el is list for el in vals)}
    ContainsList? -- Yes --> FlattenVals[vals = list(itertools.chain(*vals))]
    ContainsList? -- No --> UseVals[use vals as given]
    UseVals --> BuildPalette[sns.color_palette(cmap,res) -> np.array]
    BuildPalette --> ComputeEdges[np.linspace(min(vals), max(vals)+1, res+1)]
    ComputeEdges --> ComputeRanks[np.digitize(vals, edges) - 1]
    ComputeRanks --> IndexPalette[palette[ranks,:]]
    IndexPalette --> ConvertTuples[convert rows to tuple(i)]
    ConvertTuples --> Return[return list of RGB tuples]
    ComputeEdges -- Error(empty) --> RaiseValueError[ValueError from np.min/np.max]
    IndexPalette -- PossibleNegativeIndex --> LastColor[negative index selects last palette color]

## Examples:
Example 1 — basic usage with a list of floats:
    vals = [0.0, 2.5, 5.0, 7.25]
    colors = vals2colors(vals, cmap='viridis', res=10)
    # returns a list of four (r,g,b) tuples (floats 0..1), one per input value

Example 2 — flattening a list-of-lists:
    vals = [[0, 1, 2], [3, 4]]
    colors = vals2colors(vals, cmap='GnBu', res=50)
    # input is flattened to [0,1,2,3,4], returns 5 color tuples

Example 3 — error handling for empty input:
    vals = []
    try:
        colors = vals2colors(vals)
    except ValueError as e:
        # handle empty input (np.min/np.max failure)
        pass

Notes and implementation remarks:
- The function flattens at most one level and only when it detects at least one list element; nested containers or numpy arrays will not be flattened automatically.
- The function relies on numpy.digitize and numpy indexing semantics (including negative indices). If callers require stricter handling of out-of-range values, they should pre-clamp values or post-process ranks before indexing the palette.

## `hypertools._shared.helpers.vals2bins` · *function*

## Summary:
Converts numeric values (or a one-level list-of-lists) into integer bin indices by creating `res` uniformly spaced bins across [min(vals), max(vals)+1] and assigning each value to a bin; returns a list of integer indices in the expected range 0..res-1 for valid numeric inputs.

## Description:
This small utility centralizes the process of discretizing continuous scalar values into integer bin indices. It:
1. Optionally flattens a one-level list-of-lists (only when an element is exactly of Python type list).
2. Builds `res+1` uniformly spaced bin edges from min(vals) to max(vals)+1.
3. Uses numpy.digitize with its default behavior (right=False) to map values to bin indices, then subtracts 1 from each digitize result to produce zero-based indices.

Known callers:
- No direct callers were found in the provided snapshot. When used elsewhere, callers typically invoke this function when mapping scalar continuous data to discrete categories for plotting (e.g., color/marker assignment), bucketing, or grouping.

Why this is a separate helper:
- Encapsulates the flattening, bin-edge construction, and digitization index-shift into one reusable, consistent operation so callers do not duplicate edge construction or post-processing.

## Args:
    vals (iterable):
        - Iterable of numeric values (int/float) or an iterable whose elements may be lists of numeric values.
        - If any element of `vals` is exactly of Python type list (isinstance(el, list) is True for at least one element), the function flattens one level via itertools.chain(*vals) and proceeds with the flattened sequence.
        - Notes:
            * Tuples, numpy arrays, and other sequence types do NOT trigger the flattening branch.
            * Passing a generator/iterator is allowed but may be consumed by the function's internal checks and numpy operations; generators may therefore yield surprising results if reused after calling this function.
    res (int, optional):
        - Number of bins to create. Defaults to 100.
        - Must be a positive integer; non-integer or non-positive values will cause numpy.linspace to raise or produce invalid behavior.

## Returns:
    list[int]:
        - A list of integer indices, one per processed scalar value (after optional flattening).
        - For normal numeric inputs (finite ints/floats), returned indices fall in the range [0, res-1].
            * Explanation: numpy.digitize with right=False assigns indices according to bins[i-1] <= x < bins[i]; because bin_edges start at min(vals) and end at max(vals)+1, every original value x in vals satisfies min(vals) <= x <= max(vals) < max(vals)+1, and thus maps to an index between 0 and res-1 after the "-1" shift.
        - Unusual values:
            * NaN values may propagate through numpy reductions and produce NaN-based behavior or errors; results are undefined for NaN-containing inputs.
            * If input contains values strictly less than the computed min (which can occur only if the inputs mutate between computing min/max and digitize, or via non-deterministic iterables), then digitize could yield 0 which becomes -1 after shifting — this is a pathological case and not expected for typical usage.

## Raises:
    TypeError:
        - If `vals` is not iterable (e.g., an integer), the generator expression used in the any(...) check will raise TypeError when attempting to iterate `vals`.
        - If the flattening branch runs, itertools.chain(*vals) will attempt to iterate each element passed to it; if any of those elements are not iterable (for example, an int), a TypeError will be raised when chain tries to iterate that element.
    ValueError:
        - If `vals` (after flattening when applicable) is empty, numpy.min or numpy.max will raise a ValueError (e.g., "zero-size array to reduction operation minimum which has no identity").
    TypeError / ValueError:
        - If elements of `vals` are non-numeric strings or incompatible types, numpy.min/max or numpy.digitize may raise TypeError or ValueError.
    Other numpy errors:
        - If `res` is not valid for numpy.linspace, numpy may raise ValueError or related exceptions.

## Constraints:
Preconditions:
    - `vals` must be an iterable containing at least one numeric scalar (or an iterable of lists where flattening leads to at least one numeric scalar).
    - `res` must be a positive integer.
Postconditions:
    - Returns a list of integers of the same length as the processed scalar elements.
    - No external state is modified; the function performs pure in-memory computation.

## Side Effects:
    - None. The function does not perform I/O or mutate external/global state.

## Control Flow:
flowchart TD
    A[Start: vals, res] --> B{Is vals iterable?}
    B -- No --> E[TypeError raised when iterating]
    B -- Yes --> C{Any element is exactly type list?}
    C -- Yes --> D[Flatten one level: vals = list(chain(*vals))]
    C -- No --> F[Use vals as-provided]
    D --> G[Compute min_val = np.min(vals)]
    F --> G
    G --> H[Compute max_val = np.max(vals)]
    H --> I[Create bin_edges = np.linspace(min_val, max_val + 1, res + 1)]
    I --> J[raw_indices = np.digitize(vals, bin_edges)  (right=False)]
    J --> K[indices = raw_indices - 1]
    K --> L[Return list(indices)]

## Examples:
1) Typical usage:
    vals = [0.1, 0.5, 1.2, 3.4]
    bins = vals2bins(vals, res=4)
    # returns a list of four integers, typically in 0..3 for these finite values

2) Flattening a list-of-lists:
    vals = [[0.0, 0.5], [1.0, 2.0]]
    bins = vals2bins(vals, res=3)
    # function flattens to [0.0,0.5,1.0,2.0] and returns four indices in 0..2

3) Empty input handling:
    vals = []
    try:
        bins = vals2bins(vals)
    except ValueError:
        # numpy.min/max on empty input raises; handle accordingly
        bins = []

4) Guarding against non-iterable inputs and flattening surprises:
    def safe_vals2bins(v, res=100):
        if not hasattr(v, '__iter__'):
            raise TypeError("vals must be iterable")
        # optionally pre-flatten or validate element types before calling vals2bins
    # Validate nested contents before calling vals2bins to avoid TypeError from chain(*vals)

## `hypertools._shared.helpers.interp_array` · *function*

## Summary:
Produces a higher-resolution 1-D resampling of a numeric sequence by constructing an index-based interpolator over the input array and evaluating it at fractional index steps determined by interp_val.

## Description:
- Known callers within the provided snapshot: none found.
- Responsibility boundary: Build an interpolator that treats the input sequence element at position i as the value at index i, then evaluate that interpolator on a denser set of fractional indices between 0 (inclusive) and len(arr)-1 (exclusive). This helper isolates index construction, interpolator creation, and evaluation so callers do not duplicate those steps.
- Implementation assumptions: The function references two module-level names: np (expected to behave like numpy and provide arange) and pchip (expected to be a callable that accepts (x, y) and returns an evaluator callable, e.g., scipy.interpolate.PchipInterpolator or an equivalent wrapper). If these names are not bound appropriately in the module, the function will raise NameError or other exceptions from the missing/incorrect objects.

## Args:
    arr (array-like): One-dimensional sequence of numeric values (e.g., list, tuple, numpy.ndarray, pandas.Series). The function uses len(arr) and integer indexing into arr; elements are treated as values at integer indices 0..len(arr)-1.
    interp_val (int or float, optional): Number of subdivisions per unit index; controls sampling density. Defaults to 10. Must be finite and non-zero (interp_val == 0 causes division by zero when computing the sampling step). Positive values produce increasing fractional indices from 0 up to but not including len(arr)-1. Negative values will produce descending samples per numpy.arange semantics but are atypical.

Interdependencies:
- The function depends on the module-level bindings np and pchip. Typical binding: np = numpy and pchip = scipy.interpolate.PchipInterpolator (or a wrapper that returns a callable when called as pchip(x, y)).

## Returns:
    numpy.ndarray (or array-like): The values returned by evaluating the interpolator at the fractional index positions (q(xx)).
    - The returned array corresponds to q(xx) where:
        * x = np.arange(0, len(arr), 1)
        * xx = np.arange(0, len(arr)-1, 1/interp_val)
        * q = pchip(x, arr)
    - If xx is empty (for example, when len(arr) <= 1 or when the np.arange call produces an empty range), an empty array is returned.

## Raises:
    NameError: If the module-level names 'np' or 'pchip' are not defined (the function directly references these names).
    ZeroDivisionError: If interp_val is zero (1/interp_val triggers division by zero).
    ValueError, TypeError, or other exceptions from the interpolator:
        - pchip(x, arr) may raise if x and arr are inconsistent, non-numeric, or otherwise invalid for the interpolator.
        - q(xx) may raise if xx contains values outside the interpolator's supported domain or if xx is invalid for the interpolator implementation.
    All exceptions from pchip and the returned interpolator are propagated to the caller.

## Constraints:
Preconditions:
    - arr should be 1-D and contain numeric values. Many interpolators require at least two points; callers should ensure len(arr) >= 2 for meaningful interpolation.
    - The module must bind:
        * np to an object with arange behavior compatible with numpy.arange
        * pchip to a callable that returns an evaluator when called with (x, y)
    - interp_val should be finite and non-zero.

Postconditions:
    - The returned array contains interpolated values sampled from index 0 (inclusive) up to index len(arr)-1 (exclusive) at increments of 1/interp_val.
    - The function does not modify arr.

## Side Effects:
- No I/O (files, network, or stdout).
- No mutation of input arr.
- No modification of global or external state beyond calling pchip and the returned interpolator (any side effects from those callables are not introduced by interp_array itself).

## Control Flow:
flowchart TD
    Start --> CheckNames[Check: 'np' and 'pchip' exist]
    CheckNames -- missing --> RaiseNameError[Raise NameError]
    CheckNames -- present --> ComputeX[Compute x = np.arange(0, len(arr), 1)]
    ComputeX --> ComputeXX[Compute xx = np.arange(0, len(arr)-1, 1/interp_val)]
    ComputeXX --> CreateInterpolator[Call q = pchip(x, arr)]
    CreateInterpolator --> Evaluate[Evaluate and return q(xx)]
    Evaluate --> End

## Examples:
- Concrete numeric example (assuming np behaves like numpy and pchip behaves like scipy.interpolate.PchipInterpolator):
    * Given arr = [0, 10, 20] and interp_val = 2
    * x = [0, 1, 2]
    * xx = arange(0, 2, 0.5) -> [0.0, 0.5, 1.0, 1.5]
    * q = pchip(x, arr) (monotonic cubic interpolator)
    * Returned values q(xx) will approximately be [0.0, 5.0, 10.0, 15.0] (values between the input indices interpolated at half-step resolution)

- Edge-case guidance:
    * To include the final index len(arr)-1 in the sampling, use a different sampling strategy such as linspace(0, len(arr)-1, N) because np.arange stop is exclusive and the current xx construction excludes the endpoint.
    * If arr may have length 0 or 1, perform an early check in the caller and return arr (or an appropriate empty/single-element array) rather than invoking interp_array, which will produce an empty xx or cause interpolator errors.

## `hypertools._shared.helpers.interp_array_list` · *function*

## Summary:
Takes a list of array-like sequences and returns a same-length list where each element is the result of applying an index-based interpolator (via interp_array) to the corresponding input array; by default increases sampling density by a factor of 10.

## Description:
- Known callers within the provided snapshot: none found.
- Typical usage context: used when a pipeline needs to up-sample or smooth many parallel numeric series (e.g., multiple time series, trajectories, or feature sequences) by applying the same per-array interpolation logic to every member of a collection.
- Why this is a separate function: it encapsulates the common mapping pattern "apply interp_array to every element of a list" and centralizes minimal precondition checks and return shape expectations so callers do not need to write the loop repeatedly. It enforces the responsibility boundary of "collection-level application" while delegating per-array interpolation details and validation to interp_array.

## Args:
    arr_list (sequence[list|tuple|numpy.ndarray|pandas.Series]): A non-empty sequence (e.g., list or tuple) whose elements are array-like objects acceptable to interp_array. Each element should typically be a 1-D numeric sequence (list, tuple, or numpy/pandas 1-D array). The function accesses arr_list[0].shape and will iterate over all elements; therefore each element is expected to be indexable and compatible with interp_array.
    interp_val (int or float, optional): Sampling density factor passed through to interp_array. Defaults to 10. Must be finite and non-zero (interp_array can raise or propagate errors for invalid values).

Interdependencies and module-level requirements:
    - The module must expose a name interp_array (callable) that accepts (arr, interp_val) and returns a numeric array-like result (see interp_array documentation).
    - The module must expose a name np providing numpy-like zeros behavior (used to allocate an initial list of zero arrays). If these bindings are missing, NameError will be raised.

## Returns:
    list[numpy.ndarray]: A Python list with the same length as arr_list. Each element is the value returned by interp_array(arr, interp_val) for the corresponding input arr. Typical element semantics:
        - If arr is a 1-D numeric sequence of length N>=2, the returned element is a denser numeric array sampled by interp_array according to interp_val.
        - If an input element produces an empty result in interp_array (for example, because interp_array returns an empty array for very short inputs), the corresponding list element is that empty array.
    Edge cases:
        - If arr_list is empty, the function does not return a value; instead it raises IndexError while trying to access arr_list[0] during initialization (see Raises).
        - Returned list length always equals len(arr_list) when arr_list is non-empty.

## Raises:
    IndexError: If arr_list is empty — the implementation immediately accesses arr_list[0].shape when constructing the initial list of zeros.
    AttributeError: If arr_list[0] (or any element expected to have .shape for the initialization or during subsequent operations) does not expose a shape attribute when the function attempts to read it.
    NameError: If interp_array or np are not defined in the module namespace when called.
    Any exception raised by interp_array: interp_array may raise ValueError, TypeError, ZeroDivisionError, or other exceptions (for example when interp_val is zero, non-finite, or input arrays are invalid). Those exceptions are propagated unchanged.

## Constraints:
Preconditions:
    - arr_list must be a non-empty sequence.
    - Every element of arr_list must be acceptable input to interp_array (typically a 1-D numeric sequence).
    - Module-level names interp_array and np must be defined and behave as expected (interp_array is a callable that returns a numeric array-like; np provides zeros allocation).
    - interp_val should be a finite, non-zero numeric value appropriate for interp_array.

Postconditions:
    - The original arr_list is not modified by this function.
    - The returned list has the same number of elements as arr_list (provided arr_list was non-empty).
    - Each returned element is the result of interp_array applied to the corresponding input element.

## Side Effects:
    - No file, network, or stdout I/O is performed by this function.
    - No mutation of the input arr_list or its elements is performed by this function (it constructs a new list and assigns newly returned arrays to it).
    - Any side effects originating from interp_array (if that callable has side effects) will be observed; this function does not introduce additional external state changes.

## Control Flow:
flowchart TD
    Start --> CheckNonEmpty[Check: arr_list non-empty? (attempts to read arr_list[0].shape)]
    CheckNonEmpty -- empty --> RaiseIndexError[Raise IndexError (access arr_list[0])]
    CheckNonEmpty -- non-empty --> InitZeros[Create list of zeros using arr_list[0].shape]
    InitZeros --> ForEach[For each (idx, arr) in enumerate(arr_list)]
    ForEach --> CallInterp[Call interp_array(arr, interp_val)]
    CallInterp --> Assign[Assign result to smoothed[idx]]
    Assign --> NextIter{More items?}
    NextIter -- yes --> ForEach
    NextIter -- no --> Return[Return smoothed list]
    Return --> End

## Examples:
- Typical (conceptual) example:
    Given arr_list containing two 1-D numeric arrays, both length >= 2, and interp_val = 4, calling this function returns a two-element list where each element is the denser array produced by interp_array for the corresponding input. Each output element is independent (the function applies interp_array to each input separately).

- Error handling example (conceptual):
    If you cannot guarantee arr_list is non-empty, guard the call:
    - If arr_list may be empty, check len(arr_list) > 0 before calling, or handle IndexError to avoid an unhandled exception.
    - If arr_list elements may not be 1-D numeric sequences, validate or convert them (for example, convert pandas.Series or Python lists to numpy.ndarray) before passing them in.

Notes:
    - The initial allocation of zero arrays using arr_list[0].shape is just an implementation convenience; the function replaces each element with the value returned by interp_array, so the returned element shapes depend entirely on interp_array's outputs.
    - To include the final index of each input series in the interpolation, consult interp_array's documentation: interp_array constructs fractional indices using an exclusive stop; callers that need inclusive endpoints may need a different sampling strategy.

## `hypertools._shared.helpers.parse_args` · *function*

## Summary:
Expands a set of argument specifications into a per-item list of argument tuples: for each element in x, returns a tuple of values taken either from per-item argument sequences (parallel to x) or from constant arguments.

## Description:
This helper converts a collection of argument descriptors into a list of argument-tuples sized to match x. It iterates over x (by index) and for each argument descriptor in args either:
- If the descriptor is a tuple or list of the same length as x, it picks the element at the current index (per-item argument).
- Otherwise, it uses the descriptor value unchanged (constant argument for every x element).

Known callers within the provided context:
- None identified in the supplied file-level context. Typical callers (not verified here) are higher-level functions that accept a dataset-like sequence x and a parallel set of parameters where some parameters may be specified either as a global constant or as an item-wise list matching x.

Why this logic is isolated:
- It encapsulates the common responsibility of normalizing mixed constant-vs-per-item arguments into a single uniform structure (list of tuples) so downstream code can iterate over x with a ready-made per-item argument tuple. Keeping this logic in its own function avoids duplicating length-checking and per-item selection across callers.

## Args:
    x (sized iterable): A sequence-like object (must support len(x) and enumeration) whose length n determines the per-item expansion. Example types: list, tuple. Empty sequences are allowed (will produce an empty result).
    args (iterable): An iterable of argument descriptors. Each element may be:
        - a tuple or list of length n (one value per element of x), or
        - any other Python object treated as a scalar/constant that will be used for every element of x.
    Interdependencies:
        - If any descriptor in args is a tuple or list, its length must equal len(x). Otherwise the function prints an error and terminates the process (sys.exit(1)).

## Returns:
    list[tuple]: A list of length len(x). Each element is a tuple whose entries correspond to the provided args in the same order:
        - For a per-item descriptor (tuple/list of length n), the tuple contains the descriptor's element at that index.
        - For a scalar descriptor, the tuple contains the same scalar reference repeated for every returned tuple.
    Edge cases:
        - If args is empty, the function returns a list of empty tuples (one per item in x).
        - If x is empty (len(x) == 0), the function returns an empty list.

## Raises:
    SystemExit (via sys.exit(1)): Triggered when any element of args is a tuple or list whose length does not equal len(x). Before exiting, the function prints:
        Error: arguments must be a list of the same length as x

## Constraints:
Preconditions:
    - x must be a sized iterable (len(x) must be valid) and support iteration (enumeration).
    - args must be iterable.
    - The function only recognizes Python tuple and list types as "per-item" sequences. Other sequence-like types (e.g., numpy.ndarray, pandas.Series) are NOT treated as per-item descriptors and will be used as constant arguments.

Postconditions:
    - The returned list has length equal to len(x).
    - Each returned element is a tuple whose arity equals the number of descriptors in args.

## Side Effects:
    - Writes an error message to stdout via print(...) when a list/tuple descriptor length mismatches.
    - Calls sys.exit(1) on descriptor length mismatch, which terminates the entire Python process unless intercepted (raises SystemExit).
    - No other I/O, global state mutation, or external service calls occur.

## Control Flow:
flowchart TD
    Start --> Check_args_iterable["Iterate over args (enumerate)"]
    Check_args_iterable --> For_each_x["For each index i,item in x (enumerate)"]
    For_each_x --> For_each_arg["For each arg in args"]
    For_each_arg --> Is_list_or_tuple{"Is arg an instance of tuple or list?"}
    Is_list_or_tuple -- Yes --> Length_eq_lenx{"len(arg) == len(x) ?"}
    Length_eq_lenx -- Yes --> Append_arg_i["Append arg[i] to tmp"]
    Length_eq_lenx -- No  --> Print_error["print error message"] --> Sys_exit["sys.exit(1)"] --> End
    Is_list_or_tuple -- No  --> Append_arg_const["Append arg (constant) to tmp"]
    Append_arg_i --> Continue_args["continue to next arg"]
    Append_arg_const --> Continue_args
    Continue_args --> After_args["After all args for this x: append tuple(tmp) to args_list"]
    After_args --> Next_x_or_end{"More items in x?"}
    Next_x_or_end -- Yes --> For_each_x
    Next_x_or_end -- No  --> Return_args_list["return args_list"] --> End

## Examples:
1) Basic per-item + constant arguments
    Given x = ['a', 'b', 'c'] and args = ([1, 2, 3], 'const'):
    Result: [(1, 'const'), (2, 'const'), (3, 'const')]

2) All constant arguments
    Given x = [10, 20] and args = ('foo', 3.14):
    Result: [('foo', 3.14), ('foo', 3.14)]

3) Empty args
    Given x = [1,2,3] and args = []:
    Result: [(), (), ()]  (three empty tuples)

4) Descriptor type caveat (numpy array treated as constant)
    Given x = ['x1','x2'] and args = (numpy.array([1,2]),):
    Because numpy.ndarray is not an instance of tuple or list, the ndarray is treated as a constant.
    Result: [(array([1,2]),), (array([1,2]),)]

5) Error behavior and interception
    If x = [1,2,3] and args contains a list of length 2 (mismatched):
    The function prints "Error: arguments must be a list of the same length as x" and calls sys.exit(1), raising SystemExit.
    To guard against process termination, callers can catch SystemExit:
    - Typical pattern: wrap the call in try/except SystemExit to handle or translate the error into an exception.

## `hypertools._shared.helpers.parse_kwargs` · *function*

## Summary:
Expand a mapping of keyword argument values into a list of per-item keyword dictionaries: for each element of the input sequence, produce a dict with the same keys as kwargs where list/tuple values are either indexed per-item (when lengths match) or replaced with None, and non-list values are reused for every item.

## Description:
This utility transforms a single kwargs mapping into a list of kwargs mappings aligned with the items of x. It is intended for call sites that need to iterate over a collection of items and apply potentially per-item keyword settings (for example, plotting several datasets where some kwargs vary per dataset and others remain constant).

Known callers within the codebase:
- None provided in this isolated snippet. Typical usage is within higher-level routines that iterate over an iterable x and need a per-item kwargs dict for each element prior to processing/plotting.

Why extracted:
- Centralizes the broadcasting/broadcast-fallback behavior for keyword arguments: handling scalar repetition, per-item lists, and the fallback of None when a provided list has a mismatched length. This keeps callers simpler (they can always iterate an output list of dicts) and avoids duplicating expansion logic.

## Args:
    x (sequence, required):
        Iterable of items to process. Must support iteration (for .. in) and must implement __len__ (len(x) is called). Typical types: list, tuple, pandas.Series, numpy.ndarray.
    kwargs (mapping-like, required):
        A mapping from keys (typically strings) to values. Required capabilities:
          - Iterable over keys (i.e., "for key in kwargs" yields each key).
          - Subscriptable by those keys (kwargs[key] must be valid).
        Typical type: dict. Values may be:
          - A list or tuple: if len(value) == len(x) then value[i] is used for item i; otherwise the function assigns None for that key on every item.
          - Any other object (including numpy.ndarray, pandas.Index, generator, custom objects): treated as a scalar and reused for every item because the function only treats Python tuple and list as per-item sequences.

Notes on interdependencies:
    - Per-item expansion for a key happens only when isinstance(kwargs[key], (tuple, list)) is True and len(kwargs[key]) == len(x).
    - If kwargs[key] is a tuple/list but its length differs from len(x), that key's value becomes None in every per-item dict.

## Returns:
    list[dict[str, Any]]
        A list whose length equals len(x). For each index i the i-th element is a dict containing every key from kwargs mapped to:
          - kwargs[key][i] when kwargs[key] is a tuple/list and len(kwargs[key]) == len(x)
          - None when kwargs[key] is a tuple/list but len(kwargs[key]) != len(x)
          - kwargs[key] (the original object) when kwargs[key] is not a tuple/list

Edge cases:
    - If kwargs is empty, returns a list of empty dicts (one per element in x).
    - If x is empty, returns an empty list.
    - Numpy arrays and other non-(list/tuple) sequence types are treated as scalars (not expanded element-wise).

## Raises:
    The function contains no explicit raise statements; errors arise from invalid inputs or unsupported operations:
    - TypeError: if x does not support len(x) (e.g., a generator without __len__), a call to len(x) will raise TypeError.
    - TypeError: if kwargs is None or otherwise not iterable, "for kwarg in kwargs" raises TypeError.
    - TypeError / KeyError / IndexError: if kwargs is iterable but does not implement __getitem__ for the iterated elements (i.e., not mapping-like), then accessing kwargs[kwarg] may raise one of these exceptions depending on kwargs' runtime type and the iterated values.
    Recommendation: pass a mapping (e.g., dict) as kwargs to avoid these errors.

## Constraints:
Preconditions:
    - len(x) must be available (x must implement __len__).
    - kwargs must be mapping-like: iterates over keys and supports indexing by those keys (kwargs[key]).

Postconditions:
    - The returned list length equals len(x).
    - Each returned dict contains exactly the set of keys present in kwargs.
    - For each key, the value is determined as specified in Returns.

## Side Effects:
    - None. Function performs pure in-memory operations: creates new dictionaries and a new list. No I/O or external state mutation.

## Control Flow:
flowchart TD
    Start([Start])
    CheckItems{Enumerate x}
    ForEachItem[For each index i in 0..len(x)-1:]
    InitTmp[Create tmp = {}]
    ForEachKey[For each key in kwargs:]
    IsListTuple{Is kwargs[key] instance of tuple or list?}
    LengthCheck{Does len(kwargs[key]) == len(x)?}
    UseIndexed[Set tmp[key] = kwargs[key][i]]
    UseNone[Set tmp[key] = None]
    UseScalar[Set tmp[key] = kwargs[key]]
    AppendTmp[Append tmp to kwargs_list]
    End([Return kwargs_list])

    Start --> CheckItems --> ForEachItem --> InitTmp --> ForEachKey --> IsListTuple
    IsListTuple -- yes --> LengthCheck
    LengthCheck -- true --> UseIndexed --> ForEachKey
    LengthCheck -- false --> UseNone --> ForEachKey
    IsListTuple -- no --> UseScalar --> ForEachKey
    ForEachKey --> AppendTmp --> ForEachItem --> End

## Examples:
1) Matching per-item lists and scalar reuse
    x = ['a', 'b', 'c']
    kwargs = {'color': ['r', 'g', 'b'], 'alpha': 0.6}
    returns:
      [{'color': 'r', 'alpha': 0.6},
       {'color': 'g', 'alpha': 0.6},
       {'color': 'b', 'alpha': 0.6}]

2) Mismatched-length list becomes None
    x = [0,1,2]
    kwargs = {'label': ['one', 'two'], 'visible': True}
    returns:
      [{'label': None, 'visible': True},
       {'label': None, 'visible': True},
       {'label': None, 'visible': True}]

3) Non-list sequences are treated as scalars
    import numpy as np
    x = [1,2]
    kwargs = {'weights': np.array([0.1, 0.2])}
    returns:
      [{'weights': array([0.1,0.2])},
       {'weights': array([0.1,0.2])}]

4) Invalid usage examples (error handling)
    - kwargs = None  -> TypeError when attempting to iterate kwargs.
    - x = (i for i in range(3)) (a generator without __len__) -> TypeError when len(x) is called.
    - kwargs = ['a','b'] (a list) -> iteration yields 'a' then 'b', and then kwargs['a'] tries to index the list by the string 'a' raising TypeError or KeyError; therefore always pass a mapping (e.g., dict) as kwargs.

## `hypertools._shared.helpers.reshape_data` · *function*

## Summary:
Partition a vertically stacked observation matrix into per-category 2-D numpy arrays according to a hue vector, returning the per-category arrays and their corresponding labels lists.

## Description:
This function takes a sequence of array-like data blocks, stacks them into a single 2-D observation array using np.vstack, and then groups each stacked row into buckets determined by the categorical values in hue. The returned arrays preserve category order based on the first occurrence of each hue value.

Known callers and typical context:
- No direct callers were present in the supplied excerpt. In typical usage within preprocessing or plotting pipelines, callers supply a list of data blocks (which may be individual rows or multi-row blocks) and a per-row categorical vector (hue) to produce per-category datasets for group-wise plotting or analysis.

Why this is a separate helper:
- It centralizes three related responsibilities (stacking input blocks, computing unique categories while preserving first-seen order, and grouping rows and labels per category), avoiding repeated, error-prone code across callers and ensuring consistent ordering and alignment guarantees.

## Args:
    x (Sequence[array-like]):
        Sequence of array-like objects (numpy arrays or array-like) that can be vertically concatenated with np.vstack. Each element may be a single row (1-D) or a 2-D block with one or more rows.
        - Constraint: All elements must have compatible column dimensions so that np.vstack(x) succeeds.
        - Constraint: After stacking, the total number of rows must be equal to len(hue) for correct one-to-one mapping between stacked rows and hue entries.

    hue (Sequence[hashable]):
        Sequence of categorical values, one per stacked row, used to assign each row into a category. Duplicates are allowed and the order of returned categories follows their first occurrence in this sequence.
        - Constraint: len(hue) should match the number of rows in np.vstack(x). If not, indexing and alignment errors may occur.

    labels (Sequence[any] | None):
        Optional sequence of per-row label values. If None, labels defaults to a list of None of length len(hue).
        - Behavior: If provided and shorter than hue, zip(hue, labels) truncates iteration (rows beyond the shorter length are ignored). If provided and longer than hue, extra labels are ignored.
        - Recommendation: Provide labels of length equal to len(hue) for correct alignment.

## Returns:
    tuple (grouped_arrays, grouped_labels)
    - grouped_arrays (list[numpy.ndarray]):
        A list with one element per category (categories ordered by first occurrence in hue). Each element is a 2-D numpy.ndarray produced by np.vstack of the rows assigned to that category. Shape for category i is (n_i, m) where n_i >= 1 is the number of rows for that category and m is the number of columns/features.
    - grouped_labels (list[list]):
        A list of Python lists; grouped_labels[i] contains the labels corresponding to the rows in grouped_arrays[i]. Elements may be None if labels was None.

Edge-case return notes:
    - Every returned grouped_arrays[i] is a 2-D numpy.ndarray with at least one row, provided that the loop iterates over all rows (i.e., labels is None or labels length >= len(hue)). If labels is shorter than hue and truncation causes a category to receive zero rows, attempting np.vstack on that empty list will raise a ValueError before return.
    - grouped_labels elements are Python lists (not numpy arrays).

## Raises:
    ValueError:
        - Raised by np.vstack(x) if:
            * x is empty (no arrays to stack).
            * The array shapes are incompatible for vertical stacking (e.g., different number of columns).
        - Raised by np.vstack(i) in the final return if any per-category list i is empty (this occurs if hue contains categories that receive no appended rows due to truncation from a shorter labels sequence).
    IndexError:
        - May occur when accessing x_stacked[idx] if idx >= number of rows in x_stacked (i.e., total stacked rows < len(hue)). This indicates a mismatch between x and hue lengths.
    Note:
        - The function does not perform explicit length validation; these exceptions are raised by underlying numpy operations or Python indexing when preconditions are violated.

## Constraints:
Preconditions:
    - x must be a non-empty sequence whose elements are compatible with np.vstack.
    - The number of rows produced by np.vstack(x) should equal len(hue) for correct per-row mapping.
    - If labels is provided, it should ideally have length equal to len(hue). If labels is None, the function provides a labels list of the correct length automatically.

Postconditions:
    - For each category index i, grouped_arrays[i].shape[0] == len(grouped_labels[i]) (alignment of rows and labels) holds when iteration covered all stacked rows.
    - The order of categories in the return follows their first appearance in hue.

## Side Effects:
    - None. The function does not perform any I/O, does not modify global state, and does not mutate input arrays (np.vstack creates new arrays).

## Performance note:
    - Category lookup uses categories.index(point) inside the loop, making the grouping operation O(n * k) in the worst case (n = number of rows, k = number of unique categories). For large datasets with many categories, consider building a mapping {category: index} before the loop to reduce lookups to amortized O(1).

## Control Flow:
flowchart TD
    Start --> ComputeCategories[Compute categories = list(sorted(set(hue), key=list(hue).index))]
    ComputeCategories --> StackX[Compute x_stacked = np.vstack(x)]
    StackX --> InitLists[Initialize x_reshaped and labels_reshaped lists for each category]
    InitLists --> LabelsNoneCheck{labels is None?}
    LabelsNoneCheck -- Yes --> SetLabels[labels = [None] * len(hue)]
    LabelsNoneCheck -- No --> Continue
    SetLabels --> LoopStart
    Continue --> LoopStart
    LoopStart[For idx,(point,label) in enumerate(zip(hue,labels))] --> FindIndex[Compute idx_cat = categories.index(point)]
    FindIndex --> AppendRow[Append x_stacked[idx] to x_reshaped[idx_cat]]
    AppendRow --> AppendLabel[Append label to labels_reshaped[idx_cat]]
    AppendLabel --> LoopStart
    LoopEnd[After loop completes] --> FinalStack[Return ([np.vstack(i) for i in x_reshaped], labels_reshaped)]
    LoopStart -->|If labels shorter than hue| TruncatedIteration[Loop ends early — some stacked rows ignored]
    TruncatedIteration --> FinalStack

## Examples:
Happy path:
    import numpy as np
    x = [np.array([[1.0, 2.0]]), np.array([[3.0, 4.0]])]  # two single-row blocks
    hue = ['A', 'B']                  # one hue value per stacked row
    labels = ['r1', 'r2']
    grouped_arrays, grouped_labels = reshape_data(x, hue, labels)
    # grouped_arrays -> [array([[1.0, 2.0]]), array([[3.0, 4.0]])]
    # grouped_labels -> [['r1'], ['r2']]

Multi-row block and automatic None labels:
    x = [np.array([[1., 2.], [5., 6.]]), np.array([[3., 4.]])]
    hue = ['X', 'Y', 'X']  # corresponds to stacked rows in order
    grouped_arrays, grouped_labels = reshape_data(x, hue, None)
    # categories = ['X', 'Y']
    # grouped_arrays[0] has two rows (for 'X'), grouped_labels[0] == [None, None]

Error handling example:
    import numpy as np
    x = [np.array([[1.0, 2.0]])]  # total rows = 1
    hue = ['A', 'B']             # length 2 => mismatch
    try:
        reshape_data(x, hue, None)
    except IndexError:
        # Indicates that x produced fewer rows than hue length
        handle_misaligned_inputs()
    except ValueError:
        # Could occur due to incompatible shapes or attempting to vstack empty per-category lists
        handle_bad_shapes()

Implementation hints for re-implementers:
    - To preserve first-seen category order: deduplicate hue values while preserving order (e.g., iterate hue and append unseen values).
    - Use np.vstack to build x_stacked and to convert per-category lists to 2-D arrays before returning.
    - To avoid ValueError on empty per-category lists when labels may be shorter than hue, validate that iteration covered all stacked rows or ensure labels is None or the same length as hue beforehand.

## `hypertools._shared.helpers.patch_lines` · *function*

## Summary:
Append the first row of each subsequent 2D array to the current array for every element except the last, mutating the input sequence and returning it.

## Description:
This function iterates through a sequence of 2-dimensional array-like elements and, for each element except the final one, vertically stacks the first row of the next element onto the end of the current element. The function modifies the provided sequence in-place (it replaces elements of the sequence with the newly stacked arrays) and then returns the same sequence object.

Known callers within the provided codebase:
- None discovered in the provided source excerpt. Typical usage (outside the excerpt) is in pipelines that need to "patch" or connect adjacent line segments so that each segment explicitly includes the first row of the following segment (for plotting or interpolation continuity).

Why this is a separate helper:
- Responsibility boundary: it encapsulates the small but specific task of connecting adjacent 2D data segments by copying the next segment's first row into the current segment. Extracting this logic avoids repetition in code that prepares line/trajectory data for plotting or interpolation and makes the side-effect (in-place mutation) explicit to callers.

## Args:
    x (sequence of 2D array-like): A mutable sequence (e.g., list or numpy.ndarray of objects) whose elements are 2-dimensional numeric arrays. Each element x[i] must be indexable as x[i][row_index, col_index] (NumPy-style indexing). The function uses x[i+1][0, :] to obtain the first row of the next element.

    Notes on allowed values and interdependencies:
    - Sequence length: any non-negative integer. If len(x) <= 1, the function performs no stacking and returns x unchanged.
    - Element shape: for each index i from 0 to len(x)-2, x[i] must be a 2D array with shape (m_i, n) where m_i >= 1, and x[i+1] must have shape (m_{i+1}, n) with m_{i+1} >= 1. The number of columns n must match between x[i] and x[i+1]; otherwise stacking will fail.
    - The function expects element indexing x[i+1][0,:] to return a 1-dimensional row with the same number of columns as x[i].

## Returns:
    sequence: The same sequence object passed in as x, but with elements 0..len(x)-2 replaced by vertically stacked arrays where each new x[i] equals the previous x[i] with x[i+1]'s first row appended as an extra row.
    - If x is empty or length 1, the returned sequence is identical to the input (no modification).
    - The returned object is the same object reference as the input sequence (i.e., mutation in-place).

## Raises:
    NameError:
        - If the name 'np' is not defined in the module's runtime namespace, a NameError will be raised when the function attempts to call np.vstack. (The source code calls np.vstack; ensure an appropriate alias such as numpy as np is available.)

    IndexError:
        - If any x[i+1] does not provide a row 0 (for example, x[i+1] has zero rows or is not indexable in that way), accessing x[i+1][0,:] will raise an IndexError.

    ValueError:
        - If the number of columns in x[i] and x[i+1][0,:] differ such that numpy.vstack cannot align them, numpy will raise a ValueError.

    TypeError:
        - If x is not a sequence with len(), or its elements are not indexable in the expected way (e.g., scalars), indexing or vstack calls can raise TypeError.

## Constraints:
Preconditions:
    - The caller must supply a mutable sequence of 2D array-like objects.
    - For all adjacent pairs (x[i], x[i+1]) that will be patched, both must have at least one row and the same number of columns.
    - The runtime environment must expose the name 'np' referring to a module that provides vstack (commonly numpy imported as np).

Postconditions:
    - For every index i in 0..len(x)-2, after the call x[i] is a 2D array whose last row equals the former first row of x[i+1].
    - The original sequence object is returned and has been mutated in place; x[len(x)-1] is unchanged.

## Side Effects:
    - In-place mutation: elements of the input sequence x are replaced. Callers retain references to the same sequence object, but element objects at indices 0..len(x)-2 will be new array objects (the result of vstack).
    - No file I/O, network I/O, or stdout/stderr output.
    - No external state (globals beyond reading 'np') is modified by this function, apart from the contents of the provided sequence object.

## Control Flow:
flowchart TD
    Start --> IsLenLE1{len(x) <= 1?}
    IsLenLE1 -- Yes --> ReturnUnchanged[Return x unchanged]
    IsLenLE1 -- No --> LoopStart[for idx in 0 .. len(x)-2]
    LoopStart --> GetNextRow[Get row = x[idx+1][0,:]]
    GetNextRow --> Vstack[Call np.vstack([x[idx], row])]
    Vstack --> Assign[Assign result to x[idx]]
    Assign --> NextIdx{idx < len(x)-2?}
    NextIdx -- Yes --> LoopStart
    NextIdx -- No --> End[Return mutated x]

## Examples:
Assume a numeric array library bound to the name np (e.g., numpy imported as np).

Example scenario (conceptual, no import lines shown):
    - Given x is a list of three 2D arrays with identical column counts:
        x[0] shape = (m0, n)
        x[1] shape = (m1, n)
        x[2] shape = (m2, n)
    - After calling the helper:
        x[0] will have shape = (m0 + 1, n) and its last row equals the former first row of x[1]
        x[1] will have shape = (m1 + 1, n) and its last row equals the former first row of x[2]
        x[2] remains unchanged with shape = (m2, n)

Example usage pattern and error handling guidance:
    - Before calling, verify shapes to avoid exceptions:
        * Check len(x) and skip if <= 1.
        * For each adjacent pair, assert x[i].ndim == 2, x[i+1].ndim == 2, and x[i].shape[1] == x[i+1].shape[1].
    - If you cannot guarantee consistent shapes, perform validation and handle ValueError/IndexError around the call to provide a clear error message to callers.

## `hypertools._shared.helpers.is_line` · *function*

## Summary:
Determines whether a matplotlib-style format specification should be treated as a line-only style (no marker characters present). Returns True when the specification is None or contains no marker symbols from matplotlib's Line2D.markers.

## Description:
This helper inspects a format specification (commonly used with matplotlib plotting functions) and decides whether it describes a "line" (no marker symbols present) versus a marker-containing format. It centralizes marker-detection logic using matplotlib's canonical marker set.

Known callers and context:
    - No direct call sites were discoverable in the provided snapshot. Typical callers are plotting/formatting utilities that accept a matplotlib-like format string and need to branch between drawing pure lines and drawing markers (for choosing plotting primitives, default marker/linestyle behavior, or validation).
    - Callers should pass validated string-like inputs; this function performs minimal input coercion (only numpy.bytes_ is decoded).

Why this logic is extracted:
    - Avoids duplicating the marker detection across plotting helpers.
    - Keeps callers focused on high-level plotting decisions rather than marker-set maintenance or bytes-decoding concerns.

## Args:
    format_str (str | None | numpy.bytes_):
        - Description: A matplotlib-style format specification or None.
        - Allowed types and handling:
            * None — interpreted as indicating a line (no marker).
            * str — inspected directly for any marker symbols (e.g., '-', 'o', '^', 's').
            * numpy.bytes_ (numpy scalar) — decoded to a Python str using UTF-8 before inspection.
        - Notes:
            * Only numpy.bytes_ is specially handled and decoded. Built-in bytes objects are NOT decoded and will likely raise TypeError during membership checks.
            * The function performs string membership checks; non-string-like inputs (other than numpy.bytes_) will generally raise TypeError.

## Returns:
    bool
        - True: input is considered a line-only specification (either None or a string containing no marker symbols defined by matplotlib.lines.Line2D.markers).
        - False: input contains at least one marker symbol (indicating a marker is present).
        - Edge cases:
            * format_str is None -> returns True.
            * format_str is a numpy.bytes_ scalar -> decoded to str then evaluated.
            * format_str is a built-in bytes object -> membership checks will raise TypeError (not handled by this function).

## Raises:
    - NameError: if the global name `np` is not defined in the module (the function uses `np.bytes_` for the isinstance check). In the provided file-level imports `numpy` may be present without the `np` alias; if so, calling this function will raise NameError.
    - TypeError: if format_str is a non-string-like object that does not support the 'in' membership check with a str (for example, passing an int, or passing built-in bytes while comparing to str symbols). The function expects string-like input (or numpy.bytes_) for correct operation.
    - Any exceptions raised while accessing Line2D.markers (e.g., unusual matplotlib environment problems) will propagate.

## Constraints:
    Preconditions:
        - The module must expose numpy under the name `np` (so that np.bytes_ is available) or callers must ensure format_str is not a numpy.bytes_ scalar.
        - If format_str is not None, it should be a string-like object (or a numpy.bytes_ scalar). The function performs membership tests against the format_str.
    Postconditions:
        - No global state is mutated.
        - The function returns a boolean indicating presence/absence of marker symbols.

## Side Effects:
    - None. Pure computation only; no I/O, no global mutations, no external service calls.

## Control Flow:
flowchart TD
    Start[[Start]]
    CheckBytes{isinstance(format_str, np.bytes_)?}
    Decode[format_str = format_str.decode('utf-8')]
    BuildMarkers[markers = list(map(lambda x: str(x), Line2D.markers.keys()))]
    IsNone{format_str is None?}
    ContainsMarker{any(str(symbol) in format_str for symbol in markers)?}
    ReturnTrue[/Return True/]
    ReturnFalse[/Return False/]

    Start --> CheckBytes
    CheckBytes -- yes --> Decode --> BuildMarkers
    CheckBytes -- no --> BuildMarkers
    BuildMarkers --> IsNone
    IsNone -- yes --> ReturnTrue
    IsNone -- no --> ContainsMarker
    ContainsMarker -- yes --> ReturnFalse
    ContainsMarker -- no --> ReturnTrue

## Examples:
    # Assumes numpy is available as np and matplotlib is installed.

    import numpy as np
    from hypertools._shared.helpers import is_line

    # Line-only styles -> True
    is_line('-')            # True (line style only)
    is_line('b-')           # True (blue solid line)
    is_line(None)           # True (None treated as line)

    # Marker present -> False
    is_line('ro')           # False (contains marker 'o')
    is_line('g^--')         # False (contains marker '^')

    # numpy.bytes_ input -> decoded and evaluated
    bs = np.bytes_('ro')
    is_line(bs)             # False (decoded to 'ro')

    # Built-in bytes will not be decoded and likely raise TypeError:
    try:
        is_line(b'ro')     # Raises TypeError: a bytes-like object is required, not 'str' (from membership check)
    except TypeError:
        pass

    # Invalid non-string input -> TypeError
    try:
        is_line(123)
    except TypeError:
        # validate/convert inputs before calling
        pass

## `hypertools._shared.helpers.memoize` · *function*

## Summary:
Provides a decorator-like wrapper that attaches a simple in-memory cache to a callable so repeated calls with identical arguments return a previously computed result instead of recomputing.

## Description:
- Known callers:
    - No direct callers were discovered in the provided code scan. This helper is intended for local use as a decorator on functions within the codebase that are deterministic and relatively expensive to compute.
- Typical usage context:
    - Applied to pure or mostly-pure functions (no relevant side effects) whose return value depends only on input arguments, to avoid repeated work on identical inputs.
    - Common places: expensive CPU-bound transformations, deterministic data processing functions, or hotspots where identical calls occur frequently.
- Why this logic is extracted:
    - Centralizes and standardizes a simple memoization pattern across the codebase.
    - Exposes the cache via the original callable's attribute (callable.cache) so callers can inspect, clear, or selectively invalidate cached results without additional boilerplate at each call site.

## Args:
    obj (callable): The function or callable to wrap. Required.
        - Must accept positional and/or keyword arguments that can be meaningfully converted to strings for keying.
        - Must allow assignment of new attributes (i.e., obj.cache = {}) at decoration time; many user-defined functions and callable objects do, but some built-in callables or objects may not.

## Returns:
    callable: A wrapper function that:
        - Computes a cache key as the string concatenation of str(args) and str(kwargs).
        - If the key exists in the cache (a dict stored as obj.cache), returns the cached value.
        - Otherwise, calls the original callable with the provided arguments, stores the successful result in obj.cache under the computed key, and returns it.
    Additional observable effect: the original callable object is mutated at decoration time to have a 'cache' attribute referencing the cache dictionary.

## Raises:
    - AttributeError: If the original object does not permit setting arbitrary attributes, the assignment obj.cache = {} performed at decoration time will raise AttributeError.
    - TypeError: If a non-callable is passed as obj, the decorator will still try to attach a cache attribute; however, calling the returned wrapper will raise TypeError when it attempts to invoke obj(*args, **kwargs).
    - Any exception raised by the wrapped callable during execution is propagated to the caller and is not stored in the cache.

## Constraints:
- Preconditions:
    - obj must be a callable (intended usage). If obj is not callable, the wrapper will fail at invocation.
    - obj must permit attribute assignment (so obj.cache can be created). Builtins and certain extension objects may reject this.
    - Arguments passed to the decorated callable should have stable and meaningful str(...) representations if you expect effective caching.
- Postconditions:
    - After successful decoration, obj.cache exists and is a dict mapping string keys to cached results.
    - After a successful call with a key not previously seen, obj.cache contains that key mapped to the returned value.
    - The wrapper preserves the original callable's metadata (name, docstring) via functools.wraps.

## Side Effects:
- Mutates the decorated callable by adding a 'cache' attribute (a dict) at decoration time.
- Uses only in-memory storage; no file, network, or external I/O occurs.
- Cache can grow unbounded; callers are responsible for memory management (e.g., clearing the cache).
- Not safe for concurrent writes: simultaneous calls from multiple threads/processes can race when creating or populating cache entries.

## Implementation notes and edge cases:
- Key generation: key = str(args) + str(kwargs)
    - Two different argument tuples that stringify to the same value will collide in the cache.
    - Keyword argument ordering can lead to different string forms for semantically identical calls if argument insertion orders differ before stringification; in CPython 3.7+ dict insertion order is preserved, but callers may still construct kwargs in different orders.
    - Objects with non-deterministic or pointer-based string representations (e.g., objects that include memory addresses in their repr) will make caching unreliable.
    - Large objects (e.g., numpy arrays) produce long string representations, increasing key size and CPU cost to build keys.
- Mutability: If an argument is mutated after caching, the cached result may become stale because keys are based on the argument's string form at call time.
- Exceptions: exceptions from the wrapped callable are not cached; repeated calls that raise will re-run the underlying computation each time.
- Clearing/managing cache:
    - The cache is accessible at obj.cache. To clear the entire cache, call obj.cache.clear().
    - To remove a specific entry, delete the corresponding key from obj.cache.
    - To replace the cache with a custom mapping, assign obj.cache = <new dict-like>.

## Control Flow:
flowchart TD
    Start[Call wrapper] --> BuildKey[Compute key = str(args) + str(kwargs)]
    BuildKey --> InCache{Is key in obj.cache?}
    InCache -- Yes --> ReturnCached[Return obj.cache[key]]
    InCache -- No --> CallOriginal[Call obj(*args, **kwargs)]
    CallOriginal --> Store[Store result in obj.cache[key]]
    Store --> ReturnResult[Return stored result]
    CallOriginal -- Raises --> Propagate[Propagate exception to caller]

## Examples (usage described, no inline code):
1) Decorating a deterministic expensive function:
    - Decorate the function at definition time with this helper.
    - First call with a new set of arguments computes and stores the result in function.cache.
    - Subsequent calls with the same arguments return the result from function.cache instantly.
    - To free memory, the caller can call function.cache.clear() or delete specific keys.

2) Handling attribute-assignment failures:
    - If you plan to decorate builtins or third-party callables that may reject new attributes, decorate a wrapper function you control instead; this avoids AttributeError at decoration time.
    - If an AttributeError is observed at decoration time, wrap the callable in a small user-defined function or use an alternative cache mechanism that stores mappings externally (not as an attribute on the callable).

3) Concurrent environment caution:
    - In multi-threaded contexts, consider protecting access to function.cache with a lock or using a thread-safe caching utility. Without synchronization, two threads calling the same uncached key may both compute and attempt to store the result concurrently, leading to wasted computation or subtle races.

Overall, this helper provides a compact, transparent memoization mechanism optimized for clarity and convenience; it trades generality and thread-safety for simplicity (string-based keys, exposed per-callable cache, no eviction policy).

## `hypertools._shared.helpers.get_type` · *function*

## Summary:
Detects the runtime data container/type and returns a short string tag describing that type (e.g., list of strings, numeric numpy array, pandas DataFrame, etc.).

## Description:
This helper centralizes logic for classifying an input "data" object into one of a small set of canonical internal type-tags used by the codebase.

Known callers:
- No direct callers were discovered during the repository scan performed for this documentation. In the original project, this function is intended to be used by upstream data ingestion, validation, and plotting helpers that need to branch behavior based on whether input is a DataFrame, numpy array, list (of strings/numbers/arrays), string, or a DataGeometry instance.

Why this is a separate function:
- The function encapsulates the type-detection policy (which types are supported and how to distinguish lists of strings vs lists of numbers vs lists of arrays) so that every caller does not repeat brittle index-based checks. It provides a single place to update supported types and the text tags returned to the rest of the system.

## Args:
    data (object): The input to classify. Accepted/recognized concrete types (as inspected by the function) include:
        - list: a Python list whose first element determines the list subtype:
            * list of str/bytes -> returns 'list_str'
            * list of int/float -> returns 'list_num'
            * list of numpy.ndarray -> returns 'list_arr'
        - numpy.ndarray: inspected at data[0][0]; if that element is str/bytes -> 'arr_str', otherwise -> 'arr_num'
        - pandas.DataFrame -> 'df'
        - str or bytes -> 'str'
        - DataGeometry (from datageometry) -> 'geo'

    Notes on parameter dependencies:
    - For list processing the function examines only the first element (data[0]) to determine the subtype.
    - For numpy.ndarray processing the function accesses data[0][0] to infer whether it's an array of strings or numeric values.
    - Therefore the function requires that containers/arrays be non-empty and indexable in these positions (see Constraints).

## Returns:
    str: One of the following canonical type tags:
        - 'list_str' : list whose first element is str or bytes
        - 'list_num' : list whose first element is int or float
        - 'list_arr' : list whose first element is a numpy.ndarray
        - 'arr_str'  : numpy.ndarray whose element at [0][0] is str or bytes
        - 'arr_num'  : numpy.ndarray otherwise (numeric-like at [0][0])
        - 'df'       : pandas.DataFrame
        - 'str'      : str or bytes
        - 'geo'      : DataGeometry instance

    Edge-case returns:
    - There are no special fallback return values; the function always either returns one of the tags above or raises an exception if the input cannot be classified.

## Raises:
    TypeError: If the input is not one of the recognized types or the first-element checks fall into an unsupported type branch.
        - Exact message raised by the code for unsupported top-level types or unsupported list-element types:
          'Unsupported data type passed. Supported types: Numpy Array, Pandas DataFrame, String, List of strings, List of numbers'
    IndexError (or other Indexing/LookupErrors): If the function attempts to access data[0] or data[0][0] but the container/array is empty or has an unexpected shape, the underlying indexing operation will raise an IndexError (this is not explicitly caught by the function).
    TypeError / AttributeError (from indexing): If data is indexable but data[0] is not subscriptable (for the numpy array branch, accessing data[0][0]), a TypeError or IndexError from that access may occur.

## Constraints:
Preconditions:
    - If data is a list, it must be non-empty and its first element must be an instance of one of these: (str, bytes), (int, float), or numpy.ndarray.
    - If data is a numpy.ndarray, it must be indexable at [0][0]; typically this implies a 2D (or higher) array or a 1D array whose element at index 0 is itself indexable and holds a str/bytes value.
    - If data is a pandas.DataFrame, str/bytes, or DataGeometry instance, no extra precondition beyond the isinstance check is required.

Postconditions:
    - On success, returns one of the documented string tags and performs no mutation of the input data.
    - The function does not mutate global state or the input; it only inspects type/contents and returns a tag.

## Side Effects:
    - None. The function performs only type checks and index access on the provided object; it does not perform I/O, network calls, global state mutation, or caching.

## Control Flow:
flowchart TD
    Start --> IsList{isinstance(data, list)}
    IsList -- Yes --> ListHasFirstElement{data[0] type}
    ListHasFirstElement -- str/bytes --> ReturnListStr[/return 'list_str'/]
    ListHasFirstElement -- int/float --> ReturnListNum[/return 'list_num'/]
    ListHasFirstElement -- np.ndarray --> ReturnListArr[/return 'list_arr'/]
    ListHasFirstElement -- other --> RaiseTypeError1[/raise TypeError/]
    IsList -- No --> IsNumpy{isinstance(data, np.ndarray)}
    IsNumpy -- Yes --> IsArrStr{isinstance(data[0][0], (str,bytes))}
    IsArrStr -- True --> ReturnArrStr[/return 'arr_str'/]
    IsArrStr -- False --> ReturnArrNum[/return 'arr_num'/]
    IsNumpy -- No --> IsDataFrame{isinstance(data, pd.DataFrame)}
    IsDataFrame -- True --> ReturnDF[/return 'df'/]
    IsDataFrame -- No --> IsString{isinstance(data, (str,bytes))}
    IsString -- True --> ReturnStr[/return 'str'/]
    IsString -- No --> IsGeo{isinstance(data, DataGeometry)}
    IsGeo -- True --> ReturnGeo[/return 'geo'/]
    IsGeo -- False --> RaiseTypeError2[/raise TypeError/]

## Examples:
    Example 1 — list of strings
    try:
        result = get_type(['a', 'b', 'c'])
        # result == 'list_str'
    except Exception as e:
        # handle unexpected error (e.g., empty list)
        raise

    Example 2 — numpy array numeric
    import numpy as np
    arr = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert get_type(arr) == 'arr_num'

    Example 3 — numpy array of strings
    arr_str = np.array([['a', 'b'], ['c','d']])
    assert get_type(arr_str) == 'arr_str'

    Example 4 — pandas DataFrame
    import pandas as pd
    df = pd.DataFrame({'x':[1,2,3]})
    assert get_type(df) == 'df'

    Example 5 — DataGeometry instance
    # from datageometry import DataGeometry
    # geo = DataGeometry(...)
    # assert get_type(geo) == 'geo'

    Example 6 — error cases
    # Empty list -> indexing at data[0] raises IndexError:
    try:
        get_type([])
    except IndexError:
        # caller must validate non-empty containers before calling if they want to avoid IndexError
        pass

    # Unsupported top-level type -> TypeError with exact message:
    try:
        get_type(set([1,2,3]))
    except TypeError as e:
        # e.args[0] contains the message shown in Raises above
        pass

## `hypertools._shared.helpers.convert_text` · *function*

## Summary:
Converts inputs that represent textual data into a 2D numpy column array; otherwise returns the input unchanged.

## Description:
This helper inspects the input's canonical type tag (via get_type) and, when the tag indicates plain text (a Python string) or a list of strings, converts the input into a numpy.ndarray shaped as a column vector (n_rows x 1). For all other recognized types the function performs no mutation and returns the original object.

Known callers within the codebase:
- Upstream data ingestion / normalization helpers and plotting pipelines that require textual inputs to be represented as 2D arrays prior to downstream processing (no direct callers were discovered in the scanned repository snapshot).
Typical pipeline stage:
- Called after initial type-detection and before routines that expect a 2-dimensional array-like textual feature column (for example, before building DataGeometry objects or plotting text-labeled points).

Why this is a separate function:
- Encapsulates the logic that uniformly converts string-like inputs to a consistent 2D numpy shape used elsewhere. It keeps the conversion rule (which tags should be converted and how) in one place so callers need not repeat indexing/reshape logic or import numpy themselves.

## Args:
    data (any): The input object to potentially convert.
        - Expected to be one of the types recognized by get_type (see get_type documentation for full list of recognized tags).
        - There is no explicit type annotation in the implementation; the function simply passes `data` to get_type and acts based on the returned tag.

Interdependencies:
    - The function relies on get_type(data) to produce one of the codebase's canonical type tags (e.g., 'list_str', 'str', 'arr_str', 'arr_num', 'df', 'geo', ...).
    - The conversion branch is taken only when get_type returns 'list_str' or 'str'.

## Returns:
    - If get_type(data) returns 'list_str' or 'str': a numpy.ndarray (2D) with shape (n, 1) where n is the number of textual elements after numpy conversion.
        * For a Python string input, numpy will produce an array with size 1 and reshape to (1, 1).
        * For a list of strings, numpy will produce an (n,) array which is reshaped to (n, 1).
    - Otherwise: returns the original `data` object unchanged (no conversion performed).

All possible return forms:
    - numpy.ndarray with ndim == 2 and shape[1] == 1 (when text conversion occurs)
    - The same object that was passed in (for non-text types such as DataFrame, numeric arrays, lists of arrays, DataGeometry, etc.)

## Raises:
    - Any exception raised by get_type(data) will propagate (commonly TypeError for unsupported types, IndexError for empty/indexing failures).
    - Exceptions from numpy when constructing or reshaping the array may propagate (for example, ValueError if reshaping fails in unusual circumstances). The function does not catch or wrap these exceptions.

Exact triggering conditions visible in code:
    - If get_type raises TypeError/IndexError due to unsupported or malformed input, convert_text will not catch it.
    - If dtype is 'list_str' or 'str', the code executes numpy.array(data).reshape(-1, 1) which may raise numpy exceptions if construction/reshape fails.

## Constraints:
Preconditions:
    - get_type must be available in the same runtime and must support the canonical tags used here.
    - If the input is a list or other container, get_type may assume the container is non-empty (see get_type constraints). If the container is empty, get_type may raise IndexError prior to convert_text running its conversion branch.
    - No modification to the input is required or performed before calling; the function only inspects and (in the text case) converts.

Postconditions:
    - If a conversion happened, the returned value is a numpy.ndarray shaped (n, 1) and the original input is not mutated by this function.
    - If no conversion happened, the returned value is the same object as the input (identity preserved).

## Side Effects:
    - None visible in the source code: the function performs no I/O, network access, global state mutation, or caching. It constructs and returns new objects only when converting.

## Control Flow:
flowchart TD
    Start --> CallGetType[get_type(data)]
    CallGetType --> IsText{dtype in ['list_str','str']}
    IsText -- Yes --> Convert[np.array(data) -> reshape(-1,1)]
    Convert --> ReturnArray[/return numpy.ndarray (n,1)/]
    IsText -- No --> ReturnOriginal[/return data unchanged/]

## Examples:
    Example 1 — converting a list of strings
    from numpy import ndarray
    data = ['label1', 'label2', 'label3']
    result = convert_text(data)
    # result is a numpy.ndarray with shape (3, 1)
    # result.dtype will be a string dtype

    Example 2 — converting a single string
    data = "single_label"
    result = convert_text(data)
    # result is a numpy.ndarray with shape (1, 1)

    Example 3 — passing a non-text input (unchanged)
    import pandas as pd
    df = pd.DataFrame({'x':[1,2]})
    result = convert_text(df)
    # result is the original df object (returned unchanged)

    Example 4 — caller-side defensive error handling
    try:
        # If input might be an empty list or otherwise malformed,
        # callers should validate or handle exceptions from get_type.
        converted = convert_text(maybe_empty_list)
    except IndexError:
        # handle empty-container case (get_type accesses data[0])
        handle_empty_input()
    except TypeError as e:
        # handle unsupported types
        raise

## `hypertools._shared.helpers.check_geo` · *function*

## Summary:
Return a shallow copy of a geometry/configuration-like object with any byte-strings in its top-level `reduce` attribute and `kwargs` mapping decoded to native Python strings; lists and numpy arrays in `kwargs` are converted to Python lists with their byte elements decoded.

## Description:
This helper centralizes normalization of a geometry/config object so downstream code can assume textual (str) types for common configuration fields.

Known callers within the provided context:
    - No explicit callers were provided with the task. The function is intended to be used immediately before code that consumes a geometry-like object (for example, prior to plotting or algorithm configuration) to ensure string types.

Why this logic is extracted:
    - Decoding bytes to strings is a small, well-defined normalization step that is useful at many call sites. Centralizing it avoids repeated byte-handling logic and makes it explicit where/when byte→string conversion occurs.

## Args:
    geo (object): An object that must expose the following attributes:
        - reduce: typically a str or bytes. If bytes, it will be decoded to str.
        - kwargs: a mapping-like attribute (for example, a dict) that supports .keys() and item access (geo.kwargs[key]).
    Notes:
        - The function does not require `geo` to be a specific class, only that the above attributes exist and behave like a mapping.
        - Values inside `kwargs` that are None are left unchanged.
        - Values that are list or numpy ndarray are handled element-wise (see Returns). Other types are left unchanged.

## Returns:
    object: A shallow copy of the input `geo` (produced by copy.copy(geo)) with these changes applied:
        - If the copied object's `reduce` is a bytes instance, it is decoded using the default bytes.decode() (UTF-8).
        - For each key in copied_object.kwargs:
            - If the value is None: left unchanged.
            - If the value is a list or a numpy ndarray: the function builds a new Python list by decoding any bytes elements (bytes -> str) and assigns that list back to copied_object.kwargs[key] (replacing the original value).
            - If the value is a bytes object: it is decoded to a str and assigned back to copied_object.kwargs[key].
            - Any other value types are left unchanged.
    Edge-case returns:
        - If no bytes are present at the handled locations, the returned object is a shallow copy identical in content to the original.
        - Numpy ndarrays are converted to Python lists when processed; they are not preserved as ndarray objects.

## Raises:
    - AttributeError:
        - If `geo` has no attribute `reduce` or no attribute `kwargs` (or if `geo.kwargs` lacks a .keys() method), attribute access will raise AttributeError.
    - UnicodeDecodeError:
        - When decoding bytes to strings, bytes.decode() uses the default encoding (UTF-8). If a bytes object cannot be decoded, bytes.decode() will raise UnicodeDecodeError.

## Constraints:
    Preconditions:
        - `geo` must provide a readable `reduce` attribute and a mapping-like `kwargs` with .keys() and index assignment semantics.
        - The function only inspects and decodes top-level values: `reduce` and values directly stored at `kwargs[key]`. It does not recursively traverse nested containers beyond these first-level values.
    Postconditions:
        - The returned object is a shallow copy of the input.
        - All bytes found in the returned object's `reduce` and in first-level `kwargs` values have been decoded to str or converted into lists of decoded strings as described.
        - Because the function performs a shallow copy and then assigns into the shared mapping object, the original object's `kwargs` mapping will reflect the assignments (see Side Effects).

## Side Effects:
    - Shared mapping mutation: The function uses a shallow copy (copy.copy). The underlying `kwargs` mapping object inside the copy is the same mapping object referenced by the original `geo` (shallow copy semantics). The function assigns new values into that mapping (e.g., copied.kwargs[key] = ...), so those assignments mutate the shared mapping object and therefore will be visible on the original `geo.kwargs` as well.
    - Replacement semantics for lists/arrays: For list or ndarray values found in `kwargs`, the function creates a new Python list (with decoded elements) and assigns that list into the mapping; it does not modify the original list element-by-element.
    - No I/O, network access, stdout/stderr writes, global state, or external service calls occur within this function.

## Control Flow:
flowchart TD
    Start --> CopyGeo[geo_copy = copy.copy(geo)]
    CopyGeo --> CheckReduce{is geo_copy.reduce instance of bytes?}
    CheckReduce -- yes --> DecodeReduce[geo_copy.reduce = geo_copy.reduce.decode()]
    CheckReduce -- no --> SkipReduce[no-op]
    DecodeReduce --> IterateKeys
    SkipReduce --> IterateKeys
    IterateKeys[for each key in geo_copy.kwargs.keys()] --> GetVal[val = geo_copy.kwargs[key]]
    GetVal --> IsNone{val is None?}
    IsNone -- yes --> NextKey
    IsNone -- no --> IsListOrArray{val is list or numpy ndarray?}
    IsListOrArray -- yes --> BuildList[build new list = [decode bytes elements]]
    BuildList --> AssignNewList[geo_copy.kwargs[key] = new list]
    IsListOrArray -- no --> IsBytes{val is bytes?}
    IsBytes -- yes --> DecodeVal[geo_copy.kwargs[key] = val.decode()]
    IsBytes -- no --> LeaveVal[leave unchanged]
    DecodeVal --> NextKey
    AssignNewList --> NextKey
    LeaveVal --> NextKey
    NextKey --> IterateKeys
    IterateKeys --> Return[return geo_copy]
    Return --> End

## Examples:
- Basic example:
    Given:
        geo.reduce = b'mean'
        geo.kwargs = {'labels': [b'A', b'B'], 'method': b'max', 'other': None}
    After:
        result = check_geo(geo)
        result.reduce == 'mean'
        result.kwargs['labels'] == ['A', 'B']            # list of str
        result.kwargs['method'] == 'max'                # str
        result.kwargs['other'] is None
    Note: Because the kwargs mapping is shared between the original and the shallow copy, the assignments above (replacing values under those keys) will also be visible in geo.kwargs on the original object.

- Error handling example:
    If a bytes object cannot be decoded with the default UTF-8 codec, calling this function will raise UnicodeDecodeError. Callers that accept untrusted or unknown-encoded bytes should handle UnicodeDecodeError around this call, for example:
        try:
            safe_geo = check_geo(geo)
        except UnicodeDecodeError:
            # handle or re-encode problematic bytes before retrying
            pass

## `hypertools._shared.helpers.get_dtype` · *function*

## Summary:
Determines the canonical, short textual code for the input data's type so callers can branch on a small set of supported data categories.

## Description:
This helper inspects a single Python object and returns one of a small set of string codes that represent how the rest of the codebase should treat that object (list, NumPy array, pandas DataFrame, string/bytes, or DataGeometry). It centralizes the type-discrimination logic so caller code can be simpler and consistent.

Known callers in the repository (from provided context):
- No explicit callers were provided in the supplied source fragments. Typical callers are functions that accept user data of unknown shape/format and need to normalize or route processing (for example, high-level plotting, embedding, or data-normalization helpers). These callers call this function at the start of their pipeline to decide how to convert or iterate over the input.

Why this is a separate function:
- The decision tree for supported input types is a common operation across many data-processing routines. Extracting it prevents duplicated isinstance checks, ensures consistent ordering/precedence of type checks, and centralizes the exact return codes used by downstream logic.

## Args:
    data (any): The object whose type will be classified. There is no mutation of this object.

Notes about names and imports:
- The implementation expects that the names `np` and `pd` refer to the NumPy and pandas modules respectively (i.e., the module file that uses this function should import numpy as np and pandas as pd or otherwise provide those bindings).
- The function also depends on the DataGeometry class being importable from the package's datageometry module (the implementation performs a runtime import from a relative module).

## Returns:
    str: One of the following exact string codes indicating the detected input category:
        - 'list' : if data is an instance of Python list
        - 'arr'  : if data is an instance of numpy.ndarray
        - 'df'   : if data is an instance of pandas.DataFrame
        - 'str'  : if data is an instance of str or bytes
        - 'geo'  : if data is an instance of DataGeometry

Edge-case return behavior:
- Lists of any element types (strings, numbers, objects) are classified as 'list' (the function does not inspect list element types).
- bytes objects are classified together with str as 'str'.
- Subclasses of the tested types match according to Python's isinstance semantics (for example, a subclass of numpy.ndarray will be classified as 'arr').

## Raises:
    TypeError: Raised when the object does not match any of the supported categories. The exact message raised by the code is:
        'Unsupported data type passed. Supported types: Numpy Array, Pandas DataFrame, String, List of strings, List of numbers'
    (Callers should catch TypeError if they intend to accept or provide conversion for other types.)

## Constraints:
Preconditions:
- The name `np` must be bound to the NumPy module and `pd` to pandas in the executing module namespace, or the implementation must import/alias them prior to calling this function.
- The datageometry.DataGeometry class must be importable relative to this helper's module (the function performs a relative import).

Postconditions:
- The function returns a string code from the enumerated set {'list', 'arr', 'df', 'str', 'geo'} on success and does not mutate the input object.
- If it returns, the return value can be used as a stable key for branching logic elsewhere in the codebase.

## Side Effects:
- None: the function performs only type checks and a local import; it does not perform I/O, mutate globals, or call external services.
- Note: the function performs a runtime import of DataGeometry from a relative module. This import may trigger module import-time initialization of that module as a side effect, but the helper itself does not perform further actions.

## Control Flow:
flowchart TD
    A[Start: receive data] --> B{isinstance(data, list)}
    B -- yes --> R_LIST['return "list"']
    B -- no --> C{isinstance(data, np.ndarray)}
    C -- yes --> R_ARR['return "arr"']
    C -- no --> D{isinstance(data, pd.DataFrame)}
    D -- yes --> R_DF['return "df"']
    D -- no --> E{isinstance(data, (str, bytes))}
    E -- yes --> R_STR['return "str"']
    E -- no --> F{isinstance(data, DataGeometry)}
    F -- yes --> R_GEO['return "geo"']
    F -- no --> R_ERR['raise TypeError: Unsupported data type passed...']

## Examples:
Example 1 — NumPy array
- Context: A caller wants to know whether to treat input as a dense numeric array.
- Usage (pseudocode):
    - Given data = numpy.array([[1,2],[3,4]])
    - get_dtype(data) -> 'arr'

Example 2 — pandas DataFrame
- Given data = pandas.DataFrame({'x':[1,2]})
- get_dtype(data) -> 'df'

Example 3 — list input
- Given data = ['a','b','c'] or data = [1,2,3]
- get_dtype(data) -> 'list'

Example 4 — DataGeometry instance
- Given data = DataGeometry(...)  (an instance of the package's DataGeometry class)
- get_dtype(data) -> 'geo'

Example 5 — Unsupported type handling
- Given data = ('tuple',)  (a tuple)
- Caller code:
    try:
        kind = get_dtype(data)
    except TypeError as exc:
        # handle or convert input to a supported type
        raise

Notes on reimplementation:
- Implement the checks in the given order to preserve precedence (list first, then numpy.ndarray, then DataFrame, then str/bytes, then DataGeometry). The order matters when an object could satisfy multiple checks.
- Use Python's isinstance semantics for type checking.

