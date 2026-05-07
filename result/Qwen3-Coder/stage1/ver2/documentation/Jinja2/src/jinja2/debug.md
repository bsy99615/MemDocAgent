# `debug.py`

## `src.jinja2.debug.rewrite_traceback_stack` · *function*

## Summary:
Rewrites exception tracebacks to provide enhanced debugging information for Jinja2 templates by filtering internal frames and mapping template line numbers to source locations.

## Description:
Processes the current exception's traceback to improve debugging experience for Jinja2 template errors. This function filters out internal implementation frames, translates template line numbers to actual source locations, and constructs a cleaner traceback that points to the user's template code rather than internal Jinja2 machinery.

The function specifically handles `TemplateSyntaxError` by marking it as translated and attaching source information. For regular template execution errors, it reconstructs the traceback by replacing template frames with enhanced versions that provide accurate line number mappings.

## Args:
    source (Optional[str]): The source code of the template being processed, used to enhance error reporting for syntax errors. Defaults to None.

## Returns:
    BaseException: The original exception with its traceback rewritten to provide better debugging context for template errors.

## Raises:
    None explicitly raised - the function operates on the current exception context obtained via sys.exc_info()

## Constraints:
    Preconditions:
    - Must be called within an exception handler (sys.exc_info() must return valid exception information)
    - The current exception must be a BaseException subclass
    - Template frames in the traceback must have "__jinja_template__" in their globals

    Postconditions:
    - Returns the same exception instance with modified traceback
    - The traceback chain is properly reconstructed with filtered internal frames
    - Template line numbers are correctly mapped to source locations

## Side Effects:
    None directly observable - modifies the traceback chain of the current exception in-place through the with_traceback method

## Control Flow:
```mermaid
flowchart TD
    A[Start rewrite_traceback_stack] --> B[Get current exception info via sys.exc_info()]
    B --> C{Is TemplateSyntaxError and not translated?}
    C -- Yes --> D[Mark as translated, set source]
    D --> E[Create fake traceback for syntax error]
    C -- No --> F[Use next traceback frame]
    F --> G[Initialize empty stack]
    G --> H[Process traceback frames while not None]
    H --> I{Frame code in internal_code?}
    I -- Yes --> J[Skip internal frame, continue loop]
    I -- No --> K{Has __jinja_template__ in globals?}
    K -- Yes --> L[Get corresponding line number]
    L --> M[Create fake traceback with mapped line number]
    M --> N[Add to stack]
    K -- No --> O[Add original frame to stack]
    N --> P[Continue loop]
    O --> P
    P --> Q[Reverse stack order]
    Q --> R[Rebuild traceback chain]
    R --> S[Return exception with new traceback]
```

## Examples:
    # Typical usage in exception handling context
    try:
        # Template rendering code
        pass
    except Exception as e:
        # Rewrite traceback for better debugging
        rewritten_exception = rewrite_traceback_stack()
        raise rewritten_exception
    
    # Usage with source information for syntax errors
    try:
        # Template compilation code
        pass
    except TemplateSyntaxError as e:
        # Rewrite traceback with source context
        rewritten_exception = rewrite_traceback_stack(template_source)
        raise rewritten_exception

## `src.jinja2.debug.fake_traceback` · *function*

## Summary:
Creates a fake traceback for Jinja2 template exceptions to provide enhanced debugging information by simulating the original template execution context.

## Description:
This function generates a synthetic traceback that helps developers understand where template errors occurred by reconstructing the execution context. It's particularly useful for debugging template syntax and runtime errors by providing clearer location information than what would normally be available from the raw exception handling.

The function extracts template-local variables using `get_template_locals`, sets up appropriate global context variables, compiles a synthetic code snippet that raises the original exception, and executes it to generate a new traceback that points to the correct template location.

## Args:
    exc_value (BaseException): The original exception that occurred during template processing
    tb (Optional[TracebackType]): The original traceback object, or None if not available
    filename (str): The filename of the template where the error occurred
    lineno (int): The line number in the template where the error occurred

## Returns:
    TracebackType: A new traceback object pointing to the template location, with enhanced debugging context

## Raises:
    None explicitly raised - though the function itself catches and re-raises exceptions during execution

## Constraints:
    Preconditions:
    - exc_value must be a valid BaseException instance
    - filename should be a valid string representing a template file path
    - lineno should be a positive integer indicating the error line number
    - tb should either be a valid TracebackType or None

    Postconditions:
    - Returns a valid TracebackType object that can be used for exception chaining
    - The returned traceback accurately reflects the template location and context

## Side Effects:
    None directly observable - but internally uses sys.exc_info() to capture the generated traceback

