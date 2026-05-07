# `pretty_printers.py`

## `onlinejudge_command.pretty_printers._PrettyTokenType` · *class*

## Summary:
A small internal enumeration that classifies token types used by the pretty-printers in this module. Each member represents a logical category assigned to text tokens (body text, whitespace, newline, hints, line numbers, highlighting boundaries, and others).

## Description:
This enum exists to provide a fixed, typed set of token categories for tokenization, formatting, and rendering logic in the pretty-printers module. Typical consumers are the tokenization and rendering code paths that convert raw text / diffs into sequences of typed tokens and then map token types to colors, prefixes, or other presentation details.

Motivation:
- Encapsulates all token categories in one place so the rest of the module can perform type-safe comparisons (instead of fragile string checks).
- Serves as the single source of truth for token names used by pretty-print logic, ensuring consistency across token creation, matching, and rendering.

Instantiate this enum in situ (no factory methods are defined here); it is intended for use only as a set of constants accessed directly from the class.

## State:
Members (each is an instance of _PrettyTokenType; .name is the member name; .value is the string shown below):
- BODY (str value: 'BODY')
  - Represents ordinary body text content.
- BODY_HIGHLIGHT_LEFT (str value: 'BODY_HIGHLIGHT_LEFT')
  - Represents the left-side token of a highlighted body span (start of highlight range).
- BODY_HIGHLIGHT_RIGHT (str value: 'BODY_HIGHLIGHT_RIGHT')
  - Represents the right-side token of a highlighted body span (end of highlight range).
- WHITESPACE (str value: 'WHITESPACE')
  - Represents sequences of (rendered) whitespace characters.
- NEWLINE (str value: 'NEWLINE')
  - Represents explicit newline token boundaries.
- HINT (str value: 'HINT')
  - Represents hint text or annotations (e.g., commentary or meta-lines).
- LINENO (str value: 'LINENO')
  - Represents line-number tokens (prefixes used when showing line numbers).
- OTHERS (str value: 'OTHERS')
  - A fallback category for tokens that do not match any other category.

Attribute invariants:
- Members are singletons: for any member name, repeated accesses return the identical object (is-comparison holds).
- Member names and values are constant and immutable; callers must not attempt to mutate member attributes.
- Only the listed members exist; no other member names are valid.

For callers:
- When constructing or matching tokens, you should use the enum members (e.g., _PrettyTokenType.BODY) rather than raw strings.
- Use the .name attribute to get the enumerated name, and .value to get the string value if needed for serialization.

## Lifecycle:
Creation:
- No runtime initialization beyond Python's enum machinery is required.
- Access patterns to obtain a member:
  - By attribute: _PrettyTokenType.BODY
  - By constructor with value: _PrettyTokenType('BODY')  (raises ValueError if not a valid value)
  - By name via subscription: _PrettyTokenType['BODY']  (raises KeyError if name not found)

Usage:
- Typical usage is read-only:
  1. Tokenizer assigns a token type when producing tokens.
  2. Renderer inspects token.type and switches on member to decide styling, color, or formatting.
  3. Comparisons are performed using equality or identity (recommended: identity or equality against the enum member).
- No particular method-call ordering is required by the enum itself; it is a passive value object.

Destruction / Cleanup:
- No special cleanup required. Enum members live for the program lifetime and have no resources to release.

## Method Map:
A simple usage flow (mermaid flowchart) showing common ways to obtain and use members and possible error paths:

flowchart LR
    Start((Start))
    Start --> Attr[_PrettyTokenType.BODY (attribute access)]
    Start --> Val[_PrettyTokenType('BODY') (by value)]
    Start --> Name[_PrettyTokenType['BODY'] (by name/subscript)]
    Attr --> Use[Use in tokenization/rendering]
    Val --> Use
    Name --> Use
    Val -->|invalid value| ValueError[ValueError raised]
    Name -->|invalid name| KeyError[KeyError raised]
    Start -->|wrong attribute| AttrError[AttributeError on missing attribute]
    Use --> End((End))

## Raises:
Exceptions that callers should be prepared to handle when obtaining members:
- ValueError: raised when calling the enum class with an invalid value string (e.g., _PrettyTokenType('INVALID')).
- KeyError: raised when using subscription by name with a missing name (e.g., _PrettyTokenType['INVALID']).
- AttributeError: raised when attempting to access a non-existent attribute on the enum class (e.g., _PrettyTokenType.INVALID_ATTR).

Note: These exceptions arise from Python's enum.Enum behavior; the enum class itself does not define custom exception logic.

## Example:
- Creation:
  - Via attribute: obtain the body token type with _PrettyTokenType.BODY.
  - Via value: obtain the same with _PrettyTokenType('BODY').
  - Via name: obtain the same with _PrettyTokenType['BODY'].

- Typical usage sequence:
  1. Tokenizer assigns tokens: each token gets a .type set to one of _PrettyTokenType members (e.g., BODY, NEWLINE, LINENO).
  2. Renderer inspects token.type and maps it to presentation properties (color, prefix).
  3. Comparisons use identity or equality against the enum member (e.g., if token.type is _PrettyTokenType.NEWLINE: ...).

- Error handling:
  - If you construct from an external string, wrap creation in a try/except to handle ValueError for unexpected values or KeyError when indexing by name.

## `onlinejudge_command.pretty_printers._PrettyToken` · *class*

## Summary:
Represents a single typed text token produced and consumed by the pretty-printers: a small, immutable pair (type, value) where type is a member of _PrettyTokenType and value is the token's text content.

## Description:
_Purpose and typical usage_
- _PrettyToken is a lightweight value object used throughout the pretty-printers module to carry a token's category (how it should be rendered) together with its textual content.
- Tokenizers in the module create sequences of _PrettyToken instances to represent input text, diffs, hints, whitespace, line numbers, highlights, etc. Renderers, formatters, and printers consume these tokens to decide colors, prefixes, and layout.
- This class is intentionally minimal: it provides structured, typed storage with the ergonomics of a tuple (indexing, unpacking) and NamedTuple conveniences (_asdict, _replace) while being immutable to make token sequences safe to share.

_Known callers / factories_
- The tokenizer and rendering functions inside onlinejudge_command.pretty_printers create these tokens. Callers should prefer producing tokens with _PrettyTokenType members (e.g., _PrettyTokenType.BODY) for the .type field.

_Motivation / responsibility boundary_
- Responsibility: hold exactly two pieces of data — the token's category (.type) and its text (.value) — and provide tuple-like and mapping-like utilities.
- Not responsible for validation beyond structural storage; it does not enforce runtime type checks or semantic validation of the value content.

## State:
Attributes (public, read-only)
- type ( _PrettyTokenType )
  - Description: The token category; must be one of the members of the internal enum _PrettyTokenType (for example _PrettyTokenType.BODY, _PrettyTokenType.NEWLINE, etc.).
  - Runtime characteristics: Stored as-is; Python's typing system records the intended type but runtime enforcement is not performed by NamedTuple. Comparisons against enum members should use equality (==) or identity (is) as appropriate; prefer comparing to the enum members directly.
  - Invariant: After construction, .type refers to the same object that was passed in (no automatic conversion).

- value ( str )
  - Description: The textual content of the token. May be any Python string (including empty string, strings with whitespace or newlines).
  - Runtime characteristics: No automatic trimming, escaping, or validation is performed by this class; those operations are the caller's responsibility.
  - Invariant: Stays immutable after construction.

Class invariants
- Instances are immutable: attempts to assign to .type or .value raise AttributeError.
- Instances behave as tuples of length 2 (index 0 = type, index 1 = value).
- The tuple-like ordering is fixed: index 0 corresponds to .type, index 1 to .value.

## Lifecycle:
Creation
- Constructor signatures:
  - Positional: _PrettyToken(type_value, text_value)
  - Keyword: _PrettyToken(type=type_value, value=text_value)
- Typical required arguments:
  - type: a _PrettyTokenType member (recommended). Passing another object is allowed at runtime but will not be type-checked; doing so may break downstream code that expects an enum member.
  - value: a str object. Passing non-str values is possible at runtime but likely to cause errors later when consumers expect string behavior.
- Alternate factory patterns:
  - Construct tokens in comprehension or helper functions in tokenizer code, e.g., _PrettyToken(_PrettyTokenType.BODY, 'raw text').

Usage
- Access fields:
  - Read .type and .value attributes directly (e.g., token.type, token.value).
  - Sequence access: token[0] (type), token[1] (value).
  - Unpack: type, value = token
- Utility methods (NamedTuple-provided):
  - token._asdict(): returns an OrderedDict mapping field names to values.
  - token._replace(**kwargs): returns a new _PrettyToken with specified fields replaced (does not mutate original).
  - _PrettyToken._make(iterable): classmethod-like constructor from an iterable with two items.
  - token._fields: tuple of field names ("type", "value").
- Common patterns:
  1. Token creation in tokenizer.
  2. Renderer inspects token.type to choose styling, then uses token.value as the text to render.
  3. To produce a modified token (e.g., change value), call token._replace(value=new_value) to obtain a new instance.
- Ordering / sequencing
  - There is no special method ordering required. Typical flow is: create → read-only consumption → optional replacement to create new token.

Destruction / cleanup
- No explicit cleanup is required. Instances hold references to contained objects (enum member and string); garbage collection applies normally. No context managers or close methods are provided.

## Method Map:
flowchart LR
    Create[Create _PrettyToken(type, value)]
    Create --> Access[Access .type / .value or index / unpack]
    Access --> Render[Renderer maps .type -> style and uses .value]
    Create --> AsDict[token._asdict() -> OrderedDict]
    Create --> Replace[token._replace(...) -> new _PrettyToken]
    Create --> Make[_PrettyToken._make(iterable) -> new _PrettyToken]
    Access --> Compare[Compare via == or use in sequences]
    Compare --> End((End))

## Raises:
Possible exceptions callers should expect from typical operations (these arise from standard NamedTuple / tuple behavior, not custom code in this class):
- TypeError
  - Trigger conditions:
    - Calling the constructor with the wrong number of arguments (too few or too many).
    - Passing unexpected keyword argument names to the constructor (e.g., _PrettyToken(badname=...)).
    - Using _PrettyToken._make with an iterable of length != 2.
- AttributeError
  - Trigger conditions:
    - Attempting to assign to a field (e.g., token.value = 'x') — NamedTuple fields are read-only.
- KeyError / ValueError: Not raised by this class directly; mentioned here only to clarify that converting from external strings to _PrettyTokenType members may raise ValueError/KeyError when callers attempt to derive .type from invalid enum names (this behavior belongs to _PrettyTokenType).

Notes on runtime typing
- The annotated types are for static typing (mypy, editors). At runtime, Python does not enforce the declared type annotations on NamedTuple fields; passing an incorrect runtime type will not raise during construction but may cause downstream failures.

## Example:
- Create a token (positional):
  - token = _PrettyToken(_PrettyTokenType.BODY, 'line text')
- Create a token (keywords):
  - token = _PrettyToken(type=_PrettyTokenType.LINENO, value='  42 ')
- Access and render:
  - if token.type is _PrettyTokenType.NEWLINE:
      handle_line_break()
    else:
      print(token.value)
- Modify value immutably:
  - new_token = token._replace(value=token.value.rstrip('\n'))
- Convert to mapping:
  - d = token._asdict()  # OrderedDict([('type', <_PrettyTokenType.BODY: 'BODY'>), ('value', '...')])
- Unpack:
  - t_type, t_value = token

(Refer to the _PrettyTokenType documentation for the set of valid enum members and their semantic meanings; always prefer using those members for .type rather than raw strings.)

## `onlinejudge_command.pretty_printers._optimize_tokens` · *function*

## Summary:
Merge adjacent tokens of the same category by concatenating their text content and return a new compacted token list.

## Description:
- Known callers within the provided codebase:
  - No direct callers were identified in the provided snippets. Typical callers inside the same pretty-printers module are tokenizers, renderers, formatters, or printer pipelines that build sequences of _PrettyToken instances and want to coalesce adjacent text of the same token type before rendering or diffing.
- Typical trigger / pipeline stage:
  - Run after a tokenizer or intermediate processing step that may produce multiple successive tokens of the same .type (for example, multiple BODY tokens split by earlier transformations). This function reduces those adjacent tokens into a single token per contiguous run to simplify downstream rendering and comparisons.
- Why this logic is extracted:
  - Responsibility boundary: encapsulates the simple, well-defined transformation "coalesce adjacent same-type tokens" so callers need not repeatedly reimplement merging logic. Keeps tokenization and rendering code focused on higher-level concerns and ensures a single, consistent merging behavior across the module.

## Args:
- tokens (List[_PrettyToken])
  - Type: list (or other sequence) of _PrettyToken-like objects (see _PrettyToken documentation).
  - Allowed values: any sequence whose elements expose .type and .value attributes.
  - Interdependencies / expectations:
    - The order of elements is significant and preserved.
    - .type values should be comparable for equality (usually members of the module's _PrettyTokenType enum).
    - .value values are expected to be strings (or otherwise support the + operator for concatenation). If .value are not string-like, concatenation may raise TypeError.

## Returns:
- List[_PrettyToken]:
  - A new list derived from the input where every maximal contiguous run of tokens that share the same .type is replaced by a single _PrettyToken whose .value is the concatenation (in original order) of the run's .value values.
  - Specific behaviors:
    - If the input list is empty, returns an empty list.
    - If a token has no adjacent token with the same .type, the same token object from the input list is appended to the result (i.e., identity is preserved for non-merged tokens).
    - When adjacent tokens are merged, a new _PrettyToken is constructed for the merged run; the original input objects are not mutated.
    - Non-adjacent tokens that share the same .type are not merged (only contiguous tokens are coalesced).

## Raises:
- The function does not explicitly raise application-specific exceptions.
- Possible runtime exceptions caused by invalid inputs:
  - AttributeError:
    - If an element in tokens lacks a .type or .value attribute, attribute access (optimized[-1].type or token.type) will raise AttributeError.
  - TypeError:
    - If the element .value objects cannot be concatenated using + (for example, int + str), the expression optimized[-1].value + token.value will raise TypeError.
  - Any exceptions thrown by the _PrettyToken constructor (e.g., unexpected constructor signature) will propagate.

## Constraints:
- Preconditions:
  - Caller should pass an iterable of objects that behave like _PrettyToken (have .type and .value).
  - The .value attributes should be concatenable (strings are the intended type).
- Postconditions:
  - Returned list contains no two adjacent tokens with the same .type.
  - The textual order of token values is preserved (concatenated in the same order they appeared).
  - Input list and its token objects are not mutated by this function (new list created; new _PrettyToken objects created only for merged runs).

## Side Effects:
- None on external state. The function:
  - Does not perform I/O (no files, network, or stdout).
  - Does not mutate global or external variables.
  - Only allocates a new list and, when merging, constructs new _PrettyToken instances. It does not modify the original tokens.

## Control Flow:
flowchart TD
    Start([Start]) --> Init{optimized = []}
    Init --> ForEach[For each token in tokens]
    ForEach --> CheckEmpty{optimized is empty?}
    CheckEmpty -->|Yes| AppendFirst[append token to optimized]
    CheckEmpty -->|No| SameType?{optimized[-1].type == token.type}
    SameType? -->|Yes| Merge[create new _PrettyToken(type, optimized[-1].value + token.value) and replace optimized[-1]]
    SameType? -->|No| Append[append token to optimized]
    AppendFirst --> ForEach
    Merge --> ForEach
    Append --> ForEach
    ForEach --> End([Return optimized])

## Examples:
- Example 1 — simple merge:
  - Input (conceptual): [B:'hello ', B:'world', N:'\n', B:'x']
  - Output: [B:'hello world', N:'\n', B:'x']
  - Explanation: first two BODY (B) tokens are adjacent and merged by concatenating their .value strings.

- Example 2 — empty and single-element inputs:
  - Input: []
  - Output: []
  - Input: [L:'only']
  - Output: [L:'only']  (the same object is appended; no merging occurs)

- Example 3 — identical types separated by other types are not merged:
  - Input: [B:'a', N:'\n', B:'b']
  - Output: [B:'a', N:'\n', B:'b']  (the B tokens are not adjacent)

- Example 4 — invalid .value types:
  - If a token's .value is an int (e.g., 3) and it appears adjacent to a token whose .value is a string, concatenation will raise TypeError. Callers should ensure .value are strings.
  - Defensive usage pattern:
    - Validate or normalize token values to strings before calling this function, or wrap the call in try/except to catch TypeError/AttributeError when inputs may be malformed.

## Implementation notes (for reimplementation):
- Iterate tokens in order, maintain a result list `optimized`.
- For each token:
  - If `optimized` is non-empty and optimized[-1].type == token.type:
    - Replace optimized[-1] with a new token whose type is token.type and value is optimized[-1].value + token.value.
  - Else:
    - Append the current token object to optimized.
- Return optimized.

## `onlinejudge_command.pretty_printers._tokenize_str` · *function*

## Summary:
Split a string-like input into a list of typed tokens where each token represents a maximal contiguous run of either space/tab characters or non-space/tab characters; tokens produced use the enum members WHITESPACE (for runs of spaces/tabs) and BODY (for all other characters).

## Description:
Known callers:
- Tokenizers, renderers, diffing and printing utilities inside the pretty-printers module that need a simple, tokenized representation of a single line or fragment for coloring, alignment, diff computation, or highlighting. It is typically called as an early stage to convert raw text into _PrettyToken sequences consumed by formatters and output printers.

Why this logic is extracted:
- Responsibility boundary: centralizes the single concern of grouping adjacent characters by whether they are a space or a tab (these two characters are classified as whitespace here). Higher-level code can then operate on typed tokens (WHITESPACE vs BODY) without repeating the grouping logic.
- Note on enum usage: The module-wide enum _PrettyTokenType contains many members (e.g., BODY_HIGHLIGHT_LEFT, NEWLINE, LINENO). This function, however, only assigns _PrettyTokenType.WHITESPACE or _PrettyTokenType.BODY. Callers that require other token types (for example, to represent explicit newlines or highlighted spans) should post-process or use other helper/tokenizer functions in the module.

## Args:
    s (str-like): Input text to tokenize.
        - Expected and recommended type: str. When s is a str, token.value will be a Python str substring.
        - Allowed contents: any sequence type that supports len(), integer indexing, and slicing (s[l:r]). If s is not a str but supports these operations, this function will still produce tokens whose .value equals s[l:r] (which will be of the same sequence type as s slices).
        - Classification rule: only ' ' (space) and '\t' (tab) are considered WHITESPACE here; other Unicode whitespace characters (e.g., '\n', '\r', '\v', '\f') are treated as BODY characters.

## Returns:
    list[_PrettyToken]: A list of _PrettyToken instances representing consecutive maximal runs in the input.
    - For each token:
        - .type is set to either:
            - _PrettyTokenType.WHITESPACE for runs consisting solely of characters in the set {' ', '\t'}
            - _PrettyTokenType.BODY for runs consisting of all other characters
        - .value is the slice s[l:r] corresponding to that run (non-empty).
    - Guarantees and edge cases:
        - Reconstruction: ''.join(str(token.value) for token in result) == str(s) is true when s is a str; for non-str sequence inputs, concatenating token.value will re-create s in that sequence type.
        - Maximality: adjacent tokens always have different .type (i.e., runs are maximal under the predicate (char in ' \t')).
        - Empty input: if s == '' (or len(s) == 0), returns [].
        - Newline handling: the function does not emit a distinct NEWLINE token; '\n' is treated as BODY.

## Raises:
    TypeError:
        - If s does not support len() or indexing (for example, passing None). The implementation performs len(s) and s[i] operations; objects lacking these will raise TypeError.
    IndexError / other exceptions:
        - Unusual sequence-like objects with custom indexing/slicing logic might raise their own exceptions during slicing or indexing; those exceptions will propagate.
    (No custom exceptions are raised by this function for valid sequence inputs.)

## Constraints:
Preconditions:
    - Prefer providing a str for s. If a non-str sequence is passed, callers should be aware that token.value will be slices of that sequence (not necessarily str), which may affect downstream code that expects string behavior.

Postconditions:
    - The returned list contains zero or more _PrettyToken instances whose concatenated values reproduce the input.
    - Each token.value is non-empty and corresponds to a contiguous slice of the original input.
    - Token types are limited (for this function) to WHITESPACE and BODY.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or the input.

## Control Flow:
flowchart TD
    Start((Start))
    Start --> CheckLen{l < len(s)?}
    CheckLen -- No --> End((Return tokens))
    CheckLen -- Yes --> InitR[set r = l + 1]
    InitR --> CompareChar{r < len(s) and (s[l] in ' \\t') == (s[r] in ' \\t')?}
    CompareChar -- Yes --> IncR[ r = r + 1 ] --> CompareChar
    CompareChar -- No --> DecideType{is s[l] in ' \\t'?}
    DecideType -- Yes --> TypWH[typ = _PrettyTokenType.WHITESPACE]
    DecideType -- No --> TypBody[typ = _PrettyTokenType.BODY]
    TypWH --> Append[append _PrettyToken(typ, s[l:r])]
    TypBody --> Append
    Append --> Advance[ l = r ] --> CheckLen

## Examples:
1) Typical (str input):
    - Input: s = "  abc\tdef"
    - Output:
        [
          _PrettyToken(_PrettyTokenType.WHITESPACE, "  "),
          _PrettyToken(_PrettyTokenType.BODY, "abc"),
          _PrettyToken(_PrettyTokenType.WHITESPACE, "\t"),
          _PrettyToken(_PrettyTokenType.BODY, "def"),
        ]

