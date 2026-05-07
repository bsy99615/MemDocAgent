# `tracer.py`

## `pysnooper.tracer.get_local_reprs` · *function*

*No documentation generated.*

## `pysnooper.tracer.UnavailableSource` · *class*

*No documentation generated.*

### `pysnooper.tracer.UnavailableSource.__getitem__` · *method*

## Summary:
Returns a constant string indicating that source code is unavailable for inspection.

## Description:
This method serves as a fallback implementation when source code cannot be retrieved for a function or code object. It provides a consistent response indicating the unavailability of source code, which is useful for debugging and tracing purposes when the original source is not accessible.

## Args:
    i (int): The index being accessed (ignored in implementation)

## Returns:
    str: The literal string 'SOURCE IS UNAVAILABLE'

## Raises:
    None: This method does not raise any exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the same string value

## Side Effects:
    None: This method performs no I/O operations or external service calls

## `pysnooper.tracer.get_path_and_source_from_frame` · *function*

*No documentation generated.*

## `pysnooper.tracer.get_write_function` · *function*

*No documentation generated.*

## `pysnooper.tracer.FileWriter` · *class*

*No documentation generated.*

### `pysnooper.tracer.FileWriter.__init__` · *method*

*No documentation generated.*

### `pysnooper.tracer.FileWriter.write` · *method*

## Summary:
Writes a string to the file specified by the instance's path attribute, using either write or append mode based on the overwrite flag.

## Description:
This method performs file I/O operations to write the provided string content to a file. It determines the file mode ('w' for overwrite or 'a' for append) based on the instance's `overwrite` attribute. After writing, it resets the overwrite flag to False to prevent unintended overwrites in subsequent writes.

## Args:
    s (str): The string content to write to the file.

## Returns:
    None: This method does not return any value.

## Raises:
    IOError: If the file cannot be opened or written to due to permission issues, invalid paths, or other I/O errors.

## State Changes:
    Attributes READ: self.path, self.overwrite
    Attributes WRITTEN: self.overwrite

## Constraints:
    Preconditions: 
    - The instance must have been initialized with a valid file path
    - The `s` parameter must be a string
    - The file system must allow writing to the specified path
    
    Postconditions:
    - The string content is written to the file at self.path
    - The self.overwrite attribute is set to False regardless of initial value

## Side Effects:
    - Performs file I/O operations that may cause disk access
    - May modify the file content at self.path depending on the overwrite flag
    - Could raise IOError if file operations fail

## `pysnooper.tracer.Tracer` · *class*

*No documentation generated.*

### `pysnooper.tracer.Tracer.__init__` · *method*

*No documentation generated.*

### `pysnooper.tracer.Tracer.__call__` · *method*

*No documentation generated.*

### `pysnooper.tracer.Tracer._wrap_class` · *method*

## Summary:
Wraps all regular functions in a class with tracing functionality while skipping coroutine functions.

## Description:
This method processes all attributes of a given class and wraps any regular Python functions with the tracer's wrapping mechanism. It's used internally by the Tracer class when decorating entire classes rather than individual functions. The method preserves the original class structure while enhancing its methods with detailed execution tracing capabilities.

## Args:
    cls (type): The class whose methods need to be wrapped with tracing functionality

## Returns:
    type: The same class with its regular methods wrapped for tracing

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input must be a valid Python class object
    Postconditions: All regular functions in the class are replaced with traced versions, while coroutine functions are left unchanged

## Side Effects:
    Mutates the input class in-place by replacing function attributes with their traced counterparts

### `pysnooper.tracer.Tracer._wrap_function` · *method*

## Summary:
Wraps a function with tracing capabilities, returning either a simple wrapper for regular functions or a generator wrapper for generator functions.

## Description:
This method is responsible for creating traced versions of functions. When a function is decorated with the tracer, this method is called to wrap it appropriately. The wrapper ensures that whenever the function is called, the tracer's context manager (`with self:`) is activated to capture execution details.

