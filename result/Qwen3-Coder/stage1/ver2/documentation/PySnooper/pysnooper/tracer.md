# `tracer.py`

## `pysnooper.tracer.get_local_reprs` · *function*

## Summary:
Generates formatted string representations of local variables in a frame, sorted according to variable declaration order, with support for watched variables.

## Description:
Processes the local variables from a Python frame object and creates human-readable string representations for debugging purposes. The function organizes variables in the order they appear in the code (including varnames, cellvars, freevars, and locals) and applies custom formatting rules. It also supports watching additional variables beyond the frame's locals.

This function is extracted into its own component to separate the logic of variable representation and ordering from the higher-level tracing mechanisms, making it reusable and testable. The separation allows the tracing system to focus on instrumentation while delegating the complex task of variable formatting to this dedicated function.

## Args:
    frame (FrameType): The Python frame object containing local variables to represent
    watch (tuple, optional): Additional variables to watch and include in results. Each element must have an items() method that accepts (frame, normalize) arguments. Defaults to empty tuple.
    custom_repr (tuple, optional): Custom representation rules as (condition, action) pairs for get_shortish_repr function. Defaults to empty tuple.
    max_length (int, optional): Maximum length for string representations passed to get_shortish_repr. If None, no truncation occurs. Defaults to None.
    normalize (bool): Whether to normalize representations to remove memory addresses and similar artifacts, passed to get_shortish_repr. Defaults to False.

## Returns:
    collections.OrderedDict: An ordered dictionary mapping variable names to their string representations, sorted by declaration order as determined by the frame's code attributes and local variables.

## Raises:
    None explicitly raised

## Constraints:
    - Precondition: frame must be a valid Python frame object with f_code and f_locals attributes
    - Precondition: watch elements must have an items() method that accepts (frame, normalize) arguments
    - Precondition: custom_repr must be iterable containing (condition, action) pairs
    - Postcondition: The returned OrderedDict maintains the order of variables as defined in the frame's code attributes (co_varnames, co_cellvars, co_freevars) plus frame.f_locals keys
    - Postcondition: All variables from frame.f_locals are included in the result
    - Postcondition: Variables from watch are added to the result via update() operation

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_local_reprs] --> B[Extract code info from frame]
    B --> C[Build vars_order sequence]
    C --> D[Process frame.f_locals items]
    D --> E[Apply get_shortish_repr to each value]
    E --> F[Sort result_items by vars_order index]
    F --> G[Create OrderedDict from sorted items]
    G --> H{watch variables provided?}
    H -- Yes --> I[Iterate through watch variables]
    I --> J[Call variable.items(frame, normalize) for each]
    J --> K[Update OrderedDict with sorted results]
    K --> L[Return OrderedDict]
    H -- No --> L[Return OrderedDict]
```

## Examples:
    # Basic usage with frame object
    import inspect
    def example_func():
        x = 42
        y = "hello"
        frame = inspect.currentframe()
        result = get_local_reprs(frame)
        # Returns OrderedDict with 'x': '42', 'y': "'hello'" sorted by declaration order
    
    # Usage with watched variables
    from variables import BaseVariable
    def example_with_watch():
        a = [1, 2, 3]
        b = {"key": "value"}
        frame = inspect.currentframe()
        watch_vars = [BaseVariable('a')]
        result = get_local_reprs(frame, watch=watch_vars)
        # Returns OrderedDict including both local variables and watched variables

## `pysnooper.tracer.UnavailableSource` · *class*

## Summary:
Represents a sentinel object that provides a constant "SOURCE IS UNAVAILABLE" message when accessed via indexing.

## Description:
The UnavailableSource class serves as a placeholder object used when source code cannot be retrieved or is unavailable. It implements the `__getitem__` method to always return the string "SOURCE IS UNAVAILABLE", regardless of the index requested. This class is typically used in debugging contexts where source code inspection fails or is not possible.

## State:
- No instance attributes maintained
- The class itself has no state beyond its method implementation
- `__getitem__` method accepts any index parameter but ignores it

## Lifecycle:
- Creation: Instantiated as a singleton or inline object
- Usage: Accessed via bracket notation (e.g., `source_obj[index]`) 
- Destruction: Standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[UnavailableSource] --> B{__getitem__(i)}
    B --> C["Returns 'SOURCE IS UNAVAILABLE'"]
```

