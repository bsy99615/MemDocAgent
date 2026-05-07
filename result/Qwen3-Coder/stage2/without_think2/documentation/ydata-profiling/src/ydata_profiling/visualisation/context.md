# `context.py`

## `src.ydata_profiling.visualisation.context.manage_matplotlib_context` · *function*

## Summary:
A context manager that temporarily configures matplotlib and seaborn settings for consistent visualization rendering.

## Description:
This function provides a context manager that temporarily modifies matplotlib's rcParams and sets a specific seaborn style for plotting. It ensures that all visualizations generated within its context use a standardized appearance while preserving the original configuration upon exit. The function registers matplotlib converters, applies custom styling parameters, and properly restores the original settings even if exceptions occur during execution.

## Args:
    None

## Returns:
    Generator[Any, None, None]: A context manager generator that yields control to the enclosed code block. This allows the function to be used with Python's 'with' statement for automatic resource management.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Matplotlib and seaborn must be properly installed and importable
    - The function should be used within a context manager (with statement) to ensure proper cleanup
    
    Postconditions:
    - All matplotlib rcParams are restored to their original values upon exiting the context
    - Matplotlib converters are deregistered to prevent interference with other code
    - Seaborn style is reset to default after the context exits

## Side Effects:
    - Modifies global matplotlib rcParams settings
    - Registers and deregisters matplotlib converters
    - Sets seaborn style to "white"
    - May suppress matplotlib deprecation warnings during cleanup

## Control Flow:
```mermaid
flowchart TD
    A[Start manage_matplotlib_context] --> B[Save original rcParams]
    B --> C[Define custom rcParams dict]
    C --> D[Register matplotlib converters]
    D --> E[Update rcParams with custom values]
    E --> F[Set seaborn style to "white"]
    F --> G[Yield control to enclosed code]
    G --> H{Exit context}
    H --> I[Deregister matplotlib converters]
    I --> J[Suppress mplDeprecation warnings]
    J --> K[Restore original rcParams]
    K --> L[End]
```

## Examples:
```python
# Basic usage with matplotlib/seaborn plotting
import matplotlib.pyplot as plt
import seaborn as sns

with manage_matplotlib_context():
    # All plots here will use custom styling
    plt.figure(figsize=(8, 5.5))
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("Custom Styled Plot")
    plt.savefig('custom_plot.png')

# Multiple contexts in sequence
with manage_matplotlib_context():
    plt.plot([1, 2, 3], [1, 4, 9])

with manage_matplotlib_context():
    plt.plot([1, 2, 3], [1, 8, 27])
```

