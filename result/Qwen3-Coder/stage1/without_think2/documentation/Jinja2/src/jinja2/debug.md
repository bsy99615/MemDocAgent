# `debug.py`

## `src.jinja2.debug.rewrite_traceback_stack` · *function*

## Summary:
Rewrites a traceback stack to provide clearer debugging information for Jinja2 template exceptions by filtering out internal frames and mapping template execution locations to their original template positions.

## Description:
This function processes the current exception's traceback to enhance debugging experience for Jinja2 template errors. It filters out internal implementation frames and translates template execution line numbers to their corresponding positions in the original template source. For TemplateSyntaxError exceptions, it also marks them as translated and attaches source information. The function creates a clean, user-friendly traceback that points directly to template locations rather than internal execution details.

Known callers within the codebase:
- Called during exception handling in template rendering pipelines when exceptions occur during template processing
- Typically triggered when template syntax errors or runtime errors occur during template execution

This logic is extracted into its own function to separate the concerns of exception handling and traceback manipulation from the main template execution flow, ensuring cleaner code organization and reusable debugging utilities.

## Args:
    source (str, optional): The source code of the template being processed. Defaults to None.

## Returns:
    BaseException: The original exception with a rewritten traceback that provides better debugging context for template errors.

## Raises:
    None explicitly raised - but may propagate exceptions from underlying operations like fake_traceback creation or traceback manipulation.

## Constraints:
    Preconditions:
    - Must be called within an exception handler (sys.exc_info() must contain an active exception)
    - The source parameter should be a valid string or None
    - The current exception must be a valid BaseException instance

    Postconditions:
    - Returns the same exception instance with modified traceback
    - The returned traceback will exclude internal implementation frames
    - Template execution line numbers will be mapped to original template positions

## Side Effects:
    - Modifies the current exception's traceback chain through sys.exc_info() manipulation
    - May alter the exception's internal state (e.g., setting translated=True for TemplateSyntaxError)
    - Uses sys.exc_info() to capture and modify the current exception context

## Control Flow:
```mermaid
flowchart TD
    A[Start rewrite_traceback_stack] --> B{Current exception is TemplateSyntaxError AND not translated?}
    B -- Yes --> C[Mark as translated]
    C --> D[Set source on exception]
    D --> E[Clear traceback with with_traceback(None)]
    E --> F[Create fake traceback for syntax error]
    B -- No --> G[Advance to next traceback frame]
    F --> G
    G --> H[Initialize empty stack]
    H --> I{Traceback frame is internal?}
    I -- Yes --> J[Skip internal frame]
    J --> K[Check for __jinja_template__ in globals]
    K -- Yes --> L[Get corresponding line number]
    L --> M[Create fake traceback for template]
    M --> N[Add to stack]
    K -- No --> O[Add original traceback to stack]
    O --> N
    N --> P{More traceback frames?}
    P -- Yes --> I
    P -- No --> Q[Reverse stack order]
    Q --> R[Rebuild traceback links]
    R --> S[Return exception with new traceback]
```

## Examples:
    # Typical usage in exception handling
    try:
        template.render(context)
    except Exception as e:
        # Rewriting traceback for better debugging
        raise rewrite_traceback_stack(template.source) from e
    
    # Handling syntax errors specifically
    try:
        env.from_string(template_source)
    except TemplateSyntaxError as e:
        # Rewriting traceback for syntax errors
        raise rewrite_traceback_stack(template_source) from e