## Raises:
- No exceptions are raised by this class
- The `__getitem__` method is designed to be fault-tolerant and always return a string

## Example:
```python
# Create instance
source = UnavailableSource()

# Access via indexing (any index works)
result = source[0]  # Returns 'SOURCE IS UNAVAILABLE'
result = source[5]  # Returns 'SOURCE IS UNAVAILABLE'
result = source['anything']  # Returns 'SOURCE IS UNAVAILABLE'
```

### `pysnooper.tracer.UnavailableSource.__getitem__` · *method*

## Summary:
Returns a constant string indicating that source code is unavailable for inspection.

## Description:
This method serves as a fallback implementation when source code cannot be accessed or retrieved. It provides a consistent response indicating the unavailability of source code, which is particularly useful in debugging contexts where source code inspection is attempted but fails. This method is part of the UnavailableSource class, which acts as a sentinel object representing situations where source code is not accessible.

## Args:
    i (int): Index parameter for item access, though its value is irrelevant as the method always returns the same constant string.

## Returns:
    str: The string 'SOURCE IS UNAVAILABLE' regardless of the index parameter.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None - this method does not read any instance attributes.
    Attributes WRITTEN: None - this method does not modify any instance attributes.

## Constraints:
    Preconditions: None - the method accepts any integer index.
    Postconditions: Always returns the string 'SOURCE IS UNAVAILABLE'.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It's a pure function that returns a constant value.

## `pysnooper.tracer.get_path_and_source_from_frame` · *function*

## Summary:
Retrieves the file path and source code lines from a Python frame object, handling various execution environments including regular files, IPython notebooks, and Ansible archives.

## Description:
Extracts file path and source code from a Python frame object, implementing a multi-layered approach to source retrieval. This function serves as a utility for debugging tools to obtain source code information regardless of execution context. It first checks a cache for previously retrieved source, then attempts to load source via module loaders, handles special notebook environments (IPython), Ansible archives, and finally falls back to reading from disk.

This logic is extracted into its own function to encapsulate the complex source resolution logic and avoid duplication elsewhere in the codebase, enforcing a clear boundary between frame analysis and source retrieval.

## Args:
    frame (types.FrameType): A Python frame object containing execution context information

## Returns:
    tuple: A tuple containing (file_path, source_lines) where:
        - file_path (str): The absolute path to the source file
        - source_lines (list[str] or UnavailableSource): List of source code lines or UnavailableSource marker if source cannot be retrieved

## Raises:
    None explicitly raised - exceptions are caught internally and handled gracefully

## Constraints:
    Preconditions:
        - frame must be a valid Python frame object
        - frame.f_globals must be accessible
        - frame.f_code.co_filename must be accessible
    
    Postconditions:
        - Returns a tuple with file path and source lines
        - If source cannot be retrieved, returns UnavailableSource marker
        - Cache is updated with retrieved source for future calls

## Side Effects:
    - Reads from filesystem when source is not cached
    - Accesses IPython history manager when processing IPython notebook cells
    - Reads from ZIP archives when processing Ansible files
    - Updates global source_and_path_cache dictionary

## Control Flow:
```mermaid
flowchart TD
    A[Start: get_path_and_source_from_frame] --> B{Cache Hit?}
    B -- Yes --> C[Return cached result]
    B -- No --> D[Get module loader]
    D --> E{Loader has get_source?}
    E -- Yes --> F[Call loader.get_source()]
    F --> G{Source retrieved?}
    G -- Yes --> H[Split source into lines]
    G -- No --> I[Check IPython filename pattern]
    I --> J{Matches IPython pattern?}
    J -- Yes --> K[Access IPython history]
    K --> L[Get source chunk]
    L --> M[Split into lines]
    J -- No --> N[Check Ansible filename pattern]
    N --> O{Matches Ansible pattern?}
    O -- Yes --> P[Open ZIP archive]
    P --> Q[Read source file]
    Q --> R[Split into lines]
    O -- No --> S[Open file with open()]
    S --> T{File opened successfully?}
    T -- No --> U[Set source to UnavailableSource]
    T -- Yes --> V[Read file content]
    V --> W[Split into lines]
    U --> X[Set source to UnavailableSource]
    X --> Y[Process encoding if needed]
    Y --> Z[Cache result]
    Z --> AA[Return (file_name, source)]
```

