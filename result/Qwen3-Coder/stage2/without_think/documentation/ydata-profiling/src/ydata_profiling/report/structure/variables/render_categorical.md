# `render_categorical.py`

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical_frequency` · *function*

## Summary:
Creates a frequency table displaying unique value statistics for categorical variables.

## Description:
Generates a structured table showing the count and percentage of unique values in a categorical variable. This function is part of the categorical variable rendering pipeline and specifically focuses on presenting uniqueness statistics that help characterize the cardinality of categorical data.

The function extracts unique count (`n_unique`) and unique percentage (`p_unique`) from the summary data, applies appropriate formatting, and incorporates help tooltips and alert indicators based on the presence of these fields in the alert fields list. It returns a Table renderable object that can be embedded in HTML reports.

This logic is extracted into its own function to separate concerns: while `render_common` handles general frequency table operations and extreme observations, this function specifically addresses the unique value statistics that are fundamental to understanding categorical variable characteristics.

## Args:
    config (Settings): Configuration settings that define report styling and behavior, including HTML styling options
    summary (dict): Dictionary containing variable summary statistics including:
        - "n_unique": Integer count of unique values
        - "p_unique": Float percentage of unique values
        - "alert_fields": List of field names that triggered alerts
    varid (str): Unique identifier for the variable, used to generate anchor IDs for HTML linking

## Returns:
    Renderable: A Table object containing two rows with unique value statistics:
        - "Unique": Formatted count of unique values
        - "Unique (%)": Formatted percentage of unique values
    The returned table includes styling from config.html.style and anchor_id for HTML navigation.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - summary dictionary must contain "n_unique", "p_unique", and "alert_fields" keys
        - config must be a valid Settings object with html.style attribute
        - varid must be a non-empty string for proper anchor ID generation

    Postconditions:
        - Returns a properly formatted Table renderable object
        - Table contains exactly two rows with unique value statistics
        - Table is styled according to the provided configuration

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_categorical_frequency] --> B[Create Table with unique stats]
    B --> C{Check if n_unique in alert_fields}
    C -->|Yes| D[Set alert=True for Unique row]
    C -->|No| E[Set alert=False for Unique row]
    D --> F{Check if p_unique in alert_fields}
    F -->|Yes| G[Set alert=True for Unique (%) row]
    F -->|No| H[Set alert=False for Unique (%) row]
    G --> I[Return Table renderable]
    H --> I
```

## Examples:
```python
# Basic usage
config = Settings()
summary = {
    "n_unique": 42,
    "p_unique": 0.84,
    "alert_fields": ["n_unique"]
}
varid = "category_var_1"

table = render_categorical_frequency(config, summary, varid)
# Returns Table with:
# - "Unique": "42" with alert=True
# - "Unique (%)": "84%" with alert=False
```

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical_length` · *function*

## Summary:
Creates a statistical summary table and histogram visualization for categorical variable string lengths.

## Description:
Generates a formatted table displaying descriptive statistics (maximum, median, mean, minimum) of string lengths for categorical variables, along with a histogram visualization showing the distribution of these lengths. This function is part of the categorical variable reporting pipeline and extracts length-related statistics into separate renderable components for presentation.

The function is designed to be called by higher-level rendering functions in the categorical variable reporting system, separating concerns between statistical computation and presentation layer construction.

## Args:
    config (Settings): Configuration object containing report settings including precision and HTML styling options
    summary (dict): Dictionary containing categorical variable statistics including length-related metrics and histogram data
    varid (str): Unique identifier for the variable, used to generate unique HTML anchor IDs

## Returns:
    Tuple[Renderable, Renderable]: A tuple containing:
        - Table: A formatted table with length statistics (max, median, mean, min)
        - Image: A histogram visualization of the length distribution

## Raises:
    None explicitly raised - the function delegates to underlying components that may raise exceptions

## Constraints:
    Preconditions:
    - The summary dictionary must contain keys: "max_length", "median_length", "mean_length", "min_length", and "histogram_length"
    - The config parameter must be a valid Settings object with properly initialized report and plot configurations
    - The varid parameter must be a non-empty string

    Postconditions:
    - Returns a tuple of exactly two Renderable objects (Table and Image)
    - Both returned objects are properly configured with appropriate styling and identifiers

## Side Effects:
    None - the function is pure and has no side effects

## Control Flow:
```mermaid
flowchart TD
    A[Start render_categorical_length] --> B[Create length statistics table]
    B --> C{histogram_length type}
    C -->|list| D[Extract x,y data from list]
    C -->|other| E[Unpack histogram_length data]
    D --> F[Generate histogram data]
    E --> F
    F --> G[Create length histogram image]
    G --> H[Return (table, image) tuple]