2) Empty string:
    - Input: s = ""
    - Output: []

3) Newlines:
    - Input: s = "a\nb"
    - Output:
        [
          _PrettyToken(_PrettyTokenType.BODY, "a\nb")
        ]
      (Because '\n' is not in the set {' ', '\t'} and therefore remains part of a BODY run.)

4) Non-str sequence:
    - If s is a list-like sequence that supports slicing (e.g., a custom sequence), token.value items will be slices of that sequence. Downstream consumers expecting str should avoid passing non-str sequences or must handle non-str token.value appropriately.

5) Incorrect usage:
    - Calling with None: raises TypeError when computing len(None) or indexing None; catch TypeError to detect misuse.

## `onlinejudge_command.pretty_printers._tokenize_line` · *function*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._decode_with_recovery` · *function*

## Summary:
Attempt to decode raw bytes to a Unicode string and return any decoding diagnostic as a single HINT token; if decoding fails, return a best-effort text using replacement characters.

## Description:
This helper encapsulates a safe decode-with-recovery pattern used by pretty-printer logic that must present or process textual data coming from external sources (files, subprocess output, network). It performs a normal decode (using Python's default encoding) and, if a UnicodeDecodeError occurs, records a diagnostic _PrettyToken of type _PrettyTokenType.HINT containing the exception message, then returns a fallback string decoded with errors='replace'.

Known callers in this repository snapshot:
- No direct callers were found in the provided code snapshot. Typical callers are tokenizers and rendering functions within onlinejudge_command.pretty_printers that receive raw bytes (for example, when reading a file or capturing process output) and need both a safe str to operate on and any user-facing hint about decoding problems.

Why this function exists:
- Centralizes decode-and-diagnose behavior so that callers receive a consistent, safe string plus structured diagnostic tokens they can render to users or log.
- Keeps decoding fallback policy (strict first, then errors='replace') in one place so presentation logic does not duplicate error-handling code.

## Args:
    content (bytes): Raw input bytes to decode.
        - Expected type: bytes (or any object with a robust .decode method such as bytearray). The function signature requires bytes; callers are expected to pass bytes.
        - No default. Passing other types is not supported by the contract and may allow exceptions to propagate.

## Returns:
    Tuple[List[_PrettyToken], str]
    - tokens: A list containing zero or one _PrettyToken.
        - [] (empty list) when content.decode() succeeds.
        - [_PrettyToken(_PrettyTokenType.HINT, message)] when a UnicodeDecodeError was raised by the initial decode. The message is str(e) where e is the caught UnicodeDecodeError (for example: " 'utf-8' codec can't decode byte 0xff in position 12: invalid start byte").
    - text: A Python str with the decoded content.
        - On success: the result of content.decode() using the default encoding (explicitly, Python's bytes.decode default encoding is 'utf-8' and errors='strict').
        - On UnicodeDecodeError: the result of content.decode(errors='replace'), where invalid byte sequences are substituted (commonly with U+FFFD, the replacement character), ensuring a valid str is always returned.

## Raises:
    - UnicodeDecodeError: This exception is caught internally and will not propagate as part of normal operation.
    - AttributeError: If the provided `content` does not have a callable .decode attribute (e.g., passing an integer or other non-bytes without decode), attribute access will fail and AttributeError may propagate.
    - TypeError: If `content.decode()` raises TypeError for some non-standard object, that TypeError will propagate.
    - Any other exceptions raised by non-bytes inputs may propagate; callers should ensure they pass a bytes-like object when they want the documented behavior.

## Constraints:
Preconditions:
    - The caller should provide bytes (or a bytearray) when expecting the documented decode/recovery behavior.
Postconditions:
    - The function always returns a str as the second tuple element.
    - The tokens list length is 0 or 1. If 1, the single token is a HINT with the UnicodeDecodeError message.

## Side Effects:
    - None. The function does not perform I/O, mutate global state, or call external services. It allocates in-memory objects (a list, and possibly a _PrettyToken and a str) and returns them.

## Control Flow:
flowchart TD
    Start((Start))
    Start --> TryDecode[Try: text = content.decode()]
    TryDecode -->|success| ReturnSuccess[Return tokens = [], text]
    TryDecode -->|UnicodeDecodeError e| AppendHint[Append _PrettyToken(_PrettyTokenType.HINT, str(e))]
    AppendHint --> FallbackDecode[text = content.decode(errors='replace')]
    FallbackDecode --> ReturnError[Return tokens = [HINT token], text]
    ReturnSuccess --> End((End))
    ReturnError --> End

## Examples:
1) Successful decode
    - Input: content = b'Hello\\n'
    - Behavior: content.decode() succeeds.
    - Output: tokens == [] ; text == 'Hello\\n'

2) Recovery on invalid byte sequences
    - Input: content = b'Line1\\n\\xff\\nLine3'
    - Behavior:
        - Initial decode raises UnicodeDecodeError.
        - tokens == [_PrettyToken(_PrettyTokenType.HINT, "<UnicodeDecodeError message>")]
        - text == 'Line1\\n�\\nLine3' (invalid bytes replaced with U+FFFD or an encoding-specific replacement)
    - Caller pattern:
        - tokens, text = _decode_with_recovery(content)
        - If tokens: render the HINT token (e.g., as a colored warning) before rendering `text`.

3) Non-bytes input (incorrect usage)
    - Input: content = 12345
    - Behavior:
        - Attempting to call content.decode() raises AttributeError; this exception propagates.
    - Caller guidance:
        - Validate or convert inputs to bytes before calling this helper to avoid propagated exceptions.

Notes:
- The function deliberately does not attempt encoding detection (e.g., chardet) or alternative recovery heuristics; it focuses on a simple fail-then-replace strategy and emitting a brief diagnostic suitable for user display.
- The exact text of the UnicodeDecodeError message depends on Python's codec error formatting and will typically indicate codec name, byte position, and the reason (e.g., "invalid start byte").

## `onlinejudge_command.pretty_printers._warn_if_empty` · *function*

## Summary:
Ensure a visible hint token is present when a token sequence is empty, ends without a trailing newline, or consists solely of newline tokens; returns the (possibly mutated) token sequence with appended hint tokens as needed.

## Description:
- Known callers / context:
  - Internal callers inside the pretty-printers module that prepare or render sequences of _PrettyToken values for terminal or textual output. Typical call site: immediately after tokenizing a string or diff into a list of _PrettyToken, before rendering those tokens to the user; used to make special-case empty/whitespace-only inputs explicit to viewers.
  - Typical trigger conditions: called after tokenization of a file, program output, or expected output so that completely empty output, output that lacks a trailing newline, or output that is only newline tokens will display a human-readable hint.

- Why this is a separate function:
  - Responsibility boundary: centralizes the small but subtle rule-set that adds human-friendly HINT tokens describing three distinct situations (empty input, missing trailing newline, only-newline content). Extracting this logic avoids duplicating the conditional checks and clarifies that the function's sole job is to ensure appropriate hints exist; callers can depend on its consistent, documented behavior rather than inlining the same checks in multiple places.

## Args:
    tokens (List[_PrettyToken]):
        - A mutable sequence (expected to be a list) of _PrettyToken instances representing tokenized text.
        - Required properties: supports truthiness testing, indexing (tokens[-1]), iteration, and an append(item) operation.
        - Semantic expectation: each element is a _PrettyToken whose .type is a member of _PrettyTokenType (e.g., _PrettyTokenType.BODY, _PrettyTokenType.NEWLINE, _PrettyTokenType.HINT).
        - Note: Passing a non-list sequence (e.g., tuple) that lacks append will cause an error when the function attempts to append. Passing elements that are not _PrettyToken can cause AttributeError or IndexError during checks.

## Returns:
    List[_PrettyToken]:
        - The token sequence after ensuring relevant HINT tokens are present.
        - For non-empty input, the function appends to the passed-in list and returns the same list object (mutated in place).
        - For an empty input (falsy sequence), the function returns a newly created list containing a single hint token: _PrettyToken(_PrettyTokenType.HINT, '(empty)') — the original object passed as tokens is not mutated in this branch.
        - Possible return shapes:
            * Empty input: new list -> [HINT('(empty)')]
            * Non-empty input where last token type is BODY: original list with appended HINT('(no trailing newline)')
            * Non-empty input where all token.type == NEWLINE: original list with appended HINT('(only newline)')
            * Otherwise: original list, unchanged except possibly for appended hints depending on conditions.

## Raises:
    - No exceptions are explicitly raised by the function for correctly-typed inputs.
    - If preconditions are violated, the underlying operations may raise:
        * AttributeError: if an element lacks a .type attribute (the all(...) check uses token.type).
        * IndexError: if an element does not support indexing and the code attempts tokens[-1][0], or if a token-like element is shorter than expected when indexed.
        * AttributeError: if the provided tokens sequence does not have an append method (e.g., tuple) and the code reaches a branch that attempts tokens.append(...).
    - These exceptions reflect misuse (wrong argument shape or element types) rather than intended behavior; callers should pass a mutable list of _PrettyToken.

## Constraints:
- Preconditions:
    - tokens should be a mutable sequence (a Python list is intended) containing _PrettyToken instances.
    - Each token should provide either tuple-like indexing (token[0] returns the type) or a .type attribute (the function uses both forms in different checks). Specifically, tokens[-1][0] is used to read the last token's type; the generator expression uses token.type for each token.
- Postconditions:
    - The returned sequence will contain additional trailing HINT tokens if and only if the input matched one of the checked situations.
    - If the input was empty, the returned list is a fresh list containing a single HINT('(empty)') token; otherwise the original list object is returned (possibly mutated by appending one HINT token).
    - The function does not remove or reorder existing tokens — it only appends zero or one hint tokens (one for the BODY/no-trailing-newline case, one for the only-newline case). Note: because the BODY and all-NEWLINE conditions are mutually exclusive for well-typed tokens, at most one hint will be appended in typical correct use.

## Side Effects:
    - Mutates input: When tokens is a non-empty mutable list, the function may append one extra _PrettyToken to that list (in-place mutation).
    - No I/O is performed.
    - No global state, files, network calls, or external services are touched.

## Control Flow:
flowchart TD
    Start((Start))
    Start --> CheckEmpty{tokens is falsy?}
    CheckEmpty -->|Yes| ReturnEmpty[Return [HINT('(empty)')]]
    CheckEmpty -->|No| CheckLastBody{last token's type == BODY?}
    CheckLastBody -->|Yes| AppendNoTrailing[append HINT('(no trailing newline)')]
    CheckLastBody -->|No| SkipNoTrailing[skip]
    AppendNoTrailing --> CheckAllNewline
    SkipNoTrailing --> CheckAllNewline
    CheckAllNewline{all token.type == NEWLINE?}
    CheckAllNewline -->|Yes| AppendOnlyNewline[append HINT('(only newline)')]
    CheckAllNewline -->|No| SkipOnlyNewline[skip]
    AppendOnlyNewline --> ReturnMutated[return tokens (mutated)]
    SkipOnlyNewline --> ReturnMutated

## Examples:
- Example 1: Empty input
    - Input: tokens = []
    - Behavior: function returns a new list [ _PrettyToken(_PrettyTokenType.HINT, '(empty)') ]
    - Note: original tokens (the empty list) is not modified by this call.

- Example 2: Single body token without trailing newline
    - Input: tokens = [ _PrettyToken(_PrettyTokenType.BODY, 'line') ]
    - Behavior: tokens is mutated in-place to:
        [ _PrettyToken(_PrettyTokenType.BODY, 'line'),
          _PrettyToken(_PrettyTokenType.HINT, '(no trailing newline)') ]
      and the same list object is returned.

- Example 3: Only newline tokens
    - Input: tokens = [ _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
                        _PrettyToken(_PrettyTokenType.NEWLINE, '\n') ]
    - Behavior: tokens is mutated in-place to append the hint:
        ... , _PrettyToken(_PrettyTokenType.HINT, '(only newline)')
      and the same list object is returned.

- Example 4: Caller responsibilities / error handling
    - If a caller passes a tuple instead of a list, e.g., tokens = tuple(...), then when the function attempts to append a hint it will raise AttributeError because tuples lack append. To avoid this, callers should pass a mutable list (or other append-capable sequence) and elements must be _PrettyToken instances.

## `onlinejudge_command.pretty_printers._tokenize_large_file_content` · *function*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._replace_whitespace` · *function*

## Summary:
Converts three whitespace characters in a string into visible, printable tokens so whitespace differences are unambiguous when displayed.

## Description:
This small utility maps:
- spaces (' ') to underscore characters ('_'),
- tab characters ('\t') to the two-character sequence backslash + 't' ("\\t"),
- carriage-return characters ('\r') to the two-character sequence backslash + 'r' ("\\r").

Known callers:
- No direct call sites were discovered in the code-graph returned for this repository. The function is defined in the pretty_printers module and is intended for internal use when producing human-readable output (for example, preparing strings for printing in diffs, diagnostics, or debugging text where invisible whitespace would obscure differences).

Why this is a separate function:
- The logic is small but semantically focused: it encapsulates the exact mapping used to make whitespace visible. Extracting it as a separate function centralizes the mapping (single place to change the representation) and keeps printing / formatting code concise and readable.

## Args:
    s (str): Input text to transform.
        - Expected type: str.
        - Allowed values: any Python string (including empty string).
        - Interdependencies: none.

## Returns:
    str: A new string with the following transformations applied (in order):
        - every space character ' ' replaced by underscore '_';
        - every tab character '\t' replaced by the two-character sequence '\\t';
        - every carriage return '\r' replaced by the two-character sequence '\\r'.
    Edge-case returns:
        - Passing an empty string returns an empty string.
        - Strings that contain newline characters ('\n') are not changed for newlines; those remain present in the returned string.

## Raises:
    - AttributeError: If the supplied argument `s` does not provide a replace method (e.g., passing None or an object without a replace method). This behavior is an immediate consequence of calling the string replace method on the argument.
    - Note: The function signature annotates `s` as str; callers should pass strings to avoid runtime errors.

## Constraints:
    Preconditions:
        - The caller should pass a string-like object (ideally an instance of str).
        - The function expects and treats characters literally; it does not parse escape sequences in source code literals beyond normal Python string semantics.
    Postconditions:
        - The returned string contains no literal space characters ' ', no tab characters '\t', and no carriage-return characters '\r' — each has been replaced as described above.
        - The function does not alter other characters or introduce newline characters.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state or its input. It returns a new string.

## Control Flow:
flowchart TD
    A[Start: receive s] --> B{Has replace method? (s behaves like str)}
    B -- Yes --> C[Replace ' ' with '_']
    C --> D[Replace '\t' with '\\t']
    D --> E[Replace '\r' with '\\r']
    E --> F[Return transformed string]
    B -- No --> G[AttributeError raised when attempting .replace]
    G --> H[Caller receives exception]

## Examples:
- Basic usage:
    Input: "a b\tc\r\nd"
    Processed: spaces -> underscores, tabs -> "\\t", carriage returns -> "\\r"
    Result: "a_b\\tc\\r\nd"

- Empty string:
    Input: ""
    Result: ""

- Idempotence note:
    Running the function on its own output is safe and will not reintroduce space, tab, or carriage-return characters (the replacements are literal backslash sequences that the function does not replace again).

- Defensive usage with runtime type checking:
    When receiving input of unknown type, validate before calling:
    - Example pattern: if not isinstance(s, str): raise TypeError("expected str") before calling the function to avoid AttributeError at runtime.

## `onlinejudge_command.pretty_printers._render_tokens` · *function*

## Summary:
Convert a sequence of typed text fragments into a single formatted string by mapping each token type to an appropriate font/formatter and concatenating the results.

## Description:
This function accepts a sequence of tokens produced by the module's tokenization logic and renders them into a single human-readable string where each token's textual value is transformed according to its category (body, whitespace, newline, highlight, hint, line number, etc.). The transformed tokens are concatenated in order and returned.

Known callers within the codebase:
- No direct call sites were discovered by the repository-wide search available during documentation generation. Typical callers are other functions in the pretty-printers module that:
  - produce token sequences from raw text or diffs, and
  - then delegate presentation to _render_tokens to produce the final colored/annotated string for display in the terminal or logs.

Why this logic is extracted into its own function:
- Responsibility separation: tokenization (splitting and categorizing text) and rendering (deciding visual styling for each category) are distinct concerns. Extracting rendering allows tokenizers and diff-formatters to remain focused on structure while reusing a single, consistent rendering strategy.
- Reusability and testability: rendering behavior (including color and whitespace visualization) is centralized so it can be consistently changed, tested, and overridden via the font_* callables without editing tokenization code.
- Customization: callers can override font functions to control styling without duplicating mapping logic.

## Args:
    tokens (List[Tuple[_PrettyTokenType, str]]):
        - Required.
        - A sequence (list/iterable) of 2-tuples where:
            * the first element is a member of _PrettyTokenType (e.g., BODY, WHITESPACE, NEWLINE, LINENO, BODY_HIGHLIGHT_LEFT, BODY_HIGHLIGHT_RIGHT, HINT, OTHERS).
            * the second element is the string value to render for that token.
        - Each value must be a str; otherwise runtime errors may occur when styling functions concatenate or manipulate the value.
    font_bold (Optional[Callable[[str], str]]):
        - Optional. A function that takes a string and returns a styled string for BODY tokens.
        - Default: wraps the string with colorama.Style.BRIGHT and colorama.Style.RESET_ALL.
    font_dim (Optional[Callable[[str], str]]):
        - Optional. A function used for WHITESPACE, NEWLINE, and HINT tokens.
        - Default: wraps the string with colorama.Style.DIM and colorama.Style.RESET_ALL.
        - Note: for WHITESPACE and NEWLINE the token text is first transformed with _replace_whitespace before being handed to this callable.
    font_red (Optional[Callable[[str], str]]):
        - Optional. A function used for BODY_HIGHLIGHT_LEFT and BODY_HIGHLIGHT_RIGHT tokens.
        - Default: wraps the string with colorama.Fore.RED and colorama.Style.RESET_ALL.
    font_blue (Optional[Callable[[str], str]]):
        - Optional. A function used for LINENO tokens.
        - Default: wraps the string with colorama.Fore.CYAN and colorama.Style.RESET_ALL.
    font_normal (Optional[Callable[[str], str]]):
        - Optional. A fallback function used for OTHERS tokens.
        - Default: identity function (returns the input string unchanged).

Interdependencies:
- The tokens' first element must be one of the recognized _PrettyTokenType members; unknown token keys trigger an assertion failure.
- All font_* parameters must be callables accepting a single str and returning a str; otherwise calls will raise at runtime.

## Returns:
    str: A single string that is the concatenation of the rendered token values in the order of the input sequence.
    - Normal result: a string possibly containing ANSI escape sequences (when default colorama-based font functions are used) and visible representations of whitespace/newline tokens (because _replace_whitespace is applied to WHITESPACE and NEWLINE token values).
    - Edge-case returns:
        * An empty list of tokens yields an empty string.
        * If token values are empty strings, they contribute nothing to the final concatenation but do not cause errors.

## Raises:
    AssertionError:
        - If a token's key is not one of the expected _PrettyTokenType members, the function hits the final else branch and raises AssertionError (from assert False).
    TypeError or runtime errors from font callables:
        - If a provided font_* value is not callable, or a font callable expects a different type, calling it may raise TypeError or other exceptions.
    Errors from _replace_whitespace:
        - _replace_whitespace expects a str; passing a non-string token value may raise an AttributeError when replace is invoked. (The function's signature documents str for token values.)

## Constraints:
Preconditions:
    - tokens is an iterable of 2-tuples (token_type, token_text).
    - token_type must be a member of _PrettyTokenType.
    - token_text must be a str (or convertible to str by the caller before passing).
    - font_* arguments, if provided, must be callables mapping str -> str.

Postconditions:
    - The returned value is a str and is the concatenation of per-token outputs returned by the chosen font functions (after any token-specific preprocessing such as _replace_whitespace).
    - The function does not modify the input tokens sequence.
    - No file, network, or external state is changed by this function.

## Side Effects:
    - None intrinsic: the function performs no I/O, does not mutate global state, and does not write to files or network.
    - If default font functions are used they produce strings containing ANSI escape sequences (colorama values); emitting those strings to a terminal may change terminal appearance but this function itself only returns the string.
    - Custom font callables provided by callers may perform side effects; those are outside the function's control.

## Control Flow:
flowchart TD
    Start([Start]) --> Init{Are font_* provided?}
    Init -- No --> SetDefaults[Assign default colorama-based font functions and identity]
    Init -- Yes --> UseProvided[Use provided font functions as-is]
    SetDefaults --> Loop
    UseProvided --> Loop
    Loop[For each (key, value) in tokens:] --> CheckTokenType{key is which _PrettyTokenType?}
    CheckTokenType --> BODY[If BODY -> call font_bold(value)]
    CheckTokenType --> BODY_HL_L[If BODY_HIGHLIGHT_LEFT -> call font_red(value)]
    CheckTokenType --> BODY_HL_R[If BODY_HIGHLIGHT_RIGHT -> call font_red(value)]
    CheckTokenType --> WHITESPACE[If WHITESPACE -> transformed = _replace_whitespace(value); call font_dim(transformed)]
    CheckTokenType --> NEWLINE[If NEWLINE -> transformed = _replace_whitespace(value); call font_dim(transformed)]
    CheckTokenType --> HINT[If HINT -> call font_dim(value)]
    CheckTokenType --> LINENO[If LINENO -> call font_blue(value)]
    CheckTokenType --> OTHERS[If OTHERS -> call font_normal(value)]
    CheckTokenType --> Unknown[Else -> assert False -> AssertionError]
    BODY --> Append[Append to result list]
    BODY_HL_L --> Append
    BODY_HL_R --> Append
    WHITESPACE --> Append
    NEWLINE --> Append
    HINT --> Append
    LINENO --> Append
    OTHERS --> Append
    Append --> Loop
    Loop --> Join[After loop: join result list into a single string]
    Join --> End([Return the joined string])

## Examples:
1) Basic rendering (conceptual example showing inputs and output form):
    - Input tokens:
        [(_PrettyTokenType.LINENO, " 1 "), (_PrettyTokenType.BODY, "answer"), (_PrettyTokenType.NEWLINE, "\n")]
    - Using default fonts:
        * The lineno token text is wrapped with cyan foreground and reset.
        * The body token text is made bright.
        * The newline token is converted with _replace_whitespace ("\n" remains "\n", carriage returns/tabs/spaces within the token would be made visible) and dimmed.
    - Output: a single string that, when printed to a terminal that supports ANSI sequences, shows the line number in cyan, the answer in bright style, and the newline/dim style applied to the newline token.

2) Custom fonts example (error-tolerant usage pattern):
    - If a caller wants plain markers instead of ANSI colors, they can pass simple formatting callables that surround the text:
        * font_bold = lambda s: "[B]" + s + "[/B]"
        * font_red = lambda s: "[R]" + s + "[/R]"
        * font_dim = lambda s: "[D]" + s + "[/D]"
    - Then the same tokens as above will be rendered into a string containing those markers in place of ANSI escapes.
    - Error handling advice: validate that token values are strings and that provided font_* arguments are callables before calling to avoid TypeError/AttributeError at runtime.