## Examples:
    # Typical usage in a debugger context
    import inspect
    frame = inspect.currentframe()
    file_path, source_lines = get_path_and_source_from_frame(frame)
    
    # When source is available
    # Returns: ('/path/to/file.py', ['line1', 'line2', ...])
    
    # When source cannot be retrieved
    # Returns: ('/path/to/file.py', UnavailableSource())

## `pysnooper.tracer.get_write_function` · *function*

## Summary
Returns an appropriate write function based on the output parameter configuration for logging tracing information.

## Description
This factory function creates and returns a write function tailored to the specified output destination. It handles multiple output types including stderr, file paths, callable objects, and writable streams. The function ensures proper validation of parameters and provides fallback mechanisms for handling encoding issues.

The logic is extracted into its own function to separate the concerns of output destination determination from the actual writing process, making the tracer more modular and testable.

## Args
- output: Can be None, a string/path-like object, a callable, or a writable stream object
  - When None, writes to stderr
  - When string/path-like, treats as file path for file-based writing
  - When callable, uses as the write function directly
  - When writable stream, uses its write method
- overwrite: Boolean flag indicating whether to overwrite existing files (default: False)
  - Only valid when output is a file path/string
  - Must be False when output is None or a callable/writable stream

## Returns
- A write function that accepts a string parameter and writes it to the configured destination
- The returned function has the signature: write(s: str) -> None

## Raises
- Exception: Raised when overwrite=True is specified with a non-path output type
  - Trigger condition: overwrite=True and not isinstance(output, (pycompat.PathLike, str))

## Constraints
- Preconditions:
  - If overwrite=True, output must be a path-like object or string
  - output parameter must be one of: None, str, PathLike, callable, or WritableStream
- Postconditions:
  - Always returns a callable write function
  - Returned function accepts a single string argument

## Side Effects
- When output is a file path: Creates or modifies files on disk
- When output is None: Writes to standard error stream (sys.stderr)
- No other side effects beyond the intended write operations

## Control Flow
```mermaid
flowchart TD
    A[get_write_function called] --> B{output is None?}
    B -- Yes --> C[Define stderr write function]
    B -- No --> D{is_path = isinstance(output, (PathLike,str))?}
    D -- Yes --> E[Create FileWriter(output, overwrite).write]
    D -- No --> F{callable(output)?}
    F -- Yes --> G[write = output]
    F -- No --> H{isinstance(output, WritableStream)?}
    H -- Yes --> I[Define write function using output.write]
    H -- No --> J[Assertion Error]
    C --> K[Return write function]
    E --> K
    G --> K
    I --> K
```

## Examples
```python
# Write to stderr
write_func = get_write_function(None, False)
write_func("Tracing info\n")

# Write to file with overwrite
write_func = get_write_function("/tmp/tracing.log", True)
write_func("Tracing info\n")

# Write using custom callable
def custom_writer(s):
    print(f"LOG: {s}")
write_func = get_write_function(custom_writer, False)
write_func("Tracing info\n")

# Write to writable stream
import sys
write_func = get_write_function(sys.stdout, False)
write_func("Tracing info\n")
```

## `pysnooper.tracer.FileWriter` · *class*

## Summary:
A file writer class that handles writing content to files with overwrite or append behavior.

## Description:
The FileWriter class provides a simple interface for writing text content to files. It supports both overwriting existing files and appending to them based on the overwrite flag. This class is typically used by the pysnooper library to log tracing information to files.

## State:
- path (str): The file path where content will be written. Converted to text type for compatibility.
- overwrite (bool): Flag indicating whether to overwrite (True) or append (False) to the file.

## Lifecycle:
- Creation: Instantiate with a file path and overwrite boolean flag
- Usage: Call write() method to write content to the file
- Destruction: No explicit cleanup required; relies on Python's file handling

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
- May raise standard file I/O exceptions during write operation (FileNotFoundError, PermissionError, etc.)

## Example:
```python
# Create a FileWriter that overwrites the file
writer = FileWriter('/path/to/log.txt', overwrite=True)
writer.write('First line of log\n')

# Create a FileWriter that appends to the file  
writer = FileWriter('/path/to/log.txt', overwrite=False)
writer.write('Second line of log\n')
```

### `pysnooper.tracer.FileWriter.__init__` · *method*

## Summary:
Initializes a FileWriter instance with a file path and overwrite flag.

