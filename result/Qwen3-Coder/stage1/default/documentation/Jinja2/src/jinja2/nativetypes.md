# `nativetypes.py`

## `src.jinja2.nativetypes.native_concat` · *function*

## Summary:
Concatenates iterable values and attempts to parse the result as a Python literal expression.

## Description:
Processes an iterable of values by first examining the first two elements to optimize performance. For empty iterables, returns None. For single non-string elements, returns the element directly. For single string elements or multiple elements, it concatenates all values as strings and attempts to parse the result as a Python literal expression using ast.literal_eval. If parsing fails due to syntax errors, value errors, or memory issues, it returns the raw concatenated string.

This function is designed to handle template variable concatenation while providing safe evaluation of string representations of Python literals.

## Args:
    values (Iterable[Any]): An iterable of values to concatenate and potentially evaluate

## Returns:
    Optional[Any]: Returns None for empty iterables, the single non-string value directly, or the parsed Python literal if successful. Returns the raw concatenated string if parsing fails.

## Raises:
    None explicitly raised - handles ValueError, SyntaxError, and MemoryError internally

## Constraints:
    Preconditions:
    - Input must be an iterable of any type
    - Values should be convertible to strings for concatenation
    
    Postconditions:
    - Returns either None, the original value (for single non-string values), a parsed Python literal, or the raw concatenated string

## Side Effects:
    None - This function is pure and doesn't perform I/O or mutate external state

## Control Flow:
```mermaid
flowchart TD
    A[Start with values iterable] --> B{Empty iterable?}
    B -- Yes --> C[Return None]
    B -- No --> D{Single element?}
    D -- Yes --> E{Element is string?}
    E -- Yes --> F[Join all values as string]
    E -- No --> G[Return element directly]
    D -- No --> H[Join all values as string]
    F --> I[Try literal_eval(parse(raw))]
    H --> I
    I --> J{Parse succeeds?}
    J -- Yes --> K[Return parsed value]
    J -- No --> L[Return raw string]
```

## Examples:
```python
# Empty iterable
native_concat([])  # Returns None

# Single non-string element
native_concat([42])  # Returns 42

# Single string element (goes through full processing)
native_concat(["hello"])  # Returns "hello" (since it joins all values, which is just "hello")

# Multiple elements that form a valid literal
native_concat([1, 2, 3])  # Returns "123" (as string) or [1, 2, 3] if parsed successfully

# Generator input
native_concat(iter([1, 2, 3]))  # Returns "123" or parsed version

# String that can be parsed as literal
native_concat(["[1, 2, 3]"])  # Returns [1, 2, 3] (parsed list)
```

## `src.jinja2.nativetypes.NativeCodeGenerator` · *class*

*No documentation generated.*

### `src.jinja2.nativetypes.NativeCodeGenerator._default_finalize` · *method*

## Summary:
Returns the input value unchanged, serving as the default finalization handler for template compilation.

## Description:
This static method serves as the default implementation for finalizing values during Jinja2 template code generation. It is used when no specific finalization logic is required, simply returning the input value unchanged. The method is part of the NativeCodeGenerator class and is intended to be overridden by subclasses that require custom value finalization behavior.

## Args:
    value (Any): Any Python value that needs to be finalized. This can be of any type.

## Returns:
    Any: The same value that was passed as input, unchanged.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    None: This method is static and does not modify any instance or class state.

## Constraints:
    Preconditions: None - any value can be passed to this method
    Postconditions: The returned value is identical to the input value

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `src.jinja2.nativetypes.NativeCodeGenerator._output_const_repr` · *method*

## Summary:
Generates a quoted string representation of a sequence of values joined together for use in compiled template output.

## Description:
This method processes an iterable of values by converting each to a string, joining them into a single string, and returning the repr() of that result. It's used in Jinja2's native code generation to create constant string representations for template compilation, particularly for handling template data and constant expressions.

## Args:
    group (t.Iterable[t.Any]): An iterable collection of values to be converted to strings and joined together.

## Returns:
    str: The repr() of the concatenated string formed by converting each item in the group to a string and joining them. The result is a properly quoted Python string representation.

