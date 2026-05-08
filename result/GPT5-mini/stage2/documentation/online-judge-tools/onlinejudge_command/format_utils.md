# `format_utils.py`

## `onlinejudge_command.format_utils.percentsplit` · *function*

## Summary:
Splits an input string into an iterator of segments where single characters that are not '%' are yielded as single-character items and sequences beginning with '%' are yielded together with the following character (e.g., "%x"), effectively grouping percent-escapes with their immediate follower.

## Description:
This function iterates over an input string and yields successive segments according to a two-alternative pattern:
- any single character that is not the percent sign '%' (each yielded as a 1-character string), or
- a percent sign followed by one character (yielded as a 2-character string beginning with '%').

Known callers:
- No direct callers were found in the provided repository snapshot for this function. Typical usage in codebases is to feed the resulting segments into a formatter or parser that needs to treat percent-escapes (like "%s", "%d", "%%") as indivisible tokens while processing other characters one-by-one.

Why extracted into a helper:
- This logic isolates the tokenization rule for percent escapes so higher-level formatting/parsing code can iterate tokens without reimplementing or repeating the regular expression and edge-case handling.
- It enforces a single responsibility: tokenizing percent sequences vs. non-% characters, improving testability and reuse.

## Args:
    s (str): Input string to split.
        - Required: must be a Python str.
        - Allowed contents: any characters. The function distinguishes '%' vs non-'%' characters.
        - Interdependencies: none.

## Returns:
    Generator[str, None, None]: A generator that yields segments (strings). Each yielded value is either:
        - a single-character string consisting of a non-'%' character, or
        - a two-character string that begins with '%' followed by the character that immediately follows it in the input.
    Notes on possible return sequences:
        - For a normal character sequence like "abc" the generator yields "a","b","c".
        - For a percent escape sequence like "a%sb" the generator yields "a","%s","b".
        - For consecutive percent characters "%%" the generator yields "%%".
        - A trailing solitary '%' with no following character is not matched by the pattern and therefore is not yielded (it is effectively dropped).

## Raises:
    TypeError: If the provided s is not coercible to a string (for example, passing None will typically cause re.finditer to raise a TypeError).
    (No exceptions are raised intentionally by the function body; any regex engine errors are not expected because the pattern is static and valid.)

## Constraints:
Preconditions:
    - s must be a str (or an object acceptable to re.finditer as a string). Passing non-str may raise TypeError.
    - Caller should be aware that a trailing '%' is not preserved by this tokenization.

Postconditions:
    - Concatenating all yielded segments in order produces the original input string except for an unmatched trailing '%' (if present), which is omitted.
    - Every yielded segment is non-empty and its length is either 1 (non-'%') or 2 (a '%' plus one following character).

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and makes no external calls beyond using the Python regex engine.

## Control Flow:
flowchart TD
    A[Start: receive s (str)] --> B[Call re.finditer with pattern '[^%]|%(.)']
    B --> C{Next match found?}
    C -- No --> D[End: generator exhausted]
    C -- Yes --> E[Get match m]
    E --> F[Yield m.group(0)]
    F --> C

Decision branch explanation:
- The regex alternation yields either a single non-'%' character or a '%' plus the next character. If no match remains (for example when s ends with an unmatched '%'), iteration ends and nothing more is yielded.

## Examples:
- Basic splitting:
    list(percentsplit("hello")) -> ["h", "e", "l", "l", "o"]

- Percent-escape grouping:
    list(percentsplit("a%sb")) -> ["a", "%s", "b"]

- Consecutive percent signs:
    list(percentsplit("x%%y")) -> ["x", "%%", "y"]

- Trailing percent is dropped:
    list(percentsplit("end%")) -> ["e", "n", "d"]    (note: the final solitary '%' has no follower and is not yielded)

- Typical usage pattern for reconstruction or formatting:
    - Iterate over the generator; for tokens that start with '%', treat them as escape sequences (inspect second character) and for single characters append/process directly.

## `onlinejudge_command.format_utils.percentformat` · *function*

## Summary:
Replaces percent-escape tokens in a template string by looking up each escape's single-character key in the provided mapping and returns the resulting concatenated string.

## Description:
This function implements a simple percent-based templating substitution: the input string is tokenized so that each percent-escape (a '%' followed by one character, e.g., "%s", "%%", "%d") is treated as a single token; for each percent token the function looks up the mapping for the token's second character and appends that mapped string to the result, while non-percent characters are appended unchanged.

Known callers:
- No direct callers were found in the provided repository snapshot.
- Typical usage patterns: invoked from higher-level formatting or template rendering utilities to apply a dictionary of single-character substitution rules to a template string. It is useful in pipelines that parse a template into tokens (via percentsplit) and then need a deterministic substitution step.

Why this is a separate function:
- It isolates the substitution semantics (lookup, concatenation, and error/edge-case behavior) from tokenization and higher-level template logic.
- It centralizes validation (the assert about '%' mapping) and the side-effect (ensuring table['%'] == '%'), so callers don't need to reimplement these checks.
- Keeping this logic separate improves testability and reuse for any component that needs percent-style replacement.

## Args:
    s (str):
        - The input template string containing normal characters and percent-escapes.
        - Must be a Python str. Passing non-str values may cause underlying tokenization to raise a TypeError.
    table (Dict[str, str]):
        - A mutable mapping from single-character keys (strings of length 1) to replacement strings.
        - For a percent-escape token "%x" the code uses table['x'] to obtain the replacement.
        - If the caller provides the '%' key in table it MUST map to the literal '%' (i.e., table['%'] == '%'); otherwise an AssertionError is raised.
        - The function will set table['%'] = '%' unconditionally (after the assertion), mutating the input mapping.

Interdependencies:
    - The function relies on percentsplit(s) to produce tokens. percentsplit yields either single non-'%' characters or two-character tokens that begin with '%' and contain the escape key as the second character.
    - Because of the reliance on percentsplit, a trailing solitary '%' in the input string is dropped by tokenization and will not provoke a lookup.

## Returns:
    str:
        - The concatenation of literal characters and the mapped replacements for percent-escape tokens, in original order.
        - Examples of possible outputs:
            - Normal characters are preserved: percentformat("abc", table) -> "abc"
            - Substituted tokens: percentformat("a%sb", {'s': 'X'}) -> "aXb"
            - A "%%" token results in the substitution table['%'] which is forced to be '%' by the function (so "%%" becomes "%").

Edge-case returns:
    - If percentsplit drops a trailing lone '%' (no follower), that '%' will not appear in the returned string because no token is produced for it.

