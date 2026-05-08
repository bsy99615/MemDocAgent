# `search.py`

## `flower.utils.search.parse_search_terms` · *function*

## Summary:
Parses a user-provided search string into a structured dictionary of search tokens (result, args, kwargs, state, any) by splitting on spaces/commas while respecting quoted substrings and normalizing each token.

## Description:
This function accepts a single raw search string and returns a dictionary mapping specific token types to their normalized values:
- result: a single normalized value (last occurrence wins)
- args: ordered list of normalized positional argument tokens
- kwargs: mapping of normalized keyword names to normalized values (invalid pairs are skipped)
- state: ordered list of normalized state tokens
- any: a single normalized token used when the part does not match any other prefix (last occurrence wins)

Known callers within the codebase:
- None discovered in the current scan.

Typical usage/context:
- Called to transform a free-form search input (for example, typed into a UI or received via an API) into structured criteria that the application can use to filter or match items. This logic is extracted so tokenization, prefix handling, and normalization are centralized and not duplicated by callers.

Why this is a separate function:
- Encapsulates tokenization and prefix-based dispatching into a single reusable unit.
- Keeps higher-level logic focused on applying the parsed criteria rather than parsing details.
- Centralizes handling of quoted tokens, multiple args, kwargs parsing and invalid-pair skipping.

## Args:
    raw_search_value (str | Any):
        The raw search input to parse. Expected to be a text string containing tokens separated by spaces or commas; tokens containing spaces may be wrapped in double quotes.
        - If a falsy value is passed (None, '', False, empty containers), the function returns an empty dict.
        - If a non-str truthy object is passed, the function will still attempt to iterate the object via the regex; this is implementation-defined and callers should pass str.

## Returns:
    dict:
        A dictionary with zero or more of the following keys (only present if tokens produce them):
        - 'result' -> str
            The last normalized value from a token starting with "result:". If present multiple times, the last occurrence overwrites previous ones.
        - 'args' -> list[str]
            List of normalized values from tokens with prefix "args:". Preserves order of occurrence.
        - 'kwargs' -> dict[str, str]
            Mapping of keyword name to normalized value from tokens with prefix "kwargs:". Tokens without a single '=' separator are ignored. If the same key appears multiple times, later entries overwrite earlier ones.
        - 'state' -> list[str]
            List of normalized state values from tokens starting with "state" (note: the matching tests startswith 'state', not strictly 'state:'), appended in order of occurrence.
        - 'any' -> str
            The last normalized token that did not match any of the above prefixes.
        - If raw_search_value is falsy, the function returns an empty dict {}.

    Normalization:
        Each extracted value is passed through preprocess_search_value which strips surrounding double quotes and spaces and converts falsy inputs into the empty string.

## Raises:
    - ValueError:
        Not raised by this function directly, but the code handles ValueError when splitting kwargs tokens. Specifically, when a token with prefix 'kwargs:' does not split into exactly two parts on '=', the split assignment triggers ValueError and the token is skipped.
    - Exceptions propagated from preprocess_search_value:
        preprocess_search_value can raise AttributeError or TypeError if given a truthy object that does not support or is incompatible with .strip('" '). Those exceptions are not caught here and will propagate to the caller.

## Constraints:
Preconditions:
    - Prefer passing a str. The function assumes textual input and uses regular expression tokenization that expects strings.
    - The regex implementation uses re.findall on the provided input; passing non-str types may lead to TypeError at the regex call or unexpected behavior.

Postconditions:
    - Returns a dictionary containing only the keys produced by parsed tokens; no mutation of external state occurs.
    - For tokens recognized as kwargs but malformed (no single '='), those tokens are silently ignored.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or external resources. It only returns a new dict constructed from the parsed tokens.