## Description:
Configures the FileWriter object to manage file operations with the specified path and overwrite behavior. This method prepares the object's internal state for subsequent write operations.

## Args:
    path (str): The file path to write to. Converted to text type for cross-version compatibility.
    overwrite (bool): Flag indicating whether to overwrite existing file content (True) or append to it (False).

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.path: Stores the normalized file path
    - self.overwrite: Stores the overwrite flag

## Constraints:
    Preconditions:
    - path should be a valid file path string
    - overwrite should be a boolean value
    
    Postconditions:
    - self.path contains the normalized file path
    - self.overwrite contains the provided overwrite flag

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

### `pysnooper.tracer.FileWriter.write` · *method*

## Summary:
Writes a string to the configured file path, either truncating or appending based on the overwrite flag.

## Description:
Writes the provided string content to the file specified by self.path. The method determines the file operation mode ('w' for overwrite or 'a' for append) based on the self.overwrite flag. After writing, it resets the overwrite flag to prevent unintended overwrites in subsequent write operations. This method is typically called during the tracing process to record execution information to a log file.

## Args:
    s (str): The string content to write to the file. This is usually trace information or debugging output.

## Returns:
    None: This method performs file I/O operations and does not return a value.

## Raises:
    IOError: When the file cannot be opened or written to due to permission issues, invalid paths, or disk full conditions.

## State Changes:
    Attributes READ: 
    - self.path: Used to determine the target file location
    - self.overwrite: Used to determine the file operation mode ('w' or 'a')
    
    Attributes WRITTEN:
    - self.overwrite: Set to False after writing to prevent subsequent overwrites

## Constraints:
    Preconditions:
    - self.path must be a valid file path string
    - self.overwrite must be a boolean value
    - The file system must allow writing to the specified path
    
    Postconditions:
    - The string s is written to the file at self.path
    - self.overwrite is set to False regardless of initial value

## Side Effects:
    I/O operations: Writes to the filesystem at the path specified by self.path. May cause disk I/O performance impact during high-frequency tracing.

## `pysnooper.tracer.Tracer` · *class*

*No documentation generated.*

### `pysnooper.tracer.Tracer.__init__` · *method*

## Summary
Initializes a Tracer instance with configuration options and internal state for code tracing functionality.

## Description
Configures the Tracer object with user-specified settings and initializes internal data structures needed for tracking function execution. This method serves as the primary constructor that establishes the tracing environment, including output handling, watched variables, and platform-specific configurations.

The initialization process separates concerns by:
- Setting up the output mechanism via get_write_function
- Processing watch parameters into appropriate variable representations
- Configuring platform-specific features like color support
- Establishing internal tracking structures for function execution

## Args
- output (Optional[str, callable, object]): Output destination for tracing information. Can be None (stderr), file path string, callable, or writable stream. Default is None.
- watch (tuple): Tuple of variables to watch during tracing. Default is empty tuple.
- watch_explode (tuple): Tuple of variables to watch with deep inspection. Default is empty tuple.
- depth (int): Maximum frame depth to trace. Must be >= 1. Default is 1.
- prefix (str): Prefix string added to each traced line. Default is empty string.
- overwrite (bool): Whether to overwrite existing files when output is a file path. Default is False.
- thread_info (bool): Whether to include thread information in traces. Default is False.
- custom_repr (tuple): Custom representation functions for specific types. Default is empty tuple.
- max_variable_length (int): Maximum length of variable representations. Default is 100.
- normalize (bool): Whether to normalize line endings in output. Default is False.
- relative_time (bool): Whether to show relative timestamps. Default is False.
- color (bool): Whether to use colored output. Default is True.

## Returns
None

## Raises
- AssertionError: When depth parameter is less than 1

## State Changes
- Attributes READ: None
- Attributes WRITTEN: 
  - self._write: Write function for output
  - self.watch: Processed list of watched variables
  - self.frame_to_local_reprs: Dictionary for local variable representations
  - self.start_times: Dictionary for tracking start times
  - self.depth: Frame depth limit
  - self.prefix: Trace prefix string
  - self.thread_info: Thread information flag
  - self.thread_info_padding: Thread info padding value
  - self.target_codes: Set of target code objects
  - self.target_frames: Set of target frames
  - self.thread_local: Threading local storage
  - self.custom_repr: Custom representation functions
  - self.last_source_path: Last source file path tracked
  - self.max_variable_length: Maximum variable representation length
  - self.normalize: Normalization flag
  - self.relative_time: Relative time flag
  - self.color: Color support flag
  - self._FOREGROUND_* and self._STYLE_*: Color formatting codes (when color is enabled)

