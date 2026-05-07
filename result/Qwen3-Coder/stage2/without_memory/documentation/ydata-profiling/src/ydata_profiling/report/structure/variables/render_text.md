# `render_text.py`

## `src.ydata_profiling.report.structure.variables.render_text.render_text` · *function*

## Summary
Generates a structured HTML report template for text variables, including metadata, statistics, and visualizations.

## Description
This function creates a comprehensive report structure for text variables in a data profiling dashboard. It handles different rendering modes based on configuration settings, particularly when text redaction is enabled. The function organizes information into top and bottom sections, with detailed statistical breakdowns including word frequencies, character analysis, and sample data views.

The function is designed to be a specialized renderer for text variables that leverages common rendering utilities and categorical-specific components while providing text-specific features like word clouds and length distributions. When text redaction is enabled via `config.vars.text.redact`, it delegates to the categorical renderer to maintain consistency.

## Args
- config (Settings): Configuration object containing various settings for report generation, including text-specific options like redact, words, characters, and length flags. The redact flag determines whether sensitive information should be masked.
- summary (Dict[str, Any]): Dictionary containing statistical summary data for the text variable. Required keys include: "varid", "varname", "type", "alerts", "description", "n_distinct", "p_distinct", "n_missing", "p_missing", "memory_size", "alert_fields". Optional keys that enable specific features: "word_counts", "max_length", "category_alias_counts", "first_rows", "value_counts_without_nan", "n".

## Returns
- Dict[str, Any]: Template variables dictionary containing 'top' and 'bottom' keys. The 'top' key contains metadata and basic statistics, while the 'bottom' key contains detailed analysis sections organized into tabs.

## Raises
- None explicitly raised in the function body

## Constraints
- Preconditions:
  - The summary dictionary must contain required keys: "varid", "varname", "type", "alerts", "description", "n_distinct", "p_distinct", "n_missing", "p_missing", "memory_size", "alert_fields"
  - When `config.vars.text.words` is True, summary must contain "word_counts" key
  - When `config.vars.text.length` is True, summary must contain "max_length" key  
  - When `config.vars.text.characters` is True, summary must contain "category_alias_counts" key
  - When not redacting (`config.vars.text.redact` is False), summary must contain "first_rows" key for sample display
- Postconditions:
  - Returns a dictionary with 'top' and 'bottom' keys containing properly structured Container objects
  - All rendered elements are properly formatted using the appropriate formatters (fmt, fmt_percent, fmt_bytesize)
  - The returned template variables are compatible with the HTML report generation system

## Side Effects
- None explicitly mentioned in the function body
- May indirectly cause file I/O through the `plot_word_cloud` function which likely generates temporary files for image creation
- Uses external visualization libraries for creating word clouds and histograms
- May modify global state through the plotting system

## Control Flow
```mermaid
flowchart TD
    A[Start render_text] --> B{config.vars.text.redact?}
    B -- Yes --> C[render_categorical(config, summary)]
    B -- No --> D[Extract varid, words, characters, length]
    C --> E[Return render_categorical result]
    D --> F[Call render_common(config, summary)]
    F --> G[Initialize top_items list]
    G --> H[Create VariableInfo]
    H --> I[Add VariableInfo to top_items]
    I --> J[Create summary table]
    J --> K[Add table to top_items]
    K --> L{words and word_counts in summary?}
    L -- Yes --> M[Create mini_wordcloud Image]
    M --> N[Add mini_wordcloud to top_items]
    N --> O[Set template_variables.top]
    O --> P[Initialize bottom_items and overview_items]
    P --> Q{length and max_length in summary?}
    Q -- Yes --> R[Call render_categorical_length]
    R --> S[Add length_table to overview_items]
    S --> T[Continue processing]
    Q -- No --> T
    T --> U{characters and category_alias_counts in summary?}
    U -- Yes --> V[Call render_categorical_unicode]
    V --> W[Add overview_table_char to overview_items]
    W --> X[Store unitab reference]
    X --> Y[Continue processing]
    U -- No --> Y
    Y --> Z[Call render_categorical_frequency]
    Z --> AA[Add unique_stats to overview_items]
    AA --> AB{Not redact?}
    AB -- Yes --> AC[Create sample table from first_rows]
    AC --> AD[Add sample to overview_items]
    AD --> AE[Create overview Container]
    AE --> AF[Add overview to bottom_items]
    AF --> AG{words and word_counts in summary?}
    AG -- Yes --> AH[Create word frequency table]
    AH --> AI[Create word cloud Image]
    AI --> AJ[Create Words Container]
    AJ --> AK[Add Words container to bottom_items]
    AK --> AL[Check unitab is not None]
    AL -- Yes --> AM[Create Characters Container]
    AM --> AN[Add Characters container to bottom_items]
    AN --> AO[Create final bottom Container]
    AO --> AP[Return template_variables]
```

## Examples
```python
# Basic usage with minimal configuration
config = Settings()
summary = {
    "varid": "text_var_1",
    "varname": "review_text",
    "type": "Text",
    "alerts": [],
    "description": "Customer reviews",
    "n_distinct": 1500,
    "p_distinct": 0.75,
    "n_missing": 50,
    "p_missing": 0.02,
    "memory_size": 102400,
    "alert_fields": [],
    "word_counts": pd.Series({'good': 100, 'bad': 50}),
    "max_length": 200,
    "category_alias_counts": pd.Series({'latin': 500, 'cyrillic': 200}),
    "first_rows": ['This is a sample review.', 'Another review here.']
}

result = render_text(config, summary)
# Returns template_variables with 'top' and 'bottom' containers
# The 'top' section contains variable info and basic stats
# The 'bottom' section contains overview and detailed analysis tabs

# Usage with redaction enabled
config.vars.text.redact = True
result = render_text(config, summary)
# Delegates to render_categorical for consistent redacted output

# Usage with word analysis disabled
config.vars.text.words = False
result = render_text(config, summary)
# Omits word cloud and word frequency sections
```