## Control Flow:
flowchart TD
    Start([Start parse_search_terms])
    CheckFalsy{raw_search_value is falsy?}
    ReturnEmpty[Return {}]
    Tokenize[/re.findall(search_regexp, raw_search_value)/]
    Loop[For each query_part]
    SkipEmpty{query_part is empty?}
    PrefixResult{Starts with 'result:'?}
    SetResult[parsed_search['result']=preprocess_search_value(...)]
    PrefixArgs{Starts with 'args:'?}
    AppendArg[Ensure 'args' list exists; append(preprocess_search_value(...))]
    PrefixKw{Starts with 'kwargs:'?}
    EnsureKw[Ensure 'kwargs' dict exists]
    SplitKw[Try key,value = split('=')]
    SkipKwInvalid[On ValueError -> continue]
    SetKw[parsed_search['kwargs'][key]=preprocess_search_value(value)]
    PrefixState{Starts with 'state'?}
    AppendState[Ensure 'state' list exists; append(preprocess_search_value(...))]
    ElseAny[parsed_search['any']=preprocess_search_value(query_part)]
    End[Return parsed_search]
    Start --> CheckFalsy
    CheckFalsy -- True --> ReturnEmpty
    CheckFalsy -- False --> Tokenize
    Tokenize --> Loop
    Loop --> SkipEmpty
    SkipEmpty -- True --> Loop
    SkipEmpty -- False --> PrefixResult
    PrefixResult -- True --> SetResult --> Loop
    PrefixResult -- False --> PrefixArgs
    PrefixArgs -- True --> AppendArg --> Loop
    PrefixArgs -- False --> PrefixKw
    PrefixKw -- True --> EnsureKw --> SplitKw
    SplitKw --> |ValueError| SkipKwInvalid --> Loop
    SplitKw --> |Success| SetKw --> Loop
    PrefixKw -- False --> PrefixState
    PrefixState -- True --> AppendState --> Loop
    PrefixState -- False --> ElseAny --> Loop
    Loop --> End

## Examples:
1) Basic tokens
    Input: 'result:success args:123 args:"multi word arg" kwargs:key=value anytoken'
    Output:
    {
      'result': 'success',
      'args': ['123', 'multi word arg'],
      'kwargs': {'key': 'value'},
      'any': 'anytoken'
    }

2) Quoted token with spaces and escaped content
    Input: 'args:"a \\"quoted\\" arg"'
    Behavior: The regex keeps the quoted token intact; preprocess_search_value removes the outer quotes and surrounding spaces so the resulting arg is: 'a \"quoted\" arg'
    Output:
    {
      'args': ['a \\"quoted\\" arg']
    }

3) Multiple kwargs and malformed kwargs
    Input: 'kwargs:one=1 kwargs:badpair kwargs:two=2'
    Behavior: 'kwargs:badpair' does not contain '=', split raises ValueError and that token is skipped.
    Output:
    {
      'kwargs': {'one': '1', 'two': '2'}
    }

4) State prefix variations
    Input: 'state:running state:idle state'
    Behavior: The function checks startswith('state') and slices using len('state:'), so:
      - 'state:running' -> 'running'
      - 'state:idle'    -> 'idle'
      - 'state'         -> slice yields '' which preprocess_search_value converts to ''
    Output:
    {
      'state': ['running', 'idle', '']
    }

5) Empty input
    Input: ''
    Output: {}

6) Error propagation from preprocess_search_value (unlikely with string inputs)
    If preprocess_search_value raises (e.g., caller passes a non-str object that causes .strip to raise), that exception will propagate out of parse_search_terms. Callers should validate input types if they expect to handle such errors.

Notes and implementation details to consider when reimplementing:
- The tokenization regex: r'(?:[^\s,"]|"(?:\\.|[^"])*")+' splits by whitespace and commas but keeps quoted substrings (an inner quoted substring may contain escaped characters).
- 'state' uses startswith('state') — it is not strictly guarding for a colon; the slice uses len('state:') which expects a colon; this results in an empty-string token if the raw token is exactly 'state'.
- 'any' and 'result' keys are overwritten by later tokens of the same category; args/state accumulate; kwargs accumulate into a dict with later keys overwriting earlier ones for identical keys.

