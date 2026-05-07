# `pandas_decorator.py`

## `src.ydata_profiling.controller.pandas_decorator.profile_report` · *function*

## Summary:
Creates and returns a ProfileReport instance from a pandas DataFrame with optional configuration parameters.

## Description:
This function serves as a convenience wrapper for creating ProfileReport objects. It takes a pandas DataFrame and optional keyword arguments, then instantiates a ProfileReport object with these parameters. The function is designed to provide a clean, simple interface for initializing profiling reports while maintaining access to all ProfileReport configuration options.

## Args:
    df (DataFrame): A pandas DataFrame to be profiled
    **kwargs: Additional keyword arguments passed directly to the ProfileReport constructor

## Returns:
    ProfileReport: An initialized ProfileReport object ready for analysis

## Raises:
    ValueError: May be raised by ProfileReport.__init__ if invalid parameters are provided
    NotImplementedError: May be raised by ProfileReport.__init__ if unsupported features are requested

## Constraints:
    Preconditions:
    - df must be a valid pandas DataFrame or None
    - All kwargs must be valid parameters for ProfileReport initialization
    
    Postconditions:
    - Returns a properly initialized ProfileReport instance
    - The returned instance contains the provided DataFrame and configuration

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[profile_report called] --> B{Valid df provided?}
    B -- Yes --> C[Create ProfileReport(df, **kwargs)]
    B -- No --> C
    C --> D[Return ProfileReport instance]
```

## Examples:
```python
import pandas as pd
from ydata_profiling import profile_report

# Basic usage
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
report = profile_report(df)

# Usage with configuration
report = profile_report(df, minimal=True, dark_mode=True)
```