```

## Examples:
```python
# Typical usage within categorical variable reporting
config = Settings()
summary = {
    "max_length": 15,
    "median_length": 8,
    "mean_length": 9.2,
    "min_length": 2,
    "histogram_length": [(2, 5), (3, 10), (4, 15), (5, 20)]
}
varid = "category_var_1"

table, histogram = render_categorical_length(config, summary, varid)
# Returns a Table with length stats and Image with histogram
```

## `src.ydata_profiling.report.structure.variables.render_categorical._get_n` · *function*

## Summary:
Computes the sum of values from either a list of pandas objects or a single pandas object.

## Description:
This utility function extracts sum values from data structures commonly used in categorical variable analysis. It handles two distinct input types: a list of pandas objects (such as Series or DataFrames) where each element's sum is computed, or a single pandas object where the sum is computed directly. This abstraction allows the categorical variable rendering logic to handle different data representations uniformly.

## Args:
    value (Union[list, pd.DataFrame]): Input data structure containing numeric values. Can be either:
        - A list of pandas objects (Series/DataFrame) where each element's sum will be computed
        - A single pandas object (DataFrame/Series) where the sum will be computed directly

## Returns:
    Union[int, List[int]]: The computed sum(s) as either:
        - A single integer when input is a pandas object
        - A list of integers when input is a list of pandas objects

## Raises:
    AttributeError: When the input value or its elements don't have a `.sum()` method

## Constraints:
    Preconditions:
        - Input must be either a list of objects with `.sum()` method or a single object with `.sum()` method
        - Each pandas object in the list must support the `.sum()` method
        - The `.sum()` method must return numeric values
    
    Postconditions:
        - Returns an integer when input is a pandas object
        - Returns a list of integers when input is a list of pandas objects

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input value] --> B{Is instance list?}
    B -- Yes --> C[Iterate through list]
    C --> D[Compute v.sum() for each element]
    D --> E[Return list of sums]
    B -- No --> F[Compute value.sum()]
    F --> G[Return single sum]
```

## Examples:
```python
# Example 1: Single pandas DataFrame/Series
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
result = _get_n(df)  # Returns 21 (sum of all values)

# Example 2: List of pandas objects
series_list = [pd.Series([1, 2]), pd.Series([3, 4])]
result = _get_n(series_list)  # Returns [3, 7] (sums of each series)
```

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical_unicode` · *function*

## Summary
Renders categorical Unicode analysis results including character frequencies, Unicode categories, scripts, and blocks for textual variables.

## Description
This function generates a comprehensive Unicode analysis report for categorical variables by creating frequency tables and statistical summaries for various Unicode properties. It processes character-level data including categories, scripts, and blocks to provide detailed insights into the Unicode characteristics of textual data.

The function is typically called during the report generation phase when analyzing categorical variables that contain Unicode text data. It organizes the Unicode analysis into logical sections: character frequencies, categories, scripts, and blocks, each presented in a structured tabbed interface.

## Args
    config (Settings): Configuration object containing report settings including frequency table limits and styling options
    summary (dict): Dictionary containing pre-computed Unicode statistics and frequency data for the variable
    varid (str): Unique identifier for the variable being analyzed, used for generating HTML anchors

## Returns
    Tuple[Renderable, Renderable]: A tuple containing:
        - overview_table (Table): Statistical summary table with character counts and Unicode property counts
        - Container: Tabbed container with sections for Characters, Categories, Scripts, and Blocks

## Raises
    None explicitly raised - All potential errors in underlying functions are handled by those functions

## Constraints
    Preconditions:
        - config must be a valid Settings object with appropriate Unicode analysis configurations
        - summary must contain all required keys: "category_alias_counts", "category_alias_char_counts", "script_counts", "script_char_counts", "block_alias_counts", "block_alias_char_counts", "character_counts", "n_characters", "n_characters_distinct", "n_category", "n_scripts", "n_block_alias"
        - varid must be a valid string identifier for the variable

    Postconditions:
        - Returns a properly structured tuple of Renderable objects ready for report generation
        - All frequency tables are properly formatted with appropriate redaction settings
        - HTML anchor IDs are correctly generated using the provided varid

## Side Effects
    None - This function is pure and does not modify external state or perform I/O operations

## Control Flow
```mermaid
flowchart TD
    A[Start render_categorical_unicode] --> B[Initialize n_freq_table_max]
    B --> C[Process category data]
    C --> D[Process script data]
    D --> E[Process block data]
    E --> F[Process character data]
    F --> G[Create overview table]
    G --> H[Assemble tabbed container]
    H --> I[Return (overview_table, Container)]