Notes:
- Because the function asserts on unknown token keys, it acts as a safeguard that ensures the tokenization and rendering layers agree on the set of token types; encountering an unknown token typically indicates a bug in token creation or in a mismatch between tokenizer and renderer.
- For whitelisting or safe rendering of untrusted data, callers should ensure token_text values are safe to include in terminal output (e.g., avoid embedding control sequences) before passing to _render_tokens.

## `onlinejudge_command.pretty_printers._get_terminal_size` · *function*

## Summary:
Return a robust terminal width (number of character columns) for formatting console output, enforcing a minimum of 40 columns.

## Description:
This small utility queries the operating environment for the current terminal size and returns a single integer representing the number of character columns to use for layout decisions (wrapping, alignment, columnar printing).

Known callers within the codebase:
- No explicit callers were discovered in the provided source snapshot. Typical callers are pretty-printer and formatting routines inside the pretty_printers module that need a numeric width to compute wrap points or column widths before rendering output to stdout.

Why this logic is extracted into its own function:
- Encapsulates environment querying and the fallback policy ("use system terminal width but never less than 40") in one place so all formatting code uses a consistent width and does not duplicate the fallback logic. This separation also allows easy testing and future adjustments to the minimum width policy without changing callers.

Notes from the implementation:
- The original implementation includes the rationale that shutil.get_terminal_size() may return too-small values on some CI environments (for example, (0, 0) on Circle CI), so the function enforces a sane lower bound rather than relying on any shutil fallback.

## Args:
- None

## Returns:
- int: The number of character columns to be used for formatting output.
  - Typical return: the first element (columns) from shutil.get_terminal_size().
  - Edge-case / fallback: if the detected column count is less than 40 (including 0), the function returns 40.
  - Guarantee: the return value is always an integer >= 40.

## Raises:
- Propagates any exception raised by shutil.get_terminal_size().
  - The function performs no internal exception handling; callers that need a strict failure mode must call shutil.get_terminal_size() directly and handle exceptions themselves.

## Constraints:
- Preconditions:
  - None required of the caller. The function may be invoked in any normal runtime context where shutil.get_terminal_size() is available.
- Postconditions:
  - Returned value is an int and is >= 40.

## Side Effects:
- None visible to Python code: the function does not write files, network calls, stdout/stderr output, or mutate global variables.
- It does perform a single system/OS query via shutil.get_terminal_size() to obtain terminal dimensions.

## Control Flow:
flowchart TD
    Start --> CallGetSize[call shutil.get_terminal_size()]
    CallGetSize --> Extract[extract columns as char_in_line]
    Extract --> Check{char_in_line >= 40?}
    Check -->|yes| ReturnCols[return char_in_line]
    Check -->|no| Return40[return 40]
    ReturnCols --> End[End]
    Return40 --> End

## Examples and usage guidance:
- Typical usage (described in prose):
  - A pretty-printer that formats multiple output blocks should call this helper to obtain a stable width value and then pass that width to its wrapping/column computation routines.
  - If the formatting pipeline prints many items, call this helper once and reuse (cache) the returned value rather than calling it repeatedly, since terminal size is usually constant for the lifetime of a command and caching avoids redundant system queries.

- Error-handling guidance:
  - If the caller requires treating inability to query terminal size as an error (instead of using the enforced minimum), call shutil.get_terminal_size() directly and handle any exceptions raised there. This helper intentionally does not swallow exceptions so callers retain control over error semantics.

- Rationale for the 40-column minimum:
  - Prevents unreadably narrow layouts when the environment reports an implausibly small width (common on some CI systems). The implementation comment specifically notes an observed (0, 0) return value on Circle CI as motivation for the safe lower bound.

## `onlinejudge_command.pretty_printers.make_pretty_large_file_content` · *function*

## Summary:
Orchestrates pretty-printing of a (potentially large) binary file content by choosing a terminal width, tokenizing the content with truncation parameters, and rendering those tokens into a final formatted string.

## Description:
This function performs three sequential steps:
1. Queries the current terminal width via the module helper to determine characters-per-line for layout.
2. Delegates to the tokenization helper to split/categorize the raw bytes into presentation tokens while applying truncation/limiting behavior (limit, head, tail) using the computed width.
3. Delegates to the rendering helper to convert the token sequence into a final string (possibly containing ANSI color/formatting escapes) suitable for printing to a terminal.

Known callers:
- No direct callers were discovered in the provided source snapshot. Typical callers are CLI-facing pretty-printer routines or test helpers that need a human-friendly representation of large expected/actual file contents (for example, when displaying truncated diffs or sample outputs in the command-line tool).

Why this is a separate function:
- Encapsulates the common "terminal-aware pretty-print" pipeline so callers need only provide content and truncation parameters. The function hides the details of obtaining a terminal width and the two-step tokenize→render pipeline, making call sites simpler and keeping the responsibility boundary clear: decide parameters and ask for a fully formatted string.

## Args:
    content (bytes):
        - Required. Raw file content as a bytes object.
        - The function passes this value unchanged to the tokenizer; the tokenizer is responsible for decoding, line-splitting, and producing tokens.
    limit (int):
        - Required. An integer controlling overall size-limiting/truncation behavior.
        - The exact semantics (e.g., bytes vs. characters, whether it is a hard cap) are implemented by the tokenizer; this function only forwards the value.
    head (int):
        - Required. Number of leading lines/units to keep when truncation occurs; semantics are governed by the tokenizer.
    tail (int):
        - Required. Number of trailing lines/units to keep when truncation occurs; semantics are governed by the tokenizer.

Interdependencies:
- The values limit, head, and tail are forwarded untouched to the tokenizer. Their meaning and valid ranges are those required by _tokenize_large_file_content. Callers should ensure these are non-negative integers; passing incompatible types or negative values may cause errors in the tokenizer.

## Returns:
    str:
        - A single formatted string produced by rendering the token sequence returned from the tokenizer.
        - The string may include ANSI escape sequences when default color/font functions are used.
        - Edge cases:
            * If the tokenizer returns an empty token sequence, the renderer will return an empty string.
            * The function does not perform any additional trimming or newline normalization beyond what the renderer produces.
        - Per the renderer's documentation, a successful call returns the concatenated string resulting from rendering the token sequence.

## Raises:
    - This function does not catch exceptions raised by its helpers; exceptions from those helpers will propagate to the caller.
    - Exceptions may originate from:
        * _get_terminal_size (for example, if shutil.get_terminal_size raises).
        * _tokenize_large_file_content (e.g., for invalid argument types or internal tokenization errors).
        * _render_tokens or any font callables it invokes (see _render_tokens documentation for specific exception types).
    - Callers who need to present user-friendly errors should catch and map these exceptions at a higher level.

## Constraints:
Preconditions:
    - content must be a bytes object; otherwise the tokenizer may raise.
    - limit, head, tail must be integers (preferably non-negative); otherwise the tokenizer may raise or behave unexpectedly.
    - The runtime environment must allow querying terminal size (shutil.get_terminal_size used by the terminal-size helper); failures from that call will propagate.

Postconditions:
    - Returns a str that is the rendering of the token sequence created by the tokenizer for the provided content and truncation parameters, formatted to the terminal width used at the time of the call.
    - No global state is modified by this function.

## Side Effects:
    - The function itself performs a single OS query for terminal dimensions (via _get_terminal_size) but does not perform any I/O such as printing, file access, or network calls.
    - The renderer this function calls (_render_tokens) returns a string and, according to its documentation, does not perform file/network I/O nor mutate global state; it simply converts tokens to a string.
    - However, if the renderer invokes user-provided font callables (custom styling functions), those callables may perform side effects — such side effects are outside the control of this orchestration function and are the caller's responsibility.

## Control Flow:
flowchart TD
    Start --> GetWidth[_get_terminal_size()]
    GetWidth --> Tokenize[_tokenize_large_file_content(content, limit, head, tail, char_in_line)]
    Tokenize --> Render[_render_tokens(tokens)]
    Render --> Return[return rendered string]
    Return --> End

## Examples:
1) Basic usage (happy path):
    - Inputs:
        * content = b"line1\nline2\nline3\n"
        * limit = 1000
        * head = 3
        * tail = 0
    - Behavior:
        * The function queries terminal width, asks the tokenizer to produce tokens honoring the provided limit/head/tail, then renders them into a single string which is returned.
    - Caller would typically then print the returned string to the terminal.

2) Error handling example:
    - If a caller passes a str instead of bytes for content:
        * _tokenize_large_file_content is likely to raise TypeError or another exception when it expects bytes; that exception will propagate back to the caller.
    - Recommended pattern:
        try:
            pretty = make_pretty_large_file_content(content=binary_data, limit=10000, head=10, tail=10)
            print(pretty)
        except Exception as e:
            # map/format the error for user output or tests
            handle_error(e)

Notes:
- This function is intentionally minimal: it performs orchestration but delegates all policy and formatting details to _tokenize_large_file_content and _render_tokens. When modifying truncation/formatting behavior, change the tokenizer or renderer rather than this function.
- Because the terminal width is queried at call time, calling this function at different times (or from different environments) may yield different line-wrapping in the rendered output.

## `onlinejudge_command.pretty_printers._tokenize_file_content_without_snipping` · *function*

## Summary:
Convert raw bytes into a linear sequence of pretty-printer tokens by safely decoding the bytes, tokenizing each decoded line (preserving line endings), preserving any decoding diagnostic token, and ensuring empty / newline-only cases produce a visible hint.

## Description:
- Known callers within this codebase:
    - No direct callers were found in the provided snapshot. Typical callers are the pretty-printer entry points that take file contents or program output (raw bytes) and prepare token lists for rendering (for example, functions that render file contents, program stdout/stderr or diffs).
    - Typical pipeline stage: called during input normalization/tokenization immediately after reading raw bytes and before any rendering or diffing logic.

- Why this function is extracted:
    - Responsibility: centralize the pipeline of (1) decode-with-recovery, (2) per-line tokenization, and (3) the final "warn-if-empty" normalization so callers get a complete, render-ready token sequence.
    - This isolates decode error handling and empty-input hints from higher-level code and avoids duplicating the three-step pattern at each call site.

## Args:
    content (bytes)
        - Raw bytes to be processed. Must be a bytes-like object (e.g., bytes or bytearray) because the function delegates decoding to _decode_with_recovery, which calls content.decode().
        - No default. Passing a non-bytes object is a contract violation and may raise AttributeError or TypeError as described in Raises.

## Returns:
    List[_PrettyToken]
    - A list of _PrettyToken instances representing:
        1. Any diagnostic token(s) returned by the decode phase (zero or one token, typically a single HINT token on decode failure) appear first, in the same order returned by _decode_with_recovery.
        2. Tokens produced by tokenizing each decoded line in textual order (for each line from text.splitlines(keepends=True), the result of _tokenize_line(line) is concatenated in order).
        3. After concatenation, the list is passed through _warn_if_empty which may append a HINT token or return a new list when the sequence should signal an empty-or-special case.
    - Possible return shapes / edge cases:
        - Empty content (b''): decode returns text == '' and no decode token → no per-line tokens → _warn_if_empty returns a new list containing a single HINT('(empty)') token.
        - Content decodes successfully but contains lines: returns concatenated tokens for each line; _warn_if_empty may append a '(no trailing newline)' or '(only newline)' hint depending on token sequence.
        - Decode failure: the returned list begins with the HINT token produced by _decode_with_recovery, followed by any tokens produced by tokenizing the replacement-decoded text.

## Raises:
- Exceptions raised by helper functions or by contract violations will propagate:
    - AttributeError:
        - If content does not have a callable .decode (e.g., caller passed an int), content.decode() inside _decode_with_recovery will raise AttributeError which will propagate.
    - TypeError:
        - If content.decode() raises TypeError for non-standard objects, that TypeError will propagate.
    - Any exception raised by _tokenize_line will propagate unchanged (for example, if _tokenize_line expects a str and receives an unexpected type or raises on malformed input).
    - Any unexpected exceptions from _warn_if_empty (e.g., if the token list elements are not well-formed) will propagate.
- The function itself does not catch these exceptions; callers should handle them when appropriate.

## Constraints:
- Preconditions:
    - content must be bytes-like and decodable by bytes.decode() or else callers accept that AttributeError/TypeError may be raised from _decode_with_recovery.
    - _tokenize_line is expected to accept each line as a str (including trailing newline when present) and return an iterable/list of _PrettyToken. If _tokenize_line violates this contract, exceptions will propagate.
- Postconditions:
    - The returned object is a list of _PrettyToken that is suitable for rendering by downstream pretty-printer logic.
    - Any decode-diagnostic token (HINT) returned by _decode_with_recovery will appear at the start of the returned list.
    - The returned list will contain at least one visible hint token if the original content was empty or otherwise matched _warn_if_empty's hinting conditions.

