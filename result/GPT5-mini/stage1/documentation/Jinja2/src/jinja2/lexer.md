# `lexer.py`

## `src.jinja2.lexer._describe_token_type` · *function*

## Summary:
Return a short, human-readable description for a lexer token type identifier.

## Description:
This function converts an internal token-type identifier into a concise human-readable label (for example, to display in error messages or debug output). It first checks a module-level mapping named reverse_operators and returns an entry from that mapping when present; otherwise it looks up the token type in an internal mapping of common lexer token constants and returns the corresponding short description. If no description is found, the function returns the token_type value unchanged.

Known callers:
- Not found in the provided source snippet. Typical call sites (not enumerated here) are components that need readable token labels such as lexer error reporting, exception messages, or debugging/diagnostics code.

Why this logic is extracted:
- Converting internal token identifiers into uniform short descriptions is a single responsibility that's used across multiple places (errors, logging, diagnostics). Extracting it centralizes the mapping logic, ensures consistent wording, and keeps lexer and error-reporting code readable and small.

## Args:
    token_type (str): The token type identifier to describe.
        - Expected to be a hashable string-like identifier used by the lexer (the function is annotated to accept str).
        - The function tests membership in a module-level mapping (reverse_operators) and in an internal dictionary of known token constants, so token_type must be suitable for dictionary key lookups.

## Returns:
    str: A short human-readable description for token_type. Possible outcomes:
        - If token_type is present as a key in reverse_operators, returns reverse_operators[token_type].
        - Else if token_type matches one of the known lexer token constants, returns one of the following literal description strings:
            - "begin of comment"
            - "end of comment"
            - "comment"
            - "begin of statement block"
            - "end of statement block"
            - "begin of print statement"
            - "end of print statement"
            - "begin of line statement"
            - "end of line statement"
            - "template data / text"
            - "end of template"
        - Otherwise, returns token_type unchanged (identity fallback).

## Raises:
    - The function does not explicitly raise exceptions for missing descriptions.
    - Runtime exceptions that can occur due to the surrounding environment:
        - NameError: If the module-level name reverse_operators or the TOKEN_* constants are not defined at import/lookup time, accessing them will raise NameError.
        - TypeError: If token_type is not hashable (membership test or dictionary lookup may raise TypeError).
    - Note: the function itself contains no try/except and does not intentionally raise TemplateSyntaxError or other custom exceptions.

## Constraints:
    Preconditions:
        - The module must define the mapping reverse_operators (a mapping supporting membership test and indexing) and any TOKEN_* constants referenced in the internal dictionary. If those are missing, a NameError will occur before or within this function.
        - token_type should be a hashable value (annotated as str).
    Postconditions:
        - The function returns a string (either a description from one of the two mappings or the original token_type value).
        - No global state is modified by this function.

## Side Effects:
    - None. The function performs pure lookup operations and returns a string.
    - No I/O, no modification of global variables, no network calls, and no persisted state changes.

## Control Flow:
flowchart TD
    A[Start: call with token_type] --> B{token_type in reverse_operators?}
    B -- Yes --> C[Return reverse_operators[token_type]]
    B -- No --> D{token_type in known-token-descriptions dict?}
    D -- Yes --> E[Return mapped human-readable description]
    D -- No --> F[Return token_type unchanged]
    E --> G[End]
    C --> G
    F --> G

## Examples:
1) When module-level reverse_operators provides a description:
    (Assume elsewhere in the module: reverse_operators = {'+': 'plus operator'})
    - _describe_token_type('+')  -> 'plus operator'

2) When token_type matches one of the known lexer token constants:
    (Assume TOKEN_DATA is defined to some value used by the lexer)
    - If token_type equals the TOKEN_DATA value, the function returns "template data / text".

3) Unknown token type falls back to identity:
    - _describe_token_type('UNKNOWN_TOKEN')  -> 'UNKNOWN_TOKEN'

Usage notes:
- Callers that depend on stable, localized wording for descriptions should centralize any wording changes here to keep messages consistent across the codebase.
- When using the function in exception messages, pass a token_type that is meaningful at the point of error (the function will not augment or normalize unknown identifiers).

## `src.jinja2.lexer.describe_token` · *function*

## Summary:
Return a short, human-readable label for a lexer Token: if the token represents an identifier/name return its literal value, otherwise return a description for the token's type.

## Description:
This helper centralizes how a Token is turned into a concise string used in error messages, debug output, and stringification. It is intentionally minimal: it handles the common special-case for name tokens (so the actual identifier text is shown), and delegates all other token-type-to-label work to the module function that maps token type identifiers to readable strings.

Known callers within the codebase:
- Token.__str__: used when a Token is converted to string (for example when formatting tokens in error messages or during debugging). Token.__str__ directly returns describe_token(self).
Typical call contexts:
- When constructing human-readable lexer diagnostics or template syntax error messages.
- When logging or printing tokens during development or verbose debugging.
Why this is extracted:
- This logic enforces a single responsibility: "choose the best human-facing label for a token." Separating it keeps Token.__str__ concise and ensures consistent labeling across all places that need readable token text (error formatting, logs, etc.).

## Args:
    token (Token): A Token namedtuple-like object with at least these attributes:
        - lineno (int): source line number where the token was produced (not used by this function)
        - type (str): the token type identifier (expected to be a string constant such as TOKEN_NAME, TOKEN_DATA, etc.)
        - value (str): the token literal value (used when the type is TOKEN_NAME)
    Notes:
        - The function expects token to have .type and .value attributes. Passing an object that lacks these attributes will raise an AttributeError.
        - The function is annotated with the forward reference "Token" (the Token class in the same module). token.type should be a string-like value that _describe_token_type can accept.

## Returns:
    str: A short human-facing label for the token. Possible outcomes:
        - If token.type equals the module constant TOKEN_NAME, returns token.value (the identifier text).
        - Otherwise returns _describe_token_type(token.type), which:
            - may map known token type identifiers to phrases like "template data / text", "begin of statement block", etc.; or
            - fall back to returning token.type unchanged when no mapping exists.
    The returned value is always a str (either the token.value or the result from _describe_token_type).

## Raises:
    - AttributeError: If the passed token does not expose .type or .value (attribute access fails).
    - NameError: If the module-level constant TOKEN_NAME is not defined when the function is executed (name lookup for TOKEN_NAME).
    - Any exception raised by _describe_token_type (for example, NameError if its required module-level mappings/constants are missing, or TypeError if token.type is not hashable). This function does not catch or convert exceptions from its delegate.
    Notes:
        - The function itself contains no explicit raise statements; these are runtime errors that arise from invalid inputs or missing module-level definitions.

## Constraints:
    Preconditions:
        - token must be an object with attributes .type and .value (the Token namedtuple satisfies this).
        - token.type should be a string-like, hashable token identifier compatible with _describe_token_type.
        - The module constant TOKEN_NAME must be defined in the lexer module.
    Postconditions:
        - The function returns a string describing the token. No global state or token object is modified.

## Side Effects:
    - None. The function performs pure attribute access and a pure lookup/delegation; it does not perform I/O, logging, network calls, or mutate global state.

## Control Flow:
flowchart TD
    Start[Start: call describe_token(token)] --> CheckName{token.type == TOKEN_NAME?}
    CheckName -- Yes --> ReturnValue[Return token.value]
    CheckName -- No --> Delegate[Call _describe_token_type(token.type)]
    Delegate --> ReturnDesc[Return description from _describe_token_type]
    ReturnValue --> End[End]
    ReturnDesc --> End

## Examples:
1) Name token shows the identifier text
    - Given: token has type TOKEN_NAME and value 'user'
    - Result: describe_token(token)  -> 'user'

2) Non-name token described via mapping
    - Given: token.type corresponds to a known token type (e.g. TOKEN_DATA)
      and _describe_token_type maps that type to 'template data / text'
    - Result: describe_token(token)  -> 'template data / text'

3) Unknown token type falls back to identity
    - Given: token.type is 'SOME_UNKNOWN_TYPE' and no mapping exists
    - Result: describe_token(token)  -> 'SOME_UNKNOWN_TYPE'

Usage notes:
- Because this function defers non-name description work to _describe_token_type, any changes to wording or mappings should be made in that helper so all callers remain consistent.
- When constructing user-facing error messages, prefer passing the Token object directly (so Token.__str__ uses this function) rather than assembling the label inline.

## `src.jinja2.lexer.describe_token_expr` · *function*

## Summary:
Convert a lexer token expression (either "TYPE:VALUE" or "TYPE") into a readable string: if the expression encodes a NAME token it returns the name VALUE, otherwise it returns a short description for the token type.

## Description:
This small helper parses token expressions produced by the lexer or token-serialization logic and returns a human-oriented label:
- When given an expression of the form "TYPE:VALUE" and TYPE equals the module-level TOKEN_NAME constant, the function returns VALUE (the token's identifier/name).
- For all other inputs it resolves the TYPE portion to a short description by delegating to _describe_token_type(type).

Known callers within the codebase:
- No direct callers were found in the provided source snippet. Typical callers include lexer error formatting, token-diagnostic messages, and other places that need readable token labels for exception text or logging.

Why this is a separate function:
- The logic encapsulates a single responsibility: normalizing a compact token-expression string into a display label. Extracting it keeps lexing/formatting code small, centralizes how "NAME" tokens are exposed (returning the raw name rather than a generic label), and ensures consistent delegation to the shared token-description function (_describe_token_type) for other token types.

## Args:
    expr (str): A token expression string produced by the lexer or token serialization.
        - Allowed forms:
            * "TYPE:VALUE" — a colon-separated type and associated value (only the first colon is significant).
            * "TYPE" — a bare token type identifier.
        - Interdependency: If expr contains a colon, the substring before the first colon is compared to the module-level TOKEN_NAME constant. If they compare equal, the substring after the first colon is returned directly.

## Returns:
    str: A human-readable label for the token expression.
        - If expr contains ":" and the left-hand TYPE equals TOKEN_NAME, returns the right-hand VALUE (may be the empty string if expr ends with a colon).
        - Otherwise returns the result of _describe_token_type(TYPE) where TYPE is:
            * the left-hand substring before the first colon if expr contains ":"; or
            * the entire expr string if it does not contain ":".
        - The return value is always a str when the function completes normally.

## Raises:
    - NameError:
        * If the module-level name TOKEN_NAME is not defined at runtime, the comparison will raise NameError when the function references it.
        * _describe_token_type may raise a NameError (for example if it expects module-level mappings that are missing); such exceptions propagate through describe_token_expr.
    - TypeError:
        * If expr is not a type that supports the containment test ("in") and str operations used here (for example, None or an unsupported type), Python may raise TypeError when evaluating ":" in expr or when calling expr.split.
    - Any runtime exception raised by _describe_token_type (TypeError, KeyError, etc.) is propagated unchanged.

## Constraints:
Preconditions:
    - expr should be a text string (str) representing a lexer token expression.
    - The module must define TOKEN_NAME and expose _describe_token_type; otherwise NameError will be raised when they are accessed.

Postconditions:
    - The function returns a string representing either the raw token name (for NAME tokens) or a short description for the token type (as produced by _describe_token_type).
    - No global state is modified and there are no side effects.

## Side Effects:
    - None. The function performs pure string parsing and a delegation call; it does not perform I/O or mutate external/global state.

## Control Flow:
flowchart TD
    Start[Start: call describe_token_expr(expr)] --> HasColon{Does expr contain ":"?}
    HasColon -- Yes --> Split[Split expr into type and value by first ":"]
    Split --> IsName{Is type == TOKEN_NAME?}
    IsName -- Yes --> ReturnValue[Return value (right-hand side)]
    IsName -- No --> DescribeType[Call _describe_token_type(type)]
    DescribeType --> ReturnDesc[Return description]
    HasColon -- No --> TypeIsExpr[Set type = expr]
    TypeIsExpr --> DescribeType2[Call _describe_token_type(type)]
    DescribeType2 --> ReturnDesc2[Return description]
    ReturnValue --> End[End]
    ReturnDesc --> End
    ReturnDesc2 --> End

## Examples:
Note: actual returned descriptions from _describe_token_type depend on that function's mappings.

1) NAME token expression -> returns the raw name value
    try:
        result = describe_token_expr("NAME:username")  # assuming TOKEN_NAME == "NAME"
        # result == "username"
    except Exception as e:
        # handle missing TOKEN_NAME or other runtime errors
        raise

2) Non-name token with a value -> returns description for the token type (left side)
    try:
        # expr contains a colon but TYPE is not TOKEN_NAME
        result = describe_token_expr("DATA:ignored_value")
        # result == _describe_token_type("DATA")  (e.g., "template data / text" if that mapping exists)
    except Exception as e:
        raise

3) Bare token type -> returns description for that type
    try:
        result = describe_token_expr("END")
        # result == _describe_token_type("END")
    except Exception as e:
        raise

Usage note:
- When formatting error messages, catch and handle NameError/TypeError if the runtime environment might not have the expected lexer constants or if inputs may be malformed.

## `src.jinja2.lexer.count_newlines` · *function*

## Summary:
Counts how many times the module-level compiled regular expression (newline_re) matches substrings in the provided text and returns that count as a non-negative integer.

## Description:
This utility returns the number of occurrences matched by the module-level regex object newline_re when applied to the given string. It centralizes newline-counting logic so callers do not need to compile or manage the regex themselves.

Known callers within the provided context:
    - No direct call sites were discovered in the provided source snapshot.

Typical usage context:
    - Used in lexer/tokenizer code paths that must update or compute line counts for error reporting or token location tracking. The function enforces a single point of responsibility for counting newline-like sequences.

Reason for extraction:
    - Keeps newline-counting semantics in one place, avoids repeated regex compilation, and simplifies calling code by returning an easily-consumable integer count.

## Args:
    value (str): The input text to search for newline matches.
        - Required type: str (annotated in the signature).
        - Behavior for other types: passing a non-str may raise a TypeError from the underlying regex engine or other runtime exceptions (see Raises).

## Returns:
    int: Number of matches found by newline_re.findall(value).
        - Always a non-negative integer.
        - Zero when no matches are found (for example, an empty string or when the pattern does not match).
        - Note about capture groups: If newline_re's pattern contains capturing groups, re.findall returns a list of strings (for a single group) or tuples (for multiple groups). The function returns the length of that list, which equals the number of match occurrences, not the number of captured groups.

## Raises:
    - The function contains no explicit raise statements; however, exceptions from the called operations may propagate:
        * NameError: If the module-level name newline_re is not defined at runtime.
        * AttributeError: If newline_re exists but does not provide a findall method (i.e., is not a compiled regex-like object).
        * TypeError: If value is of an incompatible type for the regex engine (for example, None).
    - These exceptions originate from Python's attribute lookup and the regex engine when called; they are not raised by checks inside this function.

## Constraints:
    Preconditions:
        - The caller should pass a str value.
        - The module-level variable newline_re must be defined and should be a compiled regular expression object (or any object exposing a findall(str) method that behaves like re.Pattern.findall).

    Postconditions:
        - The returned integer equals len(newline_re.findall(value)).
        - No mutation to input or external state occurs.

## Side Effects:
    - None. The function performs no I/O and does not mutate global variables or external state; it only calls newline_re.findall(value) and computes its length.

## Control Flow:
flowchart TD
    Start --> EnsureRegex[Assume newline_re exists]
    EnsureRegex --> CallFindall[newline_re.findall(value)]
    CallFindall --> matchesReturned[receive list of matches]
    matchesReturned --> ComputeLen[len(matches)]
    ComputeLen --> Return[return count]
    Return --> End

## Examples:
Note: The exact counts in these examples depend on the module-level newline_re pattern. The examples below assume newline_re matches the single-character newline '\n'. If newline_re is defined to match other sequences (e.g., '\r\n' or Unicode line separators) results will vary accordingly.

    Example 1 — basic usage (assumes newline_re matches '\n')
        >>> text = "line1\nline2\nline3"
        >>> count_newlines(text)
        2

    Example 2 — no matches
        >>> text = "single line with no newline sequences"
        >>> count_newlines(text)
        0

    Example 3 — pattern with capture groups (behavior note)
        # If newline_re contains a capturing group, re.findall returns strings or tuples.
        # The function still returns the number of match occurrences.
        >>> # Suppose newline_re.findall("a\nb\n") returns ['\n', '\n'] or [('\n',),('\n',)]
        >>> count_newlines("a\nb\n")
        2

    Example 4 — defensive use with error handling
        >>> try:
        ...     result = count_newlines(None)  # incorrect type
        ... except (TypeError, AttributeError, NameError) as e:
        ...     # Handle misspecified input or module misconfiguration
        ...     print("count_newlines failed:", type(e).__name__)
        count_newlines failed: TypeError

## `src.jinja2.lexer.compile_rules` · *function*

## Summary:
Constructs lexer matching rules from an Environment's delimiter and prefix strings and returns an ordered list of (token, regex_pattern) pairs with longer delimiters given precedence.

## Description:
This function converts the delimiter and optional line-prefix configuration held on an Environment instance into escaped regex patterns and associated token identifiers. It uses re.escape to ensure literal matching of delimiters and special handling for line-based prefixes (anchoring and surrounding-whitespace handling). The returned list is sorted so that entries derived from longer delimiter strings are placed earlier — ensuring the lexer will attempt to match longer delimiters before shorter ones.

Known callers within the codebase:
    - No concrete call sites were found in the provided snapshot. Typical placement is inside lexer construction or initialization where the lexer needs a compiled set of (token, pattern) rules derived from an Environment before tokenizing template source.