## Control Flow:
```mermaid
flowchart TD
    A[Start fake_traceback] --> B{tb is not None?}
    B -- Yes --> C[Get template locals via get_template_locals]
    C --> D[Remove __jinja_exception__ from locals]
    B -- No --> E[Initialize empty locals dict]
    E --> F[Initialize globals dict]
    F --> G[Compile synthetic code with raise statement]
    G --> H[Set location string to "template"]
    H --> I{tb is not None?}
    I -- Yes --> J[Get function name from tb frame]
    J --> K{Function is "root"?}
    K -- Yes --> L[Set location to "top-level template code"]
    K -- No --> M{Function starts with "block_"?}
    M -- Yes --> N[Set location to block name]
    M -- No --> O[Keep location as "template"]
    I -- No --> P[Skip function analysis]
    O --> Q[Handle Python version compatibility]
    Q --> R{Python version >= 3.8?}
    R -- Yes --> S[Use code.replace(co_name=location)]
    R -- No --> T[Create new CodeType with location name]
    T --> U[Execute compiled code with globals and locals]
    S --> U
    U --> V[Exception caught during exec]
    V --> W[Return sys.exc_info()[2].tb_next]
```

## Examples:
    # Basic usage in template error handling
    try:
        # Template rendering code
        pass
    except Exception as e:
        # Create enhanced traceback for debugging
        enhanced_tb = fake_traceback(e, sys.exc_info()[2], "template.html", 42)
        # Use enhanced_tb for better error reporting

## `src.jinja2.debug.get_template_locals` · *function*

## Summary:
Extracts and processes template local variables from a mapping, handling context data and variable overrides based on depth.

## Description:
This function processes a mapping of local variables typically found in Jinja2 template execution contexts. It extracts context data when available and processes local variables that follow the naming convention "l_<depth>_<name>" to handle variable scoping and overrides. The function ensures that only the highest-depth version of each variable is retained, effectively implementing lexical scoping rules for template variables.

## Args:
    real_locals (Mapping[str, Any]): A mapping containing local variables from a template execution context, potentially including a "context" key and variables prefixed with "l_" followed by depth and variable name.

## Returns:
    Dict[str, Any]: A dictionary containing the processed template local variables, including context data and resolved local variables with proper scoping applied.

## Raises:
    None explicitly raised - though ValueError could be raised internally from string splitting operations, this is handled gracefully.

## Constraints:
    Preconditions:
    - real_locals should be a mapping-like object that supports .get() and .items() methods
    - Variables with names starting with "l_" should follow the pattern "l_<depth>_<name>"
    
    Postconditions:
    - The returned dictionary contains merged context data and processed local variables
    - Variable overrides are resolved based on depth (higher depth wins)
    - Missing variables are properly removed from the result

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_template_locals] --> B{ctx is not None?}
    B -- Yes --> C[Get ctx.get_all().copy()]
    B -- No --> D[data = {}]
    C --> E[data = ctx_data]
    D --> E
    E --> F[Initialize local_overrides]
    F --> G[Iterate real_locals.items()]
    G --> H{name starts with "l_" AND value is not missing?}
    H -- No --> I[Continue loop]
    H -- Yes --> J[Try split "l_<depth>_<name>"]
    J --> K{ValueError?}
    K -- Yes --> I
    K -- No --> L[Parse depth and name]
    L --> M[Get current depth for name]
    M --> N{cur_depth < depth?}
    N -- Yes --> O[Update local_overrides[name]]
    N -- No --> P[Skip update]
    O --> P
    P --> Q[Process local_overrides]
    Q --> R[Apply missing variable removals]
    R --> S[Apply variable assignments]
    S --> T[Return data]
```

## Examples:
    # Basic usage with context
    >>> locals_dict = {"context": mock_context, "l_0_var1": "value1"}
    >>> result = get_template_locals(locals_dict)
    >>> print(result)
    {'var1': 'value1'}  # Assuming context provides additional data
    
    # Usage with variable overrides
    >>> locals_dict = {
    ...     "l_0_var1": "low_priority",
    ...     "l_2_var1": "high_priority",
    ...     "l_1_var2": "value2"
    ... }
    >>> result = get_template_locals(locals_dict)
    >>> print(result)
    {'var1': 'high_priority', 'var2': 'value2'}
    
    # Usage with missing variables
    >>> locals_dict = {
    ...     "l_0_var1": "value1",
    ...     "l_1_var1": missing  # This would remove var1 from results
    ... }
    >>> result = get_template_locals(locals_dict)
    >>> print(result)
    {}  # var1 was removed due to missing value