```

## `src.jinja2.debug.fake_traceback` · *function*

## Summary:
Creates a synthetic traceback for Jinja2 template exceptions to provide meaningful debugging context.

## Description:
Generates a fake traceback that maps template execution errors back to their original template location and context. This function is used during template exception handling to create a more intuitive debugging experience by replacing the internal execution frame with a representation that shows where in the template the error occurred. It's particularly useful for providing clear error messages when template rendering fails.

## Args:
    exc_value (BaseException): The original exception that occurred during template rendering.
    tb (typing.Optional[TracebackType] or None): The original traceback object, or None if creating a fresh traceback.
    filename (str): The template filename where the error occurred.
    lineno (int): The line number in the template where the error occurred.

## Returns:
    TracebackType: A modified traceback object that provides better context for template debugging, pointing to the template location rather than internal implementation details.

## Raises:
    None explicitly raised - but may raise exceptions during code compilation or execution if invalid inputs are provided.

## Constraints:
    Preconditions:
    - The filename should be a valid path to a template file
    - The lineno should be a positive integer representing a line in the template
    - The exc_value should be a valid exception instance
    - When tb is provided, it should be a valid traceback object from template execution

    Postconditions:
    - Returns a valid traceback object that can be used for exception reporting
    - The returned traceback will have appropriate location information for template debugging
    - The traceback will indicate the correct template location (top-level, block, or general template)

## Side Effects:
    - Modifies the code object's co_name attribute to reflect template location
    - May modify global namespace with template-specific variables
    - Uses sys.exc_info() internally to capture the resulting traceback
    - May affect the current exception context through sys.exc_info()

## Control Flow:
```mermaid
flowchart TD
    A[Start fake_traceback] --> B{tb is not None?}
    B -- Yes --> C[Extract locals with get_template_locals]
    C --> D[Remove __jinja_exception__ from locals]
    B -- No --> E[Create empty locals dict]
    D --> F[Set up globals dict with filename and exception]
    F --> G[Compile template error code with proper line spacing]
    G --> H[Set location = "template"]
    H --> I{tb is not None?}
    I -- Yes --> J[Get function name from tb]
    J --> K{function == "root"?}
    K -- Yes --> L[location = "top-level template code"]
    K -- No --> M{function starts with "block_"?}
    M -- Yes --> N[location = f"block {function[6:]!r}"]
    M -- No --> O[Skip location update]
    L --> O
    N --> O
    O --> P{Python version >= 3.8?}
    P -- Yes --> Q[Use code.replace(co_name=location)]
    P -- No --> R[Create new CodeType with location]
    Q --> S[Execute compiled code]
    R --> S
    S --> T[Handle exception with exec]
    T --> U[Return sys.exc_info()[2].tb_next]
```

## Examples:
    # Basic usage in template exception handling
    try:
        template.render(context)
    except Exception as e:
        tb = fake_traceback(e, sys.exc_info()[2], "my_template.html", 15)
        # Now tb provides better debugging context for the template error
    
    # Usage when no existing traceback is available
    try:
        template.render(context)
    except Exception as e:
        tb = fake_traceback(e, None, "error_template.html", 5)
        # Creates a fresh traceback pointing to line 5 of the template

## `src.jinja2.debug.get_template_locals` · *function*

## Summary:
Extracts and merges template context data with local variable overrides from a debugging frame.

## Description:
Processes local variables from a Jinja2 template debug frame to extract context data and resolve local variable scoping. This function is primarily used in debugging contexts to provide a complete view of template variable state at a specific execution point. It merges context data with local variable overrides, ensuring only the highest-depth override is applied for each variable name.

## Args:
    real_locals (t.Mapping[str, t.Any]): A mapping of local variables from a template execution frame, typically obtained from inspecting a traceback or debugger. Expected to contain a "context" key referencing a Context object and local variables named with the pattern "l_{depth}_{variable_name}".

## Returns:
    t.Dict[str, t.Any]: A dictionary containing merged context data and resolved local variable overrides. Variables marked as missing are removed from the result, while others are set to their highest-depth override value.

## Raises:
    None explicitly raised - though ValueError may be raised internally during string parsing (when splitting variable names) which would propagate up.

## Constraints:
    Preconditions:
    - The input real_locals mapping should contain valid Python objects
    - Local variables with names starting with "l_" are processed as potential local overrides
    - Context object, if present, must have a get_all() method returning a dictionary
    - The "l_" prefixed variables must follow the naming convention "l_{depth}_{name}" where depth is an integer

    Postconditions:
    - The returned dictionary contains all context data plus resolved local variable overrides
    - Local variables marked as missing (using the 'missing' sentinel) are removed from the result
    - Only the highest-depth local variable override is preserved for each name
    - The returned dictionary is a copy and doesn't modify the original context data

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_template_locals] --> B{ctx is not None?}
    B -- Yes --> C[Get ctx.get_all().copy()]
    B -- No --> D[data = {}]
    C --> E[data = ctx.get_all().copy()]
    D --> E
    E --> F[Initialize local_overrides]
    F --> G[Iterate real_locals]
    G --> H{name starts with "l_" AND value is not missing?}
    H -- No --> I[Continue loop]
    H -- Yes --> J[Try split "l_{depth}_{name}"]
    J --> K{ValueError raised?}
    K -- Yes --> I
    K -- No --> L[Update local_overrides with depth/value]
    L --> M[Iterate local_overrides]
    M --> N{value is missing?}
    N -- Yes --> O[data.pop(name, None)]
    N -- No --> P[data[name] = value]
    O --> Q[End]
    P --> Q
```

## Examples:
    # Typical usage in debugging context
    debug_locals = {"context": template_context, "l_0_var1": "value1", "l_1_var1": "value2"}
    result = get_template_locals(debug_locals)
    # Result would contain merged context data with var1 overridden by "value2"
    
    # Handling missing variables
    debug_locals = {"context": template_context, "l_0_var1": missing}
    result = get_template_locals(debug_locals)
    # Result would contain merged context data with var1 removed if it existed

