# `utils_pandas.py`

## `src.ydata_profiling.model.pandas.utils_pandas.weighted_median` · *function*

## Summary:
Compute a weighted median-like statistic from two one-dimensional arrays; returns a numeric scalar. Note: this implementation sorts data and weights independently (it does not preserve the original data↔weight pairing), which yields non-standard but deterministic behavior.

## Description:
This helper computes a median value influenced by weights using the following steps:
1. Coerce inputs to numpy arrays if they aren't already.
2. Sort the data array and the weights array independently (each sorted ascending).
3. Compute the midpoint as half the total sum of the sorted weights.
4. If the single largest sorted weight exceeds the midpoint, return the data element(s) corresponding to the maximum weight from the original (unsorted) arrays.
5. Otherwise, compute the cumulative sum of the sorted weights, find the last index whose cumulative sum is <= midpoint, and:
   - If the cumulative sum at that index equals the midpoint exactly, return the arithmetic mean of the two adjacent sorted data values (s_data[idx] and s_data[idx+1]).
   - Otherwise return the next sorted data value (s_data[idx+1]).

Important implementation note (behavioral caveat):
    - The function sorts data and weights independently (s_data = sorted(data), s_weights = sorted(weights)). It does NOT reorder weights to follow the sort order of data, nor does it reorder data according to weight order. This severs the original elementwise pairing and produces results that do not conform to the standard definition of weighted median (where data are sorted and weights are permuted together). Callers expecting a conventional weighted median must either ensure the inputs are provided in a paired, appropriate form or use a different implementation.

Known callers within the codebase:
    - None found in the provided snapshot. Typical use cases in data-profiling: summarizing a distribution when observations carry differing importance. Because of the non-standard sort behavior, verify intended semantics before use.

Why this logic is extracted:
    - The computation involves several distinct steps and edge cases (dominant single weight, exact midpoint between two items, input coercion). Centralizing this behavior ensures consistent results and allows callers to rely on a single implementation.

## Args:
    data (np.ndarray or array-like):
        1-D sequence of numeric observations. The function will call np.array(data) when the input is not already an np.ndarray.
        Expected shape: (n,). The code does not explicitly validate dimensionality.
    weights (np.ndarray or array-like):
        1-D sequence of numeric weights (same length n as data). The function will call np.array(weights) when the input is not already an np.ndarray.
        Expected shape: (n,). The code does not validate non-negativity or types.

    Interdependencies and caller obligations:
        - For well-defined, conventional semantics: provide weights that correspond elementwise to data and are non-negative. However, because the implementation sorts the arrays independently, conventional pairing will not be respected unless the caller pre-sorts or otherwise prepares inputs to produce the intended outcome.
        - The function assumes both arrays are non-empty and (practically) of equal length; mismatches are not checked and may produce runtime errors.

## Returns:
    numeric scalar (numpy scalar or Python numeric; int or float):
        - When a single data value is selected: returns that element (numpy or Python numeric type).
        - When an exact midpoint occurs between two adjacent sorted data values: returns their arithmetic mean as a float (numpy float or Python float).
        - Although the function annotation is "-> int", the actual return value can be float and/or numpy scalar types depending on inputs—do not rely on an integer return type.

## Raises:
    The function does not explicitly raise custom exceptions but will raise numpy/Python exceptions under several conditions:
    - IndexError:
        * If either input is empty, accessing s_weights[-1] or using [0] on an empty mask will raise IndexError.
        * Computing idx = np.where(cs_weights <= midpoint)[0][-1] will raise IndexError if the selection np.where(...)[0] is empty (this can occur only if arrays are empty or if previous logic is bypassed).
    - ValueError / TypeError:
        * If inputs cannot be coerced into numeric numpy arrays (e.g., irregular nested objects), numpy may raise TypeError or ValueError during np.array or numeric operations.
    - Logical pitfalls (not explicit exceptions):
        * Negative weights or a mix of positive and negative weights yield non-standard midpoint and cumulative behavior; the code does not prevent or correct for this.

## Constraints:
    Preconditions:
        - Prefer non-empty, 1-D numeric array-like inputs.
        - Prefer equal-length data and weights (weights[i] corresponds to data[i]) if the caller intends conventional weighted-median semantics — but see the independent-sorting caveat above.
        - Prefer non-negative weights for intuitive midpoint semantics.
    Postconditions:
        - Returns a numeric scalar representing the function's computed weighted-median-like value.
        - No mutation of caller-provided arrays (inputs are re-bound locally), and no external state is modified.

## Side Effects:
    - None. No file, network, stdout, or global state side-effects. The function operates purely on local data and returns a scalar.

## Control Flow:
flowchart TD
    Start --> CoerceInputs
    CoerceInputs --> SortDataAndWeights
    SortDataAndWeights --> ComputeMidpoint
    ComputeMidpoint --> CheckLargestWeight
    CheckLargestWeight{is s_weights[-1] > midpoint?}
    CheckLargestWeight -- Yes --> SelectDataForMaxWeight
    SelectDataForMaxWeight --> ReturnValue
    CheckLargestWeight -- No --> CumSumWeights
    CumSumWeights --> FindLastIndex{idx = last i where cs_weights[i] <= midpoint}
    FindLastIndex --> CheckExactMidpoint{is cs_weights[idx] == midpoint?}
    CheckExactMidpoint -- Yes --> Return mean(s_data[idx], s_data[idx+1])
    CheckExactMidpoint -- No --> Return s_data[idx+1]
    ReturnValue --> End

## Examples:
Example 1 — balanced uniform weights
    data = [1, 2, 3]
    weights = [1, 1, 1]
    result -> 2 or 2.0 (middle element); here independent sorting produces the conventional median.

Example 2 — dominant weight (uses original pairing for max-weight selection)
    data = [10, 20, 30]
    weights = [0.1, 5.0, 0.1]
    - s_weights sorted -> [0.1, 0.1, 5.0], midpoint = 0.5*(0.1+0.1+5.0)=2.6
    - s_weights[-1] (5.0) > midpoint -> branch selects data[weights == np.max(weights)][0]
    - np.max(weights) is 5.0 and weights == 5.0 yields mask [False, True, False] -> data[...] = [20] -> returns 20

Example 3 — independent sorting leads to non-standard pairing
    data = [100, 1, 2]
    weights = [1, 2, 100]
    - s_data sorted -> [1, 2, 100]
    - s_weights sorted -> [1, 2, 100], midpoint = 51.5
    - s_weights[-1] = 100 > midpoint -> selects data[weights == 100][0] -> original data element paired with max weight is 2 -> returns 2
    Note how sorting independently results in choosing a data element based on the original weight positions, not the sorted data order.

Example 4 — exact midpoint between two sorted values
    data = [1, 2, 3, 4]
    weights = [1, 1, 1, 1]
    - s_data = [1,2,3,4], s_weights = [1,1,1,1], midpoint = 2.0
    - cs_weights = [1,2,3,4], last index where cs_weights <= midpoint is idx=1 and cs_weights[1] == midpoint -> return mean(s_data[1:3]) = mean(2,3) = 2.5

Example 5 — caller-side validation to avoid runtime errors
    if len(data)==0 or len(weights)==0:
        raise ValueError("data and weights must be non-empty and of equal length")
    if len(data) != len(weights):
        raise ValueError("data and weights must be the same length")
    # then call weighted_median(data, weights)

