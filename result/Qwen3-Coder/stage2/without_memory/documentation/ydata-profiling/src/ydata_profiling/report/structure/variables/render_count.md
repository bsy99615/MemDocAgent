# `render_count.py`

## `src.ydata_profiling.report.structure.variables.render_count.render_count` · *function*

## Summary
Generates HTML template variables for rendering count-based statistical summaries of numerical variables in data profiling reports.

## Description
This function creates a structured set of template variables containing all the necessary components to display comprehensive statistical information about numerical variables. It builds upon common template variables from `render_common` and adds specific count-based statistics, tables, histograms, and frequency information for numerical data types.

The function is designed to be called during the report generation phase when creating HTML output for numerical variables. It organizes information into two main sections: a top section with basic statistics and a bottom section with detailed visualizations and frequency distributions.

## Args
- config (Settings): Configuration object containing report settings such as precision, image formats, and display preferences
- summary (dict): Dictionary containing statistical summary data for the variable including counts, percentages, min/max values, histogram data, and frequency tables

## Returns
- dict: Template variables dictionary containing:
  - 'top' (Container): Grid layout with variable info, basic statistics table, descriptive statistics table, and mini histogram
  - 'bottom' (Container): Tabbed layout with histogram, frequency table, and extreme values tabs

## Raises
- None explicitly raised, but may raise exceptions from underlying functions like histogram plotting or formatting utilities

## Constraints
- Preconditions:
  - The summary dictionary must contain all required keys: varid, varname, alerts, description, n_distinct, p_distinct, n_missing, p_missing, mean, min, max, n_zeros, p_zeros, memory_size, histogram, value_counts_without_nan, value_counts_index_sorted, n
  - Config must have valid plot.image_format and html.style settings
- Postconditions:
  - Returns a properly structured dictionary with 'top' and 'bottom' keys
  - All returned elements are properly formatted presentation objects

## Side Effects
- Calls external visualization functions that may generate temporary plot files
- Uses formatters to convert numeric values into human-readable strings
- May involve file I/O operations during plot generation and saving

## Control Flow
```mermaid
flowchart TD
    A[Start render_count] --> B[Call render_common]
    B --> C[Create VariableInfo]
    C --> D[Create table1 (Basic stats)]
    D --> E[Create table2 (Descriptive stats)]
    E --> F[Create mini_histogram]
    F --> G[Build top Container]
    G --> H[Create histogram Image]
    H --> I[Create FrequencyTable]
    I --> J[Create extreme values Container]
    J --> K[Build bottom Container]
    K --> L[Return template_variables]
```

## Examples
```python
# Typical usage in report generation
config = Settings()
summary = {
    "varid": "var1",
    "varname": "age",
    "alerts": [],
    "description": "Age of participants",
    "n_distinct": 50,
    "p_distinct": 0.8,
    "n_missing": 5,
    "p_missing": 0.05,
    "mean": 35.2,
    "min": 18,
    "max": 85,
    "n_zeros": 2,
    "p_zeros": 0.02,
    "memory_size": 1024,
    "histogram": [np.array([1,2,3]), np.array([0,10,20,30])],
    "value_counts_without_nan": pd.Series([10, 5, 3]),
    "value_counts_index_sorted": pd.Series([10, 5, 3])
}

template_vars = render_count(config, summary)
```