## `flower.utils.search.satisfies_search_terms` · *function*

*No documentation generated.*

## `flower.utils.search.stringified_dict_contains_value` · *function*

## Summary:
Determines whether a string representation of a dictionary-like fragment contains a given key whose associated value, when converted to a string and stripping surrounding quotes, equals the provided value.

## Description:
Known callers:
    - No direct callers were discovered in the repository during documentation generation. This helper is typically used by search or filter utilities that need to inspect textual/serialized dictionary fragments embedded in logs, metadata strings, or simple textual records.

Responsibility:
    - Encapsulates fragile index-based parsing to locate a key in a stringified dict fragment and compare its textual value with a provided value. It is intentionally small and brittle: it is designed for simple, predictable stringified dicts (e.g., standard Python repr or small JSON-like fragments) rather than arbitrary or deeply-nested serialized data.

Why a separate function:
    - Centralizes the substring/index arithmetic, quote stripping, and error handling so callers avoid duplicating brittle logic and can handle exceptions in one place.

## Args:
    key (str)
        - The literal key substring to search for inside str_dict (without adding quotes).
        - Must be a str; if not, behavior is determined by Python's str.index when called with a non-str key (likely TypeError).
    value (Any)
        - The expected value to compare against the extracted textual value. The function converts this to str(value) before comparison.
        - Accepts any object with a meaningful str() representation (e.g., str, int, float).
    str_dict (str)
        - A string containing a dictionary-like fragment such as "{'foo': 'bar', 'baz': 2}" or '{"foo": "bar"}'.
        - If falsy (None, '', etc.) the function returns False immediately.
        - Must support str.index and slicing (i.e., be a str or str-like object). If it does not, the function may raise AttributeError/TypeError.

Interdependencies:
    - The function searches for the first occurrence of key in str_dict and uses that occurrence to compute the value slice. If key occurs multiple times, only the first occurrence is considered.
    - value is compared after conversion with str(); the comparison is exact string equality after removing surrounding single or double quotes from the extracted text.

## Returns:
    bool
        - True if:
            * key is found in str_dict, and
            * the substring extracted as the corresponding value (after removing surrounding double or single quotes) equals str(value).
        - False if:
            * str_dict is falsy, or
            * key is not found, or
            * the extracted (quote-stripped) value does not equal str(value).

Edge-case returns:
    - The function never returns None; it always returns a boolean except when an unhandled exception is raised (see Raises).

## Raises:
    ValueError
        - Occurs when key is found but neither a comma (',') nor a closing brace ('}') is present after the computed start-of-value index:
            * The function first attempts str_dict.index(',', key_index). If no comma is found it calls str_dict.index('}', key_index). If that second index call fails, Python raises ValueError which propagates out of the function.
    AttributeError or TypeError
        - If str_dict is not a str-like object (missing .index or not slicable) these exceptions may be raised by .index or slicing operations and are not caught.

## Constraints:
Preconditions:
    - str_dict should contain entries in a conventional "key: value" layout where the key occurrence appears in the form quoted-key followed by a colon and (typically) a single space before the value. The implementation assumes a formatting offset of +3 characters beyond the end of key (see Implementation detail below).
    - key must be present exactly as provided (the function does not add or normalize quoting around key).

Postconditions:
    - No inputs are mutated; no external state is changed.
    - The function returns True only if exact string equality between the extracted value (quote-stripped) and str(value) holds.

Implementation detail (why + len(key) + 3):
    - After locating key via str.index(key), the code computes key_index = index(key) + len(key) + 3. This offset assumes the key in the string is formatted like "'key': " or "\"key\": " — i.e. there is a closing quote, a colon, and one separating space after the colon. The computed key_index typically points to either the opening quote of a quoted value or the first digit/character of an unquoted value. If the source formatting omits the space or uses different spacing, the slicing may include or skip an extra character.

