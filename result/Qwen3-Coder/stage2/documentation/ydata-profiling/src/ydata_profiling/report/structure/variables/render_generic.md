# `render_generic.py`

## `src.ydata_profiling.report.structure.variables.render_generic.render_generic` · *function*

## Summary:
Renders standardized variable information display for unsupported variable types in data profiling reports.

## Description:
Generates a consistent UI presentation for variable metadata and summary statistics when the variable type doesn't have a specialized renderer. This function serves as a fallback mechanism to ensure all variables are displayed uniformly in reports, even when detailed analysis isn't available for specific variable types.

The function creates a structured presentation containing variable identification information, basic statistics (missing values, memory usage), and appropriate formatting. It's typically invoked when no specific variable type handler is available, providing a baseline display structure that maintains report consistency.

## Args:
    config (Settings): Configuration object containing report settings including HTML styling options
    summary (dict): Dictionary containing variable summary information with the following required keys:
        - varid (str): Unique identifier for the variable
        - alerts (list): List of alert objects associated with the variable
        - varname (str): Human-readable name of the variable
        - description (str): Description or explanation of the variable
        - n_missing (int): Count of missing values
        - p_missing (float): Percentage of missing values (0.0 to 1.0)
        - memory_size (int): Memory usage in bytes
        - alert_fields (list): List of field names that triggered alerts

## Returns:
    dict: A dictionary with two keys:
        - "top": Container object containing VariableInfo, Table, and HTML elements arranged in a grid sequence
        - "bottom": None (indicating no additional bottom section for this generic rendering)

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
    - config parameter must be a valid Settings object with html.style attribute
    - summary dictionary must contain all required keys with appropriate types
    - All values in summary dictionary must be of expected types (str, list, int, float)
    - The summary["alert_fields"] should be a list that can be checked for membership

    Postconditions:
    - Returns a properly structured dictionary with exactly "top" and "bottom" keys
    - The "top" value contains a Container with exactly three elements: VariableInfo, Table, and HTML
    - The "bottom" value is always None
    - All formatting functions (fmt, fmt_percent, fmt_bytesize) are applied appropriately

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_generic] --> B[Create VariableInfo with var_type="Unsupported"]
    B --> C[Create Table with 3 statistic rows]
    C --> D[Return dict with Container and None]
```

## Examples:
    >>> from ydata_profiling.config import Settings
    >>> config = Settings()
    >>> summary = {
    ...     "varid": "var_123",
    ...     "alerts": [],
    ...     "varname": "age",
    ...     "description": "Age of participants",
    ...     "n_missing": 5,
    ...     "p_missing": 0.01,
    ...     "memory_size": 1024,
    ...     "alert_fields": []
    ... }
    >>> result = render_generic(config, summary)
    >>> print(type(result["top"]))
    <class 'ydata_profiling.report.presentation.core.container.Container'>
    >>> print(result["bottom"])
    None
    >>> # The returned container contains VariableInfo, Table, and HTML elements
    >>> container_items = result["top"].items
    >>> print(len(container_items))
    3
```