Why this is factored out:
    - Centralizes and standardizes the mapping from declarative Environment settings to runtime regex rules and ordering logic. Extracting it prevents duplication of escaping/anchoring logic and enforces a single ordering policy (longest-first) for delimiter precedence.

## Args:
    environment (Environment): An Environment-like object exposing these attributes:
        - comment_start_string (str): the literal string that begins a comment.
        - block_start_string (str): the literal string that begins a block tag.
        - variable_start_string (str): the literal string that begins a variable tag.
        - line_statement_prefix (Optional[str]): if not None, a prefix that begins a line statement; an anchored regex rule is produced.
        - line_comment_prefix (Optional[str]): if not None, a prefix that begins a line comment; a whitespace-aware anchored regex rule is produced.

    Interdependencies and expectations:
        - The first three attributes are expected to be present and represent the core delimiters; the function always includes rules for them.
        - The last two are optional: if set to None they are skipped.
        - Attribute values should normally be non-empty strings. Empty-string values are accepted by the code (see Edge Cases) but will produce patterns that match the empty string and may break typical lexing expectations.

## Returns:
    list[tuple[str, str]]: Ordered list of 2-tuples where:
        - tuple[0] (str): the token identifier constant associated with the delimiter (the second element of the internal rule tuple; e.g., TOKEN_COMMENT_BEGIN).
        - tuple[1] (str): the regex pattern string to match that delimiter. Patterns are produced by re.escape(...) of the delimiter and, for line prefixes, are prefixed with additional anchors/whitespace matchers.

    Return shape details:
        - Always returns at least three tuples (comment, block, variable).
        - May include up to two additional tuples if line_statement_prefix and/or line_comment_prefix are provided.
        - The list is sorted with higher precedence first: primary sort key is the length of the original delimiter (longer first). When lengths tie, the secondary ordering arises from the remaining tuple items used by sorted(), but caller code should rely only on the longest-first guarantee.

## Raises:
    The function does not raise library-specific exceptions itself, but the following errors can occur due to attribute access or invalid attribute types:
        - AttributeError: if environment is missing any of the expected attributes (e.g., comment_start_string), attribute access will raise this.
        - TypeError: if an attribute used with len(...) is not a sized object or if re.escape is given a value of an unsupported type (e.g., None when a string is expected), a TypeError may be raised.
        - Any exception raised by re.escape for invalid input types will propagate (commonly TypeError).

## Constraints:
    Preconditions:
        - Caller must provide an object with the listed attributes.
        - Delimiter/prefix values should be strings (or bytes where appropriate). Setting a delimiter to an empty string is supported by the implementation but is not recommended.

    Postconditions:
        - Returns a new list of (token, pattern) tuples sorted so rules derived from longer delimiter strings appear earlier.
        - Does not mutate the Environment object or any global state.

## Side Effects:
    - None. The function performs no I/O and does not change external/global state.

## Edge Cases and Notes:
    - Empty-string delimiters: If a delimiter attribute equals the empty string (''), re.escape('') yields '' and the generated pattern will match an empty position. Such a rule will effectively match everywhere and likely short-circuit the lexer's matching logic. Consumers should avoid configuring empty delimiters.
    - Sorting behavior: The function constructs internal 3-tuples (length, token, pattern) and sorts them with reverse=True. This guarantees descending order by length as the primary key. If two delimiters share the same length, Python's tuple comparison will use token and pattern as tie-breakers; callers should not rely on a particular tie-breaker beyond length.
    - Line-prefix patterns:
        - line_statement_prefix uses the prefix r'^[ \t\v]*' + re.escape(prefix) — this anchors the prefix at the start of a line, allowing only horizontal whitespace (spaces, tabs, vertical tabs) before it.
        - line_comment_prefix uses r'(?:^|(?<=\S))[^\S\r\n]*' + re.escape(prefix) — this matches the prefix either at the start of a line or immediately after a non-whitespace character, allowing any horizontal whitespace (except newline) between that boundary and the prefix.

## Control Flow:
flowchart TD
    Start([start]) --> BuildBase["Create base rules for comment, block, variable (len, token, escaped)"]
    BuildBase --> CheckLineStmt{line_statement_prefix is not None?}
    CheckLineStmt -- yes --> AppendLineStmt["Append (len, TOKEN_LINESTATEMENT_BEGIN, anchored escaped pattern)"]
    CheckLineStmt -- no --> SkipLineStmt[skip]
    AppendLineStmt --> CheckLineComment{line_comment_prefix is not None?}
    SkipLineStmt --> CheckLineComment
    CheckLineComment -- yes --> AppendLineComment["Append (len, TOKEN_LINECOMMENT_BEGIN, whitespace-aware escaped pattern)"]
    CheckLineComment -- no --> SkipLineComment[skip]
    AppendLineComment --> Sort["Sort internal tuples descending (primary key: length)"]
    SkipLineComment --> Sort
    Sort --> StripLengths["Return list of (token, pattern) by removing length element"]
    StripLengths --> End([return rules])

## Examples (illustrative, non-executable):
    Example environment description:
        - comment_start_string: '<!--'  (length 4)
        - block_start_string: '{%'      (length 2)
        - variable_start_string: '{{'   (length 2)
        - line_statement_prefix: None
        - line_comment_prefix: '#'      (length 1)

    Result shape (conceptual):
        - The returned list will contain the comment rule first (because length 4),
          then the block and variable rules (length 2, tie broken by token/pattern),
          and finally the line_comment rule (length 1).
        - Each pattern is the escaped form of the delimiter; for example, '{{' becomes '\{\{' in the regex string returned.

    Error handling guidance:
        - If AttributeError occurs: ensure the Environment instance provides the required attribute names.
        - If TypeError occurs during re.escape or len: verify that each used attribute is a proper string (not None or another non-sized type).

## `src.jinja2.lexer.Failure` · *class*

## Summary:
Represents a callable error factory that, when invoked with line and file information, raises a parsing/lexing TemplateSyntaxError (or a provided subclass) with a fixed message.

## Description:
Failure is a small value object used by the lexer to encapsulate a diagnostic message and the exception class to raise later. Instead of raising immediately when a lexing rule fails, the lexer can create a Failure instance carrying the message and the exception type and pass that object around; invoking the instance with a line number and filename produces the actual exception.

Typical callers:
- The lexer and its rule-handling machinery instantiate Failure objects when a particular lexing or parsing condition should ultimately produce a TemplateSyntaxError but the precise location (lineno, filename) is not yet available.
- Any component that needs to defer raising a TemplateSyntaxError until additional context (line/file) is determined can use this class.

Responsibility boundary:
- Encapsulate a constant error message and an exception class.
- Provide a single-call interface that raises the stored exception with the message plus location information.
- Not responsible for validating the provided exception class; it simply stores and uses it.

## State:
- message (str)
  - Type: str
  - Valid values: any string; typically a human-readable error description produced by the lexer.
  - Invariant: remains equal to the message passed to __init__.

- error_class
  - Type: t.Type[TemplateSyntaxError] (exact type expression as in the source)
  - Valid values: any callable/class accepted as an exception; defaults to TemplateSyntaxError.
  - Invariant: remains equal to the cls argument passed to __init__.

Class invariants:
- After construction, the two attributes message and error_class remain unchanged unless externally mutated.
- The object is intended to be immutable in practice (no methods to mutate state).

## Lifecycle:
Creation:
- Instantiate with two arguments:
  - message (required): a str describing the error.
  - cls (optional): t.Type[TemplateSyntaxError], defaulting to TemplateSyntaxError.
- Example signature (as implemented):
  - __init__(self, message: str, cls: t.Type[TemplateSyntaxError] = TemplateSyntaxError)

Usage:
- The instance is a callable. Call it with:
  - lineno (int): the line number where the error happened.
  - filename (str): the filename associated with the template source.
- When called, the instance raises an exception by calling the stored error_class with (message, lineno, filename) and does not return.
- Typical sequencing:
  1. Create Failure with a message (and optionally a custom exception class).
  2. Later, when location info is available, call the Failure instance with lineno and filename to raise.

Destruction / cleanup:
- No special cleanup is required. The object participates in normal GC.
- It does not implement context manager protocols or close methods.

## Method Map:
flowchart LR
    A[Construct Failure(message, cls?)] --> B[Store message, error_class]
    B --> C[Call instance with (lineno, filename)]
    C --> D[Raise error_class(message, lineno, filename)]
    D --> E[Control flow interrupted (no return)]

(Interpretation: construct -> store state -> call -> raise -> (no return).)

## Raises:
- __init__: The constructor does not explicitly raise exceptions in the implementation. However, passing values that are invalid for later usage is possible (for example, an error_class without a compatible constructor) — such problems will surface when the instance is called.
- __call__: Always raises the stored error_class by invoking it as error_class(message, lineno, filename). Concretely:
  - Default case: raises exceptions.TemplateSyntaxError(message, lineno, filename)
  - If a custom cls was supplied, the call raises cls(message, lineno, filename).
  - Any exception raised is the direct result of calling the stored exception class constructor; if that constructor raises for other reasons, that exception propagates.

## Example:
- Creation:
  - Create a Failure with the message "unexpected end of template". Optionally pass a subclass of TemplateSyntaxError to cls; otherwise the default TemplateSyntaxError is used.

- Deferring and raising:
  1. The lexer detects an error but does not yet know the precise line/file; it constructs a Failure with the error message.
  2. The lexer continues until it can compute the lineno and filename.
  3. The lexer invokes the Failure instance with the computed lineno and filename.
  4. The call raises the stored error_class initialized with (message, lineno, filename) and does not return.

Notes:
- The class is intentionally minimal: it centralizes the pattern "store an error to be raised later with location information".
- Callers should ensure the stored error_class accepts (message, lineno, filename) as constructor arguments; otherwise, calling the Failure instance will raise a different error at invocation time.

### `src.jinja2.lexer.Failure.__init__` · *method*

## Summary:
Stores an error message and the exception class to use later so the Failure instance can be invoked to raise that exception with contextual location (lineno, filename).

## Description:
This initializer captures the textual error message and the exception class when a Failure object is created. The stored values are later used by the Failure.__call__ method to instantiate and raise the exception with line and file context.

Known callers and context:
- Instantiated where a lexer-detected error needs to be recorded now but raised later when line number and filename are available. The Failure instance is typically created at the point of detection and is invoked later (via its __call__ method) to actually raise the configured exception.
- The class's own __call__ method is a direct consumer of the stored attributes: invoking failure_instance(lineno, filename) will raise error_class(message, lineno, filename).

Why this is a separate initializer:
- Separates configuration (what error to raise and its message) from the raising action (which needs location context). This enables deferring the actual raise until the caller can supply lineno/filename and keeps raising logic localized to __call__.

## Args:
    message (str):
        Human-readable error message describing the failure. This value is stored verbatim on self.message.
    cls (t.Type[TemplateSyntaxError], optional):
        Exception class to instantiate when the Failure is invoked.
        - Default: TemplateSyntaxError
        - Expected to be a class (commonly a subclass of TemplateSyntaxError) whose constructor accepts the signature (message: str, lineno: int, filename: str).

## Returns:
    None

## Raises:
    The initializer itself does not raise. (If callers provide invalid types, errors will surface later when the instance is invoked.)

## State Changes:
    Attributes READ:
        - None
    Attributes WRITTEN:
        - self.message (str): set to the provided message argument.
        - self.error_class (t.Type[TemplateSyntaxError]): set to the provided cls argument or TemplateSyntaxError.

## Constraints:
    Preconditions:
        - Caller should pass a string for message.
        - Caller should pass an exception class for cls that can be instantiated as error_class(message, lineno, filename).
    Postconditions:
        - After return, self.message equals the provided message and self.error_class equals the provided cls (or the default TemplateSyntaxError).

## Side Effects:
    - No I/O or interactions with external services.
    - Only mutates attributes on the Failure instance (self.message and self.error_class).

## Usage note (prose example):
Create a Failure with the desired message and optional exception class at the point an error is detected; later, when line and file context are known, invoke the instance (call it) with (lineno, filename) to raise the configured exception. If cls does not accept the expected constructor arguments, a TypeError or other exception will occur at the time of invocation, not during __init__.

### `src.jinja2.lexer.Failure.__call__` · *method*

## Summary:
Raises the stored error_class using the stored message and the provided source location; never returns (always raises).

## Description:
This method is the invocation point for a Failure instance: calling it constructs and raises an exception of the type stored in self.error_class, passing the stored message together with the provided lineno and filename. The method is part of the lexer module and exists to centralize the construction and raising of template syntax errors that include location metadata rather than inlining that logic at each error site.

Known callers and context:
    - The direct call sites are not included in the provided snippet. Within the lexer module, instances of Failure are intended to be called when the lexer/parser detects an unrecoverable syntax error and needs to raise a TemplateSyntaxError (or a subclass) with the message and location information.

Why this is a separate method:
    - Encapsulates the exact exception construction and raising logic so that error creation is uniform and easily passed around (for example, as a callback or stored handler). Keeping this logic in one place ensures consistent exception types and message formatting across the lexer.

## Args:
    lineno (int): Line number in the source/template where the error occurred. Expected to be an integer representing the source line associated with the error location.
    filename (str): Name or path of the source/template file associated with the error.

## Returns:
    typing_extensions.NoReturn: This method does not return. It always raises an exception constructed from self.error_class and therefore never produces a normal return value.

## Raises:
    Exception type: The class stored in self.error_class (by default TemplateSyntaxError).
    Condition: Always — calling this method will unconditionally construct and raise self.error_class(self.message, lineno, filename).
    Notes: If self.error_class is not callable with the three arguments (message, lineno, filename), the call will raise a TypeError (or whatever exception results from an incorrect constructor signature).

## State Changes:
    Attributes READ:
        self.message
        self.error_class
    Attributes WRITTEN:
        None — the method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.error_class must be a callable (typically an exception class) whose constructor accepts three positional arguments: (message: str, lineno: int, filename: str). If it does not, the attempt to construct the exception will raise a TypeError or similar.
        - self.message should be a string (as set by Failure.__init__) representing the error description.
        - lineno must be an integer and filename must be a string as they are forwarded to the exception constructor; the method does not validate their ranges or values.

    Postconditions:
        - The call does not complete normally; instead, it raises an exception instance of self.error_class initialized with (self.message, lineno, filename).
        - No attributes on self or external objects are modified by this method.

## Side Effects:
    - Raises an exception (control flow side effect). There is no I/O, no external service interaction, and no mutation of objects outside self performed by this method.

## `src.jinja2.lexer.Token` · *class*

## Summary:
Represents a single lexer token produced by the template lexer: an immutable triple (lineno, type, value) with small read-only helpers to test and describe the token.

## Description:
Token is a lightweight, immutable data holder (a NamedTuple) used to carry lexical information from the lexer to later stages of parsing. Typical callers/factories are functions in the lexer that create Token instances for each recognized lexeme in a template source. The class exists to give a consistent, typed container for:
- lineno: the source line number where the token was found,
- type: the token's kind (for example, names like "data", "block_begin", or other lexer-specific type strings),
- value: the textual payload associated with the token (such as the matched text or identifier).

Token also provides convenience methods:
- __str__: returns a concise, human-readable label for the token by delegating to the module-level describe_token(token) helper. This presentation helper is read-only and does not modify token state.
- test(expr): match the token against a simple expression or a "type:value" expression.
- test_any(*iterable): check whether the token matches any of several expressions.

This class is strictly a data+helper container and enforces no complex invariants itself (immutability comes from being a NamedTuple).

## State:
- lineno (int)
    - Type: int
    - Meaning: the line number where this token was produced (conventionally a source line number).
    - Constraints: no runtime validation in this class; callers should pass an integer. If a non-int is passed, type checkers will flag the mismatch, but Python will accept it at runtime.
- type (str)
    - Type: str
    - Meaning: the token category name (a short string used by parser/consumer to switch behavior).
    - Constraints: expected to be a plain string. Equality comparisons use exact string equality.
- value (str)
    - Type: str
    - Meaning: the token payload (matched text, identifier, literal contents, etc.).
    - Constraints: expected to be a string; no internal normalization occurs here.

Class invariants:
- Instances are immutable (behavior of NamedTuple): once created, lineno, type, and value do not change.
- Methods operate purely on the stored fields and do not mutate state.

## Lifecycle:
Creation:
- Instantiate by calling Token(lineno, type, value).
- Required positional arguments: lineno, type, value. There are no defaults.
- Alternative creation: typical lexers will construct Token objects directly as they tokenize input.

Usage:
- Typical sequence:
    1. Construct Token with the three fields.
    2. Use token.test(expr) to check whether the token matches a pattern, or token.test_any(a, b, c) to check multiple patterns.
    3. Use str(token) (or print(token)) to obtain a concise, human-readable description produced by the module-level describe_token(token) helper.
- There is no enforced ordering among these read-only helpers. The __str__ method is read-only and will not modify the token.
- No cleanup or destruction ordering is required.

Destruction:
- No explicit cleanup is necessary. Token objects rely on normal Python garbage collection. They do not implement context managers or close semantics.

## Method Map:
graph TD
    T[Token instance]
    T --> STR["__str__\n(delegates to describe_token(token), read-only)"]
    T --> TEST["test(expr)\n- if self.type == expr -> True\n- elif ':' in expr -> compare ['type','value']"]
    T --> TESTANY["test_any(*exprs)\n- calls test(expr) for each\n- returns True if any match"]
    STR --> describe_token["describe_token(token) (module-level helper)"]
    TEST --> equality["string equality: self.type == expr"]
    TEST --> colon_split["if ':' in expr => expr.split(':',1) == [self.type, self.value]"]

