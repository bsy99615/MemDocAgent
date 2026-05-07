# `nativetypes.py`

## `src.jinja2.nativetypes.native_concat` · *function*

*No documentation generated.*

## `src.jinja2.nativetypes.NativeCodeGenerator` · *class*

*No documentation generated.*

### `src.jinja2.nativetypes.NativeCodeGenerator._default_finalize` · *method*

## Summary:
Returns the input value unchanged, serving as the default finalization function for template compilation.

## Description:
This static method acts as the default finalize function in Jinja2's native code generation system. It is used when no custom finalization logic is specified for processing template expressions. The method simply returns the input value without modification, making it suitable as a fallback handler in the template compilation pipeline.

## Args:
    value (Any): Any Python value to be returned unchanged.

## Returns:
    Any: The same value that was passed as input.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned value is identical to the input value.

## Side Effects:
    None: This method has no side effects and is pure.

### `src.jinja2.nativetypes.NativeCodeGenerator._output_const_repr` · *method*

## Summary:
Converts an iterable of values into a string representation by joining elements and returning their repr.

## Description:
This method processes an iterable of values by converting each element to a string, joining them together into a single string, and then returning the repr() of that joined string. It's used in the Jinja2 template compilation process to generate constant representations for template elements.

The method serves as a utility for creating string representations of constant template data during code generation. It's specifically designed to handle the conversion of multiple values into a single string literal that can be embedded in generated Python code.

This logic is separated into its own method to avoid code duplication and provide a clean interface for handling constant value grouping during template compilation, particularly when dealing with template data that needs to be represented as Python string literals.

## Args:
    group (Iterable[Any]): An iterable of values to be converted to string representation and joined together.

## Returns:
    str: The repr() of the joined string formed by converting each element in the group to string and concatenating them.

## Raises:
    None explicitly raised by this method, though the calling context may raise exceptions from underlying operations.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The group parameter must be iterable and each element must be convertible to string via str().
    Postconditions: The returned string is a valid Python repr() representation of the joined string.

## Side Effects:
    None

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_to_const` · *method*

*No documentation generated.*

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_pre` · *method*

## Summary:
Writes pre-formatted source code to the output buffer when available in the finalize information.

## Description:
This method performs a conditional write operation to the output buffer during Jinja2 template code generation. It checks if the `finalize.src` attribute is not None, and if so, writes that source code directly to the output buffer using the `self.write()` method.

This method is part of a paired processing system with `_output_child_post` in the NativeCodeGenerator class, where `_output_child_pre` handles pre-processing and `_output_child_post` handles post-processing of child nodes during template compilation.

The method is typically invoked during the compilation phase of Jinja2 templates when processing expressions that may require pre-formatted source code from finalization information.

## Args:
    node (nodes.Expr): The expression node being processed during code generation
    frame (Frame): The compilation frame containing execution context and evaluation state  
    finalize (CodeGenerator._FinalizeInfo): Finalization information object containing source code to write

## Returns:
    None: This method performs side effects by writing to the output buffer

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: 
    - `finalize.src` (checked for None value)
    - `self.write` (method call to write to output buffer)
    
    Attributes WRITTEN: 
    - Indirectly modifies the output buffer through `self.write()` method call

## Constraints:
    Preconditions:
    - The `finalize` parameter must be a valid `CodeGenerator._FinalizeInfo` instance
    - The `node` parameter must be a valid `nodes.Expr` instance
    - The `frame` parameter must be a valid `Frame` instance
    
    Postconditions:
    - If `finalize.src` is not None, the source code is written to the output buffer
    - No internal state of the generator object is modified