## Raises:
    AssertionError:
        - If table contains the '%' key but its value is not the literal '%' (i.e., table['%'] != '%'), the function asserts and raises AssertionError before mutating the table.
    KeyError:
        - If percentsplit yields a percent token "%x" but table does not contain key 'x', the expression table[c[1]] raises KeyError.
    TypeError:
        - If a table value for a matched key is not a str (e.g., an int), Python string concatenation (result += table[c[1]]) will raise TypeError.
        - If s is not a str and percentsplit or its regex-based implementation rejects the input, a TypeError may propagate from the tokenizer.

## Constraints:
Preconditions:
    - s must be a str (or an object acceptable to percentsplit's implementation).
    - table must be a dict-like mapping supporting key lookup and assignment with string keys.
    - If table contains '%', it must map to '%'.

Postconditions:
    - table['%'] will exist and be set to '%' when the function returns normally (i.e., after successful completion).
    - The returned string is a sequence of the original non-'%' characters and replacement strings looked up from table for each percent-escape token, in order.
    - No trailing solitary '%' (if present in s) will be preserved in the output because percentsplit does not yield it.

## Side Effects:
    - Mutates the provided table by assigning table['%'] = '%'. If the assignment occurs, the caller's mapping is modified in place.
    - No I/O, no network, no global state changes besides the table mutation.

## Control Flow:
flowchart TD
    Start([Start: percentformat(s, table)]) --> AssertCheck{Is '%' not in table OR table['%'] == '%'?}
    AssertCheck -- No --> RaiseAssertion[Raise AssertionError and exit]
    AssertCheck -- Yes --> SetPercent[Set table['%'] = '%']
    SetPercent --> InitRes[Initialize result = ""]
    InitRes --> TokenLoop[For each token c from percentsplit(s)]
    TokenLoop --> IsPercent{Does c start with '%'?}
    IsPercent -- Yes --> Lookup[Lookup replacement = table[c[1]]]
    Lookup --> AppendRep[Append replacement to result]
    AppendRep --> TokenLoop
    IsPercent -- No --> AppendChar[Append c to result]
    AppendChar --> TokenLoop
    TokenLoop --> Return[Return result]

Notes on exceptional control flow:
    - If assertion fails the function raises AssertionError and does not assign table['%'].
    - If a lookup fails (missing key) a KeyError is raised and the function exits with partial side-effects (table['%'] may already have been set).
    - If a lookup value is not a str, concatenation raises TypeError.

## Examples:
- Basic substitution:
    >>> s = "Hello, %n!"
    >>> table = {'n': 'World'}
    >>> percentformat(s, table)
    "Hello, World!"
    # After call: table contains {'n': 'World', '%': '%'}

- Literal percent using "%%":
    >>> s = "Completed: 100%%"
    >>> table = {}
    >>> percentformat(s, table)
    "Completed: 100%"
    # table becomes {'%': '%'}

- Missing key -> KeyError:
    >>> s = "Value: %x"
    >>> table = {}
    >>> percentformat(s, table)
    KeyError: 'x'  # (raised because 'x' is not present in table)

- Assertion error when caller provides incompatible '%' mapping:
    >>> s = "100%%"
    >>> table = {'%': '!'}
    >>> percentformat(s, table)
    AssertionError  # function asserts that table['%'] == '%'

- Non-string table value -> TypeError on concatenation:
    >>> s = "Number: %d"
    >>> table = {'d': 42}
    >>> percentformat(s, table)
    TypeError  # because result += 42 is invalid

Implementation notes for reimplementation:
    - Use percentsplit(s) to iterate tokens. percentsplit yields tokens that are either a single non-'%' character or a two-character token beginning with '%'.
    - Perform the assertion first to validate any preexisting '%' mapping.
    - Mutate table by setting table['%'] = '%' after the assertion check.
    - Build the output by iterating tokens and either appending the mapped replacement for percent tokens (table[c[1]]) or the token itself for non-percent tokens.

## `onlinejudge_command.format_utils.percentparse` · *function*

## Summary:
Construct a regular expression from a percent-style format and a mapping of specifiers to regex fragments, match the input string against that pattern, and return the dictionary of named captures on success or None if there is no match.

## Description:
- Known callers: No direct callers were found in the provided repository snapshot. Typical callers are parsing routines or filename/identifier extractors that represent small, structured templates using percent-escapes (e.g., "%y-%m-%d") and need to extract named fields from concrete strings.
- Purpose: Convert a lightweight percent-format (literals plus '%x' specifiers) into a single regular-expression match that:
    * wraps the first occurrence of each specifier in a named capturing group,
    * enforces later occurrences of the same specifier to match the exact same substring via a named-group backreference,
    * returns the captured substrings as a dict keyed by specifier.
- Why separated: This function centralizes the logic of turning percent-format templates + regex fragments into a single match operation and the semantics for repeated specifiers (same-text enforcement). Extracting this logic prevents duplication and keeps tokenization, group creation, and matching concerns in one place.

## Args:
    s (str):
        The input string to test against the compiled pattern.
        - Must be a string or an object acceptable to re.match; otherwise re.match may raise TypeError.
    format (str):
        Format template containing literal text and percent-escapes. Each specifier is exactly two characters: '%' followed by one character (e.g., "%a", "%1", "%_").
        - The format string is escaped so that regex metacharacters in the literal parts are treated literally; percent signs are restored so they serve as specifiers.
        - A trailing solitary '%' in the format (no following character) is silently dropped by the tokenization step (see Constraints / Edge cases).
    table (Dict[str, str]):
        Map from single-character specifier keys (the character after '%') to regex fragments (strings) that describe what that specifier should match.
        - Keys: must match the single characters used in format and must be valid Python identifiers used as named-group names (match [A-Za-z_][A-Za-z0-9_]*). Using keys that are not valid identifiers will cause a regex construction error.
        - Values: raw regex snippets (not automatically wrapped in non-capturing groups). The function wraps the first occurrence of each key with a named-capturing group: (?P<key>value).

## Returns:
    Optional[Dict[str, str]]:
        - On successful re.match of the assembled pattern against s, returns the mapping of specifier keys to the substring captured for their first occurrence.
        - If no match is found, returns None.
        - Notes:
            * Only the first occurrence of each specifier produces a capture stored in the returned dict. Later occurrences are enforced to be equal to the first occurrence by a backreference and do not produce additional dict entries.
            * The match uses re.match (anchored at the start). Trailing characters in s after the matched portion are allowed unless the pattern / table fragments explicitly prevent them.

## Raises:
    KeyError:
        - Raised when the code attempts to look up table[c] for a specifier c present in format but missing from table. This occurs when the first occurrence of a specifier is encountered in the token iteration.
    re.error:
        - Raised if the constructed regex is invalid. Common causes:
            * table values contain invalid regex syntax,
            * table keys are not valid group names (not valid Python identifiers),
            * any invalid combination of inserted fragments that violate regex grammar.
    TypeError:
        - May be raised by re.match if s is not an acceptable string-like object.

## Constraints:
Preconditions:
    - format must be a str where specifiers are written as '%' followed by a single character.
    - Every distinct specifier character used in format must exist as a key in table.
    - Each table key must be a valid Python identifier (matching [A-Za-z_][A-Za-z0-9_]*).
    - Each table value must be a valid regex fragment appropriate to be placed inside a capturing group.
Postconditions:
    - If a non-None dict is returned, each key in that dict corresponds to a distinct specifier present in format and maps to the substring captured for its first occurrence. Repeated specifier occurrences matched the same substring (enforced by backreferences).
    - If None is returned, the input did not match the assembled pattern starting at the beginning of s.

Edge cases and important details:
    - Prefix-only matching: The function uses re.match, which attempts a match at the start of s but does not require matching the entire string. Example: with format "%a" and table {'a': r'\d+'}, s "123abc" will match and return {'a': '123'} even though "abc" remains unmatched.
    - Silent drop of trailing '%' in format: Because tokenization yields only '%' followed by another character, a trailing '%' at the end of format is not yielded and thus ignored when building the pattern. This can lead to unexpected patterns (missing specifier) without raising an error. Avoid ending format strings with a solitary percent.
    - Repeated specifiers: The first occurrence produces a named capture; later occurrences use a backreference (?P=key), so they must match exactly the same substring as the first.
    - Regex anchors: Since literal parts of format are escaped, placing regex anchors (e.g., '^' or '$') in the format will be treated as literal characters. To enforce full-string match, include end-anchor constructs inside table values (for the final specifier) or post-validate (compare matched span to len(s)), or modify the code to use re.fullmatch externally.

## Side Effects:
    - None. No I/O or mutation of global state. Only interacts with the Python regex engine.

## Control Flow:
flowchart TD
    A[Start: receive s, format, table] --> B[Build table mapping: key -> '(?P<key>value)']
    B --> C[Escape format via re.escape(format) and restore '%' by replacing '\%' with '%']
    C --> D[Tokenize escaped format with percentsplit into tokens: literals or '%x']
    D --> E{For each token}
    E --> |token startswith '%'| F[let c = token[1]]
    F --> G{c not in used set?}
    G --> |Yes| H[append table[c] (named group) to pattern; add c to used]
    G --> |No| I[append backreference '(?P=c)' to pattern]
    E --> |token is literal| J[append literal token to pattern]
    H --> E
    I --> E
    J --> E
    E --> K[After loop: call re.match(pattern, s)]
    K --> L{match succeeded?}
    L --> |No| M[return None]
    L --> |Yes| N[return m.groupdict()]

## Examples:
- Successful capture with repeated specifier:
    format = "%a-%a"
    table = {'a': r'\d+'}
    s = "123-123"
    result -> {'a': '123'}

- Repeated specifier mismatch (no match):
    format = "%a-%a"
    table = {'a': r'\d+'}
    s = "123-456"
    result -> None

- Multiple different specifiers:
    format = "%y_%m-%d"
    table = {'y': r'\d{4}', 'm': r'\d{2}', 'd': r'\d{2}'}
    s = "2026_04-25"
    result -> {'y': '2026', 'm': '04', 'd': '25'}

- Prefix-only matching (important):
    format = "%a"
    table = {'a': r'\d+'}
    s = "123abc"
    result -> {'a': '123'}  # trailing "abc" is allowed because re.match only anchors at start

- Trailing solitary percent in format is dropped:
    format = "end%"
    table = {}  # there is no specifier after '%' so percentsplit drops the trailing '%'
    # The constructed pattern will be "end", so percentparse("end", "end%", {}) returns {}
    # The silent drop may mask miswritten formats; avoid trailing solitary '%'.

- Missing table key (raises KeyError):
    format = "%x-%y"
    table = {'x': r'\w+'}
    calling percentparse(s, format, table) will raise KeyError for 'y'

- Enforcing full-string match workaround:
    - Include an end anchor inside the final specifier's table value, for example:
        format = "%a"
        table = {'a': r'\d+\Z'}  # '\Z' asserts end-of-string; placed inside the capture
      Now percentparse("123", "%a", table) -> {'a': '123'}
      And percentparse("123abc", "%a", table) -> None

- Robust usage pattern:
    try:
        mapping = percentparse(some_string, "%a-%b", {'a': r'\d+', 'b': r'\w+'})
    except KeyError:
        # configuration error: format requires a specifier missing from table
    except re.error:
        # configuration error: invalid regex fragment or invalid group name
    else:
        if mapping is None:
            # input does not match the format
        else:
            # mapping contains captured substrings for each distinct specifier

## `onlinejudge_command.format_utils.glob_with_format` · *function*

## Summary:
Builds a glob pattern from a directory and a percent-style format string (with %s and %e tokens) and returns all matching filesystem paths as pathlib.Path objects.

## Description:
This function generates a filesystem glob pattern that is anchored to the given directory and that substitutes percent-escape tokens in the provided format into wildcard tokens before performing the filesystem glob.

Known callers:
- No direct callers were found in the provided repository snapshot. Treat this as a reusable helper used wherever test-case or resource file sets are discovered by directory + format strings.

Context / When to call:
- Use when you need to find files under a directory whose names follow a template containing the %s and %e escapes (or other single-character percent-escapes supported by the provided substitution table).
- Typical pipeline stage: building a list of test-case files or resource files from a directory and a user-provided filename format pattern.

Why this is a separate function:
- Encapsulates platform-specific normalization (converting forward slashes to backslashes on Windows), escaping of user-provided format strings for safe glob use, and the percent-token -> wildcard substitution (delegated to percentformat).
- Keeps pattern-construction and logging in one place so callers only need to pass directory and format strings and receive a ready-to-use list of Path objects.

Dependencies:
- percentformat(template: str, table: Dict[str,str]) -> str: used to replace percent-escapes in the (escaped) format string with table entries. The function will raise KeyError if percent tokens reference missing keys and will set table['%'] = '%'.
- module-level logger (logger.debug is invoked). The caller should ensure the module defines a logger (commonly via getLogger(__name__)).
- Uses glob.glob to perform the filesystem query and pathlib.Path to represent results.

## Args:
    directory (pathlib.Path):
        - The directory in which to anchor the glob search.
        - It is converted to string and appended with os.path.sep (ensuring the pattern searches inside the directory).
        - Must be path-like or a pathlib.Path instance; passing other types may yield incorrect behavior.
    format (str):
        - A percent-style format string describing filenames relative to the directory. Typical tokens:
            - "%s" and "%e" are used by this implementation and are mapped to '*' (glob wildcard).
            - Other percent-escapes are possible but will cause a KeyError unless supported by percentformat's table.
        - On Windows (os.name == 'nt'), forward slashes ('/') in this format are automatically converted to backslashes ('\\') before processing.
        - Note: the parameter name shadows the built-in name 'format' (callers may prefer to avoid relying on builtins).

Interdependencies between parameters:
    - directory is only used as an anchor (prefixed to the resulting glob pattern).
    - format is interpreted relative to that directory; both are required for correct pattern construction.

## Returns:
    List[pathlib.Path]:
        - A list of pathlib.Path objects for every filesystem entry that matches the generated glob pattern.
        - The list preserves the order returned by glob.glob (typically lexical order from the filesystem).
        - If no filesystem matches are found an empty list is returned.
        - The return contains only paths that matched the pattern — no information about whether each entry is a file or directory is guaranteed (use Path.is_file()/is_dir() if needed).

## Raises:
    KeyError:
        - If percentformat is invoked with a percent token (e.g., "%x") whose single-character key is not present in the substitution table used inside glob_with_format (the function uses a table mapping 's' and 'e' to '*').
    AssertionError:
        - If percentformat contains an assertion that table['%'] (if present) must equal '%' (this originates from percentformat and therefore may be raised before glob_with_format completes).
    TypeError:
        - If percentformat or other string operations encounter unexpected non-string types (e.g., if format is not a str), TypeError may propagate.
    Notes:
        - glob.glob itself does not raise on non-existent directories; it simply returns an empty list for no matches.
        - No exceptions are explicitly raised by glob_with_format beyond those that can propagate from percentformat and Python standard library calls.

## Constraints:
Preconditions:
    - directory should be convertible to string via str(directory) and represent a valid filesystem path prefix.
    - format must be a Python str (or at least accepted by glob.escape and percentformat); non-str inputs may raise.
    - The internal percent substitution table contains at least 's' and 'e' keys (this function sets them).

Postconditions:
    - The returned list contains pathlib.Path objects matching files/directories inside the provided directory according to the translated format.
    - No mutation of filesystem state occurs.
    - The module logger was invoked at debug level for each matched path (logger.debug called once per path). The logger is not created by this function; ensure a module-level logger exists.

## Side Effects:
    - Logging: calls logger.debug('testcase globbed: %s', path) for every matched path; this writes to the configured logging handlers but does not change filesystem state.
    - No filesystem writes or network I/O are performed by this function.
    - No global variables are modified by this function (it does not mutate external mappings). percentformat mutates its mapping argument, but glob_with_format constructs the table locally before calling percentformat, so no caller-supplied mapping is changed.

## Implementation details (to reimplement correctly)
1. If running on Windows (os.name == 'nt'), replace '/' with '\\' in the format string to conserve expected directory separators.
2. Build a substitution table:
    - Set table['s'] = '*'
    - Set table['e'] = '*'
   (these map the %s and %e percent-tokens in the format into glob wildcards).
3. Escape the directory prefix:
    - Convert directory to string and append os.path.sep, then escape it for safe inclusion in a glob pattern (use glob.escape).
    - This ensures the pattern is anchored to the directory and special glob characters in the directory path do not alter matching semantics.
4. Escape the format string for glob, but restore literal percent characters so percentformat can see percent-escapes:
    - Call glob.escape(format) then replace glob.escape('%') with '%' (i.e., undo escaping of '%' only). This prevents accidental escaping of percent characters while still escaping glob metacharacters in the format.
5. Call percentformat on the partially-escaped format string with the table from step 2 to obtain the right-hand side of the pattern (it will substitute %s and %e with '*').
6. Concatenate the escaped directory prefix and the percentformatted pattern to form the final glob pattern.
7. Use glob.glob(pattern) to find matching path strings and wrap each result in pathlib.Path before returning.
8. For each returned Path, call logger.debug with the message shown in the source.

## Control Flow:
flowchart TD
    Start([Start: glob_with_format(directory, format)]) --> IsWindows{os.name == 'nt'?}
    IsWindows -- Yes --> NormalizeSep[format = format.replace('/', '\\')]
    IsWindows -- No --> SkipNormalize[No change to format]
    NormalizeSep --> BuildTable
    SkipNormalize --> BuildTable
    BuildTable[Build table: {'s':'*','e':'*'}] --> EscapeDir[escaped_dir = glob.escape(str(directory)+os.path.sep)]
    EscapeDir --> EscapeFmt[escaped_fmt = glob.escape(format).replace(glob.escape('%'), '%')]
    EscapeFmt --> PercentFormat[formatted = percentformat(escaped_fmt, table)]
    PercentFormat --> PatternConcat[pattern = escaped_dir + formatted]
    PatternConcat --> GlobCall[paths_strs = glob.glob(pattern)]
    GlobCall --> ConvertPaths[paths = [pathlib.Path(p) for p in paths_strs]]
    ConvertPaths --> LogLoop[For each path in paths -> logger.debug(...)]
    LogLoop --> Return[Return paths]

Exceptional paths:
    - If percentformat raises KeyError/AssertionError/TypeError, the function propagates that exception and does not return a list.
    - If glob.glob returns an empty list the function returns [] (normal return).

## Examples:
- Typical usage:
    - directory: pathlib.Path('/project/tests')
    - format: 'case_%s_input.txt'
    - Behavior:
        - On non-Windows: pattern becomes escaped('/project/tests/') + 'case_*_input.txt'
        - The function returns Path objects for every file in /project/tests matching case_*_input.txt.

- Example (normal):
    - Input: directory = pathlib.Path('tests'), format = 'sample%se%d.txt'
    - Internal table maps %s -> '*' and %e -> '*'
    - Resulting pattern (conceptually): 'tests/' + 'sample**.txt' (two adjacent '*' are allowed and equivalent to a single wildcard in glob semantics)
    - Returns: [Path('tests/sample1e2.txt'), ...] matching filesystem entries.

- Edge-case: missing percent key
    - If format contains a percent-escape other than %s or %e (e.g., "%x"), percentformat will attempt to look up 'x' in the table and will raise KeyError; glob_with_format will propagate this exception.

- Edge-case: no matches
    - If the pattern finds no filesystem entries, an empty list is returned (no exception).

Notes:
- Because glob_with_format constructs its own substitution table, it only supports the escapes explicitly provided in the table (here 's' and 'e'). Extend the table if additional percent-escapes should be recognized.
- The function relies on percentformat's behavior (including its assertion about table['%']). If percentformat's contract changes, adjust this implementation accordingly.

## `onlinejudge_command.format_utils.match_with_format` · *function*

## Summary:
Return a regex match if a given filesystem path matches a user-specified percent-format template anchored under a base directory; otherwise return None.

## Description:
This function tests whether the absolute path (path.resolve()) matches a template (format) when interpreted as a path relative to a given base directory (directory.resolve()).

Known callers within the repository snapshot:
- No direct callers were found in the provided repository snapshot. Typical usage is in file-discovery or sample-file-matching code that needs to map concrete sample filenames (e.g., "foo.in", "foo.out") to a format template (e.g., "%s.%e") anchored to a problem/directory path.

Why this is a separate function:
- It isolates the concerns of converting a human-friendly percent-style format into a regular expression anchored to a specific directory, including platform-specific path-separator handling. This keeps template-to-regex conversion and path matching in one small, testable unit rather than repeating the same logic at each call site.

## Args:
    directory (pathlib.Path):
        - Base directory under which files described by `format` are expected to reside.
        - The code calls directory.resolve() and uses the resulting absolute path string followed by the OS path separator as the required prefix for matching.
    format (str):
        - A percent-escape template describing the expected filename portion(s) relative to the base directory.
        - Percent-escape keys used by this function:
            * %s — replaced with the regex (?P<name>.+) (captures the "name" group)
            * %e — replaced with the regex (?P<ext>in|out) (captures the "ext" group limited to 'in' or 'out')
        - Any other percent-escape (e.g. %x) will be forwarded to percentformat and, if not present in the internal mapping, will raise KeyError.
        - On Windows (os.name == 'nt') all forward slashes (/) in `format` are converted to backslashes (\\) before processing.
        - The function applies re.escape to the format string so that literal characters are matched literally; only recognized percent escapes are substituted into regex form.
    path (pathlib.Path):
        - Candidate file path to test. The function calls path.resolve() and matches the resulting absolute string against the compiled regex.

Notes on interdependencies:
- This function relies on percentformat to perform the percent-token substitution; percentformat will mutate the temporary mapping used inside this function by ensuring table['%'] == '%'.
- The mapping used inside this function is fixed (it provides only 's' and 'e' replacements). Any other % token in `format` will trigger percentformat to attempt a lookup and will raise KeyError.

## Returns:
    Optional[re.Match[str]]:
        - If the compiled pattern matches str(path.resolve()) at its beginning, returns the Match object produced by re.Pattern.match.
        - If there is no match, returns None.
        - When a match is returned, it will normally include the named groups:
            * 'name' (from %s): the filename portion matched by (?P<name>.+)
            * 'ext'  (from %e): either 'in' or 'out' (from (?P<ext>in|out))
        - The match is performed from the start of the string (pattern.match), so the match guarantees the path begins with directory.resolve() + os.path.sep followed by the formatted portion. The regex is not explicitly anchored to the end of the string, so trailing characters after the matched portion are allowed unless the `format` covers the path tail.

## Raises:
    KeyError:
        - If `format` contains a percent-escape token whose single-character key is not present in the internal mapping provided to percentformat (i.e., not 's' or 'e'), percentformat will raise KeyError during lookup. This KeyError propagates out of match_with_format.
    AssertionError:
        - If percentformat's precondition about an existing '%' mapping fails (this is unlikely here because the mapping is freshly created), percentformat may raise AssertionError. This propagates out.
    re.error:
        - If for some unexpected reason the combined regex is invalid, re.compile may raise re.error. Given the use of re.escape and the controlled replacements, this is unlikely but possible.
    TypeError / OSError / ValueError:
        - If directory or path are not valid Path-like objects, or if path.resolve()/directory.resolve() raises due to underlying OS issues, those exceptions may propagate from pathlib.Path methods.

## Constraints:
Preconditions:
    - `directory` and `path` must be pathlib.Path (or path-like) instances. They will be resolved to absolute paths via .resolve().
    - `format` must be a str. It may include literal characters and percent-escapes; only the escapes 's' and 'e' are supported by the internal mapping used here.
Postconditions:
    - No persistent external state is modified by this function (the mapping passed to percentformat is a local dict); percentformat will mutate that local mapping by setting table['%'] = '%', but callers see no mutation of their inputs.
    - The returned Match (if not None) will have named groups 'name' and 'ext' if the format contained %s and %e respectively.

## Side Effects:
    - No file or network I/O is performed by this function.
    - Internally, the temporary mapping passed to percentformat is mutated (table['%'] = '%'), but because the mapping is local to this function there is no observable mutation of caller-provided objects.
    - The function calls .resolve() on the provided Path objects which may cause filesystem metadata access (no writes).

## Control Flow:
flowchart TD
    Start([Start]) --> WindowsCheck{os.name == 'nt'?}
    WindowsCheck -- Yes --> ReplaceSlashes[Replace '/' with '\\' in format]
    WindowsCheck -- No --> KeepFormat[Keep format unchanged]
    ReplaceSlashes --> BuildTable
    KeepFormat --> BuildTable
    BuildTable[Build table = {'s':'(?P<name>.+)', 'e':'(?P<ext>in|out)'}] --> EscapeFormat[Escape literal chars in format with re.escape and restore percent signs]
    EscapeFormat --> percentformatCall[Call percentformat(escaped_format, table)]
    percentformatCall --> CompileRegex[Compile regex: re.escape(directory.resolve() + os.path.sep) + substituted_pattern]
    CompileRegex --> TryMatch[pattern.match(str(path.resolve()))]
    TryMatch --> MatchFound{match?}
    MatchFound -- Yes --> ReturnMatch[Return Match object]
    MatchFound -- No --> ReturnNone[Return None]

Notes on exceptional paths:
    - percentformat may raise KeyError or AssertionError; these exit the function abruptly.
    - re.compile may raise re.error on invalid regex.
    - path.resolve()/directory.resolve() may raise OSError/ValueError in unusual circumstances.

## Examples:
- Successful match example:
    >>> from pathlib import Path
    >>> directory = Path("/home/user/problem")
    >>> fmt = "%s.%e"            # expected files like "foo.in" or "foo.out"
    >>> path = directory / "sample1.in"
    >>> m = match_with_format(directory, fmt, path)
    >>> bool(m)
    True
    >>> m.group("name")
    "sample1"
    >>> m.group("ext")
    "in"

- No match (different filename):
    >>> path = directory / "README.md"
    >>> match_with_format(directory, "%s.%e", path) is None
    True

- Format with unsupported percent token -> KeyError:
    >>> match_with_format(directory, "%x.%e", directory / "a.in")
    KeyError: 'x'  # percentformat attempts table['x'] and fails

- Windows path handling:
    - If calling on Windows (os.name == 'nt') and format uses forward slashes ("/"), they will be converted to backslashes before building the regex so templates like "%s/%s.%e" will use backslash separators on Windows.

## `onlinejudge_command.format_utils.path_from_format` · *function*

## Summary:
Builds a pathlib.Path by substituting the "%s" and "%e" tokens in a filename template with the provided name and extension, then joining the substituted string to the given directory.

## Description:
This function creates a minimal substitution dictionary with two keys — 's' mapped to the provided name and 'e' mapped to the provided ext — then calls percentformat(format, table) to perform percent-style single-character substitutions. The string returned by percentformat is joined to directory using pathlib.Path's division operator (directory / substituted_string) and the resulting pathlib.Path is returned.

Known callers within the repository snapshot:
- No direct callers were found in the provided snapshot.
Typical use:
- Generate a filename or nested path from a template such as "%s.%e" and place it under a target directory (e.g., producing "out/solution.py" from "%s.%e", "solution", "py").

Why this is factored out:
- Keeps the mapping for canonical filename tokens ('s' and 'e') in a single place and delegates token parsing and validation to percentformat. This simplifies callers and centralizes filename-template logic.

## Args:
    directory (pathlib.Path):
        - Directory under which the substituted template will be resolved.
        - Must be a pathlib.Path (or compatible object). The function signature expects pathlib.Path; passing another type may change / behavior or raise an error.
    format (str):
        - Percent-style template string. Tokens are percent-escapes of the form "%x" where x is a single character.
        - Common templates: "%s.%e", "%s", "sub/%s.%e".
        - Any token other than "%s" or "%e" will cause percentformat to attempt a lookup and raise KeyError because this function only supplies 's' and 'e'.
    name (str):
        - Replacement value for "%s". Must be a str; percentformat concatenates these values into a result string, so non-str values will raise TypeError during substitution.
    ext (str):
        - Replacement value for "%e". Must be a str. The function does not add or enforce a leading dot; include it in ext or in the format if desired.

Interdependencies:
    - Relies on percentformat(format, table) for token parsing, validation, substitution, and the side-effect of ensuring table['%'] == '%'. The local table passed here contains only 's' and 'e'.

## Returns:
    pathlib.Path
        - The path produced by directory / substituted_string where substituted_string is the string returned by percentformat(format, table).
        - Behavior notes:
            * If substituted_string is empty (e.g., format is ""), directory / "" yields directory (no new name appended).
            * If substituted_string contains path separators (e.g., "sub/one.txt"), those become child segments under directory: directory / "sub/one.txt" -> directory/sub/one.txt
            * If substituted_string is an absolute path (starts with the platform root), pathlib.Path's division semantics return the absolute path (the right-hand operand overrides directory).
        - Examples:
            * directory=Path("out"), format="%s.%e", name="main", ext="cpp" -> Path("out/main.cpp")
            * directory=Path("out"), format="tests/%s.%e", ... -> Path("out/tests/main.cpp")
            * directory=Path("out"), format="/abs/%s.%e", ... -> Path("/abs/main.cpp") (absolute replaces)

## Raises:
    KeyError:
        - Raised when the format template contains a percent-escape "%x" and x is not present in the substitution table. Since this function only provides 's' and 'e', any other token will cause KeyError from percentformat.
    TypeError:
        - If name or ext are not strings, percentformat's concatenation may raise TypeError during substitution.
        - If directory is not a pathlib.Path (or an object that supports path division with a str/Path), the division operator may raise TypeError. The annotated signature requires pathlib.Path for correctness.
    AssertionError:
        - Will NOT be raised by percentformat in this call because the table passed is newly created and does not contain '%' prior to the call. percentformat's AssertionError only occurs when a preexisting table['%'] is present and not equal to '%'.
    Other exceptions:
        - Any exception raised by percentformat (e.g., regex or tokenizer errors) will propagate unchanged.

## Constraints:
Preconditions:
    - directory should be a pathlib.Path.
    - format must be a str valid for percentformat's tokenizer.
    - name and ext must be str.
Postconditions:
    - Returns a pathlib.Path constructed from the provided directory and the substituted template.
    - No external/global state is mutated by this function. percentformat will set table['%'] = '%' on the local table, but that table is not exposed to callers.

## Side Effects:
    - No I/O, no logging, no global state mutation.
    - Local mutation: percentformat will set table['%'] = '%' on the local substitution table; this mutation is internal and not observable by callers.

## Control Flow:
flowchart TD
    Start([Start: path_from_format(directory, format, name, ext)]) --> CreateTable[Create table = {'s': name, 'e': ext}]
    CreateTable --> CallPercent[Call percentformat(format, table)]
    CallPercent --> PercentErr{percentformat raises?}
    PercentErr -- Yes --> Propagate[Propagate the exception to caller]
    PercentErr -- No --> GotString[percentformat returns substituted_string]
    GotString --> MakePath[Compute result = directory / substituted_string]
    MakePath --> Return([Return pathlib.Path result])

## Examples:
- Successful construction:
    >>> directory = Path("build")
    >>> path_from_format(directory, "%s.%e", "solution", "py")
    Path("build/solution.py")

- Template with nested directory:
    >>> path_from_format(Path("out"), "tests/%s.%e", "case1", "txt")
    Path("out/tests/case1.txt")

- Empty template:
    >>> path_from_format(Path("out"), "", "name", "ext")
    Path("out")  # percentformat returns "" so directory / "" == directory

- Missing token -> handle KeyError:
    >>> try:
    ...     path_from_format(Path("out"), "%x", "a", "b")
    ... except KeyError as e:
    ...     # format referenced an unsupported token 'x'
    ...     handle_missing_token(e)

- Non-string name/ext -> handle TypeError:
    >>> try:
    ...     path_from_format(Path("out"), "%s.%e", 123, None)
    ... except TypeError:
    ...     # name/ext must be str for substitution
    ...     handle_bad_types()

## `onlinejudge_command.format_utils.is_backup_or_hidden_file` · *function*

## Summary:
Returns True when a filesystem path refers to a typical backup or hidden file name (tilde-suffixed, Emacs/Vim-style pound-delimited, or dot-prefixed).

## Description:
This predicate inspects only the final path component (basename) and classifies names commonly used for editor backups and hidden files:
- basename ending with '~' (e.g., "file.txt~")
- basename starting and ending with '#' (e.g., "#file.txt#")
- basename starting with '.' (e.g., ".gitignore", ".", "..")

Known callers within the provided file-level context:
- No direct callers were identified in the supplied source snippet. In practice, this function is typically invoked by file-discovery or filtering routines that need to ignore editor backup files and dotfiles when processing directories.

Why this is a separate function:
- Encapsulates a small but frequently reused classification rule so callers can read a descriptive name instead of duplicating literal string tests.
- Centralizes the definition of what the project considers a "backup or hidden" filename, making it easier to update the policy in one place.

## Args:
    path (pathlib.Path): The path to classify. Only the final path component (path.name) is examined. The function expects a Path-like object; passing other types will likely raise an AttributeError before reaching the tests.

## Returns:
    bool: True if the path's basename matches any of the backup/hidden naming patterns; False otherwise.

    Possible return cases:
    - True:
        * basename.endswith('~')
        * basename.startswith('#') and basename.endswith('#')
        * basename.startswith('.')
    - False:
        * basename that does not meet any of the above tests (including the empty string basename).

## Raises:
    No exceptions are explicitly raised by the function itself.
    However, if the argument does not provide a .name attribute (for example, passing an incompatible type), attribute-access errors (AttributeError) may be raised by the caller's misuse.

## Constraints:
    Preconditions:
    - The caller must provide an object with a .name attribute (pathlib.Path or compatible).
    - This function does not resolve symlinks, check file existence, or inspect directories — it operates purely on the textual basename.

    Postconditions:
    - The function deterministically returns a boolean based solely on the basename string.
    - Calling the function has no observable external effects.

## Side Effects:
    None. The function performs no I/O, no filesystem access, and mutates no external state.

## Control Flow:
flowchart TD
    Start([start])
    A[basename = path.name]
    C1{endswith '~'?}
    C2{starts with '#' and ends with '#'?}
    C3{starts with '.'?}
    TrueNode([return True])
    FalseNode([return False])
    Start --> A --> C1
    C1 -- yes --> TrueNode
    C1 -- no --> C2
    C2 -- yes --> TrueNode
    C2 -- no --> C3
    C3 -- yes --> TrueNode
    C3 -- no --> FalseNode

## Examples:
- Typical positive cases:
    is_backup_or_hidden_file(Path('notes.txt~'))    -> True
    is_backup_or_hidden_file(Path('#temp#'))        -> True
    is_backup_or_hidden_file(Path('.env'))          -> True
    is_backup_or_hidden_file(Path('.'))             -> True
    is_backup_or_hidden_file(Path('..'))            -> True

- Typical negative cases:
    is_backup_or_hidden_file(Path('README.md'))     -> False
    is_backup_or_hidden_file(Path('archive.tar.gz'))-> False

- Edge usage note:
    If the caller passes an object without a .name attribute, an AttributeError will occur before the classification logic runs; callers should ensure they pass pathlib.Path (or an object with a compatible .name string).

## `onlinejudge_command.format_utils.drop_backup_or_hidden_files` · *function*

## Summary:
Filters a list of filesystem paths by removing any entries whose basenames identify them as editor backup files or hidden files; returns a new list with the original order preserved.

## Description:
This function scans the provided sequence of pathlib.Path objects and removes any path whose final path component (basename) is classified as a backup or hidden filename. For each removed path it emits a warning via the module-level logger.

Known callers within the supplied source context:
- No direct callers were identified in the supplied snippets. Typically this function is invoked immediately after discovering files (e.g., directory listing) to exclude editor backup files and dotfiles before further processing (such as formatting or uploading).

Why this logic is extracted:
- Encapsulates filtering-plus-logging behavior so callers need not duplicate both the classification rule (is_backup_or_hidden_file) and the logging side effect.
- Keeps file-discovery and processing code focused on their primary tasks by centralizing the policy for which filenames to ignore and how to notify about them.

## Args:
    paths (List[pathlib.Path]): A list of pathlib.Path (or Path-like) objects to filter.
        - Each element is expected to have a .name attribute (the function delegates basename checks to is_backup_or_hidden_file, which inspects path.name).
        - Passing elements that lack .name (e.g., plain strings) is misuse and may raise AttributeError from the called predicate.

## Returns:
    List[pathlib.Path]: A newly-allocated list containing only those input paths that are NOT classified as backup or hidden files.
        - Order is preserved: the returned list enumerates surviving paths in the same order they appeared in the input.
        - If all inputs are dropped, an empty list is returned.
        - The original input list is not modified.

## Raises:
    No exceptions are explicitly raised by this function itself.
    However, exceptions raised by is_backup_or_hidden_file (for example AttributeError if an element lacks a .name attribute) will propagate to the caller.

## Constraints:
    Preconditions:
    - Caller should pass a list of pathlib.Path or compatible objects exposing a .name attribute.
    - is_backup_or_hidden_file governs the exact classification rules (tilde-suffixed, pound-delimited, or dot-prefixed basenames). This function does not re-implement those checks.

    Postconditions:
    - The returned list contains only paths for which is_backup_or_hidden_file(path) returned False.
    - Every ignored path produced a logger.warning side-effect before being excluded.

## Side Effects:
    - Emits a logging WARNING for each path that is ignored. The code uses the module-level logger via logger.warning (the message in the implementation is logged with the ignored path).
    - No filesystem I/O, no file deletion, and no mutation of the input list occur.

## Control Flow:
flowchart TD
    Start([Start])
    I[Initialize result = []]
    ForEach[/For each path in paths/]
    Check{is_backup_or_hidden_file(path)?}
    Warn[/logger.warning("ignore a backup file: %s", path)/]
    Append[/result += [path] (preserve order)/]
    EndLoop([After loop])
    Return[/return result/]
    Start --> I --> ForEach --> Check
    Check -- yes --> Warn --> ForEach
    Check -- no --> Append --> ForEach
    ForEach --> EndLoop --> Return

## Examples:
- Typical usage:
    Given paths: [Path('.env'), Path('main.cpp'), Path('notes.txt~')]
    After call: drop_backup_or_hidden_files(paths) -> [Path('main.cpp')]
    Side effect: a WARNING log entry is emitted for Path('.env') and Path('notes.txt~').

- Empty input:
    drop_backup_or_hidden_files([]) -> []

- Misuse and error handling:
    If callers pass wrong element types (e.g., strings) that do not have a .name attribute, the underlying predicate may raise AttributeError. Callers should validate or convert inputs (e.g., wrap in pathlib.Path) before invoking this function.

- Example pattern where this function fits in a pipeline:
    1) discover files with pathlib.Path.rglob or glob
    2) normalize paths to pathlib.Path objects
    3) call drop_backup_or_hidden_files(...) to remove backups/dotfiles (and log ignored items)
    4) proceed to content processing on the filtered list