## Args:
    function (callable): The function to be wrapped with tracing capabilities

## Returns:
    callable: A wrapped version of the input function that enables tracing when called

## Raises:
    NotImplementedError: When attempting to wrap coroutine functions or async generator functions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.target_codes (adds function.__code__ to the set)

## Constraints:
    Preconditions: The input must be a callable function
    Postconditions: The returned function behaves identically to the input function but with tracing enabled

## Side Effects:
    I/O: Writes tracing information to the configured output destination via self.write()
    Mutations: Adds the function's code object to self.target_codes set

### `pysnooper.tracer.Tracer.write` · *method*

## Summary:
Formats and writes a string message with prefix and newline to the output destination.

## Description:
This method takes a string message and prepends the tracer's prefix followed by a newline character before passing it to the internal `_write` method for actual output. The formatted string is constructed using string formatting with the instance's prefix attribute.

## Args:
    s (str): The string message to be written, which will be prefixed and formatted with a trailing newline.

## Returns:
    None: This method does not return any value.

## Raises:
    Exception: May raise exceptions propagated from the underlying `_write` method implementation.

## State Changes:
    Attributes READ: self.prefix
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `self.prefix` attribute must be defined and accessible; the `self._write` method must be callable.
    Postconditions: The formatted string (prefix + message + newline) is passed to the `_write` method for output processing.

## Side Effects:
    I/O operations: Writes formatted string to the configured output destination through the `_write` method.

### `pysnooper.tracer.Tracer.__enter__` · *method*

*No documentation generated.*

### `pysnooper.tracer.Tracer.__exit__` · *method*

*No documentation generated.*

### `pysnooper.tracer.Tracer._is_internal_frame` · *method*

## Summary:
Determines whether a given frame corresponds to the tracer's internal implementation code rather than user code being traced.

## Description:
This method serves as a utility to identify internal frames within the pysnooper tracer's execution flow. It compares the filename of the provided frame with the filename of the Tracer.__enter__ method's code to distinguish between user code and tracer-internal code. This distinction is crucial for proper tracing behavior, ensuring that the tracer doesn't interfere with its own operation while tracing user code.

The method is called during the setup phase (`__enter__`) and during active tracing (`trace`) to filter out internal frames from the tracing process, particularly when dealing with nested tracing or when the tracing depth exceeds 1.

## Args:
    frame (FrameType): A Python frame object representing the execution context to be checked

## Returns:
    bool: True if the frame's code file matches the Tracer.__enter__ method's code file, indicating it's an internal frame; False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The frame parameter must be a valid Python frame object (not None)
    - The frame's f_code attribute must be accessible
    
    Postconditions:
    - Returns a boolean value indicating internal vs external frame status
    - Does not modify any instance state

## Side Effects:
    None - This is a pure utility method that only performs comparisons and returns a boolean value

### `pysnooper.tracer.Tracer.set_thread_info_padding` · *method*

## Summary:
Updates the thread info padding to accommodate the longest thread identifier encountered and returns the thread info string left-justified to that padding width.

## Description:
This method is responsible for maintaining consistent column widths when displaying thread information in the tracing output. It ensures that thread identifiers of varying lengths are properly aligned by tracking the maximum length seen so far and applying left-justification to all thread info strings.

The method is called internally by the tracer when thread information is being displayed, specifically in the `trace` method when `self.thread_info` is enabled.

## Args:
    thread_info (str): Thread identification information string to process

## Returns:
    str: The input thread_info string left-justified to the current maximum padding width

## Raises:
    None

## State Changes:
    Attributes READ: self.thread_info_padding
    Attributes WRITTEN: self.thread_info_padding

## Constraints:
    Preconditions: The method assumes thread_info is a string
    Postconditions: self.thread_info_padding is updated to be at least the length of thread_info, and the returned string is left-justified to this padding width

## Side Effects:
    None

### `pysnooper.tracer.Tracer.trace` · *method*

*No documentation generated.*