## Constraints
- Preconditions:
  - depth must be >= 1
  - output parameter must be compatible with get_write_function requirements
- Postconditions:
  - All internal state is properly initialized
  - self._write is a callable function
  - self.watch contains properly processed variable objects
  - Color codes are initialized appropriately based on platform support

## Side Effects
- May create or modify files on disk if output specifies a file path
- May write to stderr if output is None
- May initialize color formatting codes based on platform detection
- No other side effects beyond initialization

### `pysnooper.tracer.Tracer.__call__` · *method*

## Summary:
Enables the Tracer to be used as a decorator for functions or classes, wrapping them with tracing functionality.

## Description:
This method implements the callable interface of the Tracer class, allowing instances to be used directly as decorators. When invoked, it determines whether the decorated object is a function or class and applies appropriate wrapping logic. If tracing is disabled globally, it returns the original object unchanged.

## Args:
    function_or_class: Either a function or class object to be wrapped with tracing capabilities

## Returns:
    - If tracing is disabled: the original function_or_class unchanged
    - If function_or_class is a class: the decorated class with traced methods
    - If function_or_class is a function: the wrapped function with tracing enabled

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The function_or_class parameter must be either a callable function or a class
        - The Tracer instance must be properly initialized
    Postconditions:
        - If tracing is disabled, the original object is returned unchanged
        - If tracing is enabled, the object is wrapped with tracing functionality

## Side Effects:
    None directly caused by this method invocation
    - The method may indirectly cause side effects through the wrapped functions/classes
    - The global DISABLED flag controls whether tracing occurs

### `pysnooper.tracer.Tracer._wrap_class` · *method*

## Summary:
Wraps all regular functions in a class with tracing functionality while preserving coroutine functions unchanged.

## Description:
This method processes all attributes of a given class and applies tracing wrapper to regular functions, enabling detailed inspection of method execution. It is invoked by the Tracer's `__call__` method when a class is decorated with the tracer. The method specifically excludes coroutine functions from wrapping to avoid conflicts with async execution patterns.

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
    - The class should have a `__dict__` attribute containing its attributes
    
    Postconditions:
    - All regular functions in the class are replaced with traced versions
    - Coroutine functions remain unchanged
    - The returned class is identical to the input class but with modified methods

## Side Effects:
    None

### `pysnooper.tracer.Tracer._wrap_function` · *method*

## Summary:
Creates a traced wrapper for a function that monitors its execution with detailed variable tracking.

## Description:
This method generates a wrapper around the provided function that enables detailed tracing of its execution. The wrapper ensures that when the function is called, the Tracer's context manager (`__enter__` and `__exit__`) is activated to capture variable states and execution flow. The method distinguishes between regular functions, generator functions, and special function types (coroutine/async generator) to return the appropriate wrapper.

When a function is wrapped, the Tracer's `target_codes` set is updated to include the function's code object, enabling the tracer to recognize and monitor executions of this function.

## Args:
    function (callable): The function to wrap with tracing capabilities

## Returns:
    callable: A wrapped version of the input function that will be traced when executed. Returns a simple wrapper for regular functions, or a generator wrapper for generator functions. Generator wrappers properly handle the yield/return flow of generator functions.

## Raises:
    NotImplementedError: When attempting to wrap coroutine functions (detected by pycompat.iscoroutinefunction) or async generator functions (detected by pycompat.isasyncgenfunction)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.target_codes (adds function.__code__ to the set)

## Constraints:
    Preconditions: The function parameter must be a callable object
    Postconditions: The returned wrapper will execute the original function while providing tracing information through the Tracer's context manager

## Side Effects:
    Registers the function's code object in self.target_codes for tracing purposes

### `pysnooper.tracer.Tracer.write` · *method*

## Summary:
Formats and writes trace information with a configurable prefix to the designated output destination.

## Description:
Writes formatted trace messages to the configured output destination by prepending the instance's prefix to the input string and appending a newline character. This method serves as a centralized interface for all trace message output within the Tracer class, ensuring consistent formatting and proper integration with the configured output mechanism.