## `onlinejudge_command.format_utils.construct_relationship_of_files` · *function*

## Summary:
Group discovered filesystem paths into test cases by parsing each path according to a percent-style format anchored under a base directory, returning a mapping from test-case name -> {'in'|'out': path}.

## Description:
This function takes a list of filesystem paths and a format template (the same kind interpreted by match_with_format) and builds a dictionary that associates each test case name with its available input/output sample files. It validates each path using match_with_format and enforces simple consistency rules: each case name may have at most one file for each extension (ext) and input files ('in') are required for every case.

Known callers within the provided repository snapshot:
- No direct callers were found in the provided snapshot. Typical usage is in the file-discovery / sample-file-collection stage of a CLI that prepares input/output sample pairs for test execution or packaging.

Why this logic is extracted into its own function:
- It centralizes the non-trivial logic of grouping flat filesystem paths into named test cases and handling validation and error reporting in one place. This keeps higher-level code free of parsing, duplicate-detection, and exit-on-error responsibilities.

## Args:
    paths (List[pathlib.Path]):
        - A list of Path objects (or Path-like items coerced earlier) representing candidate files discovered in a directory tree.
        - Each path will be resolved (path.resolve()) before being matched; callers should expect filesystem resolution to occur.
    directory (pathlib.Path):
        - The base directory under which the format template is anchored. Passed unchanged to match_with_format which resolves it internally.
        - Must be the same directory used when the format template was intended (i.e., match_with_format will expect resolved paths to start with directory.resolve() + os.path.sep).
    format (str):
        - A percent-style template describing how names and extensions appear relative to `directory`. It must be acceptable to match_with_format (typically uses %s for the test name and %e for the extension, where %e is limited to 'in'|'out').