## Side Effects:
    I/O: Writes to the output buffer via the `self.write()` method call

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_post` · *method*

## Summary:
Writes a closing parenthesis to the generated code when finalize information indicates a function call or expression needs to be closed.

## Description:
This method is part of the code generation pipeline in NativeCodeGenerator and handles post-processing of child nodes. It's designed to complement the `_output_child_pre` method which writes the opening part of a finalize operation. When the finalize information contains source code that needs to be closed (indicated by `finalize.src` being not None), this method writes a closing parenthesis to properly terminate the expression.

## Args:
    node (nodes.Expr): The AST expression node being processed
    frame (Frame): The compilation frame containing execution context
    finalize (CodeGenerator._FinalizeInfo): Finalization information containing source code to write

## Returns:
    None: This method performs I/O operations and doesn't return a value

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self (through the write method), finalize.src
    Attributes WRITTEN: None (modifies external state via write method)

## Constraints:
    Preconditions: 
    - The method assumes that if `finalize.src` is not None, then appropriate opening syntax was already written
    - The `node` parameter must be a valid AST expression node
    - The `frame` parameter must contain valid compilation context
    
    Postconditions:
    - If `finalize.src` is not None, a closing parenthesis is written to the output
    - The method maintains consistency with the matching `_output_child_pre` method

## Side Effects:
    I/O: Writes a closing parenthesis character to the generated code output stream

## `src.jinja2.nativetypes.NativeEnvironment` · *class*

*No documentation generated.*

## `src.jinja2.nativetypes.NativeTemplate` · *class*

## Summary:
A Jinja2 template class that provides both synchronous and asynchronous rendering using native Python type handling.

## Description:
NativeTemplate is a specialized Jinja2 template implementation that extends the base Template class. It provides rendering capabilities for templates using a NativeEnvironment, which optimizes the concatenation of rendered template fragments. This class is designed to work specifically with NativeEnvironment and offers both synchronous and asynchronous rendering methods.

## State:
- environment_class: Class variable set to NativeEnvironment, indicating the environment type used for rendering operations
- Inherits all state from the base Template class including template source, AST representation, and compilation artifacts

## Lifecycle:
- Creation: Typically instantiated through Environment.from_string() or similar factory methods that create templates bound to a NativeEnvironment
- Usage: Call render() for synchronous rendering or render_async() for asynchronous rendering with proper async environment configuration
- Destruction: Inherits standard cleanup behavior from the parent Template class

## Method Map:
```mermaid
graph TD
    A[NativeTemplate] --> B[render()]
    A --> C[render_async()]
    B --> D[new_context()]
    B --> E[environment_class.concat()]
    B --> F[handle_exception()]
    C --> G[new_context()]
    C --> H[environment_class.concat()]
    C --> F
```

## Raises:
- RuntimeError: render_async() raises this exception when called on an environment not configured for async mode
- Exception: All other exceptions during rendering are caught and handled by the environment's handle_exception() method

## Example:
```python
# Create a template with NativeEnvironment
env = NativeEnvironment()
template = env.from_string("Hello {{ name }}!")

# Synchronously renders a template with provided context data and returns the concatenated result
result = template.render(name="World")

# Asynchronously renders a template with provided context data and returns the concatenated result
async_result = await template.render_async(name="World")
```

### `src.jinja2.nativetypes.NativeTemplate.render` · *method*

## Summary:
Executes a Jinja2 template with the provided context and returns the rendered content, handling exceptions through the environment's error handler.

## Description:
This method implements the core rendering logic for NativeTemplate instances. It creates a runtime context from the provided arguments, executes the template's compiled root render function (which yields output segments), and concatenates these segments into a final rendered string. When rendering encounters an exception, it delegates to the environment's exception handler for proper error reporting.

## Args:
    *args (Any): Positional arguments to be merged into the template context dictionary
    **kwargs (Any): Keyword arguments to be merged into the template context dictionary

## Returns:
    Any: The rendered template content as a concatenated string, or the result of environment exception handling when rendering fails

## Raises:
    Exception: Any exception occurring during template execution is caught and processed by the environment's exception handler

## State Changes:
    Attributes READ: 
    - self.new_context: Creates a new execution context for template rendering
    - self.environment_class: Provides the concat method for combining output segments  
    - self.root_render_func: The compiled template rendering function that yields output segments
    - self.environment.handle_exception: Exception handling mechanism for rendering errors
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The template must have a valid root_render_func that can be executed with a context
    - The environment_class must provide a concat method compatible with the output of root_render_func
    - The context creation must succeed with the provided arguments
    
    Postconditions:
    - Returns either the rendered template content (as a string) or an exception handling result
    - The NativeTemplate instance remains unmodified throughout execution

## Side Effects:
    - Executes the template's compiled root render function which may perform I/O operations
    - Calls the environment's exception handler when rendering fails
    - May iterate over generator output from root_render_func during concatenation

### `src.jinja2.nativetypes.NativeTemplate.render_async` · *method*

## Summary:
Asynchronously renders a template with provided context data and returns the concatenated result.

## Description:
This method provides asynchronous rendering capability for Jinja2 templates. It validates that the environment is configured for async operations, creates a rendering context from the provided arguments, executes the template's root render function asynchronously, and concatenates the resulting generator into a single output string. When exceptions occur during rendering, it delegates to the environment's exception handler.

## Args:
    *args (t.Any): Positional arguments to be merged into the rendering context dictionary
    **kwargs (t.Any): Keyword arguments to be merged into the rendering context dictionary

## Returns:
    t.Any: The concatenated rendered template output, or an exception handling result if rendering fails

## Raises:
    RuntimeError: When the environment was not created with async mode enabled

## State Changes:
    Attributes READ: 
    - self.environment.is_async
    - self.environment_class
    - self.root_render_func
    - self.environment.handle_exception
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The environment must be initialized with async mode enabled (environment.is_async must be True)
    - The template must have a valid root_render_func method
    - The template must have a valid environment_class with a concat method
    
    Postconditions:
    - If successful, returns the rendered template content as a concatenated string
    - If an exception occurs, returns the result of environment.handle_exception()

## Side Effects:
    - May perform I/O operations during template rendering
    - May call external services if template contains async operations
    - Invokes environment's exception handling mechanism when errors occur

