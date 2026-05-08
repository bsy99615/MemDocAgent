# `render_text.py`

## `src.ydata_profiling.report.structure.variables.render_text.render_text` · *function*

## Summary:
Generates a complete HTML report structure for text variables by combining basic statistics, frequency distributions, and optional analysis components.

## Description:
Creates a comprehensive template variables dictionary for rendering text variable reports in HTML format. This function orchestrates multiple presentation components to display key characteristics of text data including basic statistics, frequency tables, unique value analysis, and optional extensions like string length distributions, word frequencies, and Unicode character analysis.

The function serves as the primary entry point for text variable report generation and handles conditional rendering based on configuration settings. When redaction is enabled, it delegates to the categorical rendering function to avoid exposing sensitive text data. Otherwise, it builds a structured report with top and bottom containers that organize variable information, statistics, and detailed analyses.

This logic is extracted into its own function to separate concerns: while `render_common` handles general frequency table operations and extreme observations, `render_text` specifically manages the text-specific components and conditional rendering logic.

## Args:
    config (Settings): Configuration object containing report settings including:
        - `vars.text.words`: Whether to include word frequency analysis
        - `vars.text.characters`: Whether to include Unicode character analysis
        - `vars.text.length`: Whether to include string length analysis
        - `vars.text.redact`: Whether to redact sensitive information
        - `html.style`: HTML styling configuration
        - `plot.image_format`: Format for generated plots (png, svg, etc.)
    summary (dict): Dictionary containing text variable statistics including:
        - "varid": Variable identifier
        - "varname": Variable name
        - "type": Variable type (typically "Text")
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

## Returns:
    dict: Template variables dictionary containing:
        - "top": Container with VariableInfo, basic statistics table, and frequency table small
        - "bottom": Container with tabs for Overview and Words/Characters sections
        - Additional keys populated by render_common for frequency tables and extreme observations

## Raises:
    None explicitly raised - All potential errors are handled by underlying components

## Constraints:
    Preconditions:
        - config must be a valid Settings object with properly initialized configurations
        - summary must contain all required keys for basic text analysis
        - Required keys include: "varid", "varname", "type", "alerts", "description", "n_distinct", "p_distinct", "n_missing", "p_missing", "memory_size", "value_counts_without_nan", "count", "first_rows", "alert_fields"
        - Optional keys depend on enabled features (length, words, characters analysis)

    Postconditions:
        - Returns a complete template variables dictionary ready for HTML rendering
        - All returned components are properly styled and anchored
        - The structure follows the expected report layout with top and bottom containers

## Side Effects:
    None - This function is pure and does not modify external state or perform I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start render_text] --> B{Redact enabled?}
    B -->|Yes| C[Call render_categorical(config, summary)]
    B -->|No| D[Initialize variables from config and summary]
    C --> E[Return categorical render result]
    D --> F[Call render_common for base template variables]
    F --> G[Create VariableInfo component]
    G --> H[Create basic statistics table]
    H --> I[Create top Container with info, table]
    I --> J{Words enabled AND word_counts in summary?}
    J -->|Yes| K[Create mini wordcloud Image]
    J -->|No| L[Skip wordcloud]
    K --> M[Add wordcloud to top Container]
    L --> M
    M --> N[Initialize bottom_items and overview_items]
    N --> O{Length enabled AND max_length in summary?}
    O -->|Yes| P[Call render_categorical_length]
    O -->|No| Q[Skip length analysis]
    P --> R[Add length_table to overview_items]
    R --> S{Characters enabled AND category_alias_counts in summary?}
    S -->|Yes| T[Call render_categorical_unicode]
    S -->|No| U[Skip Unicode analysis]
    T --> V[Add overview_table_char to overview_items]
    V --> W[Add unique_stats to overview_items]
    W --> X{Redact disabled?}
    X -->|Yes| Y[Create sample table from first_rows]
    X -->|No| Z[Skip sample table]
    Y --> AA[Add sample to overview_items]
    AA --> AB[Create Overview container]
    AB --> AC{Words enabled AND word_counts in summary?}
    AC -->|Yes| AD[Create common words FrequencyTable and Image]
    AC -->|No| AE[Skip words section]
    AD --> AF[Add words container to bottom_items]
    AE --> AF
    AF --> AG{Characters enabled AND category_alias_counts in summary?}
    AG -->|Yes| AH[Add characters container to bottom_items]
    AG -->|No| AI[Skip characters section]
    AH --> AJ[Create bottom Container with tabs]
    AI --> AJ
    AJ --> AK[Return template_variables]
```

## Examples:
```python
# Basic usage for text variable report generation
config = Settings()
summary = {
    "varid": "text_var_1",
    "varname": "Text Variable",
    "type": "Text",
    "alerts": [],
    "description": "A sample text variable",
    "n_distinct": 10,
    "p_distinct": 0.2,
    "n_missing": 5,
    "p_missing": 0.05,
    "memory_size": 1024,
    "value_counts_without_nan": pd.Series([50, 30, 20], index=['A', 'B', 'C']),
    "count": 250,
    "first_rows": [['A', 'X'], ['B', 'Y'], ['C', 'Z']],
    "alert_fields": [],
    "word_counts": pd.Series([10, 5, 3], index=['hello', 'world', 'test']),
    "category_alias_counts": pd.Series([100, 50], index=['Latin', 'Greek']),
    "max_length": 15,
    "median_length": 8,
    "mean_length": 9.2,
    "min_length": 2,
    "histogram_length": [(2, 5), (3, 10), (4, 15), (5, 20)]
}

template_vars = render_text(config, summary)
# Returns complete template variables for HTML rendering
```

