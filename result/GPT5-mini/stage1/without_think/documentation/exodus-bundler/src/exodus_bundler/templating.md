# `templating.py`

## `src.exodus_bundler.templating.render_template` · *function*

## Summary:
Performs literal placeholder substitution in a text string by replacing every occurrence of {{key}} with the provided replacement value.

## Description:
This function performs a minimal, order-dependent templating pass: it iterates through the provided context mapping and for each (key, value) pair replaces all literal occurrences of the substring "{{key}}" in the input text with value.

Known callers within a typical repository usage:
    - Called during simple text- or file-rendering steps where small, trusted substitutions are needed (e.g., rendering a README fragment, configuration snippet, or CLI message) after context values are computed.
    - Typical trigger: a template-like string is available and the caller needs straightforward placeholder replacement without the overhead of a full templating engine.

Responsibility boundary:
    - Single responsibility: literal, sequential placeholder replacement.
    - Intentionally does not handle expression evaluation, escaping, conditional logic, loops, or advanced templating features. It does not sanitize or escape values.

## Args:
    string (str):
        - The input text containing zero or more placeholders in the exact form {{key}}.
        - Must be a Python text string (str). The function calls string.replace which requires a str receiver and operates on text.
    **context (keyword arguments: any -> any):
        - Mapping of placeholder names (keys) to replacement values.
        - Each key is converted to a string using the '%s' formatting operator to form the token name; e.g., key 1 becomes the token "{{1}}".
        - Each value is expected to be a str. Providing a non-str value will raise a TypeError when used as the replacement in str.replace.
        - Interdependencies:
            * Replacements are applied in the iteration order of context.items() (insertion order in Python 3.7+). Earlier replacements can create or remove substrings that later replacements may match (cascading effects).

## Returns:
    str:
        - The resulting string after applying all substitutions.
        - If a placeholder in the input has no corresponding key in context, that placeholder is left unchanged.
        - If context is empty or no keys match, the original string is returned unchanged (a new str object may still be returned).

## Raises:
    AttributeError:
        - If `string` does not support the replace method (for example, if string is None or an incompatible type), calling string.replace will raise AttributeError.
    TypeError:
        - If a replacement `value` is not a str (or otherwise not acceptable as the second argument to str.replace), str.replace will raise TypeError.
        - Note: keys are converted to str via '%s' so non-str keys will not raise here; they produce tokens formed from their str() representation.

## Constraints:
    Preconditions:
        - `string` must be a str (text string).
        - Context values should be str; keys may be any object (they will be converted to strings).
    Postconditions:
        - All literal substrings matching "{{key}}" (with key converted to str) for keys present in context will have been replaced by the corresponding values, applied in context iteration order.
        - No external state is modified.

## Side Effects:
    - None on external I/O, network, files, or global state. The function performs pure string transformation and returns a new string.
    - Logical side-effect within the produced string: because replacements are applied sequentially, replacement values that themselves contain placeholder-like substrings may be subject to later replacements (cascading substitution), altering the final string content.

## Control Flow:
flowchart TD
    A[Start: call render_template(string, **context)] --> B{Is string a str and has replace?}
    B -- No --> C[AttributeError when calling string.replace] --> Z[End]
    B -- Yes --> D{context empty?}
    D -- Yes --> E[Return original string]
    D -- No --> F[For each (key,value) in context.items() in iteration order]
    F --> G[Form token = "{{%s}}" % key  (key converted to str)]
    G --> H{token present in string?}
    H -- Yes --> I[string = string.replace(token, value)]
    H -- No --> J[No change for this key]
    I --> K{More keys?}
    J --> K
    K -- Yes --> F
    K -- No --> L[Return final string] --> Z[End]

## Examples:
1) Basic substitution
    Call: render_template("Hello, {{name}}!", name="Alice")
    Returns: "Hello, Alice!"

2) Non-string key (converted to str)
    Call: render_template("ID: {{1}}", **{1: "one"})
    Returns: "ID: one"  (key 1 is converted to "1" to form "{{1}}")

3) Missing key left intact
    Call: render_template("Value: {{x}}, Missing: {{y}}", x="10")
    Returns: "Value: 10, Missing: {{y}}"

4) Order-dependent / cascading replacement
    Call: render_template("A={{a}} B={{b}}", a="{{b}}", b="X")
    Possible outcome:
        - If ('a','{{b}}') is applied before ('b','X'): result becomes "A=X B=X".
        - Because replacements are sequential, avoid making replacement values that intentionally contain other placeholders unless this cascading is desired.

5) Error examples
    - Non-str replacement value:
        Call: render_template("Count: {{n}}", n=5)
        Raises: TypeError from str.replace because replacement value is not a str.
    - Non-str string argument:
        Call: render_template(None, any="x")
        Raises: AttributeError because NoneType has no replace method.

Notes and best practices:
    - For safe templating features (escaping, control structures, automatic type coercion), prefer a full templating library (e.g., Jinja2).
    - This function is suitable for small, trusted substitutions where keys may be non-string but replacement values are guaranteed to be strings.

## `src.exodus_bundler.templating.render_template_file` · *function*