## Raises:
- On instantiation:
    - TypeError: raised by Python if the constructor is called with the wrong number of positional arguments (standard NamedTuple/typing behavior).
- On __str__:
    - The method delegates to describe_token(token) and may propagate exceptions raised by that helper (for example, TypeError or other runtime errors originating from the module-level formatting logic). The __str__ method itself does not perform additional validation.
- Methods test and test_any:
    - The methods expect string expressions. If a non-string is passed to test(expr), typical runtime errors may occur (e.g., TypeError when checking membership ":" in expr or AttributeError when calling expr.split). The class does not validate argument types itself.

## Example:
- Typical construction and usage (conceptual example; not source code):
    - Create a token for line 10 with type "name" and value "user":
        - Token(10, "name", "user")
    - Check exact type match:
        - token.test("name") -> True
    - Check type:value pair:
        - token.test("name:user") -> True
    - Check multiple possible matches:
        - token.test_any("data", "name:user", "block_begin") -> True if any expression matches
    - Get a printable description:
        - str(token) -> result of describe_token(token) (module-level helper)

Notes and implementation hints:
- The test method first checks exact equality with the token type. Checking "name" will match before any "type:value" style match is attempted.
- The "type:value" matching uses a single split at the first colon; the code compares the resulting [type, value] list to [self.type, self.value].
- test_any accepts any number of string expressions and short-circuits on the first successful match.
- Because Token is a NamedTuple, reimplementation should preserve immutability and field order (lineno, type, value) and the same method semantics.

### `src.jinja2.lexer.Token.__str__` · *method*

## Summary:
Return a concise, human-readable label for this token by delegating to the module helper that formats tokens; it does not modify the token's state.

## Description:
This dunder method is invoked whenever the Token instance is converted to a string (for example via str(token) or when the token is formatted into an error message or debug output). Typical callsites and contexts:
- Error formatting for lexer/parser diagnostics (producing readable token names inside TemplateSyntaxError messages).
- Debugging and logging code that prints or logs Token objects.
- Any code that implicitly converts a Token to str (e.g., f"{token}" or "{}".format(token)).

Why this is a separate method:
- String conversion of a Token must follow a single, consistent rule for human-facing labels. That logic is implemented in the module-level helper describe_token; Token.__str__ keeps the delegation explicit and minimal so the rule is centralized and easy to maintain.

## Args:
    self (Token): The Token instance to stringify. The method expects the object to expose at least:
        - .type (str): token type identifier
        - .value (str): token literal (used for name tokens)

## Returns:
    str: A short human-facing label for the token produced by calling describe_token(self).
    Possible outcomes (determined by describe_token):
        - If the token represents an identifier/name (module constant TOKEN_NAME), returns the token.value (the identifier text).
        - Otherwise returns a descriptive string for the token.type as provided by the module mapping, or falls back to returning token.type unchanged when no mapping exists.
    The return value is always a str when describe_token successfully completes.

## Raises:
    AttributeError:
        - If the Token instance does not expose .type or .value attributes (attribute access fails).
    NameError:
        - If module-level constants required by describe_token (for example TOKEN_NAME) are missing from the lexer module at runtime.
    Any exception raised by describe_token or its helpers:
        - For example, exceptions from the internal mapping function (_describe_token_type) such as TypeError (if token.type is an unexpected/unhashable value) or other runtime errors. Token.__str__ does not catch these; exceptions propagate to the caller.

## State Changes:
    Attributes READ:
        - self.type
        - self.value
    Attributes WRITTEN:
        - None (this method does not modify the Token instance)

## Constraints:
    Preconditions:
        - The object must behave like the module Token (have .type and .value attributes).
        - token.type should be a string-like, hashable token identifier acceptable to describe_token/_describe_token_type.
        - The lexer module must define any constants used by describe_token (e.g., TOKEN_NAME).
    Postconditions:
        - No mutation of the Token instance or global state.
        - A str describing the token is returned if no exception is raised.

## Side Effects:
    - None. No I/O, logging, network access, or mutation of external objects is performed by this method; it merely delegates and returns the result.

## Implementation notes for reimplementation:
    - Implement __str__ to forward the Token instance to the module-level describe_token function and return its result.
    - Do not attempt to replicate describe_token's mapping logic in __str__; keep the delegation to ensure consistent wording across the codebase.

### `src.jinja2.lexer.Token.test` · *method*

## Summary:
Performs a match check between this token and an expression string, returning True when the expression refers to this token's type or to this token's exact type:value pair.

## Description:
This method is a compact matcher used to determine whether a token satisfies a given expression used by token-matching code. Known callers:
- Token.test_any (present on the same class) which composes multiple match expressions.
- Lexer and parser token-matching logic (common usage): the method is typically invoked during lexing or parsing when a component needs to check whether the current token is of a particular type or a specific type/value pair.

Why this is a separate method:
- Centralizes the matching semantics (simple type equality and optional compound "type:value" equality) so callers do not duplicate string-splitting and comparison logic.
- Keeps caller code concise and consistent; test_any can rely on this single implementation for matching behavior.

Behavior summary:
- If expr exactly equals the token's type (self.type), returns True.
- Otherwise, if expr contains a colon (":"), splits expr at the first colon only and returns True if the left-hand part equals self.type and the right-hand part equals self.value.
- For all other cases returns False.

Examples (illustrative):
- For a token with type name and value foo:
  - expr = name  -> True
  - expr = name:foo -> True
  - expr = name:bar -> False
  - expr = name:foo:bar -> True if self.value == "foo:bar" (only the first colon is used to split)

## Args:
    expr (str): The match expression. Two accepted forms:
        - A plain token type string (e.g., "name")
        - A compound "type:value" string where the portion before the first colon is compared to the token type and the portion after the first colon is compared to the token value.
    No default value; callers must supply a string.

## Returns:
    bool: True when the expression matches this token according to the rules above; False otherwise.
    - True when expr == self.type
    - True when ":" in expr and expr.split(":", 1) == [self.type, self.value]
    - False in all other cases

## Raises:
    TypeError: If expr is not a string (e.g., None or a non-iterable), operations like the membership check (":" in expr) or equality comparisons will raise a TypeError at runtime.
    Note: the method itself does not explicitly raise other exceptions; attribute access assumes self has attributes type and value (Token as a NamedTuple guarantees these).

## State Changes:
    Attributes READ:
        self.type
        self.value
    Attributes WRITTEN:
        None — this method does not modify self or any external state.

## Constraints:
    Preconditions:
        - self must expose string attributes type and value (the Token NamedTuple provides these).
        - expr should be a str; callers passing non-str values risk TypeError.
    Postconditions:
        - No mutation occurs on self or other objects.
        - The return value is deterministic and based only on self.type, self.value, and expr.

## Side Effects:
    - None: the method performs pure string operations and comparisons only; it does not perform I/O, logging, or mutate external objects.

## Implementation notes (for reimplementation):
    - Perform the equality check self.type == expr first (fast path).
    - Use a single split with maxsplit=1 (expr.split(":", 1)) when a colon is present so that additional colons in the value are preserved on the right-hand side.
    - All string comparisons are exact and case-sensitive (no normalization performed).

### `src.jinja2.lexer.Token.test_any` · *method*

## Summary:
Check whether this token matches any one of the provided match expressions; returns True as soon as one match is found.

## Description:
Performs a multi-expression match by delegating each expression to the token's single-expression matcher. Known callers and context:
- Lexer and parser token-matching logic during lexing/parsing phases, where components need to accept multiple alternative token types or type:value pairs.
- Call sites that want to test several possible token patterns in a single, concise call instead of invoking the single-expression matcher repeatedly.

Why this is a separate method:
- Encapsulates the common pattern of testing against multiple candidate expressions and centralizes short-circuiting behavior so callers remain concise and consistent.
- Keeps callers free from manually iterating expressions or duplicating call-site logic for early exit when a match is found.

## Args:
    *iterable (str): Zero or more match expression strings. Each expression should follow the same conventions accepted by the single-expression matcher:
        - A token type string (e.g., "name")
        - A compound "type:value" string where the portion before the first colon is compared to the token type and the portion after the first colon is compared to the token value
    Notes:
        - Passing no arguments is allowed; the method will return False in that case.
        - Expressions should be str; passing non-str values will likely raise a TypeError when evaluated.

## Returns:
    bool: True if at least one provided expression matches this token according to the single-expression matching rules; False otherwise.
    - Returns False for an empty argument list.
    - Evaluation is short-circuited: as soon as a matching expression is found the method returns True and remaining expressions are not tested.

## Raises:
    TypeError: If any provided expression is not a string (e.g., None or another non-str type), the delegated single-expression matcher will perform string operations that raise a TypeError.
    Note: The method itself does not explicitly raise other exceptions; any exception raised by the delegated matcher will propagate.

## State Changes:
    Attributes READ:
        self.type (used indirectly via self.test)
        self.value (used indirectly via self.test)
    Attributes WRITTEN:
        None — no attributes of self are modified.

## Constraints:
    Preconditions:
        - self must expose string attributes type and value (Token NamedTuple provides these).
        - Each expression in iterable should be a str following the single-expression matcher format.
    Postconditions:
        - No mutation of self or external objects occurs.
        - The return value is a deterministic bool computed from self.type, self.value, and the supplied expressions.
        - If True is returned, it implies that at least one expression satisfied the single-expression matching rules.

## Side Effects:
    - None intrinsic: the method performs only in-process string comparisons and calls the pure single-expression matcher.
    - Note: if the delegated matcher (self.test) were modified to have side effects, those would occur; as implemented, there are no I/O or external interactions.

## `src.jinja2.lexer.TokenStreamIterator` · *class*

## Summary:
A thin iterator wrapper over a TokenStream that implements Python's iterator protocol by yielding the stream's current Token and advancing the underlying stream; closes the stream and ends iteration when it reaches the EOF token.

## Description:
TokenStreamIterator is a small adapter that makes a TokenStream usable in iteration contexts (for loops, next(), iter(), and other consumers that expect an iterator). It is instantiated by TokenStream.__iter__ and is the object returned whenever a TokenStream is iterated. Typical callers are the parser/lexer pipeline and any code that consumes tokens one-by-one.

Motivation:
- Keeps iterator semantics (return current token, detect EOF, advance, and close on EOF) in one place so callers do not need to manipulate the TokenStream directly.
- Separates iteration behavior from TokenStream internals while remaining lightweight.

Responsibility boundary:
- It does not implement token production; that responsibility stays with the underlying TokenStream.
- It assumes the stream exposes a current attribute, supports next(self.stream) to advance, and a close() method.
- It does not buffer tokens or provide random access — it only yields the current token and advances.

## State:
- stream: TokenStream
    - Type: TokenStream (an object that exposes current: Token, __next__ to advance via next(stream), and close(): None)
    - Valid values: a live TokenStream instance created by TokenStream(...). Must not be None.
    - Invariants:
        - stream.current is always a Token instance while the stream is live.
        - If stream.current.type is TOKEN_EOF, the iterator will call stream.close() and raise StopIteration.
    - Notes on __init__ parameter:
        - The constructor requires a single positional argument: stream, which must already be a properly initialized TokenStream (TokenStream.__init__ calls next(self) to prime current).
        - No default value; callers must supply a TokenStream instance.

Class invariants:
- The iterator object simply forwards to the underlying stream; there is no independent token cursor beyond stream.current.
- Using the same TokenStreamIterator instance in more than one concurrent iteration shares state; tokens consumed by one consumer are not available to another reuse of the same iterator.

## Lifecycle:
Creation:
- Instantiate by calling TokenStream.__iter__(), which returns TokenStreamIterator(self). Alternatively, callers may construct TokenStreamIterator(stream) directly with a prepared TokenStream.
- Required argument: stream (TokenStream). The stream should be initialized and primed so stream.current contains the first logical token.

Usage:
- Typical usage patterns:
    - Use in a for-loop: for token in token_stream: ...
    - Explicit iteration: it = iter(token_stream); token = next(it)
- Call sequence per iteration:
    1. __next__ reads token = stream.current.
    2. If token.type is TOKEN_EOF:
        - Calls stream.close()
        - Raises StopIteration
    3. Otherwise:
        - Calls next(stream) to advance the underlying stream to the following token.
        - Returns the token that was read in step 1.
- __iter__ returns self to satisfy iterator protocol; no state reset happens on __iter__.

Destruction / cleanup:
- The iterator does not implement a close method or context manager protocol.
- When iteration reaches EOF, the iterator ensures the underlying TokenStream is closed (stream.close() is called).
- There is no other explicit cleanup; normal garbage collection applies.

## Method Map:
graph TD
    TS[TokenStream] -->|__iter__ returns| TSI[TokenStreamIterator]
    TSI -->|__iter__ returns self| SELF(self)
    TSI -->|__next__| CHECK{read stream.current}
    CHECK -->|if token.type is TOKEN_EOF| CLOSE_AND_STOP[call stream.close(); raise StopIteration]
    CHECK -->|else| ADVANCE[call next(stream)]
    ADVANCE -->|returns| RETURN_TOKEN[return previously-read token]

## Raises:
- __init__
    - No explicit exceptions raised by __init__ itself. However, if the passed stream is malformed (missing attributes), attribute access will later raise when methods are used.
- __next__
    - StopIteration:
        - Raised when the current token's type is TOKEN_EOF. Before raising, stream.close() is invoked.
    - AttributeError or other propagated exceptions:
        - If stream or stream.current is missing or not the expected type, attribute access or next(stream) may raise AttributeError or TypeError; these propagate to the caller. These are precondition violations (caller must pass a valid TokenStream).

## Example:
- Getting an iterator from a TokenStream and iterating (conceptual usage):
    - token_stream = TokenStream(generator, name, filename)   # TokenStream primes current
    - it = iter(token_stream)  # returns a TokenStreamIterator
    - while True:
          try:
              token = next(it)  # yields current token; advances stream
          except StopIteration:
              break
    - Or more simply:
          for token in token_stream:
              process(token)
    - Notes:
      - Iteration ends when a token with type TOKEN_EOF is encountered; the iterator will call token_stream.close() and StopIteration will be raised.
      - Re-using the same TokenStreamIterator in nested loops shares the same underlying stream state and is not safe for independent passes.

### `src.jinja2.lexer.TokenStreamIterator.__init__` · *method*

## Summary:
Stores a reference to the TokenStream to create an iterator object that delegates iteration operations to that stream, establishing the iterator's internal state.

## Description:
This constructor is called when a new TokenStreamIterator is created to iterate over a TokenStream. Known callers and usage contexts:
- TokenStream.__iter__ constructs and returns TokenStreamIterator(self) when iteration over a TokenStream begins (e.g., when "for token in token_stream" or iter(token_stream) is used).
- Any external code that explicitly creates an iterator for a TokenStream by calling TokenStreamIterator(token_stream).

This logic is implemented as a small constructor rather than being inlined because the iterator object needs to hold a persistent reference to the TokenStream and participate in Python's iterator protocol via its own __iter__ and __next__ methods. Keeping this initialization separate clarifies ownership (the iterator holds a reference) and keeps iteration semantics (in __next__) localized to the iterator class.

## Args:
    stream (TokenStream):
        - A TokenStream instance that provides the token cursor state (attributes and methods used by the iterator: current, close, and __next__ semantics via next(stream)).
        - No default. Must be supplied.
        - Allowed values: any object implementing the TokenStream interface (see TokenStream class in src.jinja2.lexer). Passing None or an incompatible object will not raise here but will cause attribute or protocol errors when using the iterator.

## Returns:
    None
    - The constructor does not return a value; it initializes the iterator object in-place.

## Raises:
    - This method does not explicitly raise exceptions.
    - Implicit errors: if a non-conforming object is provided as stream, subsequent iterator operations will raise AttributeError or TypeError when those operations attempt to access expected attributes or call next(stream).

## State Changes:
    Attributes READ:
        - None in the constructor body (it does not inspect or call methods on the stream).
    Attributes WRITTEN:
        - self.stream: set to the provided stream reference.

## Constraints:
    Preconditions:
        - The caller should provide an object that implements the TokenStream interface expected by TokenStreamIterator:
            * Has a .current attribute (a Token-like object with .type and .lineno used by __next__).
            * Implements .close() and supports being advanced via next(stream) (i.e., is an iterator object with __next__).
        - The TokenStream may be already advanced or closed; the constructor does not validate that state.

    Postconditions:
        - After construction, self.stream holds a direct reference to the provided TokenStream object.
        - No other attributes on self are modified or created by this constructor.
        - The iterator and the TokenStream share the same mutable state: advancing the iterator will mutate the TokenStream's state (the TokenStream is not copied).

## Side Effects:
    - None performed by the constructor itself (no I/O, no external service calls).
    - Important semantic side effect to note: because the iterator stores a reference to the same TokenStream object, iteration via this TokenStreamIterator will mutate the TokenStream (advance its cursor, possibly close it). Multiple iterator instances created for the same TokenStream will share and mutate the same underlying stream state.

Notes:
- See src.jinja2.lexer.TokenStream for the TokenStream responsibilities and the iteration protocol that TokenStreamIterator relies upon.

### `src.jinja2.lexer.TokenStreamIterator.__iter__` · *method*

## Summary:
Returns the iterator object itself so the TokenStreamIterator instance conforms to Python's iterator protocol without altering internal state.

## Description:
This method enables TokenStreamIterator to be used directly in Python iteration contexts (for loops, iter(), tuple()/list() constructions, and any consumer that expects an iterator). Typical callers are:
- the built-in iter() call when an iteration context is started,
- for-loops and other language constructs that request an iterator,
- consumer code that explicitly calls iter(token_iterator).

