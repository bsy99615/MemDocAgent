# `utils.py`

## `parsel.utils.flatten` · *function*

## Summary:
Returns a fully materialized, depth-first flattened list of the atomic (non-listlike) elements found by traversing the input iterable.

## Description:
Known callers within this codebase:
- parsel.utils.iflatten — iflatten is a generator that performs a depth-first traversal and, when it encounters a nested listlike element, delegates to this function to materialize that nested sequence. This mutual relation is the primary and documented caller relationship.

Why this logic is extracted into its own function:
- Responsibility separation: flatten is a small, focused convenience wrapper that materializes the output of the lazy traversal implemented by iflatten. Keeping materialization logic here keeps the generator (iflatten) lean and reusable for streaming/iterative use without forcing allocation.
- API clarity: callers who want a list rather than an iterator need a single-line, explicit function that returns List[Any] instead of dealing with generator-to-list conversion at each call site.
- Boundary: flatten is responsible only for materializing the flattened sequence; the traversal and the definition of what is "listlike" are implemented elsewhere (iflatten and _is_listlike).

## Args:
    x (Iterable[Any]):
        - Any iterable whose elements may be atomic values or nested iterables.
        - No additional validation is performed by flatten; the function simply calls list(iflatten(x)).
        - Interdependencies: behavior depends on the module-level helper _is_listlike used by iflatten to classify elements as listlike vs atomic. For surprising behavior (e.g., whether strings are treated as listlike), consult that helper.

## Returns:
    List[Any]:
        - A Python list containing the flattened, atomic elements yielded by iflatten(x), in depth-first order.
        - Edge cases:
            - If x is empty, returns an empty list.
            - If x contains only atomic elements, returns a list with those elements in original order.
            - If x contains nested listlike elements, their atomic contents are inserted at the point of nesting (depth-first).
        - Memory note: this function materializes the entire flattened sequence in memory. For very large or deeply nested inputs, peak memory usage will grow with the size of the flattened result.

## Raises:
    TypeError:
        - If x is not iterable, calling list(iflatten(x)) will raise TypeError when the iteration is attempted; flatten does not catch this.
    RecursionError:
        - Deeply nested or self-referential structures may cause a RecursionError during the traversal performed by iflatten/flatten.
    Any exception propagated from underlying operations:
        - Exceptions raised by iteration over x, by the listlike classifier _is_listlike, or by any code called during traversal (including any side-effectful iterator) will propagate through flatten unchanged.

## Constraints:
Preconditions:
- The argument x must implement the iterable protocol (i.e., be suitable for use in a for-loop). No explicit type coercion or validation is performed.

Postconditions:
- The returned list contains only elements classified as non-listlike by the traversal logic (i.e., atomic values as defined by _is_listlike).
- The returned list is a new list object (mutating the original input collections is not performed by flatten).

Performance constraints:
- Time complexity is proportional to traversing every element reachable through the nested iterables (O(n) in number of visited items, ignoring cost of _is_listlike).
- Space complexity is O(m) where m is the number of flattened elements (since the full result is stored in a Python list).

## Side Effects:
- No direct I/O is performed.
- No mutation of global state in this function itself.
- Indirect side effects can occur if iteration over x or the _is_listlike helper have side effects (those will occur during traversal and are not suppressed).

## Control Flow:
flowchart TD
    Start --> Call_iflatten
    Call_iflatten --> AdvanceGenerator
    AdvanceGenerator -->|yields atomic el| AppendToList
    AdvanceGenerator -->|yields from nested flatten| AppendNestedResults
    AppendToList --> AdvanceGenerator
    AppendNestedResults --> AdvanceGenerator
    AdvanceGenerator -->|StopIteration| ReturnList
    ReturnList --> End

## Examples:
- Typical use (materialize flattened result):
    - Given nested_iterable = [1, [2, 3], (4, [5, 6])]
    - flatten(nested_iterable) returns [1, 2, 3, 4, 5, 6]

- Streaming alternative:
    - If you need to process items one at a time without materializing the full result, use iflatten directly (for item in iflatten(huge_nested_iterable): process(item))

- Error handling example:
    - If the input may not be iterable, guard or handle TypeError:
        - try: result = flatten(maybe_non_iterable)
          except TypeError: handle_invalid_input()

