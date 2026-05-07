# `tracer.py`

## `pysnooper.tracer.get_local_reprs` · *function*

## Summary:
Creates ordered string representations of local variables from a Python execution frame for debugging purposes.

## Description:
Processes local variables from a Python frame object to generate human-readable string representations, maintaining a consistent variable ordering. This function is used by the pysnooper library to display variable states during function execution tracing. It handles both regular local variables and additional "watched" variables that provide extra monitoring capabilities.

## Args:
    frame (frame): Python frame object containing local variables to represent
    watch (tuple, optional): Additional variables to monitor, each item should be an object with an `items(frame, normalize)` method that returns key-value pairs for the frame. Defaults to empty tuple.
    custom_repr (tuple, optional): Custom representation functions to override default formatting for specific types. Defaults to empty tuple.
    max_length (int, optional): Maximum length for string representations. Defaults to None (no limit).
    normalize (bool, optional): Whether to normalize representations (e.g., for consistent comparison). Defaults to False.

## Returns:
    collections.OrderedDict: Ordered mapping of variable names to their string representations, sorted according to variable declaration order in the frame's code. The order follows: co_varnames, co_cellvars, co_freevars, then f_locals keys in declaration order.

## Raises:
    ValueError: If a variable name from f_locals is not found in the combined vars_order (which should not normally occur under normal Python execution).

## Constraints:
    Preconditions:
    - frame must be a valid Python frame object with proper f_code and f_locals attributes
    - watch elements must have an items(frame, normalize) method that returns iterable key-value pairs
    
    Postconditions:
    - Returns an OrderedDict with all local variables and watched variables
    - Variable ordering follows Python's declaration order in the frame's code
    - All returned values are string representations of the variables

## Side Effects:
    None directly observable from this function's interface.

## Control Flow:
```mermaid
flowchart TD
    A[Start get_local_reprs] --> B[Extract vars_order from frame.f_code]
    B --> C[Process f_locals into (name, repr) pairs]
    C --> D[Call utils.get_shortish_repr for each variable]
    D --> E[Sort result_items by vars_order.index(key)]
    E --> F[Create OrderedDict from sorted items]
    F --> G[Process watch variables]
    G --> H[Update OrderedDict with watched items]
    H --> I[Return OrderedDict]
```

## Examples:
    # Basic usage with a frame object
    result = get_local_reprs(current_frame)
    
    # Usage with watched variables
    watched = [SomeWatchedVariable()]
    result = get_local_reprs(current_frame, watch=watched)
```

## `pysnooper.tracer.UnavailableSource` · *class*

## Summary:
Represents a placeholder object that provides a constant "SOURCE IS UNAVAILABLE" message when source code cannot be accessed.

## Description:
The UnavailableSource class serves as a fallback mechanism when source code inspection fails or is not available. It implements the sequence protocol to always return a fixed message indicating source unavailability. This class is typically instantiated by the tracer when it encounters functions or code where source code cannot be retrieved, such as compiled bytecode or dynamically generated code.

## State:
This class has no instance attributes. It is a minimal placeholder class with no internal state.

## Lifecycle:
Creation: Instantiated automatically by the tracer when source code is unavailable. No explicit construction is required by users.
Usage: Accessed via indexing (e.g., `source[0]`) to retrieve the "SOURCE IS UNAVAILABLE" message.
Destruction: No special cleanup required as it's a simple placeholder class.

## Method Map:
```mermaid
graph TD
    A[Tracer] --> B[UnavailableSource()]
    B --> C[source[i] returns "SOURCE IS UNAVAILABLE"]
