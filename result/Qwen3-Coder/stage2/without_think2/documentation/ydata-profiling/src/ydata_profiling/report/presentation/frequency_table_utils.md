# `frequency_table_utils.py`

## `src.ydata_profiling.report.presentation.frequency_table_utils._frequency_table` · *function*

## Summary:
Transforms a frequency table series into a formatted list of dictionaries suitable for display in UI components, handling special cases like "Other values" and "Missing" entries.

## Description:
This utility function processes a pandas Series containing frequency counts and converts it into a structured list of dictionaries that can be rendered in user interfaces. It handles truncation of results based on maximum display limits, aggregates remaining values into "Other values" categories, and accounts for missing data. The function is designed to normalize frequencies for proportional display while preserving statistical accuracy.

## Args:
    freqtable (pd.Series): A pandas Series containing frequency counts for various categories, indexed by labels.
    n (int): Total count of observations in the dataset.
    max_number_to_print (int): Maximum number of top-frequency categories to display before aggregating others.

## Returns:
    List[Dict[str, Any]]: A list of dictionaries representing rows for display, each containing:
        - label (str): Category label or special indicator ("Other values", "(Missing)")
        - width (float): Normalized width for proportional display (frequency / max_frequency)
        - count (int): Raw frequency count
        - percentage (float): Percentage of total observations (0.0 to 1.0)
        - n (int): Total observation count (same as input)
        - extra_class (str): CSS class identifier for styling ("other", "missing", or empty string)

## Raises:
    None explicitly raised, but may raise pandas/numpy exceptions if inputs are malformed.

## Constraints:
    Preconditions:
        - freqtable should be a valid pandas Series
        - n should be a non-negative integer
        - max_number_to_print should be a non-negative integer
    Postconditions:
        - Returns an empty list if no meaningful data exists (all zero frequencies)
        - All returned dictionaries have consistent keys and types
        - Percentage values are capped at 1.0 for overflow protection

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _frequency_table] --> B{max_number_to_print > n?}
    B -- Yes --> C[max_number_to_print = n]
    B -- No --> C
    C --> D{max_number_to_print < len(freqtable)?}
    D -- Yes --> E[freq_other = sum(freqtable[max_number_to_print:])]
    D -- No --> F[freq_other = 0]
    E --> G[min_freq = freqtable.values[max_number_to_print]]
    F --> G
    G --> H[freq_missing = n - sum(freqtable)]
    H --> I{len(freqtable) == 0?}
    I -- Yes --> J[Return []]
    I -- No --> K[max_freq = max(freqtable[0], freq_other, freq_missing)]
    K --> L{max_freq == 0?}
    L -- Yes --> M[Return []]
    L -- No --> N[Initialize rows list]
    N --> O[Process top categories]
    O --> P{freq_other > min_freq?}
    P -- Yes --> Q[Add "Other values" row]
    P -- No --> R[Skip "Other values"]
    Q --> S[Add "Missing" row if needed]
    R --> S
    S --> T[Return rows]
```

## Examples:
    # Basic usage with normal data
    freq_series = pd.Series([10, 5, 3, 2], index=['A', 'B', 'C', 'D'])
    result = _frequency_table(freq_series, 20, 3)
    # Returns list of 3 dictionaries for top 3 categories
    
    # Usage with missing data
    freq_series = pd.Series([10, 5], index=['A', 'B'])
    result = _frequency_table(freq_series, 20, 5)
    # Returns list with "Missing" entry if missing count > min_freq
    
    # Edge case: empty frequency table
    freq_series = pd.Series([], dtype='int64')
    result = _frequency_table(freq_series, 10, 5)
    # Returns empty list []
    
    # Edge case: all zero frequencies
    freq_series = pd.Series([0, 0, 0], index=['A', 'B', 'C'])
    result = _frequency_table(freq_series, 10, 3)
    # Returns empty list [] due to max_freq == 0

## `src.ydata_profiling.report.presentation.frequency_table_utils.freq_table` · *function*

## Summary:
Generates formatted frequency table data for UI presentation, handling both single and multiple frequency distributions with appropriate aggregation and truncation.

## Description:
This function serves as a wrapper around the internal `_frequency_table` utility to process frequency distribution data for display in user interfaces. It supports both single frequency series and lists of frequency series, automatically routing to the appropriate processing logic. The function ensures proper formatting and aggregation of frequency data while maintaining compatibility with UI rendering requirements.

## Args:
    freqtable (Union[pd.Series, List[pd.Series]]): Either a single pandas Series containing frequency counts or a list of such Series objects.
    n (Union[int, List[int]]): Total count of observations in the dataset, either a single integer or a list matching the length of freqtable.
    max_number_to_print (int): Maximum number of top-frequency categories to display before aggregating remaining values into "Other values".

## Returns:
    Union[List[Dict[str, Any]], List[List[Dict[str, Any]]]]: When freqtable is a single Series, returns a list of dictionaries representing frequency rows. When freqtable is a list, returns a list of such lists, one for each frequency series processed.

## Raises:
    None explicitly raised, but may propagate exceptions from internal `_frequency_table` function or pandas operations.

## Constraints:
    Preconditions:
        - freqtable must be either a pandas Series or a list of pandas Series
        - n must be either an integer or a list of integers with matching length to freqtable
        - max_number_to_print must be a non-negative integer
    Postconditions:
        - Returns properly formatted data structures compatible with UI rendering
        - Handles edge cases gracefully (empty inputs, zero frequencies)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start freq_table] --> B{isinstance(freqtable, list) AND isinstance(n, list)?}
    B -- Yes --> C[Process multiple frequency tables]
    B -- No --> D[Process single frequency table]
    C --> E[Zip freqtable and n, apply _frequency_table to each pair]
    D --> F[Apply _frequency_table to single inputs]
    E --> G[Return list of lists]
    F --> G
```