Notes on parameter interdependencies:
- The `format` must contain tokens that produce named groups 'name' and 'ext' (e.g., %s and %e) because the function reads m.groupdict()['name'] and ['ext'] from the match. If match_with_format returns a Match lacking those groups, a KeyError or IndexError will propagate.
- The semantics of valid ext values (typically 'in' and 'out') are determined by the regex substitution performed by match_with_format; construct_relationship_of_files assumes 'in' and 'out' semantics when validating completeness.

## Returns:
    Dict[str, Dict[str, pathlib.Path]]:
        - A mapping where each key is a test-case name (string captured from the matched path via group 'name'), and the value is a dict mapping extension names to the corresponding pathlib.Path.
        - Typical structure: { "sample1": {"in": Path(...), "out": Path(...)}, "sample2": {"in": Path(...)} }
        - Each inner dict uses the literal ext strings produced by match_with_format (commonly 'in' and 'out').
        - Possible edge-case returns:
            * If execution reaches a normal return, the returned dict contains at least one test-case entry (the function enforces this and will exit on empty results).

## Raises:
    SystemExit (via sys.exit(1)):
        - If any file in `paths` does not match the supplied `format` when anchored under `directory`, the function logs an error and calls sys.exit(1), which raises SystemExit.
        - If any test case lacks an 'in' file (the code treats any case missing 'in' as an error), the function logs an error and calls sys.exit(1). Note: an assertion before the log ensures an 'out' exists in such a case; if that assertion fails, AssertionError is raised instead of the logged exit path.
        - If no test cases are found after processing all paths, the function logs an error and calls sys.exit(1).

    AssertionError:
        - If two files for the same test-case name yield the same ext (duplicate ext within one case) the assertion assert ext not in tests[name] will raise AssertionError.
        - If a case is missing 'in' and also missing 'out', the code contains assert 'out' in tests[name] which would raise AssertionError; in normal structure this is a guard to ensure tests[name]['out'] is present before attempting to report it.

    Any exceptions propagated from:
        - match_with_format (e.g., KeyError if the format contains unsupported percent-escapes),
        - pathlib.Path.resolve() or other filesystem-related calls (OSError, ValueError),
        - Unexpected runtime errors (TypeError, AttributeError) if inputs are not the expected types.