```

## Raises:
This class does not raise any exceptions under normal operation. The `__getitem__` method always returns a string and does not perform any error-prone operations.

## Example:
```python
# Typically used internally by the tracer
source = UnavailableSource()
message = source[0]  # Returns "SOURCE IS UNAVAILABLE"
```

### `pysnooper.tracer.UnavailableSource.__getitem__` · *method*

## Summary:
Returns a constant string indicating that source code is unavailable when indexed.

## Description:
This method implements the indexing protocol (`__getitem__`) for the `UnavailableSource` class. It serves as a fallback mechanism when source code cannot be retrieved or accessed during debugging operations. The method is called when attempting to access elements from an `UnavailableSource` instance using bracket notation (e.g., `source[i]`).

## Args:
    i (any): The index being accessed - this parameter is ignored as the method always returns the same constant value.

## Returns:
    str: The string 'SOURCE IS UNAVAILABLE' regardless of the index provided.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None - this method does not read any instance attributes.
    Attributes WRITTEN: None - this method does not modify any instance attributes.

## Constraints:
    Preconditions: None - the method accepts any argument and behaves consistently.
    Postconditions: Always returns the string 'SOURCE IS UNAVAILABLE'.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It's a pure function that only returns a constant value.

## `pysnooper.tracer.get_write_function` · *function*

## Summary:
Returns an appropriate write function based on the output destination specification.

## Description:
This function determines and returns the correct write function for logging tracing information based on the specified output destination. It supports writing to stderr, files, callable objects, or writable streams, with proper validation of overwrite behavior.

The function is extracted to centralize the logic for determining write destinations, enforcing clear responsibility boundaries between destination specification and actual writing operations.

## Args:
    output (None, str, PathLike, callable, or WritableStream): Specifies where to write output. 
        - None: Write to stderr
        - str or PathLike: Write to a file at the specified path
        - callable: Use the callable directly as the write function
        - WritableStream: Wrap the stream's write method
    overwrite (bool): When True, overwrites existing files. Only valid when output is a path-like object.

## Returns:
    callable: A write function that accepts a string argument and writes it to the determined destination.

## Raises:
    Exception: Raised when overwrite=True is specified but output is not a path-like object.

## Constraints:
    Preconditions:
        - If overwrite=True, then output must be a path-like object (str or PathLike)
        - output parameter must be one of the supported types
    
    Postconditions:
        - Always returns a callable write function
        - The returned function accepts a single string argument

## Side Effects:
    - When output is a file path, opens and potentially modifies files on disk
    - When output is None, writes to stderr stream
    - No other side effects

## Control Flow:
```mermaid
flowchart TD
    A[get_write_function] --> B{output is None?}
    B -- Yes --> C[Write to stderr]
    B -- No --> D{is_path?}
    D -- Yes --> E[Return FileWriter.write]
    D -- No --> F{callable(output)?}
    F -- Yes --> G[Use callable directly]
    F -- No --> H{isinstance(output, WritableStream)?}
    H -- Yes --> I[Wrap output.write]
    H -- No --> J[Assertion Error]
    C --> K[Return write function]
    E --> K
    G --> K
    I --> K
```

## Examples:
```python
# Write to stderr
write_func = get_write_function(None, False)
write_func("Tracing info\\n")

# Write to file with overwrite
write_func = get_write_function("/tmp/tracing.log", True)
write_func("Tracing info\\n")

# Write to custom callable
def my_writer(s):
    print(f"LOG: {s}")
write_func = get_write_function(my_writer, False)
write_func("Tracing info\\n")
```

## `pysnooper.tracer.FileWriter` · *class*

## Summary:
A file writer that handles writing content to files with overwrite or append behavior.

## Description:
The FileWriter class provides a simple interface for writing string content to files. It maintains an internal state to control whether subsequent writes should overwrite existing content or append to it. This class is typically used by the pysnooper library to log tracing information to files.

## State:
- path (str): The file path where content will be written. Converted to text type for compatibility.
- overwrite (bool): Flag indicating whether to overwrite the file ('w') or append to it ('a'). Set to False after each write operation.

## Lifecycle:
- Creation: Instantiate with a file path and overwrite boolean flag
- Usage: Call write() method with string content to write to the file
- Destruction: No explicit cleanup required; relies on Python's file handling mechanisms

## Method Map:
```mermaid
graph TD
    A[FileWriter.__init__] --> B[FileWriter.write]
    B --> C[open(file, 'w'/'a', encoding='utf-8')]
    C --> D[output_file.write(s)]
    D --> E[overwrite = False]
```

## Raises:
- None explicitly raised by __init__
- May raise standard file I/O exceptions during write operations (FileNotFoundError, PermissionError, etc.)

## Example:
```python
# Create a FileWriter that overwrites the file
writer = FileWriter('/tmp/log.txt', overwrite=True)
writer.write('First line\\n')