## Side Effects:
- No I/O (no file, network, or stdout writes).
- No modification of global state.
- May allocate and return a new list (in the empty-content branch within _warn_if_empty). Otherwise, tokens produced by _tokenize_line are concatenated into the tokens list and _warn_if_empty may append to that list (in-place mutation in the typical non-empty case).

## Control Flow:
flowchart TD
    Start((Start))
    Start --> Decode[_decode_with_recovery(content) -> (initial_tokens, text)]
    Decode --> ForLines[For each line in text.splitlines(keepends=True)]
    ForLines --> Tokenize[_tokenize_line(line) -> list of tokens]
    Tokenize --> Append[initial_tokens += tokenized_line_tokens]
    Append --> Loop{more lines?}
    Loop -->|yes| ForLines
    Loop -->|no| PostProcess[_warn_if_empty(initial_tokens)]
    PostProcess --> Return[return final tokens]
    Return --> End((End))

## Examples:
- Happy path (simple file content)
    - Input: content = b'Hello\\nWorld\\n'
    - Behavior:
        1. _decode_with_recovery returns tokens = [] and text = 'Hello\\nWorld\\n'.
        2. Each line ('Hello\\n', 'World\\n') is passed to _tokenize_line; their token lists are concatenated.
        3. _warn_if_empty sees non-empty tokens and typically returns the same list (possibly mutated if it appends a hint).
        4. Returned value: list of _PrettyToken representing the two lines (and possibly final newline semantics).

- Decode failure (invalid bytes)
    - Input: content = b'Line1\\n\\xff\\nLine3'
    - Behavior:
        1. _decode_with_recovery catches UnicodeDecodeError and returns initial_tokens = [ HINT(token describing the UnicodeDecodeError) ] and text decoded with errors='replace' (invalid bytes replaced).
        2. Each line of the replacement-decoded text is tokenized and appended after the HINT token.
        3. _warn_if_empty runs on the concatenated list and may append additional hints if required.
        4. Returned value: list beginning with the HINT token followed by tokens for each decoded line.

- Caller error handling example
    - If a caller might receive non-bytes input, it should guard:
        - Try: tokens = _tokenize_file_content_without_snipping(maybe_bytes)
        - Except AttributeError/TypeError: handle/report invalid input type.

Notes:
- This function is a thin assembly of three steps: safe decode (which may produce a leading HINT), per-line tokenization, and final normalization via _warn_if_empty. It intentionally leaves detailed token semantics and rendering decisions to the tokenizers and renderers that produce and consume _PrettyToken instances.

## `onlinejudge_command.pretty_printers.make_pretty_all` · *function*

## Summary:
Compose file-content tokenization and rendering: decode and tokenize raw bytes into pretty-printer tokens, then render those tokens into a single formatted string suitable for terminal display.

## Description:
- Known callers within the codebase:
    - No direct callers were discovered in the provided snapshot. Typical callers are pretty-printer entry points that accept raw file contents or program output (bytes) and need a final human-readable representation to display in the terminal or logs. Examples include callers that render files, stdout/stderr captures, or diffs after normalization.
    - Typical pipeline stage: invoked after reading raw bytes from a file or process and just before the resulting string is printed, logged, or compared.

- Why this logic is extracted:
    - Responsibility boundary: this function encapsulates the two-step pipeline of (1) converting raw bytes into a sequence of typed tokens (handling decoding diagnostics and empty-content hints) and (2) rendering that token sequence into a single styled string. Keeping these steps together prevents repetition at call sites and guarantees consistent decoding/normalization + rendering behavior for all callers.
    - Simplicity and reuse: callers do not need to know or reproduce the tokenization and rendering details; they call this single helper to get a terminal-ready string.

## Args:
    content (bytes)
        - Raw bytes to be converted into a pretty-printed string.
        - Must be a bytes-like object (bytes or bytearray). The function delegates decoding to the module's decode-with-recovery helper which calls content.decode(), so passing a non-bytes object (e.g., int or an object without decode) violates the contract and will raise an error (see Raises).
        - There is no default value.

## Returns:
    str
    - A single string produced by rendering the token sequence returned from tokenization.
    - Typical content:
        * Human-readable text derived from the decoded bytes.
        * May include ANSI escape sequences when default colorama-based font functions are used (so printing the result to a terminal may produce colored/dim/bright output).
        * May contain visible hints inserted by tokenization (for example "(empty)", "(no trailing newline)", or decode-diagnostic hints), styled according to renderer defaults (usually dim).
    - Edge cases:
        * If content == b'': tokenization will produce a hint token (e.g., HINT('(empty)')) and the rendered string will be the rendered hint (not an empty string).
        * If content contains undecodable bytes, tokenization typically produces a leading decode-diagnostic token followed by tokens for replacement-decoded text; the rendered string will begin with the rendered diagnostic hint.

## Raises:
- Propagated exceptions from helper calls; this function performs no internal exception handling:
    - AttributeError:
        - If content does not provide a callable .decode (for example, caller passed an int), the underlying decode call will raise AttributeError which will propagate.
    - TypeError:
        - If content.decode() or any rendering helper is called with an invalid type, the underlying TypeError will propagate.
    - Any exception raised by the tokenizer (_tokenize_line or other tokenization helpers) or by the renderer (_render_tokens) will propagate unchanged (for example, AssertionError from encountering an unexpected token type in _render_tokens).

## Constraints:
- Preconditions:
    - content must be bytes-like and suitable for bytes.decode(); callers that pass other types must handle or expect type errors.
    - The module's tokenizer and renderer implementations must be available and must accept the types described by the helper contracts (tokenizer returns a list of tokens; renderer accepts that token list).
- Postconditions:
    - The returned value is a str representing the rendered tokens in textual order.
    - Any decode-diagnostic or empty-content hinting performed at tokenization will be reflected in the rendered string (styled according to rendering defaults).

## Side Effects:
- No I/O: this function does not read/write files, network resources, or write to stdout/stderr itself.
- No mutation of global state: the function delegates to pure helpers that produce and return values.
- The returned string may include ANSI sequences (via default font functions using colorama). Emitting that string to a terminal may change terminal appearance, but this function only returns the string.
- Custom font/render callables provided deeper in the renderer (not by this function) could perform side effects; such side effects are outside this function's control.

## Control Flow:
flowchart TD
    Start((Start)) --> Tokenize[_tokenize_file_content_without_snipping(content)]
    Tokenize --> TokensList[receive List of _PrettyToken tokens]
    TokensList --> Render[_render_tokens(tokens)]
    Render --> Output[receive rendered str]
    Output --> Return((Return rendered string))

## Examples:
1) Simple content (happy path)
    - Input: content = b'Hello\nWorld\n'
    - Behavior:
        * Tokenization decodes to 'Hello\nWorld\n' and produces tokens for each line.
        * Rendering maps tokens to styled fragments and concatenates them.
        * Output: a str that, when printed, shows "Hello" and "World" with default styles and proper newline renderings.

2) Empty content
    - Input: content = b''
    - Behavior:
        * Tokenization returns a tokens list containing a HINT token such as '(empty)'.
        * Rendering returns the styled hint string (e.g., dimmed '(empty)') rather than an empty string.

3) Invalid bytes (decode failure)
    - Input: content that contains invalid UTF-8 sequences (e.g., b'Line1\n\xff\nLine3')
    - Behavior:
        * Tokenization produces a leading decode-diagnostic HINT token and tokenizes the replacement-decoded text.
        * Rendering includes the diagnostic hint followed by the rendered lines.

4) Caller error-handling pattern
    - If callers may pass non-bytes input, they should guard:
        * Try calling make_pretty_all(maybe_bytes)
        * Catch AttributeError/TypeError to detect invalid input types and handle/report appropriately.

Notes:
- The function is intentionally a small composition (tokenize -> render) and is designed to let tokenization and rendering evolve independently while preserving a single, stable entry point for producing terminal-ready strings from raw bytes.

## `onlinejudge_command.pretty_printers._skip_whitespaces` · *function*

## Summary:
Advance the string index past a contiguous run of ASCII whitespace characters and return a compacted list of tokens representing those skipped characters.

## Description:
This helper scans the input string s starting at index i and consumes a contiguous run of characters in the set {' ', '\t', '\r', '\n'}. For each consumed character it emits a _PrettyToken whose .type is either _PrettyTokenType.WHITESPACE (for space or tab) or _PrettyTokenType.NEWLINE (for carriage return or newline) and whose .value is the character itself. The function then calls _optimize_tokens on the collected per-character tokens so adjacent tokens of the same .type are coalesced before returning.

Known callers / usage context:
- Used by tokenizers and formatting code inside onlinejudge_command.pretty_printers during a linear text scan to normalize and represent runs of whitespace/newlines as typed tokens for downstream rendering, diffing, or formatting.
- Typical pipeline stage: invoked when the scanner encounters a whitespace character to skip the run and obtain tokens that represent the skipped region.

Why this logic is extracted:
- Encapsulates the single responsibility "recognize and tokenize contiguous whitespace/newline runs and coalesce same-type runs." This prevents repeated inline character-by-character handling and ensures consistent tokenization across the module.

See also:
- onlinejudge_command.pretty_printers._PrettyToken (token representation)
- onlinejudge_command.pretty_printers._PrettyTokenType (token categories; access members as _PrettyTokenType.WHITESPACE, _PrettyTokenType.NEWLINE)
- onlinejudge_command.pretty_printers._optimize_tokens (merges adjacent tokens of the same .type)

## Args:
    i (int):
        - Start index in s from which scanning begins.
        - Expected: 0 <= i <= len(s) for typical callers. Python negative indices in the range [-len(s), -1] are valid but callers should prefer non-negative indices.
    s (str):
        - Input text to scan; must be a Python str.

## Returns:
    Tuple[int, List[_PrettyToken]]:
        - int: the index position immediately after the last consumed whitespace character.
            - If no whitespace is present at i, returns the original i unchanged.
            - Otherwise returns j where j is the smallest index >= i such that j == len(s) or s[j] not in {' ', '\t', '\r', '\n'}.
        - List[_PrettyToken]: a (possibly empty) list of tokens representing the consumed characters.
            - Each token's .type is one of the enum members (accessed as attributes):
                * _PrettyTokenType.WHITESPACE for ' ' and '\t'
                * _PrettyTokenType.NEWLINE for '\r' and '\n'
            - The returned list has been processed by _optimize_tokens: adjacent tokens with the same .type are coalesced (for example, separate '\r' and '\n' characters will be merged into a single NEWLINE token with .value == '\r\n').
            - Note on identity semantics: _optimize_tokens may reuse input token objects for tokens that were not merged, and will create new _PrettyToken objects for merged runs. Because this function first creates per-character tokens, merged runs will result in new tokens while single-character runs may be returned as the same per-character token object produced here.

## Raises:
    - IndexError:
        - If i is less than -len(s), accessing s[i] may raise IndexError. The function itself guards against overrunning s by checking i < len(s) in its loop condition.
    - TypeError:
        - If s is not a str, indexing or membership checks may raise TypeError.
    - Other exceptions:
        - Any exceptions raised by constructing _PrettyToken or by _optimize_tokens (e.g., from malformed token-like inputs) will propagate.

## Constraints:
    Preconditions:
        - Caller should supply a valid start index and a str object.
        - Only the ASCII characters ' ', '\t', '\r', '\n' are treated as whitespace here (no other Unicode whitespace categories).
    Postconditions:
        - The returned index points immediately after the consumed run (or equals the input index if no whitespace).
        - The returned token list contains no adjacent tokens with identical .type (guaranteed by _optimize_tokens).
        - The input string s is not modified.

## Side Effects:
    - No external I/O or global state mutations.
    - Allocates a temporary list of per-character _PrettyToken objects and calls _optimize_tokens to produce the final token list.

## Control Flow:
flowchart TD
    Start([Start])
    Check{i < len(s) and s[i] in ' \\t\\r\\n'?}
    Start --> Check
    Check -- No --> ReturnNoWhitespace([return i, []])
    Check -- Yes --> Classify{s[i] in ' \\t'?}
    Classify -- Yes --> MakeWS[_PrettyToken(_PrettyTokenType.WHITESPACE, s[i])]
    Classify -- No --> MakeNL[_PrettyToken(_PrettyTokenType.NEWLINE, s[i])]
    MakeWS --> Append[append token to tokens; i += 1]
    MakeNL --> Append
    Append --> Check
    Check -->|loop ends| Optimize[_optimize_tokens(tokens)]
    Optimize --> Return([return i, optimized_tokens])

## Examples:
1) No whitespace at i
    - Input: i = 0, s = "abc"
    - Result: (0, [])

2) Simple spaces and tabs
    - Input: i = 3, s = "foo  \tbar"
    - Behavior: produces per-character tokens for ' ', ' ', '\t' then _optimize_tokens coalesces them into a single WHITESPACE token with .value "  \t".
    - Example return: (6, [_PrettyToken(_PrettyTokenType.WHITESPACE, "  \t")])

3) CRLF handling
    - Input: substring at i begins with "\r\n"
    - Behavior: creates two NEWLINE tokens for '\r' and '\n'; _optimize_tokens merges them into one NEWLINE token with .value "\r\n".
    - Example return: (i + 2, [_PrettyToken(_PrettyTokenType.NEWLINE, "\r\n")])

4) Mixed whitespace and non-whitespace
    - Input: i = 0, s = "\n \tA"
    - Behavior: consumes '\n', ' ', '\t' producing tokens NEWLINE("\n"), WHITESPACE(" "), WHITESPACE("\t"); optimization merges adjacent WHITESPACE tokens.
    - Example return: (3, [_PrettyToken(_PrettyTokenType.NEWLINE, "\n"), _PrettyToken(_PrettyTokenType.WHITESPACE, " \t")])

5) Invalid index caution
    - Input: i = -9999, s = "short"
    - Behavior: may raise IndexError when attempting s[i]; callers should ensure i is in a sane range.

Implementation note:
    - Implemented by looping while i < len(s) and s[i] in ' \\t\\r\\n', classifying each char to WHITESPACE or NEWLINE, appending a per-character _PrettyToken to a list, incrementing i, then returning i and _optimize_tokens(tokens).

## `onlinejudge_command.pretty_printers._make_diff_between_line_and_line_by_comparing_word_by_word` · *function*

## Summary:
Produce two parallel token sequences for two input lines by scanning them word-by-word and emitting aligned body and whitespace tokens; differing words are marked with left/right highlight token types so renderers can emphasize per-word differences.

## Description:
This internal helper tokenizes two single-line strings a and b in lockstep at the granularity of words (sequences of non-whitespace characters) while preserving and emitting interleaving whitespace/newline tokens via the shared helper _skip_whitespaces. It returns two lists of _PrettyToken instances that represent the original strings exactly when concatenated, but with BODY tokens for identical words and BODY_HIGHLIGHT_LEFT / BODY_HIGHLIGHT_RIGHT tokens for words that differ between the two lines.

Known callers and usage context:
- Internal to onlinejudge_command.pretty_printers (non-public). It is used by the module's diff/pretty-print pipeline whenever the library needs a word-level alignment between two lines to produce colored/annotated side-by-side output or inline highlights.
- Typical trigger: two lines are known (or assumed) to contain the same number of whitespace-separated words and the caller wants a token stream for rendering differences per word.

Why this is a separate function:
- Responsibility separation: this function focuses solely on aligned, word-level comparison and token emission, leaving whitespace tokenization to _skip_whitespaces and leaving higher-level layout/formatting to other parts of the pretty-printers module.
- Reuse and testability: extracting this logic avoids duplicating the alignment/word-comparison logic across multiple renderers and makes the semantics of "when to highlight a word" explicit.

## Args:
    a (str):
        - Left-side input line to compare. Must be a Python str.
        - Leading/trailing/multiple whitespace are preserved in emitted tokens, but are ignored when checking the precondition on the number of words (see Preconditions).
    b (str):
        - Right-side input line to compare. Same expectations as a.

Interdependencies:
    - The function asserts that a.strip().split() and b.strip().split() produce the same number of words. That is, the number of whitespace-separated tokens (after removing leading/trailing whitespace) must be equal for both inputs. If this is not true, the function raises AssertionError.

## Returns:
    Tuple[List[_PrettyToken], List[_PrettyToken]]:
        - First element: tokens_a — a list of _PrettyToken instances representing the left input a.
        - Second element: tokens_b — a list of _PrettyToken instances representing the right input b.

    Semantics of the returned tokens:
        - Both lists, when concatenating token.value in order, reproduce the original strings exactly:
            ''.join(t.value for t in tokens_a) == a
            ''.join(t.value for t in tokens_b) == b
        - The sequence contains tokens produced by:
            * _skip_whitespaces for contiguous runs of ASCII whitespace characters; those tokens have types _PrettyTokenType.WHITESPACE or _PrettyTokenType.NEWLINE (and are already optimized/coalesced by _skip_whitespaces).
            * Word tokens for sequences of non-whitespace characters: if a word at the current position is identical in a and b, both sides get a _PrettyTokenType.BODY token with that word as .value. If they differ, the left side gets _PrettyTokenType.BODY_HIGHLIGHT_LEFT and the right side gets _PrettyTokenType.BODY_HIGHLIGHT_RIGHT for their respective word values.
        - The number of word (BODY / BODY_HIGHLIGHT_*) tokens on each side is equal (guaranteed by the initial assertion).

## Raises:
    AssertionError:
        - If len(a.strip().split()) != len(b.strip().split()). This precondition is used to ensure word-by-word alignment.

    Propagated exceptions from helpers:
        - Exceptions raised by _skip_whitespaces (for example IndexError for extremely invalid start indices in pathological external calls, or TypeError if non-str inputs are passed further upstream) will propagate.
        - Construction of _PrettyToken or enum access errors may propagate if unusual values are used; callers should treat this function as potentially raising exceptions stemming from lower-level tokenization utilities.

## Constraints:
    Preconditions:
        - Both a and b must be Python str objects.
        - After splitting on whitespace and stripping ends, both lines must contain the same number of words:
            len(a.strip().split()) == len(b.strip().split())

    Postconditions (guarantees after successful return):
        - Both returned token lists together represent exactly the input strings (concatenation property noted above).
        - The same number of word tokens (BODY or BODY_HIGHLIGHT_*) appears in tokens_a and tokens_b and they are aligned in order: the nth word token in tokens_a corresponds to the nth word token in tokens_b.
        - All whitespace runs have been emitted via tokens produced by _skip_whitespaces (and thus are already optimized/coalesced where adjacent whitespace/newline characters are merged).

## Side Effects:
    - None. The function does not perform I/O, mutate global state, or interact with external services. It allocates and returns new lists and uses _PrettyToken constructors.