## Raises:
    None explicitly raised, though underlying operations may raise exceptions from str() or join() operations.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The group parameter must be iterable and each item in the group must be convertible to a string without raising exceptions.
    Postconditions: The returned string is a valid Python representation of the joined string, suitable for use in generated Python code.

## Side Effects:
    None

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_to_const` · *method*

## Summary:
Converts an AST expression node to a constant value with finalization, handling TemplateData nodes specially.

## Description:
Processes an AST expression node by extracting its constant value, validating the representation safety, and applying finalization processing. This method serves as a key component in Jinja2's native code generation pipeline for handling constant expressions.

The method is typically called during template compilation when generating Python source code from AST nodes. It's part of a trio of related methods (`_output_child_to_const`, `_output_child_pre`, `_output_child_post`) that work together to properly handle expression compilation with appropriate syntax and finalization.

This method exists separately from inline processing to encapsulate the logic for constant conversion with safety checks and finalization, making the code more modular and reusable.

## Args:
    node (nodes.Expr): The AST expression node to convert to a constant value
    frame (Frame): The compilation frame containing execution context for evaluating the node
    finalize (CodeGenerator._FinalizeInfo): Finalization information containing processing instructions for the constant value

## Returns:
    t.Any: Either the raw constant value from the node (when node is TemplateData) or the finalized constant value (when node is not TemplateData)

## Raises:
    nodes.Impossible: Raised when the constant value derived from the node cannot be safely represented as a Python literal

## State Changes:
    Attributes READ: 
        - None: This method doesn't directly read instance attributes
    Attributes WRITTEN:
        - None: This method doesn't directly modify instance attributes

## Constraints:
    Preconditions:
        - The node parameter must be a valid nodes.Expr instance
        - The frame parameter must be a valid Frame instance
        - The finalize parameter must be a valid CodeGenerator._FinalizeInfo instance
        - The node's as_const method must be callable and return a valid constant value
    Postconditions:
        - If the node is a TemplateData instance, the raw constant value is returned
        - Otherwise, the constant value is processed through finalize.const() and returned
        - The returned value represents the constant form of the node with appropriate finalization

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_pre` · *method*

## Summary:
Writes finalized source code to output when available, serving as a pre-processing step for child node compilation.

## Description:
This method serves as a pre-processing hook in the template compilation pipeline, specifically designed to output pre-computed source code fragments when they are available in the finalize information. It is part of a paired approach with `_output_child_post` to handle proper formatting around child node expressions.

The method is typically called during the code generation phase of Jinja2 template compilation, where it receives a node expression, compilation frame, and finalize information containing pre-computed source code that should be written to the output.

## Args:
    node (nodes.Expr): The AST expression node being compiled
    frame (Frame): The compilation frame containing execution context
    finalize (CodeGenerator._FinalizeInfo): Finalization information containing pre-computed source code

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    None explicitly raised: The method only performs conditional writing based on finalize.src availability