## Summary:
Reads a template text file (absolute or relative to the module's template directory), applies literal placeholder substitution using the provided context, and returns the rendered text.

## Description:
This function centralizes the common pattern of loading a template from disk and performing in-memory placeholder substitution. It resolves relative filenames against a module-level template_directory (joining the directory and the given filename), opens the file for reading, reads its entire contents as text, and delegates the placeholder substitution to the render_template function (which performs literal "{{key}}" -> value replacements in iteration order).

Known callers within the codebase:
    - No direct callers were discovered in the provided context. Typical callers are repository components that need to render small text templates stored as files (e.g., README fragments, configuration snippets, CLI help text) where a lightweight literal substitution is sufficient. Callers usually invoke this during build or bundle preparation steps when a file-based template must be turned into a final text artifact.

Responsibility boundary:
    - Responsibility: file path resolution (absolute vs. relative), file reading, and delegating text substitution to render_template.
    - Boundary: it does not perform any writing, validation of context values, escaping, or advanced templating logic. Those concerns are delegated to callers or to a full template engine.

## Args:
    filename (str):
        - Path to the template file. May be an absolute path or a path relative to the module's template_directory.
        - Must be a text string (str). Passing a non-str filename will cause os.path.isabs to implicitly accept it if it supports the path protocol, otherwise a TypeError may occur.
        - If a relative path is provided, the function attempts to resolve it by joining template_directory and filename. The module-level variable template_directory must exist and be a valid path-like str; otherwise a NameError will be raised.
    **context (keyword arguments: any -> any):
        - Placeholder names to replacement values forwarded to render_template.
        - Keys are used (after conversion to string by render_template) to form tokens of the exact form {{key}}.
        - Values are expected to be str; non-str values will typically raise TypeError when render_template attempts str.replace with a non-str replacement.
        - Replacements are applied in the iteration order of the provided keyword mapping; earlier replacements can influence later matches (cascading effects).

## Returns:
    str:
        - The fully rendered template text returned by render_template after applying all substitutions.
        - On success, always returns the value returned by render_template (documented to be a str). If the file exists but contains no matching tokens, the file content (possibly unchanged) is returned.
        - No None or other sentinel return values are produced by this function itself.

## Raises:
    NameError:
        - If a relative filename is provided and the module-level variable template_directory is not defined, accessing template_directory will raise NameError.

    FileNotFoundError:
        - Raised when the resolved filename does not exist on disk and open() attempts to read it.

    PermissionError:
        - Raised when the file exists but the running process lacks permission to open it for reading.

    IsADirectoryError:
        - Raised if the resolved path points to a directory rather than a regular file and open() is called.

    OSError (generic):
        - Other low-level OS errors encountered by open() or file reading (I/O errors, file system errors) are propagated.

    UnicodeDecodeError:
        - If the file contains bytes that cannot be decoded by the system default encoding used by open(), a UnicodeDecodeError may be raised while reading.

    AttributeError / TypeError:
        - Errors propagated from render_template:
            * AttributeError if render_template is given a non-str (e.g., render_template expects to call str.replace on the input text).
            * TypeError if a replacement value provided in context is not an acceptable type for str.replace.
        - These occur only if the file contents are not a str or context contains non-str replacement values (as described in render_template's documentation).

## Constraints:
    Preconditions:
        - filename should be a path-like text string.
        - If a relative filename is used, template_directory must be defined at module scope and be a valid path string.
        - The caller must ensure context values are strings when string replacement semantics are desired.

    Postconditions:
        - The file at the resolved path has been opened and fully read into memory (no file handle remains open after return because the file is opened with a context manager).
        - The returned string reflects render_template's sequential replacements applied to the file contents.
        - No files are created or modified by this function.

## Side Effects:
    - Performs file I/O: opens and reads the specified file from disk.
    - Relies on module-level state:
        * template_directory (read-only): used when filename is relative.
        * render_template (callable): used to perform substitutions; its behavior affects the final result and possible exceptions.
    - No network calls, no writes to disk, no modifications of global variables by this function itself.

## Control Flow:
flowchart TD
    A[Start: call render_template_file(filename, **context)] --> B{Is filename an absolute path?}
    B -- No --> C[Resolve filename = os.path.join(template_directory, filename)]
    C --> D[Attempt open(resolved filename,'r') with context manager]
    B -- Yes --> D
    D --> E{open() succeeds?}
    E -- No --> F[Propagate FileNotFoundError/PermissionError/IsADirectoryError/OSError] --> Z[End]
    E -- Yes --> G[Read entire file content into a string]
    G --> H[Call render_template(file_content, **context)]
    H --> I{render_template raises?}
    I -- Yes --> J[Propagate AttributeError/TypeError from render_template] --> Z[End]
    I -- No --> K[Return rendered string] --> Z[End]

## Examples:
1) Absolute path usage
    Call: render_template_file("/etc/templates/welcome.txt", name="Alice")
    Behavior: The function opens /etc/templates/welcome.txt, reads the content (e.g., "Hello, {{name}}!"), calls render_template(..., name="Alice"), and returns "Hello, Alice!".

2) Relative path resolved against template_directory
    - Precondition: module variable template_directory is set to "/opt/myapp/templates"
    Call: render_template_file("header.txt", version="1.2")
    Behavior: The function resolves path to "/opt/myapp/templates/header.txt", reads it, substitutes tokens like {{version}} and returns the rendered text.

3) Error handling example
    Try:
        Call: render_template_file("missing.txt")
    Possible outcome:
        - If "/.../templates/missing.txt" does not exist, FileNotFoundError is raised.
        - Caller should catch FileNotFoundError to provide fallback behavior (e.g., log and continue).

Notes and best practices:
    - Ensure template_directory is defined and points to the intended templates folder when passing relative filenames.
    - Provide context values as strings to avoid TypeError from underlying str.replace operations performed by render_template.
    - For larger or untrusted templates, prefer a full-featured templating engine (e.g., Jinja2) that provides escaping and richer features.