This is implemented as a dedicated method to satisfy the iterator protocol contract (an iterator's __iter__ must return the iterator object). Keeping this logic in its own method keeps iteration initialization separate from token advancement logic implemented in __next__.

## Args:
This is an instance method; no explicit arguments beyond:
    self (TokenStreamIterator): the iterator instance that will be returned.

## Returns:
    TokenStreamIterator: The same instance (self) passed in. No new object is created and no internal state is changed.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
Attributes READ:
    - None (this method does not read any self.<attr> attributes).

Attributes WRITTEN:
    - None (this method does not modify any self.<attr> attributes).

## Constraints:
Preconditions:
    - The TokenStreamIterator instance must be properly constructed (.__init__ executed) so subsequent iteration (via __next__) will operate correctly. This method itself does not validate internal fields.

Postconditions:
    - After the call, the same object is returned and no attributes are modified.
    - The iterator is ready to be used by the caller; it does not reset or rewind any underlying stream.

## Side Effects:
    - None. This method performs no I/O, no external service calls, and makes no mutations to objects outside self.

## Notes and Usage Guidance:
    - Because __iter__ returns self, the TokenStreamIterator is both an iterable and its own iterator. Calling iter(instance) or using the instance in a for-loop yields the same object.
    - Consequence: using the same TokenStreamIterator instance in nested or concurrent iterations will share the single iterator state (tokens already consumed by one consumer will not be available to the other). To restart or have independent passes, obtain a fresh iterator instance.

### `src.jinja2.lexer.TokenStreamIterator.__next__` · *method*

## Summary:
Returns the current token from the underlying token stream and advances the stream to the next token; if the current token is the end-of-file marker, closes the stream and signals iteration end by raising StopIteration.

## Description:
This implements the iterator protocol's next operation for a TokenStreamIterator: it yields the token that is currently available on the associated token stream (self.stream.current), then advances the stream so subsequent calls return subsequent tokens.

Known callers and context:
- Any consumer that uses the iterator protocol (built-in next() or a for-loop) to pull tokens from a TokenStreamIterator.
- Typically invoked by the parser/lexer pipeline during template parsing where tokens are consumed one by one.
- It is intentionally a separate method to encapsulate the iterator semantics (return current, detect EOF, advance the underlying stream, and ensure stream closure on EOF) in a single, well-defined operation rather than duplicating this logic at each call site.

Why this logic is its own method:
- Provides correct and consistent iterator behavior (including proper EOF handling and stream closure) for all callers.
- Keeps EOF detection and advancement behavior centralized so callers do not need to manage stream state and closure themselves.

## Args:
None.

## Returns:
Token
- The token that was the stream's current token at the time of call.
- Possible values: any Token instance provided by the underlying stream implementation.
- Edge case: there is no return when the current token is the end-of-file marker — instead, StopIteration is raised.

## Raises:
StopIteration
- Raised exactly when the current token's type is TOKEN_EOF. In that case the method first calls self.stream.close() and then raises StopIteration.

Potential AttributeError or other exceptions
- If self.stream or self.stream.current does not exist or is improperly implemented, an AttributeError or other exception raised by the underlying objects may propagate. (This reflects precondition requirements rather than explicit checks.)

## State Changes:
Attributes READ:
- self.stream
- self.stream.current (the current token object)
- token.type (the token's type is inspected against TOKEN_EOF)

Attributes WRITTEN / Mutated:
- self.stream.close() is called when the current token is TOKEN_EOF (mutates the stream's internal state; exact effects depend on stream implementation).
- next(self.stream) is invoked on the underlying stream when the current token is not EOF, advancing the stream's internal position to the next token.

## Constraints:
Preconditions:
- self.stream must be a token stream-like object that exposes:
  - a current attribute pointing to the current Token,
  - supports next(self.stream) (i.e., implements the iterator protocol / __next__),
  - provides a close() method callable without arguments.
- The current token object must have a .type attribute comparable to TOKEN_EOF.

Postconditions:
- If the returned token was not an EOF marker:
  - The stream has been advanced to the next token via next(self.stream).
  - The returned value is the token that was current prior to advancing.
- If the current token was an EOF marker:
  - self.stream.close() has been called.
  - StopIteration is raised and no token is returned.

## Side Effects:
- Calls self.stream.close() when EOF is encountered — this may free resources or change stream state depending on the stream implementation.
- Calls next(self.stream) to advance the underlying stream when the current token is not EOF — this mutates the stream's internal cursor/state.
- No I/O is performed directly by this method itself; any I/O side effects depend on the concrete implementation of the underlying stream's close/advance behavior.

## `src.jinja2.lexer.TokenStream` · *class*

## Summary:
Represents a consumable stream of lexer Token objects with push-back, lookahead, and convenient conditional/required consumption helpers. TokenStream adapts a Token-producing iterable into a mutable, parser-friendly stream that preserves error location context (name, filename) and centralizes EOF semantics.

## Description:
TokenStream wraps any iterable or generator that yields Token instances (the lexical output). It is typically constructed by passing the lexer generator to the parser front-end. The stream provides:
- a single visible token (self.current) that callers inspect,
- deterministic advancement rules (pushed tokens returned before generator tokens),
- lookahead via look(),
- push-back via push(),
- conditional and required-consume helpers (next_if, skip_if, expect),
- an iterator adapter via __iter__ returning TokenStreamIterator.

Motivation / responsibility:
- Centralize token consumption semantics (priority of pushed tokens, generator exhaustion handling, EOF sentinel installation) so parser code can consistently test and consume tokens without duplicating logic.
- Provide uniform TemplateSyntaxError messages when expected tokens are missing.

Known callers:
- The template parser and related parsing utilities.
- TokenStreamIterator (returned by __iter__) for Python iteration contexts (for-loops or explicit next()).

## State:
- _iter: Iterator[Token]
    - Type: iterator over Token produced from the supplied generator (iter(generator)).
    - After close(): iter(()) (an empty iterator).
    - Invariants: yields Token instances or raises runtime exceptions; after close no tokens are yielded.

- _pushed: deque[Token]
    - Type: collections.deque
    - Purpose: FIFO push-back buffer. Tokens appended here are returned by future __next__ calls before taking from _iter.
    - Invariant: remains intact across close(); tokens in _pushed will still be returned even after close().

- current: Token
    - Type: Token (lineno:int, type:str, value:str)
    - Meaning: the currently-visible token for consumers.
    - Invariant: always a Token instance. When stream is fully exhausted and no pushed tokens remain, current.type == TOKEN_EOF.

- closed: bool
    - Type: bool
    - Meaning: True once close() is called (either explicitly or because the underlying iterator was exhausted).
    - Invariant: When True, _iter yields no tokens (iter(())), and current.type is TOKEN_EOF (though pushed tokens may still exist).

- name: Optional[str]
    - For error messages (may be None).

- filename: Optional[str]
    - For error messages (may be None).

Class invariants:
- self._pushed is a deque-like object; self.current is a Token.
- Truthiness: bool(stream) is True iff self._pushed is non-empty or self.current.type is not TOKEN_EOF.
- TokenStream methods preserve these invariants; close() sets current to an EOF Token (preserving lineno), sets _iter = iter(()), and sets closed True but does NOT clear _pushed.

## Creation / Priming behavior:
Signature:
    def __init__(self, generator: Iterable[Token], name: Optional[str], filename: Optional[str]) -> None

Behavior:
- Converts generator to iterator and creates an empty deque for _pushed.
- Initializes self.current = Token(1, TOKEN_INITIAL, "") (a synthetic starting token).
- Immediately calls next(self) once to prime the stream so that current is the first token from the generator (or an EOF sentinel if the generator is empty).
- If the generator raises an exception during priming, that exception propagates out of __init__ (i.e., construction can raise runtime exceptions thrown by the generator).

## Public methods (signatures and behavior)
All return types below are precise and reflect what a reimplementation must provide.

- def __iter__(self) -> TokenStreamIterator
    - Returns a new TokenStreamIterator bound to this TokenStream. Does not mutate stream state.
    - Exceptions: none intentionally; malformed stream may cause later attribute errors during iteration.

- def __bool__(self) -> bool
    - Return True if there are tokens immediately available: bool(self._pushed) or self.current.type is not TOKEN_EOF.
    - Non-mutating. No exceptions in normal operation.

- @property def eos(self) -> bool
    - Convenience property returning not bool(self), i.e., True when there are no tokens available (no pushed tokens and current is TOKEN_EOF).
    - Non-mutating.

- def push(self, token: Token) -> None
    - Append token to the right of self._pushed so it will be returned by subsequent __next__ calls before any tokens from _iter.
    - No type-checking is performed; the method will raise AttributeError/TypeError if _pushed is missing or not deque-like (indicating an invalid stream).

- def look(self) -> Token
    - Peek the token immediately after the current token and return it without permanently advancing the visible current token.
    - Implementation semantics:
        1. old_token = next(self)   # advances, returning previous current
        2. result = self.current    # now the token that followed previous current
        3. self.push(result)        # ensure result will be returned later
        4. self.current = old_token # restore visible current
        5. return result
    - Effect: result is appended to _pushed and will be returned in sequence later.
    - Exceptions: propagates exceptions from next(self) or generator.

- def skip(self, n: int = 1) -> None
    - Call next(self) n times (no-op if n <= 0).
    - Advances the stream by up to n tokens; will not raise StopIteration (underlying StopIteration is converted to EOF via close()).
    - Exceptions: runtime errors from underlying generator propagate.

- def next_if(self, expr: str) -> Optional[Token]
    - If self.current.test(expr) is True: return next(self) (consumes and returns the current token).
    - Otherwise: return None and leave the stream unchanged.
    - Return type: Optional[Token].
    - Exceptions: Token.test may raise (TypeError if expr not a str); next(self) can propagate runtime exceptions from the generator.

- def skip_if(self, expr: str) -> bool
    - Return True if next_if(expr) returned a Token (i.e., a token matched and was consumed), otherwise False.
    - Equivalent to: return self.next_if(expr) is not None
    - Exceptions: same as next_if.

- def __next__(self) -> Token
    - Return the token that was current at call start (rv) and advance the stream's current token to the next available one, according to this priority:
        1. If self._pushed is non-empty:
            - self.current = self._pushed.popleft()
        2. Else if rv.type is not TOKEN_EOF:
            - Attempt self.current = next(self._iter)
              - If next(self._iter) raises StopIteration: call self.close() to install EOF sentinel.
        3. Else (rv.type is TOKEN_EOF and no pushed tokens): current remains the EOF token.
      Finally return rv (the token that was current at call start).
    - Important edge behavior after close():
        - close() sets current to an EOF token but leaves _pushed intact.
        - If _pushed contains tokens after close(), bool(stream) may still be True even though current.type is TOKEN_EOF.
        - The first __next__() call after close() returns the EOF token (rv will be that EOF token); subsequent __next__() calls will pop tokens from _pushed and set them as current as usual.
    - Exceptions:
        - Does not raise StopIteration for generator exhaustion; StopIteration from _iter is caught and converted via close().
        - Runtime exceptions raised by the underlying generator during next(self._iter) propagate.

- def close(self) -> None
    - Replace self.current with Token(self.current.lineno, TOKEN_EOF, ""), set self._iter = iter(()), and set self.closed = True.
    - Does NOT clear or mutate _pushed (pushed tokens remain queued).
    - Exceptions: AttributeError if current has no lineno (indicates broken invariants); otherwise none.

- def expect(self, expr: str) -> Token
    - If self.current.test(expr) is True:
        - return next(self) (consume and return the matched token).
    - Else:
        - expr = describe_token_expr(expr)
        - If self.current.type is TOKEN_EOF:
            * raise TemplateSyntaxError(f"unexpected end of template, expected {expr!r}.", self.current.lineno, self.name, self.filename)
        - Else:
            * raise TemplateSyntaxError(f"expected token {expr!r}, got {describe_token(self.current)!r}", self.current.lineno, self.name, self.filename)
    - Exceptions:
        - TemplateSyntaxError on mismatch as described above.
        - Any exception raised by Token.test, describe_token_expr, or describe_token will propagate.

## Pseudocode for __next__ (precise, to aid reimplementation)
    def __next__(self) -> Token:
        rv = self.current
        if self._pushed:
            self.current = self._pushed.popleft()
        elif self.current.type is not TOKEN_EOF:
            try:
                self.current = next(self._iter)
            except StopIteration:
                self.close()
        return rv

Notes: ensure identity comparisons use "is" with TOKEN_EOF only if TOKEN_EOF is a singleton constant object; the original uses "is" for TOKEN_EOF and TOKEN_INITIAL. If your reimplementation represents token types as strings, use equality comparisons instead.

## Raises (summary by method)
- __init__: propagates runtime exceptions raised by the generator during initial priming.
- __next__/look/skip/skip_if/next_if: may propagate runtime exceptions from the underlying generator or Token.test; StopIteration from the generator is handled internally and converted to an EOF sentinel (not re-raised).
- expect: raises TemplateSyntaxError for mismatches (two specific messages for EOF vs non-EOF), and propagates other helper exceptions (Token.test, describe_token, describe_token_expr).
- push/close/__iter__/__bool__/eos: generally do not raise in normal operation; AttributeError may occur if invariants are broken.

## Lifecycle usage examples
1) Construction and first-token priming:
    token_stream = TokenStream(token_generator, name="tpl", filename="tpl.html")
    # after construction token_stream.current is the first token or an EOF token if generator empty

2) Conditional consumption:
    if token_stream.next_if("name:for"):
        # consumed the 'for' name token
    else:
        # stream unchanged

3) Required token:
    token = token_stream.expect("block_begin")  # raises TemplateSyntaxError if mismatch

4) Lookahead without consuming:
    next_token = token_stream.look()
    # next_token is appended to _pushed and will be returned in-order later; visible current is unchanged

5) Push-back manual token:
    token_stream.push(token_to_reinsert)

6) Iteration:
    for tk in token_stream:  # uses TokenStreamIterator
        process(tk)
    # The iterator will call stream.close() and raise StopIteration when it encounters current.type == TOKEN_EOF.

7) EOF + pushed tokens edge-case (explicit demonstration):
    - After calling close(), the stream sets current to an EOF token but leaves _pushed intact.
    - Example sequence:
        close()  # current now EOF, _pushed may contain tokens
        next(stream)  -> returns EOF token (rv == EOF token installed by close())
        next(stream)  -> if _pushed had items, returns the first pushed token (popleft) as rv and sets current to the next pushed or iter token.

## Implementation notes and pitfalls
- Always perform Token.test(expr) checks before advancing the stream (expect/next_if rely on this).
- Do not clear _pushed on close(); tests rely on pushed tokens being returned after an EOF sentinel is installed.
- The code in the original uses "is" to compare token types to TOKEN_EOF and TOKEN_INITIAL; when reimplementing with string constants, prefer equality (==) unless your token type constants are canonical singletons.
- The constructor primes the first token by calling next(self) once; if you omit priming, client code that expects current to reflect the first token will break.
- Keep TemplateSyntaxError messages exact if you need compatibility with tests or external consumers that assert the exact error text.

## Quick reference: public method signatures
    __init__(self, generator: Iterable[Token], name: Optional[str], filename: Optional[str]) -> None
    __iter__(self) -> TokenStreamIterator
    __bool__(self) -> bool
    @property eos(self) -> bool
    push(self, token: Token) -> None
    look(self) -> Token
    skip(self, n: int = 1) -> None
    next_if(self, expr: str) -> Optional[Token]
    skip_if(self, expr: str) -> bool
    __next__(self) -> Token
    close(self) -> None
    expect(self, expr: str) -> Token

### `src.jinja2.lexer.TokenStream.__init__` · *method*

## Summary:
Initializes a TokenStream by wrapping an iterable of Token objects, creating the internal pushback buffer and metadata, and priming the stream so self.current holds the first available token (or an EOF token if the generator is empty).

## Description:
This constructor is called when a token stream is created as the input to the parser stage of the template compilation pipeline. Typical callers are the lexer or higher-level parsing entrypoints that convert raw template text into a sequence of Token objects and then construct a TokenStream to feed the parser.

The initializer performs two distinct responsibilities that justify it being a dedicated method:
1. Setup of the stream's runtime scaffolding (an iterator over the provided generator, a deque for pushed-back tokens, and metadata fields).
2. Priming the stream by advancing once so that self.current already refers to the first meaningful token (or EOF)—this simplifies subsequent consumer code which always reads from self.current and uses next(self) to advance.

By performing the initial advance inside __init__, consumers do not need to remember to prime the stream before using its look/expect/next semantics.

## Args:
    generator (t.Iterable[Token]):
        An iterable (often a generator) that yields Token instances in lexical order.
        - Required.
        - The initializer will call iter(generator) and immediately advance it once.
        - If generator is not actually iterable, iter(generator) will raise TypeError.
    name (t.Optional[str]):
        Optional logical name for the template or stream; used in error messages.
        - May be None.
    filename (t.Optional[str]):
        Optional filename for the template; used in error messages and diagnostics.
        - May be None.

## Returns:
    None
    - The constructor does not return a value; it sets up instance state. After return, self.current will hold the first token from the generator, or an EOF token if the generator was already exhausted.

## Raises:
    TypeError:
        - If the provided generator is not iterable (raised by iter(generator)).
    Any exception raised by the generator when it is advanced:
        - The initializer calls next(self._iter) (via next(self)), so any exception (other than StopIteration) raised by the generator's iteration logic will propagate out of __init__.
    No explicit TemplateSyntaxError or other custom exceptions are raised by this method itself.