## State Changes:
    Attributes READ: 
        - self (the NativeCodeGenerator instance)
        - finalize.src (accessed to check if it's not None)
    Attributes WRITTEN:
        - self (through the self.write() call, which modifies the output buffer)

## Constraints:
    Preconditions:
        - The finalize parameter must be a valid CodeGenerator._FinalizeInfo instance
        - The node parameter must be a valid nodes.Expr instance
        - The frame parameter must be a valid Frame instance
    Postconditions:
        - If finalize.src is not None, it will be written to the output via self.write()
        - No modifications to the object's state beyond output generation

## Side Effects:
    I/O operations: Writes to the output buffer via self.write() when finalize.src is not None

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_post` · *method*

## Summary:
Writes a closing parenthesis to the generated code when finalize context requires it.

## Description:
This method is part of the template code generation process in Jinja2's native types system. It serves as the post-processing step for expression nodes, complementing the `_output_child_pre` method which handles pre-processing. When the finalize information contains source code that requires closing syntax (such as parentheses), this method writes the closing parenthesis to maintain proper Python syntax in the generated code.

The method is typically invoked during Jinja2 template compilation when generating Python source code from template AST nodes. It ensures that expressions wrapped with finalize context are properly closed with parentheses, maintaining syntactic correctness of the generated code.

## Args:
    self: The NativeCodeGenerator instance
    node (nodes.Expr): The expression node being processed in the template AST
    frame (Frame): The compilation frame containing execution context  
    finalize (CodeGenerator._FinalizeInfo): Finalization information that determines if closing syntax is needed

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    None explicitly raised: The method doesn't contain explicit exception handling

## State Changes:
    Attributes READ: 
        - finalize.src: Source code information from finalization context that determines if closing parenthesis is needed
        - self.write: Method used for outputting generated code
    
    Attributes WRITTEN:
        - None: This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
        - The finalize parameter must be a valid CodeGenerator._FinalizeInfo instance
        - The node parameter must be a valid nodes.Expr instance
        - The frame parameter must be a valid Frame instance
        - The method should only be called in the context of template code generation
        
    Postconditions:
        - When finalize.src is not None, a closing parenthesis is written to the output stream
        - The generated code maintains proper syntax structure

## Side Effects:
    - I/O operation: Writes a closing parenthesis character to the output stream via self.write()
    - Mutates the generated Python code output stream by appending closing syntax

## `src.jinja2.nativetypes.NativeEnvironment` · *class*

## Summary:
A specialized Jinja2 environment that uses native Python code generation and optimized concatenation for template rendering.

## Description:
The `NativeEnvironment` class is a subclass of the standard Jinja2 `Environment` that customizes template compilation and value concatenation behavior. It provides a more efficient code generation approach using `NativeCodeGenerator` and implements optimized string concatenation via `native_concat` to handle template variable processing safely.

This environment is designed for scenarios where performance and safety of template variable handling are important considerations, particularly when dealing with mixed-type template variables that may need to be converted to Python literals.

## State:
- `code_generator_class`: Set to `NativeCodeGenerator` - determines the code generation strategy for compiling templates
- `concat`: Set to `staticmethod(native_concat)` - defines how template values are concatenated and evaluated

## Lifecycle:
- Creation: Instantiated like any standard `Environment` class, inheriting all standard environment configuration options
- Usage: Used identically to `Environment` for template loading, rendering, and compilation
- Destruction: Inherits standard `Environment` cleanup behavior

## Method Map:
```mermaid
flowchart TD
    A[NativeEnvironment.__init__] --> B[Environment.__init__]
    B --> C[Sets code_generator_class = NativeCodeGenerator]
    C --> D[Sets concat = staticmethod(native_concat)]
    D --> E[Template compilation uses NativeCodeGenerator]
    E --> F[Template rendering uses native_concat for value processing]
```

## Raises:
- Inherits all exceptions from `Environment.__init__`
- May raise exceptions from `NativeCodeGenerator` during template compilation
- May raise exceptions from `native_concat` during template value processing

## Example:
```python
from jinja2 import NativeEnvironment

# Create a native environment
env = NativeEnvironment()

# Load and render a template
template = env.from_string("Hello {{ name }}!")
result = template.render(name="World")
print(result)  # Output: "Hello World!"

# The environment uses native code generation and optimized concatenation
```

## `src.jinja2.nativetypes.NativeTemplate` · *class*

## Summary:
A Jinja2 template class that renders templates using native Python code generation and optimized value concatenation for enhanced performance and safety.

## Description:
The `NativeTemplate` class extends the standard Jinja2 `Template` class and sets the `environment_class` attribute to `NativeEnvironment`. It provides both synchronous and asynchronous rendering methods that leverage native Python code generation and optimized string concatenation for improved performance and safer template variable handling.

This template class is designed for scenarios where performance and security of template rendering are important considerations, particularly when dealing with mixed-type template variables that may need to be converted to Python literals. It works in conjunction with `NativeEnvironment` to provide enhanced template compilation and rendering capabilities.

## State:
- `environment_class`: Class attribute set to `NativeEnvironment` - determines the environment used for template compilation and rendering
- Inherited attributes from `Template`: All standard template attributes including `name`, `filename`, `globals`, `environment`, `root_render_func`, `new_context`, etc.

## Lifecycle:
- Creation: Instantiated through normal template creation processes (e.g., `NativeEnvironment.from_string()` or `NativeEnvironment.get_template()`) which creates a `NativeTemplate` instance
- Usage: Templates are typically rendered by calling either `render()` or `render_async()` methods with context data
- Destruction: Inherits standard template cleanup behavior from the parent `Template` class

## Method Map:
```mermaid
flowchart TD
    A[NativeTemplate.render] --> B[Template.new_context]
    B --> C[environment_class.concat]
    C --> D[root_render_func(ctx)]
    D --> E[Returns concatenated result]
    
    A --> F[Exception handling]
    F --> G[environment.handle_exception()]
    
    A[NativeTemplate.render_async] --> H[Template.new_context]
    H --> I[environment_class.concat]
    I --> J[Async root_render_func(ctx)]
    J --> K[Returns concatenated result]
    
    H --> L[Exception handling]
    L --> M[environment.handle_exception()]
```

## Raises:
- `RuntimeError`: Raised by `render_async()` when the environment was not created with async mode enabled
- All exceptions that can occur during template rendering, which are handled by delegating to `environment.handle_exception()`

## Example:
```python
from jinja2 import NativeEnvironment

# Create a native environment
env = NativeEnvironment()

# Create a template
template = env.from_string("Hello {{ name }}! You have {{ count }} messages.")

# Render synchronously
result = template.render(name="Alice", count=5)
print(result)  # Output: "Hello Alice! You have 5 messages."

# For async rendering (requires async environment)
async_result = await template.render_async(name="Bob", count=3)
print(async_result)  # Output: "Hello Bob! You have 3 messages."
```

### `src.jinja2.nativetypes.NativeTemplate.render` · *method*

## Summary:
Renders the template with provided context data and returns the concatenated output, handling exceptions gracefully.

## Description:
Executes the template rendering process by creating a context from the provided arguments, running the root render function, and concatenating the results. If an exception occurs during rendering, it delegates to the environment's exception handler. This method is part of the Jinja2 native template rendering system.

## Args:
    *args (Any): Positional arguments to be merged into the rendering context dictionary
    **kwargs (Any): Keyword arguments to be merged into the rendering context dictionary

## Returns:
    Any: The concatenated rendered template output (typically str) or an exception-handled result if rendering fails

## Raises:
    Exception: Propagated from underlying rendering functions or environment exception handling mechanisms

## State Changes:
    Attributes READ: 
    - self.new_context: Creates rendering context
    - self.environment_class.concat: Concatenates rendered content
    - self.root_render_func: Executes template rendering
    - self.environment.handle_exception: Handles rendering exceptions
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The template must have been properly initialized with a valid environment
    - The root_render_func must be callable and available on the instance
    - The environment_class must support the concat method
    
    Postconditions:
    - Returns either the rendered template content (typically str) or an exception-handled result
    - The context is created with the provided arguments but is not stored on the instance

## Side Effects:
    - May perform I/O operations during template rendering
    - May invoke external functions through the root_render_func
    - May call environment-specific exception handling mechanisms

### `src.jinja2.nativetypes.NativeTemplate.render_async` · *method*

## Summary:
Asynchronously renders a template with provided context variables and returns the concatenated result.

## Description:
This method executes an asynchronous template rendering process that generates output by processing the template's root render function with the provided context. It validates that the environment supports async operations before proceeding with rendering.

## Args:
    *args (t.Any): Positional arguments to be merged into the rendering context
    **kwargs (t.Any): Keyword arguments to be merged into the rendering context

## Returns:
    t.Any: The concatenated rendered template output, or an exception handler result

## Raises:
    RuntimeError: When the environment was not created with async mode enabled

## State Changes:
    Attributes READ: self.environment, self.environment_class, self.root_render_func
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The environment must have been initialized with async mode enabled (self.environment.is_async must be True)
    - The root_render_func must be callable and return an async iterable
    
    Postconditions:
    - If successful, returns the concatenated string representation of the rendered template
    - If an exception occurs, returns the result of environment.handle_exception()

## Side Effects:
    - May perform I/O operations during template rendering
    - Calls external methods (root_render_func, environment_class.concat, handle_exception)
    - May involve asynchronous iteration over template nodes