## `parsel.utils.iflatten` · *function*

## Summary:
Yields a depth-first sequence of the non-listlike elements found by recursively traversing the input iterable, producing items without building the entire flattened list in memory.

## Description:
iflatten is a generator that walks the provided iterable and emits each atomic (non-listlike) element it encounters. For every element in the input:
- If the element is classified as listlike by the helper _is_listlike, the function delegates to flatten on that element (which itself calls list(iflatten(...))) and yields each item from the returned sequence.
- Otherwise it yields the element directly.

Known callers within this codebase:
- parsel.utils.flatten — calls list(iflatten(x)) to produce a fully materialized list. This is the primary, documented caller. No other callers were discovered by the available code inspection.

Why this is a separate function:
- Responsibility separation: iflatten encapsulates the lazy, recursive traversal logic (a generator) while flatten provides a convenience wrapper that returns a materialized list. Extracting the generator keeps flatten simple and enables other consumers to iterate lazily without allocating a list up-front.
- Reusability: the generator form is useful for streaming pipelines or large nested iterables where full materialization is undesirable.
- Boundary: this function is only responsible for traversal & delegation to flatten for nested listlike elements; it does not decide what is considered listlike — that is delegated to _is_listlike.

## Args:
    x (Iterable[Any]): An iterable whose elements may be atomic values or nested iterables. The function does not validate types beyond attempting to iterate over x itself.

Notes on parameters:
- There are no additional parameters.
- Behavior depends on _is_listlike(el). The exact classification of "listlike" (e.g., whether strings/bytes are listlike) is determined by that helper; callers should consult its implementation when surprising behavior is observed.

## Returns:
    Iterator[Any]: A generator that yields the flattened, atomic elements found in depth-first order.

Possible return behaviors / edge cases:
- If x is empty, the iterator yields nothing (equivalent to an empty iterator).
- If x contains only atomic elements, the iterator yields those elements in order.
- If x contains nested listlike elements, the nested contents are yielded recursively.
- No guarantee is made about list mutation during iteration; modifying nested structure while iterating may cause unpredictable results or runtime errors coming from the underlying Python iteration semantics.

## Raises:
- The function itself does not raise explicit custom exceptions.
- It may propagate exceptions raised by:
    - Iterating x (e.g., TypeError if x is not iterable).
    - _is_listlike(el) if that helper raises.
    - flatten(el) / subsequent recursion if nested elements cause errors (e.g., recursion depth exceeded on self-referential structures).
- No exceptions are caught internally; all are passed to the caller.

## Constraints:
Preconditions:
- x must be an iterable. If x is not iterable, a TypeError will be raised by the iteration protocol before any yielding occurs.
- The helper _is_listlike must be available in the same module namespace; its behavior influences correctness.

Postconditions:
- After iteration completes, every yielded value is an element for which _is_listlike returned False (i.e., atomic / non-listlike), unless _is_listlike misclassifies types.
- The generator completes (StopIteration) once the traversal finishes or an exception is propagated.

Performance constraints:
- Memory-efficient for streaming: iflatten itself yields items lazily, but because flatten calls list(iflatten(...)) when descending, using flatten on many nested elements will materialize those sublists. Consumers that only use iflatten directly (or list(iflatten(...)) at top-level) will determine peak memory usage.
- Deeply nested or self-referential structures may cause deep recursion and potentially RecursionError.

## Side Effects:
- No I/O is performed.
- Does not mutate global state.
- Side effects can occur indirectly if underlying iterables or _is_listlike have side effects during iteration/classification; these are not introduced by iflatten itself.

## Control Flow:
flowchart TD
    Start --> CheckNextElement
    CheckNextElement -->|no more elements| End
    CheckNextElement -->|el retrieved| IsListlike
    IsListlike -->|True| CallFlatten
    IsListlike -->|False| YieldEl
    CallFlatten -->|flatten returns sequence| YieldFromFlatten
    YieldFromFlatten --> CheckNextElement
    YieldEl --> CheckNextElement
    End

## Examples:
- Typical usage via the provided wrapper:
    - flatten(nested_iterable) will return a fully flattened list by calling list(iflatten(nested_iterable)).
