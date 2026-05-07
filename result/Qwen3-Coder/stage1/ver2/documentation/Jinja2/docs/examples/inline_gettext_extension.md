# `inline_gettext_extension.py`

## `docs.examples.inline_gettext_extension.InlineGettext` · *class*

*No documentation generated.*

### `docs.examples.inline_gettext_extension.InlineGettext.filter_stream` · *method*

## Summary:
Converts gettext expressions in template data tokens into Jinja2 template blocks for translation processing.

## Description:
Processes a stream of Jinja2 template tokens, identifying and converting gettext expressions (such as _("hello world")) in data tokens into proper Jinja2 template blocks using 'trans' and 'endtrans' constructs. This method is part of the InlineGettext Jinja2 extension that enables inline internationalization within templates.

The method handles nested parentheses in gettext expressions by maintaining a parenthesis stack counter. It transforms text like _("hello world") into Jinja2 template blocks: {% trans %}hello world{% endtrans %}. The method preserves line numbers and properly manages token positioning during transformation.

This logic is separated into its own method to encapsulate the complex token transformation logic and maintain clean separation of concerns within the Jinja2 extension architecture.

## Args:
    stream: An iterator of Jinja2 tokens to process

## Returns:
    Generator of Jinja2 tokens where gettext expressions in data tokens have been converted to proper template blocks

## Raises:
    TemplateSyntaxError: When a gettext expression is not properly closed with matching parentheses

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Input stream must be a valid iterator of Jinja2 tokens with appropriate attributes
    - Tokens must have 'type', 'value', and 'lineno' attributes
    - The method assumes _outside_re and _inside_re regex patterns are defined in the class scope
    
    Postconditions:
    - All gettext expressions in data tokens are converted to proper Jinja2 template blocks
    - Line numbers are preserved throughout the transformation
    - Proper nesting of parentheses in gettext expressions is maintained
    - The resulting token stream is valid for further Jinja2 processing

## Side Effects:
    None - This is a pure transformation method that yields new tokens without side effects