Limitations:
    - Uses the first occurrence of key; duplicate or nested uses of the same key can cause incorrect matches.
    - Not a full parser: commas inside nested structures or values containing commas may cause premature slicing at the first comma found after key_index.
    - Whitespace variance or unexpected formatting may change slice boundaries.

## Side Effects:
    - None. No I/O, no global state mutation, no external service calls.

## Control Flow:
flowchart TD
    Start --> CheckFalsy{Is str_dict falsy?}
    CheckFalsy -- Yes --> ReturnFalse1[Return False]
    CheckFalsy -- No --> Convert[Convert value -> str(value)]
    Convert --> FindKey[Find first occurrence of key in str_dict]
    FindKey --> KeyFound{Found?}
    KeyFound -- No --> ReturnFalse2[Return False]
    KeyFound -- Yes --> ComputeIndex[Compute key_index = index(key) + len(key) + 3]
    ComputeIndex --> FindComma[Try find ',' after key_index]
    FindComma -- Found --> comma_index[comma_index = index(',')]
    FindComma -- NotFound --> FindBrace[Try find '}' after key_index]
    FindBrace -- Found --> brace_index[comma_index = index('}')]
    FindBrace -- NotFound --> RaiseVE[Raises ValueError]
    comma_index --> Extract[Extract substring = str_dict[key_index:comma_index]]
    brace_index --> Extract
    Extract --> Strip[Strip surrounding single/double quotes from substring]
    Strip --> Compare{Does str(value) == substring?}
    Compare -- Yes --> ReturnTrue[Return True]
    Compare -- No --> ReturnFalse3[Return False]

## Examples:
Example 1 — quoted string value (match):
    Input:
        key = 'foo'
        value = 'bar'
        str_dict = "{'foo': 'bar', 'baz': 2}"
    Rationale:
        - index('foo') locates the key; computed slice yields "'bar'" which is stripped to "bar".
        - str('bar') == "bar" -> function returns True.

Example 2 — numeric value (match):
    Input:
        key = 'baz'
        value = 2
        str_dict = "{'foo': 'bar', 'baz': 2}"
    Rationale:
        - Computed slice yields "2" (no surrounding quotes). str(2) == "2" -> function returns True.

Example 3 — missing key (no match):
    Input:
        key = 'missing'
        value = 'x'
        str_dict = "{'foo': 'bar'}"
    Result:
        - key not found -> function returns False.

Example 4 — malformed fragment (raises ValueError):
    Input:
        key = 'k'
        value = 'v'
        str_dict = "{'k': 'v'   "  (missing trailing '}' and no comma)
    Result:
        - The attempt to find ',' after key_index fails and the subsequent attempt to find '}' also fails -> str.index('}', key_index) raises ValueError which propagates to the caller.
    Guidance:
        - Callers that may supply malformed fragments should wrap calls in try/except ValueError.

Reimplementation guidance:
    - If you need robust behavior for all JSON-like inputs or nested structures, parse using json.loads (after normalizing quotes) or use an actual parser rather than relying on index arithmetic.

## `flower.utils.search.preprocess_search_value` · *function*

## Summary:
Normalizes a user-provided search token by removing surrounding double-quote characters and spaces; returns an empty string for falsy inputs.