## Control Flow:
flowchart TD
    Start([Start])
    Assert{len(a.strip().split()) == len(b.strip().split())?}
    Start --> Assert
    Assert -- No --> Error[Raise AssertionError]
    Assert -- Yes --> Init[Initialize token lists and indices l_a=0,l_b=0]
    Init --> SkipStart[Call skip_whitespaces() -> append leading whitespace tokens]
    SkipStart --> Loop{while l_a < len(a) and l_b < len(b)}
    Loop --> FindEnds[Find r_a, r_b: end indices of the next word on each side]
    FindEnds --> ExtractWords[word_a = a[l_a:r_a]; word_b = b[l_b:r_b]]
    ExtractWords --> Compare{word_a == word_b?}
    Compare -- Yes --> AppendSame[append BODY token to both lists]
    Compare -- No --> AppendDiff[append BODY_HIGHLIGHT_LEFT to tokens_a and BODY_HIGHLIGHT_RIGHT to tokens_b]
    AppendSame --> Advance[set l_a = r_a; l_b = r_b]
    AppendDiff --> Advance
    Advance --> Skip[call skip_whitespaces() to append whitespace tokens after the word]
    Skip --> Loop
    Loop --> EndAssert{l_a == len(a) and l_b == len(b)?}
    EndAssert -- No --> Error2[AssertionError due to logic invariant broken]
    EndAssert -- Yes --> Return[return (tokens_a, tokens_b)]

## Examples:
1) Simple differing word
    - Input:
        a = "  foo bar"
        b = "baz bar"
    - Precondition:
        a.strip().split() -> ["foo","bar"], b.strip().split() -> ["baz","bar"] => lengths equal (2).
    - Representative returned token sequences (illustrative form showing type:value):
        tokens_a = [WHITESPACE:"  ", BODY_HIGHLIGHT_LEFT:"foo", WHITESPACE:" ", BODY:"bar"]
        tokens_b = [BODY_HIGHLIGHT_RIGHT:"baz", WHITESPACE:" ", BODY:"bar"]

2) Identical lines
    - Input:
        a = "alpha\tbeta"
        b = "alpha\tbeta"
    - Result:
        tokens_a and tokens_b contain WHITESPACE tokens for the tab (from _skip_whitespaces) and BODY tokens for "alpha" and "beta" without highlight types because words match.

3) Mixed whitespace types (CRLF)
    - Input:
        a = "x\r\ny"
        b = "x\r\nz"
    - Behavior:
        - _skip_whitespaces will produce a single NEWLINE token with value "\r\n" for each side between word tokens.
        - Words "x" match, "y" vs "z" differ, so the second word tokens are highlighted left/right.

Notes and implementation considerations for callers:
    - The function assumes ASCII whitespace classification for token boundaries (spaces, tabs, carriage returns, newlines) consistent with _skip_whitespaces; other Unicode whitespace characters are not specially handled.
    - The function treats any maximal run of non-whitespace characters as a "word" (this includes punctuation and symbols). If callers need a different notion of "word" (e.g., language-aware tokenization), perform that normalization before calling this helper.
    - If you cannot guarantee the same number of words in both lines, you should either normalize the inputs first or use a different diffing routine that can handle insertions/deletions (this helper is strictly for aligned, per-word comparisons).

## `onlinejudge_command.pretty_printers._tokenize_str_with_highlight` · *function*

## Summary:
Tokenize input text and produce a new list of _PrettyToken objects where every BODY token is replaced by the corresponding highlighted BODY token (left or right), while non-BODY tokens are preserved in order.

## Description:
- Known callers within the codebase and context:
  - Used by pretty-printers, diffing, and rendering code in this module when a single-line input needs BODY spans annotated as highlighted on one side of a comparison. It is called after tokenization and before rendering so the renderers can select highlight-specific styling.
- Why this is extracted into its own function:
  - Encapsulates the repeated mapping step BODY -> BODY_HIGHLIGHT_LEFT/RIGHT based on side, keeping tokenization and rendering code small and focused.
  - Ensures a consistent, centralized behavior so highlighting semantics do not diverge across callers.

## Args:
    s (str)
        Input text to tokenize. The function delegates tokenization to _tokenize_str(s); therefore the same constraints apply:
        - Recommended: pass a Python str.
        - Allowed: any sequence that supports len(), integer indexing and slicing. If a non-str sequence is passed, token.value items in returned tokens will be slices of that sequence (not necessarily str).
    is_right (bool) (keyword-only)
        Determines which highlight token type to assign to BODY tokens:
        - True  -> _PrettyTokenType.BODY_HIGHLIGHT_RIGHT
        - False -> _PrettyTokenType.BODY_HIGHLIGHT_LEFT
        Expectation: callers should pass a boolean. The implementation tests this value in an if-statement; Python truthiness will be used (e.g., non-zero integers evaluate True), but passing a bool is recommended for clarity.

Interdependencies:
    - The function directly calls _tokenize_str(s) and processes the tokens it yields. Any behavior, exceptions, or constraints of _tokenize_str apply here.

## Returns:
    list[_PrettyToken]
        - A newly created Python list (a different object from any list used internally by _tokenize_str) whose elements are _PrettyToken objects in the same order as the tokens emitted by _tokenize_str(s).
        - For each token t yielded by _tokenize_str(s):
            - If t.type == _PrettyTokenType.BODY:
                - A new _PrettyToken instance is created and appended with:
                    - .type = _PrettyTokenType.BODY_HIGHLIGHT_RIGHT if is_right is True (truthy)
                    - .type = _PrettyTokenType.BODY_HIGHLIGHT_LEFT if is_right is False (falsy)
                    - .value = t.value (the same object/reference as the original token's value)
            - Else:
                - The original token object t is appended to the returned list unchanged (same object identity).
        - Ordering: the returned list preserves the sequence order of tokens from _tokenize_str(s).
        - Edge cases:
            - Empty input -> returns [].
            - If all tokens are non-BODY -> returns a list of the exact same token objects returned by _tokenize_str.
            - If s is a non-str sequence, returned token.value objects are slices of that sequence (as produced by _tokenize_str).

## Raises:
    - Propagated from _tokenize_str(s):
        - TypeError: when s does not support required sequence operations (e.g., len(s) or indexing), or similar misuse.
        - Any other exceptions raised by _tokenize_str (IndexError or custom sequence errors) are not caught and propagate unchanged.
    - This function does not raise any new custom exceptions itself.

## Constraints:
- Preconditions:
    - s must be a sequence supporting len(), indexing and slicing. Prefer str.
    - is_right should be provided as a keyword argument and is expected to be a boolean.
- Postconditions:
    - A new list object is returned.
    - The concatenation of returned token.value items reproduces the original input when s is a str (i.e., ''.join(token.value for token in result) == s).
    - BODY tokens in the result are newly constructed _PrettyToken instances with highlight types; non-BODY tokens are the same objects produced by _tokenize_str.

## Side Effects:
- No I/O.
- No mutation of global state.
- Allocates a new list and, for BODY tokens, allocates new _PrettyToken objects. Non-BODY tokens are appended by reference (no copy).

## Control Flow:
flowchart TD
    Start((Start))
    Start --> CallTokenize[_tokenize_str(s) -> iterable/list of tokens]
    CallTokenize --> ForEach{for each token t in tokens}
    ForEach --> IsBody{t.type == _PrettyTokenType.BODY?}
    IsBody -- Yes --> CheckRight{is_right truthy?}
    CheckRight -- True --> CreateRight[_PrettyToken(BODY_HIGHLIGHT_RIGHT, t.value)]
    CheckRight -- False --> CreateLeft[_PrettyToken(BODY_HIGHLIGHT_LEFT, t.value)]
    CreateRight --> AppendNew[append new token to result list]
    CreateLeft --> AppendNew
    IsBody -- No --> AppendOld[append original token t to result list]
    AppendOld --> Continue[continue loop]
    AppendNew --> Continue
    Continue --> ForEach
    ForEach --> End((return result list))

## Examples:
1) Typical example:
    - s = "  hello\tworld"
    - is_right = False
    - _tokenize_str(s) -> [WHITESPACE("  "), BODY("hello"), WHITESPACE("\t"), BODY("world")]
    - Return:
        [ WHITESPACE("  ")  (same object),
          _PrettyToken(BODY_HIGHLIGHT_LEFT, "hello"),  (new object)
          WHITESPACE("\t")  (same object),
          _PrettyToken(BODY_HIGHLIGHT_LEFT, "world")  (new object)
        ]

2) Empty input:
    - s = ""
    - is_right = True
    - Return: []

3) Error propagation:
    - s = None -> calling this function raises TypeError coming from _tokenize_str (no additional handling here).

4) Non-str sequence:
    - s is a sequence of characters or custom sliceable sequence -> returned token.value elements are slices of s; callers expecting str values should avoid passing non-str sequences.

## `onlinejudge_command.pretty_printers._make_diff_between_line_and_line_by_difflib` · *function*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._make_diff_between_line_and_line` · *function*

## Summary:
Choose a diff strategy for two single-line strings and return a pair of aligned token sequences describing each line; if both lines contain the same number of whitespace-separated words (after stripping), perform a word-by-word aligned diff, otherwise delegate to a difflib-based alignment routine.

## Description:
- Known callers and context:
  - Internal to the pretty-printers pipeline: this dispatcher is invoked by the module's diff/pretty-print routines when two single lines must be converted into sequences of display tokens for side-by-side or inline difference rendering.
  - Typical trigger: comparing a single "expected" line and a single "actual" line during result-reporting to produce colored/annotated output.
- Why this is extracted:
  - Responsibility separation: centralizes the policy that prefers per-word alignment when both lines contain the same number of whitespace-separated words, otherwise uses a flexible difflib alignment. This keeps higher-level pretty-print code simpler and makes the selection policy explicit and testable.

## Args:
    a (str):
        - Left (first) input line to compare. Must be a Python str.
        - Note: the word-count decision uses a.strip().split() (leading/trailing whitespace is preserved in produced tokens but ignored for the word-count check).
    b (str):
        - Right (second) input line to compare. Same expectations as a.

Interdependencies:
    - The boolean condition len(a.strip().split()) == len(b.strip().split()) determines which helper is invoked:
        * If True: calls the module's word-by-word helper optimized for aligned per-word highlighting.
        * If False: calls a difflib-based helper that can handle insertions/deletions.
    - Both helpers are expected to adhere to the same high-level return contract (token sequences per side); callers should consult each helper's documentation for implementation-specific guarantees.

## Returns:
    Tuple[List[_PrettyToken], List[_PrettyToken]]:
        - A pair (tokens_a, tokens_b).
        - Each element is a list of _PrettyToken instances (the module's NamedTuple with fields .type and .value).
        - Contract / semantics:
            * Concatenation property (guaranteed by the word-by-word helper; typically preserved by the difflib helper): joining the token.value strings should reproduce each original input line:
                ''.join(t.value for t in tokens_a) == a
                ''.join(t.value for t in tokens_b) == b
            * Token types (.type) are members of _PrettyTokenType and indicate how renderers should style or highlight text (e.g., BODY, BODY_HIGHLIGHT_LEFT, BODY_HIGHLIGHT_RIGHT, WHITESPACE, NEWLINE, etc.).
            * When the word-counts are equal, the word-by-word helper guarantees aligned word tokens (the nth word token corresponds on both sides). When counts differ, the difflib helper produces an alignment that can include insertions/deletions according to its algorithm.

## Raises:
    - This dispatcher performs only a simple branching test and does not itself raise custom exceptions.
    - Propagated exceptions:
        * If a or b are not str, attribute access like .strip() or .split() may raise AttributeError/TypeError.
        * Exceptions raised by the delegated helper functions (for example, AssertionError from the word-by-word helper if misused, or other implementation-specific errors from the difflib helper) propagate to the caller.
    - Note: because this function checks the word counts before calling the word-by-word helper, an AssertionError from that helper should not occur when the dispatcher is used as intended.

## Constraints:
    Preconditions:
        - Both a and b must be Python str instances.
        - The dispatcher bases its choice on whitespace-separated word count; it does not perform input normalization beyond that check.
    Postconditions:
        - The returned token lists represent the respective input lines in a tokenized form appropriate for rendering.
        - The exact alignment semantics (per-word alignment vs. difflib alignment) depend on which helper was selected.

## Side Effects:
    - None performed by this function itself: no I/O, no global state mutation, no network calls.
    - Allocates and returns lists and _PrettyToken instances created by the delegated helper functions.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> CountWords[Compute w_a = len(a.strip().split()), w_b = len(b.strip().split())]
    CountWords --> CompareCounts{w_a == w_b?}
    CompareCounts -- Yes --> WordHelper[_make_diff_between_line_and_line_by_comparing_word_by_word(a,b)]
    CompareCounts -- No --> DifflibHelper[_make_diff_between_line_and_line_by_difflib(a,b)]
    WordHelper --> Return[Return (tokens_a, tokens_b)]
    DifflibHelper --> Return
    Return --> End([End])

## Examples:
1) Aligned per-word highlighting (equal word counts)
    - Input example: a = "first second", b = "first THIRD"
    - Behavior: this dispatcher chooses the word-by-word helper; the returned token lists (tokens_a, tokens_b) will contain _PrettyToken tokens such that "first" is BODY on both sides and the second word is highlighted left/right. Whitespace tokens preserve spacing.

2) Difflib alignment (unequal word counts)
    - Input example: a = "one two three", b = "one three"
    - Behavior: this dispatcher delegates to the difflib-based helper which produces token sequences that represent the deletion of "two" on the right (and appropriate highlight/omit tokens) while preserving the concatenation property for each side as implemented by that helper.

Usage note:
- If callers require guaranteed per-word alignment, they should ensure the inputs have the same number of whitespace-separated words (or pre-normalize them) so the word-by-word helper is selected. Otherwise, rely on the difflib helper for flexible alignment.

## `onlinejudge_command.pretty_printers._LineDiffOp` · *class*

## Summary:
Represents a single line-level diff operation used by the pretty-printers: a small, immutable triple (lineno, left, right) that associates a 0-based line index with the tokens present on the left and right sides for that line.

## Description:
This NamedTuple is a value object produced and consumed by the pretty-printers' diffing and rendering logic. Each instance bundles:
- lineno: a 0-based line index (see note below) that identifies the relevant line position in one or both sides of a diff,
- left: an optional list of _PrettyToken instances representing tokens on the "left" side for that line,
- right: an optional list of _PrettyToken instances representing tokens on the "right" side for that line.

Typical scenarios for instantiation:
- The module's diffing/formatting code constructs a sequence of _LineDiffOp objects when converting a textual diff (or two lists of tokenized lines) into a renderable line-by-line representation.
- A renderer traverses such a sequence to print colored side-by-side or inline diffs, or to compute which lines are unchanged/added/removed.

Motivation / responsibility:
- Responsibility: provide an immutable, tuple-like record tying a line index to its left/right token lists so renderers and higher-level formatting logic can operate on a uniform sequence of line-diff operations.
- It is intentionally lightweight and does not perform validation or enforce semantic constraints (for example, it does not require that exactly one of left/right be None).

## State:
Attributes (public, read-only)
- lineno (int)
  - Meaning: 0-based line index. The original source includes a note that this "may be an index of the left side, the right side or the both sides" — i.e., it is an index meaningful to whatever side(s) the operation pertains to.
  - Valid range/values: any Python integer. Typical usage expects non-negative integers corresponding to line numbers; negative values are not prevented by the type but are likely semantically invalid for renderers.
  - Invariant: remains the same after construction (immutable).

- left (Optional[List[_PrettyToken]])
  - Meaning: list of tokens for the left-side line, or None if no left-side line exists for this operation (e.g., a pure insertion on the right).
  - Valid values: either None or a list-like sequence containing zero or more _PrettyToken instances. The class does not validate element types at runtime.
  - Invariant: reference is immutable from the perspective of this object (the tuple field cannot be reassigned), but the contained list object is a normal Python list and can be mutated by other code if references are shared — callers should treat token lists as immutable for safety.

- right (Optional[List[_PrettyToken]])
  - Meaning: list of tokens for the right-side line, or None if no right-side line exists for this operation (e.g., a deletion on the left).
  - Valid values and invariants: same notes as .left.

Class-level invariants
- Instances are immutable with respect to their tuple fields: attempts to assign to lineno, left, or right will raise AttributeError.
- The object behaves as a tuple of length 3: index 0 = lineno, index 1 = left, index 2 = right.
- No additional invariants (e.g., about left/right mutual exclusivity or about lineno sign) are enforced by the class itself.

## Lifecycle:
Creation
- Constructor forms:
  - Positional: _LineDiffOp(lineno_value, left_tokens_or_None, right_tokens_or_None)
  - Keyword: _LineDiffOp(lineno=..., left=..., right=...)
- Required args:
  - lineno must be provided (no default).
  - left and right must be provided (explicitly as lists or None) when calling the constructor because this NamedTuple defines three fields; there are no defaults supplied by the type itself.
- Typical callers: the pretty-printers' diff-building code and any test utilities that construct expected diffs.

Usage
- Common usage pattern:
  1. Build a sequence (list) of _LineDiffOp instances representing the transformed diff of two tokenized inputs.
  2. Iterate the sequence in order; for each entry read lineno, then inspect left and right to decide how to format and color the line (unchanged, added, removed, or modified).
  3. Query token lists to generate text and styling using token.type and token.value.
- Ordering / sequencing:
  - There is no required method call order because this is a passive data container. However, typical render pipelines create instances, then read fields in a single read-only pass.

Destruction / cleanup
- No explicit cleanup is required. Instances hold references to their contained objects; Python's garbage collector reclaims them when no longer referenced. There is no close() or context-manager protocol.

Utility methods inherited from NamedTuple / tuple
- _asdict(): returns an OrderedDict mapping field names to values.
- _replace(**kwargs): returns a new _LineDiffOp with specified fields replaced.
- _make(iterable): construct from an iterable of length 3.
- Tuple behaviors: indexing, unpacking, equality comparison, iteration.

## Method Map:
flowchart LR
    Create[Create _LineDiffOp(lineno,left,right)]
    Create --> Store[Immutable tuple fields: lineno,left,right]
    Store --> Consume[Renderer or formatter reads fields]
    Consume --> RenderLeft[If left is not None render left tokens]
    Consume --> RenderRight[If right is not None render right tokens]
    RenderLeft --> Finish((Done))
    RenderRight --> Finish((Done))
    Consume --> Replace[Optional: call _replace(...) to create modified copy]
    Replace --> Consume

## Raises:
Exceptions that may occur during typical usage (arising from NamedTuple / tuple behavior, not custom code):
- TypeError
  - Trigger conditions:
    - Calling the constructor with the wrong number of positional arguments.
    - Using _LineDiffOp._make with an iterable that does not yield exactly three items.
    - Passing unexpected keyword names to the constructor.
- AttributeError
  - Trigger conditions:
    - Attempting to assign to a field (e.g., op.lineno = 1) — NamedTuple fields are read-only.
- Note: The class itself performs no runtime type checking of field contents; invalid element types in left/right or a semantically incorrect lineno will not raise at construction time but may lead to errors later in rendering code.

## Example:
- Constructing a line-diff operation for a modified line:
  - lineno = 3
  - left = a list of _PrettyToken tokens representing the original content of line 3
  - right = a list of _PrettyToken tokens representing the new content of line 3
  - The created _LineDiffOp ties lineno to those two token lists so the renderer can display a side-by-side or inline diff for that line.

- Constructing an insertion (no left line):
  - lineno = 5, left = None, right = list of tokens for the inserted line

- Constructing a deletion (no right line):
  - lineno = 2, left = list of tokens for the removed line, right = None

(Use _LineDiffOp._replace(...) to make modified copies rather than mutating existing instances.)

## `onlinejudge_command.pretty_printers._make_diff_between_file_and_file_by_comparing_line_by_line` · *function*