## State Changes:
Attributes READ:
    - self._pushed (read indirectly by __next__ when priming)
    - self.current (read by __next__ during priming)
    - self._iter (read by __next__ when pulling the first token)
    - TOKEN_EOF / TOKEN_INITIAL (module-level token type sentinels are compared in __next__/close)

Attributes WRITTEN:
    - self._iter: set to iter(generator) initially; may be replaced with iter(()) by close() if the generator is exhausted during priming.
    - self._pushed: set to a new deque() (empty pushback buffer).
    - self.name: set to the provided name.
    - self.filename: set to the provided filename.
    - self.closed: set to False initially; may be set to True by close() if the generator is exhausted while priming.
    - self.current: set first to an initial Token(1, TOKEN_INITIAL, "") and then updated by the priming call to the first real token or to an EOF token.

## Constraints:
Preconditions:
    - generator must be an iterable yielding Token objects; the method does not validate element types.
    - name and filename should be strings or None; no runtime validation is performed.

Postconditions (guarantees after __init__ completes without raising):
    - self._iter is an iterator wrapping the provided generator (or an empty iterator if the generator was exhausted while priming).
    - self._pushed is an empty deque ready for push/pop operations.
    - self.name and self.filename are set to the supplied values (which may be None).
    - self.current is the first Token yielded by the provided generator.
        - If the generator yielded no tokens, self.current is an EOF token (Token(lineno, TOKEN_EOF, "")) and self.closed is True.
        - Otherwise self.closed remains False (unless the first yielded token logic itself caused closure).
    - The stream is already primed: consumers may inspect self.current immediately and use next(self) to advance.

## Side Effects:
    - The initializer consumes (advances) the provided generator once. If the generator produces items via side effects, those side effects will occur during construction.
    - The first token is pulled from the generator during construction; this may run arbitrary user code inside the generator (and those exceptions will propagate).
    - If the generator is exhausted on the first advance, the stream is closed (self.closed becomes True) and the iterator is replaced with an empty iterator.

### `src.jinja2.lexer.TokenStream.__iter__` · *method*

## Summary:
Return a new TokenStreamIterator that adapts this TokenStream to Python's iterator protocol. The call itself does not change the TokenStream's attributes.

## Description:
- Known callers and context:
    - Consumers that iterate over tokens (parser or other token-consuming code) obtain an iterator by calling this method when they begin token consumption.
    - Typical usage: starting a for-loop or calling iter() / next() on a TokenStream instance; the returned iterator implements the iteration lifecycle (yield current token, advance, close at EOF).
- Why this is a separate method:
    - Encapsulates the iterator-adapter construction in one place so iteration semantics are centralized and callers do not need to implement the yield/advance/EOF handling themselves.
    - Keeps TokenStream focused on token production, buffering, and direct token-manipulation helpers (push, look, skip), while TokenStreamIterator provides the protocol adapter.

## Args:
    None.

## Returns:
    TokenStreamIterator
    - A freshly constructed TokenStreamIterator bound to this TokenStream (equivalent to calling TokenStreamIterator(self)).
    - The iterator will, when advanced, read this stream's current Token and advance the underlying stream; iteration ends when a token with type TOKEN_EOF is encountered (the iterator calls the stream's close() before raising StopIteration).
    - Edge-case behavior: if the stream is already at EOF when the iterator is first advanced, the iterator will call stream.close() and raise StopIteration on the first next() invocation.

## Raises:
    - This method does not intentionally raise exceptions.
    - If the TokenStreamIterator constructor or later iteration operations detect that the provided stream is malformed (missing required attributes or methods such as current, __next__, or close), attribute access or calls will raise AttributeError/TypeError. These exceptions indicate a precondition violation (invalid TokenStream) rather than a behavior specific to this method.

## State Changes:
- Attributes READ:
    - None directly by this method. It does not access or mutate self.current, self._pushed, or other attributes; it only passes self to the iterator constructor.
- Attributes WRITTEN:
    - None.

## Constraints:
- Preconditions:
    - The TokenStream instance (self) should be a valid, initialized stream that exposes:
        - current: a Token-like object (used by the iterator when iteration begins),
        - __next__ (so next(self) can advance the stream),
        - close() (so the iterator can close the stream when EOF is reached).
    - In practice, TokenStream.__init__ primes self.current (so callers should normally iterate after construction). If these attributes are missing or in an unexpected state, iteration will fail when the returned iterator is used.
- Postconditions:
    - A TokenStreamIterator object bound to this TokenStream is returned.
    - No attributes on self are modified by this call; subsequent iteration using the returned iterator will mutate self as tokens are consumed.

## Side Effects:
    - This method performs no I/O and does not call external services.
    - There are no mutations of external objects performed by this method itself.
    - Note: using the returned iterator will mutate this TokenStream (advance current, potentially call close()), so callers should be aware that iteration has side effects on the TokenStream instance.

## Usage notes and caveats:
    - Example usage (conceptual):
        - for token in token_stream:
              process(token)
      The for-loop calls token_stream.__iter__() and iterates via the returned TokenStreamIterator.
    - Multiple iterators created from the same TokenStream share the same underlying stream state; advancing one iterator advances the underlying TokenStream and affects all iterators bound to it. Do not assume independent cursors.

### `src.jinja2.lexer.TokenStream.__bool__` · *method*

## Summary:
Return whether the token stream currently has any tokens remaining (either queued/pushed tokens or a non‑EOF current token) without advancing or mutating the stream.

## Description:
Known callers and usage contexts:
- TokenStream.eos property (defined as not self) — uses this boolean test to determine end-of-stream.
- Parser loops or other consumer code that test the TokenStream object in boolean contexts (e.g., while stream: ...) to decide whether more tokens are available.
- Any client code that needs a quick, non-destructive check of whether the stream has been exhausted.

Why this is a separate method:
- Encapsulates the truthiness logic for the stream in one place so consumers can rely on Python truth-testing semantics (bool(stream)) rather than inspecting internal fields. Keeping this as a dedicated method avoids duplicating the EOF/pushed-token check in multiple places and makes the eos property (and any other boolean checks) concise and intention-revealing.

## Args:
- None

## Returns:
- bool
    - True if at least one token is available to be consumed:
        * there are one or more tokens in the internal push-back buffer (self._pushed is non-empty), or
        * the current token's type is not TOKEN_EOF.
    - False only when both:
        * self._pushed is empty (no queued tokens), and
        * self.current.type is TOKEN_EOF (the current token is the EOF sentinel).
    - Notes:
        * The check is non-destructive: it does not advance the iterator or remove tokens from any buffer.

## Raises:
- None. The implementation performs only attribute reads and boolean tests. It assumes self._pushed and self.current exist and have the expected attributes (see Preconditions). If those invariants are violated by external mutation, Python may raise AttributeError or other runtime errors — such errors are not raised by this method itself in normal use.

## State Changes:
- Attributes READ:
    - self._pushed (inspect emptiness via bool(self._pushed))
    - self.current and specifically self.current.type
- Attributes WRITTEN:
    - None — this method does not modify any attributes on self or external objects.

## Constraints:
- Preconditions:
    - self._pushed must be a deque-like container that supports truth-testing (bool(self._pushed)).
    - self.current must be a Token-like object with a .type attribute (the code initializes current to a Token in __init__).
    - TOKEN_EOF is the sentinel token type used to mark the end of the stream; the method expects equality comparison with self.current.type to be valid.
- Postconditions:
    - No changes to self or its contained tokens occur as a result of calling this method.
    - The returned boolean correctly reflects the immediate availability of tokens per the rules in Returns.

## Side Effects:
- None. The method performs only read-only checks and causes no I/O, no iteration advancement, and no mutation of self or external objects.

### `src.jinja2.lexer.TokenStream.eos` · *method*

## Summary:
Return True when the token stream is at end-of-stream (no tokens available) without advancing or mutating the stream.

## Description:
- Known callers and contexts:
    - Parser code and other token consumers that need to detect the end of the token sequence (for example, loop conditions in a parser: while not stream.eos: ...).
    - Any consumer that wants a named, intention-revealing check for stream exhaustion instead of using Python truth-testing directly.
    - Unit tests that assert the stream has been fully consumed after parsing.
- Lifecycle stage:
    - Called during parsing or any token-consumption phase after tokenization/lexing when the consumer needs to know whether more tokens remain.
- Rationale for being a separate property:
    - Encapsulates the "end-of-stream" query behind a readable API (stream.eos) rather than repeating the negated truthiness check (not stream) everywhere.
    - Provides a stable, intention-revealing accessor that delegates to the stream's truthiness logic so callers do not need to inspect internal fields.
    - Keeps token-consumer code clearer and less coupled to TokenStream internals.

## Args:
- None.

## Returns:
- bool
    - True when the token stream is exhausted (no queued/pushed tokens and the current token is the EOF sentinel).
    - False when at least one token is immediately available for consumption (either there are pushed tokens or the current token is not the EOF sentinel).
    - Edge cases:
        - If the TokenStream object has been externally mutated in a way that breaks its invariants (missing attributes or unexpected types), evaluation may raise a runtime exception instead of returning a boolean.

## Raises:
- None intentionally.
- Possible implicit exceptions (precondition violations):
    - AttributeError or TypeError if self does not expose the attributes or methods expected by the truthiness logic (for example, missing self._pushed or self.current, or current lacking a .type attribute). These are not raised by eos itself in normal operation but can occur if the TokenStream instance is in an invalid state.

## State Changes:
- Attributes READ:
    - self._pushed (checked for truthiness via the TokenStream.__bool__ implementation)
    - self.current and specifically self.current.type (to determine whether the current token is TOKEN_EOF)
- Attributes WRITTEN:
    - None. This property performs only read-only checks and does not modify self or any external objects.

## Constraints:
- Preconditions:
    - self must be a properly-initialized TokenStream instance:
        - self._pushed must be a deque-like container (truth-testing supported).
        - self.current must be a Token-like object with a .type attribute.
        - TOKEN_EOF is the sentinel token type used to denote the end of the stream; comparisons against self.current.type must be valid.
    - The TokenStream.__bool__ implementation is relied upon; eos is defined as the negation of the stream's truthiness.
- Postconditions:
    - No mutation of the TokenStream occurs as a result of calling this property.
    - The return value accurately reflects immediate token availability according to the TokenStream.__bool__ semantics.

## Side Effects:
- None. No I/O, no iterator advancement, and no mutations of self or external state are performed.

### `src.jinja2.lexer.TokenStream.push` · *method*

## Summary:
Appends the given token to the stream's internal pushed-token queue so it will be returned by subsequent iteration before tokens from the underlying generator.

## Description:
Known callers and context:
- TokenStream.look: uses push to put a previously-current token back onto the pushed queue after advancing the stream so that the token will be returned again in sequence.
- Iteration protocol (__next__): although not a direct caller, __next__ reads the pushed queue and will return tokens pushed by this method before pulling new tokens from the underlying generator.

Why this is a separate method:
- Encapsulates the enqueue/pushback semantic for tokens in one place for clarity and future extension (e.g., validation or logging) without duplicating deque manipulation logic across the class or external callers.

## Args:
    token (Token): The token object to enqueue for future retrieval. The implementation expects the same Token objects the stream yields (objects with attributes like type and lineno and methods such as test), but the method performs no type-checking and will append any value given.

## Returns:
    None

## Raises:
    No explicit exceptions are raised by this method. Errors will only occur if the underlying deque is missing or in an unexpected state (for example, if self._pushed is not initialized or does not support append), which would raise the underlying exception (AttributeError or TypeError).

## State Changes:
Attributes READ:
    self._pushed

Attributes WRITTEN:
    self._pushed (mutated via deque.append(token))

## Constraints:
Preconditions:
    - The TokenStream instance must be initialized so that self._pushed exists and is a deque (the class constructor sets this).
    - The caller should pass a Token (or token-like) object consistent with the rest of the stream; the method itself does not validate the token.

Postconditions:
    - The provided token is placed at the right (end) of the internal pushed-token deque.
    - Subsequent calls to TokenStream.__next__ will return items from self._pushed (left-to-right via popleft) before pulling new tokens from the underlying iterator; thus the pushed token will be returned in FIFO order relative to other pushed tokens.

## Side Effects:
    - Mutates the internal deque self._pushed.
    - No I/O, no external service calls, and no modifications to objects outside self other than the token being referenced by the deque (i.e., the token object is stored but not modified).

### `src.jinja2.lexer.TokenStream.look` · *method*

## Summary:
Peek the token immediately after the current token and return it without permanently advancing the stream; the current token is left as it was and the peeked token is appended to the internal push-back queue so subsequent iteration produces the same sequence.

## Description:
- Known callers and context:
    - Parser or other consumers that need one-token lookahead while deciding how to parse a construct. This method is invoked during the parsing stage after tokenization, whenever the consumer must inspect the next token without consuming the current one.
- Why this is a separate method:
    - Encapsulates the "peek without consuming" pattern and the correct interplay with the TokenStream's internal iterator and push-back queue.
    - Keeps the logic centralized so callers do not need to manipulate the pushed queue or restore the stream state manually, preventing subtle bugs in iterator/push semantics.

## Args:
    None

## Returns:
    Token
    - The Token instance that immediately follows the current token at the time of the call.
    - If the stream is at or past end-of-input, a Token whose type is the EOF token (the same token that the stream would return for end-of-stream) is returned.
    - The returned Token is also appended to the TokenStream's internal pushed deque; it is the exact object that will be yielded later when the stream advances.

## Raises:
    - The method itself does not explicitly raise exceptions.
    - It may propagate exceptions raised by the underlying token generator when advancing (i.e., calls performed by next(self) / the internal iterator). Those exceptions are not raised by look() itself but come from the generator code.

## State Changes:
- Attributes READ:
    - self.current (reads the currently-visible token to compute/restore state)
    - indirectly reads the internal iterator state through calling next(self)
- Attributes WRITTEN:
    - self._pushed (appends the peeked token via push(result))
    - self.current (temporarily changed by next(self) and then restored to its original value by assignment)
    - indirectly may modify self._iter and self.closed if advancing triggers the stream to close (via TokenStream.__next__/close)

## Constraints:
- Preconditions:
    - The TokenStream must be initialized (self.current holds a Token and the stream internal iterator exists).
    - There is no requirement that the stream not be at EOF; look() supports peeking at EOF.
- Postconditions:
    - After the call, self.current has the same value it had before the call (no net change to the visible current token).
    - The returned Token equals the token that would be seen immediately after the current token (i.e., the next token in sequence).
    - The returned Token is appended to self._pushed, preserving the original iteration sequence; subsequent calls to __next__ will yield the same sequence of tokens as if look had not been called (except that the internal pushed deque will contain the peeked tokens).
    - If the underlying iterator was exhausted while obtaining the peeked token, the stream may be closed (self.closed set True) and the returned token may be an EOF token; this is handled by the stream's normal close semantics.

## Side Effects:
    - Mutates the internal push-back deque (self._pushed) by appending the peeked token.
    - Temporarily advances the stream via next(self) which may cause the underlying token generator to be advanced and may trigger stream closure (side effects from the generator itself may occur and propagate).
    - No I/O or external service calls are performed by look() itself.

### `src.jinja2.lexer.TokenStream.skip` · *method*

## Summary:
Advances the token stream by consuming n tokens, mutating the stream's current token and internal buffers accordingly.

## Description:
Calls next(self) n times to consume tokens from the stream. Each call to next(self) returns the token that was current at call start and advances the stream's current token according to the TokenStream semantics (prefer a pushed token, otherwise take the next token from the underlying iterator, and on exhaustion install an EOF token).

Known callers and context:
- No direct external call sites were discovered during repository analysis for this specific method. Typical callers are parser or token-processing routines that need to skip over tokens (for example, to ignore separators or optional tokens).
- Within this class, related helper methods that perform token consumption and are commonly used alongside skip are:
  - next_if(expr) / skip_if(expr): conditional consumption when the current token matches an expression.
  - expect(expr): validates the current token and then consumes it by calling next(self).
- This logic is factored into its own method to provide a concise, reusable way to perform repeated token advancement without duplicating the loop-and-advance pattern at each call site.

## Args:
    n (int): Number of tokens to consume. Defaults to 1.
        - Allowed values: any integer. If n <= 0 the method performs zero iterations (no-op).
        - Typical usage: n >= 0. Very large n is allowed but will exhaust the underlying iterator and leave the stream at EOF if there are fewer than n remaining tokens.

## Returns:
    None

## Raises:
    None directly.
    - Behavior note: next(self) (i.e., TokenStream.__next__) handles StopIteration from the underlying iterator internally by calling close() and installing an EOF token; therefore skip will not raise StopIteration even if n exceeds remaining tokens.

## State Changes:
Attributes READ:
    - self.current (inspected by next(self) and used implicitly as the returned previous token)
    - self._pushed (checked for presence by next(self))
    - self._iter (advanced by next(self) when appropriate)

Attributes WRITTEN:
    - self.current (updated on each advancement to the next token, or to an EOF token if the iterator is exhausted)
    - self._pushed (mutated if next(self) consumes a token from the left of the deque)
    - self._iter (may be replaced with an empty iterator via close())
    - self.closed (may be set to True via close())

## Constraints:
Preconditions:
    - The TokenStream instance must be initialized (self._iter is an iterator of Token, self._pushed is a deque, and self.current is a Token). Calling skip on a closed stream is allowed; it will repeatedly observe the EOF token.
    - n must be an integer (type hinted as int). Non-integer types will raise a TypeError before method logic (caller responsibility).