## Description:
This helper isolates the small, well-defined transformation applied to raw search inputs: if the provided value is truthy, it strips leading and trailing double-quote characters (") and space characters; otherwise it yields an empty string. No other characters are removed, and interior characters (including other quote types or whitespace inside the string) are preserved.

Known callers within the codebase:
- None discovered in the current scan. (If present elsewhere, typical callers would be search parsing routines, query-building helpers, or UI/backend code that needs a normalized token before matching.)

Why this logic is a separate function:
- Encapsulates a single normalization behavior so callers do not duplicate the exact strip pattern or the falsy-to-empty-string rule.
- Keeps higher-level search parsing code concise and focused on control flow rather than small normalization details.
- Centralizes future changes to the normalization rule (for example, to add additional character removal or encoding handling).

## Args:
    raw_value (str | None | Any):
        The value to normalize. Expected to be a str (text) in typical usage.
        - If raw_value is a falsy value (None, empty string, 0, empty container, etc.), the function returns an empty string.
        - If raw_value is truthy, the function calls raw_value.strip('" ') and returns that result.
        - Interdependencies: none.

## Returns:
    str or any:
        - If raw_value is falsy: returns the empty string ''.
        - If raw_value is truthy and is a str: returns a str with any leading/trailing double-quote characters (") and space characters removed.
        - If raw_value is truthy but not a str: returns whatever result raw_value.strip('" ') produces. In typical, correct usage this will be a str; however, if the input type implements strip differently, the returned type may differ.

## Raises:
    AttributeError:
        - If raw_value is truthy but does not implement a strip method (for example, an object without strip), Python will raise AttributeError when attempting raw_value.strip('" ').
    TypeError:
        - If raw_value is truthy and implements strip but expects a different argument type (for example, bytes.strip expects a bytes argument), passing the str argument '" ' will raise TypeError.
    Note: these are implicit exceptions raised by calling the strip method; they are not explicitly raised in the function body.

## Constraints:
Preconditions:
    - Prefer passing a native Python str. The function assumes callers provide textual input or None.
    - Avoid passing bytes, unless callers first decode to str, because bytes.strip expects a bytes argument and will raise TypeError.

Postconditions:
    - The function will either return a normalized (str) token or the empty string.
    - If the function returns without raising, no global state or external side effects will have changed.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or external systems.

## Control Flow:
flowchart TD
    Start([Start])
    CheckTruthy{raw_value is truthy?}
    TruthyCall[/Call raw_value.strip('" ')/]
    ReturnValue1[Return stripped result]
    ReturnValue2[Return '' (empty string)]
    Error[Possible AttributeError/TypeError from strip]
    Start --> CheckTruthy
    CheckTruthy -- True --> TruthyCall
    TruthyCall --> |strip succeeds| ReturnValue1
    TruthyCall --> |strip raises| Error
    CheckTruthy -- False --> ReturnValue2

## Examples:
- Input: None
  Output: ''

- Input: '' (empty string)
  Output: ''

- Input: ' "foo" '
  Output: 'foo'  (leading/trailing double quotes and spaces removed)

- Input: '"bar'
  Output: 'bar'  (leading double quote removed)

- Input: '  "a " b"  '
  Output: 'a " b'  (only outermost leading/trailing " and spaces removed; interior quotes and spaces preserved)

- Incorrect usage example to illustrate error handling:
  - If raw_value is a bytes object (b'"x"'), strip('" ') will raise TypeError because bytes.strip expects a bytes argument; callers should decode bytes to str first, or handle the exception.

Usage guidance:
- Callers that accept unvalidated user input should ensure the value is a str (e.g., decode bytes, convert other types, or explicitly handle None) before calling this function to avoid implicit exceptions.

## `flower.utils.search.task_args_contains_search_args` · *function*

## Summary:
Return True if every element in the provided search arguments is contained in the given task arguments; otherwise return False.

## Description:
This function implements a simple predicate used to determine whether a task's argument collection contains all requested search tokens. Typical callers are filtering or matching routines that decide whether a task meets user-provided search criteria (for example, when searching/listing tasks that include a set of flags or options). The logic is extracted into its own function to encapsulate the membership test and the early-falsy guard, making call sites concise and ensuring a single consistent interpretation of "contains all search args".

Known callers within the codebase:
- No explicit callers are included in the provided context. In practice it is used wherever the codebase needs to check whether a task's arguments include a collection of required tokens (e.g., task filtering, UI search, or API query handlers).

Why this is a separate function:
- Centralizes the membership logic and the special-case behavior for falsy task_args (empty/None), so callers do not need to duplicate the guard or reimplement the all(...) pattern.
- Makes unit testing and behavior changes easier (single point of change for the membership semantics).

## Args:
    task_args (Any): A container or sequence representing a task's arguments. Must support Python membership test ("x in task_args") for each element of search_args. Typical types: list/tuple/set of strings, or a single string containing tokens. If task_args is falsy (None, empty sequence, empty string, empty dict, etc.), the function returns False immediately.
    search_args (Iterable): An iterable of items to search for in task_args. Each element will be tested with the membership operator (a in task_args). Typical type: list or tuple of strings. May be empty.

Notes on interdependencies:
- Both arguments are used together: membership checks assume task_args supports membership semantics for items coming from search_args. If search_args contains items incompatible with task_args' membership check, a TypeError may be raised by Python.

## Returns:
    bool: True if:
        - task_args is truthy (not None or empty), and
        - every element in search_args is present in task_args (i.e., for all a in search_args, a in task_args is True).
    False otherwise.

All possible outcomes and edge cases:
- If task_args is falsy (e.g., None, [], (), "", {}), the function returns False immediately (even if search_args is empty).
- If search_args is empty and task_args is truthy, the function returns True (because all() over an empty iterable yields True).
- If search_args contains at least one element not found in task_args, the function returns False.
- If membership testing raises an exception (e.g., because task_args does not support membership with elements from search_args), that exception propagates to the caller.

## Raises:
    Any exception raised by Python's membership testing or iteration, such as:
    - TypeError: If search_args is not iterable, or if elements of search_args cannot be checked for membership against task_args (for instance, unhashable items when task_args is a set, or incompatible types).
    - Other exceptions that may occur during iteration of search_args.

The function itself does not raise custom exceptions.

## Constraints:
Preconditions:
- Preferably call with task_args that is either None or a container/sequence/string supporting membership testing.
- search_args should be an iterable (can be empty).

Postconditions:
- The function returns a boolean and does not mutate inputs.
- No side effects are performed.

## Side Effects:
- None. The function performs pure, read-only checks and does not perform any I/O, global state mutation, or external calls.

## Control Flow:
flowchart TD
    Start-->CheckTaskArgsFalsy
    CheckTaskArgsFalsy{Is task_args falsy?}
    CheckTaskArgsFalsy-->|Yes|ReturnFalse
    CheckTaskArgsFalsy-->|No|IterateSearchArgs
    IterateSearchArgs-->CheckEachMember
    CheckEachMember{Is current a in task_args?}
    CheckEachMember-->|No|ReturnFalse
    CheckEachMember-->|Yes|NextArg
    NextArg-->IterateSearchArgs
    IterateSearchArgs-->|AllChecked|ReturnTrue
    ReturnFalse-->End
    ReturnTrue-->End

## Examples:
Example 1 — typical list-of-strings usage:
    task_args = ['--queue=high', '--retries=3', '--verbose']
    search_args = ['--queue=high', '--verbose']
    result = task_args_contains_search_args(task_args, search_args)  # True

Example 2 — search_args empty:
    task_args = ['--x']
    search_args = []
    result = task_args_contains_search_args(task_args, search_args)  # True

Example 3 — empty task_args:
    task_args = []
    search_args = []
    result = task_args_contains_search_args(task_args, search_args)  # False (special-case: empty task_args => False)

Example 4 — string-based membership:
    task_args = "--debug --fast"
    search_args = ["--debug"]
    result = task_args_contains_search_args(task_args, search_args)  # True (string supports substring membership)

Example 5 — potential TypeError propagation:
    task_args = None  # falsy => returns False immediately, no TypeError
    search_args = object()  # non-iterable
    # If task_args were non-falsy but search_args is not iterable, iteration would raise TypeError.

