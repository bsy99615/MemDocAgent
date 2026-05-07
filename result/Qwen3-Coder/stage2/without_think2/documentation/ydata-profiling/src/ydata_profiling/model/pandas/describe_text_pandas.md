# `describe_text_pandas.py`

## `src.ydata_profiling.model.pandas.describe_text_pandas.pandas_describe_text_1d` · *function*

## Summary:
Processes and summarizes text data from a pandas Series, computing various descriptive statistics including length, character, and word distributions based on configuration settings.

## Description:
This function serves as the primary entry point for analyzing textual data within a pandas Series. It performs type conversion, extracts first rows for display, and conditionally computes detailed statistics based on enabled configuration flags. The function delegates specific statistical computations to specialized helper functions, enabling modular and reusable text analysis logic.

The function is extracted from the broader profiling pipeline to encapsulate the core logic for text data summarization, separating it from general data type handling and ensuring clean responsibility boundaries. This modular approach allows for easier testing, maintenance, and extension of text-specific analysis capabilities.

## Args:
    config (Settings): Configuration object containing flags that control which text analyses to perform (length, characters, words).
    series (pd.Series): Input pandas Series containing text data to be analyzed.
    summary (dict): Dictionary containing pre-computed summary statistics, particularly value counts without NaN values.

## Returns:
    Tuple[Settings, pd.Series, dict]: A tuple containing:
        - config: The unchanged configuration object
        - series: The input series converted to string type
        - summary: The updated summary dictionary with additional text statistics including:
          - "first_rows": First 5 rows of the series
          - Conditional additions based on config flags:
            * When config.vars.text.length is True: Adds length statistics and histogram
            * When config.vars.text.characters is True: Adds Unicode character statistics  
            * When config.vars.text.words is True: Adds word frequency statistics

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - The input series must be a valid pandas Series.
        - The summary dictionary must contain a key "value_counts_without_nan".
        - The config object must have a nested structure with vars.text attributes controlling analysis flags.
        - The "value_counts_without_nan" in summary must be a pandas Series with valid index and numeric values.
        
    Postconditions:
        - The series is converted to string type.
        - The summary dictionary is updated with "first_rows" key.
        - Conditional statistics are added to the summary based on config flags.
        - The returned tuple preserves the original structure and types.

## Side Effects:
    - Modifies the input summary dictionary in-place by updating it with new keys.
    - May perform I/O operations through the histogram_compute function when computing histograms.
    - The function modifies the index of value_counts to string type.

## Control Flow:
```mermaid
flowchart TD
    A[Start pandas_describe_text_1d] --> B[Convert series to string type]
    B --> C[Extract value_counts_without_nan from summary]
    C --> D[Convert value_counts index to string type]
    D --> E[Update summary with first_rows (head of series)]
    E --> F{config.vars.text.length enabled?}
    F -->|Yes| G[Call length_summary_vc with value_counts]
    G --> H[Update summary with length results]
    H --> I[Call histogram_compute for length histogram]
    I --> J[Update summary with histogram data]
    F -->|No| J
    J --> K{config.vars.text.characters enabled?}
    K -->|Yes| L[Call unicode_summary_vc with value_counts]
    L --> M[Update summary with unicode results]
    K -->|No| M
    M --> N{config.vars.text.words enabled?}
    N -->|Yes| O[Call word_summary_vc with value_counts and stop_words]
    O --> P[Update summary with word results]
    N -->|No| P
    P --> Q[Return config, series, summary tuple]
```

## Examples:
```python
import pandas as pd
from ydata_profiling.config import Settings

# Example 1: Basic usage with all text analysis enabled
config = Settings()
config.vars.text.length = True
config.vars.text.characters = True
config.vars.text.words = True

series = pd.Series(['hello', 'world', 'hello'])
summary = {
    "value_counts_without_nan": pd.Series([2, 1], index=['hello', 'world'])
}

config_result, series_result, summary_result = pandas_describe_text_1d(config, series, summary)
# Returns the same config, string-converted series, and summary with all text statistics

# Example 2: Usage with only length analysis enabled
config.vars.text.length = True
config.vars.text.characters = False
config.vars.text.words = False

config_result, series_result, summary_result = pandas_describe_text_1d(config, series, summary)
# Result will contain length-related statistics but not character or word statistics

# Example 3: Handling empty series
empty_series = pd.Series([], dtype=object)
empty_summary = {"value_counts_without_nan": pd.Series([], dtype='object')}

config_result, series_result, summary_result = pandas_describe_text_1d(config, empty_series, empty_summary)
# Processes gracefully with empty inputs
```