Postconditions:
    - The token stream has advanced by up to n tokens. For each consumed token, the stream's current token is updated according to TokenStream.__next__ rules:
        1. If self._pushed is non-empty, current becomes self._pushed.popleft().
        2. Else if the previous current token was not TOKEN_EOF, the stream attempts to set current to next(self._iter); if the iterator is exhausted, close() is invoked and current becomes a TOKEN_EOF token.
        3. Else (current is already TOKEN_EOF and no pushed tokens) current remains TOKEN_EOF.
    - The method returns None.

## Side Effects:
    - No external I/O, logging, or network calls.
    - Mutates internal stream state (see Attributes WRITTEN). If the underlying iterator is exhausted while skipping, the stream will be closed (self.current set to an EOF token, self._iter replaced with an empty iterator, and self.closed set to True).

### `src.jinja2.lexer.TokenStream.next_if` · *method*

## Summary:
Conditionally consume and return the current token if it matches the given match expression; otherwise leave the stream unchanged and return None. This call advances the stream only when the current token matches.

## Description:
Known callers and contexts:
- TokenStream.skip_if: uses next_if to attempt a conditional skip and converts the result to a boolean.
- Parser and lexer consumer code: used during parsing/token-consumption phases when the caller wants to consume a token only if it matches a specific type or type:value expression (e.g., optional punctuation or optional keywords).
- TokenStream consumers that implement lookahead/conditional parsing decisions.

Lifecycle stage:
- Invoked during token consumption in the parsing phase right after tokenization; it participates in the parser's token-matching/consumption pipeline where optional tokens are accepted only when present.

Why this is a separate method:
- Encapsulates the common pattern "if current token matches X then consume it" so callers do not duplicate the test + advance logic.
- Ensures consistent semantics for conditional consumption (no state change when the condition does not hold) and leverages the central __next__ advancement behavior.

## Args:
    expr (str): A match expression. Two allowed forms:
        - A plain token type string (e.g., "name")
        - A compound "type:value" string (e.g., "name:foo") which will match only when both type and value match.
    No default. Must be provided and should be a str.

## Returns:
    Optional[Token]:
        - When the current token matches expr (Token.test(expr) returns True): returns the token that was current at call start. As a side effect the stream is advanced by one token (see State Changes).
        - When the current token does not match expr: returns None and the stream state is unchanged.
    Edge cases:
        - If the current token is an EOF token and expr matches that EOF token, the EOF Token instance is returned. In that case the stream remains at EOF (further calls will continue to return the EOF token).
        - The returned Token is the same Token instance that was current before advancing (i.e., the token that satisfied the match).

## Raises:
    TypeError:
        - If expr is not a str (for example None or another non-string object), Token.test(expr) will likely raise a TypeError during the membership (":" in expr) or split operations. This method does not catch that; callers should pass a str.
    Note: next(self) (TokenStream.__next__) does not propagate StopIteration; it converts iterator exhaustion into an internal EOF token.

## State Changes:
Attributes READ:
    - self.current — inspected to perform the match via self.current.test(expr).

Attributes WRITTEN / Mutated:
    - self.current — when a match occurs, next(self) is invoked which returns the prior current token and advances self.current to the next token (from pushed tokens, the underlying iterator, or to an installed EOF token).
    - self._pushed — may be mutated by next(self) (a popleft() occurs if there are pushed tokens).
    - self._iter — may be replaced with an empty iterator by next(self).close() if the underlying iterator is exhausted.
    - self.closed — may be set True by next(self).close() if the iterator is exhausted.
    If no match occurs, no attributes are modified.

## Constraints:
Preconditions:
    - self must be a properly initialized TokenStream (self.current is a Token, self._pushed is a deque, self._iter is an iterator).
    - expr should be a str. Passing a non-str risks runtime TypeError raised by Token.test.

Postconditions:
    - If the method returns a Token: that token is the token that was current at call start and the stream has advanced one token according to TokenStream.__next__ semantics (pushed tokens prioritized, otherwise underlying iterator, otherwise EOF installed).
    - If the method returns None: the stream is unchanged (self.current remains the same, no deque or iterator mutation).

## Side Effects:
    - No external I/O or network activity.
    - Mutates internal stream state only when a match occurs (advances current, may mutate _pushed, may set closed and replace _iter if underlying iterator ends).
    - No mutation of objects outside self beyond deque operations on self._pushed and assignments on self._iter and self.current.

### `src.jinja2.lexer.TokenStream.skip_if` · *method*

## Summary:
Checks whether the current token matches the given expression and, if so, consumes it returning True; otherwise returns False and leaves the stream state unchanged. If the current token is EOF and matches, the method returns True but the stream remains at EOF (no advancement).

## Description:
This is a thin boolean wrapper around the token-consumption helper next_if. It is used by parser/grammar code during the parsing stage when an optional token should be consumed if present (for example optional punctuation, delimiters, or optional keywords). Typical callers are parser routines and helper functions that implement grammar rules and need a simple boolean indicating whether the optional token was present and consumed.

Why this method exists separately:
- It provides a simple True/False API for the common pattern "if current token matches X then consume it", avoiding repetitive code that checks for None returned by next_if.
- Keeps calling sites concise and expresses intent (optional consumption) clearly.

## Args:
    expr (str): A match expression in the same format accepted by Token.test:
        - A plain token type (e.g., "name")
        - A compound "type:value" string (e.g., "name:foo")
    No default value. Passing a non-string will typically raise a TypeError from Token.test.

## Returns:
    bool:
        - True if the current token matched expr and next_if consumed it (or returned the matching token).
        - False if the current token did not match expr and no consumption occurred.
    Edge cases:
        - If the current token is the EOF token and matches expr, the method returns True but the stream does not advance (self.current remains the EOF token). This is because advancing from EOF does not change the stream state in the underlying TokenStream.__next__ implementation.

## Raises:
    TypeError:
        - If expr is not a str (this will surface from Token.test operations like ":" in expr or expr.split).
    Propagated exceptions:
        - Any exception raised by next_if, next(self), or the underlying token generator (for example runtime errors from the generator) is propagated unchanged; this method does not catch or wrap these exceptions.

## State Changes:
Attributes READ:
    self.current — inspected by Token.test (via next_if) to determine if it matches expr.

Attributes WRITTEN (only when a match occurs and next(self) advances):
    self.current — when a non-EOF token is consumed, self.current is updated to the next token (from the pushed deque or the underlying iterator). If the underlying iterator is exhausted while advancing, close() will set self.current to an EOF token and set self.closed to True.
    self._pushed — may be mutated (popleft) by __next__ if previously pushed tokens are consumed.
    self._iter — may be consumed; when exhausted it may be replaced by an empty iterator by close().
    self.closed — may be set to True by close() if the iterator is exhausted during advancement.

Important note about EOF:
    - If the current token at call time is an EOF token and it matches expr, next(self) will return that EOF token but will not advance self.current or change self.closed. Therefore skip_if can return True without changing the stream state in that special case.

## Constraints:
Preconditions:
    - self must be a properly-initialized TokenStream (attributes current, _pushed, _iter exist).
    - expr should be a str in an accepted form; non-str values will cause TypeError.

Postconditions:
    - If the method returns True and the matched token was not EOF: self.current now refers to the token that followed the consumed token; if the underlying iterator was exhausted during this operation, self.current will be an EOF token and self.closed will be True.
    - If the method returns True and the matched token was EOF: self.current remains the EOF token and other stream state is unchanged.
    - If the method returns False: no attribute of the stream is changed.

## Side Effects:
    - Mutates only in-memory TokenStream state when a non-EOF token is consumed (see Attributes WRITTEN). No I/O, logging, or external side effects occur.

### `src.jinja2.lexer.TokenStream.__next__` · *method*

## Summary:
Returns the token that is currently held and advances the stream's current token to the next available token (from the pushed deque, the underlying iterator, or to a sentinel EOF token). This mutates the stream's state by consuming one token from its input sources.

## Description:
This method implements one step of advancing a TokenStream. It is invoked whenever a consumer wants to read the next token while preserving the token ordering semantics of pushed tokens (tokens explicitly re-inserted into the stream), the underlying generator, and EOF handling.

Known callers and contexts:
- TokenStream.__init__: calls next(self) once to initialize the stream's first current token.
- TokenStream.look: calls next(self) to peek forward, then restores state by pushing back the looked token.
- TokenStream.skip: repeatedly calls next(self) to advance by n tokens.
- TokenStream.next_if / skip_if: call next(self) when the current token matches an expression.
- TokenStream.expect: calls next(self) after validating the current token.
- Any external consumer that iterates over the TokenStream via the iterator wrapper (TokenStreamIterator) will cause this method to be invoked as part of iteration.

Why this logic is a dedicated method:
- It centralizes the token-advancement semantics (preference for pushed tokens, falling back to the iterator, and consistent EOF production) in one place so all call sites get identical behavior. Putting this logic inline in many callers would duplicate error-prone state transitions and EOF handling.

## Args:
    None

## Returns:
    Token
        The token that was current at the time of the call (the "previous" token). After the call:
        - If a pushed token existed, the stream's current token becomes the dequeued pushed token.
        - Else if the previous current token was not an EOF token, the stream attempts to obtain the next token from the underlying iterator and sets that as current.
        - If the underlying iterator raises StopIteration, the stream is closed and a TOKEN_EOF token is installed as the current token.
        - If the previous current token was already an EOF token and no pushed tokens exist, the current token remains the EOF token and repeated calls return that EOF token.

## Raises:
    None directly.
    - Note: next(self._iter) may raise StopIteration, but this method catches it and converts it to a call to close(), so the caller does not see a StopIteration from this method.

## State Changes:
Attributes READ:
    - self.current (inspected and used as the value returned and to decide whether the iterator should be advanced; its .type and .lineno may be used)
    - self._pushed (truthiness checked)
    - self._iter (used via next(self._iter) when appropriate)

Attributes WRITTEN:
    - self.current (set to the dequeued pushed token, the next token from the iterator, or — via close() — an EOF token)
    - self._iter (may be replaced by close() with an empty iterator)
    - self.closed (may be set to True by close())

Note: When a token is consumed from the pushed deque, the deque is mutated (popleft).

## Constraints:
Preconditions:
    - self should be a properly initialized TokenStream: self._iter must be an iterator that yields Token objects, self._pushed must be a deque, and self.current must be a Token instance.
    - There is no requirement that the stream is not closed; calling the method on a closed stream is allowed and will return the EOF token repeatedly.

Postconditions:
    - The returned value is the token that was current at call start.
    - The stream's current token will be advanced according to the priority:
        1. If self._pushed is non-empty: current <- self._pushed.popleft()
        2. Else if current.type is not TOKEN_EOF: attempt current <- next(self._iter); if StopIteration occurs then close() is called and current becomes an EOF token.
        3. Else (current.type is TOKEN_EOF and no pushed tokens): current remains the EOF token.
    - If the underlying iterator is exhausted, the stream will be closed (self.current set to an EOF token, self._iter set to an empty iterator, and self.closed set True).

## Side Effects:
    - No external I/O, logging, or network calls.
    - Mutates the internal deque self._pushed by popping its leftmost element when present.
    - May replace self._iter with an empty iterator and set self.closed to True via close().
    - Mutates self.current to the new current token.

### `src.jinja2.lexer.TokenStream.close` · *method*

## Summary:
Set the stream into a final end-of-file state by replacing the current token with an EOF token (preserving its line number), replacing the underlying iterator with an empty iterator, and marking the stream as closed.

## Description:
- Known caller:
    - TokenStream.__next__ — invoked when the underlying token iterator raises StopIteration; __next__ calls close() to finalize the stream.
- Lifecycle / context:
    - Used when the token generator is exhausted to ensure consumers observe a consistent end-of-stream token and a drained iterator. This method centralizes finalization so EOF semantics are uniform across the TokenStream lifecycle.
- Why this is a separate method:
    - The method encapsulates three related state transitions (set EOF current token, replace iterator with an empty iterator, set closed flag). Centralizing these avoids duplicated logic and ensures that EOF finalization is atomic and testable.

## Args:
    None

## Returns:
    None

## Raises:
    - AttributeError: if self.current does not have a lineno attribute. In normal operation self.current is a Token and this will not occur.
    - The method performs no other explicit error raising.

## State Changes:
- Attributes READ:
    - self.current (reads the Token object)
    - self.current.lineno (reads the integer line number from the current token)
- Attributes WRITTEN:
    - self.current is set to a new Token with:
        - lineno = the previously read self.current.lineno
        - type = TOKEN_EOF
        - value = "" (empty string)
    - self._iter is replaced with iter(()) — an iterator that yields no items
    - self.closed is set to True
- Note: self._pushed is not modified by this method (it is left intact).

## Constraints:
- Preconditions:
    - self.current must be a Token-like object exposing lineno. TokenStream's constructor and typical use guarantee this.
- Postconditions (guaranteed after the call):
    - self.current.type is TOKEN_EOF and self.current.value == "".
    - self.current.lineno equals the lineno of the token that was current immediately before calling close().
    - self._iter yields no further items (iter(())).
    - self.closed is True.
    - The deque self._pushed remains unchanged; therefore:
        - If self._pushed is empty, TokenStream.__bool__ will evaluate False (because current.type is TOKEN_EOF) and the .eos property will be True.
        - If self._pushed contains tokens, TokenStream.__bool__ will evaluate True (because bool(self._pushed) is True) and .eos will be False even though current.type is TOKEN_EOF. In this case, the first next() call after close() will return the EOF token (the previous current), and subsequent calls will begin returning the pushed tokens (because __next__ will pop from self._pushed and update current).

## Side Effects:
    - Mutates only the TokenStream instance: replaces current, replaces _iter, sets closed to True.
    - Does not perform I/O or communicate with external services.
    - Does not remove or mutate Token objects stored in self._pushed; Tokens are immutable data objects and remain unchanged.

### `src.jinja2.lexer.TokenStream.expect` · *method*

## Summary:
Consume and return the current token if it matches the given token expression; otherwise raise a TemplateSyntaxError. On success the stream advances by one token (self.current is updated to the next token).

## Description:
This method is used during parsing to assert that the next token in the stream has an expected shape and to consume it in a single step. Typical callers are parser code that validate token sequences (for example when parsing a specific grammar construct) — any code that must require a particular token at the current parse position will call this method to both check and advance the stream.

It is implemented as a dedicated method to centralize two responsibilities:
- concise token matching using the token-test expression syntax (delegated to Token.test), and
- uniform, user-friendly error messages for the two failure cases (unexpected end-of-stream vs. unexpected token), including attaching the token's lineno, stream name, and filename to the TemplateSyntaxError.

Keeping this logic in one method avoids duplicating error formatting and advancement semantics at every call site.

## Args:
    expr (str): A token expression describing the required token.
        - Format: either "TYPE" or "TYPE:VALUE" (only the first colon is significant).
        - Semantics: interpreted by Token.test:
            * "TYPE" matches tokens whose type equals TYPE.
            * "TYPE:VALUE" matches tokens whose type equals TYPE and whose value equals VALUE.
        - No default; caller must pass a string. If a non-str is passed, Token.test may raise a TypeError or AttributeError which will propagate.

## Returns:
    Token: The token that was matched and consumed (the "current" token at time of call).
        - On success the returned Token is the token that satisfied the expression.
        - Edge-case: if the token matched is an EOF token and Token.test returns True for the provided expr, the EOF Token is returned; the iterator advancement logic leaves current as TOKEN_EOF (see postconditions).

## Raises:
    TemplateSyntaxError:
        - If the current token does not match expr, one of two TemplateSyntaxError messages is raised:
            1) Unexpected end of template:
                - Condition: self.current.type is TOKEN_EOF and self.current.test(expr) is False.
                - Message: "unexpected end of template, expected {expr!r}."
                - The exception is raised with the lineno of the current token and the stream's name and filename.
            2) Unexpected token:
                - Condition: self.current.test(expr) is False and current.type is not TOKEN_EOF.
                - Message: "expected token {expr!r}, got {describe_token(self.current)!r}"
                - The exception is raised with the lineno of the current token and the stream's name and filename.
    Any exception raised by Token.test (for example TypeError when expr is not a string) or by describe_token/describe_token_expr will propagate unchanged.

## State Changes:
Attributes READ:
    - self.current (used to inspect the token; its .type and .lineno and .value may be read)
    - self.current.type
    - self.current.lineno
    - self.name (included in raised TemplateSyntaxError)
    - self.filename (included in raised TemplateSyntaxError)
    - self._pushed (inspected indirectly by __next__)
    - self._iter (advanced indirectly by __next__)

Attributes WRITTEN / mutated (via the call to next(self)):
    - self.current is updated to the next token from the stream (the stream advances by one token).
    - If a pushed token is consumed, self._pushed may have its leftmost element removed (popleft).
    - If the underlying iterator is exhausted during advancement, self.close() may be invoked which:
        * sets self.current to an EOF Token (lineno preserved),
        * sets self._iter to an empty iterator,
        * sets self.closed to True.
    - No other attributes are modified by expect itself.

Important behavioral guarantee: if the method raises TemplateSyntaxError (matching failed), the stream is not advanced and no state is changed by this method (it performs the test first and only calls next(self) on success).

## Constraints:
Preconditions:
    - self must be a properly-initialized TokenStream with a valid self.current Token (the constructor sets an initial Token and advances once).
    - expr should be a str conforming to the token expression formats described above; otherwise Token.test may raise.
    - The module-level helpers/constants referenced when constructing error messages (describe_token, describe_token_expr, TOKEN_EOF) must be available at runtime; otherwise a NameError may be raised while preparing the error message.

