# `inline_gettext_extension.py`

## `docs.examples.inline_gettext_extension.InlineGettext` · *class*

## Summary:
A Jinja2 template extension that converts inline gettext expressions into proper Jinja2 translation blocks.

## Description:
This class extends Jinja2's template processing by implementing a filter_stream method that transforms text tokens containing gettext expressions (like _("hello")) into proper Jinja2 translation blocks. It enables inline internationalization within Jinja2 templates by converting expressions into the appropriate Jinja2 syntax.

The extension processes template streams token by token, identifying text content that contains gettext expressions and converting them into Jinja2 trans/endtrans blocks.

## State:
- `paren_stack`: Integer representing the nesting level of parentheses in gettext expressions. Starts at 0 and is incremented/decremented based on parenthesis matching to track nested expressions.

## Lifecycle:
- Creation: Instantiated as part of a Jinja2 environment configuration. Inherits from jinja2.ext.Extension and requires no special constructor arguments.
- Usage: Automatically invoked during template compilation when the extension is registered with a Jinja2 Environment via the extensions parameter.
- Destruction: Managed automatically by Jinja2's extension lifecycle management.

## Method Map:
```mermaid
graph TD
    A[Template Compilation] --> B[filter_stream Called]
    B --> C[Iterate Through Stream Tokens]
    C --> D{Token Type}
    D -->|Not "data"| E[Yield Original Token]
    D -->|Is "data"| F[Process Text Content]
    F --> G{Parentheses Level}
    G -->|Outside| H[Search _outside_re]
    G -->|Inside| I[Search _inside_re]
    H --> J{Match Found?}
    J -->|Yes| K[Process Match]
    J -->|No| L[End Parsing]
    K --> M{Match Content}
    M -->|Escape| N[Yield Escaped Text]
    M -->|Opening| O[Yield trans Block]
    M -->|Closing| P[Yield endtrans Block]
    P --> Q[Update Parentheses Stack]
    Q --> R{Stack Empty?}
    R -->|Yes| S[Yield endtrans Block]
    R -->|No| T[Continue Parsing]
```

## Raises:
- `TemplateSyntaxError`: Raised when encountering unclosed gettext expressions in templates, specifically when paren_stack is non-zero after processing all tokens.

## Example:
```python
from jinja2 import Environment
from docs.examples.inline_gettext_extension import InlineGettext

# Register the extension with a Jinja2 environment
env = Environment(extensions=[InlineGettext])

# Template containing inline gettext expressions
template_source = '''
<p>{{ _("Hello, {name}!") }}</p>
<p>{{ _("Welcome back") }}</p>
'''

# The extension will automatically convert these to proper Jinja2 translation blocks
template = env.from_string(template_source)
```

### `docs.examples.inline_gettext_extension.InlineGettext.filter_stream` · *method*

## Summary:
Processes a Jinja2 template stream to convert inline gettext expressions into proper template blocks.

## Description:
This method transforms raw template data tokens containing inline gettext expressions (like `_(...)`) into structured Jinja2 template blocks. It handles parsing of nested parentheses and ensures proper opening/closing of translation blocks while maintaining line number tracking for error reporting.

The method is part of the InlineGettext extension and operates on a stream of tokens, converting text containing gettext expressions into appropriate template syntax. This approach allows for seamless integration of inline translations within templates without requiring users to manually write full translation blocks.

## Args:
    stream: An iterable of Jinja2 tokens representing the template stream to process

## Returns:
    Generator of Jinja2 tokens with inline gettext expressions converted to proper template blocks

## Raises:
    TemplateSyntaxError: When encountering unclosed gettext expressions in the template stream

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input stream must contain valid Jinja2 tokens with proper token types
    Postconditions: All inline gettext expressions in the stream are properly converted to trans/endtrans blocks

## Side Effects:
    None