## Summary:
Produce a sequence of line-level diff operations by comparing two multi-line strings line-by-line and generating tokenized diffs only for lines that differ.

## Description:
This function is a low-level step in the pretty-printers' diff pipeline: given two entire file contents (or arbitrary multi-line string values) it compares them line-by-line and returns a list of _LineDiffOp records describing the differences for rendering.

Known callers and context:
- Internal to the pretty-printers module: invoked by higher-level formatting/renderer code that needs a sequence of line-diff operations to produce colored, side-by-side or inline human-readable diffs.
- Typical trigger: after obtaining the "expected" and "actual" output strings for a test/run, the pretty-printer pipeline calls this function to convert the raw strings into a compact list of per-line tokenized diffs for rendering.

Why this logic is extracted:
- Responsibility separation: isolates the line-level iteration and policy for when to produce a diff operation (only when lines differ according to check_lines_match).  It delegates single-line alignment/tokenization to specialized helpers (_make_diff_between_line_and_line and _tokenize_line), keeping the loop-and-collection logic simple and reusable.

## Args:
    a (str)
        - The "left" multi-line string to compare (for example, expected output).
        - Must be a Python str. Leading/trailing whitespace and line endings are preserved in tokens produced for rendering, except the function uses rstrip() only for a precondition check (see Constraints).
    b (str)
        - The "right" multi-line string to compare (for example, actual output).
        - Must be a Python str.

    compare_mode (CompareMode) (keyword-only)
        - A member of the CompareMode enum, controls how lines are considered matching.
        - Allowed values:
            * Any CompareMode except CompareMode.IGNORE_SPACES_AND_NEWLINES (the function asserts that this value is not provided).
        - Notes:
            * The function uses check_lines_match(lines_a[i], lines_b[i], compare_mode=compare_mode) to decide whether a particular pair of lines should be considered equal (and therefore skipped) or considered different (and therefore tokenized/diffed).
            * When compare_mode is CompareMode.EXACT_MATCH or CompareMode.CRLF_INSENSITIVE_EXACT_MATCH the function permits appending ops representing leftover lines (see Control Flow / Constraints below).

## Returns:
    List[_LineDiffOp]
        - A list (possibly empty) of _LineDiffOp instances, each representing a single line-level diff operation.
        - For a given _LineDiffOp entry:
            * lineno is the 0-based line index (as used by this function's loop).
            * left is either a list of _PrettyToken tokens for the left/`a` line, or None when the operation represents an insertion (no left line).
            * right is either a list of _PrettyToken tokens for the right/`b` line, or None when the operation represents a deletion (no right line).
        - Generation rules:
            * For each index i from 0 up to min(len(lines_a), len(lines_b))-1:
                - If check_lines_match(lines_a[i], lines_b[i], compare_mode=compare_mode) returns True: no _LineDiffOp is generated for that line (the lines are treated as equal).
                - If it returns False: the function calls _make_diff_between_line_and_line(lines_a[i], lines_b[i]) to obtain (tokens_a, tokens_b) and appends _LineDiffOp(i, tokens_a, tokens_b).
            * If compare_mode is EXACT_MATCH or CRLF_INSENSITIVE_EXACT_MATCH, and either side still has remaining items beyond the processed min index, the function will create _LineDiffOp entries for those remaining lines:
                - Remaining left-only lines produce entries with left tokens and right = None (tokens obtained via _tokenize_line).
                - Remaining right-only lines produce entries with left = None and right tokens.
        - Edge cases:
            * If all corresponding lines match, the returned list is empty.
            * The function never synthesizes ops for lines that check_lines_match considers equal.

## Raises:
    AssertionError
        - If compare_mode == CompareMode.IGNORE_SPACES_AND_NEWLINES (the function asserts this is not used).
        - If len(a.rstrip().splitlines()) != len(b.rstrip().splitlines()). The function asserts that the number of lines (after stripping trailing whitespace/newlines from both inputs) is equal. If this precondition is violated an AssertionError is raised.
    Propagated exceptions from helpers:
        - Exceptions raised by check_lines_match, _make_diff_between_line_and_line, or _tokenize_line propagate to the caller (for example, TypeError/AttributeError if non-str inputs are passed or any AssertionError or other error those helpers raise).

## Constraints:
    Preconditions:
        - Both a and b must be str instances.
        - compare_mode must not be CompareMode.IGNORE_SPACES_AND_NEWLINES.
        - The two inputs must satisfy: len(a.rstrip().splitlines()) == len(b.rstrip().splitlines()). This enforces that, after trimming trailing whitespace/newlines, the two texts have the same count of logical lines. The assert makes the function unsuitable when the caller expects differing logical line counts.
    Postconditions:
        - Returned list contains exactly one _LineDiffOp for each pair of line indices that are considered different by check_lines_match, plus possible trailing-only ops when compare_mode allows them.
        - The sequence of returned _LineDiffOp items is ordered by ascending lineno and each lineno corresponds to the index used when iterating the splitlines(keepends=True) arrays.

## Side Effects:
    - The function is pure with respect to external state: it performs no I/O, does not mutate global state, and performs no network or filesystem operations.
    - It allocates Python objects (lists, _PrettyToken instances created by helpers, _LineDiffOp tuples) and returns them.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> AssertMode{compare_mode != IGNORE_SPACES_AND_NEWLINES?}
    AssertMode -- No --> RaiseAssertionError1[AssertionError: invalid compare_mode]
    AssertMode -- Yes --> AssertLines{len(a.rstrip().splitlines()) == len(b.rstrip().splitlines())?}
    AssertLines -- No --> RaiseAssertionError2[AssertionError: unequal logical line counts]
    AssertLines -- Yes --> SplitLines[lines_a = a.splitlines(keepends=True), lines_b = b.splitlines(keepends=True)]
    SplitLines --> Loop[for i in 0 .. min(len(lines_a),len(lines_b))-1]
    Loop --> CheckLineMatch
    CheckLineMatch{check_lines_match(lines_a[i],lines_b[i])?}
    CheckLineMatch -- True --> Skip[no op for this i]
    CheckLineMatch -- False --> MakeLineDiff[_make_diff_between_line_and_line(lines_a[i],lines_b[i]) -> (tokens_a,tokens_b)]
    MakeLineDiff --> AppendOp[ops.append(_LineDiffOp(i,tokens_a,tokens_b))]
    Skip --> Continue
    Continue --> LoopEnd[advance i]
    LoopEnd --> TailCheck{compare_mode in (EXACT_MATCH,CRLF_INSENSITIVE_EXACT_MATCH)?}
    TailCheck -- Yes --> LeftRemainder[append left-only ops while i < len(lines_a)]
    LeftRemainder --> RightRemainder[append right-only ops while i < len(lines_b)]
    RightRemainder --> ReturnOps[return ops]
    TailCheck -- No --> ReturnOps
    ReturnOps --> End([End])

## Examples:
1) Basic usage
    - Inputs:
        a = "line1\nunchanged\nleft-only\n"
        b = "line1\nmodified\nright-only\n"
        compare_mode = CompareMode.EXACT_MATCH
    - Behavior (conceptual):
        * line 0: "line1" matches -> no op
        * line 1: "unchanged" vs "modified" -> _make_diff_between_line_and_line produces (tokens_a1, tokens_b1) -> ops.append(_LineDiffOp(1, tokens_a1, tokens_b1))
        * line 2: if splitlines(keepends=True) results put both sides at same index but content differs -> corresponding tokens appended or, if one side lacked a terminal newline and splitlines produced a remainder, the tail-handling code (since compare_mode is EXACT_MATCH) will create left-only or right-only ops using _tokenize_line.
    - Returned value: a list containing one or more _LineDiffOp entries describing the differing lines. Each token list reproduces its original line when token.value strings are concatenated (delegated helper contract).

2) Caller responsibility example (precondition failure)
    - If a and b have different logical line counts after rstrip (for example a = "x\n\n" and b = "x\n"), the function will raise AssertionError because the precondition about equal logical line counts is violated. The caller should normalize or choose a different comparison strategy in that case.

Notes:
- This function assumes tokenization/alignment responsibility is handled by _make_diff_between_line_and_line and _tokenize_line; it focuses on identifying which line indices need tokenized diffs and collecting the resulting _LineDiffOp objects in order.

## `onlinejudge_command.pretty_printers._tokenize_line_with_highlight` · *function*

## Summary:
Convert a line's token stream into a list of pretty-printer tokens where every body-text token is replaced by a highlighted-body token on the specified side; non-body tokens are preserved in order and identity.

## Description:
This helper takes the token sequence produced by the module's tokenizer for a single input line and marks the body text tokens as highlighted on either the left or right side according to is_right. It is intended to be used in a rendering/diff pipeline immediately after tokenization and before layout/colorization so that renderers can style highlighted body spans differently from ordinary body text.

Known callers and typical context:
- Callers are the pretty-printer rendering/diff functions that render lines with highlighted differences (side-by-side or unified views). Typical usage:
  1. Tokenize a raw line with _tokenize_line to produce a sequence of _PrettyToken.
  2. Call this function to convert BODY tokens to BODY_HIGHLIGHT_LEFT or BODY_HIGHLIGHT_RIGHT depending on which side is being rendered.
  3. Pass the returned tokens to token-to-string renderers that map _PrettyTokenType members to colors/prefixes.
- This logic is separated into its own function to keep a single, small responsibility: apply a side-specific highlight transformation to an existing token stream while preserving ordering and non-body token instances.

## Args:
    line (str):
        The original source line text used only to call the tokenizer. Must be a str.
    is_right (bool):
        Keyword-only flag indicating which side the highlight should represent.
        - True: body tokens become _PrettyTokenType.BODY_HIGHLIGHT_RIGHT
        - False: body tokens become _PrettyTokenType.BODY_HIGHLIGHT_LEFT

Notes on interdependency:
- This function calls _tokenize_line(line) and therefore requires that _tokenize_line exists and returns an iterable of _PrettyToken instances.
- It relies on _PrettyTokenType having members BODY, BODY_HIGHLIGHT_LEFT, and BODY_HIGHLIGHT_RIGHT, and on constructing new _PrettyToken instances.

## Returns:
    list[_PrettyToken]:
        A new list containing tokens corresponding to the token stream for the input line, in the same order and of the same length as the iterable returned by _tokenize_line.
        - For each token produced by _tokenize_line:
            * If token.type == _PrettyTokenType.BODY: the returned list contains a new _PrettyToken whose .type is either BODY_HIGHLIGHT_RIGHT (if is_right True) or BODY_HIGHLIGHT_LEFT (if is_right False) and whose .value equals the original token.value.
            * Otherwise: the original token object is appended unchanged (same identity).
        - Invariant: no token in the returned list will have .type equal to _PrettyTokenType.BODY for positions that were BODY in the input; they will be replaced by the corresponding BODY_HIGHLIGHT_* member.

## Raises:
    - This function does not explicitly raise exceptions itself.
    - It will propagate any exception raised by:
        * _tokenize_line(line) (for example, TypeError if line is not acceptable to the tokenizer)
        * _PrettyToken(...) constructor (for example, TypeError for wrong arguments)
    - Consumers should catch exceptions from the tokenizer or the token constructor as appropriate.

## Constraints:
Preconditions:
    - Caller should pass a Python str as line and a bool for is_right.
    - _tokenize_line must be available in the same module and must return an iterable of _PrettyToken (objects with .type and .value attributes).
    - _PrettyTokenType must define the enum members BODY, BODY_HIGHLIGHT_LEFT, BODY_HIGHLIGHT_RIGHT.

Postconditions:
    - The returned list has the same length and ordering as the input token iterable.
    - Every token that had type BODY in the input is replaced by a token with a BODY_HIGHLIGHT_* type in the output.
    - All non-BODY tokens in the output are the same objects that _tokenize_line yielded (no copy was made).

## Side Effects:
    - None performed directly by this function: it does not perform I/O, mutate global state, or call external services.
    - Side effects may occur if _tokenize_line or the _PrettyToken constructor have side effects; this function will propagate them.

## Control Flow:
flowchart TD
    Start([Start])
    CallTokenizer[_tokenize_line(line) -> iterable of tokens]
    Start --> CallTokenizer
    ForEach[For each token in iterable]
    CallTokenizer --> ForEach
    CheckType{token.type == _PrettyTokenType.BODY?}
    ForEach --> CheckType
    TrueBranch[Create new _PrettyToken(BODY_HIGHLIGHT_RIGHT or LEFT, token.value)]
    FalseBranch[Append original token unchanged]
    CheckType -->|yes| TrueBranch
    CheckType -->|no| FalseBranch
    TrueBranch --> AppendToList[append new token to result list]
    FalseBranch --> AppendToList
    AppendToList --> LoopBack{more tokens?}
    LoopBack -->|yes| ForEach
    LoopBack -->|no| ReturnResult[return result list]
    ReturnResult --> End([End])

## Examples:
- Typical happy-path usage (conceptual):
    tokens = _tokenize_line_with_highlight("some example line", is_right=False)
    # All BODY tokens produced by the tokenizer for this line are now BODY_HIGHLIGHT_LEFT,
    # non-BODY tokens are preserved, and token ordering is unchanged.

- When rendering the right side of a diff:
    tokens_right = _tokenize_line_with_highlight(line_text, is_right=True)
    # Renderers will see BODY_HIGHLIGHT_RIGHT tokens and apply the right-side highlight style.

- Error propagation example (conceptual):
    try:
        tokens = _tokenize_line_with_highlight(maybe_not_a_string, is_right=True)
    except Exception as e:
        # Handle exceptions propagated from _tokenize_line or token construction
        handle_error(e)

## `onlinejudge_command.pretty_printers._make_diff_between_file_and_file_by_difflib` · *function*

## Summary:
Produce a sequence of line-level diff operations that describe how to transform the left file content into the right file content using difflib.SequenceMatcher; the result is a list of _LineDiffOp entries encoding deletions, insertions, and replacements with tokenized, side-highlighted line contents.

## Description:
This function computes a line-oriented diff between two text inputs (both provided as full file contents strings), tokenizes each differing line and marks body tokens as highlighted on the appropriate side, and returns a flat list of _LineDiffOp objects describing the per-line differences in order.

Known callers within the codebase:
- No direct callers were discovered in the provided snapshot. Intended callers are the module's pretty-printer rendering and formatting functions that need a tokenized, line-by-line diff representation to render colored side-by-side or inline diffs (for example: top-level diff formatter functions within the pretty_printers module).

Why this logic is extracted:
- Responsibility boundary: it isolates diff discovery and tokenization/highlight assignment from rendering. Callers receive a normalized sequence of _LineDiffOp entries and do not need to handle difflib details, line-splitting behavior, or which tokens should be highlighted for the left/right side.

## Args:
    a (str):
        The full content of the "left" file (or original text). Must be a Python str. The function will call a.splitlines(keepends=True) to produce a list of lines including their line-ending characters.
    b (str):
        The full content of the "right" file (or new text). Must be a Python str. The function will call b.splitlines(keepends=True).

Notes:
- Both inputs are treated purely as sequences of lines; they are not interpreted as paths or file handles.
- Passing non-str values will likely raise an error when splitlines is called (TypeError) or downstream when tokenization functions are invoked.

## Returns:
    List[_LineDiffOp]:
        A list (possibly empty) of _LineDiffOp instances describing the line-level diff. Each element is a tuple-like object (lineno, left_tokens_or_None, right_tokens_or_None) where:
        - lineno (int): a 0-based line index that identifies the relevant line position. This index is taken from the index variable used during diff iteration and corresponds to the position in the line list produced by splitlines(keepends=True) for the applicable side(s).
        - left (Optional[List[_PrettyToken]]): None for inserted lines (present only on the right); otherwise a list of tokens for the left-side line with body tokens transformed to BODY_HIGHLIGHT_LEFT via _tokenize_line_with_highlight(..., is_right=False).
        - right (Optional[List[_PrettyToken]]): None for deleted lines (present only on the left); otherwise a list of tokens for the right-side line with body tokens transformed to BODY_HIGHLIGHT_RIGHT via _tokenize_line_with_highlight(..., is_right=True).

Possible return shapes / edge cases:
- []: when the two inputs are identical line-for-line (difflib reports only 'equal' opcodes).
- A sequence containing:
  - deletion ops: _LineDiffOp(lineno, left_tokens, None)
  - insertion ops: _LineDiffOp(lineno, None, right_tokens)
  - replacement ops: _LineDiffOp(lineno, left_tokens, right_tokens) for aligned replaced lines, or the function may emit separate deletion/insertion ops when replacement ranges are uneven.
- The order of entries follows difflib.SequenceMatcher.get_opcodes() order and the function's internal expansion logic.

## Raises:
    AssertionError:
        - If difflib yields an opcode tag not in {'replace', 'delete', 'insert', 'equal'}, the final else branch triggers assert False.
        - In the 'delete' branch: assert l_b == r_b (ensures right-side slice is empty for a delete opcode). If violated, AssertionError is raised.
        - In the 'insert' branch: assert l_a == r_a (ensures left-side slice is empty for an insert opcode). If violated, AssertionError is raised.
        - In the 'replace' inner-position alignment loop: assert l_a == l_b before constructing a paired replacement pair. If that assert fails, AssertionError is raised.
    Exceptions propagated from called functions:
        - Any exception raised by _tokenize_line_with_highlight (e.g., from tokenization or _PrettyToken construction) will propagate.
        - Any exception from a.splitlines or b.splitlines (unlikely for str inputs) will propagate.

## Constraints:
Preconditions:
    - Both a and b must be Python str objects containing the entire textual contents of the left and right inputs respectively.
    - The module must provide _tokenize_line_with_highlight and _LineDiffOp (the function uses these directly).
    - _tokenize_line_with_highlight must accept a single-line string and keyword is_right: bool, and return a list of _PrettyToken instances (as assumed by the module).

Postconditions:
    - The returned list contains only _LineDiffOp instances (per module contract).
    - Tokens returned in left/right entries that originated from BODY tokens will have been converted to BODY_HIGHLIGHT_LEFT or BODY_HIGHLIGHT_RIGHT by _tokenize_line_with_highlight.
    - No I/O is performed and no global state is modified by this function itself.

## Side Effects:
    - The function performs no I/O (it operates purely on the two string inputs).
    - It does not mutate global module state.
    - It may indirectly cause side effects or exceptions via _tokenize_line_with_highlight or token constructors if those functions perform side effects; such behavior is not introduced by this function itself.

## Control Flow:
flowchart TD
    Start([Start])
    A[a.splitlines(keepends=True)] --> B[b.splitlines(keepends=True)]
    B --> C[Create difflib.SequenceMatcher and set_seqs(lines_a, lines_b)]
    C --> D[get_opcodes() loop]
    D --> E{opcode tag}
    E -->|replace| F[handle replace]
    E -->|delete| G[handle delete: emit left-only ops]
    E -->|insert| H[handle insert: emit right-only ops]
    E -->|equal| I[skip]
    F --> F1[while leading leftover lines on left -> append left-only ops]
    F --> F2[while leading leftover lines on right -> append right-only ops]
    F --> F3[while lines on both sides: assert l_a==l_b -> tokenize both sides -> append paired ops]
    F --> F4[emit remaining left-only and right-only ops]
    G --> J[tokenize each deleted left line -> append left-only ops]
    H --> K[tokenize each inserted right line -> append right-only ops]
    I --> L[no ops emitted for this opcode]
    J --> M[continue loop]
    K --> M
    L --> M
    M --> N{more opcodes?}
    N -->|yes| D
    N -->|no| O[return ops list]
    O --> End([End])