# Subsequent writes will append
writer = FileWriter('/tmp/log.txt', overwrite=False)
writer.write('Second line\\n')
```

### `pysnooper.tracer.FileWriter.__init__` · *method*

## Summary:
Initializes a FileWriter instance with a file path and overwrite configuration.

## Description:
Configures a FileWriter object to manage output to a specified file path. The overwrite flag determines whether subsequent write operations will overwrite existing content or append to it. This method prepares the object for file I/O operations by storing the path and overwrite settings.

## Args:
    path (str): The file path where output will be written. May be a string or other type convertible to text.
    overwrite (bool): Flag indicating whether to overwrite existing file content (True) or append to it (False).

## Returns:
    None: This method initializes the object's state and returns no value.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying type conversion may raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.path: Stores the path as a text type representation
        - self.overwrite: Stores the overwrite flag value

## Constraints:
    Preconditions:
        - The path parameter should be convertible to a text type
        - The overwrite parameter should be a boolean value
    Postconditions:
        - self.path contains the text representation of the provided path
        - self.overwrite contains the provided overwrite flag value

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only stores the provided parameters in object attributes.

### `pysnooper.tracer.FileWriter.write` · *method*

*No documentation generated.*

## `pysnooper.tracer.Tracer` · *class*

*No documentation generated.*

### `pysnooper.tracer.Tracer.__init__` · *method*

## Summary:
Initializes a Tracer instance with configuration options for code tracing and variable monitoring.

## Description:
Configures the Tracer object with various settings that control how code execution is traced and variables are monitored. This constructor sets up internal state management, variable watching mechanisms, and output handling for the tracing functionality.

## Args:
    output (None, str, PathLike, callable, or WritableStream, optional): Specifies where to write tracing output. Defaults to None (stderr).
    watch (tuple, optional): Tuple of variable names or expressions to monitor during tracing. Defaults to ().
    watch_explode (tuple, optional): Tuple of variable names or expressions to monitor with deep inspection. Defaults to ().
    depth (int, optional): Maximum frame depth to trace. Defaults to 1.
    prefix (str, optional): Prefix string added to each tracing line. Defaults to ''.
    overwrite (bool, optional): Whether to overwrite existing output files. Defaults to False.
    thread_info (bool, optional): Whether to include thread information in traces. Defaults to False.
    custom_repr (tuple, optional): Custom representation functions for specific types. Defaults to ().
    max_variable_length (int, optional): Maximum length of variable representations. Defaults to 100.
    normalize (bool, optional): Whether to normalize line endings in output. Defaults to False.
    relative_time (bool, optional): Whether to show relative timestamps. Defaults to False.
    color (bool, optional): Whether to use colored output. Defaults to True.

## Returns:
    None: This method initializes the object's state and returns nothing.

## Raises:
    AssertionError: When depth is less than 1.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._write: Write function for output
        - self.watch: List of watched variables
        - self.frame_to_local_reprs: Dictionary mapping frames to local variable representations
        - self.start_times: Dictionary tracking start times for frames
        - self.depth: Frame depth limit
        - self.prefix: Output prefix string
        - self.thread_info: Thread information flag
        - self.thread_info_padding: Thread information padding value
        - self.target_codes: Set of target code objects
        - self.target_frames: Set of target frame objects
        - self.thread_local: Thread-local storage
        - self.custom_repr: Custom representation functions
        - self.last_source_path: Last source file path
        - self.max_variable_length: Maximum variable representation length
        - self.normalize: Normalization flag
        - self.relative_time: Relative time flag
        - self.color: Color output flag
        - self._FOREGROUND_* and self._STYLE_*: Color formatting constants (conditionally set)

## Constraints:
    Preconditions:
        - depth must be >= 1
        - output parameter must be one of the supported types (None, str, PathLike, callable, or WritableStream)
        - If overwrite=True, then output must be a path-like object (str or PathLike)
    
    Postconditions:
        - All internal state attributes are properly initialized
        - self._write is assigned a valid write function
        - self.watch contains properly wrapped variable objects
        - self.depth is guaranteed to be >= 1 due to assertion

## Side Effects:
    - May open and modify files on disk if output specifies a file path
    - May write to stderr if output is None
    - Sets up color formatting constants based on platform support

### `pysnooper.tracer.Tracer.__call__` · *method*

*No documentation generated.*

### `pysnooper.tracer.Tracer._wrap_class` · *method*

## Summary:
Wraps all regular functions in a class with tracing functionality while preserving coroutine functions unchanged.

## Description:
This method iterates through all attributes of a given class and wraps any regular functions with the tracer's wrapping mechanism. It specifically excludes coroutine functions and generator functions to avoid conflicts with the tracing system. This method is typically called internally by the Tracer's `__call__` method when a class is decorated with the tracer.

## Args:
    cls (type): The class whose methods need to be wrapped with tracing functionality

## Returns:
    type: The same class with its regular functions wrapped for tracing

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The input must be a valid Python class object
    - The class should have attributes that can be inspected via `__dict__`
    
    Postconditions:
    - All regular functions in the class are replaced with traced versions
    - Coroutine functions remain unchanged
    - Generator functions are handled specially (though not implemented in this method)
    - The returned class is identical to the input class but with wrapped methods

## Side Effects:
    None directly observable from this method. However, the wrapped functions will produce tracing output when called.

### `pysnooper.tracer.Tracer._wrap_function` · *method*

## Summary:
Wraps a function to enable detailed tracing of its execution, handling different function types including generators, coroutines, and regular functions.

## Description:
This method creates a wrapper around the provided function that enables detailed tracing of its execution. It determines the appropriate wrapper type based on the function's characteristics and returns the wrapped version. The wrapper ensures that when the function is called, the Tracer's context manager is activated to monitor variable changes, execution flow, and performance metrics.

The method is called internally by the Tracer's `__call__` method when wrapping individual functions. It serves as the core mechanism for enabling tracing on any callable object, with special handling for different Python function types.

## Args:
    function (callable): The function to be wrapped for tracing. Can be a regular function, generator function, coroutine function, or async generator function.

## Returns:
    callable: A wrapped version of the input function that enables tracing when executed. The returned wrapper will be either a simple wrapper for regular functions or a generator wrapper for generator functions.

## Raises:
    NotImplementedError: Raised when attempting to wrap coroutine functions or async generator functions, as these are not currently supported by the tracing mechanism.

## State Changes:
    Attributes READ:
        - self.target_codes: Set containing code objects of traced functions
    
    Attributes WRITTEN:
        - self.target_codes: Adds the input function's code object to this set for tracking

## Constraints:
    Preconditions:
        - The input function must be callable
        - The Tracer instance must be properly initialized
        - The function must not be a coroutine or async generator function (these raise NotImplementedError)
    
    Postconditions:
        - The function's code object is added to self.target_codes for tracing identification
        - The returned wrapper function maintains the original function's signature and behavior
        - Generator functions are wrapped with a special generator-aware wrapper that preserves tracing at yield points

## Side Effects:
    - Adds the function's code object to the tracer's target codes set for identification during tracing
    - No direct I/O operations or external service calls
    - The wrapper function will activate the Tracer's context manager when called, which may result in:
      * Setting sys.settrace() to enable execution tracing
      * Writing trace information to the configured output destination
      * Modifying thread-local storage for tracking

### `pysnooper.tracer.Tracer.write` · *method*

## Summary:
Formats and writes a string message with the tracer's prefix and newline to the configured output destination.

## Description:
The write method is responsible for formatting log messages with the tracer's prefix and appending a newline character before delegating the actual writing to the internal `_write` function. This method serves as a centralized formatting point for all tracing output, ensuring consistent message structure across the tracer's logging system.

This method is called internally by various tracing operations including variable tracking, source path logging, execution timing, return values, and exception reporting. It's designed to be a thin wrapper around the underlying write function that adds consistent formatting.

## Args:
    s (str): The string message to be written. This is typically a formatted tracing message that will be prefixed and newline-appended.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions. Exceptions from the underlying `_write` function are propagated.

## State Changes:
    Attributes READ:
        - self.prefix: The prefix string to prepend to the message
        - self._write: The underlying write function that actually outputs the formatted message
    
    Attributes WRITTEN:
        - None: This method doesn't modify any attributes of the Tracer instance itself.

## Constraints:
    Preconditions:
        - The Tracer instance must be properly initialized with a valid `_write` function
        - The `prefix` attribute must be a string or convertible to string
        - The input string `s` should be a valid string
    
    Postconditions:
        - The formatted string (prefix + s + newline) is written to the configured output destination
        - The method completes without modifying the Tracer's internal state

## Side Effects:
    - Writes formatted text to the configured output destination (stderr, file, or custom writer)
    - May cause file I/O operations when writing to files
    - May cause console output when writing to stderr
    - May invoke custom callable when the output destination is a callable object

### `pysnooper.tracer.Tracer.__enter__` · *method*

*No documentation generated.*

### `pysnooper.tracer.Tracer.__exit__` · *method*

## Summary:
Exits a tracing context and records the elapsed execution time for the traced operation.

## Description:
This method is the `__exit__` hook of the Tracer context manager. It is automatically called when exiting a `with` statement block that uses the tracer. It restores the previous tracing function from the thread's trace stack, cleans up tracking data for the current execution frame, and logs the total execution time of the traced operation.

The method is part of the context manager protocol and ensures proper cleanup of tracing resources while providing timing information about the traced code execution. When the tracer is disabled (DISABLED flag is True), the method returns early without performing any tracing operations.

## Args:
    exc_type (type or None): Exception type if an exception occurred in the context, otherwise None
    exc_value (Exception or None): Exception instance if an exception occurred in the context, otherwise None  
    exc_traceback (traceback or None): Traceback if an exception occurred in the context, otherwise None

## Returns:
    None: This method returns None, allowing normal exception propagation in the context manager. In the special case where DISABLED is True, it returns early without performing any tracing operations.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ:
        - self.thread_local.original_trace_functions: Stack of previous trace functions
        - self.start_times: Maps frames to their start timestamps
        - self._FOREGROUND_YELLOW, self._STYLE_DIM, self._STYLE_NORMAL, self._STYLE_RESET_ALL: Color formatting constants
        - thread_global.depth: Current nesting depth of traced calls
    
    Attributes WRITTEN:
        - self.thread_local.original_trace_functions: Pops the most recent trace function from the stack
        - self.target_frames: Removes the calling frame from the set of tracked frames
        - self.frame_to_local_reprs: Removes tracking data for the calling frame
        - self.start_times: Removes the start time for the calling frame

## Constraints:
    Preconditions:
        - Must be called as part of a context manager exit sequence (`with` statement)
        - The calling frame must be tracked by the tracer (present in self.target_frames)
        - The tracer must not be disabled (DISABLED flag check)
    
    Postconditions:
        - The previous tracing function is restored in the thread's trace stack
        - Tracking data for the current frame is cleaned up
        - Execution time is logged to the configured output destination
        - Thread global depth counter is decremented appropriately

## Side Effects:
    - Writes formatted timing information to the configured output destination via self.write()
    - Modifies the thread's tracing function stack by popping the most recent trace function
    - May modify thread-global depth counter
    - Accesses and modifies thread-local storage

### `pysnooper.tracer.Tracer._is_internal_frame` · *method*

## Summary:
Determines whether a given frame represents internal tracer implementation code rather than user code.

## Description:
This method checks if a frame's source file matches the source file of the Tracer.__enter__ method. It's used to filter out internal implementation frames from being traced, ensuring that only user code appears in the trace output. This prevents the tracer from logging its own internal operations, keeping the trace clean and focused on the actual program execution.

The method is called from two key locations:
1. In `__enter__` method to determine if the calling frame should be traced
2. In `trace` method to skip internal frames when depth > 1

## Args:
    frame (FrameType): A Python frame object to check

## Returns:
    bool: True if the frame represents internal tracer code (same filename as Tracer.__enter__), False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The frame parameter must be a valid Python frame object with a f_code attribute containing co_filename
    Postconditions: Returns a boolean value indicating whether the frame is internal to the tracer

## Side Effects:
    None

### `pysnooper.tracer.Tracer.set_thread_info_padding` · *method*

## Summary
Updates the thread information padding to ensure consistent column width formatting for thread identifiers in tracing output.

## Description
This method manages the padding width for thread information displayed in pysnooper's trace output. When thread information is enabled via the `thread_info` parameter, this method ensures that all thread identifiers are displayed with consistent width by tracking the maximum length encountered and left-justifying subsequent entries to that width.

The method is called internally by the tracer's `trace` method when processing trace events and thread information needs to be formatted for display.

## Args
    thread_info (str): Thread identifier string in the format "{ident}-{name} " where ident is the thread ID and name is the thread name.

## Returns
    str: The input thread_info string left-justified to the current maximum padding width.

## Raises
    None explicitly raised

## State Changes
    Attributes READ: self.thread_info_padding
    Attributes WRITTEN: self.thread_info_padding

## Constraints
    Preconditions: 
    - The method assumes `thread_info` is a string
    - The method assumes `self.thread_info_padding` is initialized to 0 in `__init__`
    
    Postconditions:
    - `self.thread_info_padding` is updated to be at least the length of `thread_info`
    - The returned string is left-justified to the current padding width

## Side Effects
    None

### `pysnooper.tracer.Tracer.trace` · *method*

*No documentation generated.*