## Examples:
    # Single frequency table usage
    freq_series = pd.Series([10, 5, 3, 2], index=['A', 'B', 'C', 'D'])
    result = freq_table(freq_series, 20, 3)
    # Returns list of dictionaries for top 3 categories with aggregated "Other values"
    
    # Multiple frequency tables usage
    freq_series1 = pd.Series([10, 5], index=['A', 'B'])
    freq_series2 = pd.Series([8, 4, 2], index=['X', 'Y', 'Z'])
    result = freq_table([freq_series1, freq_series2], [15, 14], 2)
    # Returns list of two lists, each containing formatted frequency data

## `src.ydata_profiling.report.presentation.frequency_table_utils._extreme_obs_table` · *function*

## Summary:
Creates a formatted table of extreme observations from a frequency table for display in reports.

## Description:
Generates a list of dictionaries representing the most frequent observations from a frequency table, with normalized widths and percentage calculations for visualization purposes. This function extracts the top N observations and formats them with additional metadata for rendering in report presentations.

## Args:
    freqtable (pd.Series): A pandas Series containing frequency counts for observations, indexed by labels.
    number_to_print (int): The number of top observations to include in the result.
    n (int): Total count of observations used to calculate percentages.

## Returns:
    List[Dict[str, Any]]: A list of dictionaries, each representing a row in the extreme observations table with keys:
        - "label": The observation label
        - "width": Normalized width for visualization (frequency/max_frequency)
        - "count": Raw frequency count
        - "percentage": Percentage of total observations (frequency/n)
        - "extra_class": Empty string placeholder for CSS classes
        - "n": Total observation count used for percentage calculation

## Raises:
    None explicitly raised, but may raise pandas-related exceptions if freqtable is invalid.

## Constraints:
    Preconditions:
        - freqtable must be a valid pandas Series
        - number_to_print must be a non-negative integer
        - n must be a positive integer
    Postconditions:
        - Returns exactly number_to_print rows (or fewer if freqtable has fewer elements)
        - All returned dictionaries contain the same set of keys
        - Width values are between 0 and 1

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _extreme_obs_table] --> B{freqtable.iloc[:number_to_print]}
    B --> C[obs_to_print = top observations]
    C --> D[max_freq = max frequency in obs_to_print]
    D --> E{max_freq != 0}
    E -->|True| F[width = freq / max_freq]
    E -->|False| G[width = 0]
    F --> H[Create row dictionary]
    G --> H
    H --> I[Add row to rows list]
    I --> J[Return rows list]
```

## Examples:
```python
# Basic usage
freqtable = pd.Series([10, 5, 3, 2], index=['A', 'B', 'C', 'D'])
result = _extreme_obs_table(freqtable, 3, 20)
# Returns list of 3 dictionaries with labels A, B, C
# Widths normalized to max frequency of 10
# Percentages calculated as 10/20, 5/20, 3/20

# Edge case with zero max frequency
freqtable = pd.Series([0, 0, 0], index=['A', 'B', 'C'])
result = _extreme_obs_table(freqtable, 2, 10)
# Returns list of 2 dictionaries with width = 0 for all entries
```

## `src.ydata_profiling.report.presentation.frequency_table_utils.extreme_obs_table` · *function*

## Summary:
Generates a formatted table of extreme observations from frequency data for report presentation.

## Description:
Creates a nested list structure of dictionaries representing the most frequent observations from frequency tables, suitable for display in profiling report visualizations. This function handles both single and multiple frequency table inputs by delegating to the internal `_extreme_obs_table` function.

## Args:
    freqtable (Union[pd.Series, List[pd.Series]]): Either a single pandas Series containing frequency counts indexed by labels, or a list of such Series for multiple tables.
    number_to_print (int): The number of top observations to include in each result table.
    n (Union[int, List[int]]): Total count of observations used to calculate percentages, either a single integer or a list matching the length of freqtable.

## Returns:
    List[List[Dict[str, Any]]]: A list of lists of dictionaries, where each inner list corresponds to one frequency table and contains dictionaries representing extreme observations with standardized keys.

## Raises:
    None explicitly raised by this function, though underlying operations may raise pandas or standard Python exceptions.

## Constraints:
    Preconditions:
        - freqtable must be a valid pandas Series or list of Series
        - number_to_print must be a non-negative integer
        - n must be a positive integer or list of positive integers
    Postconditions:
        - Returns a list with same length as input freqtable when it's a list
        - Each returned dictionary contains the same set of keys
        - When freqtable is a single Series, returns a list containing one list of dictionaries

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start extreme_obs_table] --> B{isinstance(freqtable, list) AND isinstance(n, list)}
    B -->|True| C[Zip freqtable and n, apply _extreme_obs_table to each pair]
    B -->|False| D[Apply _extreme_obs_table to freqtable, n directly]
    C --> E[Return list of results]
    D --> E
```

## Examples:
```python
# Single frequency table usage
freqtable = pd.Series([10, 5, 3, 2], index=['A', 'B', 'C', 'D'])
result = extreme_obs_table(freqtable, 3, 20)
# Returns [[{'label': 'A', 'width': 1.0, 'count': 10, 'percentage': 0.5, ...}, ...]]

# Multiple frequency tables usage
freqtables = [pd.Series([10, 5]), pd.Series([3, 2])]
ns = [15, 5]
result = extreme_obs_table(freqtables, 2, ns)
# Returns [[...], [...]] - one list per frequency table
```