- Using the generator directly for streaming:
    - Converting to a list: list(iflatten(nested_iterable)) produces the same result as flatten(nested_iterable).
    - Iterating lazily: for item in iflatten(huge_nested_iterable): process(item)

Error handling example:
- If the input is not iterable, iteration will raise TypeError immediately when the generator is first advanced; callers should validate inputs or handle TypeError/TypeError-derived exceptions as appropriate.

Implementation notes for reimplementers:
- Implement iflatten as a generator that:
    1. Iterates over x.
    2. For each element el, calls a listlike predicate _is_listlike(el).
    3. If True, delegates to flatten(el) and yields each result (yield from).
    4. Otherwise yields el.
- Ensure no swallowing of exceptions: let iteration and helper exceptions propagate to the caller.
- Keep the generator lazy; avoid precomputing lists except via flatten when descending into a nested listlike element (as flatten is documented to materialize).

## `parsel.utils._is_listlike` · *function*

*No documentation generated.*

## `parsel.utils.extract_regex` · *function*

## Summary:
Extracts substrings from input text using a regular expression and returns a flattened list of the matches, optionally applying HTML entity replacement while preserving the "lt" and "amp" entities.

## Description:
Known callers within the codebase:
- No direct internal callers were found in available memory. In typical usage within a scraping/parsing library, higher-level extraction utilities or selector helpers call this function when a regex pattern is used to produce extracted fields.

Why this logic is extracted into its own function:
- Consolidates common behavior for regex-based extraction into one place: accepts either a pattern string or a compiled Pattern, uses a named-group "extract" (if present) to return a single extracted value via search, falls back to findall for multi-value extraction, flattens nested findall results into a single list, and optionally normalizes HTML entities.
- Avoids duplication of compilation, matching semantics, flattening, and entity normalization across the codebase.

## Args:
    regex (Union[str, Pattern[str]]):
        - A regular expression pattern or compiled Pattern. If a str is passed it is compiled with re.compile(regex, re.UNICODE).
        - If the (compiled) Pattern contains a named capturing group called "extract" (i.e., "extract" in regex.groupindex), the function will use regex.search(text).group("extract") to obtain at most one extracted value.
        - Otherwise, regex.findall(text) is used; that may return a list of strings or a list of tuples when there are multiple capture groups. The resulting structure is flattened before returning.
    text (str):
        - The text to search. Must be a Python str.
    replace_entities (bool, optional):
        - Default: True.
        - If True, each returned item is passed to the module-level entity replacer with keep=["lt", "amp"] so &lt; and &amp; remain as entities.
        - If False, no entity replacement is applied and the flattened results are returned as-is (which may include non-str elements in unusual cases).

Interdependencies:
- Uses the module-level flatten helper to convert nested lists/tuples returned by findall into a single flat list.
- Uses a module-level entity-replacement callable (the function imported from w3lib.html in the file). The function body references w3lib_replace_entities; ensure that name is bound in module scope (see Side Effects / Notes).

## Returns:
    List[str]
    - A newly allocated list containing zero or more extracted substrings.
    - Cases:
        - Named group "extract" present:
            - If regex.search(text) finds a match and group "extract" returns a non-None value -> returns [that_value].
            - If the group did not participate (None) or no match -> returns [].
            - Only the first match is considered because regex.search is used.
        - No named group "extract":
            - Returns the flattened result of regex.findall(text). For patterns with multiple capture groups, captured tuples are flattened in encounter order into the result list.
    - Practical note: under normal usage with string patterns against string input, returned elements will be str. If replace_entities=False, the function returns the raw flattened results which could be non-str only in atypical or erroneous capture situations.

## Raises:
    re.error
        - Raised if a str for regex cannot be compiled by re.compile.
    NameError
        - The implementation calls w3lib_replace_entities when replace_entities=True. The file's import statement provides replace_entities from w3lib.html but does not bind w3lib_replace_entities. If no symbol named w3lib_replace_entities exists in module scope, a NameError will be raised at runtime. To avoid this, bind w3lib_replace_entities = replace_entities or import under that name.
    Any exception raised by the entity-replacer callable
        - If replace_entities=True and an element in the flattened list is not a str (or the replacer otherwise fails), exceptions from that callable (e.g., TypeError) will propagate.
    Any exception raised by flatten
        - flatten may raise TypeError (if input is not iterable) or RecursionError on extreme nested structures; these propagate.

