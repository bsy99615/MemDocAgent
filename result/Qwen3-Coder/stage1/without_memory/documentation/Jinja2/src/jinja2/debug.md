# `debug.py`

## `src.jinja2.debug.rewrite_traceback_stack` · *function*

## Summary:
Rewrites traceback information to provide clearer debugging context for Jinja2 template errors by filtering internal frames and mapping template line numbers to source locations.

## Description:
This function processes exception tracebacks to improve debugging experience when Jinja2 templates fail. It removes internal implementation frames from the traceback, maps template line numbers to actual source line numbers, and constructs a cleaner traceback that points to user-facing template code rather than Jinja2's internal machinery.

The function is typically called when handling exceptions during template rendering to provide more meaningful error messages to developers. It's extracted into its own function to encapsulate the complex traceback manipulation logic and maintain clean separation between template execution and error reporting.

## Args:
    source (str, optional): The source code of the template being processed. Defaults to None.

## Returns:
    BaseException: The exception with its traceback rewritten to provide better debugging information.

## Raises:
    None explicitly raised - delegates to underlying exception handling mechanisms.

## Constraints:
    Preconditions:
    - Must be called within an exception handler (sys.exc_info() must contain an active exception)
    - The exception must be either a TemplateSyntaxError or a regular exception
    
    Postconditions:
    - The returned exception has a cleaned-up traceback chain
    - TemplateSyntaxError instances are marked as translated
    - Internal Jinja2 frames are filtered out from the traceback

## Side Effects:
    None - This function only manipulates traceback objects and doesn't perform I/O or modify external state.

## Control Flow:
```mermaid
flowchart TD
    A[Get current exception info] --> B{Is TemplateSyntaxError AND not translated?}
    B -- Yes --> C[Mark as translated]
    C --> D[Set source]
    D --> E[Create fake traceback]
    E --> F[Set tb = fake_traceback result]
    B -- No --> F[Set tb = tb.tb_next]
    F --> G[Initialize empty stack]
    G --> H{tb is not None?}
    H -- Yes --> I[Check if frame is internal code]
    I -- Yes --> J[Skip frame, continue loop]
    J --> K{Template found in globals?}
    K -- Yes --> L[Get corresponding line number]
    L --> M[Create fake traceback for template]
    M --> N[Add to stack]
    K -- No --> O[Add original tb to stack]
    O --> P[Move to next frame]
    P --> H
    H -- No --> Q[Reverse stack order]
    Q --> R[Rebuild traceback links]
    R --> S[Return exception with new traceback]
```

## Examples:
```python
try:
    # Template rendering code that might raise an exception
    template.render(context)
except Exception as e:
    # Rewrite traceback for better debugging
    raise rewrite_traceback_stack(template_source) from e
```

## `src.jinja2.debug.fake_traceback` · *function*

*No documentation generated.*

## `src.jinja2.debug.get_template_locals` · *function*

*No documentation generated.*

