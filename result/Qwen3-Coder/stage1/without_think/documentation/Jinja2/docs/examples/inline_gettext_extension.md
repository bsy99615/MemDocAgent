# `inline_gettext_extension.py`

## `docs.examples.inline_gettext_extension.InlineGettext` · *class*

## Summary:
An extension for Jinja2 template processing that converts inline gettext expressions into proper Jinja2 translation blocks.

## Description:
The InlineGettext class is a Jinja2 extension that processes template streams to transform special inline gettext syntax (such as `_(...)`) into proper Jinja2 translation blocks. It extends the base Extension class and implements the filter_stream method to intercept and modify template token streams during template compilation.

This extension enables developers to write internationalized templates using convenient inline syntax that gets converted to standard Jinja2 translation constructs during template compilation. The extension specifically targets data tokens in the template stream and processes them to identify and convert gettext expressions.

## State:
- The class inherits from jinja2.ext.Extension and doesn't define any instance attributes beyond what's inherited
- The filter_stream method uses a local variable `paren_stack` to track nesting levels of parentheses in gettext expressions
- The method processes tokens from the template stream and modifies data tokens containing gettext expressions

## Lifecycle:
- Creation: Instantiated as part of Jinja2 environment configuration; no special construction requirements
- Usage: Automatically invoked by Jinja2 during template compilation when the extension is registered
- Destruction: Managed by Jinja2's lifecycle management; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[filter_stream] --> B{token.type == "data"?}
    B -- Yes --> C[Process data token]
    B -- No --> D[Yield original token]
    C --> E[Initialize paren_stack]
    E --> F[Loop through matches]
    F --> G{Match found?}
    G -- No --> H[End loop]
    G -- Yes --> I{Inside parentheses?}
    I -- No --> J[Look for outside pattern match]
    I -- Yes --> K[Look for inside pattern match]
    J --> L{Match group starts with "\"?}
    L -- Yes --> M[Yield escaped character]
    L -- No --> N[Yield trans block begin]
    N --> O[Yield trans name]
    O --> P[Yield trans block end]
    P --> Q[Set paren_stack = 1]
    K --> R{Match group == "(" or paren_stack > 1?}
    R -- Yes --> S[Yield data token]
    R -- No --> T[Update paren_stack]
    T --> U{paren_stack == 0?}
    U -- Yes --> V[Yield endtrans block begin]
    V --> W[Yield endtrans name]
    W --> X[Yield endtrans block end]
    H --> Y[Yield remaining data]
    Y --> Z[Return]
```

## Raises:
- TemplateSyntaxError: Raised when there are unclosed gettext expressions in the template stream, indicating malformed gettext syntax

## Example:
```python
# Register the extension with a Jinja2 environment
from jinja2 import Environment
from docs.examples.inline_gettext_extension import InlineGettext

env = Environment(extensions=[InlineGettext])
template = env.from_string('Hello {{ name }}! _(Welcome message)')
# The template will be processed to convert _(Welcome message) into proper Jinja2 translation blocks
```

### `docs.examples.inline_gettext_extension.InlineGettext.filter_stream` · *method*

## Summary:
Converts inline gettext expressions in template data tokens into proper Jinja2 trans/endtrans template blocks.

## Description:
This method is part of the InlineGettext Jinja2 Extension and processes template token streams to transform inline gettext syntax (like `_(...)`) into proper Jinja2 template blocks. It specifically targets "data" tokens containing gettext expressions and converts them into `trans`...`endtrans` blocks that Jinja2 can properly process for internationalization.

The method implements a sophisticated parsing algorithm that handles nested parentheses within gettext expressions using a parenthesis stack mechanism. It only processes data tokens, preserving all other token types unchanged.

## Args:
    stream: An iterator of Jinja2 tokens representing a parsed template

## Returns:
    Generator yielding Jinja2 tokens with inline gettext expressions converted to proper template syntax

## Raises:
    TemplateSyntaxError: When encountering unclosed gettext expressions in the template

## State Changes:
    Attributes READ: None - this method accesses no instance attributes
    Attributes WRITTEN: None - this method modifies no instance attributes

## Constraints:
    Preconditions: 
    - Input stream must be a valid Jinja2 token stream
    - Class must define `_outside_re` and `_inside_re` regex patterns (likely at class level)
    - Method assumes proper Jinja2 token structure
    
    Postconditions:
    - All valid gettext expressions in data tokens are converted to proper Jinja2 trans/endtrans blocks
    - The returned token stream maintains proper line numbering and token types
    - Unclosed expressions raise TemplateSyntaxError with appropriate context

## Side Effects:
    None - this method is pure and doesn't cause any external I/O or mutations