The method is primarily invoked internally by the Tracer class during tracing operations, specifically from the `__exit__` method when reporting elapsed time and from the `trace` method when logging various execution events such as variable changes, function calls, returns, and exceptions.

## Args:
    s (str): The trace message to be written, without a trailing newline character.

## Returns:
    None: This method does not return any value.

## Raises:
    Exception: Propagates any exceptions raised by the underlying `_write` function, which depends on the configured output destination (stderr, file, or custom writer).

## State Changes:
    Attributes READ:
        - self.prefix: Configuration prefix applied to all trace messages
        - self._write: Internal write function for outputting trace messages
    
    Attributes WRITTEN:
        - None: This method does not modify any instance attributes directly.

## Constraints:
    Preconditions:
        - self.prefix must be a string or convertible to string
        - self._write must be a callable function that accepts a string argument
        - The input string `s` should not contain trailing newlines (though the method will add one)

    Postconditions:
        - The formatted string (prefix + s + newline) is written to the configured output destination
        - The method completes without modifying the Tracer instance's state

## Side Effects:
    - I/O operation to the configured output destination (stderr, file, or custom writer)
    - Potential file system access when writing to file paths
    - Possible console output when writing to stderr or stdout

### `pysnooper.tracer.Tracer.__enter__` · *method*

## Summary:
Enters the tracing context by configuring frame tracing and installing the tracer's global trace function.

## Description:
This method implements the context manager protocol's `__enter__` method for the Tracer class. When called as part of a `with` statement, it prepares the execution environment for tracing by:
1. Setting up thread-local depth tracking
2. Configuring the calling frame for tracing if it's not an internal frame
3. Managing a stack of original trace functions for proper cleanup
4. Recording execution start time for timing measurements
5. Installing the tracer's trace function globally via sys.settrace()

This method is automatically invoked when entering a `with Tracer():` block and should not be called directly.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ:
    - self.target_frames
    - self.thread_local
    - self.start_times
    - self.trace
    - self._is_internal_frame
    
    Attributes WRITTEN:
    - thread_global.depth (via setdefault)
    - calling_frame.f_trace (when not internal frame)
    - self.target_frames (when not internal frame)
    - self.thread_local.original_trace_functions (stack management)
    - self.start_times (start time recording)
    - sys.trace (global trace function replacement)

## Constraints:
    Preconditions:
    - Must be called as part of a context manager protocol (`with` statement)
    - The calling frame must be accessible via `inspect.currentframe().f_back`
    - The Tracer instance must be properly initialized
    - The DISABLED global flag should be False to enable tracing
    
    Postconditions:
    - The calling frame's f_trace attribute is set to self.trace (if not internal)
    - The global trace function is replaced with self.trace via sys.settrace()
    - A stack of original trace functions is maintained in thread_local storage
    - Execution start time for the calling frame is recorded
    - Thread depth tracking is initialized/updated

## Side Effects:
    - Modifies the global trace function via sys.settrace()
    - Sets the f_trace attribute on the calling frame (when not internal)
    - Updates thread-local storage for trace function stack management
    - Records timestamps for execution timing measurement
    - May affect program execution flow due to trace function installation

### `pysnooper.tracer.Tracer.__exit__` · *method*

*No documentation generated.*

### `pysnooper.tracer.Tracer._is_internal_frame` · *method*

## Summary:
Determines whether a given frame represents internal tracer implementation code rather than user code being traced.

## Description:
This method serves as a utility to distinguish between frames that belong to the pysnooper tracer's internal implementation and those that represent user code being traced. It compares the filename of the provided frame's code object with the filename of the Tracer.__enter__ method's code object. This distinction is crucial for filtering out internal frames during tracing to prevent cluttering the trace output with the tracer's own implementation details.

The method is primarily used in the Tracer.trace method to skip internal frames when depth > 1, ensuring clean trace output focused on user code execution.

## Args:
    frame (FrameType): A Python frame object to check for internal tracer status

## Returns:
    bool: True if the frame's code filename matches the Tracer.__enter__ method's code filename, indicating it's an internal frame; False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The frame parameter must be a valid Python frame object
    - The Tracer.__enter__ method must be defined and accessible
    
    Postconditions:
    - Returns a boolean value indicating internal vs user frame status
    - Does not modify any object state

## Side Effects:
    None

### `pysnooper.tracer.Tracer.set_thread_info_padding` · *method*