```

## Examples
```python
# Typical usage in report generation pipeline
config = Settings()
summary = {
    "category_alias_counts": pd.Series([10, 5, 3]),
    "category_alias_char_counts": {"Latin": pd.Series([2, 1]), "Greek": pd.Series([1, 1])},
    "script_counts": pd.Series([15, 8]),
    "script_char_counts": {"Latin": pd.Series([3, 2]), "Greek": pd.Series([2, 1])},
    "block_alias_counts": pd.Series([20, 12]),
    "block_alias_char_counts": {"Basic Latin": pd.Series([5, 3]), "Latin-1 Supplement": pd.Series([4, 2])},
    "character_counts": pd.Series([100, 50, 25]),
    "n_characters": 1000,
    "n_characters_distinct": 200,
    "n_category": 10,
    "n_scripts": 5,
    "n_block_alias": 8
}
varid = "var_123"

overview_table, unicode_container = render_categorical_unicode(config, summary, varid)
```

## `src.ydata_profiling.report.structure.variables.render_categorical.render_categorical` · *function*

## Summary
Generates a complete HTML report structure for categorical variables by combining basic statistics, frequency distributions, and optional analysis components.

## Description
Creates a comprehensive template variables dictionary for rendering categorical variable reports in HTML format. This function orchestrates multiple presentation components to display key characteristics of categorical data including basic statistics, frequency tables, unique value analysis, and optional extensions like string length distributions, word frequencies, and Unicode character analysis.

The function leverages helper functions to modularize different aspects of categorical variable analysis:
- `render_common` for base frequency and extreme observation tables
- `render_categorical_frequency` for unique value statistics  
- `render_categorical_length` for string length analysis
- `render_categorical_unicode` for Unicode character analysis

This extraction into a dedicated function enables clean separation of concerns, allowing the categorical variable reporting pipeline to maintain modularity while providing a unified interface for generating complete categorical variable reports.

## Args
    config (Settings): Configuration object containing report settings including:
        - `vars.cat.n_obs`: Maximum number of observations to display in frequency tables
        - `plot.image_format`: Format for generated plots (png, svg, etc.)
        - `vars.cat.words`: Whether to include word frequency analysis
        - `vars.cat.characters`: Whether to include Unicode character analysis
        - `vars.cat.length`: Whether to include string length analysis
        - `vars.cat.redact`: Whether to redact sensitive information
        - `html.style`: HTML styling configuration
        - `plot.cat_freq.show`: Whether to show categorical frequency plots
        - `plot.cat_freq.max_unique`: Maximum unique values to plot
    summary (dict): Dictionary containing categorical variable statistics including:
        - "varid": Variable identifier
        - "varname": Variable name
        - "type": Variable type (can be list)
        - "alerts": List of alerts for the variable
        - "description": Variable description
        - "n_distinct": Count of distinct values
        - "p_distinct": Percentage of distinct values
        - "n_missing": Count of missing values
        - "p_missing": Percentage of missing values
        - "memory_size": Memory usage in bytes
        - "value_counts_without_nan": Frequency counts for values
        - "count": Total count of observations
        - "first_rows": Sample rows of data
        - "alert_fields": Fields that triggered alerts
        - Optional keys for extended analysis: "max_length", "median_length", "mean_length", "min_length", "histogram_length", "word_counts", "category_alias_counts", etc.

## Returns
    dict: Template variables dictionary containing:
        - "top": Container with VariableInfo, basic statistics table, and frequency table small
        - "bottom": Container with tabs for Overview and Categories sections
        - Additional keys populated by render_common for frequency tables and extreme observations

## Raises
    None explicitly raised - All potential errors are handled by underlying components

## Constraints
    Preconditions:
        - config must be a valid Settings object with properly initialized configurations
        - summary must contain all required keys for basic categorical analysis
        - Required keys include: "varid", "varname", "type", "alerts", "description", "n_distinct", "p_distinct", "n_missing", "p_missing", "memory_size", "value_counts_without_nan", "count", "first_rows", "alert_fields"
        - Optional keys depend on enabled features (length, words, characters analysis)

    Postconditions:
        - Returns a complete template variables dictionary ready for HTML rendering
        - All returned components are properly styled and anchored
        - The structure follows the expected report layout with top and bottom containers

## Side Effects
    None - This function is pure and does not modify external state or perform I/O operations

## Control Flow
```mermaid
flowchart TD
    A[Start render_categorical] --> B[Initialize variables from config and summary]
    B --> C[Call render_common for base template variables]
    C --> D[Create VariableInfo component]
    D --> E[Create basic statistics table]
    E --> F[Create FrequencyTableSmall for top frequencies]
    F --> G[Set template_variables["top"] with info, table, fqm]
    G --> H[Create frequency_table from template_variables["freq_table_rows"]]
    H --> I[Call render_categorical_frequency for unique stats]
    I --> J[Initialize overview_items list]
    J --> K{length enabled AND max_length in summary?}
    K -->|Yes| L[Call render_categorical_length]
    K -->|No| M[Skip length analysis]
    L --> N[Add length_table to overview_items]
    N --> O{characters enabled AND category_alias_counts in summary?}
    O -->|Yes| P[Call render_categorical_unicode]
    O -->|No| Q[Skip Unicode analysis]
    P --> R[Add overview_table_char to overview_items]
    R --> S[Add unique_stats to overview_items]
    S --> T{redact disabled?}
    T -->|Yes| U[Create sample table from first_rows]
    T -->|No| V[Skip sample table]
    U --> W[Add sample to overview_items]
    W --> X[Initialize string_items with frequency_table]
    X --> Y{length enabled AND max_length in summary?}
    Y -->|Yes| Z[Add length_histo to string_items]
    Z --> AA[Set show and max_unique from config]
    AA --> AB{show AND max_unique > 0?}
    AB -->|Yes| AC{value_counts_without_nan is list?}
    AC -->|Yes| AD[Create batch grid with cat frequency plots]
    AC -->|No| AE{single label AND n_distinct <= max_unique?}
    AE -->|Yes| AF[Create single cat frequency plot]
    AE -->|No| AG[Create HTML warning message]
    AD --> AH[Add plot container to string_items]
    AF --> AH
    AG --> AH
    AH --> AI[Create bottom_items list]
    AI --> AJ[Create Overview container]
    AJ --> AK[Create Categories container]
    AK --> AL[Set template_variables["bottom"] with tabs]
    AL --> AM{words enabled AND word_counts in summary?}
    AM -->|Yes| AN[Create common words FrequencyTable]
    AN --> AO[Add words container to bottom_items]
    AO --> AP{characters enabled AND category_alias_counts in summary?}
    AP -->|Yes| AQ[Add characters container to bottom_items]
    AQ --> AR[Return template_variables]
```

## Examples
```python
# Basic usage for categorical variable report generation
config = Settings()
summary = {
    "varid": "cat_var_1",
    "varname": "Category Variable",
    "type": "Categorical",
    "alerts": [],
    "description": "A sample categorical variable",
    "n_distinct": 10,
    "p_distinct": 0.2,
    "n_missing": 5,
    "p_missing": 0.05,
    "memory_size": 1024,
    "value_counts_without_nan": pd.Series([50, 30, 20], index=['A', 'B', 'C']),
    "count": 250,
    "first_rows": [['A', 'X'], ['B', 'Y'], ['C', 'Z']],
    "alert_fields": []
}

template_vars = render_categorical(config, summary)
# Returns complete template variables for HTML rendering
```

