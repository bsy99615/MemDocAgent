# `imbalance_pandas.py`

## `src.ydata_profiling.model.pandas.imbalance_pandas.column_imbalance_score` · *function*

## Summary:
Computes an imbalance score for a categorical column by converting class counts to an entropy-based normalized measure in the range [0, 1], where 0 indicates maximum entropy (perfectly balanced) and values closer to 1 indicate stronger imbalance.

## Description:
This function accepts observed counts per class for a single column and the number of distinct classes expected, and returns a normalized imbalance score derived from Shannon entropy (base 2).

Known callers within the codebase and typical context:
- Used by routines that evaluate per-column categorical imbalance as part of a profiling / feature-quality pipeline. Typical callers compute class counts for a column (value counts) and then call this function to summarize how imbalanced that column is relative to the number of classes.
- No specific call-sites were provided in the supplied context; expect calls from higher-level profiling functions that iterate over columns and compute summary statistics.

Why this logic is extracted into its own function:
- Encapsulates the exact entropy-based formula and normalization rule in one place so that all imbalance scoring is consistent across the codebase.
- Keeps caller code focused on data collection (value counts and class enumeration) and delegates mathematical normalization and edge-case handling (n_classes <= 1) to this dedicated function.

## Args:
    value_counts (pd.Series):
        A pandas Series representing counts per class for the column. Expected to contain non-negative numeric counts (integers or floats). The function converts this Series to a numpy float array before computing entropy.
    n_classes (int):
        The number of possible classes for the column (must be an integer). Typical values are >= 1. This value is used to normalize the entropy by the maximum entropy log2(n_classes).

## Returns:
    Union[float, int]:
        - If n_classes > 1: returns a float in the range [0.0, 1.0], computed as
            1 - (entropy(value_counts_array, base=2) / log2(n_classes))
          where entropy(...) is the Shannon entropy (base 2) of the provided counts interpreted as a distribution.
          Interpretation:
            * 0.0: maximum entropy (uniform distribution across classes, i.e., perfectly balanced)
            * 1.0: minimum entropy (all mass concentrated in a single class, i.e., maximally imbalanced)
            * Values between 0 and 1: intermediate imbalance levels.
        - If n_classes <= 1: returns the integer 0 (no meaningful imbalance when there is 0 or 1 class).

## Raises:
    This function does not explicitly raise exceptions. However, underlying operations may raise runtime errors:
    - AttributeError: if value_counts does not provide to_numpy (unlikely for a valid pandas Series).
    - TypeError/ValueError: if value_counts contains types that cannot be converted to floats or if scipy.stats.entropy is passed invalid input (e.g., NaN/inf in the array).
    The caller should ensure value_counts is a pandas Series of non-negative numeric counts and that n_classes is an integer.

## Constraints:
    Preconditions:
        - value_counts should be a pandas Series of non-negative numeric counts (integers or floats). Negative counts are semantically invalid and may produce incorrect or undefined behavior in entropy computation.
        - n_classes must be an integer representing the number of possible classes. For meaningful normalized scores, n_classes should be >= 2.
    Postconditions:
        - If n_classes > 1, the return value is a float in [0.0, 1.0].
        - If n_classes <= 1, the return value is 0.

## Side Effects:
    - This function has no I/O (no file, network, or stdout operations).
    - It does not mutate external state, global variables, or the input Series.
    - It calls into scipy.stats.entropy and numpy (via to_numpy) but does not interact with external services.

## Control Flow:
flowchart TD
    Start --> Check_n_classes
    Check_n_classes{n_classes > 1?}
    Check_n_classes -- Yes --> Convert[value_counts.to_numpy(dtype=float)]
    Convert --> ComputeEntropy[entropy(value_counts_array, base=2)]
    ComputeEntropy --> Normalize[divide by log2(n_classes)]
    Normalize --> Score[1 - normalized_entropy]
    Score --> ReturnFloat
    Check_n_classes -- No --> ReturnZero
    ReturnFloat --> End
    ReturnZero --> End

## Examples:
- Numeric example (illustrative, not code):
    * Suppose a column has two classes with counts [50, 50] and n_classes = 2.
      entropy([50, 50], base=2) = 1.0; log2(2) = 1.0 -> normalized_entropy = 1.0 -> score = 1 - 1 = 0.0 (balanced).
    * Suppose a column has two classes with counts [100, 0] and n_classes = 2.
      entropy([100, 0], base=2) = 0.0; log2(2) = 1.0 -> normalized_entropy = 0.0 -> score = 1 - 0 = 1.0 (maximally imbalanced).
    * For n_classes = 1 (or 0), the function returns 0 indicating no meaningful imbalance score.

- Usage guidance:
    * Prior to calling, compute value_counts for a column as counts per class (e.g., pandas.Series of class counts). Pass that Series and the total number of possible classes.
    * Validate inputs where appropriate (e.g., ensure no NaNs in counts, ensure n_classes >= 1) to avoid runtime errors from underlying numeric conversions or entropy calculation.