## Examples:
1) Simple usage (happy path):
    left = "line1\ncommon\noldline\n"
    right = "line1\ncommon\nnewline\n"
    ops = _make_diff_between_file_and_file_by_difflib(left, right)
    # ops will contain one _LineDiffOp describing the replaced line,
    # with left populated (tokens for "oldline\n" highlighted as left)
    # and right populated (tokens for "newline\n" highlighted as right).

2) Identical contents:
    left = "same\nlines\n"
    right = "same\nlines\n"
    ops = _make_diff_between_file_and_file_by_difflib(left, right)
    # ops == []  (no entries emitted because all opcodes are 'equal')

3) Handling insertion and deletion:
    left = "a\nb\nc\n"
    right = "a\nb\nc\nd\n"
    ops = _make_diff_between_file_and_file_by_difflib(left, right)
    # Last line is an insertion: expect a _LineDiffOp with left=None and right set to tokens for "d\n".

4) Error handling example:
    try:
        result = _make_diff_between_file_and_file_by_difflib(123, "some")
    except Exception as e:
        # a.splitlines will raise TypeError because 123 is not a str.
        handle_error(e)

Implementation notes for re-implementers:
- Use splitlines(keepends=True) to preserve line-endings, ensuring tokens include trailing newlines for accurate rendering.
- Use difflib.SequenceMatcher.set_seqs(lines_a, lines_b) and iterate matcher.get_opcodes() to examine diff segments.
- For replacement ranges where the counts differ, the function emits left-only and right-only ops to represent unpaired lines and emits paired ops where counts align.
- Ensure to call _tokenize_line_with_highlight(line, is_right=...) to obtain tokens with the correct highlight side.

## `onlinejudge_command.pretty_printers._make_diff_between_file_and_file` · *function*

## Summary:
Selects and runs the appropriate line-oriented diff strategy for two text contents and returns a sequence of line-level diff operations; it chooses a fast line-by-line comparator when the two texts have the same number of logical lines, and falls back to a difflib-based diff (with optional CRLF normalization) when they differ.

## Description:
This function is the dispatcher in the pretty-printers diff pipeline: given two full-text strings (commonly "expected" and "actual" program outputs) and a comparison mode, it decides whether to compare the texts line-by-line (one-to-one) or to compute a richer difflib-based diff that can represent insertions/deletions/replacements across differing line counts.

Known callers and context:
- Internal callers are other functions in the onlinejudge_command.pretty_printers module that produce user-facing colored/annotated diffs. Typical callers call this after obtaining expected and actual output strings for a test case and when they need a List[_LineDiffOp] describing which lines differ and how to highlight tokens.
- Trigger condition: called when the system needs a rendered diff (for example, when a test's output does not match the expected output or when producing a side-by-side/inlined diff view).

Why this logic is extracted:
- Separates responsibility of choosing a diff strategy and performing small normalizations (compare_mode downgrading and CRLF handling) from the two concrete diff implementations:
  - _make_diff_between_file_and_file_by_comparing_line_by_line: optimized for the case where inputs have the same logical line count and only per-line differences need tokenized alignment.
  - _make_diff_between_file_and_file_by_difflib: robust difflib-driven algorithm for insertions/deletions/replacements when line counts differ.
- Keeps callers simple: they receive a unified List[_LineDiffOp] regardless of which internal strategy was used.

## Args:
    a (str):
        - Left text input (e.g., expected output).
        - Must be a Python str. The function will treat it as the full file/text contents; line splitting is performed by helpers (splitlines with keepends=True inside helpers).
        - The local variable a may be replaced with a CRLF-normalized copy (a.replace('\r\n','\n')) in one branch — the original caller's object is not mutated.

    b (str):
        - Right text input (e.g., actual output).
        - Must be a Python str. Like `a`, it may be locally replaced with a CRLF-normalized copy.

    compare_mode (CompareMode) (keyword-only):
        - Enum value from onlinejudge_command.output_comparators.CompareMode.
        - Allowed/expected values: any CompareMode except CompareMode.IGNORE_SPACES_AND_NEWLINES (the function asserts this is not passed).
        - Effects:
            * If compare_mode preserves line ordering semantics and the two inputs have the same logical number of lines (after rstrip().splitlines()), the function delegates to the line-by-line comparator with the same compare_mode.
            * If the inputs have different line counts, the function will:
                - If compare_mode is CompareMode.IGNORE_SPACES, emit a warning and downgrade compare_mode to CompareMode.CRLF_INSENSITIVE_EXACT_MATCH for the purposes of diff generation.
                - (The code checks for CompareMode.IGNORE_SPACES_AND_NEWLINES as well in the downgrade tuple, but the top-level assert prevents that value from being passed.)
            * If compare_mode is CompareMode.CRLF_INSENSITIVE_EXACT_MATCH and either input contains '\r', the function will emit a warning and replace CRLF sequences ('\r\n') with LF ('\n') in both inputs before calling the difflib-based comparator.

## Returns:
    List[_LineDiffOp]:
        - The function returns the list produced by the chosen helper:
            * If the two inputs have the same logical line count: returns result of _make_diff_between_file_and_file_by_comparing_line_by_line(a, b, compare_mode=compare_mode).
            * Otherwise: returns result of _make_diff_between_file_and_file_by_difflib(a, b) after possibly downgrading compare_mode and normalizing CRLFs.
        - Representation contract (as produced by helpers):
            * Each _LineDiffOp describes a single logical line position and contains either left tokens, right tokens, or both (for replacements).
            * The returned list may be empty when there are no diffs to report.
        - No additional wrapping or transformation is applied by this dispatcher beyond possible CRLF replacement in local copies of a/b.

## Raises:
    AssertionError:
        - If the caller passes compare_mode == CompareMode.IGNORE_SPACES_AND_NEWLINES, the function immediately raises AssertionError (top-level assert).
    Propagated exceptions:
        - Any exception raised by the delegated helpers (e.g., TypeError if a or b is not a str, AssertionError raised inside the helpers, errors from tokenization code) propagates to the caller.
    Notes:
        - The function itself does not assert equality of line counts; instead it routes to the appropriate helper. The line-count-sensitive assertion (if any) may be present in the by-comparing_line_by_line helper and would propagate from there.

## Constraints:
    Preconditions:
        - a and b must be Python str instances containing the full textual contents to compare.
        - compare_mode must not be CompareMode.IGNORE_SPACES_AND_NEWLINES (this is enforced by an assert).
    Postconditions:
        - The returned list is the exact list produced by the chosen internal strategy; callers can rely on the helpers' contract about ordering (ascending lineno) and tokenization/highlight conventions.
        - If CRLF normalization was performed, it was only applied to local copies of a and b used for diffing; original caller variables are unaffected.

## Side Effects:
    - Logging: the function may emit warnings via the module logger (logger.warning) in two situations:
        1) When compare_mode is an "ignore spaces" flavor but the texts differ in line counts: a warning is emitted that ignores the requested compare_mode and uses the default compare mode for diff generation instead.
        2) When compare_mode == CompareMode.CRLF_INSENSITIVE_EXACT_MATCH and either input contains '\r': a warning is emitted stating that carriage returns are removed from the diff.
      These are the only observable external side effects performed by this function.
    - No file, network, or stdout/stderr I/O is performed by the function itself (beyond the logging mentioned).
    - No global state is mutated by this function; it only reassigns local variables and returns a value.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> AssertMode{compare_mode != IGNORE_SPACES_AND_NEWLINES?}
    AssertMode -- No --> RaiseAssertion[AssertionError: invalid compare_mode]
    AssertMode -- Yes --> CountCheck{len(a.rstrip().splitlines()) == len(b.rstrip().splitlines())?}
    CountCheck -- Yes --> ByLine[_make_diff_between_file_and_file_by_comparing_line_by_line(a, b, compare_mode)]
    ByLine --> ReturnByLine[return ops]
    CountCheck -- No --> DowngradeCheck{compare_mode in (IGNORE_SPACES, IGNORE_SPACES_AND_NEWLINES)?}
    DowngradeCheck -- Yes --> WarnDowngrade[logger.warning(...downgrading compare_mode...)] --> SetMode[compare_mode = CRLF_INSENSITIVE_EXACT_MATCH]
    DowngradeCheck -- No --> SkipDowngrade
    SetMode --> CRLFCheck
    SkipDowngrade --> CRLFCheck{compare_mode == CRLF_INSENSITIVE_EXACT_MATCH?}
    CRLFCheck -- Yes --> HasCR{'\r' in a or '\r' in b?}
    HasCR -- Yes --> WarnCR[logger.warning("carriage return '\\r' is removed from diff")] --> Normalize[ a = a.replace('\r\n','\n'); b = b.replace('\r\n','\n') ] --> CallDifflib
    HasCR -- No --> CallDifflib
    CRLFCheck -- No --> CallDifflib
    CallDifflib[_make_diff_between_file_and_file_by_difflib(a, b)] --> ReturnDifflib[return ops]
    ReturnDifflib --> End([End])

## Examples:
1) Typical same-line-count path
    - Inputs:
        a = "one\nsame\nlast\n"
        b = "one\nchanged\nlast\n"
        compare_mode = CompareMode.EXACT_MATCH
    - Behavior:
        * The function sees both inputs have the same number of logical lines and calls _make_diff_between_file_and_file_by_comparing_line_by_line(a, b, compare_mode=CompareMode.EXACT_MATCH).
        * The returned list contains _LineDiffOp entries only for lines where check_lines_match returned False (here: the second line).

    - Example usage:
        ops = _make_diff_between_file_and_file_by_comparing_line_by_line(a, b, compare_mode=CompareMode.EXACT_MATCH)
        # (dispatcher usage)
        ops = _make_diff_between_file_and_file(a, b, compare_mode=CompareMode.EXACT_MATCH)

2) Different-line-count path with downgrade and CRLF normalization
    - Inputs:
        a = "l1\r\nl2\r\n"           # Windows CRLF line endings, 2 logical lines
        b = "l1_extra\nl2\nl3\n"     # 3 logical lines
        compare_mode = CompareMode.IGNORE_SPACES
    - Behavior:
        * The function detects unequal logical line counts (after rstrip().splitlines()), so it cannot use the simple line-by-line comparator.
        * Because compare_mode is IGNORE_SPACES, it logs a warning about ignoring the requested compare_mode and downgrades to CRLF_INSENSITIVE_EXACT_MATCH for diff generation.
        * Since the (downgraded) compare_mode == CRLF_INSENSITIVE_EXACT_MATCH and there are '\r' characters in `a`, it logs a warning about removing carriage returns and performs a.replace('\r\n','\n') and b.replace('\r\n','\n') (no external mutation).
        * It calls _make_diff_between_file_and_file_by_difflib with the possibly-normalized strings and returns that result.

    - Example usage with error-handling:
        try:
            ops = _make_diff_between_file_and_file(a, b, compare_mode=CompareMode.IGNORE_SPACES)
        except AssertionError:
            # raised only if compare_mode was IGNORE_SPACES_AND_NEWLINES
            handle_bad_compare_mode()
        except Exception as e:
            # handle tokenization/difflib errors propagated from helpers
            handle_other_error(e)

3) Error example: invalid compare_mode
    - Inputs:
        compare_mode = CompareMode.IGNORE_SPACES_AND_NEWLINES
    - Behavior:
        * The function immediately raises AssertionError because that compare_mode is not permitted by this dispatcher.
        * Callers must avoid passing that enum member (it is asserted out).

Notes for implementers:
- Preserve the exact branching behavior:
  - Use a top-level assert to forbid CompareMode.IGNORE_SPACES_AND_NEWLINES.
  - Use len(a.rstrip().splitlines()) == len(b.rstrip().splitlines()) to decide the line-count-equality check.
  - If downgrading compare_mode, emit a clear logger.warning before changing the local variable.
  - For CRLF normalization, check if '\r' is present anywhere in either input, warn, then replace '\r\n' with '\n' in local copies prior to calling the difflib-based helper.
- Do not perform any other normalization (e.g., do not strip trailing whitespace globally) — normalization is limited to the CRLF replacement described above.
- Return the exact list returned by the delegated helper without further modification.

## `onlinejudge_command.pretty_printers._MergedDiffOp` · *class*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._reconstruct_entire_diff` · *function*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._add_lines_around_diff_lines` · *function*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._add_dots_between_gaps` · *function*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._len_of_tokens` · *function*

## Summary:
Compute the total printable character width of a sequence of pretty-printer tokens, counting visible representations for whitespace and excluding newline characters contributed by whitespace/newline tokens.

## Description:
This helper iterates a list of typed tokens produced by the pretty-printers and accumulates the number of characters that would be shown when tokens are rendered with visible whitespace. For tokens whose type indicates whitespace or newline, the token's text is transformed with the module's visible-whitespace mapping and any newline characters are removed before measuring length; for all other token types the raw string length is used.

Known callers:
- Internal formatting and rendering routines inside the pretty_printers module that need to compute layout widths, alignment paddings, or width-based truncation. These callers typically invoke this function after tokenization and before final rendering to determine column widths or to align multi-column outputs.

Why this logic is extracted:
- Encapsulates the precise rule set for how whitespace and newline tokens contribute to printed width (space -> underscore, tab -> backslash+t, carriage-return -> backslash+r, and newlines removed for these token types). Extracting it prevents duplication of the exact transformation and length-calculation logic across multiple renderers and centralizes behavior for easier maintenance and testing.

## Args:
    tokens (List[_PrettyToken]): Sequence of tokens to measure.
        - Each token is expected to be an object with attributes:
            - .type: a member of _PrettyTokenType (e.g., WHITESPACE, NEWLINE, BODY, etc.).
            - .value: a str containing the token's text content.
        - Allowed values:
            - An empty list is allowed and yields 0.
            - Tokens may contain any characters including spaces, tabs, carriage returns, and newlines.
        - Interdependencies:
            - The behavior depends on .type: only tokens whose type is _PrettyTokenType.WHITESPACE or _PrettyTokenType.NEWLINE are transformed with the visible-whitespace mapping and have newline characters removed prior to length measurement.

## Returns:
    int: Non-negative integer representing the sum of measured character widths for all tokens in the input sequence according to the pretty-printer's visible-whitespace rules.
    - For a non-whitespace token, the contribution is len(token.value).
    - For WHITESPACE or NEWLINE tokens, the contribution is len(_replace_whitespace(token.value).replace('\n', '')) — i.e., measure after replacing spaces/tabs/carriage-returns with visible sequences and removing newline characters.
    - Edge cases:
        - Empty tokens list -> 0.
        - Tokens whose .value is an empty string contribute 0.
        - Newline characters that occur inside WHITESPACE or NEWLINE tokens do not contribute to the returned length because they are removed before counting.

## Raises:
    TypeError:
        - If the provided tokens argument is not iterable (e.g., None), the attempt to iterate will raise TypeError (e.g., "'NoneType' object is not iterable").
    AttributeError:
        - If an element in tokens does not expose .type or .value attributes, attribute access will raise AttributeError.
        - If token.value is not a string-like object and _replace_whitespace is invoked on it (for WHITESPACE/NEWLINE types), _replace_whitespace or the subsequent .replace('\n', '') call may raise AttributeError because the value does not implement the string replace method.
    Note: The function does not catch these exceptions; they propagate to the caller.

## Constraints:
    Preconditions:
        - Each element of tokens should be a _PrettyToken (or an equivalent object) whose .type is a member of _PrettyTokenType and .value is a str. This ensures predictable behavior from _replace_whitespace and from len().
    Postconditions:
        - The return value is an integer >= 0.
        - Calling this function has no side effects: it does not mutate tokens or global state.

## Side Effects:
    - None. The function performs only local computation and does not perform I/O, mutate input tokens, or call external services.

## Control Flow:
flowchart TD
    Start([Start]) --> Init[set result = 0]
    Init --> ForEach{for each token in tokens}
    ForEach --> CheckType{token.type in (WHITESPACE, NEWLINE)?}
    CheckType -- Yes --> Transform[_replace_whitespace(token.value)]
    Transform --> RemoveNewline[call .replace('\n', '') on transformed text]
    RemoveNewline --> AddLen1[add len(transformed_without_newlines) to result]
    CheckType -- No --> AddLen2[add len(token.value) to result]
    AddLen1 --> ForEach
    AddLen2 --> ForEach
    ForEach --> End[return result]

## Examples:
Example 1 — basic mixed tokens:
- Input tokens:
    - _PrettyToken(_PrettyTokenType.BODY, "ab")
    - _PrettyToken(_PrettyTokenType.WHITESPACE, " \t")
    - _PrettyToken(_PrettyTokenType.NEWLINE, "\n")
- Measurement steps:
    - BODY contributes len("ab") = 2
    - WHITESPACE: " \t" -> spaces become "_" and tab becomes "\t" (two characters), yielding "_" + "\\t" whose length is 3
    - NEWLINE: "\n" -> transformed remains "\n" and then newline is removed -> "" contributes 0
- Result: 2 + 3 + 0 = 5

Example 2 — empty list:
- Input tokens: []
- Result: 0

Example 3 — token values containing carriage return:
- Input token: _PrettyToken(_PrettyTokenType.WHITESPACE, "x\r y")
- Transformation: "\r" -> "\\r" (two characters), spaces -> "_", so measured string length accounts for these visible substitutions; any '\n' characters would be removed prior to counting.

Example 4 — error handling:
- If tokens is None, a TypeError from iterating None is raised.
- If a token lacks .value or .type, an AttributeError is raised when those attributes are accessed.

## `onlinejudge_command.pretty_printers._tokens_from_line_diff_ops` · *function*

*No documentation generated.*

## `onlinejudge_command.pretty_printers._summary_token_of_diff_ops` · *function*

## Summary:
Produce a compact summary token (or none) that reports how many lines were deleted and added across a sequence of merged diff operations.

## Description:
This function scans a list of merged-diff operation objects and produces either an empty list (no summary required) or a singleton list containing one hint token that reports the total number of deleted and added lines found in the provided operations.

Known callers within the codebase:
- No direct callers were found in the provided snapshot. Conceptually, this helper is intended for the pretty-printer / diff-summary stage of the output formatting pipeline: after detailed per-line tokens or highlights are generated, callers may call this function to append a concise summary hint when there are changed lines that are not expanded inline.

Why this logic is extracted:
- Centralizes the simple counting-and-formatting responsibility so token-generation code does not duplicate logic.
- Keeps the textual phrasing for the summary in one place for easy updates.
- Separates concerns: callers prepare merged diff ops; this function only interprets them and decides whether to emit a single hint token.