## Constraints:
Preconditions:
    - `paths` is an iterable of Path-like objects; each element should be resolvable via pathlib.Path.resolve().
    - `directory` must be a Path-like object that can be resolved.
    - `format` must be a string compatible with match_with_format and must produce named capture groups 'name' and 'ext'.

Postconditions:
    - On a successful return (no SystemExit), the returned dict:
        * contains one or more test-case entries,
        * has no duplicate extension entries per test case,
        * for every case key, there exists at least the 'in' entry (the function enforces presence of 'in' for every returned case).
    - The function does not mutate the provided Path objects; it only reads/resolves them and stores references in the returned dict.

## Side Effects:
    - Calls logger.error and logger.info to record problems and summary information (logger is used at module scope).
    - Calls sys.exit(1) on several validation failures; this terminates the process by raising SystemExit if not caught.
    - Invokes path.resolve() (on each path passed to match_with_format) and directory.resolve() indirectly via match_with_format; these calls access filesystem metadata (no writes).
    - No network access, file writing, or global state mutation is performed by this function itself.

## Control Flow:
flowchart TD
    Start([Start]) --> InitTests[Create empty defaultdict(dict) tests]
    InitTests --> ForEachPath{For each path in paths}
    ForEachPath --> ResolvePath[Call path.resolve() and match_with_format(directory, format, resolved_path)]
    ResolvePath --> MatchFound{match returned?}
    MatchFound -- No --> LogUnrecognizable[logger.error('unrecognizable file found', path)] --> ExitUnrecognizable[sys.exit(1) -> SystemExit]
    MatchFound -- Yes --> ExtractGroups[Extract name = match.groupdict()['name']; ext = match.groupdict()['ext']]
    ExtractGroups --> DupCheck{ext already in tests[name]?}
    DupCheck -- Yes --> AssertionError[assert ext not in tests[name] -> AssertionError]
    DupCheck -- No --> SavePath[tests[name][ext] = path] --> ForEachPath
    ForEachPath --> FinishedLoop[after all paths processed]
    FinishedLoop --> CheckCases{for each name in tests: is 'in' in tests[name]?}
    CheckCases -- No --> EnsureOut[assert 'out' in tests[name]] --> LogDangling[logger.error('dangling output case', tests[name]['out'])] --> ExitDangling[sys.exit(1) -> SystemExit]
    CheckCases -- Yes --> ContinueCheck
    ContinueCheck --> EmptyCheck{if not tests}
    EmptyCheck -- True --> LogNoCases[logger.error('no cases found')] --> ExitNoCases[sys.exit(1) -> SystemExit]
    EmptyCheck -- False --> LogInfo[logger.info('%d cases found', len(tests))] --> ReturnTests[return tests]
    ReturnTests --> End([End])