Note:
- The function intentionally catches AttributeError when attempting to call .group("extract") on a None match and treats it as "no matches" (returning an empty list) rather than propagating the AttributeError.

## Constraints:
Preconditions:
- text must be a Python str.
- If regex is provided as a str, it must be a syntactically valid regular expression.
- If replace_entities=True, ensure a compatible callable is bound to w3lib_replace_entities in module scope.

Postconditions:
- Returns a list (possibly empty) of extracted substrings.
- If replace_entities=True and the entity-replacer behaves as expected, returned strings will have HTML entities replaced except for "lt" and "amp".

## Side Effects:
- No I/O (files, network, stdout) is performed.
- No global state is mutated by extract_regex itself.
- Calls an external string-processing callable for entity replacement when replace_entities=True; any side effects or exceptions originate from that callable.

Important module binding note:
- The function body invokes w3lib_replace_entities(..., keep=["lt", "amp"]). The file-level import statement shows from w3lib.html import replace_entities. If the module does not assign w3lib_replace_entities = replace_entities (or otherwise define w3lib_replace_entities), calling extract_regex with replace_entities=True will raise NameError. Fix by adding either:
    - w3lib_replace_entities = replace_entities
  or importing under that name.

## Control Flow:
flowchart TD
    Start --> IsRegexStr{regex is str?}
    IsRegexStr -->|yes| CompileRegex[compile regex with re.UNICODE]
    IsRegexStr -->|no| UsePattern[use passed Pattern]
    CompileRegex --> CheckGroup["extract" in regex.groupindex?]
    UsePattern --> CheckGroup
    CheckGroup -->|yes| TrySearch[try: m = regex.search(text); extracted = m.group("extract")]
    TrySearch -->|m is None (AttributeError)| StringsEmpty[strings = []]
    TrySearch -->|success| ExtractedValue[extracted is not None?]
    ExtractedValue -->|yes| strings = [extracted]
    ExtractedValue -->|no| strings = []
    CheckGroup -->|no| FindAll[strings = regex.findall(text)]
    StringsEmpty --> Flatten[strings = flatten(strings)]
    strings = [extracted] --> Flatten
    FindAll --> Flatten
    Flatten --> IfReplace{replace_entities?}
    IfReplace -->|no| ReturnPlain[return strings]
    IfReplace -->|yes| MapReplace[return [w3lib_replace_entities(s, keep=["lt","amp"]) for s in strings]]
    MapReplace --> End
    ReturnPlain --> End

## Examples:
- Simple findall:
    - pattern = r"\b\w{3}\b"
    - text = "one two three four"
    - extract_regex(pattern, text) -> ["one", "two"]

- Named-group "extract" (single value via search):
    - pattern = re.compile(r"ID:(?P<extract>\d+)")
    - text = "User ID:123; other ID:456"
    - extract_regex(pattern, text) -> ["123"]

- Multiple capture groups (flattening):
    - pattern = re.compile(r"(\d+)-([A-Z]+)")
    - text = "123-ABC and 456-DEF"
    - extract_regex(pattern, text) -> ["123", "ABC", "456", "DEF"]

- HTML entity replacement:
    - pattern = r".+"
    - text = "a &amp; b &lt; c &copy;"
    - extract_regex(pattern, text) -> ["a &amp; b &lt; c ©"]  (requires w3lib_replace_entities behaving like w3lib.html.replace_entities)
    - With replace_entities=False the returned string remains "a &amp; b &lt; c &copy;".

- Invalid regex handling:
    - pattern = "(unclosed"
    - extract_regex(pattern, text) will raise re.error during compilation; callers should catch re.error when patterns are untrusted.

- Name binding preventive action:
    - If the module does not define w3lib_replace_entities, add:
        - from w3lib.html import replace_entities
        - w3lib_replace_entities = replace_entities

## `parsel.utils.shorten` · *function*

## Summary:
Return a string no longer than `width` characters by either returning the original text (if it fits), returning a truncated prefix plus the full `suffix`, or returning a rightmost slice of the `suffix` when `width` is very small.

## Description:
Known callers in this codebase:
- No direct callers were found in the available repository memory. Typical callers are UI/templating or text-processing utilities that need to constrain displayed text length (e.g., previews, labels, or log snippets).

