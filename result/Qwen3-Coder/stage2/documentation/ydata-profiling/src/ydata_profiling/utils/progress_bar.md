# `progress_bar.py`

## `src.ydata_profiling.utils.progress_bar.progress` · *function*

## Summary:
Creates a progress bar wrapper that displays a message and updates the progress bar when a function is called.

## Description:
A decorator factory that wraps a function with progress bar functionality. The returned decorator updates a tqdm progress bar with a specified message before executing the wrapped function, then increments the progress bar upon completion.

## Args:
    fn (Callable): The function to wrap with progress bar functionality
    bar (tqdm): A tqdm progress bar instance to update
    message (str): Message to display in the progress bar's postfix

## Returns:
    Callable: A decorated version of the input function that updates the progress bar when invoked

## Raises:
    None explicitly raised - depends on the behavior of the wrapped function `fn`

## Constraints:
    Preconditions:
    - `bar` must be a valid tqdm progress bar instance
    - `message` must be a string
    - `fn` must be callable
    
    Postconditions:
    - The returned function behaves identically to `fn` except for progress bar updates
    - The progress bar is updated exactly once per function invocation

## Side Effects:
    - Modifies the state of the provided tqdm progress bar instance
    - Sets the progress bar's postfix string during execution
    - Increments the progress bar counter after function execution

## Control Flow:
```mermaid
flowchart TD
    A[progress() called] --> B{Create inner function}
    B --> C[Return inner function]
    C --> D[inner() called]
    D --> E[bar.set_postfix_str(message)]
    E --> F[fn(*args, **kwargs)]
    F --> G[bar.update()]
    G --> H[return ret]
```

## Examples:
```python
from tqdm import tqdm
from src.ydata_profiling.utils.progress_bar import progress

# Create a progress bar
bar = tqdm(total=100)

# Wrap a function with progress tracking
def process_item(item):
    # Some processing work
    return item * 2

wrapped_function = progress(process_item, bar, "Processing items")
result = wrapped_function(5)  # Progress bar shows "Processing items" and updates
```