## Args:
- ops (List[_MergedDiffOp]):
  - Type: iterable (typically a list) of objects representing merged diff operations.
  - Required attributes on each element:
    - has_diff: bool-like indicating whether this operation contains a difference. Only operations where has_diff is truthy are considered for counting.
    - left_lineno: integer or None. A non-None value indicates presence on the left/original side and causes the function to count one deleted line.
    - right_lineno: integer or None. A non-None value indicates presence on the right/modified side and causes the function to count one added line.
  - Interdependencies:
    - An operation may increment both removed and added counts if both left_lineno and right_lineno are non-None and has_diff is truthy.
    - The function performs no type coercion beyond testing for None; callers should provide line numbers in conventional numeric forms if downstream consumers expect integers.

## Returns:
- List[_PrettyToken]:
  - If both removed and added counts are zero, the function returns an empty list [].
  - Otherwise, the function returns a list with exactly one _PrettyToken:
    - .type: the _PrettyTokenType enum member named HINT — i.e., the actual singleton enum object that callers obtain via attribute access (_PrettyTokenType.HINT). This is the enum member object itself, not a plain string.
    - .value: the literal string formatted as:
      (also {removed} lines are deleted and {added} lines are added...)
      where {removed} and {added} are decimal integer counts computed from ops.
  - Notes:
    - There is no pluralization or localization — the same phrase is used even when a count equals 1.
    - The function never returns more than one token.

## Raises:
- The function does not deliberately raise exceptions.
- Possible runtime exceptions if preconditions are violated:
  - AttributeError if an element of ops lacks has_diff, left_lineno, or right_lineno attributes.
  - TypeError if ops is not iterable.
  - If _PrettyToken construction imposed constraints in another version, invalid inputs there could raise additional exceptions; under normal module usage this does not occur.

## Constraints:
- Preconditions:
  - ops must be iterable and its elements must expose has_diff, left_lineno, and right_lineno via attribute lookup.
  - left_lineno and right_lineno are interpreted only for None-ness; they do not need to be validated as integers by this function.
- Postconditions:
  - If the function returns [], then across ops there were no elements with has_diff truthy that contributed non-None left_lineno or right_lineno.
  - If the function returns a singleton list, that token's .type is the singleton enum member corresponding to HINT (accessible as _PrettyTokenType.HINT) and its .value encodes the integer counts used to decide to produce the token.

## Side Effects:
- None. The function performs no I/O, does not mutate ops, and does not modify global state.

## Control Flow:
flowchart TD
    Start([Start: receive ops])
    Start --> Init[removed = 0, added = 0]
    Init --> Loop[for each op in ops]
    Loop --> HasDiff{op.has_diff ?}
    HasDiff -->|no| NextOp[continue]
    HasDiff -->|yes| CheckLeft[op.left_lineno is not None ?]
    CheckLeft -->|yes| IncRemoved[removed += 1]
    CheckLeft -->|no| SkipRemoved
    IncRemoved --> CheckRight
    SkipRemoved --> CheckRight
    CheckRight -->|yes| IncAdded[added += 1]
    CheckRight -->|no| SkipAdded
    IncAdded --> NextOp
    SkipAdded --> NextOp
    NextOp --> Loop
    Loop --> AfterLoop{removed == 0 and added == 0 ?}
    AfterLoop -->|yes| ReturnEmpty[return []]
    AfterLoop -->|no| ReturnHint[return [HINT token with formatted summary]]
    ReturnEmpty --> End([Finish])
    ReturnHint --> End

## Examples:
- No diffs:
  - If ops is empty or contains no element with has_diff truthy, the function returns [].

- Some diffs:
  - Given three ops where two have has_diff true and only left_lineno present, and one has has_diff true and only right_lineno present, removed = 2 and added = 1. The function returns:
    [_PrettyToken(_PrettyTokenType.HINT, '(also 2 lines are deleted and 1 lines are added...)')]

- Malformed input:
  - If an element lacks the required attributes, callers will see an AttributeError; callers that may receive heterogeneous inputs should validate elements before calling this helper.

## `onlinejudge_command.pretty_printers._tokenize_pretty_diff` · *function*

## Summary:
Generate a sequence of pretty-printer tokens that represent a human-friendly diff between two text contents, optionally truncating the expanded diff and appending a compact summary token for the hidden remainder.

## Description:
This helper performs the tokenization stage of the pretty-printer diff pipeline: it computes a line-oriented diff between the actual output and the expected text (using the module's diff dispatcher), post-processes/merges the raw diffs to include a few surrounding context lines and visual gap markers, converts the resulting per-line merged diff operations into _PrettyToken tokens suitable for rendering, and optionally appends a compact summary token for any operations omitted due to truncation.

Known callers and typical context:
- Internal callers are other functions inside onlinejudge_command.pretty_printers that prepare user-facing colored/annotated diffs for test failures or output comparisons. Typical usage is in the final formatting stage of a failure-reporting pipeline after actual and expected outputs are available and a CompareMode has been chosen.
- Typical trigger: invoked when a human-readable diff is required (for example, after check_lines_match determines outputs do not match).

Why this logic is a dedicated function:
- It isolates the tokenization orchestration (diff selection → context expansion → gap insertion → line→token translation → optional summary) so callers need only provide inputs and rendering parameters and receive a ready-to-render token sequence.
- Delegates specialized tasks to smaller helpers (_make_diff_between_file_and_file, _add_lines_around_diff_lines, _add_dots_between_gaps, _tokens_from_line_diff_ops, _summary_token_of_diff_ops) and enforces the high-level flow and truncation contract.

## Args:
- output (str):
    - The actual output text (right/modified side) to compare. Must be a Python str containing the full contents (may include newlines).
    - Not mutated by this function; passed to helpers for diffing and context merging.

- expected (str) (keyword-only):
    - The expected output text (left/original side). Must be a Python str.
    - Not mutated by this function; passed to helpers.

- compare_mode (CompareMode) (keyword-only):
    - One of the CompareMode enum members (onlinejudge_command.output_comparators.CompareMode).
    - Special handling: if compare_mode is CompareMode.IGNORE_SPACES_AND_NEWLINES, the function downgrades it to CompareMode.IGNORE_SPACES and emits a logger.warning about the downgrade before continuing. The (possibly-downgraded) value is forwarded to _make_diff_between_file_and_file.
    - Note: other warnings and behaviors related to compare_mode (e.g., CRLF normalization) are performed inside the diff helper called by this function.

- char_in_line (int) (keyword-only):
    - An integer forwarded to the _tokens_from_line_diff_ops helper.
    - Interpretation: the maximum number of characters per line used by tokenization/wrapping logic is determined by the tokenization helper; this parameter configures that behavior. Callers should provide a non-negative integer; typical callers pass the terminal width or a configured wrap width.
    - The exact semantics for zero or small values are defined by _tokens_from_line_diff_ops; this function simply forwards the value.

- limit (int) (keyword-only):
    - Truncation control for the number of merged diff operations that are expanded into detailed tokens.
    - Semantics: -1 means "no limit" (all merged operations are tokenized). Any other integer N is used as a Python slice index:
        * merged_ops[:N] — the first N merged diff operations are converted to tokens via _tokens_from_line_diff_ops.
        * merged_ops[N:] — the remainder is not expanded inline; instead it is summarized by calling _summary_token_of_diff_ops(merged_ops[N:]) and appending its returned token(s) (if any) to the final token list.
    - Edge behavior: limit == 0 produces zero expanded lines and the full merged_ops are passed to the summarizer (so the summary may reflect all changes). Negative values other than -1 are treated according to standard Python slicing semantics (but callers should use -1 for unlimited).

## Returns:
- List[_PrettyToken]
    - A flat list of _PrettyToken instances representing:
        1. The tokenized form of the merged diff operations for the expanded prefix (merged_ops[:limit] when limit != -1, otherwise all merged_ops).
        2. If limit != -1, any tokens returned by _summary_token_of_diff_ops for the omitted suffix merged_ops[limit:]; typically this is either [] or a singleton list containing one HINT token describing counts of removed/added lines.
    - The returned token sequence is ready for the module's renderers: renderers decide colors/prefixes based on each token's .type and print token.value.
    - Possible empty return: when there are no merged diff operations or when tokenization yields no tokens, the function may return an empty list [].

## Raises:
- Propagated exceptions from delegated helpers:
    - AssertionError, TypeError, AttributeError, or other exceptions raised by any helper (for example, if non-str arguments are passed, or if a helper validates inputs and raises).
    - This function itself only explicitly uses logger.warning and assignments; it does not raise new exceptions beyond those propagated from called helpers.
- No exceptions are raised merely because limit == -1 (that is the unlimited sentinel).

## Constraints:
- Preconditions:
    - output and expected must be Python str instances containing the full textual contents to compare.
    - compare_mode must be a CompareMode member; CompareMode.IGNORE_SPACES_AND_NEWLINES is accepted here but downgraded (and a warning is emitted). Other invalid values for compare_mode will be handled or cause errors in the diff helper.
    - char_in_line should be an integer; the semantic requirement (non-negative, non-zero, etc.) is enforced or assumed by the tokenization helper.
- Postconditions:
    - The returned tokens represent the diff of the provided texts according to the (possibly adjusted) compare_mode and the module's diff/tokenization logic.
    - No input objects (output, expected) are mutated by this function.

## Side Effects:
- Logging:
    - If compare_mode is CompareMode.IGNORE_SPACES_AND_NEWLINES, emits a logger.warning describing that the requested mode is ignored and CompareMode.IGNORE_SPACES is used instead.
    - Additional warnings or informational logs may be emitted by _make_diff_between_file_and_file (e.g., CRLF normalization warnings) and other helpers; those are side effects of their behavior and propagate.
- No file, network, or stdout/stderr I/O is performed by this function itself (beyond logging). The function does not mutate global state.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> CheckMode{compare_mode == IGNORE_SPACES_AND_NEWLINES?}
    CheckMode -- Yes --> WarnDowngrade[logger.warning(downgrade to IGNORE_SPACES)] --> SetMode[compare_mode = IGNORE_SPACES]
    CheckMode -- No --> Continue
    SetMode --> CallDiff
    Continue --> CallDiff[_make_diff_between_file_and_file(output, expected, compare_mode=compare_mode)]
    CallDiff --> Ops[ops returned (List[_LineDiffOp])]
    Ops --> AddContext[_add_lines_around_diff_lines(output, expected, ops=ops, size=4) -> merged_ops]
    AddContext --> AddDots[_add_dots_between_gaps(output, expected, ops=merged_ops) -> merged_ops]
    AddDots --> TruncateCheck{limit == -1?}
    TruncateCheck -- Yes --> ToToken[_tokens_from_line_diff_ops(merged_ops, char_in_line=char_in_line) -> tokens]
    TruncateCheck -- No --> SliceAndToken[_tokens_from_line_diff_ops(merged_ops[:limit], char_in_line=char_in_line) -> tokens_partial]
    SliceAndToken --> Summary[_summary_token_of_diff_ops(merged_ops[limit:]) -> summary_tokens]
    Summary --> Concat[tokens = tokens_partial + summary_tokens]
    Concat --> Return([return tokens])
    ToToken --> Return

## Examples:
1) Typical usage where full diff is rendered:
- Given actual output and expected strings and wanting full expansion:
  - Provide limit = -1 (unlimited) and a reasonable char_in_line (for example, terminal width).
  - The function returns tokens for all merged diff operations with no appended summary token.

2) Truncated diff with summary:
- When very long diffs should be compacted in the UI, set limit to an integer N (e.g., 40). The function will expand only the first N merged diff operations and will append a single HINT token (if there are omitted diffs) describing how many lines were deleted/added in the hidden suffix; the summary token is generated by _summary_token_of_diff_ops.

3) Edge-case: limit == 0
- No merged diff operations are expanded inline (the expanded tokens list is empty), and the summary token (if any) summarizes all merged operations.

4) Handling an unsupported compare mode requested by caller
- If the caller passes CompareMode.IGNORE_SPACES_AND_NEWLINES, the function does not raise; instead it logs a warning and continues with CompareMode.IGNORE_SPACES. (Lower-level helpers may log further messages depending on text content.)

Notes:
- This function is a coordinating wrapper; to understand the detailed token types and how char_in_line affects output, consult the documentation for:
    - _make_diff_between_file_and_file
    - _add_lines_around_diff_lines
    - _add_dots_between_gaps
    - _tokens_from_line_diff_ops
    - _summary_token_of_diff_ops
- The returned tokens are intended for consumption by the module's renderer which maps _PrettyToken.type to colors and prefixes.

## `onlinejudge_command.pretty_printers.make_pretty_diff` · *function*

## Summary:
Produce a terminal-ready, human-friendly diff string by safely decoding raw bytes, tokenizing a line-oriented diff against the expected text, and rendering the resulting tokens.

## Description:
This function orchestrates the three-stage pipeline required to present a pretty diff from raw bytes:
1. Decode the raw bytes into a Unicode string and collect any decoding diagnostic tokens via _decode_with_recovery.
2. Obtain a terminal width (via _get_terminal_size) and forward the decoded text, expected text, compare_mode, width, and truncation limit to _tokenize_pretty_diff to obtain diff tokens.
3. Render the combined sequence of diagnostic and diff tokens into a single string using _render_tokens and return it.

Known callers:
- No direct call sites were discovered in the available snapshot. Typical callers include failure-reporting code and command handlers that need to display differences between captured program output (bytes) and an expected string. The usual trigger is: after a comparison detects a mismatch (for example, check_lines_match returns False or a CompareMode-based comparator indicates differences), call make_pretty_diff to obtain a human-readable diff for logging or printing.

Why this is a separate function:
- It centralizes the orchestration of decoding, tokenization, and rendering so callers need only supply raw bytes and comparison parameters to get a fully formatted diff string. This keeps caller code simple and ensures consistent treatment of decoding diagnostics, terminal width, and truncation semantics.

## Args:
    output_bytes (bytes):
        - Raw bytes produced by an external source (subprocess stdout, file contents, captured network payload).
        - Must be a bytes-like object with a .decode method. Passing non-bytes may lead to AttributeError or TypeError from underlying helpers.
    expected (str) (keyword-only):
        - The expected text to compare against; must be a Python str.
    compare_mode (CompareMode) (keyword-only):
        - A CompareMode enum member describing comparison semantics (see onlinejudge_command.output_comparators.CompareMode).
        - Note: any compare-mode normalization or downgrade (for example, IGNORE_SPACES_AND_NEWLINES → IGNORE_SPACES) is performed by the tokenizer _tokenize_pretty_diff; make_pretty_diff forwards the provided value unchanged.
    limit (int) (keyword-only):
        - Truncation control forwarded to the tokenizer:
            * -1: unlimited — expand all merged diff operations inline.
            * N >= 0: expand at most the first N merged diff operations; remaining operations are summarized.
        - The limit value is passed verbatim to _tokenize_pretty_diff and follows Python slicing semantics.

## Returns:
    str
    - A single string containing the rendered representation of the decoding diagnostics (if any) followed by the tokenized diff rendered for terminal display.
    - Characteristics:
        * Always returns a Python str.
        * May include ANSI escape sequences when default color/font functions are used by _render_tokens.
        * If no tokens are produced (no diagnostics and no diff), returns the empty string.
        * If tokenization produced a summary token due to truncation, that summary is included in the rendered string.

## Raises:
    - Propagated exceptions from underlying helpers (make_pretty_diff itself does not explicitly raise new exceptions):
        * AttributeError / TypeError: if output_bytes is not bytes-like and .decode access/call fails (originating from _decode_with_recovery).
        * Any exception raised by shutil.get_terminal_size() will propagate through _get_terminal_size (for example, OSError in unusual environments).
        * AssertionError: may be raised by _render_tokens if a token with an unknown token type is encountered (this assertion enforces tokenizer/renderer agreement).
        * TypeError or other runtime errors: may be raised by font callables invoked inside _render_tokens if callers supplied invalid font_* values (for example, a non-callable).
        * Any other exceptions raised by _tokenize_pretty_diff or its delegated helpers will propagate (for example, if invalid argument types are passed).
    - Note: UnicodeDecodeError will not propagate under normal operation because _decode_with_recovery converts decoding failures into a diagnostic token and a replacement-decoded string.

## Constraints:
Preconditions:
    - output_bytes should be a bytes-like object expected to represent text.
    - expected must be a str.
    - compare_mode should be a CompareMode enum member.
    - limit must be an int (use -1 for unlimited).
Postconditions:
    - Returns a str representing the rendered tokens returned by helpers.
    - Does not mutate input objects.
    - Any decoding diagnostic token produced by _decode_with_recovery is included in the rendered output.

## Side Effects:
    - make_pretty_diff itself performs no I/O and does not mutate global state.
    - Indirect side effects may include:
        * Logging emitted by helpers (for example, _tokenize_pretty_diff may log warnings if it downgrades an unsupported compare mode).
        * A system query for terminal size via shutil.get_terminal_size() inside _get_terminal_size (this is an environment inquiry but not a state mutation).
    - The returned string may contain ANSI escape sequences; printing it to a terminal will affect terminal appearance while displayed.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> Decode[_decode_with_recovery(output_bytes) -> (tokens, output)]
    Decode --> GetWidth[_get_terminal_size() -> char_in_line]
    GetWidth --> Tokenize[_tokenize_pretty_diff(output, expected=expected, compare_mode=compare_mode, char_in_line=char_in_line, limit=limit) -> diff_tokens]
    Tokenize --> Concat[tokens += diff_tokens]
    Concat --> Render[_render_tokens(tokens=tokens) -> final_str]
    Render --> Return([return final_str])
    Return --> End([End])

## Examples:
1) Basic usage (conceptual):
    - Inputs:
        * output_bytes = b"foo\\nbar\\n"
        * expected = "foo\\nqux\\n"
        * compare_mode = CompareMode.STRICT
        * limit = -1
    - Behavior:
        * Decodes bytes to "foo\nbar\n" with no diagnostics.
        * Tokenizes the diff between "foo\nbar\n" and "foo\nqux\n".
        * Renders and returns a string containing the formatted diff (may include ANSI escapes).

2) Decoding fallback (conceptual):
    - Inputs:
        * output_bytes contains invalid bytes (e.g., b"ok\\xff\\nend\\n")
        * expected is a str
    - Behavior:
        * _decode_with_recovery returns a HINT token describing the UnicodeDecodeError and a replacement-decoded string.
        * The HINT token is included in the token sequence; the final returned string contains the decoded-output diff and the diagnostic hint (styled by _render_tokens).

3) Truncated diff with summary (conceptual):
    - Inputs:
        * Very long outputs and limit = 50
    - Behavior:
        * _tokenize_pretty_diff expands up to the first 50 merged diff operations and appends a summary token for the omitted remainder.
        * Returned string contains the expanded prefix and the summary hint.

Implementation notes for reimplementation:
    - Implement these three steps in order: safe decode-with-diagnostic, terminal-width acquisition with a sensible minimum, and tokenization/render pipeline.
    - Ensure decoding errors are converted into a diagnostic token plus a replacement-decoded string (do not let UnicodeDecodeError propagate).
    - Forward compare_mode exactly to the tokenizer; let the tokenizer decide and log any mode downgrades.
    - Respect the limit sentinel (-1) as unlimited and otherwise pass limit directly to the tokenization stage.
    - Allow exceptions from helpers to propagate so callers can handle them; explicitly document the common propagated exceptions (AssertionError from renderer on unknown token types, TypeError from font callables, OS-level errors from terminal-size queries).