Why this logic is extracted:
- Provides a single, well-tested policy for truncation and suffix handling so callers do not duplicate corner-case logic (especially behavior when `width` is less than or equal to the suffix length). It centralizes decisions about how many characters to preserve from the original text and how to treat very small widths.

Behavior summary:
- If len(text) <= width: returns the original `text` unchanged.
- If len(text) > width and width > len(suffix): returns text[: width - len(suffix)] + suffix. The returned string length equals `width`.
- If len(text) > width and 0 <= width <= len(suffix): returns suffix[len(suffix) - width :], i.e., the rightmost `width` characters of `suffix`. The returned string length equals `width`.
- If width < 0: raises ValueError with the message "width must be equal or greater than 0".

## Args:
    text (str): Input text to shorten. The function signature requires a string; the implementation uses len() and slicing, so other sequence-like objects that implement these operations may behave similarly but are not the intended type.
    width (int): Maximum permitted length of the returned string. Must be an integer value.
        - width < 0: invalid — a ValueError is raised.
        - width == 0: valid — the function returns an empty string ("") when truncation is needed (and also returns "" if text is empty).
        - width > 0: follow the truncation rules above.
    suffix (str): String appended to indicate truncation. Defaults to "..." (length 3). Must be a str; its length determines whether a prefix from `text` is preserved when truncating.

Interdependencies:
- When truncation is required, the number of characters preserved from `text` is computed as width - len(suffix) but only used when that value is positive (i.e., when width > len(suffix)).

## Returns:
    str: A string whose length is <= width when width >= 0.
    Concrete possibilities:
    - Original `text` (len(text) <= width).
    - A concatenation of a prefix of `text` and the full `suffix` (len(text) > width and width > len(suffix)). The returned length equals `width`.
    - A rightmost slice of `suffix` of length `width` (len(text) > width and 0 <= width <= len(suffix)). The returned length equals `width`.
    - For width == 0 the function always returns "" (empty string).

## Raises:
    ValueError: If width < 0. Exact message produced: "width must be equal or greater than 0"
    TypeError (indirect): If arguments do not support the operations used (len(), comparison with int, slicing), Python will raise the corresponding TypeError; this is not explicitly raised in the function.

## Constraints:
Preconditions:
- Prefer passing Python str for `text` and `suffix`, and an integer for `width`.
- width must be >= 0 to avoid raising ValueError.

Postconditions:
- On successful return (width >= 0), the returned value's length is <= width.
- If truncation occurred, returned value length equals `width` and either contains the full `suffix` appended to a prefix of `text` (when width > len(suffix)) or is a suffix fragment of length `width` (when 0 <= width <= len(suffix)).

## Side Effects:
- None. The function performs no I/O and mutates no external state.

## Control Flow:
flowchart TD
    Start[Start] --> CheckFit{len(text) <= width?}
    CheckFit -- Yes --> ReturnText[Return text]
    CheckFit -- No --> CheckSuffixLen{width > len(suffix)?}
    CheckSuffixLen -- Yes --> ReturnPrefix[Return text[:width - len(suffix)] + suffix]
    CheckSuffixLen -- No --> CheckNonNeg{width >= 0?}
    CheckNonNeg -- Yes --> ReturnSuffixSlice[Return suffix[len(suffix) - width :]]
    CheckNonNeg -- No --> RaiseErr[Raise ValueError("width must be equal or greater than 0")]

## Examples:
1) Text fits
    Input: text="Hello", width=10
    Output: "Hello"

2) Truncate and append suffix (default suffix = "...")
    Input: text="The quick brown fox", width=10
    Calculation: len(suffix)=3 -> preserve 10-3=7 chars from text -> text[:7] == "The qui"
    Output: "The qui..."

3) width equals suffix length
    Input: text="LongText", width=3, suffix="..."
    Output: "..."  (full suffix; returned length == width)

4) Very small width returns suffix slice
    Input: text="LongText", width=1, suffix="..."
    Output: "."  (rightmost 1 character of suffix)

5) width zero
    Input: text="Non-empty", width=0
    Output: ""  (empty string)

6) Negative width raises
    Call: shorten("text", -1)
    Result: ValueError("width must be equal or greater than 0")