Postconditions:
    - On success (no exception):
        * The returned Token equals the token that was current at call start.
        * The stream has advanced: self.current now refers to the next token (or remains TOKEN_EOF if the stream reached its end).
    - On failure (TemplateSyntaxError raised):
        * self remains unchanged (no tokens consumed, no attributes modified by expect).

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside of the TokenStream except for mutation to internal collections referenced above (self._pushed via popleft is internal).
    - The only side effect visible to callers is advancing the TokenStream (consuming one token) on success.

## Implementation notes and edge cases:
    - The method first calls self.current.test(expr). Reimplementation must ensure the test is performed before any advancement.
    - Error messages differ between EOF and non-EOF mismatches; tests and callers (unit tests / parser code) may assert the exact text and the attached lineno/name/filename fields of TemplateSyntaxError.
    - If expr is malformed (not a string), Token.test may raise (TypeError/AttributeError) — this behavior is preserved and should not be swallowed.
    - next(self) must behave like TokenStream.__next__: return the current token and then advance self.current; if the underlying iterator raises StopIteration, the stream should be closed (current set to an EOF Token, _iter replaced with an empty iterator, closed set True).
    - When formatting the non-EOF mismatch message, describe_token(self.current) should be used to produce the human-readable representation inserted into the exception message.

## `src.jinja2.lexer.get_lexer` · *function*

## Summary:
Return a cached Lexer for the given Environment configuration, creating and caching a new one if none exists for that configuration.

## Description:
This function centralizes creation and reuse of Lexer instances keyed by the environment's lexing-related configuration. It computes a key from a fixed set of Environment attributes (block/variable/comment delimiters, line prefixes, trimming flags, newline handling, and trailing newline preference), then checks a module-level cache for an existing Lexer. If the cache contains a Lexer for that key it is returned; otherwise a new Lexer is constructed with the provided Environment and stored in the cache before being returned.

Known callers within the provided context:
- No direct callers were available in the provided snippets. Typically, this function is invoked by higher-level template compilation or parsing code when an Environment needs a Lexer (for example, during template parsing, tokenization, or when rendering templates that require lexing).

Why this logic is extracted:
- Responsibility boundary: creation and caching of Lexer instances is a cross-cutting concern that should be centralized to avoid duplicate Lexer construction for equivalent Environment configurations, control memory usage through reuse, and keep the rest of the parser/renderer logic unaware of caching mechanics.
- Encapsulation: callers obtain a ready-to-use Lexer for an Environment without duplicating the key computation or cache lookup logic.

## Args:
    environment (Environment): The Environment instance whose lexing configuration determines which Lexer to return.
        - Required attributes accessed (must exist on the Environment):
            * block_start_string
            * block_end_string
            * variable_start_string
            * variable_end_string
            * comment_start_string
            * comment_end_string
            * line_statement_prefix
            * line_comment_prefix
            * trim_blocks
            * lstrip_blocks
            * newline_sequence
            * keep_trailing_newline
        - The function does not modify the Environment; it only reads these attributes.
        - Type constraint: expects an object compatible with the Environment type imported in the module.

## Returns:
    Lexer: A Lexer instance configured for the provided Environment.
    - Returned value is either:
        * an existing Lexer retrieved from the module-level cache for the computed key, or
        * a newly constructed Lexer(environment) stored in the cache and then returned.
    - The function always returns a Lexer (assuming no exceptions are raised during construction).

## Raises:
    - Any exception raised by the Lexer constructor will propagate to the caller.
      For example, if Lexer(...) validates environment configuration and raises TemplateSyntaxError (or other exceptions), get_lexer does not catch it and so the exception will surface to the caller.
    - The function itself does not explicitly raise exceptions; missing required attributes on the provided environment will result in an AttributeError raised when attempting to read them.

## Constraints:
    Preconditions:
        - The caller must supply a valid Environment-like object that exposes the attributes listed above.
        - The environment attribute values used to form the key should be immutable for the duration you expect the cached Lexer to remain valid; otherwise cache reuse may return a Lexer whose configuration no longer matches the current Environment attributes.
    Postconditions:
        - After a successful call, the module-level cache contains a mapping from the computed key to the returned Lexer (either pre-existing or newly inserted).
        - The returned object is a Lexer constructed with the provided Environment (or the cached equivalent).

## Side Effects:
    - Mutates module-level cache: on a cache miss, assigns the newly created Lexer into the module-level cache under the computed key.
    - No I/O, network, stdout, or external service calls are performed by this function itself.
    - No direct mutation of the provided Environment instance occurs.

## Control Flow:
flowchart TD
    Start --> ComputeKey[Compute key from environment attributes]
    ComputeKey --> CacheLookup[Lookup key in _lexer_cache]
    CacheLookup -->|Found| ReturnCached[Return cached Lexer]
    CacheLookup -->|Not found| Construct[Construct Lexer(environment)]
    Construct --> InsertCache[Insert Lexer into _lexer_cache under key]
    InsertCache --> ReturnNew[Return newly constructed Lexer]
    ReturnCached --> End[End]
    ReturnNew --> End

## Examples:
- Basic usage
    try:
        lexer = get_lexer(env)
        # lexer can now be used for tokenization/parsing
    except Exception as e:
        # Any exception from Lexer(...) (e.g., configuration errors) will propagate here.
        raise

- Notes on cache validity
    # Avoid mutating the Environment's lexing-related attributes after obtaining a cached lexer,
    # because subsequent uses of the cached lexer will reflect the configuration at cache-insert time.

## `src.jinja2.lexer.OptionalLStrip` · *class*

## Summary:
OptionalLStrip is an immutable tuple subclass that collects positional members into a tuple instance. Its sole purpose is to provide a distinct type (OptionalLStrip) whose instances behave like tuples containing the provided members.

## Description:
OptionalLStrip should be instantiated when a compact, typed, immutable container is required and the codebase benefits from distinguishing this container from a plain tuple by type. Callers create instances by passing the elements as positional arguments; any keyword arguments passed are accepted by the constructor signature but ignored.

Motivation:
- Provides a semantic marker type distinct from tuple while retaining all tuple behaviour.
- Allows type-checking or isinstance() checks against OptionalLStrip to detect this specific semantic case elsewhere in the lexer/parser logic.

Typical callers / factories:
- Lexer or parser components that want to mark a collected set of left-strip tokens/options with a distinct type.
- Any code that previously treated these collections as tuples but wants a stronger type signal.

Responsibility boundary:
- It does not add methods or attributes beyond tuple semantics.
- It does not perform validation or mutation; it simply packs the provided positional arguments into a tuple of members.

## State:
- Inherits all tuple semantics and immutability. Instances are immutable sequences of the provided members.
- Attributes:
    - No instance attributes (class defines __slots__ = ()). All state is the tuple contents stored by the tuple base.
- __init__ / __new__ parameters:
    - Positional members (*members): Any objects; they are stored in the tuple in the same order they are passed.
    - **kwargs: Accepted by the signature but ignored (no effect). Callers may pass keyword args without raising errors; they will not be stored.
- Valid values:
    - Members may be any Python object (no type constraint enforced by the class).
- Class invariants:
    - Instances are tuples whose elements remain constant for the lifetime of the object.
    - No per-instance attributes exist beyond the tuple contents.

## Lifecycle:
- Creation:
    - Instantiate by calling OptionalLStrip(elem1, elem2, ...)
    - No required positional arguments; calling OptionalLStrip() yields an empty OptionalLStrip (an empty tuple instance of this type).
    - Keyword arguments may be provided but will be ignored.
- Usage:
    - After creation, use exactly like a tuple: iteration, indexing, slicing, len(), unpacking, hashing, comparison, etc.
    - Typical operations: isinstance(x, OptionalLStrip) to detect the special type, iterate through contained members, or access by index.
    - There is no special method sequence required — construction followed by any tuple operations is valid.
- Destruction / cleanup:
    - No cleanup or close actions required. Instances rely on Python's normal garbage collection; no context manager support.

## Method Map:
Flow of the single relevant operation:

graph TD
    A[Call OptionalLStrip(*members, **kwargs)] --> B[OptionalLStrip.__new__]
    B --> C[tuple.__new__ returns tuple instance of provided members]
    C --> D[Use as tuple: iteration/indexing/hashing]

(Interpretation: the constructor packs the positional members into a tuple by delegating to the tuple base; kwargs are ignored.)

## Raises:
- The class implementation itself does not explicitly raise exceptions.
- Potential runtime exceptions may come from Python internals when performing tuple construction only if unusual conditions arise (e.g., memory exhaustion), but no class-level validation or error raising is present.
- Passing unsupported argument forms is safe: kwargs are accepted by the signature and ignored rather than causing TypeError.

## Example:
- Create an instance with two members:
    inst = OptionalLStrip('a', 'b')
    type(inst) is OptionalLStrip
    tuple(inst) == ('a', 'b')
    len(inst) == 2
- Create an empty instance:
    empty = OptionalLStrip()
    tuple(empty) == ()
- Keyword args are ignored:
    inst2 = OptionalLStrip(1, 2, some_flag=True)  # some_flag is ignored; inst2 == (1, 2)
- Typical usage pattern:
    if isinstance(x, OptionalLStrip):
        for item in x:
            process(item)

### `src.jinja2.lexer.OptionalLStrip.__new__` · *method*

## Summary:
Constructs and returns a new OptionalLStrip instance whose elements are exactly the positional arguments supplied to the constructor.

## Description:
This __new__ is the object-creation entry point for the OptionalLStrip tuple subclass. When OptionalLStrip(...) is called, Python collects positional arguments into a tuple named members and passes them to this method; the method then delegates to the base tuple constructor to create and return an instance of the subclass whose contents match those collected positional arguments.

Known callers / lifecycle:
- Invoked whenever code constructs an OptionalLStrip instance (e.g., within lexer construction code that creates marker/flag objects). It runs at object-creation time during the lexing/parsing pipeline whenever OptionalLStrip(...) is executed.

Why separate __new__:
- OptionalLStrip subclasses tuple (an immutable type). Controlling instance creation (to ensure the returned object is an instance of the subclass and initialized from the collected positional args) must be done in __new__, because __init__ cannot modify the already-constructed immutable tuple contents.

## Args:
    cls (type): The class being instantiated (OptionalLStrip or a subclass).
    *members (Any): Zero or more positional arguments. The interpreter packs these into a tuple (members). The items of that packed tuple become the elements of the returned OptionalLStrip instance.
    **kwargs (Any): Accepted by the signature for compatibility but ignored by this implementation. Providing keyword arguments will not affect the returned object and will not cause an error here.

Important notes about members:
- members is the varargs tuple produced by Python. The method passes that tuple as the single iterable argument to the base tuple constructor.
- If the caller intends to expand an iterable into elements, they must unpack it: OptionalLStrip(*iterable). Passing an iterable without unpacking (OptionalLStrip(iterable)) will make the iterable itself a single element of the resulting OptionalLStrip.

## Returns:
    OptionalLStrip: An instance of cls whose length equals the number of positional arguments passed.
    - No positional args -> returns an empty OptionalLStrip (len == 0).
    - n positional args -> returns an OptionalLStrip with n elements, where element i equals the i-th positional argument.

Examples:
    - OptionalLStrip() -> OptionalLStrip(())
    - OptionalLStrip(1, 2) -> OptionalLStrip((1, 2))
    - OptionalLStrip([1, 2]) -> OptionalLStrip(([1, 2],))  # list is a single element
    - OptionalLStrip(*[1, 2]) -> OptionalLStrip((1, 2))    # iterable unpacked into elements

## Raises:
    - This implementation does not explicitly raise exceptions. Under normal operation (Python collects positional args into a tuple), delegating to tuple.__new__(cls, members) will succeed and not raise. No additional exception behavior should be expected from this method.

## State Changes:
    Attributes READ:
        - None (the method only receives cls and the collected members; it does not read instance attributes).
    Attributes WRITTEN:
        - None on an existing instance. The method returns a newly-created tuple-subclass instance initialized by the base tuple constructor.

## Constraints:
    Preconditions:
        - cls should be a tuple subclass (OptionalLStrip is defined as such). The method relies on normal tuple construction semantics.
        - Callers that intend to expand iterables into separate elements must use argument-unpacking.

    Postconditions:
        - The returned value is an instance of cls.
        - len(returned) == number of positional arguments given.
        - For each index i, returned[i] == members[i] (members is the varargs-tuple).

## Side Effects:
    - No I/O, no external network or filesystem access.
    - No mutation of provided arguments or global state performed by this method.
    - The created object is immutable (it is a tuple subclass and OptionalLStrip declares __slots__ = ()), so no instance attributes beyond tuple items can be added.

## Implementation guidance:
    - Implement exactly as: return super().__new__(cls, members)
    - Accept **kwargs in the signature for compatibility but do not use them.
    - Rely on Python's varargs packing: members will always be a tuple; passing it to tuple.__new__ produces a tuple whose elements are the packed items.

## `src.jinja2.lexer._Rule` · *class*

## Summary:
Represents a single lexer rule as an immutable tuple containing a compiled regular-expression pattern, the associated token name(s) or deferred-failure tuple, and an optional command hint.

## Description:
This small, immutable value object is used by the lexer to describe how to match input and what to do when a match occurs. It separates the static description of a rule (regex, resulting tokens or deferred failure, and an optional command) from the runtime engine that applies rules to input.

Scenarios for instantiation:
- Constructed during lexer setup or rule-table building when enumerating the lexical rules for a template language.
- Returned by rule factory utilities that convert declarative rule descriptions into an executable form for the lexer.

Motivation and responsibility boundary:
- Encapsulates the three pieces of data required by the lexer for each rule.
- Keeps rule data immutable and transportable (safe to store in sequences or maps).
- Does not perform matching, token emission, or state transitions itself — it only provides data the lexer uses.

## State:
- pattern: t.Pattern[str]
  - Type: compiled regular-expression object (as produced by re.compile(...)).
  - Purpose: used by the lexer to test whether this rule matches the input at the current position.
  - Valid values: any compiled regex pattern object. No runtime validation is performed by _Rule itself.
  - Invariant: non-empty and unchanged after construction (NamedTuple immutability).

- tokens: t.Union[str, t.Tuple[str, ...], t.Tuple[Failure]]
  - Type (exact): one of
    - str — a single token name
    - t.Tuple[str, ...] — a variable-length tuple of token names (zero or more token-name strings)
    - t.Tuple[Failure] — a tuple typed to contain Failure; according to the annotation this denotes a one-element tuple whose element is a Failure instance
  - Purpose: indicates what the lexer should produce or defer when the pattern matches:
    - If a str or t.Tuple[str, ...]: token name(s) the lexer should emit.
    - If a t.Tuple[Failure]: a deferred error factory instance (Failure) that should be called later with line/filename to raise a TemplateSyntaxError.
  - Valid values: adhere to the exact type alternatives above. Note that the annotation t.Tuple[Failure] denotes a single-element tuple containing a Failure (not an arbitrary-length sequence of Failures).
  - Invariant: the field's type and contents are fixed on construction.

- command: t.Optional[str]
  - Type: either a string or None.
  - Purpose: optional directive or state-transition hint for the lexer (semantics implemented by the lexer engine).
  - Valid values: any string recognized by the lexer or None to indicate no command.
  - Invariant: immutable after construction.

Class invariants:
- Instances are immutable (NamedTuple behavior): pattern, tokens, and command cannot be changed after creation.
- All three fields are present; supply None explicitly for command when no command is required.

## Lifecycle:
Creation:
- Constructor signature (positional or named): _Rule(pattern, tokens, command)
  - pattern (t.Pattern[str]): compiled regex
  - tokens (str | tuple[str, ...] | tuple[Failure]): see types above
  - command (str | None): optional; pass None if no command is desired
- The class provides no validation logic; incorrect types will not raise at construction time but may cause errors when the lexer uses the fields.

Usage:
- Typical lexer interaction:
  1. The lexer iterates rules (a sequence of _Rule) or queries them by state.
  2. For each rule, the lexer applies rule.pattern.match(input_at_pos).
  3. On match:
     - If tokens is a str or tuple[str, ...], emit those token names according to the lexer's emission API.
     - If tokens is a tuple[Failure] (single-element tuple per the type annotation), treat it as a deferred error: later call the contained Failure instance with (lineno, filename) to raise the stored TemplateSyntaxError.
     - If command is not None, the lexer applies the command according to its own state-machine rules (for example, push/pop or change lexer mode).
- No required ordering or lifecycle methods exist on _Rule itself; it is a passive data carrier.

Destruction / cleanup:
- No cleanup necessary. Standard garbage collection applies. No context manager or close semantics.

## Method Map:
flowchart LR
    A[Create _Rule(pattern,tokens,command)] --> B[Immutable container]
    B --> C[Lexer iterates rule list]
    C --> D[Apply rule.pattern.match(input_at_pos)]
    D -->|no match| E[next rule]
    D -->|match| F[Inspect rule.tokens]
    F -->|str or tuple[str,...]| G[Emit token(s)]
    F -->|tuple[Failure] (single-element)| H[Defer error; call Failure(lineno,filename) later to raise]
    F -->|command != None| I[Apply lexer command/state transition]

## Raises:
- Construction:
  - No explicit validation; constructing with wrong argument types will not raise beyond normal Python errors for incorrect argument counts or catastrophic misuse (TypeError for wrong call signature).
  - Because _Rule does not validate types, supplying a non-pattern for pattern or an unexpected tokens shape will not raise until the lexer attempts to use those fields (e.g., AttributeError when calling match on a non-pattern).
- Runtime usage:
  - Using the fields incorrectly (for example, treating a t.Tuple[Failure] as an arbitrary-length tuple of Failures) can produce IndexError, TypeError, or AttributeError in the lexer — these are not raised by _Rule itself but by the consumer.