## Summary
Sets thread information padding to ensure consistent alignment of thread identifiers in trace output.

## Description
This method manages the padding width for thread information displayed in tracing output. It calculates the length of the provided thread_info string, updates the internal `thread_info_padding` attribute to track the maximum required width, and returns the thread_info string padded with spaces to maintain consistent column alignment.

The method is called during tracing when thread information is being formatted for display. It ensures that all thread information entries in the trace output are properly aligned by maintaining a global minimum padding width across all observed thread identifiers.

## Args
- thread_info (str): Thread identifier string to be padded, typically in the format "ident-name "

## Returns
- str: The input thread_info string padded with trailing spaces to match the current maximum padding width

## Raises
- None

## State Changes
- Attributes READ: self.thread_info_padding
- Attributes WRITTEN: self.thread_info_padding

## Constraints
- Preconditions: The thread_info parameter must be a string
- Postconditions: self.thread_info_padding is updated to be at least the length of thread_info, and the returned string is padded to this width

## Side Effects
- Updates the internal self.thread_info_padding attribute to track maximum width requirement
- Returns a string with trailing spaces for alignment purposes

### `pysnooper.tracer.Tracer.trace` · *method*

## Summary:
Handles Python tracing events to log function calls, variable changes, and execution flow with detailed debugging information.

## Description:
The trace method is the core event handler for Python's tracing mechanism, invoked for each line of code execution when tracing is active. It processes different types of tracing events (call, return, exception) to provide detailed insights into program execution including variable states, execution timing, and source code context. This method is responsible for filtering which frames to trace based on configured depth and target specifications, formatting and outputting trace information, and managing the tracing state.

The method is designed to be called by Python's built-in tracing infrastructure and is not intended to be called directly by users. It integrates with the Tracer class's configuration to provide customizable debugging output including variable tracking, timing information, and color-coded formatting.

## Args:
    self (Tracer): The Tracer instance that owns this method
    frame (FrameType): The current Python frame being traced
    event (str): The type of tracing event ('call', 'return', 'exception')
    arg (Any): Additional argument associated with the event (varies by event type)

## Returns:
    callable: Returns self.trace to continue tracing, or None to stop tracing

## Raises:
    NotImplementedError: When thread_info is enabled with normalize flag

## State Changes:
    Attributes READ:
        - self.target_codes: Set of code objects to trace
        - self.target_frames: Set of frame objects to trace
        - self.depth: Maximum depth for tracing
        - self._is_internal_frame: Method to detect internal frames
        - self.normalize: Flag for normalizing output
        - self.relative_time: Flag for relative timing
        - self.thread_info: Flag for thread information
        - self.watch: Variables to watch during tracing
        - self.custom_repr: Custom representation functions
        - self.max_variable_length: Maximum variable representation length
        - self.start_times: Dictionary tracking start times per frame
        - self.frame_to_local_reprs: Dictionary tracking variable representations per frame
        - self.last_source_path: Last source file path tracked
        - self.thread_info_padding: Padding for thread information alignment
        - self._FOREGROUND_* and _STYLE_*: Color formatting codes
        - thread_global.depth: Current tracing depth (thread-local)

    Attributes WRITTEN:
        - self.frame_to_local_reprs: Updated with current frame's variable representations
        - self.start_times: Updated with start time for current frame
        - self.last_source_path: Updated with current source file path
        - self.thread_info_padding: Updated with maximum thread info width
        - thread_global.depth: Incremented/decremented based on call/return events

## Constraints:
    Preconditions:
        - frame must be a valid Python frame object
        - event must be one of 'call', 'return', or 'exception'
        - self.target_codes and self.target_frames must be properly initialized sets
        - self.depth must be >= 1
        - thread_global must be accessible as a thread-local object with depth attribute

    Postconditions:
        - For 'call' events: thread_global.depth is incremented and variable tracking begins
        - For 'return' events: thread_global.depth is decremented and variable tracking ends
        - For 'exception' events: exception information is formatted and written
        - Variable representations are properly tracked and displayed
        - Trace output is formatted according to configuration settings

## Side Effects:
    - Writes formatted trace information to the configured output destination
    - Modifies thread-local storage to track tracing depth
    - Accesses filesystem to retrieve source code when needed
    - May access IPython history manager for notebook environments
    - May read from ZIP archives for Ansible files
    - Updates internal dictionaries for tracking variable states and timing