## Examples:
- Basic happy-path usage (illustrative):
    >>> from pathlib import Path
    >>> paths = [Path("/home/user/problem/sample1.in"), Path("/home/user/problem/sample1.out")]
    >>> directory = Path("/home/user/problem")
    >>> fmt = "%s.%e"  # expect %s -> name, %e -> 'in' or 'out'
    >>> result = construct_relationship_of_files(paths, directory, fmt)
    >>> # result -> {"sample1": {"in": Path("/home/user/problem/sample1.in"), "out": Path("/home/user/problem/sample1.out")}}

- Handling a non-matching file:
    * If paths includes a file that does not match `format` under `directory`, the function logs an error and exits the program by calling sys.exit(1). In test code you can catch SystemExit to assert that this behavior happened.

    Example:
    >>> import sys
    >>> try:
    ...     construct_relationship_of_files([Path("/tmp/unexpected.txt")], Path("/tmp"), "%s.%e")
    ... except SystemExit as e:
    ...     assert e.code == 1

- Duplicate extension within one case:
    * If two files map to the same case name and identical ext (e.g., two different "sample1.in" candidates), an AssertionError is raised because of assert ext not in tests[name].

Notes:
- This function relies on match_with_format to interpret `format`. That helper enforces how %s and %e are converted to regex groups and will raise KeyError if the `format` contains unsupported percent tokens. Ensure `format` produces named groups 'name' and 'ext' as used here.
- Because the function calls sys.exit(1) on validation failures, caller code that wants to handle these failures programmatically should catch SystemExit.

