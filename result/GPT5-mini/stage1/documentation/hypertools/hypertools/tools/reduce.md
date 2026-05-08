# `reduce.py`

## `hypertools.tools.reduce.reduce` · *function*

*No documentation generated.*

## `hypertools.tools.reduce.reduce_list` · *function*

## Summary:
Applies a fitted-or-fit-transform-style dimensionality-reduction model to a list of 2D arrays and returns the reduced data split back into the original list segments.

## Description:
This helper centralizes the logic for running a single model.fit_transform over multiple input arrays concatenated along the sample (row) axis, then splitting the transformed result back into the original grouping sizes.

Known callers:
- No direct callers were found within the provided code snapshot. Typical callers are higher-level tools that need to reduce multiple related datasets (for example, one array per subject or experimental condition) using a single shared model so that the reduced representations are comparable.

Why this logic is factored out:
- Ensures a single model call across all data for consistent projection (important for models that learn global components).
- Encapsulates the bookkeeping of concatenating inputs, computing split indices, and splitting the reduced output back into per-input arrays. Keeping this separate avoids repeating that pattern and reduces the risk of inconsistent splitting.

## Args:
    x (Sequence[array-like, shape=(n_i, d)]):
        A non-empty sequence (e.g., list or tuple) of 2D array-like objects. Each element xi must be convertible to a numpy 2D array and represents n_i samples with d features. All xi must have the same number of columns (d) so that vertical stacking is valid.
    model (object with fit_transform method):
        Any object providing a method fit_transform(X) that accepts a 2D array of shape (sum_i n_i, d) and returns a 2D array of shape (sum_i n_i, k) (k may be equal to d or a different number of components). The function does not call model.fit separately; it calls model.fit_transform once on the vertically stacked data.

Interdependencies:
- The xi objects must be compatible with numpy.vstack; i.e., they must have the same number of columns (d). The model.fit_transform is expected to return an output with the same number of rows as its input (sum_i n_i). If the model changes the number of rows, splitting will likely fail.

## Returns:
    list[numpy.ndarray]:
        A list of 2D numpy arrays corresponding to the reduced representations of each input xi in x. The returned list length equals len(x). Each returned array has shape (n_i, k), where n_i is the number of rows in the corresponding input xi, and k is the number of output dimensions produced by model.fit_transform.

    Notes on edge-case returns:
    - For a single-element input list (len(x) == 1), the function still returns a list containing one 2D array (the reduced version of the single input).
    - The values and dtypes are whatever numpy receives from model.fit_transform; no dtype casting is performed by this function.

## Raises:
    ValueError:
        - If x is empty, numpy.vstack(x) will raise a ValueError (or equivalent) because there is nothing to stack.
        - If elements of x have incompatible shapes (different number of columns), numpy.vstack will raise a ValueError.
        - If model.fit_transform returns an array whose number of rows does not match sum(len(xi) for xi in x), the subsequent numpy.vsplit call will raise a ValueError for invalid split indices.
    AttributeError:
        - If the provided model does not implement fit_transform, an AttributeError (or similar) will propagate when attempting to call model.fit_transform.
    Any exception raised by model.fit_transform (e.g., due to invalid data types or model-specific constraints) will propagate up unchanged.

## Constraints:
Preconditions:
    - x must be a non-empty sequence of 2D array-like objects.
    - Every xi in x must have the same number of columns (feature dimension d).
    - model must implement fit_transform and must accept the stacked input shape (sum_i n_i, d).

Postconditions:
    - The returned list has length len(x).
    - The concatenation (vertical stack) of returned arrays equals model.fit_transform of the concatenation of inputs (within numerical precision and as produced by the model).
    - Row counts are preserved: each returned array has the same number of rows as the corresponding input xi.

## Side Effects:
    - No I/O is performed.
    - No mutation of global state occurs within this function.
    - The only external interaction is the call to model.fit_transform; any side effects there (e.g., training state on the model object) are performed by the model itself and not by this function.

## Control Flow:
flowchart TD
    Start[Start]
    Start --> ComputeSplit[Compute split indices: cumsum of lengths]
    ComputeSplit --> Stack[vstack all inputs -> X (sum_n x d)]
    Stack --> FitTransform[Call model.fit_transform(X) -> X_reduced]
    FitTransform --> VSplit[vsplit X_reduced using split indices -> list chunks]
    VSplit --> CheckLen{len(x) > 1 ?}
    CheckLen -- Yes --> ReturnList[List(x_r) returned]
    CheckLen -- No --> ReturnSingle[List([x_r[0]]) returned]
    ReturnList --> End[End]
    ReturnSingle --> End

## Examples (prose, realistic usage and error handling):
1) Typical happy-path usage:
    - Prepare three datasets: A with shape (50, 100), B with shape (40, 100), and C with shape (60, 100) (so d = 100).
    - Instantiate a dimensionality-reduction model that provides fit_transform (for example, a PCA-like object configured to return k=10 components).
    - Call this function with x = [A, B, C] and model. The function will:
        * Stack A, B, C into an array of shape (150, 100),
        * Call model.fit_transform on the stacked array, receiving an array of shape (150, 10),
        * Split that result back into three arrays with shapes (50, 10), (40, 10), and (60, 10),
        * Return [A_reduced, B_reduced, C_reduced].

2) Single-input usage:
    - When x contains exactly one array (e.g., x = [A] where A has shape (100, 50)), the function will return a list containing a single reduced array with shape (100, k).

3) Error handling scenarios:
    - If x is empty, a caller should expect a ValueError from the stacking operation. Example handling strategy: check that x is non-empty before calling, or catch ValueError and raise a clearer application-level error.
    - If the inputs have mismatched feature dimensions (different numbers of columns), numpy.vstack will raise a ValueError. Validate input shapes ahead of calling if this is a possibility.
    - If model.fit_transform fails (for example, due to invalid data types or algorithm-specific constraints), its exception will propagate; callers can catch exceptions from the model call to handle training failures.

## Implementation notes (to reimplement correctly):
    - Compute split indices as the cumulative sum of the number of rows in each xi, excluding the final accumulated total (i.e., np.cumsum([len(xi) for xi in x])[:-1]).
    - Vertically stack the inputs to produce a single 2D array with shape (sum_i n_i, d).
    - Call model.fit_transform once on the stacked array. Verify (implicitly by relying on numpy.vsplit) that the returned array has the same number of rows.
    - Split the transformed array into segments using numpy.vsplit with the previously computed split indices.
    - Return a normal Python list of numpy arrays; for len(x) == 1 ensure the returned value is a list containing the single numpy array (not a nested list or scalar).

