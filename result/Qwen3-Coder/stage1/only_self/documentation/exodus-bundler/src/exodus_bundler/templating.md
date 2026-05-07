# `templating.py`

## `src.exodus_bundler.templating.render_template` · *function*

## Summary:
Replaces template placeholders in a string with corresponding values from a context dictionary.

## Description:
Processes a string containing template placeholders in the format `{{key}}` and substitutes them with values from the provided context. This function enables basic string templating functionality for dynamic content generation. The replacement process iterates through all context items and replaces all occurrences of each placeholder.

## Args:
    string (str): The template string containing placeholders in `{{key}}` format.
    **context (dict): Keyword arguments mapping placeholder names to their replacement values.

## Returns:
    str: The input string with all matching placeholders replaced by their corresponding context values.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - The input string must be a valid string object.
    - All keys in context must be strings to enable proper replacement.
    
    Postconditions:
    - The returned string will have all matching placeholders replaced.
    - If a placeholder key is not found in context, it remains unchanged in the output.
    - Placeholder replacement is performed sequentially for each context item.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start render_template] --> B{string is valid?}
    B -- Yes --> C[Iterate through context items]
    C --> D{Key exists in string?}
    D -- Yes --> E[Replace {{key}} with value]
    E --> F[Update string]
    F --> G{More context items?}
    G -- Yes --> C
    G -- No --> H[Return processed string]
    B -- No --> I[Return original string]
```

## Examples:
    >>> render_template("Hello {{name}}!", name="World")
    "Hello World!"
    
    >>> render_template("{{greeting}} {{name}}", greeting="Hi", name="Alice")
    "Hi Alice"
    
    >>> render_template("No placeholders here")
    "No placeholders here"
    
    >>> render_template("Multiple {{item}}s: {{item}} and {{item}}", item="apple")
    "Multiple apples: apple and apple"
```

## `src.exodus_bundler.templating.render_template_file` · *function*

*No documentation generated.*