## Example:
- Construct a rule that matches one or more spaces and emits a WHITESPACE token:
  - pattern = re.compile(r'\s+')
  - rule = _Rule(pattern, "WHITESPACE", None)

- Construct a rule that matches an unexpected sequence and defers raising a TemplateSyntaxError:
  - f = Failure("unexpected sequence")
  - rule = _Rule(re.compile(r'...'), (f,), None)
  - Later, when the lexer knows lineno and filename, call f(lineno, filename) to raise the stored TemplateSyntaxError.

Implementation notes for reimplementation:
- Preserve the exact three-field NamedTuple shape and typing.
- Treat the class as a passive immutable data holder with no side-effecting methods.
- Do not add implicit validation; align behavior with the original by allowing the lexer to decide how to interpret and validate the fields at use time.

## `src.jinja2.lexer.Lexer` · *class*

*No documentation generated.*

### `src.jinja2.lexer.Lexer.__init__` · *method*

## Summary:
Initializes a Lexer instance by compiling the lexer's regular-expression rules and storing lexer configuration derived from the provided Environment onto the instance.

## Description:
This initializer prepares the internal state required for tokenizing Jinja2 templates. It:
- compiles per-token regular expressions (via helper c, re.compile with MULTILINE|DOTALL),
- obtains tag-specific rules via compile_rules(environment),
- escapes environment-delimited strings (block/variable/comment start/end) and uses them to build combined regexes for the lexer's root and special states,
- reads trim/lstrip/newline settings from the Environment and stores them,
- constructs self.rules, a mapping of lexer state names to ordered lists of _Rule objects that drive the lexer state machine.

Known callers and typical call-time context:
- Called whenever a Lexer object is instantiated (e.g., new Lexer(environment)) as part of template parsing/compilation setup. Typical call sites are code paths that set up lexing for a given Environment or Template compilation phase. The method is the entry point executed during Lexer construction and not intended to be invoked repeatedly after initialization.

Why this is a separate method:
- The construction of multiple, interdependent regular expressions and the assembly of a complex mapping of lexer states is non-trivial and benefits from being isolated in the initializer. Keeping this logic in __init__ centralizes configuration based on Environment values and ensures a ready-to-use self.rules structure for the lexer's runtime tokenization logic.

## Args:
    environment (Environment): An Environment instance that provides the template delimiter strings and lexer configuration flags. Required attributes on environment:
        - block_start_string (str)
        - block_end_string (str)
        - comment_end_string (str)
        - variable_end_string (str)
        - trim_blocks (bool)
        - lstrip_blocks (bool)
        - newline_sequence (str)
        - keep_trailing_newline (bool)
    These attributes are read to build regexes and flags. Passing an object that lacks these attributes or uses incompatible types will raise an error.

## Returns:
    None

## Raises:
    AttributeError:
        - If the provided environment does not expose any of the required attributes listed above.
    re.error:
        - If any of the dynamically constructed regular-expression patterns are invalid when passed to re.compile (this can happen if environment delimiter strings contain characters producing an invalid pattern after the composition logic).
    TypeError:
        - If environment is None or some of the required attributes are of incompatible types (e.g., non-string values where strings are expected) such that operations like re.escape or string formatting fail.
    Any exceptions raised by compile_rules(environment) or other helpers called during initialization will propagate unchanged.

## State Changes:
Attributes READ:
    - (none of self.* attributes are read in this method; it only reads values from the provided environment and module-level helpers)

Attributes WRITTEN:
    - self.lstrip_blocks (bool): set from environment.lstrip_blocks
    - self.newline_sequence (str): set from environment.newline_sequence
    - self.keep_trailing_newline (bool): set from environment.keep_trailing_newline
    - self.rules (dict[str, list[_Rule]]): populated with the lexer's state machine rules. Expected keys include at least "root" and token-begin states (e.g., TOKEN_COMMENT_BEGIN, TOKEN_BLOCK_BEGIN, TOKEN_VARIABLE_BEGIN, TOKEN_RAW_BEGIN, TOKEN_LINESTATEMENT_BEGIN, TOKEN_LINECOMMENT_BEGIN). Each value is an ordered list of _Rule instances built from compiled regexes and associated action tokens.

## Constraints:
Preconditions:
    - environment must be an Environment-like object exposing the attributes listed in Args and using expected types (strings for delimiter/newline attributes, booleans for trim/lstrip flags).
    - Module-level identifiers used by this initializer must be available and valid: compiled helper names and constants (e.g., compile_rules, whitespace_re, float_re, integer_re, name_re, string_re, operator_re, TOKEN_*, _Rule, OptionalLStrip, Failure). The initializer assumes these exist in the module/global scope.

Postconditions:
    - After return, the Lexer instance is configured and ready for use by the lexer's tokenization routines: self.rules is a mapping of lexer states -> rule lists that the lexer will consult for matching tokens; newline and trimming flags are stored on the instance.
    - No external resources (files, network) are opened; all state changes are confined to the Lexer instance.

## Side Effects:
    - No I/O or network operations.
    - Instantiates compiled regular-expression Pattern objects and _Rule instances (memory allocation).
    - May execute compile_rules(environment) which could have its own side effects (documented where compile_rules is implemented). Exceptions from those calls propagate.

### `src.jinja2.lexer.Lexer._normalize_newlines` · *method*

## Summary:
Replaces occurrences of the module-level newline pattern with the lexer's configured newline sequence and returns the normalized string, without mutating object state.

## Description:
This helper normalizes newline characters in a piece of text according to the lexer's configured newline_sequence. Known callers:
- Lexer.wrap: called for TOKEN_DATA values (value strings produced by the lexer) and for the contents of TOKEN_STRING (the string literal content before escape decoding). It is invoked during the token wrapping stage that converts raw token tuples into Token objects, immediately before the Token is yielded to consumers.
This logic is factored into a dedicated method so all newline normalization is applied consistently from a single location (controlled by the Environment via self.newline_sequence) rather than duplicated at each call site.

## Args:
    value (str): Input text to normalize. Must be a Python string.

## Returns:
    str: A new string where every match of the module-level newline_re pattern has been replaced with self.newline_sequence.
    Edge cases:
    - If value is the empty string, the empty string is returned.
    - If there are no matches of newline_re in value, the original string content is returned (possibly the same object or a new equal string).

## Raises:
    This method does not explicitly raise exceptions. However:
    - If value is not a str, Python will raise a TypeError when passing it into the regex substitution machinery.
    - If self.newline_sequence is not a str (contrary to Environment expectations), behavior is undefined and may raise a TypeError.

## State Changes:
    Attributes READ:
        - self.newline_sequence
    Attributes WRITTEN:
        - None (no attributes of self are modified)

## Constraints:
    Preconditions:
        - The Lexer instance must have self.newline_sequence defined (typically provided by Environment) and it should be a string.
        - The module-level name newline_re must be a compiled regular expression object with a valid sub method (as used by re.Pattern.sub).
        - value must be a str (type hinted as str).
    Postconditions:
        - The returned string will contain self.newline_sequence in place of every substring matched by newline_re.
        - No other attributes on self are modified.

## Side Effects:
    - None: the method performs no I/O, does not call external services, and does not mutate objects outside of returning the new string.

### `src.jinja2.lexer.Lexer.tokenize` · *method*

## Summary:
Create a primed TokenStream from a template source string by running the lexer's token generator and wrapping its token tuples into Token objects; returns a parser-ready stream without mutating the Lexer instance.

## Description:
- Known callers and lifecycle stage:
    - Called by parser components and the template compilation pipeline that need a TokenStream for parsing (e.g., template parser/front-end). It is invoked at the start of the parsing stage after the raw template source is read.
    - This method encapsulates the transition from raw source text to a TokenStream (lexer -> token wrapper -> stream), so callers receive a ready-to-use, primed TokenStream.

- Why this is a separate method:
    - Separates concerns: tokeniter produces low-level (lineno, token_name, raw_value) tuples while wrap converts those tuples to Token objects and applies normalization/validation; TokenStream then provides push/look semantics and primes the first token. Putting these steps into one helper makes the public API simple (one call to get a TokenStream) while keeping each processing stage modular and testable.

## Args:
    source (str): The full template source text to lex. Must be a str.
    name (Optional[str]): Optional template name used in error messages. Can be None.
    filename (Optional[str]): Optional filename used in error messages. Can be None.
    state (Optional[str]): Optional initial lexer state. Allowed values:
        - None (default): treated as the normal start (equivalent to "root").
        - "root": start in root state.
        - "variable": starts inside a variable block (lexer will push "variable_begin").
        - "block": starts inside a block (lexer will push "block_begin").
      If a provided non-None state is not one of "root", "variable", or "block", an AssertionError is raised by tokeniter.

## Returns:
    TokenStream: A primed TokenStream instance wrapping the lexer's tokens.
    - The returned stream has already been primed (TokenStream __init__ advances once), so stream.current is the first token (or an EOF sentinel if the template produced no tokens).
    - The TokenStream holds the provided name and filename for use in error messages.

## Raises:
    TemplateSyntaxError: If the lexing process detects malformed template input (for example unmatched delimiters, invalid identifier characters, unterminated string/raw/comment blocks). These errors are raised by tokeniter or wrap and include lineno, name, and filename context.
    RuntimeError: If a runtime invariant in the lexer/wrap is violated (for example, dynamic-group resolution failures indicated by "#bygroup" or "#pop" patterns). These originate from tokeniter or wrap.
    AssertionError: If the provided state argument is invalid (tokeniter asserts allowed states).
    Any exception raised by TokenStream construction/priming: TokenStream __init__ primes the incoming generator and will propagate any exception that occurs while obtaining the first token (including the TemplateSyntaxError or runtime errors above).

## State Changes:
- Attributes READ:
    - None directly on this method; however, calling this method causes the invoked helpers to read Lexer attributes such as:
        - self.rules (lexer rules used by tokeniter)
        - self.keep_trailing_newline (controls trimming of trailing blank line)
        - self.lstrip_blocks (affects whitespace handling)
        - self.newline_sequence (used by wrap/_normalize_newlines)
  (Those are read indirectly by tokeniter and wrap.)

- Attributes WRITTEN:
    - None. tokenize does not modify any self.<attr> fields on the Lexer instance.

## Constraints:
- Preconditions:
    - source must be a str (the lexer expects textual input).
    - If state is provided and not None, it must be one of "root", "variable", or "block" (otherwise tokeniter raises AssertionError).
    - name and filename may be None or strings; they are only used for error context.

- Postconditions:
    - A TokenStream instance is returned. The stream is primed so stream.current is the first token or an EOF token if no tokens were produced.
    - The Lexer instance remains unchanged (no attributes are mutated by this call).

## Side Effects:
    - No external I/O or network calls.
    - Allocates generator/iterator objects and the TokenStream; priming the TokenStream will drive the lexer's generator up to the first yielded Token, which can cause validation and raise lexical exceptions (TemplateSyntaxError, RuntimeError) during construction.
    - Exceptions raised during lexing are propagated to the caller and may include template location context (lineno, name, filename).

### `src.jinja2.lexer.Lexer.wrap` · *method*

## Summary:
Transform a raw lexer triple stream (lineno, raw_token_kind, raw_text) into finalized Token objects by filtering ignored tokens, remapping token kinds, normalizing text/newlines, validating identifiers, unescaping string literals, and converting numeric literals. The method yields Token instances and does not mutate Lexer instance state.

## Description:
Known callers and context:
- Called by: Lexer.tokenize (it passes tokeniter's output into wrap). The returned iterator is typically wrapped by TokenStream and consumed by the parser.
- Pipeline stage: final lexical normalization step after pattern matching; called immediately after tokeniter produces raw matches and before parsing.

Why this logic is a separate method:
- Keeps pattern-matching (tokeniter) and token normalization/validation responsibilities separated.
- Enables lazy, streaming conversion from raw triples to Token objects without buffering.
- Centralizes all conversions and error reporting for lexemes in a single place for easier maintenance and testing.

## Args:
    stream (Iterable[Tuple[int, str, str]]):
        Iterable that yields 3-tuples:
        - lineno (int): line number where the match occurred.
        - token (str): raw token kind as produced by tokeniter (module-level token constants or group names such as "keyword").
        - value_str (str): the raw matched substring for that token.
        Preconditions: each yielded item must be a 3-tuple of (int, str, str).
    name (Optional[str], default=None):
        Optional logical template name used in TemplateSyntaxError error messages.
    filename (Optional[str], default=None):
        Optional filename used in TemplateSyntaxError error messages.

## Returns:
    Iterator[Token]
        Yields Token(lineno, type, value) for each input triple that is not filtered out.
        For each token kind the returned Token fields are:
        - lineno (int): forwarded from input.
        - type (str): generally the (possibly remapped) token kind; specific remappings below.
        - value: the normalized/converted payload (details below).
        Specific conversion rules:
        - If token in ignored_tokens: skipped (nothing yielded).
        - TOKEN_LINESTATEMENT_BEGIN -> remapped type TOKEN_BLOCK_BEGIN (value unchanged).
        - TOKEN_LINESTATEMENT_END -> remapped type TOKEN_BLOCK_END (value unchanged).
        - TOKEN_RAW_BEGIN and TOKEN_RAW_END: skipped (used only for raw block delimiting).
        - TOKEN_DATA: value = self._normalize_newlines(value_str) (string with Lexer.newline_sequence).
        - "keyword": token type is replaced by the raw value_str (so token.type == value_str); the value payload remains the original value_str.
        - TOKEN_NAME: value = value_str (string). Additionally, the method validates that value.isidentifier() is True; otherwise it raises TemplateSyntaxError.
        - TOKEN_STRING: value = unquoted, newline-normalized, and escape-decoded string:
            * The code uses value_str[1:-1] to strip surrounding quotes, then self._normalize_newlines,
            * encodes to ASCII with "backslashreplace", then decodes using "unicode-escape" to interpret backslash escapes.
            * Any Exception raised during this process is converted to a TemplateSyntaxError (see Raises).
        - TOKEN_INTEGER: value = int(value_str.replace("_", ""), 0)
            * Underscores are allowed and removed; base 0 lets Python infer base from prefixes (0x, 0o, 0b).
        - TOKEN_FLOAT: value = literal_eval(value_str.replace("_", ""))
            * Underscores are removed before literal_eval; literal_eval enforces Python literal syntax.
        - TOKEN_OPERATOR: token type is replaced by operators[value_str] (module-level mapping). The value remains the original value_str unless transformed above.
        - For all other token kinds: value remains value_str and the token type is unchanged.
        Order and laziness:
        - Tokens are yielded in the same order as the input stream after filtering and remapping.
        - Because this is a generator, conversions and exceptions occur lazily as the iterator is consumed.

## Raises:
    TemplateSyntaxError
        - When TOKEN_NAME contains invalid identifier characters:
            Condition: token == TOKEN_NAME and not value_str.isidentifier()
            Exact message passed to TemplateSyntaxError: "Invalid character in identifier"
            TemplateSyntaxError is raised with arguments (message, lineno, name, filename).
        - When processing TOKEN_STRING and any Exception occurs during unquoting/unescaping:
            Condition: any Exception e raised while slicing, normalizing, encoding, or decoding the string.
            The final message passed to TemplateSyntaxError is the last colon-separated segment of str(e): msg = str(e).split(":")[-1].strip()
            The original exception is attached as the __cause__ (via "raise ... from e").
    KeyError
        - When token == TOKEN_OPERATOR and value_str is not present in the module-level operators mapping.
        - This KeyError is not caught and will propagate to the caller.
    ValueError, SyntaxError, etc.
        - int(...) may raise ValueError for an invalid integer literal.
        - literal_eval(...) may raise ValueError, SyntaxError, or other exceptions for invalid float/number literals.
        - These exceptions are not caught within wrap and propagate to the caller.

## State Changes:
Attributes READ:
    - self._normalize_newlines (method): invoked for TOKEN_DATA and TOKEN_STRING conversions.
Attributes WRITTEN:
    - None. The method does not assign to any self.<attribute> fields or mutate Lexer state.

## Constraints:
Preconditions:
    - The module-level names used by this method must be present and correctly defined:
        * ignored_tokens: iterable of token kinds that should be skipped.
        * operators: dict-like mapping from operator string to operator token kind.
        * TOKEN_* constants referenced in the method (for example TOKEN_DATA, TOKEN_NAME, TOKEN_STRING, TOKEN_INTEGER, TOKEN_FLOAT, TOKEN_OPERATOR, TOKEN_LINESTATEMENT_BEGIN, TOKEN_LINESTATEMENT_END, TOKEN_RAW_BEGIN, TOKEN_RAW_END, TOKEN_BLOCK_BEGIN, TOKEN_BLOCK_END).
    - For TOKEN_STRING: value_str must be a quoted literal (so slicing with [1:-1] is meaningful); malformed quotes may cause exceptions which will be re-raised as TemplateSyntaxError.
Postconditions:
    - Every yielded value is a Token object whose type and value reflect the above mapping and conversions.
    - Ignored tokens and raw block boundary tokens are never yielded.
    - Numeric tokens are converted to native numeric Python objects (int or the literal_eval result).
    - The method does not change Lexer attributes.

## Side Effects:
    - No file, network, or external I/O is performed.
    - No mutation of objects outside the generator (only Token instances are created and yielded).
    - Exceptions raised by conversions are propagated or converted to TemplateSyntaxError as documented.
    - The generator is lazy: side effects (including exceptions) only occur during iteration/consumption.

### `src.jinja2.lexer.Lexer.tokeniter` · *method*

*No documentation generated.*

