# `render_text.py`

## `src.ydata_profiling.report.structure.variables.render_text.render_text` · *function*

## Summary:
Generates HTML template variables for rendering text variable reports with comprehensive statistics, frequency distributions, and optional visualizations.

## Description:
Creates a structured dictionary of template variables specifically designed for rendering text variable reports in data profiling dashboards. This function handles the complex orchestration of multiple report components for text data, including basic statistics, word analysis, character analysis, and length distributions. It dynamically constructs report sections based on configuration settings and available data while maintaining consistent formatting and navigation elements.

The function serves as the main entry point for text variable rendering in the profiling pipeline, providing a complete set of presentation-ready components that can be directly consumed by HTML templates. It intelligently handles conditional rendering based on configuration flags and ensures proper organization of report sections through container hierarchies.

Known callers within the codebase:
- Called by the main profiling pipeline when processing text variables
- Triggered during report generation when text variable summaries are available
- Part of the variable-specific rendering chain that handles different data types differently

This logic is extracted into its own function rather than inlined because it encapsulates the complex orchestration of multiple report components for text data, handles conditional rendering based on configuration flags, and manages the hierarchical structure of text variable reports with proper section organization.

## Args:
    config (Settings): Configuration object containing report settings including:
        - vars.text.words: Boolean flag indicating whether to include word analysis
        - vars.text.characters: Boolean flag indicating whether to include character analysis
        - vars.text.length: Boolean flag indicating whether to include length analysis
        - vars.text.redact: Boolean flag indicating whether to redact sensitive information
        - plot.image_format: Format for generated images (png, svg, etc.)
        - html.style: HTML styling configuration
    summary (dict): Dictionary containing text variable statistics including:
        - varid: Variable identifier
        - varname: Variable name
        - type: Variable type information
        - alerts: List of alerts associated with the variable
        - description: Variable description
        - n_distinct: Count of distinct values
        - p_distinct: Percentage of distinct values
        - n_missing: Count of missing values
        - p_missing: Percentage of missing values
        - memory_size: Memory usage in bytes
        - first_rows: Sample rows of data
        - alert_fields: Fields that triggered alerts
        - word_counts: Word frequency counts
        - category_alias_counts: Category alias frequency counts
        - max_length: Maximum string length
        - median_length: Median string length
        - mean_length: Mean string length
        - min_length: Minimum string length
        - histogram_length: Length distribution data

## Returns:
    dict: Template variables dictionary containing:
        - top: Container with variable information, basic statistics table, and optional mini wordcloud
        - bottom: Container with tabs for Overview and Words/Characters sections

## Raises:
    None explicitly raised by this function, but may propagate exceptions from:
        - Underlying visualization functions when generating plots
        - Helper functions when processing summary data
        - Formatting functions when handling special data types

## Constraints:
    Preconditions:
        - config must be a valid Settings object with all required attributes
        - summary must contain all required keys for text variable analysis
        - All referenced keys in summary must be present and properly formatted
        - Variables in summary must be compatible with the expected data types

    Postconditions:
        - Returns a complete template_variables dictionary ready for HTML rendering
        - All returned containers are properly structured with correct sequence types
        - All HTML anchor IDs are properly prefixed with the variable ID
        - Conditional sections are only included when their respective configuration flags are enabled

## Side Effects:
    None: This function is pure and does not modify external state or perform I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start render_text] --> B{config.vars.text.redact enabled?}
    B -- Yes --> C[Call render_categorical for redacted view]
    B -- No --> D[Extract config and summary variables]
    C --> E[Return redacted render]
    D --> F[Call render_common for base template variables]
    F --> G[Initialize top_items list]
    G --> H[Create VariableInfo component]
    H --> I[Create basic statistics Table]
    I --> J[Add var_info and table to top_items]
    J --> K{words enabled AND word_counts in summary?}
    K -- Yes --> L[Create mini_wordcloud Image]
    K -- No --> M[Skip mini_wordcloud]
    L --> N[Add mini_wordcloud to top_items]
    N --> O[Set template_variables['top'] with Container]
    O --> P[Initialize bottom_items and overview_items lists]
    P --> Q{length enabled AND max_length in summary?}
    Q -- Yes --> R[Call render_categorical_length]
    Q -- No --> S[Skip length analysis]
    R --> T[Add length_table to overview_items]
    T --> U{characters enabled AND category_alias_counts in summary?}
    U -- Yes --> V[Call render_categorical_unicode]
    U -- No --> W[Skip character analysis]
    V --> X[Add overview_table_char to overview_items]
    X --> Y[Call render_categorical_frequency]
    Y --> Z[Add unique_stats to overview_items]
    Z --> AA{redact disabled?}
    AA -- Yes --> AB[Create sample Table from first_rows]
    AA -- No --> AC[Skip sample table]
    AB --> AD[Add sample to overview_items]
    AD --> AE[Create overview Container]
    AE --> AF[Add overview to bottom_items]
    AF --> AG{words enabled AND word_counts in summary?}
    AG -- Yes --> AH[Create word frequency table]
    AH --> AI[Create word container with fqwo and image]
    AI --> AJ[Add word container to bottom_items]
    AJ --> AK{characters enabled AND category_alias_counts in summary?}
    AK -- Yes --> AL[Add character container to bottom_items]
    AL --> AM[Set template_variables['bottom'] with tabs Container]
    AM --> AN[Return template_variables]
```

## Examples:
```python
# Basic usage in a profiling context
from ydata_profiling.config import Settings
from ydata_profiling.report.structure.variables.render_text import render_text

config = Settings()
summary = {
    "varid": "text_col",
    "varname": "Text Column",
    "type": "Text",
    "alerts": [],
    "description": "A sample text column",
    "n_distinct": 50,
    "p_distinct": 0.25,
    "n_missing": 2,
    "p_missing": 0.05,
    "memory_size": 1024,
    "first_rows": [["Hello world", "Foo bar"], ["Test data", "Another test"]],
    "alert_fields": [],
    "word_counts": pd.Series([10, 5, 3, 2, 1]),
    "category_alias_counts": pd.Series([100, 50, 25]),
    "max_length": 15,
    "median_length": 8,
    "mean_length": 9.2,
    "min_length": 2,
    "histogram_length": [(2, 5), (3, 8), (4, 12)]
}

template_vars = render_text(config, summary)
# Returns a complete template_variables dictionary ready for HTML rendering
```

