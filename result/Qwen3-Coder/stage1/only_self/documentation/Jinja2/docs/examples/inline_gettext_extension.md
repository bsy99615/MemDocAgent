# `inline_gettext_extension.py`

## `docs.examples.inline_gettext_extension.InlineGettext` · *class*

## Summary:
A Jinja2 extension that converts inline gettext expressions into proper Jinja2 translation blocks.

## Description:
This class extends Jinja2's Extension base class to preprocess template streams by transforming inline gettext function calls (such as _("hello world")) into standard Jinja2 translation blocks using trans/endtrans constructs. This enables internationalization of templates while allowing developers to use familiar gettext syntax.

During template compilation, the extension processes data tokens in the stream, identifying gettext expressions using internal regular expressions and converting them into appropriate Jinja2 syntax. The transformation handles nested parentheses and maintains proper line number tracking for error reporting.

## State:
- `paren_stack`: Integer counter tracking nesting levels of parentheses in gettext expressions
- The class has no other persistent state attributes

## Lifecycle:
- Creation: Instantiated as part of Jinja2 environment configuration when the extension is registered
- Usage: Automatically invoked by Jinja2 engine during template compilation when the extension is enabled
- Destruction: Managed by Jinja2's extension lifecycle management

## Method Map:
```mermaid
graph TD
    A[filter_stream] --> B{token.type == "data"?}
    B -- Yes --> C[Parse data token for gettext expressions]
    B -- No --> D[Yield token unchanged]
    C --> E{Match found with _outside_re/_inside_re?}
    E -- Yes --> F[Process match based on paren_stack state]
    F --> G{Escape sequence?}
    G -- Yes --> H[Yield escaped character]
    G -- No --> I{Paren stack 0?}
    I -- Yes --> J[Yield trans block begin]
    I -- No --> K{Parentheses handling}
    K --> L[Yield data or endtrans block]
    E -- No --> M[Yield remaining token content]
    C --> N{Remaining unprocessed content?}
    N -- Yes --> O[Yield remaining data]
```

## Raises:
- TemplateSyntaxError: Raised when encountering unclosed gettext expressions in the template stream, indicating malformed inline gettext syntax

## Example:
```python
# Register extension with Jinja2 environment
from jinja2 import Environment
env = Environment(extensions=['docs.examples.inline_gettext_extension.InlineGettext'])

# Template containing inline gettext - this gets transformed internally
template_source = 'Hello {{ _("world") }}!'
template = env.from_string(template_source)
result = template.render()

# The inline _("world") becomes equivalent to:
# {% trans %}world{% endtrans %}
```

### `docs.examples.inline_gettext_extension.InlineGettext.filter_stream` · *method*

## Summary:
Processes a Jinja2 template stream to convert gettext expressions into proper translation blocks by identifying and transforming text tokens containing function calls like `_()`.

## Description:
This method filters a Jinja2 template token stream, specifically targeting "data" tokens that contain gettext function calls (such as `_("Hello")`). It uses regular expressions to identify these expressions and converts them into proper Jinja2 translation blocks using `{% trans %}` and `{% endtrans %}` syntax. The method maintains a parenthesis stack to correctly handle nested parentheses within gettext expressions.

During processing, the method splits data tokens when gettext expressions are found, yielding appropriate token types including data, block_begin, name, and block_end tokens. Line numbers are properly maintained when splitting tokens. The method is designed to be used as part of the Jinja2 extension system during template compilation.

## Args:
    stream: A Jinja2 token stream to process

## Returns:
    Generator yielding modified tokens where gettext expressions are converted to proper Jinja2 trans/endtrans blocks

## Raises:
    TemplateSyntaxError: When there are unclosed gettext expressions in the template

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The stream must be a valid Jinja2 token stream with proper token structure
    Postconditions: All gettext expressions in data tokens are properly converted to trans/endtrans blocks, maintaining proper line numbering

## Side Effects:
    None

