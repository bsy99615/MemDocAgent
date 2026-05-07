# `__init__.py`

## `datasette.utils.__init__.documented` · *function*

## Summary:
Registers a function as "documented" by appending it to a module-level collection and returns the original function unchanged.

## Description:
This decorator is intended to mark functions as documented by adding the function object to a module-level collection named functions_marked_as_documented and then returning the original function. Typical usage is as a decorator applied to functions whose presence should be recorded for later introspection, automated documentation generation, or registration.

Known callers in the provided context:
- No explicit call sites or decorated functions were present in the supplied source excerpt. In general, callers are simply functions in this or other modules annotated with @documented.

Why this logic is a separate helper:
- Encapsulates the "mark-and-return" pattern used by decorators so that code that needs to record functions as documented can do so consistently without duplicating the append-and-return behavior at each call site.
- Separates the side effect (registration) from function definition, making it simple to collect documented functions for runtime inspection or offline documentation tools.

## Args:
    fn (callable): The function being decorated. Any callable is accepted; the decorator does not change it.

Notes on fn:
- The decorator does not validate the callable's signature or behavior; it only stores and returns it.
- If fn is not a function (e.g., a class or other callable), it will still be appended and returned.

## Returns:
    callable: The same object passed in as fn (identity return). After successful execution, the same callable instance will be found appended to functions_marked_as_documented.

Possible return-related observations:
- The function returned is identical (is) to the original callable; no wrapper is created.

## Raises:
    NameError: If the module-level name functions_marked_as_documented is not defined when the decorator runs.
    AttributeError: If functions_marked_as_documented exists but does not provide an append method (i.e., is not a mutable sequence or has no append attribute).

These are direct consequences of executing:
    functions_marked_as_documented.append(fn)

## Constraints:
Preconditions:
- The module must define a name functions_marked_as_documented that supports an append(fn) operation (commonly a list).
- The decorator must be applied at import/decoration time (as with any decorator). Ensure functions_marked_as_documented is created before any use of @documented during module import.

Postconditions:
- After the decorator runs successfully, functions_marked_as_documented[-1] (the last element) will be the fn that was just decorated.
- The original function object is returned unchanged to the place where it was defined.

## Side Effects:
- Mutates module-level state by appending to functions_marked_as_documented.
- No I/O operations are performed.
- No network or external service calls.
- No other global state is modified by this function.

## Control Flow:
flowchart TD
    Start --> CheckListExists
    CheckListExists -->|exists and has append| AppendFn
    CheckListExists -->|missing name| RaiseNameError
    CheckListExists -->|no append method| RaiseAttributeError
    AppendFn --> ReturnFn
    ReturnFn --> End

## Examples:
Example 1 — normal usage (recommended pattern):
    # ensure the collection exists before any decoration
    functions_marked_as_documented = []

    @documented
    def my_api_function(arg1, arg2):
        "Example function that will be registered as documented."
        return arg1 + arg2

    # After import, my_api_function is appended to the list:
    assert functions_marked_as_documented[-1] is my_api_function

Example 2 — defensive error handling if list may be missing:
    try:
        @documented
        def maybe_bad():
            pass
    except NameError:
        # Module didn't define functions_marked_as_documented
        # Ensure registration list exists and re-decorate or handle accordingly
        functions_marked_as_documented = []
        @documented
        def maybe_bad():
            pass

Notes:
- In typical deployments the module defines functions_marked_as_documented (e.g., as an empty list) at import time, so the decorator rarely raises.
- Avoid relying on the ordering beyond knowing decorated functions are appended in decoration order; if deterministic ordering is required across modules, ensure import ordering is handled explicitly.

## `datasette.utils.__init__.await_me_maybe` · *function*

## Summary:
Resolve a value that may be a plain value, a callable (sync or async), or a coroutine: call it if callable, await it if it's a coroutine, and return the final resolved value.

## Description:
This asynchronous helper centralizes the small but common pattern of accepting either direct values, callables, or coroutine objects and normalizing them into a concrete result.

Known callers in the provided context:
    - No explicit callers were available in the provided file-level context. Typical usage is in places that accept user-provided configuration, lazy-evaluated defaults, or plugin hooks where the provider may be synchronous or asynchronous.

Why this is extracted:
    - It encapsulates the responsibility boundary of "normalize sync/async inputs to a single resolved value", keeping call sites simple and agnostic to whether a value is produced synchronously, lazily via a callable, or produced by an async coroutine.

## Args:
    value (typing.Any): The input to resolve.
        - If value is callable, it will be invoked with no arguments (value()).
        - If value (after optional invocation) is a coroutine object (asyncio.iscoroutine returns True), it will be awaited.
        - Any other value is returned unchanged.
        - There are no additional parameters; the function treats the input opaquely beyond the callable/coroutine checks.

## Returns:
    typing.Any: The resolved result value.
        - If a plain value is passed: returns that value unchanged.
        - If a callable returns a plain value: returns that value.
        - If a coroutine object is passed: awaits it and returns the coroutine's result.
        - If a callable returns a coroutine object (e.g., calling an async function): awaits that coroutine and returns its result.

## Raises:
    - Any exception raised by calling value() (if value is callable) will propagate unchanged.
    - Any exception raised while awaiting a coroutine will propagate unchanged.
    - There are no explicit catches or translations of exceptions in this function; callers should handle exceptions as needed.

## Constraints:
Preconditions:
    - Must be called from asynchronous code (it is an async function). The caller must await await_me_maybe(...) or run it in an event loop (for example via asyncio.run) from synchronous entry points.
    - If the environment does not have a running event loop and the caller attempts to directly await from a context that doesn't support it, the usual asyncio runtime errors will occur (this function itself does not manage loop creation).

Postconditions:
    - On successful return, the result is the fully-resolved value (i.e., the callable has been invoked if necessary and any coroutine object has been awaited).
    - No additional state is modified by this function itself beyond the side effects of calling or awaiting the provided value.

## Side Effects:
    - This function does not perform I/O by itself.
    - Side effects are entirely those produced by calling the provided callable or awaiting the provided coroutine (for example: network calls, file writes, DB changes, mutation of globals, logging).
    - No global variables or module-level state are modified by await_me_maybe itself.

## Control Flow:
flowchart TD
    Start --> IsCallable{callable(value)?}
    IsCallable -- Yes --> Call["value = value()"]
    IsCallable -- No --> AfterCall["value unchanged"]
    Call --> IsCoroutineAfterCall{asyncio.iscoroutine(value)?}
    AfterCall --> IsCoroutineAfterCall
    IsCoroutineAfterCall -- Yes --> Await["value = await value"]
    IsCoroutineAfterCall -- No --> Return["return value"]
    Await --> Return

## Behavior notes and edge cases:
    - The function uses asyncio.iscoroutine to detect coroutine objects. This will return True for native coroutine objects (e.g., those returned by calling an async def function) but will return False for some awaitables that are not coroutine objects (for example, certain objects implementing __await__ or futures). Such non-coroutine awaitables will NOT be awaited by this function and will be returned as-is.
    - If broader awaitable detection is required (to also await asyncio.Future or other awaitables), consider using inspect.isawaitable instead. The current implementation intentionally checks for coroutine objects only.
    - If a callable requires arguments, await_me_maybe will call it with no arguments; callables that need parameters are incompatible with this helper and should be wrapped in a zero-argument callable (e.g., a lambda or functools.partial).

## Examples:
    - Resolving a plain value:
        result = await await_me_maybe(42)
        # result == 42

    - Resolving a synchronous callable:
        result = await await_me_maybe(lambda: "hello")
        # result == "hello"

    - Resolving a coroutine object:
        coro = some_async_func()      # some_async_func is async def
        result = await await_me_maybe(coro)
        # result == await coro

    - Resolving a callable that returns a coroutine:
        result = await await_me_maybe(lambda: some_async_func())
        # the lambda is called, returns a coroutine, which is awaited; result == awaited value

    - Error propagation:
        # If the callable raises or the awaited coroutine raises, the exception propagates:
        result = await await_me_maybe(lambda: 1/0)  # ZeroDivisionError propagates

## `datasette.utils.__init__.urlsafe_components` · *function*

## Summary:
Split a comma-separated token into components and apply tilde-based percent-decoding to each component, returning a list of decoded strings.

## Description:
- Known callers in this repository: None were identified in the provided project context.
- Typical callers / use-cases: URL/path segment parsing, decoding comma-separated token payloads (for example in query parameters or small compound identifiers), or any place where a comma-separated list of URL-ish components may use "~" as an alternate percent-encoding marker.
- Why this is a separate function: Encapsulates two related responsibilities — canonical splitting on commas and applying the non-standard tilde-to-percent decoding provided by tilde_decode — so callers do not need to remember to split and decode in the same way. This keeps parsing logic consistent across the codebase and centralizes edge-case handling (empty components, plus-to-space behaviour inherited from tilde_decode).

See also: datasette.utils.__init__.tilde_decode for details about how tilde-encoded sequences are decoded and how literal '%' characters are preserved.

## Args:
    token (str):
        - Type: str (or any object that implements a .split(str) method that returns an iterable of components).
        - Expected format: a single string containing zero or more components separated by literal commas (',').
        - Allowed values: any string. An empty string is allowed.
        - Notes: Leading, trailing, or consecutive commas produce empty components (e.g., ',a' -> ['', 'a']; 'a,,b' -> ['a', '', 'b']).
        - Interdependencies: None.

## Returns:
    list[str]: A list containing each component after decoding with tilde_decode.
    - For each substring produced by token.split(","), the function returns tilde_decode(substring).
    - Guarantees:
        - Returned value is a list whose length equals the number of items yielded by token.split(",").
        - Each list element is the decoded string (type str).
        - Empty components (from adjacent commas or leading/trailing commas) appear as decoded empty strings in the returned list.
    - Edge-case examples:
        - Input "" -> [""] (empty input yields a single empty component).
        - Input "," -> ["", ""] (a single comma yields two empty components).
        - Input "a,,b" -> ["a", "", "b"].

## Raises:
    AttributeError:
        - If token does not support the .split method (for example, passing None or an int), .split will raise an AttributeError.
        - If a component returned by .split does not meet tilde_decode expectations (tilde_decode uses .replace internally), tilde_decode may raise an AttributeError for non-string-like components.
    Other exceptions:
        - Any exception raised by tilde_decode (e.g., unexpected exceptions from underlying urllib.parse.unquote_plus) will propagate unchanged. The function does not capture or translate exceptions.

## Constraints:
- Preconditions:
    - Caller should provide a string (or a split-capable object). The function assumes comma is the intended delimiter and does not perform trimming.
    - Do not expect validation of percent-escape correctness; tilde_decode delegates decoding behavior to urllib.parse.unquote_plus.
- Postconditions:
    - The return is a list of strings where each element corresponds to a comma-separated component of the input, after tilde-decoding.
    - No global state is modified.

## Side Effects:
- None: no I/O, no network, no mutation of globals. Only CPU and memory used to split and decode strings.
- Any errors raised originate from calls to .split or tilde_decode (which itself has no side effects beyond local computation).

## Control Flow:
flowchart TD
    Start([Start: receive token])
    Start --> Split[Split token on ',' into components list]
    Split --> ForEach{For each component in components}
    ForEach --> Decode[Call tilde_decode(component)]
    Decode --> Collect[Collect decoded component into result list]
    Collect --> ForEach
    ForEach --> Return[Return result list]
    Return --> End([End])

## Examples:
1) Basic decoding
    Input: "users~2Falice,docs~2Fintro"
    Behavior: split -> ["users~2Falice", "docs~2Fintro"]; tilde_decode on each turns "~2F" into "/"
    Output: ["users/alice", "docs/intro"]

2) Preserving literal '%' and handling pluses (tilde_decode semantics apply)
    Input: "version%3A1~2Fbeta,hello+world"
    Behavior:
        - First component: '%' is preserved by tilde_decode; "~2F" decodes to '/' -> "version%3A1/beta"
        - Second component: '+' becomes space via tilde_decode -> "hello world"
    Output: ["version%3A1/beta", "hello world"]

3) Empty components from adjacent commas
    Input: "a,,b,"
    Behavior: split -> ["a", "", "b", ""]; decode empty components to "".
    Output: ["a", "", "b", ""]

4) Non-string input (error handling)
    Input: None
    Behavior: token.split(",") raises AttributeError
    Result: AttributeError propagated to caller

Notes:
- If callers need trimming of whitespace around components, or want to ignore empty components, perform those steps before or after calling this function — this function intentionally only splits on commas and decodes each component.

## `datasette.utils.__init__.path_from_row_pks` · *function*

## Summary:
Generate a stable, comma-separated identifier for a database row using either the rowid or the table primary key(s), optionally applying tilde-encoding to each component.

## Description:
- What it does: Builds a string identifier for a single row by selecting either the special "rowid" field (when use_rowid is True) or the values from the provided primary key names (pks). Each chosen value is converted to text and, if quote is True, passed through the module's tilde_encode function to produce an ASCII-safe fragment. The fragments are joined with commas in the order they are produced and returned as a single string.
- Known callers: No direct callers were found in the supplied source excerpt. In the Datasette codebase this function is typically used when constructing URL path segments, permalinks, or other row-specific identifiers that must be uniquely derived from a row's primary key(s) or rowid.
- Why this is a separate function: It centralizes the logic for producing consistent, reversible row identifiers from either rowid or multiple primary key values and for applying the chosen quoting/escaping policy (tilde encoding). Extracting this logic avoids duplication wherever row-specific path strings must be produced and enforces consistent ordering, encoding, and error behavior.

## Args:
    row (mapping): Mapping-like object representing a row. When use_rowid is True, the function reads row["rowid"]. Otherwise, for each name in pks it reads row[pk]. Each row[pk] may be either:
        - a dict containing a "value" key (then row[pk]["value"] is used), or
        - any value (used directly).
      Typical type: dict[str, Any] where values are primitives or dicts with "value".
    pks (sequence of str): Ordered sequence of primary key column names. The order determines the order of fragments in the returned identifier. Ignored when use_rowid is True.
    use_rowid (bool): If True, produce the identifier from row["rowid"] only (pks ignored). If False, use values for each key named in pks.
    quote (bool, default True): If True, each fragment is passed through tilde_encode(str(fragment)) before joining; if False, each fragment is converted to str(fragment) and used as-is.

Interdependencies and important notes:
- If use_rowid is True, pks is ignored entirely.
- The order of elements in the returned identifier follows pks order (when use_rowid is False).
- Each fragment is converted to str before calling tilde_encode, so non-string values are stringified.

## Returns:
    str: A single string formed by joining the chosen fragments with commas (",").
    - When use_rowid is True: return is the tilde-encoded (or plain) string representation of row["rowid"].
    - When use_rowid is False:
        - For pks = ["a","b"], and values v_a, v_b, the return is "frag_a,frag_b" where frag_X is tilde_encode(str(v_X)) when quote is True, else str(v_X).
    - If the produced bits list is empty (e.g., pks is empty and use_rowid is False), returns the empty string "".

## Raises:
- KeyError: If use_rowid is True and "rowid" is not present in row, or if use_rowid is False and any pk in pks is not a key in row. Also raised if a value is expected to be a dict with "value" but that key is missing when the code attempts row[pk]["value"].
- NameError: If quote is True but tilde_encode is not defined in the module at runtime.
- AttributeError / TypeError: If row is not subscriptable (e.g., None) or if row[pk] is an unexpected type that causes indexing errors; these are typical Python errors raised by invalid inputs.
- TypeError: If tilde_encode (when present) returns a non-str for any fragment, the final join will raise TypeError.
- Any exception raised by tilde_encode will propagate unchanged.

## Constraints:
Preconditions:
- Caller must pass a mapping-like object for row such that row["rowid"] or row[pk] access is valid according to use_rowid and pks.
- If a pk value is stored as a dict, that dict must provide a "value" key when that branch is taken.
- If quote is True, the module must expose a callable named tilde_encode that accepts a str and returns a str (tilde_encode(str(fragment)) is invoked).

Postconditions:
- The returned string is deterministic for the same inputs and respects pks ordering (when use_rowid is False).
- No mutation of the row argument or any global state is performed by this function.

## Side Effects:
- None intrinsic: the function performs no I/O and does not mutate global state.
- Indirect side effects only if tilde_encode has side effects (tilde_encode is expected to be pure; if not, its side effects will occur).

## Control Flow:
flowchart TD
    Start --> Check_use_rowid
    Check_use_rowid -->|True| Read_rowid
    Check_use_rowid -->|False| Build_bits_from_pks
    Read_rowid --> Create_bits_list[row["rowid"]]
    Build_bits_from_pks --> ForEach_pk
    ForEach_pk -->|pk exists and value is dict| Use_value_field[row[pk]["value"]]
    ForEach_pk -->|pk exists and value not dict| Use_value_direct[row[pk]]
    ForEach_pk -->|missing pk| Raise_KeyError
    Create_bits_list --> Quote_check
    Use_value_field --> Quote_check
    Use_value_direct --> Quote_check
    Quote_check -->|quote True| Call_tilde_encode
    Quote_check -->|quote False| Convert_to_str
    Call_tilde_encode --> Append_fragment
    Convert_to_str --> Append_fragment
    Append_fragment --> More_bits?
    More_bits? -->|yes| ForEach_pk
    More_bits? -->|no| Join_with_commas
    Join_with_commas --> Return_result
    Return_result --> End

## Examples:
1) Using rowid:
    Input:
      row = {"rowid": 42, "id": 1}
      pks = ["id"]
      use_rowid = True
      quote = True
    Behavior:
      Reads row["rowid"] -> 42, converts to "42" and returns tilde_encode("42") (commonly "42" if digits are safe).

2) Using primary keys (simple values):
    Input:
      row = {"id": "alice", "group": "dev"}
      pks = ["id","group"]
      use_rowid = False
      quote = True
    Behavior:
      fragments = [tilde_encode("alice"), tilde_encode("dev")]
      return "<encoded alice>,<encoded dev>"

3) Using primary keys where stored value is a dict:
    Input:
      row = {"id": {"value": 7}, "name": {"value": "Bob"}}
      pks = ["id","name"]
      use_rowid = False
      quote = False
    Behavior:
      fragments = [str(7), "Bob"]
      return "7,Bob"

4) Edge / error handling:
    - If use_rowid is False and pks contains a key not present in row, a KeyError is raised; callers should catch KeyError or validate input first.
    - If quote is True but tilde_encode is missing or raises, that error propagates (NameError or whatever tilde_encode raises). Wrap calls if you need to handle missing encoder.

Notes:
- The exact encoded strings depend on the implementation and contract of tilde_encode in the same module. For predictable, reversible ASCII-safe output, ensure tilde_encode implements the module's recommended per-byte escape contract (escape unsafe bytes as "~XX" hex).

## `datasette.utils.__init__.compound_keys_after_sql` · *function*

## Summary:
Construct a parenthesized SQLite boolean expression that implements keyset (cursor) pagination for a compound primary key by producing an OR-of-ANDs clause comparing columns to named parameter placeholders (":pN").

## Description:
This helper builds the SQL fragment used to select rows that come strictly after a given compound key tuple when paginating by keys. For N key columns it returns N parenthesized OR-clauses; the k-th clause asserts equality for the first k-1 columns and a greater-than comparison for the k-th column. The same named parameter (for example :p0) is reused across clauses for a given column position. The function calls escape_sqlite for each identifier so callers get consistent identifier quoting.

Known callers / context:
- No direct call sites appear in the provided snippet. Typical callers are code paths that build WHERE clauses for cursor/keyset pagination — e.g., pagination helpers or view logic that convert a cursor into a WHERE fragment and then bind parameter values for the cursor components.
- This function is extracted so SQL-generation code can reuse a single, well-tested routine for the somewhat tricky AND/OR pattern required by compound-key keyset pagination, and so callers can control placeholder numbering via start_index.

## Args:
    pks (list[str]):
        - Ordered list of primary-key column identifiers from most-significant (first) to least-significant (last).
        - Must be a Python list (not a tuple) because the implementation copies via pks[:] and pops from the copy; passing a tuple will cause an AttributeError when .pop() is invoked on the sliced copy.
        - Each element is passed to escape_sqlite; elements must therefore be acceptable input for escape_sqlite (commonly plain column name strings).

    start_index (int, optional):
        - Default: 0
        - Integer offset applied to the generated named parameter placeholders.
        - The first placeholder used for the most-significant column will be ":p{start_index}", then ":p{start_index+1}", etc.
        - start_index should normally be >= 0; using negative values will produce negative-numbered placeholder names (e.g., :p-1) which are unlikely to be valid with DB parameter binding.

## Returns:
    str: A parenthesized SQL boolean expression fragment with these properties:
        - The overall string is wrapped in a single pair of parentheses: "(" + joined_clauses + ")".
        - Each OR branch is parenthesized and consists of zero or more equality comparisons for preceding columns followed by a greater-than comparison for the branch's last column.
        - Clauses are joined with the literal sequence "\n  or\n" (newline, two spaces, "or", newline) for readability.
        - Named placeholders use the format ":pN" where N = start_index + column_position (0-based).
        - Equality comparisons reuse the same placeholder names across clauses for the same column positions.

    Behavior examples (assuming escape_sqlite returns identifiers unchanged):
        - pks = ["pk1", "pk2", "pk3"], start_index = 0
            returns:
            "( (pk1 > :p0)\n  or\n (pk1 = :p0 and pk2 > :p1)\n  or\n (pk1 = :p0 and pk2 = :p1 and pk3 > :p2) )"
          (Spacing shown visually; actual returned string contains a single outer pair of parentheses and the three parenthesized clauses joined with newline-or-newline.)

        - pks = ["id"], start_index = 3
            returns "( (id > :p3) )" (i.e., a single parenthesized clause inside an outer pair)

        - pks = [] (edge case)
            returns "()"
          Note: An empty fragment is usually invalid in a WHERE clause; callers should validate pks before using the result.

    Parameter binding mapping:
        - For pks = ["a","b","c"] and start_index = 0, placeholders are :p0 (for a), :p1 (for b), :p2 (for c).
        - Callers must bind exactly those names (e.g., {'p0': v_a, 'p1': v_b, 'p2': v_c}) when executing the full query with Python's sqlite3 named parameters.

## Raises:
    - AttributeError: If pks is not a list (for example a tuple), the implementation will call .pop() on the sliced copy and raise AttributeError.
    - NameError: If escape_sqlite is not defined in the module namespace at call time.
    - TypeError / AttributeError: If elements of pks are not strings or otherwise incompatible with escape_sqlite (escape_sqlite may call .lower() and run regex match).
    - The function itself does not explicitly raise custom exceptions; the above are runtime errors implied by its operations.

## Constraints:
Preconditions:
    - pks must be a non-null list of strings (list[str]) in column sort order.
    - escape_sqlite must be available in the same module namespace and accept the pks elements.
    - start_index should be an integer; use non-negative values for standard DB drivers.

Postconditions:
    - The returned value is a string representing a SQL boolean expression fragment. If callers bind parameters matching the generated names, the expression evaluates to true for rows lexicographically greater than the provided compound key.
    - The original pks list is not modified (the function operates on a shallow copy).

## Side Effects:
    - None. The function only returns a string and does not perform I/O or mutate external/global state.
    - It depends on escape_sqlite for identifier formatting; ensure escape_sqlite's behavior meets your quoting/escaping expectations.

## Control Flow:
flowchart TD
    Start --> CopyPks[pks_left = pks[:]]
    CopyPks --> EmptyCheck{pks_left empty?}
    EmptyCheck -- True --> ReturnEmpty["return '()'"]
    EmptyCheck -- False --> LoopStart
    LoopStart --> LastAndRest[last = pks_left[-1]; rest = pks_left[:-1]]
    LastAndRest --> BuildAndClauses[build equality clauses for rest using :p(i+start_index); append last > :p(len(rest)+start_index)]
    BuildAndClauses --> AddOrClause[or_clauses.append("(" + " and ".join(and_clauses) + ")")]
    AddOrClause --> PopLast[pks_left.pop()]
    PopLast --> LoopCheck{pks_left non-empty?}
    LoopCheck -- True --> LoopStart
    LoopCheck -- False --> ReverseAndJoin[or_clauses.reverse(); join with "\n  or\n"; wrap with "(" ")"]
    ReverseAndJoin --> ReturnResult[return result]
    ReturnResult --> End

## Examples (usage and binding):
Example — three-column compound key:
    Inputs:
        pks = ["first_name", "last_name", "id"]
        start_index = 0
    Result (assuming escape_sqlite is identity):
        "( (first_name > :p0)\n  or\n (first_name = :p0 and last_name > :p1)\n  or\n (first_name = :p0 and last_name = :p1 and id > :p2) )"
    Example binding with Python's sqlite3 named parameters:
        Provide a mapping {'p0': value_first_name, 'p1': value_last_name, 'p2': value_id} to the execute call for the full query that includes this fragment.

Example — validation note:
    - Avoid calling this function with pks == [].
    - Ensure you pass a list of identifiers; do not pass a tuple (which will raise AttributeError due to .pop()).

## `datasette.utils.__init__.CustomJSONEncoder` · *class*

## Summary:
A json.JSONEncoder subclass that makes sqlite3 Rows/Cursors and bytes objects JSON-serializable by converting them to standard JSON-friendly types.

## Description:
CustomJSONEncoder exists to be passed as the encoder class to json.dumps (or similar APIs that accept a JSON encoder) when serializing objects produced by sqlite3 and when bytes objects may be present. It implements a custom default(obj) handler that:

- Converts sqlite3.Row instances to tuples (order-preserving, indexable sequence).
- Converts sqlite3.Cursor instances to lists (iterating the cursor yields rows).
- Converts bytes objects either to a UTF-8 decoded string (when the bytes are valid UTF-8) or to a small dictionary containing a base64 representation when they are not valid UTF-8.

Typical call sites:
- json.dumps(rows_or_row, cls=CustomJSONEncoder)
- Any HTTP JSON response generation that needs to serialize database rows, cursors, or arbitrary bytes.

Motivation and responsibility boundary:
- The class isolates serialization rules for a few non-JSON-native objects encountered frequently in this codebase (sqlite3 Row/Cursor and bytes). It does not attempt to handle arbitrary types beyond delegating to the standard json.JSONEncoder.default behavior, which will raise TypeError for unknown types.
- It also encodes non-UTF-8 bytes as a small JSON object with a "$base64" flag, leaving decoding responsibilities to the consumer.

## State:
- No instance attributes are added by this subclass. It relies entirely on inherited behavior from json.JSONEncoder.
- __init__ parameters: none required or added. Use the default JSONEncoder constructor signature if needed (e.g., json.dumps(..., cls=CustomJSONEncoder, indent=2) — optional keyword args are handled by json library when instantiating).

Class invariants:
- Instances do not carry custom mutable state between calls.
- Calling default(obj) is side-effect free except when the object is a sqlite3.Cursor: converting a cursor to a list will iterate it and therefore consume it (the cursor becomes exhausted).

## Lifecycle:
Creation:
- Instantiate with no special arguments: encoder = CustomJSONEncoder() is valid, but typically you don't instantiate directly — pass the class to json.dumps via cls=CustomJSONEncoder.

Usage:
- Primary method: default(self, obj) — invoked by the JSON encoding machinery for objects the encoder does not natively know how to serialize.
- Typical usage pattern:
    1. Call json.dumps(data, cls=CustomJSONEncoder) or json.dump(file, data, cls=CustomJSONEncoder).
    2. The JSON library creates an instance and calls default(obj) whenever it encounters an unsupported object type.
- Sequencing: There is no required ordering of method calls; the encoder may be reused by the json module across encoding of nested objects as needed.

Destruction:
- No special cleanup or close methods are required.

## Method Map:
flowchart LR
    A[json.dumps / json.dump] --> B[JSONEncoder instantiation (internal)]
    B --> C[encoder.default(obj) called for non-primitive objects]
    C -->|sqlite3.Row| D[return tuple(obj)]
    C -->|sqlite3.Cursor| E[return list(obj)  (consumes cursor)]
    C -->|bytes (utf8)| F[return obj.decode("utf8") (str)]
    C -->|bytes (invalid utf8)| G[return {"$base64": True, "encoded": base64_string}]
    C -->|other| H[delegate to json.JSONEncoder.default -> TypeError if unsupported]

## Raises:
- __init__: no documented exceptions raised by this subclass; standard JSONEncoder __init__ behavior applies.
- default(self, obj):
    - If obj is not handled by the custom cases (Row, Cursor, bytes), the method calls json.JSONEncoder.default(self, obj) which, by design, raises TypeError("... is not JSON serializable") for unsupported types. This is the expected mechanism to signal un-serializable objects.
    - Note: bytes that contain invalid UTF-8 will not raise here — they are converted to a base64-carrying dict instead.
    - Converting a sqlite3.Cursor to a list may raise database-related exceptions if iteration triggers them (e.g., if the cursor is tied to a connection that is closed); such exceptions propagate from the underlying sqlite3 implementation.

## Edge cases and important notes:
- sqlite3.Cursor -> list(cursor) consumes the cursor. After encoding, the cursor will be exhausted and cannot be re-used to iterate results again unless re-executed.
- For bytes:
    - If bytes.decode("utf8") succeeds, the encoder returns a (Python) str and json will produce a JSON string.
    - If bytes.decode("utf8") raises UnicodeDecodeError, the encoder returns a dict:
        {"$base64": True, "encoded": "<base64-encoded-bytes-as-latin1-decoded-string>"}
      The "encoded" value is produced by base64.b64encode(obj).decode("latin1"), which ensures the base64 bytes are converted to a JSON-safe str without altering the 0–255 byte values (latin1 maps byte-by-byte to Unicode codepoints 0–255).
- The presence of the "$base64": True flag lets consumers detect and decode these values back into raw bytes.

## Example:
- Serialize a sqlite3.Row:
    row = <sqlite3.Row instance>
    json_str = json.dumps(row, cls=CustomJSONEncoder)  # produces a JSON array (tuple -> list in JSON)

- Serialize a cursor (note cursor will be consumed):
    cur = <sqlite3.Cursor after executing a query>
    json_str = json.dumps(list(cur), cls=CustomJSONEncoder)  # or json.dumps(cur, cls=CustomJSONEncoder)

- Serialize bytes:
    good_bytes = b"hello"
    json.dumps(good_bytes, cls=CustomJSONEncoder)  # -> JSON string "hello"
    raw_bytes = b"\xff\x00"
    json.dumps(raw_bytes, cls=CustomJSONEncoder)   # -> {"$base64": True, "encoded": " /A=="} (base64 value as string)

## Implementation notes for reimplementation:
- Subclass json.JSONEncoder and override default(self, obj).
- Import sqlite3 and base64 from the same module-scope imports as used here.
- Use isinstance(obj, sqlite3.Row) and isinstance(obj, sqlite3.Cursor) to detect sqlite types.
- For bytes, attempt obj.decode("utf8") inside a try/except UnicodeDecodeError; on exception return {"$base64": True, "encoded": base64.b64encode(obj).decode("latin1")}.
- For all other objects, call and return json.JSONEncoder.default(self, obj).

### `datasette.utils.__init__.CustomJSONEncoder.default` · *method*

## Summary:
Return JSON-serializable representations for several non-JSON-native objects (sqlite3.Row, sqlite3.Cursor, and bytes), delegating to the standard JSONEncoder for anything else.

## Description:
This method overrides JSONEncoder.default to provide application-specific conversions when the JSON encoder encounters objects it does not know how to serialize. It is invoked by the Python json machinery during encoding (for example, via json.dumps(..., cls=CustomJSONEncoder) or when a CustomJSONEncoder instance encodes nested values).

Known callers and contexts:
- The json module's encoding pipeline: json.dumps, json.dump, JSONEncoder().encode, and JSONEncoder().iterencode when CustomJSONEncoder is supplied as the encoder class. The json library calls this method when it encounters a value that it cannot convert into a JSON scalar, list, or mapping by its normal rules.
- Rare direct calls: callers may explicitly call CustomJSONEncoder().default(obj), but typical usage is indirect via the json API.

Why this is a separate method:
- Centralizes conversions for specific types used throughout the application so JSON output is consistent and maintainable. Placing this logic in the JSONEncoder.default override avoids spreading type-specific serialization logic across multiple call sites.

## Args:
    obj (Any): The value the JSON encoder is attempting to serialize.

## Returns:
    - tuple: If obj is an instance of sqlite3.Row — returns a tuple containing the row's column values in order. (JSON will ultimately represent tuples as arrays.)
    - list: If obj is an instance of sqlite3.Cursor — returns list(obj), i.e., the cursor consumed into a Python list. The list's elements are the items yielded by the cursor (often rows).
    - str: If obj is bytes that successfully decode as UTF-8 — returns the decoded Unicode string.
    - dict: If obj is bytes that fail to decode as UTF-8 — returns a marker mapping:
        {"$base64": True, "encoded": "<base64-string>"}
      where "<base64-string>" is the base64 encoding of the original bytes, converted to a Python str by decoding the base64 bytes with latin1.
    - Otherwise: delegates to json.JSONEncoder.default(self, obj). The base implementation typically raises TypeError with a message like "Object of type X is not JSON serializable".

Edge cases and additional notes:
- Empty bytes (b'') decode to the empty string and return ''.
- Bytes containing valid UTF-8 sequences are returned as the decoded Unicode text. If decoding raises UnicodeDecodeError, the bytes are base64-encoded instead.
- The returned dict for non-UTF-8 bytes uses an explicit "$base64" marker so downstream consumers can detect and decode the original bytes.
- For sqlite3.Cursor, the returned list may be large and will materialize the entire result set in memory.

## Raises:
    TypeError: If the object is not one of the handled types and the superclass json.JSONEncoder.default raises TypeError (standard behavior when an object is not JSON serializable).

## State Changes:
    Attributes READ:
        - None (the method does not read any attributes from self).
    Attributes WRITTEN:
        - None (the method does not modify self).

## Side Effects:
    - Consuming a sqlite3.Cursor by calling list(cursor) will iterate the cursor, which:
        * May perform database I/O to fetch rows.
        * Will exhaust the cursor/iterator (i.e., advance its internal state), so subsequent attempts to iterate the same cursor may yield no results.
        * May allocate memory proportional to the number of rows (potentially large).
    - No files, network services, or external processes are directly invoked by this method.
    - No attributes on self are mutated; however, external objects passed as obj (notably sqlite3.Cursor) may be mutated/exhausted by the conversion.

## Constraints:
    Preconditions:
        - None required beyond typical JSONEncoder usage. Caller should supply values via the json API with CustomJSONEncoder as the encoder class or call the encoder through the standard encoding pipeline.
    Postconditions:
        - For handled types, the method returns a plain Python object that the JSON encoder can represent (str, tuple/list, dict). If delegation to the superclass occurs and that superclass cannot serialize the object, a TypeError is raised.

## Implementation rationale:
    - sqlite3.Row -> tuple: converts row objects into a simple, predictable sequence of values that the JSON encoder will represent as an array. This removes sqlite-specific types from JSON output.
    - sqlite3.Cursor -> list: materializes query results into a stable snapshot suitable for JSON output. The trade-offs are additional memory usage and potential DB I/O.
    - bytes handling: prefer UTF-8 decoding to produce a human-readable string when possible; otherwise produce an explicit base64-encoded payload with a clear marker so clients can restore the original binary safely.

## `datasette.utils.__init__.sqlite_timelimit` · *function*

## Summary:
Temporarily installs a SQLite progress handler that cancels running statements when a time budget (in milliseconds) is exceeded; the handler is removed when the generator-based context ends.

## Description:
Sets a progress handler on the provided SQLite connection which is invoked periodically while SQLite executes statements. The handler checks a deadline (current high-resolution time + ms) and signals SQLite to abort the running statement by returning 1 when the deadline has been reached.

Known callers within the codebase:
- Callers were not provided in the supplied context. Typical use is around code that executes SQL on a sqlite3 connection and must enforce a per-query time limit (for example, request handlers, query-runner utilities, or interactive query endpoints that run user-supplied SQL).

Why this is a separate function:
- Encapsulates the lifecycle (installation and guaranteed cleanup) of the progress handler. Centralizing this ensures the handler frequency decision (n) and final cleanup (removing the handler in a finally block) are applied consistently without duplicating boilerplate in every caller.

## Args:
    conn: sqlite3.Connection-like
        A SQLite connection object that provides set_progress_handler(callable, n). The callable must accept no arguments; set_progress_handler will call it periodically. If conn lacks set_progress_handler an AttributeError will be raised when this function calls it.
    ms: int or float
        Timeout in milliseconds. Non-integer numeric values are supported. If ms is 0 or negative the computed deadline will be now or in the past and the handler will indicate cancellation on its next invocation.

Interdependencies:
    - The handler invocation interval (n) is chosen based on ms:
        * If ms <= 20: n = 1 (check every virtual machine instruction).
        * Otherwise: n = 1000 (check every 1000 virtual machine instructions).
      This trades off between responsiveness and handler overhead.

## Returns:
    A generator that yields exactly once. Intended usage is as a context manager: the caller should wrap it with contextlib.contextmanager or otherwise use a compatible wrapper so it can be used as "with ...:".

Behavior while active:
    - While the handler is installed, any SQL statement executing on conn will trigger periodic calls to the handler.
    - If the handler returns 1 (deadline reached), SQLite will abort the currently executing statement and propagate an error through the sqlite wrapper; the exact exception type depends on the SQLite/python wrapper in use.
    - If the handler returns None, execution continues normally.

## Raises:
    - The function itself does not raise explicit exceptions.
    - AttributeError if conn does not implement set_progress_handler.
    - Any exceptions raised by conn.set_progress_handler will propagate.
    - If a long-running query is aborted by the handler, the exception raised to the executing code is produced by the sqlite wrapper (not raised directly by this function).

## Constraints:
Preconditions:
    - conn must be a valid, open SQLite connection exposing set_progress_handler.
    - ms should be a numeric value; passing non-numeric values will cause a TypeError when arithmetic is attempted.

Postconditions:
    - On exit from the yielded context (normal exit, exception, or query-abort), conn.set_progress_handler(None, n) is called to remove the handler.
    - No matter how the block exits, the handler is cleared to avoid affecting subsequent operations on the connection.

## Side Effects:
    - Installs and later removes a progress handler on the sqlite connection; this alters how SQLite executes statements on that connection while the handler is present.
    - The handler may cause in-progress queries to be aborted; those aborts manifest as exceptions from the sqlite wrapper to the code executing the query.
    - No external I/O (files, network, stdout) and no global state mutations are performed by this function.

## Control Flow:
flowchart TD
    Start --> ComputeDeadline[Compute deadline = time.perf_counter() + (ms / 1000)]
    ComputeDeadline --> ChooseN{ms <= 20?}
    ChooseN -- yes --> SetN1[n = 1]
    ChooseN -- no --> SetN1000[n = 1000]
    SetN1 --> DefineHandler[Define handler(): if time.perf_counter() >= deadline -> return 1]
    SetN1000 --> DefineHandler
    DefineHandler --> Install[conn.set_progress_handler(handler, n)]
    Install --> Yield[Yield control to caller (execute block)]
    Yield --> FinallyBlock[finally: conn.set_progress_handler(None, n)]
    FinallyBlock --> End[Exit]

## Examples:
Example: using as a context manager after converting the generator with contextlib.contextmanager.

    import contextlib
    from sqlite3 import Connection

    # conn: a sqlite3.Connection object
    timed_ctx = contextlib.contextmanager(sqlite_timelimit)

    try:
        with timed_ctx(conn, 500):   # 500 ms time budget
            # run queries on conn here
            conn.execute("SELECT ...")  # may be aborted if it exceeds 500ms
    except Exception as e:
        # Handle the sqlite wrapper's exception resulting from cancellation
        handle_sqlite_error(e)

Notes for implementers:
    - Use time.perf_counter() for monotonic high-resolution timing as in the original.
    - Ensure the progress handler cleanup happens in a finally clause so the handler is removed even if the block raises.
    - Choose the handler frequency (n) deliberately: n=1 gives the earliest detection but highest overhead; n=1000 reduces overhead but checks less often.

## `datasette.utils.__init__.InvalidSql` · *class*

## Summary:
A minimal, application-specific Exception subclass used to represent an "invalid SQL" error condition.

## Description:
InvalidSql is a direct subclass of Python's built-in Exception that provides a distinct exception type which callers can raise and catch to indicate that a SQL statement or query is invalid for the current context. The class itself contains no validation logic or additional behavior — it exists only as a typed marker so code can handle SQL-related errors separately from other exceptions.

Intended usage:
- Raise when SQL validation, parsing, or preparation detects an unrecoverable problem specific to SQL input.
- Catch in higher-level code to handle SQL errors distinctly (for logging, converting to an error response, etc.).

This documentation does not assert any specific callers or factories; it only documents the type-level behavior observable in the source.

## State:
This class defines no custom attributes and inherits all state and behavior from Exception / BaseException.

Inherited and commonly used attributes:
- args (tuple): Positional arguments provided at construction (commonly a single message string).
- __cause__, __context__, __traceback__: Standard exception metadata managed by the interpreter.

Constructor signature (inherited):
- __init__(*args: object) -> None
  - args: optional positional arguments passed to Exception. No defaults beyond the empty tuple.

Class invariants:
- No additional invariants are enforced by InvalidSql beyond those of Exception.
- str(instance) and repr(instance) follow Exception's behavior derived from args.

## Lifecycle:
Creation:
- Instantiate with zero or more positional arguments like any Exception:
    InvalidSql() or InvalidSql("message describing the error")
- No required parameters.

Usage:
- Typical sequence:
    1) Construct (optionally with a message).
    2) raise InvalidSql(...) where appropriate.
    3) Allow propagation or catch InvalidSql in calling code to handle the condition.

Destruction / cleanup:
- No cleanup or resource management responsibilities. Instances are handled by normal Python exception lifecycle and garbage collection.

## Method Map:
Mermaid flowchart of the typical interaction flow (no custom methods beyond Exception):

graph LR
    A[Instantiate InvalidSql] --> B[raise InvalidSql]
    B --> C[Exception propagates through call stack]
    C --> D[Catch InvalidSql in caller/handler]
    D --> E[Handle (log/convert/return error)]

(There are no instance methods declared on InvalidSql; all behavior is inherited from Exception/BaseException.)

## Raises:
- InvalidSql.__init__ contains no custom code and does not raise exceptions itself under normal construction.
- Raising an InvalidSql instance propagates the exception in the usual way; any side-effect exceptions would originate from code that constructs the arguments (e.g., if a caller supplies an object whose __str__ raises), but that behavior is not specific to this class.

## Example:
- Create, raise, and handle an InvalidSql:

1) Raising:
    raise InvalidSql("syntax error near 'FROM'")

2) Catching:
    try:
        validate_sql(some_sql)  # function that may raise InvalidSql
    except InvalidSql as e:
        # e.args[0] typically contains the message if one was provided
        handle_sql_error(str(e))

## `datasette.utils.__init__.validate_sql_select` · *function*

## Summary:
Validate that a provided SQL string is an allowed SELECT statement and does not contain any forbidden constructs; raises InvalidSql on rejection, otherwise returns None.

## Description:
This function enforces a project-level policy that only certain forms of SELECT statements are accepted. It:
- Strips full-line SQL comments that begin with -- (lines whose leading whitespace-stripped text starts with "--"), trims surrounding whitespace, and lowercases the text.
- Tests the normalized SQL against a set of allowed regular-expression patterns (module-level allowed_sql_res). If none match, it raises InvalidSql("Statement must be a SELECT").
- Then scans the normalized SQL for any disallowed patterns defined in the module-level iterable disallawed_sql_res (each entry is a (compiled-regex, message) pair). If any such pattern is found, it raises InvalidSql with the associated message.

Known callers discovered in the provided context:
- None could be located in the supplied source excerpt. Typical use cases are: validating user-supplied SQL before executing it in APIs, web handlers, or CLI commands that accept ad-hoc SELECT queries.

Why this is factored out:
- Centralizes SQL validation rules and error messages in one place so different parts of the application can consistently enforce the same allowed SELECT syntax and forbidden constructs without duplicating regex logic or messages.

## Args:
    sql (str): The SQL statement to validate.
        - Required; must be a string. Passing non-string values will raise an AttributeError or TypeError when the function attempts to call string methods.
        - May be multi-line. Lines that begin (after leading whitespace is stripped) with "--" are removed before validation.
        - Input is normalized by stripping surrounding whitespace and converting to lower-case before applying pattern checks.

## Returns:
    None
    - On success (i.e., the normalized SQL matches at least one allowed pattern and no disallowed pattern is found), the function returns None and does not modify any external state.
    - No transformed SQL is returned; validation is a side-effect-free check.

## Raises:
    InvalidSql("Statement must be a SELECT")
        - Raised when, after comment removal, trimming, and lowercasing, the SQL does not match any of the regular expressions in module-level allowed_sql_res.
    InvalidSql(msg)
        - Raised when any compiled regex in module-level disallawed_sql_res matches the normalized SQL. The raised InvalidSql message is the msg associated with the matching regex.
    NameError
        - If module-level variables allowed_sql_res or disallawed_sql_res are not defined in the module namespace, a NameError will occur at runtime.
    AttributeError / TypeError
        - If sql is not a string or lacks .split/.strip methods, attribute errors or type errors may be raised when normalizing or iterating lines.

## Constraints:
Preconditions:
    - The caller must supply a SQL argument of type str.
    - The module-level iterables allowed_sql_res and disallawed_sql_res must be defined and populated with:
        * allowed_sql_res: an iterable of compiled regular-expression objects whose .match(sql) is used to determine allowed statements (match from start).
        * disallawed_sql_res: an iterable of (compiled-regex, message) pairs whose .search(sql) is used to find forbidden constructs.
Postconditions:
    - If the function returns normally (None), the SQL string satisfied at least one allowed pattern and did not match any disallowed patterns according to the module-level regex lists.
    - If the function raises InvalidSql, no guarantee is made about the SQL content beyond the reason provided in the exception message.

## Side Effects:
    - None: the function performs no I/O, does not modify global variables, and does not execute SQL. It only inspects and validates the given string.
    - The only observable effect is raising InvalidSql on validation failure.

## Control Flow:
flowchart TD
    Start[Start] --> RemoveComments[Remove lines that start with --]
    RemoveComments --> Normalize[Trim whitespace and lowercase]
    Normalize --> CheckAllowed{any pattern in allowed_sql_res matches (r.match) ?}
    CheckAllowed -- No --> RaiseNotSelect[raise InvalidSql("Statement must be a SELECT")]
    CheckAllowed -- Yes --> ForEachDisallowed[for each (r,msg) in disallawed_sql_res]
    ForEachDisallowed --> DisallowedMatch{r.search(sql) ?}
    DisallowedMatch -- Yes --> RaiseDisallowed[raise InvalidSql(msg)]
    DisallowedMatch -- No --> NextPattern[continue loop]
    NextPattern --> ForEachDisallowed
    ForEachDisallowed --> OKReturn[return None]

## Examples:
- Example 1 — valid SELECT:
    Input: "SELECT id, name FROM users"
    Behavior: After normalization it matches an allowed SELECT pattern in allowed_sql_res and none of the disallowed patterns match; function returns None.

- Example 2 — statement is not a SELECT:
    Input: "  -- top comment line\nDROP TABLE users;"
    Behavior: The comment line is removed, remaining text is "drop table users;"; no allowed SELECT pattern matches, so InvalidSql("Statement must be a SELECT") is raised.

- Example 3 — disallowed construct:
    Input: "SELECT * FROM users; -- inline comment\n; ATTACH DATABASE 'file.sqlite' AS d"
    Behavior: Normalized SQL will include the ATTACH clause; if a disallowed regex detects ATTACH and has message "ATTACH not allowed", the function raises InvalidSql("ATTACH not allowed").

- Example 4 — improper usage:
    Input: None (non-string)
    Behavior: The function will attempt to call .split on the argument and will raise an AttributeError/TypeError. Callers should ensure the argument is a str before invoking this validator.

## `datasette.utils.__init__.append_querystring` · *function*

## Summary:
Append a querystring fragment to a base URL by inserting either '?' or '&' as the separator depending on whether the URL already contains a query portion.

## Description:
This small utility returns a new URL formed by concatenating the provided querystring onto the provided url. It chooses '?' as the separator when the url contains no existing query ('?' not present), and '&' when the url already contains a query ('?' present).

Known callers within the provided context:
- No direct callers were included in the provided file snippet. A project-wide search is recommended to find specific call sites. Typical callers are code paths that build links for HTTP responses, HTML anchors, or API redirect URLs where a query fragment must be appended to an existing URL.

Why this logic is extracted:
- Centralizes the small but error-prone decision of which separator to use so other code does not duplicate the "does URL already contain a query?" check.
- Keeps URL construction code concise and avoids subtle bugs such as producing "??" or forgetting to insert any separator when adding additional parameters.

## Args:
    url (any): The base URL or URL-like object to which the querystring should be appended. The implementation uses Python string formatting, so any object will be coerced via its __format__/__str__ representation. Callers should pass a str for predictable results.
    querystring (any): The raw query fragment to append (e.g., "a=1&b=2"). This is not validated or escaped by the function; it will be coerced to string if not already.

Notes about parameters:
- The function does not require url or querystring to be str but treats them as such by converting to their string representation.
- querystring should typically not include a leading '?' — it is expected to be only the fragment after the separator.

## Returns:
    str: A new string equal to the concatenation: <url><separator><querystring>, where <separator> is '?' if the original url did not contain '?', otherwise '&'.

All possible return behaviors:
- If url contains no '?': returns "url?querystring".
- If url contains at least one '?': returns "url&querystring".
- If querystring is an empty string, the result will be "url?" or "url&" (i.e., the separator will still be appended).
- Non-string inputs are converted to strings in the result.

## Raises:
    None explicitly. The function does not raise exceptions itself. Implicitly:
    - If url or querystring instances have __format__ implementations that raise, that exception will propagate.
    - There is no validation of values, encoding, or structure.

## Constraints:
Preconditions:
- Caller should pass url and querystring that are suitable for direct string concatenation (ideally str). If the caller needs percent-encoding or to merge with existing query parameters safely, do that before calling this function.

Postconditions:
- The returned value is a str containing the original url representation followed immediately by either '?' or '&', then the stringified querystring.
- The function guarantees exactly one additional separator character is inserted between the existing url and the appended querystring.

## Side Effects:
- None. This function performs pure string operations and does not perform I/O, modify global state, or call external services.

## Control Flow:
flowchart TD
    A[Start] --> B{Does url contain "?"}
    B -- Yes --> C[Set separator = "&"]
    B -- No --> D[Set separator = "?"]
    C --> E[Return url + "&" + querystring]
    D --> E[Return url + "?" + querystring]
    E --> F[End]

## Examples:
Example 1 — append parameters to a URL with no existing query:
    url = "https://example.org/resource"
    querystring = "page=2&limit=10"
    result = append_querystring(url, querystring)
    # result == "https://example.org/resource?page=2&limit=10"

Example 2 — append parameters to a URL that already has a query:
    url = "https://example.org/search?q=term"
    querystring = "page=2"
    result = append_querystring(url, querystring)
    # result == "https://example.org/search?q=term&page=2"

Example 3 — empty querystring:
    url = "https://example.org/resource"
    querystring = ""
    result = append_querystring(url, querystring)
    # result == "https://example.org/resource?"

Example 4 — non-string inputs (coerced to str):
    url = "https://example.org/item"
    querystring = {"a": 1}  # not recommended; will be stringified
    result = append_querystring(url, querystring)
    # result == "https://example.org/item?{'a': 1}"

Recommendations:
- If adding or merging individual query parameters, prefer using a URL/query-building utility (e.g., urllib.parse.urlencode and urllib.parse.urlparse/ParseResult) to avoid double-encoding, incorrect separators, or malformed query fragments before calling this function.

## `datasette.utils.__init__.path_with_added_args` · *function*

## Summary:
Constructs a URL path string by taking an existing request.path (or a supplied path) and producing a query string that merges the request's current query parameters with additional arguments, where None values remove keys.

## Description:
This utility builds a new path+query-string by:
- reading existing query parameters from request.query_string,
- removing any keys whose value is None in the provided args,
- appending or replacing parameters using the supplied args (preserving order).

Known callers within the codebase:
- Used anywhere that needs to generate links that modify, add, or remove URL query parameters while preserving the original path and unaffected parameters. (Call sites typically include view handlers and template helpers that render pagination, filtering, or sorting links.)

Why this function is extracted:
- Encapsulates the common, error-prone logic of merging current query parameters with requested modifications (including removals signaled by None). This prevents duplication of parse/merge/encode logic across views and templates and centralizes URL-encoding semantics.

## Args:
    request (object): Required. An object that provides two attributes:
        - path (str): The base request path to use when path argument is not provided (e.g., "/table").
        - query_string (str): The raw query string portion from the request (e.g., "a=1&b=2"), without a leading '?'.
      The function does not require a specific request class, but these two attributes must be present and query_string must be a str acceptable to urllib.parse.parse_qsl.

    args (dict | iterable[tuple[str, Any]]): Required. Additional query arguments to apply.
        - If dict: it is converted to items() and treated as an unordered mapping of key->value pairs.
        - If iterable of (key, value) 2-tuples: treated in the given order.
        - Semantics for values:
            * value is None: that key is removed from the resulting query string (i.e., existing occurrences are dropped).
            * value is not None: that (key, value) pair is appended to the parameters (and will appear in the encoded query string). Multiple pairs with the same key are allowed; this function does not deduplicate keys beyond removing keys whose provided value is None.

    path (str | None): Optional. If provided, this string is used as the base path instead of request.path.

Interdependencies:
    - If args is a dict, ordering is not guaranteed; pass an ordered iterable of tuples if parameter order matters.
    - If args is not a dict and not an iterable of pairs, a TypeError will occur when iterating.

## Returns:
    str: The resulting path concatenated with a properly URL-encoded query string (including a leading '?' when there is at least one parameter). Possible outcomes:
        - If there are parameters after merging: "<path>?<encoded_query>"
        - If no parameters remain: "<path>" (no trailing '?')
    Notes on encoding and ordering:
        - Existing parameters retained from request.query_string preserve their original order (except keys removed due to None in args).
        - New/overriding parameters from args are appended in the order they appear when args is an iterable of pairs, or in dict.items() order if args is a dict.
        - URL encoding behavior is delegated to urllib.parse.urlencode; values are converted to strings by that routine.

## Raises:
    - TypeError: If args is not a dict and not an iterable of (key, value) pairs (the comprehension and set/list constructions will raise during iteration).
    - AttributeError: If the request object does not have .path or .query_string attributes.
    - Any exceptions raised by urllib.parse.parse_qsl or urllib.parse.urlencode may propagate (for example if non-string types cause unexpected behavior in encoding).

## Constraints:
Preconditions:
    - request.path must be a string (or at least convertible to a string) representing the path component.
    - request.query_string must be a string acceptable to urllib.parse.parse_qsl (commonly the raw query string without a leading '?').
    - args must be either a dict or an iterable of 2-tuples (key, value).

Postconditions:
    - The returned string is a concatenation of the chosen path and either an empty string or a leading '?' followed by a URL-encoded query string.
    - Keys present in args with value None will not appear in the returned query string, even if they appeared in request.query_string.
    - All non-None key/value pairs from args will appear in the returned query string (they are appended, not merged to overwrite all existing entries with the same key).

## Side Effects:
    - None. This function does not perform I/O, mutate global state, or interact with external services. It only reads attributes from the passed request-like object and returns a string.

## Control Flow:
flowchart TD
    A[Start] --> B{path provided?}
    B -- yes --> C[use provided path]
    B -- no  --> D[use request.path]
    C --> E{args is dict?}
    D --> E
    E -- yes --> F[args = args.items()]
    E -- no  --> G[leave args as-is]
    F --> H[compute args_to_remove = {k for k,v in args if v is None}]
    G --> H
    H --> I[parse request.query_string into pairs]
    I --> J[filter pairs where key not in args_to_remove]
    J --> K[append (key,value) pairs from args where value is not None]
    K --> L[query_string = urlencode(current_pairs)]
    L --> M{query_string non-empty?}
    M -- yes --> N[prefix with '?']
    M -- no  --> O[no prefix]
    N --> P[return path + query_string]
    O --> P[return path]

## Examples:
1) Remove parameter and add another (typical pagination/filter link generation):
    Given:
        request.path = "/items"
        request.query_string = "q=search&page=2&sort=asc"
        args = {"page": None, "page_size": "50"}
    Result:
        "/items?q=search&sort=asc&page_size=50"

2) Append multiple values and preserve ordering (args as iterable of tuples):
    Given:
        request.path = "/search"
        request.query_string = "q=term"
        args = [("filter", "a"), ("filter", "b")]
    Result:
        "/search?q=term&filter=a&filter=b"

3) Use explicit path override:
    Given:
        request.path = "/orig"
        path = "/override"
        request.query_string = "a=1"
        args = {"b": "2"}
    Result:
        "/override?a=1&b=2"

4) No remaining parameters:
    Given:
        request.path = "/x"
        request.query_string = "a=1"
        args = {"a": None}
    Result:
        "/x"

## `datasette.utils.__init__.path_with_removed_args` · *function*

## Summary:
Return a path string with specified query parameters removed, preserving the order and other parameters; the source of the query string is either the request or an explicit path argument.

## Description:
This function builds a new path + query string by parsing an existing query string, removing selected parameter occurrences, and re-encoding the remaining parameters.

Typical usage context:
- Generating links in request handlers or templates when one or more query parameters must be omitted (for example: clearing a filter, toggling a sort parameter, or removing pagination parameters when constructing a "clear filters" link).
- Used anywhere a request-like object is available that exposes .query_string and .path attributes.

Known callers within the provided codebase:
- No specific callers were returned by the lookup performed during documentation generation. Expect it to be referenced in request-handling or templating code where URL manipulation is needed.

Why this is a separate function:
- Encapsulates parsing, selective removal, and re-encoding of query parameters so multiple call sites can reuse consistent behavior without duplicating URL-manipulation logic.
- Keeps caller code concise and reduces risk of subtle bugs (e.g., incorrect percent-encoding/decoding handling).

## Args:
    request (object)
        - Required. Any object exposing string attributes:
            * request.query_string: source query string to parse (the function does not add or remove a leading '?' — it treats this attribute as the raw query portion).
            * request.path: fallback path to use when path parameter is not supplied.
        - If these attributes are missing, an AttributeError will be raised when accessed.
    args (set[str] | dict[str, str])
        - Required. Determines which query parameter occurrences to remove.
        - If a set: any parameter whose key is a member of the set will be removed (value is ignored).
        - If a dict: a parameter occurrence is removed only if both its key matches a dict key and its decoded value equals the corresponding dict value (key-and-value match).
        - Keys and values used for matching should be provided as decoded strings (matching is performed after URL-decoding by urllib.parse.parse_qsl).
        - Passing any other type (e.g., list, None) is unsupported and will cause the function to raise an exception (see Raises).
    path (str | None)
        - Optional. If None, request.path is used as the base path and request.query_string as the query source.
        - If provided and it contains a '?' character, the path is split at the first '?': the portion before is used as the path and the portion after is used as the query string source (overriding request.query_string).
        - If provided and contains no '?', the provided string is used as the path while the request.query_string remains the query source.

## Returns:
    str: The resulting path possibly followed by a query string.
    - If there are retained parameters, returns "<path>?<encoded-query>" (query portion encoded using urllib.parse.urlencode).
    - If no parameters remain after removals, returns just "<path>" (no trailing '?').
    - The function preserves the order of retained parameters as they appear in the parsed source query string and retains duplicate keys for retained occurrences.

## Raises:
    AttributeError
        - If the request object does not have .query_string or .path attributes (accessed at the start of the function).
    NameError
        - If args is neither a set nor a dict, the internal should_remove predicate will not be defined and the function will raise NameError when attempting to call should_remove.
    Any exception raised by urllib.parse.parse_qsl or urllib.parse.urlencode
        - These are propagated; they are rare for normal string inputs but will surface if the underlying library raises for malformed inputs.

## Constraints:
Preconditions:
    - request.query_string and request.path must be present and acceptable to string operations and to urllib.parse.parse_qsl/urlencode.
    - args must be either a set or a dict (recommended: validate or normalize args before calling).
    - If path is supplied and contains a '?', it must be a correctly formed path/query pair (the portion after '?' will be parsed as a query string).

Postconditions:
    - Returned string contains no occurrences of query parameters that met the removal criteria.
    - Returned string is a concatenation of the chosen path and the re-encoded query string (or the path alone if no query parameters remain).
    - The function does not mutate request or any global state.

## Side Effects:
    - None. Purely functional string parsing and construction; no I/O, no network, no global state mutation.

## Implementation details relevant to behavior (urllib semantics)
    - The function uses urllib.parse.parse_qsl to turn the source query string into a list of (key, value) pairs; parse_qsl performs percent-decoding and converts '+' characters into spaces when decoding values. Matching against args happens after this decoding.
    - The function uses urllib.parse.urlencode on a list of (key, value) pairs to build the resulting query string; urlencode uses quote_plus which encodes spaces as '+' by default.
    - Because of these behaviors:
        * When matching dict-based removals, provide decoded strings (e.g., a value that was percent-encoded in the URL will be matched against its decoded form).
        * The output query string may use '+' for spaces due to urlencode's encoding behavior.

## Control Flow:
flowchart TD
    A[Start] --> B{path arg provided?}
    B -- No --> C[use request.path and request.query_string]
    B -- Yes --> D{path contains '?'?}
    D -- No --> E[use provided path and request.query_string]
    D -- Yes --> F[split path -> path, query_string_from_path]
    F --> G[use provided path and query_string_from_path]
    C --> H[determine type of args]
    E --> H
    G --> H
    H --> I{args is set?}
    I -- Yes --> J[should_remove = key in set]
    I -- No --> K{args is dict?}
    K -- Yes --> L[should_remove = args.get(key) == value]
    K -- No --> M[should_remove undefined -> NameError on call]
    J --> N[parse_qsl(query_string) -> list of (k,v) decoded]
    L --> N
    N --> O[iterate pairs: if not should_remove(k,v) append to retained list]
    O --> P[urlencode(retained list) -> new_query_string]
    P --> Q{new_query_string non-empty?}
    Q -- Yes --> R[return path + "?" + new_query_string]
    Q -- No --> S[return path]

## Examples:
Example 1 — remove parameter by name (use a set)
    request.path = "/search"
    request.query_string = "q=dogs&tag=puppy&page=2"
    args = {"page"}
    -> returns "/search?q=dogs&tag=puppy"

Example 2 — remove only specific key/value occurrences (use a dict)
    request.path = "/items"
    request.query_string = "type=shoe&color=red&color=blue"
    args = {"color": "red"}  # match against decoded values
    -> returns "/items?type=shoe&color=blue"

Example 3 — explicit path with its own query string overrides request.query_string
    request.path = "/ignored"
    request.query_string = "x=1"
    path = "/search?q=apple&lang=en"
    args = {"lang"}
    -> returns "/search?q=apple"

Example 4 — recommended defensive pattern to avoid runtime NameError
    # Normalize caller-side:
    if isinstance(args, (list, tuple)):
        args = set(args)
    elif args is None:
        args = set()
    # Now call function safely
    new_path = path_with_removed_args(request, args)

## `datasette.utils.__init__.path_with_replaced_args` · *function*

## Summary:
Builds a URL (path plus query string) by merging an existing request's query parameters with a set of replacements, additions, or removals and returning the resulting path string.

## Description:
This helper reconstructs a request path with a new query string computed as:
- Start from the provided path (explicit path argument) or request.path when no path is supplied.
- Parse the existing request.query_string into (key, value) pairs.
- Preserve existing query parameters except those whose keys appear in args.
- Append entries from args whose values are not None (these replace or add parameters).
- If an args value is None, that key is removed from the final query string.

Known callers within the codebase:
- No concrete call-sites were provided in the current context. Typical callers are HTTP request handlers, view functions, or template helpers that need to render links while changing, adding, or removing specific query parameters (e.g., updating pagination, toggling filters, or clearing facets).

Why this logic is extracted:
- Encapsulates the consistent behavior for merging, replacing, and removing query parameters in one place.
- Prevents duplication of parse/filter/encode logic in views and templates and ensures consistent handling of parameter removal (value None -> drop).

## Args:
    request (object):
        - Required attributes:
            * path (str): base request path (e.g., "/search").
            * query_string (str): the raw query string to parse (e.g., "q=term&page=2"); this value is passed directly to urllib.parse.parse_qsl.
        - If these attributes are missing, attribute access will raise an AttributeError.
    args (dict[str, Optional[str]] | Iterable[tuple[str, Optional[str]]]):
        - Replacement parameter set. Two accepted forms:
            * dict: converted to args.items() (dict iteration order is used).
            * iterable of (key, value) pairs: used as provided (order preserved).
        - Semantics per (key, value):
            * value is a string (or other object acceptable to urllib's encoding): the key will be added or replace any existing parameters with that key.
            * value is None: the key will be removed (no parameter with that key appears in the final query string).
        - Multiple entries with the same key are allowed when using an iterable of pairs; they will all be appended (after preserved existing, non-replaced params).
    path (str | None, optional):
        - If provided, used as the base path in the returned string; otherwise request.path is used.

## Returns:
    str: The composed path string: base path + (empty string or '?' + percent-encoded query string).
    - If no query parameters remain after merging, returns just the base path (no trailing '?').
    - Ordering:
        * Existing request parameters that are not replaced retain their parsed order.
        * Entries from args (except those with value None) are appended in the iteration order of args.

## Raises:
    - AttributeError: if request lacks the required .path or .query_string attributes.
    - TypeError: may be raised by urllib.parse.parse_qsl or urllib.parse.urlencode if inputs contain types they cannot handle (e.g., malformed iterables). These originate from the standard library calls used and are not explicitly raised by this function.

## Constraints:
    Preconditions:
        - request.path must be a string representing the path component to be used if path is not provided.
        - request.query_string must be a string acceptable to urllib.parse.parse_qsl.
        - args must be a mapping or iterable of (key, value) pairs where keys are strings (or string-like) and values are either string-like or None.
    Postconditions:
        - The returned string begins with the chosen base path and, if any parameters remain, contains a single '?' followed by the percent-encoded query string.
        - No parameter with value None appears in the output.
        - No original parameter with a key present in args remains in the output (they are replaced or removed).

## Side Effects:
    - None. The function performs no I/O, does not modify external state, and makes no network calls. It only uses standard library parsing/encoding functions.

## Control Flow:
flowchart TD
    Start[Start]
    A{path provided?}
    A -- yes --> UsePath[use provided path]
    A -- no --> UseRequestPath[use request.path]
    UsePath --> ArgDictCheck
    UseRequestPath --> ArgDictCheck
    ArgDictCheck{args is dict?}
    ArgDictCheck -- yes --> Convert[args = args.items()]
    ArgDictCheck -- no --> Convert
    Convert --> KeysToReplace[compute keys_to_replace from args]
    KeysToReplace --> ParseQS[parse request.query_string with urllib.parse.parse_qsl]
    ParseQS --> Loop[for each (key,value) in parsed pairs]
    Loop --> InReplace{key in keys_to_replace?}
    InReplace -- yes --> Skip[skip this pair]
    InReplace -- no --> Keep[append pair to current]
    Skip --> Loop
    Keep --> Loop
    Loop --> Extend[extend current with args entries where value is not None]
    Extend --> Encode[urlencode(current)]
    Encode --> HasQS{encoded query_string non-empty?}
    HasQS -- yes --> PrefixAdd[prefix with '?']
    HasQS -- no --> NoPrefix[use empty string]
    PrefixAdd --> Return[return path + query_string]
    NoPrefix --> Return

## Examples:
1) Replace one parameter and preserve others
    - Inputs:
        * request.path = "/search"
        * request.query_string = "q=python&page=2"
        * args = {"page": "3"}
    - Call returns: "/search?q=python&page=3"

2) Remove a parameter by setting its value to None
    - Inputs:
        * request.path = "/items"
        * request.query_string = "category=books&sort=asc"
        * args = [("sort", None)]
    - Call returns: "/items?category=books"

3) Provide an explicit path to override request.path
    - Inputs:
        * request.path = "/old"
        * path = "/new"
        * request.query_string = "a=1"
        * args = [("b", "2")]
    - Call returns: "/new?a=1&b=2"

4) Multiple entries and ordering
    - Inputs:
        * request.query_string = "a=1&b=2"
        * args = [("b", "20"), ("c", "3")]
    - Call returns: "/path?a=1&b=20&c=3"
    - Explanation: existing "a" preserved (its relative order kept), "b" replaced, "c" appended.

Notes:
- Keys and values are URL-encoded via urllib.parse.urlencode. Ensure keys and values are string-like or acceptable to the standard library encoding routines to avoid TypeError.

## `datasette.utils.__init__.escape_css_string` · *function*

## Summary:
Normalize CRLF to LF and replace each single-character match (as determined by the module-level _css_re) with a CSS hexadecimal escape: a backslash followed by the character's Unicode code point as a 6-digit uppercase hexadecimal string.

## Description:
This function performs two deterministic transformations, in order:
1. Replace all Windows-style CRLF ("\r\n") sequences with LF ("\n") using s.replace.
2. Use the module-level regular expression _css_re to find matches and substitute each match with a CSS-style hexadecimal escape produced by taking ord(m.group()), formatting it as an uppercase hexadecimal string, zero-padding to 6 digits, and prefixing it with a single backslash. For example, the character U+000A becomes the six-digit hex "00000A" and is substituted as "\00000A".

Known callers within the provided analysis context:
- No callers were found in the supplied snippets. Search the repository for "escape_css_string(" to find call sites in the full codebase.

Why this is a separate function:
- It centralizes the CSS-escaping policy (6-digit, uppercase, zero-padded hex escapes) and line-ending normalization so all callers get consistent, reversible escapes without duplicating formatting logic.

## Args:
    s (str): The input text. Must be a Python str. If a non-str is passed, attribute access for replace() will fail (see Raises).

## Returns:
    str: A new string with:
      - All occurrences of "\r\n" converted to "\n".
      - Every match of the module-level _css_re replaced by a 7-character sequence: a single backslash "\" followed by six uppercase hexadecimal digits representing ord(m.group()) zero-padded to width 6.
    Examples:
      - Input: "Line\r\nBreak" -> Output: "Line\nBreak"
      - If _css_re matches the control character U+0001 in "A\u0001B":
          Output: "A\000001B"  (that is, A + "\" + "000001" + B)

## Raises:
    AttributeError: If s does not support replace (for example, s is None or an object lacking replace).
    TypeError: If a match returned by _css_re has length != 1; ord() requires a single-character string and will raise TypeError for longer strings.
    NameError: If the module-level variable _css_re is not defined in the module namespace at call time (this is a programming/configuration error).

## Constraints:
Preconditions:
  - s must be a str.
  - The module-level _css_re must be defined and should be a compiled regular expression whose matches are single characters. The function relies on m.group() returning a one-character string.
Postconditions:
  - The function returns a str.
  - Any substring matched by _css_re has been replaced by a backslash plus six uppercase hex digits derived from ord(m.group()).
  - CRLF sequences are normalized to LF.

## Side Effects:
  - None. The function performs pure string transformations and does not perform I/O, mutate global state, or call external services. It does, however, reference the module-level _css_re during execution.

## Control Flow:
flowchart TD
    Start --> Normalize[Call s.replace("\r\n", "\n")]
    Normalize --> ApplyRegex[_css_re.sub(lambda m: ... , normalized_s)]
    ApplyRegex --> MatchLoop{For each match m}
    MatchLoop --> GetMatch[Get m.group() (full match)]
    GetMatch --> CheckLength{Is len(match) == 1?}
    CheckLength -- Yes --> Compute[Compute ord(match) -> format as uppercase hex -> zfill(6)]
    CheckLength -- No --> TypeError[ord() raises TypeError]
    Compute --> Prepend[Prepend backslash "\" to hex string]
    Prepend --> Replace[Replace match with escaped sequence]
    Replace --> End[Return final string]

## Examples:
- Simple normalization:
    Input: "Hello\r\nWorld"
    Output: "Hello\nWorld"

- Escaping a matched control character:
    Given _css_re matches U+0001,
    Input: "A\u0001B"
    Output: "A\000001B"
    (In a Python literal display this may appear as "A\\000001B"; the function returns a single backslash character followed by six hex digits.)

- Error cases:
    - Passing bytes: b"text".replace will exist, but bytes.replace returns bytes; the function expects a str and will likely raise other errors downstream. Always decode bytes to str first.
    - If _css_re can match multiple characters (e.g., via a character class with quantifier), calling this function will raise TypeError from ord(m.group()).

Notes:
- The exact set of characters that are escaped is determined entirely by the module-level _css_re. Inspect its definition in this module to understand which Unicode code points are targeted for escaping.

## `datasette.utils.__init__.escape_sqlite` · *function*

## Summary:
Return either the identifier unchanged or the identifier wrapped in square brackets: if a module-level regex matches the input and the lowercased input is not found in a module-level reserved-word set, return the input unmodified; otherwise return the input wrapped in square brackets.

## Description:
This function implements a simple rule for preparing an identifier for use in SQLite SQL text by choosing between leaving it unquoted or wrapping it in square brackets.

What the function does (directly observable from the code):
- Calls _boring_keyword_re.match(s). If that returns a truthy match object, proceeds to the next check.
- Calls s.lower() and tests membership in reserved_words; if s.lower() is not in reserved_words, returns s unchanged.
- In all other cases returns the string f"[{s}]" (the original s surrounded by '[' and ']').

Notes about module-level dependencies (not defined in this function):
- _boring_keyword_re: a module-level compiled regular expression object referenced by name.
- reserved_words: a module-level collection (e.g., set) referenced by name, used as a membership test for s.lower().

Known callers:
- No callers are visible in the provided snippet. Typically this utility is used by code that dynamically constructs SQL identifiers (table names, column names, aliases) before embedding them into SQL statements.

Why this is a separate function:
- Encapsulates the two-step decision (pattern test + reserved-word test) in one place so SQL-building code can consistently apply the same quoting rule.

## Args:
    s (str): The identifier to evaluate and possibly quote.
        - The implementation calls _boring_keyword_re.match(s) and s.lower(), so s must be a type acceptable to both operations (commonly a str).
        - If s is not a string-like object, runtime errors may occur (see Raises).

## Returns:
    str: Either:
        - The original s (exact same object/value), when both conditions are met:
            * _boring_keyword_re.match(s) returns a truthy value, and
            * s.lower() is not a member of reserved_words.
        - Otherwise, the original s wrapped in square brackets, produced as the formatted string f"[{s}]".
    - The function does not change characters within s; it only decides whether to wrap s in square brackets.

## Raises:
    NameError: If _boring_keyword_re or reserved_words is not defined in the module namespace at call time (the code references these names).
    TypeError or AttributeError: If s is of a type that does not support the operations used:
        - If _boring_keyword_re.match(s) cannot accept the provided type, the underlying regex engine will raise TypeError.
        - If s has no lower() method, calling s.lower() will raise AttributeError.
    (No exceptions are explicitly raised in the function body; the above are possible runtime errors directly implied by the operations performed.)

## Constraints:
Preconditions:
    - The module-level names _boring_keyword_re and reserved_words must be defined before calling.
    - s should be a string (str) or otherwise compatible with the module-level regex and the .lower() call.
Postconditions:
    - The return value is a str that is either the original identifier or the original identifier wrapped in square brackets.
    - The function does not modify any external state.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state.

## Control Flow:
flowchart TD
    Start --> MatchCheck
    MatchCheck{_boring_keyword_re.match(s) ?}
    MatchCheck -- True --> ReservedCheck
    MatchCheck -- False --> BracketReturn
    ReservedCheck{s.lower() not in reserved_words ?}
    ReservedCheck -- True --> ReturnOriginal
    ReservedCheck -- False --> BracketReturn
    ReturnOriginal --> End[Return s]
    BracketReturn --> End[Return "[" + s + "]"]

## Examples:
Example 1 — identifier passes both checks:
    Given _boring_keyword_re.match("username") is truthy and "username".lower() not in reserved_words,
    escape_sqlite("username") -> "username"

Example 2 — reserved word:
    Given "select" is present in reserved_words,
    escape_sqlite("SELECT") -> "[SELECT]"

Example 3 — fails regex match (contains space):
    If _boring_keyword_re.match("user name") is falsy,
    escape_sqlite("user name") -> "[user name]"

Example 4 — non-string input:
    If s is None, calling _boring_keyword_re.match(None) or None.lower() will raise TypeError or AttributeError.
    Callers should validate or coerce inputs before calling if non-strings are possible.

Implementation remark for callers:
    - This function only chooses whether to wrap the identifier in square brackets; it does not escape or sanitize inner characters (for example, a ']' in s is not escaped). If identifiers may contain problematic characters, callers should sanitize or reject them before calling.

## `datasette.utils.__init__.make_dockerfile` · *function*

## Summary:
Produces a Dockerfile text (string) that packages the provided SQLite files and configuration so Datasette can be run inside a container.

## Description:
This function assembles and returns a Dockerfile (multi-line string) that:
- copies the current build context into /app and sets WORKDIR /app,
- optionally installs system packages via apt when requested,
- installs Python packages (including either a branch archive or the published datasette package plus additional install targets),
- runs `datasette inspect` on the provided database files to generate inspect-data.json,
- sets ENV PORT to the numeric port and EXPOSEs that port,
- and sets CMD to run a shell-invoked datasette serve command that uses an environment variable $PORT at runtime.

Typical callers and context:
- Packaging or CLI code that prepares a Dockerfile for building a Datasette image (for example: "docker", "package", or "deploy" subcommands). No explicit callers were provided in the loaded context; callers are expected to call this function to generate a Dockerfile string that they then write to disk and build with docker.

Why this is a separate function:
- Centralizes Dockerfile templating and argument assembly (flags, environment variables, apt packages, branch vs PyPI installation, spatialite handling), keeping packaging/CLI code concise and avoiding duplicated string-building logic.

## Args:
- files (Iterable[str])
    - Paths to database files (typically SQLite files). Each element will be added as a `-i <filename>` flag to the datasette serve command and also included in the `datasette inspect` command line.
    - No explicit emptiness check is performed; an empty iterable produces a Dockerfile with no `-i` flags and a `datasette inspect` command with no file arguments.
- metadata_file (Optional[str])
    - When provided, `--metadata <metadata_file>` is appended to the serve command.
- extra_options (Optional[str])
    - A whitespace-separated string of additional CLI options to append to the serve command. The function splits this string on whitespace (using simple .split()) and appends each token as a separate argument; tokens containing spaces cannot be represented.
- branch (Optional[str])
    - If provided, the pip install list will start with the GitHub archive URL for that branch:
      https://github.com/simonw/datasette/archive/{branch}.zip
    - If not provided, the pip install list is prefixed with the string "datasette".
- template_dir (Any truthy/falsey)
    - If truthy, adds `--template-dir templates/` to the serve command.
- plugins_dir (Any truthy/falsey)
    - If truthy, adds `--plugins-dir plugins/` to the serve command.
- static (Optional[Iterable[Tuple[str, str]]])
    - Iterable of (mount_point, path) pairs. For each pair, the function appends `--static <mount_point>:<mount_point>` to the serve command. Note: only the mount_point is used in the rendered option.
- install (Iterable[str])
    - Additional pip install targets. If branch is supplied the branch archive is prepended; otherwise "datasette" is prepended. The function expects `install` to be iterable; it converts it to a list for formatting.
- spatialite (bool)
    - When True:
      - Adds system packages required for spatialite to the apt-get list: "python3-dev", "gcc", "libsqlite3-mod-spatialite".
      - Sets environment_variables["SQLITE_EXTENSIONS"] = "/usr/lib/x86_64-linux-gnu/mod_spatialite.so".
- version_note (Optional[str])
    - When provided, adds `--version-note <version_note>` to the serve command.
- secret (str)
    - Required secret string. Always injected into the environment_variables mapping as DATASETTE_SECRET (overwriting any existing key).
- environment_variables (Optional[Dict[str, str]], default None)
    - Mapping of additional environment variables to write into the Dockerfile as ENV lines. If None, an internal dict is created. This mapping will be mutated by the function to include DATASETTE_SECRET and possibly SQLITE_EXTENSIONS.
- port (int, default 8001)
    - Numeric port inserted into the Dockerfile's ENV and EXPOSE lines. The serve command in CMD uses the runtime environment variable $PORT (the function appends "--port $PORT" to the command string; note $PORT is not shell-quoted).
- apt_get_extras (Optional[Iterable[str]])
    - Extra system package names to install via apt. The function shallow-copies this iterable into an internal list and may extend it (e.g., with spatialite packages) before rendering.
    - If the final apt_get_extras list is non-empty, the function formats a module-level template APT_GET_DOCKERFILE_EXTRAS with " ".join(apt_get_extras) and includes the result in the Dockerfile.

## Returns:
- str: The rendered Dockerfile text (trimmed with .strip()).
  - Contains:
    - FROM python:3.11.0-slim-bullseye
    - COPY . /app and WORKDIR /app
    - An apt-get RUN block when apt_get_extras is non-empty (produced by formatting APT_GET_DOCKERFILE_EXTRAS with the joined package names)
    - ENV lines for each key in environment_variables (after mutation)
    - RUN pip install -U <install targets> where install_targets is the list built from branch/install logic
    - RUN datasette inspect <files> --inspect-file inspect-data.json where <files> is the whitespace-joined files iterable
    - ENV PORT <port> and EXPOSE <port>
    - CMD <cmd> where <cmd> is a single shell command string produced by:
      - assembling argument list for `datasette serve --host 0.0.0.0` with -i flags and other options,
      - applying shlex.quote to each argument,
      - appending `--port $PORT` unquoted,
      - joining into a single string.

Edge cases in the return value:
- If apt_get_extras is empty or None (and spatialite is False), no apt RUN block will be present.
- If environment_variables is None and only the secret is injected, the ENV block will contain only DATASETTE_SECRET; if spatialite True, SQLITE_EXTENSIONS will also be present.
- If files is empty, the `RUN datasette inspect` line will include no filenames (an empty argument list).

## Raises:
- NameError: if apt_get_extras (after processing spatialite) is non-empty but the module-level constant APT_GET_DOCKERFILE_EXTRAS is not defined. The code references APT_GET_DOCKERFILE_EXTRAS when rendering the apt block; if that name is missing, a NameError will occur at runtime.
- TypeError: if arguments are of incorrect types that cause operations to fail, for example:
    - shlex.quote requires string-like parts; passing non-str elements in files, extra_options tokens, or install may raise a TypeError.
    - If files or install are not iterable, attempts to iterate them will raise TypeError.
- The function performs no explicit validation and thus may surface other Python exceptions if unexpected input types are used.

## Constraints:
Preconditions:
- files and install should be iterables of strings.
- secret should be provided (string-like).
- If apt_get_extras behavior is required, the module must define APT_GET_DOCKERFILE_EXTRAS as a format string that accepts a single placeholder for the whitespace-joined package list.

Postconditions:
- The returned string is a ready-to-write Dockerfile.
- If the caller passed a mutable mapping as environment_variables, that mapping will be mutated to include DATASETTE_SECRET (and possibly SQLITE_EXTENSIONS).
- The original apt_get_extras iterable is not mutated; the function shallow-copies it into an internal list before extension.

## Side Effects:
- No file, network, or subprocess I/O is performed by this function.
- Mutation: environment_variables mapping passed by the caller is modified in-place to add or overwrite:
    - "DATASETTE_SECRET" => secret
    - "SQLITE_EXTENSIONS" => "/usr/lib/x86_64-linux-gnu/mod_spatialite.so" (if spatialite True)
- The function reads the module-level name APT_GET_DOCKERFILE_EXTRAS when formatting apt-get instructions (so the module must define it to use apt-get features).

## Control Flow:
flowchart TD
    A[start] --> B[init cmd = ["datasette","serve","--host","0.0.0.0"]]
    B --> C[environment_variables = provided or {}]
    C --> D[set DATASETTE_SECRET in environment_variables]
    D --> E[apt_get_extras = list(copy of provided apt_get_extras) or []]
    E --> F[for each filename in files: append -i filename to cmd]
    F --> G[append --cors and --inspect-file inspect-data.json]
    G --> H{metadata_file?}
    H -- yes --> H1[append --metadata metadata_file]
    H -- no --> I
    H1 --> I
    I --> J{template_dir?}
    J -- yes --> J1[append --template-dir templates/]
    J -- no --> K
    J1 --> K
    K --> L{plugins_dir?}
    L -- yes --> L1[append --plugins-dir plugins/]
    L -- no --> M
    L1 --> M
    M --> N{version_note?}
    N -- yes --> N1[append --version-note version_note]
    N -- no --> O
    N1 --> O
    O --> P{static?}
    P -- yes --> P1[for each mount_point,_ append --static mount:mount]
    P -- no --> Q
    P1 --> Q
    Q --> R{extra_options?}
    R -- yes --> R1[split extra_options and append each token]
    R -- no --> S
    R1 --> S
    S --> T[quote each cmd part with shlex.quote]
    T --> U[append --port $PORT unquoted]
    U --> V[join cmd parts into single string]
    V --> W{branch?}
    W -- yes --> W1[install = [branch-archive] + list(install)]
    W -- no --> W2[install = ["datasette"] + list(install)]
    W1 --> X
    W2 --> X
    X --> Y{spatialite?}
    Y -- yes --> Y1[apt_get_extras.extend(spatialite pkgs); set SQLITE_EXTENSIONS env var]
    Y -- no --> Z
    Y1 --> Z
    Z --> AA[format Dockerfile template using apt_get_extras, environment_variables, install, files, port, cmd]
    AA --> END[end]

## Examples (narrative):
Example — basic Dockerfile with two SQLite files:
- Inputs:
  - files: ["db1.sqlite", "db2.sqlite"]
  - metadata_file: "metadata.json"
  - extra_options: None
  - branch: None
  - template_dir: False
  - plugins_dir: False
  - static: None
  - install: [] (empty iterable)
  - spatialite: False
  - version_note: None
  - secret: "s3cr3t"
  - environment_variables: None
  - port: 8001
  - apt_get_extras: None
- Outcome:
  - install resolves to ["datasette"]
  - CMD in the Dockerfile will be a single shell command roughly equivalent to:
    datasette serve --host 0.0.0.0 -i db1.sqlite -i db2.sqlite --cors --inspect-file inspect-data.json --metadata metadata.json --port $PORT
    (each token in the real CMD will be shell-quoted; $PORT is appended unquoted)
  - RUN pip install -U datasette
  - RUN datasette inspect db1.sqlite db2.sqlite --inspect-file inspect-data.json
  - ENV PORT 8001 and EXPOSE 8001
  - Environment block will include DATASETTE_SECRET 's3cr3t'

Example — branch install + spatialite + apt packages:
- Inputs:
  - branch: "feature-branch"
  - install: ["some-plugin==1.2"]
  - spatialite: True
  - apt_get_extras: ["curl"]
  - secret: "another-secret"
- Outcome:
  - install resolves to ["https://github.com/simonw/datasette/archive/feature-branch.zip", "some-plugin==1.2"]
  - apt_get_extras becomes a list copy of ["curl"] extended with spatialite packages
  - The Dockerfile will include an apt RUN block produced by formatting APT_GET_DOCKERFILE_EXTRAS with the joined apt package names (caller must ensure that APT_GET_DOCKERFILE_EXTRAS exists in the module)
  - ENV SQLITE_EXTENSIONS will be present and point to /usr/lib/x86_64-linux-gnu/mod_spatialite.so

Usage note and defensive recommendations:
- Validate and coerce inputs before calling (e.g., ensure files and install are lists of strings).
- If you plan to request apt package installation, confirm that the module defines APT_GET_DOCKERFILE_EXTRAS; otherwise a NameError will occur when rendering the apt block.
- Because environment_variables is mutated in-place, pass a copy if you need to preserve the caller-side mapping unchanged.

## `datasette.utils.__init__.temporary_docker_directory` · *function*

## Summary:
Creates a temporary build context directory containing the provided SQLite files, a generated Dockerfile (and optional metadata.json), plus optional templates/plugins/static trees; yields the directory path for use (typically inside a with-context) and guarantees cleanup and cwd restoration when the context exits.

## Description:
This generator-based context manager prepares a self-contained directory suitable for building a Datasette Docker image. It:
- creates a temporary directory and a subdirectory named for the deployment,
- resolves and copies (or hard-links) each provided database file into that subdirectory,
- parses and merges metadata and writes metadata.json when present,
- builds a Dockerfile string via make_dockerfile and writes it into the directory,
- duplicates optional templates, plugins, and static mount directories into the build context (using link-or-copy semantics),
- yields the path to the populated directory, and
- always removes the temporary directory and restores the original working directory when the generator exits (including on error).

Known callers:
- No explicit callers were found in the provided snapshot. Typical callers are CLI commands or packaging/deploy utilities that need a temporary Docker build context before running docker build or similar steps.

Why a separate function:
- Encapsulates the multi-step preparation of a build context (filesystem creation, metadata parsing/merge, Dockerfile generation, linking/copying assets) and the corresponding cleanup, making the packaging/deploy code straightforward and robust to errors.

## Args:
    files (Iterable[str]):
        Relative paths (relative to the current working directory at call time) to database files to include in the build context.
        - Each entry is used to produce a source path (os.path.join(saved_cwd, file)) and a destination filename (basename of the entry).
        - Must be iterable; empty iterable is allowed (produces no -i flags in the Dockerfile and no files copied).
    name (str):
        Directory name to create inside the temporary directory (used to form tmpdir/<name>).
        - Should be a simple name (no path traversal). If it contains path separators, os.mkdir may fail.
    metadata (file-like or None):
        Optional file-like object exposing read() that returns metadata text (JSON or YAML). If provided, its contents are parsed with parse_metadata().
        - If None or falsy, no metadata is read and metadata_content defaults to {}.
    extra_options (Any):
        Passed through to make_dockerfile unchanged (typically a str of extra CLI options).
    branch (Any):
        Passed to make_dockerfile. If present, that influences how the Dockerfile installs datasette (branch archive vs PyPI).
    template_dir (str | falsy):
        If truthy, treated as a relative path (from saved cwd) to a templates directory to copy into the build context under "templates".
    plugins_dir (str | falsy):
        If truthy, treated as a relative path (from saved cwd) to a plugins directory to copy into the build context under "plugins".
    static (Iterable[Tuple[str,str]]):
        Iterable of (mount_point, path) pairs. For each pair, the function copies/link-duplicates the directory at saved_cwd/path into the build context at <datasette_dir>/<mount_point>.
        - Must be iterable; if empty, no static directories are processed.
    install (Iterable[str]):
        Passed to make_dockerfile to determine pip install targets. Should be iterable of strings.
    spatialite (bool):
        Passed to make_dockerfile. When True may cause additional apt packages and environment variables to be injected by make_dockerfile.
    version_note (Any):
        Passed to make_dockerfile (optional version note string).
    secret (str):
        Secret value passed to make_dockerfile (and ultimately injected into the Dockerfile ENV via make_dockerfile).
    extra_metadata (dict | None, default None):
        Mapping of metadata keys/values to merge into parsed metadata. Only keys whose value is not None are merged.
        - Default: None (treated as {}).
    environment_variables (dict | None, default None):
        Mapping to supply to make_dockerfile. The function itself does not mutate this mapping, but make_dockerfile may mutate it in-place.
    port (int, default 8001):
        Numeric port forwarded into the Dockerfile generation.
    apt_get_extras (Iterable[str] | None, default None):
        Passed to make_dockerfile to request additional apt packages in the Dockerfile.

## Returns:
    Generator that yields:
        str: Absolute path to the temporary datasette build directory (tmpdir/<name>).
    Behavior:
        - The caller should use this function as a context manager (for example: with temporary_docker_directory(...) as build_dir: ...). Execution within the with-block receives the build_dir path.
        - When the context exits (normal return or exception), the temporary directory will be removed and the process CWD restored.

## Raises:
    - BadMetadataError:
        Raised by parse_metadata(metadata.read()) when metadata text is neither valid JSON nor valid YAML. Occurs only when metadata is truthy and its contents fail parsing.
    - NameError / TypeError (from make_dockerfile):
        Any error raised by make_dockerfile (e.g., NameError if module-level templates required by make_dockerfile are missing, or TypeError from unexpected argument types) will propagate.
    - OSError / FileNotFoundError / PermissionError (filesystem operations):
        - os.mkdir(datasette_dir) may raise OSError if creation fails (permission denied, invalid name, etc).
        - os.chdir(datasette_dir) may raise OSError if directory missing or inaccessible.
        - Opening/writing "metadata.json" or "Dockerfile" may raise I/O errors (PermissionError, OSError).
        - link_or_copy and link_or_copy_directory may raise errors from the underlying filesystem copy operations (FileNotFoundError if a source file/directory does not exist; PermissionError; OSError).
    - Any other exceptions raised during the setup phase will propagate to the caller; in all cases the finally block will attempt to cleanup the TemporaryDirectory and restore the current working directory.

## Constraints:
Preconditions:
    - The current working directory (when calling) must be readable and contain the relative paths referenced by `files`, `template_dir`, `plugins_dir`, and entries in `static`.
    - `files` must contain paths that exist and are readable by the calling process; otherwise link_or_copy will raise a filesystem error.
    - `name` will be used as a single-level directory name inside the temporary directory; avoid path separators in `name` to prevent unexpected os.mkdir failures.
    - `metadata`, if provided, must expose a read() method that returns the metadata text as str.
    - `static` must be an iterable of (mount_point, path) pairs; each `path` is resolved relative to the saved cwd.
Postconditions:
    - While inside the yielded context, the build directory exists at the yielded path and contains:
        - a Dockerfile,
        - optionally metadata.json (if metadata_content was non-empty),
        - the provided files (copied or hard-linked),
        - optional templates/, plugins/, and static mount-point directories as requested.
    - After the context exits, the temporary directory and all its contents are removed (tmp.cleanup()) and the process working directory is restored to its original value.
    - Any exceptions raised during setup will still trigger cleanup in the finally block.

## Side Effects:
    - Filesystem:
        - Creates a TemporaryDirectory and a subdirectory named by `name`.
        - Writes Dockerfile and (optionally) metadata.json in the created datasette_dir.
        - Copies or hard-links each file in `files` into the build directory.
        - Copies or hard-links template, plugins, and static directory trees when requested.
        - Removes the TemporaryDirectory and all its contents when the context exits.
    - Process state:
        - Temporarily changes the current working directory to the build directory for the setup/writing operations; the original CWD is restored in the finally block.
    - No network, database, or persistent global state is modified by this function itself (network/installation steps are performed later by Docker build or at runtime).

## Control Flow:
flowchart TD
    A[Start] --> B[extra_metadata = extra_metadata or {}]
    B --> C[Create TemporaryDirectory tmp]
    C --> D[Create datasette_dir = tmp.name/name; os.mkdir(datasette_dir)]
    D --> E[saved_cwd = os.getcwd()]
    E --> F[Compute file_paths = join(saved_cwd, each file) and file_names = basename(each file)]
    F --> G{metadata provided?}
    G -- yes --> G1[metadata_content = parse_metadata(metadata.read())]
    G -- no  --> G2[metadata_content = {}]
    G1 --> H[Merge non-null keys from extra_metadata into metadata_content]
    G2 --> H
    H --> I[Call make_dockerfile(file_names, metadata_filename?, ...)]
    I --> J[os.chdir(datasette_dir)]
    J --> K{metadata_content non-empty?}
    K -- yes --> K1[write metadata.json with json.dumps(metadata_content)]
    K -- no  --> L
    K1 --> L
    L --> M[write Dockerfile with returned string]
    M --> N[for each (path, filename) -> link_or_copy(path, datasette_dir/filename)]
    N --> O{template_dir?}
    O -- yes --> O1[link_or_copy_directory(saved_cwd/template_dir -> datasette_dir/templates)]
    O -- no  --> P
    O1 --> P
    P --> Q{plugins_dir?}
    Q -- yes --> Q1[link_or_copy_directory(saved_cwd/plugins_dir -> datasette_dir/plugins)]
    Q -- no  --> R
    Q1 --> R
    R --> S[for each (mount_point,path) in static -> link_or_copy_directory(saved_cwd/path -> datasette_dir/mount_point)]
    S --> T[yield datasette_dir]
    T --> U[context body executes]
    U --> V[finally: tmp.cleanup(); os.chdir(saved_cwd)]
    V --> End

## Examples:
Example — typical usage (recommended pattern):
    try:
        with temporary_docker_directory(
            files=["db1.sqlite","db2.sqlite"],
            name="my-datasette",
            metadata=open("metadata.yml") if os.path.exists("metadata.yml") else None,
            extra_options=None,
            branch=None,
            template_dir="templates",
            plugins_dir="plugins",
            static=[("public","static")],
            install=["some-plugin"],
            spatialite=False,
            version_note=None,
            secret="replace-with-secret",
            extra_metadata={"title": "My Published Dataset"},
            environment_variables={"ADDITIONAL":"value"},
            port=8001,
            apt_get_extras=None,
        ) as build_dir:
            # build_dir is a temporary directory containing:
            # - Dockerfile
            # - optional metadata.json
            # - db1.sqlite and db2.sqlite
            # - templates/, plugins/, and public/
            # A caller would typically run: subprocess.run(["docker","build","-t","my-image","."]), cwd=build_dir
            pass
    except BadMetadataError as e:
        # metadata parse error from parse_metadata(metadata.read())
        handle_metadata_error(e)
    except (FileNotFoundError, PermissionError, OSError) as e:
        # missing source file or filesystem permission problems from link_or_copy / copy operations
        handle_filesystem_error(e)

Example — defensive recommendations:
    - Validate that every file in `files` exists before entering the context if you want to fail early with a clear message.
    - Pass a copy of an environment_variables dict if you must preserve the original mapping (make_dockerfile may mutate it).
    - If `name` comes from user input, sanitize it to avoid path separators or injection-like values.

Notes:
    - This function is intended to be used as a context manager (the implementation yields once and performs cleanup in finally). The module imports and usage patterns in the repository assume it will be wrapped or decorated appropriately so it can be used with the with-statement.

## `datasette.utils.__init__.detect_primary_keys` · *function*

## Summary:
Return an ordered list of the column names that form a table's primary key, ordered by primary-key ordinal when available.

## Description:
This synchronous helper converts the PRAGMA-derived column metadata returned by the schema-inspection helper into a simple list of primary-key column names.

Known callers (within the supplied snapshot):
    - None directly in the provided snapshot. Higher-level code that needs primary-key column names (URL builders, row lookups, schema renderers) is expected to call this helper or an async wrapper that uses it.

Typical trigger/context:
    - Called during schema introspection when code must determine which columns uniquely identify rows for a given table.

Why this logic is extracted:
    - Keeps higher-level logic free from PRAGMA details and the Column record shape. It provides a compact, stable output (list of names) that other components can depend on.

## Args:
    conn (sqlite3.Connection or DB-API connection-like object)
        - Synchronous connection-like object accepted by table_column_details.
        - Must support conn.execute(sql) returning a cursor-like object with fetchall().
    table (str)
        - Table identifier forwarded to table_column_details (which escapes it with escape_sqlite).
        - Must be a string or string-like object acceptable to escape_sqlite and the SQLite engine.

Interdependencies and expectations:
    - Delegates to table_column_details(conn, table) to obtain column metadata.
    - Expects each returned Column record to provide:
        * name (str): column name. May be an empty string for expression/hidden columns in some SQLite versions.
        * is_pk (int or bool-like): zero/False for non-PK columns, or a positive integer (1,2,...) / True for PK columns. The implementation uses this attribute to filter and order PK columns.
    - If table_column_details raises, this function will propagate that exception unchanged.

## Returns:
    list[str]
        - A list of column.name strings for every Column where column.is_pk is truthy.
        - Ordering:
            * If column.is_pk holds 1-based ordinals for composite primary keys (common in SQLite PRAGMA output), the list is sorted ascending by that ordinal so the lowest ordinal appears first.
            * If column.is_pk is a boolean True for all PK columns (no ordinals), sorting does not change relative order; the stable sort preserves the order supplied by table_column_details.
        - If no primary-key columns are found, returns an empty list [].
        - Note: column.name may be an empty string for certain expression or hidden columns; callers should not assume names are always non-empty.

## Raises:
    - Any exception raised by table_column_details is propagated (common examples):
        * sqlite3.OperationalError if the PRAGMA fails or the connection is invalid/closed.
        * Any other sqlite3.* exceptions arising from executing PRAGMA.
    - AttributeError:
        * If table_column_details returns items that do not have the required .is_pk or .name attributes, an AttributeError will be raised when this function attempts to access them.
    - TypeError / AttributeError:
        * If conn does not implement execute() or the returned cursor has no fetchall(), these errors will surface from table_column_details.

## Constraints:
Preconditions:
    - conn must be compatible with table_column_details (support conn.execute(...).fetchall()).
    - table must be an identifier valid for escape_sqlite and SQLite.
    - Column records returned by table_column_details must expose .is_pk and .name.

Postconditions:
    - No global or database state is modified.
    - The function returns a list of strings (possibly empty) representing PK column names, or it raises an exception propagated from the underlying helper or AttributeError if the returned records lack expected attributes.

## Side Effects:
    - None beyond calling table_column_details, which performs read-only PRAGMA queries against the supplied connection.
    - No filesystem, network, or global-state side effects.

## Control Flow:
flowchart TD
    Start --> CallCols[Call table_column_details(conn, table)]
    CallCols --> ColsReturned[Receive list of Column records]
    ColsReturned --> Filter[Filter columns where column.is_pk is truthy]
    Filter --> AnyPKs{Any PK columns found?}
    AnyPKs -- No --> ReturnEmpty[Return []]
    AnyPKs -- Yes --> SortByOrdinal[Sort PK columns by column.is_pk ascending]
    SortByOrdinal --> MapNames[Map sorted columns to column.name]
    MapNames --> ReturnNames[Return list of names]
    ReturnEmpty --> End
    ReturnNames --> End

## Examples:
1) Basic usage (synchronous):
    try:
        pk_names = detect_primary_keys(conn, "users")
        # pk_names is a list of strings, e.g. ["id"] or ["user_id","group_id"]
    except sqlite3.OperationalError as e:
        # handle database-level errors (invalid table, closed connection, etc.)
        raise

2) Composite primary key (ordinal values present):
    - If table_column_details yields two PK columns with is_pk values 1 and 2:
        detect_primary_keys(conn, "membership") -> ["user_id", "group_id"]

3) No primary key:
    - For a table or view without PK columns:
        detect_primary_keys(conn, "logs") -> []

## `datasette.utils.__init__.get_outbound_foreign_keys` · *function*

## Summary:
Returns a list of single-column outbound foreign key relationships for the given table by querying SQLite's PRAGMA foreign_key_list and filtering out multi-column (compound) foreign keys.

## Description:
This function inspects the SQLite schema for the specified table and returns only those outbound foreign key constraints that consist of a single column. It performs a read-only PRAGMA query against the provided database connection to obtain the foreign key information, normalizes the rows into a consistent dictionary form, then removes any foreign key entries that are part of a compound foreign key (multiple columns that share the same foreign key id).

Known callers within the codebase:
- No direct callers were found in the provided repository memory. Typical use-cases in this project: schema introspection routines, API endpoints or UI code that need to show or traverse simple foreign-key relationships (e.g., "jump to related rows" links). This function is designed to be called during schema inspection stages (for example, when building table metadata), not during high-frequency query loops.

Why this logic is extracted into its own function:
- Responsibility boundary: encapsulates the SQLite-specific PRAGMA call and the logic to filter out compound foreign keys. This keeps higher-level code (which consumes simple outbound relationships) free from PRAGMA parsing details, and centralizes handling of SQLite's column order and ID-based grouping logic in one place.

## Args:
    conn (sqlite3.Connection or DB-like object):  
        A DB connection or object exposing execute(sql) -> cursor and cursor.fetchall() -> list[tuple]. The function expects conn.execute(...) to return a cursor-like object with a fetchall() method. The conn must be connected to an SQLite database.
    table (str):  
        Name of the table whose outbound foreign keys should be inspected. This string is inserted verbatim into the PRAGMA call inside square-bracket identifier quoting: PRAGMA foreign_key_list([<table>]). The caller should pass the bare table name (not quoted). The function does not perform additional escaping beyond square-bracket quoting; callers should avoid passing unsafe, untrusted input as the table name.

Interdependencies:
- conn must implement execute() and the underlying database must understand the PRAGMA foreign_key_list(table) statement.
- The PRAGMA returns rows with the expected 8 columns (id, seq, table, from, to, on_update, on_delete, match); otherwise the function may raise an unpacking error.

## Returns:
    list[dict]: A list of dictionaries, each describing a single-column outbound foreign key on the given table. Each dictionary has these keys:
        - "column" (str): local column name in `table` that references another table.
        - "other_table" (str): name of the referenced table.
        - "other_column" (str): referenced column name in the other table.

    Edge cases and possible return values:
        - [] (empty list) if the table has no foreign keys or only compound (multi-column) foreign keys.
        - One entry per single-column foreign key. If a multi-column foreign key exists, none of its columns will appear in the returned list because they share the same PRAGMA "id".
        - If PRAGMA returns rows but some rows are None, those rows are skipped.

## Raises:
    - sqlite3.OperationalError (or the DB driver's equivalent) if the PRAGMA execution fails (for example, if the table name is invalid in the context of the database).
    - AttributeError if `conn` does not provide an execute method returning a cursor with fetchall().
    - ValueError (unpacking error) if a returned row does not have the expected number of columns (the code attempts to unpack 8 values per row). This can occur if the DB driver or SQLite version returns a different shape for PRAGMA foreign_key_list results.

Note: The function does not explicitly catch these exceptions; callers should handle them as appropriate.

## Constraints:
Preconditions:
    - The `conn` must be a live SQLite database connection (or compatible DB-like object) and accept PRAGMA statements.
    - The `table` parameter must be the intended table name, with no additional quoting that would break the square-bracket identifier notation.

Postconditions:
    - No modifications are made to the database state.
    - The returned list contains only single-column outbound FKs (compound foreign keys are excluded).

## Side Effects:
    - None beyond a read-only query to the SQLite database. The function executes a PRAGMA statement and fetches results; it does not write to disk, modify global state, or call external services.

## Control Flow:
flowchart TD
    Start --> ExecutePRAGMA[Execute PRAGMA foreign_key_list([table])]
    ExecutePRAGMA --> FetchAll[fetchall() -> infos]
    FetchAll --> CheckInfos{infos empty?}
    CheckInfos -- Yes --> ReturnEmpty[Return []]
    CheckInfos -- No --> Iterate[For each info in infos]
    Iterate --> InfoIsNone{info is None?}
    InfoIsNone -- Yes --> Skip[Skip entry]
    InfoIsNone -- No --> Unpack[Unpack into id, seq, table_name, from_, to_, on_update, on_delete, match]
    Unpack --> Append[Append dict with column, other_table, other_column, id, seq to fks]
    Append --> LoopBack[Continue loop]
    LoopBack --> AfterLoop[After loop: compute id_counts]
    AfterLoop --> Filter[Filter fks: keep only those with id_counts[id] == 1]
    Filter --> BuildResult[Map each to dict with column, other_table, other_column]
    BuildResult --> ReturnResult[Return list]
    ReturnResult --> End

## Examples:
Example 1 — basic usage (typical):
    import sqlite3
    conn = sqlite3.connect("example.db")
    try:
        fks = get_outbound_foreign_keys(conn, "orders")
        # fks might look like:
        # [
        #   {"column": "customer_id", "other_table": "customers", "other_column": "id"},
        #   {"column": "product_id", "other_table": "products", "other_column": "id"},
        # ]
    finally:
        conn.close()

Example 2 — handling missing table or PRAGMA errors:
    import sqlite3
    conn = sqlite3.connect(":memory:")
    try:
        try:
            fks = get_outbound_foreign_keys(conn, "nonexistent_table")
        except sqlite3.OperationalError as e:
            # Handle error: table may not exist or PRAGMA failed
            handle_error(e)
    finally:
        conn.close()

Implementation notes for re-implementation:
    - Use PRAGMA foreign_key_list([table]) to obtain rows describing outbound foreign keys.
    - Expect each row to contain 8 elements: id, seq, table, from, to, on_update, on_delete, match.
    - Group rows by the "id" field: if multiple rows share the same id, they form a compound foreign key and should be excluded entirely.
    - Only return mappings for those rows where id is unique (single-column foreign keys), and include only local column, referenced table, and referenced column in the returned dicts.

## `datasette.utils.__init__.get_all_foreign_keys` · *function*

## Summary:
Builds a complete foreign-key map for an SQLite connection by enumerating all tables and collecting each table's incoming and outgoing single-column foreign-key relationships.

## Description:
This function inspects the database schema to produce, for every table, two lists:
- "incoming": other tables that reference this table
- "outgoing": tables that this table references

Known callers within the codebase:
- datasette.database.Database.get_all_foreign_keys — used as the higher-level API that prepares a connection and delegates to this utility to obtain the full FK graph.
- Typical invocation context: schema-inspection or metadata endpoints that need a database-wide view of relationships (e.g., building relationship graphs, exposing "related rows" links in a UI). It is expected to be called when the application needs a snapshot of the schema, not from tight, high-frequency query loops.

Why this logic is extracted into its own function:
- Responsibility boundary: centralizes the logic for iterating all tables and assembling a bidirectional FK mapping, while delegating SQLite-specific row parsing and compound-FK filtering to get_outbound_foreign_keys. This keeps connection-level orchestration separate from per-table PRAGMA parsing and allows reuse wherever a complete FK map is required.

## Args:
    conn (sqlite3.Connection or DB-like object):
        A database connection or object exposing execute(sql) -> cursor semantics. The function calls conn.execute('select name from sqlite_master where type="table"') and then iterates the returned rows. The connection must be open and point to an SQLite database. There is no additional parameter validation.

Interdependencies:
    - Relies on get_outbound_foreign_keys(conn, table) to return a list of single-column outbound FK dicts with keys "column", "other_table", and "other_column".
    - If get_outbound_foreign_keys raises, those exceptions propagate to the caller.

## Returns:
    dict[str, dict]: Mapping keyed by table name (str). Each value is a dict with two keys:
        - "incoming": list[dict] — each dict describes a foreign key from another table to this table:
            - "other_table" (str): table that holds the referencing column
            - "column" (str): column name on this table being referenced
            - "other_column" (str): column name on other_table that references this table
        - "outgoing": list[dict] — each dict describes a foreign key from this table to another:
            - "other_table" (str): referenced table name
            - "column" (str): column name on this table that references the other table
            - "other_column" (str): column name on other_table that is referenced

Edge-case returns:
    - If the database has no tables, an empty dict is returned.
    - If a foreign-key references a non-existent table, that reference is skipped (it will not appear in the mapping).
    - If a table has only compound (multi-column) foreign keys, get_outbound_foreign_keys will exclude them and so no entries for those compound FKs will appear.

## Raises:
    - sqlite3.OperationalError (or the DB driver's equivalent) if the initial SELECT on sqlite_master fails (for example, if the connection is not an SQLite DB).
    - AttributeError if conn does not provide an execute method that returns an iterable of rows.
    - Any exception raised by get_outbound_foreign_keys is propagated unchanged (for example, errors while executing PRAGMA foreign_key_list).
    - No exceptions are caught internally by this function; callers should handle DB errors as appropriate.

## Constraints:
Preconditions:
    - conn must be a valid, open SQLite connection (or DB-like object) that accepts the SELECT query used to list tables.
    - get_outbound_foreign_keys must be available in the calling context and adhere to its contract (returning only single-column outbound FK dicts).

Postconditions:
    - The returned mapping contains an entry for every table discovered via sqlite_master (each mapped to an object with "incoming" and "outgoing" lists).
    - No database modifications are performed by this function; it is read-only.

## Side Effects:
    - Executes read-only SQL against the provided connection (SELECT on sqlite_master and PRAGMA calls invoked indirectly via get_outbound_foreign_keys).
    - Does not write files, mutate global variables, or call external services.
    - May observe transient database state (e.g., concurrent schema changes by other connections may affect results).

## Control Flow:
flowchart TD
    Start --> ListTables[Query sqlite_master for type="table"]
    ListTables --> BuildInitialMap[Build table_to_foreign_keys with empty incoming/outgoing per table]
    BuildInitialMap --> ForEachTable[For each table in tables]
    ForEachTable --> GetOutbound[Call get_outbound_foreign_keys(conn, table)]
    GetOutbound --> ForEachFK[For each fk in returned list]
    ForEachFK --> ExtractFields[Extract other_table, column (from), other_column (to)]
    ExtractFields --> TableExistsCheck{Is other_table in map?}
    TableExistsCheck -- No --> SkipEntry[Skip this foreign key (referenced table missing)]
    TableExistsCheck -- Yes --> AppendIncoming[Append incoming entry to referenced table]
    AppendIncoming --> AppendOutgoing[Append outgoing entry to current table]
    AppendOutgoing --> ContinueFKLoop[Continue next fk]
    ContinueFKLoop --> AfterFKs[After processing all fks for table]
    AfterFKs --> ContinueTableLoop[Continue next table]
    ContinueTableLoop --> EndLoop[After all tables processed]
    EndLoop --> Return[Return table_to_foreign_keys]
    Return --> End

## Examples:
1) Typical usage scenario (narrative):
    - Provide an open SQLite connection for a database file.
    - Call this utility to obtain a mapping of all tables to their incoming and outgoing single-column foreign-key relationships.
    - Use the returned mapping to render relationship links in a UI or to compute a graph of table dependencies.

2) Example of a possible returned structure (JSON-like):
    {
      "customers": {
        "incoming": [
          {"other_table": "orders", "column": "id", "other_column": "customer_id"}
        ],
        "outgoing": []
      },
      "orders": {
        "incoming": [],
        "outgoing": [
          {"other_table": "customers", "column": "customer_id", "other_column": "id"}
        ]
      }
    }

3) Error handling guidance:
    - If the provided connection is not an SQLite connection or has been closed, callers should expect sqlite3.OperationalError or AttributeError; wrap calls in try/except to surface a user-friendly error message.
    - If a foreign key references a table that does not exist in sqlite_master, that reference will be silently skipped (no exception is raised for that specific condition).

## `datasette.utils.__init__.detect_spatialite` · *function*

## Summary:
Check whether a SQLite database connection exposes Spatialite's geometry metadata by detecting a "geometry_columns" entry in sqlite_master; returns True when Spatialite-style geometry metadata exists, otherwise False.

## Description:
This function queries the provided SQLite connection's sqlite_master table to test for the presence of a table or other sqlite_master entry named "geometry_columns". It is used to detect whether a database has Spatialite-style geometry metadata registered.

Known callers within the provided source context:
- No direct callers were provided in the scope for this task. In typical applications, this helper is called during database introspection or initialization to decide whether to enable Spatialite-specific handling (e.g., when deciding to expose geometry columns, register Spatialite virtual tables, or adapt SQL generation).

Why this logic is extracted into a dedicated function:
- Encapsulates the specific query and boolean conversion in one place so higher-level code can simply ask "is this database Spatialite-enabled?" without duplicating SQL or handling the result shape. It isolates the detection logic and makes testing and future changes (alternative detection queries) straightforward.

## Args:
    conn (object): A DB-API-like SQLite connection object (for example, sqlite3.Connection) or any object exposing an execute(sql) method that returns a cursor with a fetchall() method.
        - Required.
        - No other parameters.
        - Interdependencies: conn must be connected to the target database and be usable for executing SQL statements.

## Returns:
    bool: True if the sqlite_master table contains at least one row whose tbl_name is "geometry_columns"; False otherwise.
    - Possible return values:
        - True: One or more rows matched — typical indicator of Spatialite (or equivalent) geometry metadata presence.
        - False: No matching rows — no Spatialite-style geometry metadata detected.

## Raises:
    Any exception raised by conn.execute(...) or the resulting cursor.fetchall() will propagate unchanged.
    - Common examples (depending on the connection implementation): sqlite3.Error, sqlite3.OperationalError, AttributeError (if conn lacks execute or returned cursor lacks fetchall).
    - The function does not catch or wrap these exceptions.

## Constraints:
    Preconditions:
        - conn must be a valid, open connection to a SQLite database (or an object implementing the same execute/fetchall behavior).
        - The connection must permit reading sqlite_master (no access restrictions).
    Postconditions:
        - No modifications to the database or connection are performed.
        - The function returns a boolean and does not alter conn state beyond executing a read query.

## Side Effects:
    - I/O: Executes a read-only SQL query against the provided connection (may result in disk I/O or file access depending on the SQLite backend).
    - No writes are performed.
    - No global variables or external caches are modified.
    - No network calls are performed by this function itself.

## Control Flow:
flowchart TD
    A[Start: receive conn] --> B[Call conn.execute(sql)]
    B --> C[Call cursor.fetchall()]
    C --> D{len(rows) > 0?}
    D -- Yes --> E[Return True]
    D -- No --> F[Return False]
    B --> G[conn.execute raises exception]
    G --> H[Exception propagates to caller]

## Examples:
- Typical usage scenario (described in prose):
    1. Obtain a SQLite connection open to the target database.
    2. Call the function with that connection to determine whether Spatialite-style geometry metadata exists.
    3. Based on the boolean result, the application may enable geometry-related features or skip Spatialite-specific initialization.
    4. Surround the call with error handling to catch and handle database errors (for example, logging or falling back to a non-Spatialite code path) because any database exceptions will propagate.

- Example usage pattern (pseudocode description):
    Acquire a connection object conn.
    Try:
        has_spatial = detect_spatialite(conn)
    Except database-related error as e:
        handle_or_log(e)
        assume has_spatial = False (or re-raise)
    If has_spatial:
        perform Spatialite-aware initialization
    Else:
        proceed with non-spatial logic

## `datasette.utils.__init__.detect_fts` · *function*

## Summary:
Checks whether a companion full-text-search (FTS) table exists for a given SQLite table and returns the companion table name (table + "_fts") if present; otherwise returns None.

## Description:
This small utility inspects SQLite's sqlite_master table to determine whether a table named "<table>_fts" exists when the base table "<table>" exists. It performs two existence checks:
1. Verify the base table exists.
2. If it does, check for the companion FTS table named by appending "_fts" to the base table name.

Known callers within the provided repository snapshot:
    - No direct callers were found in the provided code snapshot. Typical consumers would be search/indexing subsystems or administrative routines that need to detect whether a table has an associated FTS virtual table.

Why this is extracted into a separate function:
    - Encapsulates the two-step existence check (base table then fts companion) into a single reusable utility.
    - Centralizes the specific sqlite_master queries so callers do not duplicate SQL and so future changes to the detection logic (naming conventions or additional checks) are localized.

## Args:
    conn (sqlite3.Connection or DB-API compatible connection-like object):
        - A live SQLite connection object (or any object exposing an execute(sql: str) -> cursor interface).
        - The connection must support executing SQL strings and returning a cursor with a fetchone() method.
    table (str):
        - The base table name to check (e.g., "notes").
        - Must be a simple table identifier (not a SQL expression). The function formats the table name into SQL directly; providing untrusted input may lead to SQL errors or injection risks (see Constraints).

## Returns:
    Optional[str]:
        - If both the base table exists and a companion table named "<table>_fts" exists, returns the companion table name as a string (for example, "notes_fts").
        - Otherwise returns None.
    Edge cases:
        - If the base table does not exist, returns None.
        - If the base table exists but the "<table>_fts" table does not exist, returns None.

## Raises:
    - Passes through exceptions raised by the connection/cursor layer:
        * sqlite3.Error (or other DB-API exceptions) may be raised if the SQL is invalid, the connection is closed, or underlying I/O/permission errors occur.
    - Specific trigger conditions:
        * If the provided table name contains characters that make the generated SQL invalid (for example, unescaped quotes or braces), conn.execute(...) may raise sqlite3.OperationalError or a similar exception.

## Constraints:
    Preconditions:
        - conn must be a valid, open SQLite connection (or compatible object) with execute(sql: str) and the returned cursor must implement fetchone().
        - table must be a str. Prefer table names that are validated or known trusted identifiers (alphanumeric and underscores) to avoid SQL syntax errors or injection.
    Postconditions:
        - No changes are made to the database schema or rows; the function performs only read queries against sqlite_master.
        - The function returns either a string (the FTS table name) or None; it does not return truthy sentinel objects.

## Side Effects:
    - No file, network, or stdout/stderr I/O is performed by this function.
    - No mutation of global state or database state occurs; only SELECT queries against sqlite_master are executed.
    - It may cause the database engine to access the database file via the connection, which is a read operation.

## Control Flow:
flowchart TD
    A[Start] --> B[Execute SELECT for base table]
    B --> C{base table exists?}
    C -- No --> G[Return None]
    C -- Yes --> D[Compute fts_table = table + "_fts"]
    D --> E[Execute SELECT for fts_table]
    E --> F{fts table exists?}
    F -- Yes --> H[Return fts_table name]
    F -- No --> G[Return None]

## Examples:
- Typical usage (described):
    1. Obtain a sqlite3.Connection (for example, via a call that opens the database file).
    2. Call the function with the connection and the base table name, e.g. supply "notes".
    3. If the return value is "notes_fts", a companion FTS table exists; if None, no companion FTS table was found.

- Error handling guidance (prose):
    - Because the function executes raw SQL with the table name interpolated, surround the call with a try/except that catches sqlite3.Error (or the DB-API exception base used in your environment) to handle malformed names, closed connections, or I/O errors. If table names come from user input, validate them against an allowlist or a strict pattern (e.g., r'^[A-Za-z0-9_]+$') before calling this function to avoid SQL syntax issues or injection risks.

- Recommendation:
    - For untrusted table names, validate or sanitize the input rather than relying on this function to be safe against injection. If your application uses a naming convention other than appending "_fts", adapt callers or wrap this utility to enforce that convention.

## `datasette.utils.__init__.detect_fts_sql` · *function*

## Summary:
Constructs an SQL query string that finds SQLite FTS virtual tables which reference the provided table name as their content source.

## Description:
This function builds and returns a single SQL query (string) that, when executed against a SQLite database, searches sqlite_master for virtual tables declared using FTS that reference the specified table.

Known callers within the provided codebase:
- No explicit call sites were present in the supplied context. Typical callers are schema-inspection routines that need to detect whether a regular table is used as the backing content for one or more FTS virtual tables, for example when preparing to drop or migrate a table.

Why this logic is extracted:
- Detecting FTS references requires a specific, somewhat complex SQL pattern against sqlite_master and consistent escaping of the input table name. Centralizing this logic ensures callers do not duplicate the pattern or forget to escape single quotes, and keeps schema-inspection code clearer.

## Args:
    table (str): The target table name to search for in FTS virtual-table CREATE statements.
        - Must be a Python string. The function calls table.replace("'", "''") to escape single quotes for embedding inside SQL string literals.
        - Interdependencies: The escaped value is inserted into:
            * content="{table}" (double-quoted string in the SQL pattern)
            * content=[{table}] (bracketed form)
            * tbl_name = "{table}" (tbl_name comparison)
        - If table is not a str (or str-like object with replace), calling this function will raise an AttributeError.

## Returns:
    str: A SQL query string. Executing this query against a SQLite connection returns rows with a single column named "name" for sqlite_master entries matching any of these patterns:
        - A VIRTUAL TABLE USING FTS with content="{table}"
        - A VIRTUAL TABLE USING FTS with content=[{table}]
        - A VIRTUAL TABLE USING FTS whose tbl_name equals {table}
    Notes and edge cases:
        - The returned value is always a str; there are no conditional or None returns.
        - Only single quotes in the input are escaped (replaced with two single quotes). Double quotes, square brackets, whitespace, or other characters are not otherwise sanitized by this function.
        - The detection relies on matching parts of the CREATE statement text using SQL LIKE patterns; differences in quoting, spacing, comments, or non-standard CREATE statements may lead to false negatives.

## Raises:
    AttributeError: If the provided table argument does not implement replace (e.g., None or an int), calling table.replace("'", "''") will raise AttributeError.
    (The function itself does not explicitly raise other exceptions.)

## Constraints:
Preconditions:
    - The caller must pass a valid table name as a Python str.
    - The returned SQL is intended for execution on a SQLite database using sqlite_master schema table and standard FTS CREATE syntax.

Postconditions:
    - Returns a syntactically complete SQL string with the provided table name inserted and single quotes doubled.
    - No database access or side effects are performed by the function.

Limitations and security considerations:
    - This function does not fully sanitize the table identifier for embedding into raw SQL; because identifiers cannot be parameterized in SQL, callers must ensure the table name is trusted or validated.
    - Recommended safe practices:
        * Prefer whitelisting valid table names (e.g., check against a schema listing or a regex such as r'^[A-Za-z_][A-Za-z0-9_]*$').
        * If the table name originates from user input, validate or coerce it before calling detect_fts_sql.
    - Only single quotes are escaped. Unusual table names containing double quotes, square brackets, newlines, or SQL wildcards (%)/_ may interfere with matching or cause the query to behave unexpectedly.

Additional detail about sqlite_master condition:
    - The query includes rootpage = 0 to target virtual tables (FTS virtual tables typically have rootpage 0 in sqlite_master), which narrows results to virtual-table entries rather than ordinary tables or indexes.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state, global variables, or databases.

## Control Flow:
flowchart TD
    Start([Start]) --> HasReplace{"table has replace() method?"}
    HasReplace -- Yes --> Escape["escaped = table.replace(\"'\",\"''\")"]
    Escape --> Build["sql = template.format(table=escaped)"]
    Build --> ReturnSQL([Return SQL string])
    HasReplace -- No --> AttributeErrorNode["AttributeError raised by calling replace()"]

## Examples:
1) Basic (safe) usage — validate first, then execute:
    - import re
    - if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', table_name):
    -     raise ValueError("Invalid table name")
    - sql = detect_fts_sql(table_name)
    - cursor.execute(sql)
    - fts_tables = [row[0] for row in cursor.fetchall()]

2) Defensive coercion for non-string inputs:
    - table_name = str(table_name)
    - sql = detect_fts_sql(table_name)
    - cursor.execute(sql)
    - matches = cursor.fetchall()

Interpreting results:
    - An empty list indicates no matching FTS virtual tables were found under the SQL patterns used.
    - Matches depend on how FTS tables were declared; if CREATE statements use unusual formatting/quoting, detection may miss them.

## `datasette.utils.__init__.detect_json1` · *function*

## Summary:
Determines whether the SQLite JSON1 extension (the json() SQL scalar function) is available by attempting to execute a simple JSON function call and returning True on success or False on failure.

## Description:
This function tests availability of SQLite's JSON1 extension by executing SELECT json('{}') on a provided database connection (or an in-memory connection if none is provided). Typical callers are initialization or feature-detection code that must decide whether to enable JSON1-dependent features or fallback behavior. The logic is extracted into its own function to centralize the single responsibility of "detect JSON1 support" and to make callers' code clearer and easier to test.

Known callers within provided context:
- No specific callers available in the supplied file context. In practice, this is used during application startup, test setup, or conditional feature enabling where the presence of the json() SQL function must be detected.

Why this function is separate:
- Encapsulates the probe for JSON1 in a single place.
- Hides the try/except probing logic from callers.
- Allows tests to stub or mock detection behavior easily.

## Args:
    conn (sqlite3.Connection | Any, optional): A database connection object with an execute(sql: str) method.
        - If None (default), an in-memory SQLite connection is created via sqlite3.connect(":memory:").
        - The function is duck-typed: any object providing execute(sql: str) that behaves like a DB-API connection is acceptable.
        - If a non-connection object lacking execute is passed, execute will raise an exception which the function catches and maps to False.

## Returns:
    bool: True if executing "SELECT json('{}')" succeeds (indicating that the json() function is available); False if executing that statement raises an exception.
    - Possible return values:
        - True: The database connection accepted and executed the json('{}') expression.
        - False: An exception occurred while executing the statement (e.g., json() not defined, SQL error, or execute raises).

## Raises:
    Any exception raised by sqlite3.connect(":memory:") when conn is None:
        - The sqlite3.connect call is performed outside the try/except block. If establishing the in-memory connection fails (for example, if the sqlite3 implementation raises on connect), that exception will propagate to the caller.
    Note: Exceptions raised by conn.execute(...) are caught by the function and will not propagate; instead the function returns False.

## Constraints:
    Preconditions:
        - If conn is provided, it should be a usable DB-API style connection with an execute(sql: str) method.
        - Caller should be prepared to handle an exception only if sqlite3.connect fails when conn is None.
    Postconditions:
        - The function returns True or False according to whether the SELECT json('{}') call succeeded.
        - If conn was None, an in-memory connection may have been created and left open (the function does not close it).

## Side Effects:
    - May open a new in-memory SQLite connection (sqlite3.connect(":memory:")) when conn is None. That connection is not closed by this function, so the caller is responsible for resource management if needed.
    - No file, network, stdout, database writes, or external service calls are performed by the function itself aside from the SQL execution on the provided connection.
    - No global state is modified.

## Control Flow:
flowchart TD
    Start([Start])
    ConnNone{conn is None?}
    CreateConn[call sqlite3.connect(":memory:")]
    TryExec[try: conn.execute("SELECT json('{}')")]
    ExecSuc[execution succeeds -> return True]
    ExecFail[execution raises Exception -> return False]
    Start --> ConnNone
    ConnNone -- Yes --> CreateConn --> TryExec
    ConnNone -- No --> TryExec
    TryExec -- Success --> ExecSuc
    TryExec -- Exception --> ExecFail

## Examples:
- Example 1: Probe using a new temporary in-memory connection (typical, simple probe)
    result = detect_json1()
    if result:
        # JSON1 is available; enable JSON1-based features
        pass
    else:
        # JSON1 is not available; use fallback implementations
        pass

- Example 2: Probe using an existing connection object (same connection used elsewhere)
    # existing_conn should provide execute(sql: str)
    result = detect_json1(existing_conn)
    if result:
        # existing_conn supports json()
        pass

- Example 3: Handling the potential connect-time exception when relying on in-memory connect
    try:
        result = detect_json1()  # may raise if sqlite3.connect fails
    except Exception as e:
        # handle unexpected sqlite connection failure (rare)
        raise

## `datasette.utils.__init__.table_columns` · *function*

## Summary:
Return a list of column names for the given table by extracting the name field from the detailed PRAGMA-derived column metadata.

## Description:
This tiny helper delegates to the synchronous inspection function that produces normalized per-column metadata (table_column_details) and returns only the name attribute from each Column record. It is useful when callers only need the list of column names rather than the full metadata.

Known callers within the provided snapshot:
    - None explicitly present in the snapshot. Typical call sites in the application include request handlers, schema-rendering utilities, or any code that needs only column names rather than full column metadata.

Why this is factored out:
    - Keeps callers' intent explicit: callers that only need names use this function instead of mapping over the full metadata themselves. This centralizes the simple projection [column.name for ...] so the projection is consistent and easy to reuse.

## Args:
    conn (sqlite3.Connection or DB-API connection-like): A connection-like object supporting conn.execute(sql).fetchall() or otherwise suitable for being passed through to table_column_details. The connection is used only for executing read-only PRAGMA queries via table_column_details.
        - Required. If conn does not provide the expected execute()/fetchall() behavior, the call will raise at runtime.
    table (str): Table identifier to inspect. Passed through to table_column_details (which escapes the value via escape_sqlite before embedding it in a PRAGMA statement).
        - Must be a string or string-like; providing other types may raise errors in escape_sqlite or the underlying SQLite engine.

Interdependencies between parameters:
    - Both arguments are forwarded unchanged to table_column_details; correctness depends on that function's preconditions (e.g., the connection being open and compatible, table being a valid identifier).

## Returns:
    list[str]: A list of column name strings in the same order that SQLite reports the table columns (the ordinal order). Possible return shapes:
        - Non-empty list of strings: when the table exists and has columns.
        - Empty list: when the PRAGMA produced no rows (e.g., the table does not exist or has no columns).
    No other return types are produced by this function.

## Raises:
    - Propagates exceptions raised by table_column_details or by the underlying connection operations, for example:
        * sqlite3.OperationalError (or DB-API-specific errors) if the PRAGMA execution fails (invalid table name, closed connection, etc.).
        * TypeError / AttributeError if conn or the return values do not conform to the expected interface (for example, if table_column_details returns objects without a .name attribute).
        * Any exception raised by escape_sqlite(table) or supports_table_xinfo() (if they fail inside table_column_details).
    This function does not catch or transform exceptions; they bubble up to the caller.

## Constraints:
Preconditions:
    - conn must be a connection-like object compatible with table_column_details (conn.execute(...).fetchall()).
    - table must be a value acceptable to escape_sqlite (typically a string).
    - The module-level Column record used by table_column_details must include a .name attribute (string) on each returned record.

Postconditions:
    - The function returns a list of strings (possibly empty) corresponding to the names of columns reported by the underlying SQLite PRAGMA call.
    - No mutation of global state or the connection occurs beyond performing read-only PRAGMA queries via the helper.

## Side Effects:
    - Performs read-only database metadata queries indirectly via table_column_details (PRAGMA table_xinfo or PRAGMA table_info).
    - No filesystem, network, stdout, or external service side effects are performed by this function itself.
    - No global variables are modified.

## Control Flow:
flowchart TD
    Start --> CallDetails
    CallDetails[call table_column_details(conn, table)] --> GotColumns{rows returned?}
    GotColumns -- Yes --> MapNames[for each column: take column.name]
    MapNames --> ReturnList[return list of names]
    GotColumns -- No --> ReturnEmpty[return []]
    ReturnList --> End
    ReturnEmpty --> End

## Examples:
Example — synchronous usage with sqlite3:
    - Obtain a sqlite3.Connection conn (open and valid).
    - Call names = table_columns(conn, "users").
    - names will be a list of strings in column order, e.g. ["id", "username", "email"].
    - If the "users" table does not exist, names will be [].

Error-handling sketch:
    - To surface DB errors to the caller, allow exceptions to propagate or catch them explicitly:
        try:
            names = table_columns(conn, "users")
        except sqlite3.OperationalError as e:
            # handle invalid table name or closed connection
            raise

Notes for implementers:
    - The function is a simple projection over the Column records returned by table_column_details; reimplementation must ensure the called helper returns objects with a .name attribute (e.g., namedtuple Column with a name field) and that exceptions from the helper are allowed to propagate unchanged.

## `datasette.utils.__init__.table_column_details` · *function*

## Summary:
Inspect a SQLite table's schema using PRAGMA and return a normalized list of column metadata records (one per column), with a consistent "hidden" flag present for each column.

## Description:
This helper executes a PRAGMA-based schema inspection on the provided connection and converts each returned PRAGMA row into a module-level Column record.

Known callers (within this codebase snapshot):
- Database.table_column_details: an async wrapper that executes this synchronous helper via the Database object's execute function.

Why this is factored out:
- Encapsulates low-level PRAGMA SQL, result normalization and the conditional handling for SQLite versions that do or do not support PRAGMA table_xinfo. Keeping this logic in one place ensures callers receive a stable return shape (including a hidden flag) regardless of the SQLite version.

Behavior summary:
- If supports_table_xinfo() returns True, the function runs:
    PRAGMA table_xinfo(<escaped table>)
  and constructs Column instances directly from each returned row.
- If supports_table_xinfo() returns False, the function runs:
    PRAGMA table_info(<escaped table>)
  and constructs Column instances from each returned row with an extra trailing hidden flag of 0 appended to normalize the shape.

Notes:
- The table identifier is passed through escape_sqlite(table) before being embedded into the PRAGMA SQL text.
- The function relies on a module-level Column record/tuple type for constructing return values; each returned object is an instance of that Column type.

## Args:
    conn: A DB-connection-like object that supports conn.execute(sql).fetchall().
        - Typical type: sqlite3.Connection (or a DB-API connection proxy).
        - The code calls conn.execute(...).fetchall(), so conn.execute must return a cursor-like object with fetchall().
    table (str): Table identifier to inspect. Passed to escape_sqlite(table) before embedding into the PRAGMA statement.
        - Should be a string or string-like object accepted by escape_sqlite and by the SQL/SQLite engine.
        - If table is not a string, callers should ensure it's converted/coerced; otherwise runtime errors may occur.

Interdependencies:
- escape_sqlite(table) is used to prepare the identifier for SQL.
- supports_table_xinfo() (imported from sqlite) determines which PRAGMA to use.
- Column (module-level record) is used to construct returned rows.

## Returns:
    list[Column]: A list (possibly empty) of Column records; one element per column reported by the PRAGMA.
    Each Column record corresponds to the fields produced by PRAGMA table_xinfo / table_info plus a normalized "hidden" field. The expected field order (based on standard SQLite PRAGMA output and the fallback behavior) is:
        - cid (int): Column id (0-based ordinal). May be -1 for certain hidden or expression columns in some SQLite versions.
        - name (str): Column name (may be empty for some expressions).
        - type (str or None): Declared type string for the column, or an empty string / None if none declared.
        - notnull (int): 0 or 1 indicating whether the column has a NOT NULL constraint.
        - dflt_value (str or None): The declared default value expression or None if none.
        - pk (int): 0 or 1 (or larger ordinal for composite primary keys in some SQLite versions) indicating primary key membership/position.
        - hidden (int): 0 or 1:
            * If PRAGMA table_xinfo was used, this is the native value returned by table_xinfo.
            * If PRAGMA table_info was used (fallback), this function appends a synthetic 0 to represent hidden=False.
    Edge cases:
        - If the PRAGMA returns no rows (table doesn't exist or has no columns), an empty list is returned.
        - Field types and exact values for some fields (e.g., cid, pk) are determined by the SQLite engine and version; the function only normalizes presence of the hidden field.

## Raises:
    - Propagates any exceptions raised by:
        * supports_table_xinfo() if that call fails (unlikely).
        * escape_sqlite(table) if it raises for invalid input.
        * conn.execute(...) or cursor.fetchall() — e.g., sqlite3.OperationalError if the PRAGMA is invalid or the connection is closed.
    - TypeError / AttributeError may be raised if conn does not provide execute() or the returned cursor has no fetchall().

## Constraints:
Preconditions:
    - The connection object must implement conn.execute(sql) and the returned object must implement fetchall().
    - Module-level names used by the function must be defined (Column, escape_sqlite, supports_table_xinfo).
    - The caller should supply a table identifier appropriate for escape_sqlite and SQLite.

Postconditions:
    - The function returns a list of Column records with exactly the expected number of fields (including the hidden field) per element.
    - No global state is modified by this function.

## Side Effects:
    - Performs read-only execution of a PRAGMA statement on the provided connection.
    - No filesystem, network, or other external I/O is performed by this function itself.
    - No mutation of global variables or the passed connection object (beyond using it to execute the read-only PRAGMA).

## Control Flow:
flowchart TD
    Start --> CheckSupportsXinfo
    CheckSupportsXinfo{supports_table_xinfo() ?}
    CheckSupportsXinfo -- True --> UseTableXinfo
    CheckSupportsXinfo -- False --> UseTableInfo
    UseTableXinfo --> ExecuteXinfo[conn.execute("PRAGMA table_xinfo(<escaped_table>)")]
    ExecuteXinfo --> FetchRowsX[rows = cursor.fetchall()]
    FetchRowsX --> BuildColumnsX[return [Column(*r) for r in rows]]
    UseTableInfo --> ExecuteInfo[conn.execute("PRAGMA table_info(<escaped_table>)")]
    ExecuteInfo --> FetchRowsI[rows = cursor.fetchall()]
    FetchRowsI --> BuildColumnsI[return [Column(*(list(r) + [0])) for r in rows]]
    BuildColumnsI --> End
    BuildColumnsX --> End

## Examples:
Example — synchronous inspection with a sqlite3 connection:
    - Prepare a connection and call the function with the target table name.
    - Result is a list of Column records; each record contains (cid, name, type, notnull, dflt_value, pk, hidden).
    - If the table does not exist, an empty list is returned.

Realistic usage scenario (pseudocode-style description):
    1. Given a sqlite3.Connection conn connected to an on-disk database.
    2. Call columns = table_column_details(conn, "users")
    3. Iterate to render a schema table or generate documentation:
       for col in columns:
           use col.name, col.type, bool(col.notnull), col.dflt_value, bool(col.hidden)

Error-handling sketch:
    - Wrap calls in try/except to surface DB errors:
        * On sqlite3.OperationalError: the table name may be invalid or the connection might be closed.
        * On AttributeError: the conn object did not implement execute()/fetchall().

Implementation note for re-implementers:
    - To reproduce this function correctly, ensure Column is a record type (e.g., namedtuple) whose field order matches the row layout described above. When SQLite lacks table_xinfo, append a 0 to each PRAGMA table_info() row before constructing Column to provide a uniform return shape.

## `datasette.utils.__init__.filters_should_redirect` · *function*

## Summary:
Transforms legacy "_filter_..." special request arguments into a list of normalized (parameter, value) tuples for use in a redirect, and returns tuples that indicate which original special-argument keys should be removed.

## Description:
Parses a mapping of special query/request arguments and emits two kinds of tuples:
- Normalized filter parameters to be added to the redirected URL (param_name, value), where param_name is formed as "{column}__{op}".
- Cleanup directives for original special-argument keys (original_key, None) indicating those keys should be removed during the redirect.

Typical callers and context:
- Request-routing or request-parsing code that wants to migrate legacy filter-form parameters (prefixed with "_filter_") into the normalized query-parameter format and perform a redirect to a cleaner URL.
- No explicit call sites were available in the provided snapshot. Expect callers in request handlers that detect legacy UI form submissions or older API clients and perform an HTTP 302/303 redirect after normalizing query parameters.

Why extracted:
- Centralizes translation rules for both single and numbered legacy filter syntaxes.
- Ensures consistent behavior (including operator parsing and cleanup key generation) across all places that need to canonicalize legacy filter arguments before issuing redirects.

## Args:
    special_args (Mapping[str, str])
        - A mapping-like object (e.g., dict or request.args MultiDict) of parameter names to string values.
        - Keys expected (examples):
            - Single filter: "_filter_column", "_filter_op", "_filter_value"
            - Numbered filters: "_filter_column_1", "_filter_op_1", "_filter_value_1", "_filter_column_2", ...
        - The function uses .get(key) and iterates over the mapping's keys. The mapping must support these operations.

Interdependencies and important notes:
- The function relies on the presence/absence of keys and their values in special_args; it does not mutate special_args.
- Operator parsing may embed a value: an operator string containing "__" is split into operator and value; the embedded value takes precedence over any separate _filter_value.

## Returns:
    list[tuple[str, Optional[str]]]
    - Elements are 2-tuples:
        - For normalized parameters: (f"{column}__{op}", value) where value is a string (may be empty "").
        - For cleanup directives: (original_key, None) where None indicates the original key should be removed.
    - Empty list if no relevant special filter keys are present.
    - The returned list may contain multiple normalized parameters and multiple cleanup tuples. The order:
        - Single-filter tuples (if any) are appended first.
        - Numbered-filter tuples are appended in the iteration order of the internal column key list, which follows the mapping's key iteration order.

## Raises:
    - The function does not explicitly raise. However:
        - If special_args does not implement .get or is not iterable, AttributeError or TypeError may occur.
        - The function assumes string-like values; non-string values will be used as-is without validation.

## Constraints:
Preconditions:
    - special_args must be a mapping-like object supporting .get and iteration.
    - Keys and values should be strings or None-like values.

Postconditions:
    - The function returns a new list and does not modify special_args.
    - For any present single or numbered filter keys, the returned list will include cleanup tuples (key, None) for those keys.

## Side Effects:
    - None. This function is pure in that it has no I/O and does not mutate external state.

## Detailed behavior:
1. Single filter syntax:
    - Reads:
        - filter_column = special_args.get("_filter_column")
        - filter_op = special_args.get("_filter_op") or ""         (default: empty string)
        - filter_value = special_args.get("_filter_value") or ""   (default: empty string)
    - If filter_op contains "__", the function splits on the first "__" into (op, value) and replaces filter_value with that embedded value.
    - If filter_column is truthy, the function appends (f"{filter_column}__{op}", filter_value) to the result.
    - If any of the keys "_filter_column", "_filter_op", "_filter_value" exist in special_args, the function appends cleanup tuples (key, None) for each key present.

2. Numbered filter syntax:
    - Identifies keys matching a filter-column pattern (keys like "_filter_column_1", "_filter_column_2", etc.). The code expects a regex (referred to as filter_column_re) that matches these numbered keys — in practice this means keys of the form "_filter_column_<number>".
    - For each matched column key:
        - Extracts the trailing number suffix with column_key.split("_")[-1] (e.g., "1").
        - Reads:
            - column = special_args[column_key]
            - op = special_args.get(f"_filter_op_{number}") or "exact"   (default: "exact" for numbered filters)
            - value = special_args.get(f"_filter_value_{number}") or ""  (default: empty string)
        - If op contains "__", splits on the first "__" into (op, value), overriding the separate _filter_value_{n}.
        - If column is truthy, appends (f"{column}__{op}", value).
        - Always appends cleanup tuples (f"_filter_column_{number}", None), (f"_filter_op_{number}", None), (f"_filter_value_{number}", None).

Important distinctions:
- Default operator for single-filter syntax is the empty string "", while for numbered filters the default operator is "exact".
- Embedded "__" in the operator string is used to carry a value; when present, the parsed embedded value overrides the separately supplied _filter_value or _filter_value_n.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> ReadSingle["_filter_column?_filter_op?_filter_value?"]
    ReadSingle --> IfSingleColumn{_filter_column truthy?}
    IfSingleColumn -- yes --> ParseSingleOp{"_filter_op contains '__'?"}
    ParseSingleOp -- yes --> SplitSingleOpValue["op, value = split"]
    ParseSingleOp -- no --> KeepSingleOpValue
    SplitSingleOpValue --> AppendSingle["append (column__op, value)"]
    KeepSingleOpValue --> AppendSingle
    IfSingleColumn -- no --> SkipSingleAppend
    AppendSingle --> CleanupSingle["append cleanup tuples for present single keys"]
    SkipSingleAppend --> CleanupSingle
    CleanupSingle --> CollectNumbered["collect keys matching filter_column_re"]
    CollectNumbered --> ForEachNumbered["for each numbered column key"]
    ForEachNumbered --> ReadNumbered["read column, op (default exact), value (default '')"]
    ReadNumbered --> IfNumberOpSplit{"op contains '__'?"}
    IfNumberOpSplit -- yes --> SplitNumberOp["op, value = split"]
    IfNumberOpSplit -- no --> KeepNumberOp
    SplitNumberOp --> IfNumberColumn{column truthy?}
    KeepNumberOp --> IfNumberColumn
    IfNumberColumn -- yes --> AppendNumbered["append (column__op, value)"]
    IfNumberColumn -- no --> SkipNumberedAppend
    AppendNumbered --> AddNumberCleanup["append numbered cleanup tuples"]
    SkipNumberedAppend --> AddNumberCleanup
    AddNumberCleanup --> End([return redirect_params])

## Examples:
Example — single filter:
    Input:
        {"_filter_column": "name", "_filter_op": "contains", "_filter_value": "alice"}
    Output:
        [("name__contains", "alice"),
         ("_filter_column", None), ("_filter_op", None), ("_filter_value", None)]

Example — single op embedding value:
    Input:
        {"_filter_column": "status", "_filter_op": "exact__active"}
    Output:
        [("status__exact", "active"),
         ("_filter_column", None), ("_filter_op", None), ("_filter_value", None)]

Example — numbered filters:
    Input:
        {
            "_filter_column_1": "name", "_filter_op_1": "contains", "_filter_value_1": "bob",
            "_filter_column_2": "age", "_filter_op_2": "exact", "_filter_value_2": "30"
        }
    Output (processing order follows mapping iteration order):
        [("name__contains", "bob"),
         ("_filter_column_1", None), ("_filter_op_1", None), ("_filter_value_1", None),
         ("age__exact", "30"),
         ("_filter_column_2", None), ("_filter_op_2", None), ("_filter_value_2", None)]

Example — how to use returned tuples for a redirect:
    - Take returned tuples with value not None and add them to the query parameters for the redirect URL.
    - Remove keys with value None from the original parameter set (or omit them when building the redirected query string).
    - Issue a redirect (HTTP 302/303) to the normalized URL containing only the normalized filter parameters.

Notes and recommendations:
- If you need deterministic ordering of numbered filters independent of the mapping insertion order, sort the collected numbers (convert suffixes to integers) before processing.
- If you require the exact regular expression object used to detect numbered column keys (filter_column_re), consult the module-level definition in the full source; the function expects keys of the form "_filter_column_<number>".

## `datasette.utils.__init__.is_url` · *function*

## Summary:
Performs a strict syntactic check that accepts only a single HTTP or HTTPS URL string with no whitespace characters.

## Description:
Returns True only when the input is:
1) a Python str (not bytes or other types),
2) beginning with the exact, case-sensitive prefix "http://" or "https://", and
3) containing no whitespace characters anywhere as detected by a module-level regular expression called whitespace_re.

This function is a lightweight predicate intended for quick shape checks (e.g., validating configuration values, simple form validation). It intentionally does not perform full URL parsing, network checks, or semantic validation (host existence, percent-encoding, allowed ports, etc.). The logic is extracted into a single function to centralize the scheme-and-whitespace policy and avoid duplication across the codebase.

Known callers:
- No explicit callers are present in the provided snippet. Typical use cases are configuration validators, form validators, or other utilities that need a cheap conservative test for "is this a single http(s) URL string?".

## Args:
    value (any): The value to test. Any Python object may be passed; non-str inputs (including bytes, None, numbers, lists, etc.) are considered invalid and result in False.

## Returns:
    bool: True if and only if:
        - value is an instance of str (bytes and other types return False)
        - value starts with "http://" or "https://" (case-sensitive)
        - whitespace_re.search(value) returns no match (i.e., contains no whitespace)
    False is returned for all other inputs.

    Representative examples:
        - True: "http://example.com", "https://example.com/path?x=1"
        - False:  b"https://example.com" (bytes), "HTTP://example.com" (uppercase scheme),
                 " https://example.com" (leading space), "http://ex\nample.com" (embedded newline),
                 "" (empty string), None

## Raises:
    NameError: If the module-level variable whitespace_re is not defined at call time (the function calls whitespace_re.search()).
    AttributeError: If whitespace_re exists but does not provide a .search() callable (for example, if it is not a compiled regex-like object).
    Note: The function code does not explicitly raise errors for normal input types; the above are runtime errors caused by improper module state.

## Constraints:
    Preconditions:
        - No required precondition on the input type; the function guards non-str inputs by returning False.
        - The module should define whitespace_re with a .search(string) method (typically a compiled re.Pattern). If this is not true, calling the function may raise NameError or AttributeError.
    Postconditions:
        - The function will always return a bool when whitespace_re is correctly defined.
        - If it returns True, the input is guaranteed to be a str, starts with "http://" or "https://", and contains no whitespace characters.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state.

## Control Flow:
flowchart TD
    Start([Start]) --> IsString{Is value an instance of str?}
    IsString -- No --> ReturnFalse1([Return False])
    IsString -- Yes --> StartsWithScheme{Starts with "http://" or "https://"? (case-sensitive)}
    StartsWithScheme -- No --> ReturnFalse2([Return False])
    StartsWithScheme -- Yes --> ContainsWhitespace{whitespace_re.search(value) finds match?}
    ContainsWhitespace -- Yes --> ReturnFalse3([Return False])
    ContainsWhitespace -- No --> ReturnTrue([Return True])

Notes:
- The scheme check is case-sensitive: "HTTP://example.com" will be rejected.
- By default, the module should provide a whitespace_re such as re.compile(r'\s') (a regex that matches any whitespace character) so whitespace_re.search(value) returns a match for any whitespace in value.

## Examples:
Guidance — defining whitespace_re in the module:
    To avoid NameError/AttributeError, ensure the module defines whitespace_re as a regex-like object with a .search method. A conventional definition is:
        whitespace_re = re.compile(r'\s')
    (This is a suggested convention; the function only requires a .search method that returns a match object when whitespace exists.)

Example 1 — basic validation:
    Input: "https://example.com/path"
    Result: True

Example 2 — leading/trailing whitespace (explicitly rejected):
    Input: " https://example.com"
    Result: False
    Rationale: is_url does not strip input; callers must sanitize before calling if trimming is desired.

Example 3 — sanitizing before validation:
    Given user_input = " https://example.com "
    - user_input.strip() -> "https://example.com"
    - is_url(user_input.strip()) -> True
    Guidance: If you want to accept URLs with accidental surrounding whitespace, explicitly strip() or otherwise sanitize before calling is_url.

Example 4 — bytes and non-strings:
    Input: b"https://example.com" -> False (bytes are not accepted)
    Input: None -> False

Security and usage note:
- Do not rely on this function alone for security-sensitive decisions (open-redirect protection, host allowlists, SSRF mitigation, etc.). For such cases, parse and validate URLs with a robust URL-parsing library and apply additional checks (allowed schemes, host validation, character encoding checks, port ranges, etc.).

## `datasette.utils.__init__.to_css_class` · *function*

## Summary:
Converts an arbitrary text string into a valid, unique CSS class name suitable for use in HTML, returning the input unchanged when it is already a valid CSS class; otherwise returns a sanitized name with a 6-character MD5 suffix to preserve uniqueness.

## Description:
- Purpose and intent:
    Converts user-provided or generated identifiers (for example, table names) into safe CSS class names. It aims to preserve simple valid names unchanged for readability, while guaranteeing uniqueness and safety for names that contain invalid characters or reserved prefixes by appending a deterministic short hash suffix.

- Known callers (from the provided code snapshot):
    - No direct callers were found in the provided snapshot of the repository. In the typical project usage this function is intended to be called at template rendering or HTML generation time when table/column/database names are turned into CSS class attributes.

- Why this logic is a separate function:
    - Centralizes the canonical rules for producing CSS-safe identifiers (validation, sanitization, uniqueness).
    - Keeps template and rendering code simple — callers can rely on this function to handle edge cases (whitespace, invalid chars, prefix issues, collisions after sanitization).
    - Ensures consistent hashing and sanitization is used everywhere it is needed.

## Args:
    s (str): Input text to convert into a CSS class. Must be a text string (unicode in Python 3). The function will call s.encode('utf8'), so passing non-text objects that lack an encode method will raise an exception.

## Returns:
    str: A CSS-safe class name. Behavior details:
    - If s matches the module-level regular expression css_class_re, the function returns s unchanged.
    - Otherwise the function:
        1. Computes md5(s.encode('utf8')) and takes the first 6 hex characters as md5_suffix.
        2. Removes any leading underscores and hyphens from s.
        3. Replaces runs of whitespace in s with single hyphens.
        4. Removes remaining invalid characters using the module-level regex css_invalid_chars_re (via its sub("") method).
        5. Joins the cleaned name and the md5_suffix with a hyphen. If the cleaned name is empty after sanitization, the result will be just the md5_suffix.
    - Examples of possible return shapes:
        * Unchanged: "table1" -> "table1" (if it matches css_class_re)
        * Sanitized + hash: "2021 sales" -> "2021-sales-<6-hex>"
        * Hash only: input that is entirely stripped by sanitization -> "<6-hex>"

## Raises:
    - AttributeError or TypeError: If the provided s is not a text string and does not support encode('utf8'), attempting to call s.encode('utf8') will raise an exception. The function does not catch exceptions raised by encode or by the regex match/sub operations.
    - No other exceptions are explicitly raised by the function.

## Constraints:
- Preconditions:
    - s should be a str (text). The function assumes UTF-8 encoding of the input text.
    - The module-level regular expressions css_class_re and css_invalid_chars_re must be defined elsewhere in the same module. Their exact patterns determine what is considered "already valid" and which characters are removed; this function relies on those definitions but does not define them.

- Postconditions:
    - The returned value is a non-empty str containing only characters permitted by css_invalid_chars_re (i.e., any characters that css_invalid_chars_re removes will not appear in the return value).
    - If the input was considered valid by css_class_re, the original input is returned verbatim; otherwise the returned value contains the deterministic 6-character MD5 suffix and thus is unique for the given original input.

## Side Effects:
- None. The function performs no I/O and mutates no external state. It only computes values and returns a string.

## Control Flow:
flowchart TD
    A[Start: receive s] --> B{css_class_re.match(s)?}
    B -- Yes --> C[Return s unchanged]
    B -- No --> D[Compute md5_suffix = md5(s.encode('utf8'))[:6]]
    D --> E[Strip leading '_' and '-' from s]
    E --> F[Replace whitespace with hyphens in s]
    F --> G[Remove invalid chars using css_invalid_chars_re.sub("", s)]
    G --> H[bits = [cleaned_s, md5_suffix] (omit empty items)]
    H --> I[return "-".join(bits)]
    I --> End

## Examples:
- Basic valid name preserved:
    Input: "items" (assume css_class_re considers this valid)
    Result: "items"

- Name with whitespace and invalid chars:
    Input: "2021 sales!"
    Processing:
      - md5_suffix = first 6 hex of md5("2021 sales!")
      - strip prefixes (none)
      - whitespace -> hyphen -> "2021-sales!"
      - remove invalid chars (exclamation removed) -> "2021-sales"
      - join -> "2021-sales-<6-hex>"

- Name that becomes empty after sanitization:
    Input: "!!!" (all characters removed by invalid-char regex)
    Processing:
      - cleaned_s -> "" (empty)
      - md5_suffix computed -> e.g. "a1b2c3"
      - bits -> ["a1b2c3"]
      - result -> "a1b2c3"

- Robust usage notes:
    - Callers should pass text (str). If callers may pass other types, they should coerce to str first (for example, str(value)) to avoid encode-related errors.
    - Because the suffix uses md5 of the original input, two different inputs that sanitize to the same cleaned string will still produce different outputs (because the md5 suffix differs), preventing collisions.

## `datasette.utils.__init__.link_or_copy` · *function*

## Summary:
Create a filesystem entry at dst that contains the same contents as src by attempting a hard link first and falling back to a file copy if linking is not possible.

## Description:
This small utility is intended for use when populating temporary directories or otherwise duplicating files on the local filesystem where a hard link is preferable for speed and space-savings but may fail if source and destination are on different devices or linking is not permitted.

Known callers within the codebase:
- No direct callers were discovered in the provided repository snapshot. The function is documented and implemented for use by higher-level routines that prepare temporary directories or move files between locations where preserving contents efficiently is desired.

Why this logic is extracted:
- Encapsulates the common pattern "try to hard-link, otherwise copy" in a single place so calling code does not need to repeat error-handling and fallback behavior.
- Makes intent explicit (prefer hard link) and centralizes handling of cross-device or permission issues into one testable function.

## Args:
    src (str | os.PathLike): Path to the existing source file whose contents should be made available at dst. Must point to a regular file (not a directory).
    dst (str | os.PathLike): Path for the destination filesystem entry to create. Parent directory of dst must already exist and be writable.

Interdependencies:
- src must exist and be readable by the process.
- The parent directory of dst must exist and be writable; the function does not create directories.

## Returns:
    None

The function does not return a value. On success, when the function returns normally, dst exists and contains the same byte contents as src (either as a hard link to the same inode or as a separate copied file).

## Raises:
- Any exception raised by shutil.copyfile when the fallback copy is attempted will propagate out of this function. Notable possibilities include:
    - shutil.SameFileError: raised when src and dst refer to the same path (copying a file onto itself).
    - OSError / IOError (or subclasses such as PermissionError, IsADirectoryError, FileNotFoundError): filesystem I/O errors during the copy operation (e.g., insufficient permissions, dst parent directory missing, dst is a directory).
- The initial os.link(src, dst) call may raise OSError variants (e.g., PermissionError, FileExistsError, OSError for cross-device link attempts), but all OSError exceptions raised by os.link are caught and handled by falling back to copying; they will not propagate directly from the link call.

## Constraints:
Preconditions:
- src must refer to an existing regular file readable by the process.
- dst's parent directory must already exist and be writable.
- There must be sufficient disk space for the copy fallback (if the copy branch is taken).

Postconditions (guarantees after normal return):
- dst exists as a file and its contents are byte-wise equal to src at the time of the operation.
- If the link branch succeeded, dst is a hard link to the same inode as src (same device and inode). If the copy branch ran, dst is a distinct file with copied contents.

## Side Effects:
- Filesystem mutation: creates or overwrites dst (shutil.copyfile overwrites dst if it exists).
- Possible change of filesystem metadata (link count increment when hard link is created).
- No network I/O, no global state mutation beyond filesystem, and no stdout/stderr activity by the function itself.

## Control Flow:
flowchart TD
    Start --> TryLink
    TryLink -->|os.link succeeds| Done
    TryLink -->|os.link raises OSError| Copy
    Copy -->|shutil.copyfile succeeds| Done
    Copy -->|shutil.copyfile raises exception| Error
    Error --> End

## Examples:
Example 1 — typical usage when populating a temp directory:
    import tempfile, os
    from datasette.utils import link_or_copy

    src = "/var/data/my.db"
    with tempfile.TemporaryDirectory() as td:
        dst = os.path.join(td, "my.db")
        # After this call, td/my.db exists and contains the same bytes as src.
        link_or_copy(src, dst)
        # Now open or inspect td/my.db as needed.

Example 2 — caller handling copy errors:
    try:
        link_or_copy("/path/to/file.txt", "/tmp/target/file.txt")
    except Exception as e:
        # shutil.copyfile errors (disk full, permission denied, etc.) will be raised here.
        handle_failure(e)

## `datasette.utils.__init__.link_or_copy_directory` · *function*

## Summary:
Attempts to duplicate a directory tree from src to dst using hard links for files when possible; if linking fails, falls back to copying file contents.

## Description:
This helper centralizes the logic for duplicating a directory tree into a destination directory with a best-effort preference for hard links. It first tries to create hard links for files (fast, space-efficient). If an OSError occurs during that attempt (for example when hard links are not permitted or when crossing filesystems), it falls back to copying file contents.

Known callers within the provided code context:
    - No direct callers were identified in the provided source files. Typical callers in an application would be code that needs to deploy or duplicate static assets, templates, or other directory trees where a destination directory should be populated from an existing source directory.

Why this is a dedicated function:
    - Encapsulates the two-step strategy (link-first, then copy-on-failure) so callers do not need to implement or duplicate the fallback behavior.
    - Keeps filesystem-specific error handling constrained to a single place, making it easier to change the fallback policy or add logging later.

## Args:
    src (str | os.PathLike): Path to the source directory that should be duplicated. Must refer to an existing directory (see Preconditions).
    dst (str | os.PathLike): Path to the destination directory where the contents from src will be placed. May be an existing directory; directories will be created as needed.

Interdependencies:
    - Both arguments are treated as directory path-like values and are passed unchanged to copytree. The function does not validate types beyond what copytree enforces.

## Returns:
    None
    - The function performs actions for their side effects (creating files/directories or links) and does not return a value.

## Raises:
    - Any exception raised by the fallback copytree call will propagate to the caller. Common examples from the underlying copytree include:
        * FileNotFoundError / NotADirectoryError: if src does not exist or is not a directory.
        * PermissionError: when the process lacks permission to read src or write dst.
        * OSError or subclass: filesystem errors during the fallback copy.
    - Note: An OSError raised by the initial link-based copy attempt is caught and suppressed; that error does not propagate.

## Constraints:
Preconditions:
    - src should refer to an existing directory readable by the process. If src is missing or not a directory, the fallback copytree will raise an error.
    - Caller should expect that src and dst are not the same path; behavior is dependent on underlying copytree implementation and may be undefined or error-prone if they are identical.

Postconditions:
    - On successful return, dst exists and contains a directory tree reflecting the contents of src.
    - If the link-first attempt succeeded, regular files in dst are hard links to files in src (sharing the same inode on the same filesystem). If the link attempt failed and the fallback succeeded, files in dst are independent copies.
    - If the fallback copy fails, no guarantee is made about the partially-created contents in dst — partial contents may exist and exceptions will propagate.

## Side Effects:
    - File system I/O: creates directories and either hard links or copies of files under dst.
    - May modify filesystem metadata (link counts) on the source files if hard links are created.
    - No network I/O, global variable mutation, or database writes occur in this function.

## Control Flow:
flowchart TD
    Start --> AttemptLinkCopy
    AttemptLinkCopy[Call copytree(src, dst, copy_function=os.link, dirs_exist_ok=True)]
    AttemptLinkCopy -->|success| EndSuccess
    AttemptLinkCopy -->|raises OSError| FallbackCopy
    FallbackCopy[Call copytree(src, dst, dirs_exist_ok=True)]
    FallbackCopy -->|success| EndSuccess
    FallbackCopy -->|raises Exception| EndError
    EndSuccess --> End[Return None]
    EndError --> Error[Exception propagates to caller]

## Examples:
- Typical use:
    Call link_or_copy_directory('/path/to/source', '/path/to/destination') to populate the destination with the source tree. If hard links are permitted and possible, the destination files will be linked to the source; otherwise they will be copied.

- Error handling example (in prose):
    A caller that wants to present a friendly message on failure should wrap the call in a try/except block that handles PermissionError, FileNotFoundError, and OSError. If an exception is caught, the caller may choose to remove any partially-created destination contents or retry with different permissions/paths.

- Cross-filesystem scenario:
    If src is on filesystem A and dst is on filesystem B, the initial attempt to create hard links typically raises OSError (invalid cross-device link). This function will catch that OSError and then perform a full recursive copy into dst; if that copy succeeds, the destination will contain independent file copies.

## `datasette.utils.__init__.module_from_path` · *function*

## Summary:
Loads and executes a Python source file from disk and returns a new ModuleType instance (with the provided name) whose namespace contains the results of executing that file.

## Description:
Creates a fresh types.ModuleType(name), sets module.__file__ to the provided path (and module.__name__ is set by ModuleType(name)), reads and compiles the source file with dont_inherit=True, executes the compiled code in the module's namespace, and returns the module. Any exceptions raised while opening, compiling, or executing are propagated.

Known callers within the codebase:
- None were present in the immediate context provided. Typical external use-cases include ad-hoc plugin loaders, test helpers that need to load a single-file module by path, or dynamic configuration loaders that treat a Python script as a module.

Why this is factored out:
- Encapsulates the common pattern of reading, compiling, and executing a source file into an isolated module object without touching global import state. Callers that need this primitive can avoid duplicating boilerplate and clearly handle registration, package context, and security separately.

## Args:
    path (str | os.PathLike):
        Filesystem path to the Python source file. Passed to open(path, "r"); must be readable by the process.
    name (str):
        Name used to construct the ModuleType. This becomes module.__name__ and is used in repr(module). The function does not validate that 'name' is a valid importable or package name.

Interdependencies:
- 'path' and 'name' are independent; the function does not register the created module under 'name' in sys.modules or set package metadata.

## Returns:
    types.ModuleType
        A newly-created module instance with:
        - module.__name__ == name (set by ModuleType(name))
        - module.__file__ == path
        - module.__dict__ populated by executing the compiled source

Edge cases:
- The returned module is not placed into sys.modules; it is an isolated object. Relative imports inside the executed file will generally fail unless the module's __package__ and sys.modules entries are set appropriately — something this function does not do.

## Raises:
    FileNotFoundError:
        If the file at 'path' does not exist (raised by open()).
    OSError / PermissionError:
        For filesystem errors opening/reading the file.
    SyntaxError / IndentationError:
        If compile(...) fails because the source is invalid. The compile call uses filename=path for reporting.
    Any exception raised by the module's top-level code:
        Exceptions raised during exec(compiled_code, module.__dict__) propagate unchanged (for example ImportError, RuntimeError, ValueError, or custom exceptions).

Implementation detail:
- compile(..., dont_inherit=True) prevents the compiled code from inheriting caller-side __future__ flags. The module's language semantics are determined only by the file's contents and interpreter defaults.

## Constraints:
Preconditions:
- 'path' must point to a readable text file containing valid Python source for the running interpreter.
- This function does not set module.__package__, does not create or modify sys.modules entries, and therefore does not establish package context required for relative imports.

Postconditions:
- The returned ModuleType has __name__ and __file__ set and its namespace populated by executing the source.
- No changes are made to sys.modules or sys.path by this function.

## Side Effects:
- I/O: opens and reads the file at 'path' using open(path, "r") (text mode). The system default encoding is used unless the caller reads the file themselves with a chosen encoding.
- Arbitrary code execution: executing the module's top-level code can perform any side effects (file I/O, network access, DB writes, spawning threads, registering handlers, etc.).
- The function itself does not modify global import state (e.g., sys.modules).

Security note:
- Do not use this function on untrusted code; executing arbitrary source runs with the process's privileges.

## Control Flow:
flowchart TD
    A[Start] --> B[Create ModuleType(name) -> module.__name__]
    B --> C[Set module.__file__ = path]
    C --> D[Open path with open(path, "r")]
    D -->|open fails| E[Raise FileNotFoundError/OSError]
    D --> F[Read file contents]
    F --> G[Compile(contents, filename=path, mode="exec", dont_inherit=True)]
    G -->|compile fails| H[Raise SyntaxError/IndentationError]
    G --> I[exec(compiled_code, module.__dict__)]
    I -->|exec raises| J[Propagate exception from module code]
    I --> K[Return module]

## Examples and guidance:
Basic usage (happy path):
- Given a file /tmp/example.py that defines VALUE = 5, call the function with path="/tmp/example.py" and name="example". The returned module has module.VALUE == 5, module.__name__ == "example", and module.__file__ == "/tmp/example.py".

Handling missing or invalid files:
- Wrap calls in try/except to catch FileNotFoundError/OSError for I/O issues and SyntaxError/IndentationError for invalid source. Also catch general exceptions to handle runtime errors raised during module execution.

Package-relative imports:
- This function does not set up package metadata (module.__package__, sys.modules entries). If the source relies on relative imports, prefer using importlib utilities that correctly establish package context, for example:
  - importlib.util.spec_from_file_location + importlib.util.module_from_spec + spec.loader.exec_module(module)
  - or importlib.machinery.SourceFileLoader to load a module with proper import semantics.
Using those facilities lets you set module.__package__, register the module in sys.modules, and preserve import behavior consistent with standard imports.

Encoding-sensitive files:
- open(path, "r") uses the platform default encoding. If your source file uses a different encoding or contains a coding cookie, consider reading the file explicitly with the correct encoding and then compiling the text, or use importlib which respects coding cookies.

Implementation tips:
- If you control the loader and need import-like behavior (relative imports, discovery), implement a loader using importlib to create a module spec, set __spec__ and __package__, register the module in sys.modules, and then execute the module code via the loader's exec_module.

## `datasette.utils.__init__.path_with_format` · *function*

## Summary:
Builds a request path string that enforces a response format (via URL extension or _format query parameter) while preserving an existing query string and optionally additional query parameters.

## Description:
This helper composes a URL path (string) from either a request-like object or an explicit path. It is intended for use when generating links that should request a specific output format (e.g., JSON, CSV, HTML) while preserving any existing query parameters. The function encapsulates the logic for:
- optionally removing a pre-existing file extension (replace_format),
- placing the desired format either as a path extension (when no extension exists) or as an _format query parameter (when the path already contains an extension),
- merging extra query-string parameters and preserving an existing request.query_string.

Known callers within the codebase:
- Specific call sites were not inspected for this task. Typical call sites are view/template helpers or link-building utilities that need to produce URLs for a particular format (for example, endpoints that offer web and JSON responses).

Why this logic is extracted:
- Centralizes consistent rules for when to use a path extension versus an _format query parameter.
- Ensures existing query strings are preserved and combined in a predictable, sorted order when adding extra parameters.
- Keeps link-construction behavior uniform across the codebase instead of duplicating conditional logic everywhere a format-specific link is built.

## Args:
    request (optional): An object with attributes:
        - path (str): the request path (without query string).
        - query_string (str or bytes): the raw query string (without a leading '?').
      If provided, request.path is used as the base path and request.query_string is used to preserve existing query parameters.
      Default: None.
    path (optional, str): A path string to use if no request is provided. Example: "/foo" or "/foo.csv".
      Default: None.
      Note: Either request or path must be provided; otherwise an AttributeError will occur when the function attempts to operate on None.
    format (str): The desired output format name (e.g., "json", "csv", "html").
      Behavior:
        - If the base path already contains a dot (.), the function will add _format=format to the query parameters.
        - Otherwise the function will append ".{format}" to the path.
      Default: None (but passing None is allowed technically; it will insert the string "None" as an extension or as a query parameter).
    extra_qs (optional, mapping): Additional query-string parameters to merge into the URL.
      Expected type: mapping of str -> str (or values coercible to strings). Keys/values will be passed to urllib.parse.urlencode.
      If omitted or falsy, no additional parameters are merged.
      Default: None.
    replace_format (optional, str): If provided, and the base path ends with ".{replace_format}", that trailing extension is removed before applying the new format logic.
      Example: replace_format="json" will strip a trailing ".json" from the path.
      Default: None.

Interdependencies:
- If both request and path are provided, request takes precedence (request.path is used).
- If the path contains a dot (.), format is added to the query string as _format rather than appended as a path extension.

## Returns:
    str: The composed path string including any appended extension or query string.
    Possible return shapes:
      - "/resource.format" (no query string)
      - "/resource.format?existing=1" (preserves existing request.query_string)
      - "/resource.ext?_format=format&foo=bar" (if base path had an extension)
      - "/resource?_format=format&foo=bar" (if extension existed but was removed via replace_format)
    Notes:
      - Query parameters from extra_qs are URL-encoded with urllib.parse.urlencode over sorted(qs.items()) to yield deterministic ordering.
      - If request.query_string is non-empty and extra_qs is provided, the final URL will contain both (request.query_string first, then an ampersand, then encoded extra_qs).
      - If format is None, the string "None" will be used as the extension or as the value of _format.

## Raises:
    AttributeError:
        - If neither request nor path is provided (path will be None) the function will attempt to call string methods (e.g., endswith, contains ".") on None and raise AttributeError.
        - If replace_format is truthy but path is None, the same AttributeError will occur.
    TypeError / ValueError:
        - urllib.parse.urlencode may raise TypeError/ValueError if extra_qs contains values or keys that are not encodable or if keys are not sortable in Python 3 when sorted(qs.items()) is attempted. Use a dict with string-like keys to avoid this.

## Constraints:
Preconditions:
    - At least one of request or path must be provided and not None.
    - If request is provided, it must expose:
        - path: a str representing the path portion of the URL (no query string),
        - query_string: a str (preferred) representing the existing query string without a leading '?' (if bytes, it will be inserted as-is).
    - extra_qs should be a mapping (dict-like) with keys and values that can be converted to strings and URL-encoded.
Postconditions:
    - The returned value is a string that represents the original path modified to request the specified format, and that preserves any existing and extra query parameters.
    - If extra_qs is provided, the final query-string parameters are deterministic in order (sorted by key).

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and makes no network calls. It only computes and returns a string.

## Control Flow:
flowchart TD
    Start --> Init[Set qs = extra_qs or {}]
    Init --> ChoosePath{request provided?}
    ChoosePath -->|yes| UseRequestPath[base = request.path]
    ChoosePath -->|no| UseGivenPath[base = path]
    UseRequestPath --> CheckReplace
    UseGivenPath --> CheckReplace
    CheckReplace{replace_format and base endswith ".replace_format"?}
    CheckReplace -->|yes| StripExt[remove trailing ".replace_format"]
    CheckReplace -->|no| KeepPath
    StripExt --> HasDot
    KeepPath --> HasDot
    HasDot{Does base contain a "."?}
    HasDot -->|yes| AddQueryParam[qs["_format"] = format]
    HasDot -->|no| AppendExt[base = base + "." + format]
    AddQueryParam --> BuildQuery
    AppendExt --> BuildQuery
    BuildQuery{qs non-empty?}
    BuildQuery -->|yes| EncodeExtra[encode sorted(qs.items())]
    EncodeExtra --> RequestQSCheck{request and request.query_string?}
    RequestQSCheck -->|yes| CombineBoth[return base + "?" + request.query_string + "&" + extra]
    RequestQSCheck -->|no| ReturnExtra[return base + "?" + extra]
    BuildQuery -->|no| RequestOnlyCheck
    RequestOnlyCheck{request and request.query_string?}
    RequestOnlyCheck -->|yes| ReturnRequest[return base + "?" + request.query_string]
    RequestOnlyCheck -->|no| ReturnBase[return base]

## Examples:

Example 1 — Using a request-like object and adding an extra query parameter:
    class Req:
        path = "/cars"
        query_string = "page=2"
    path_with_format(request=Req(), format="json", extra_qs={"foo": "bar"})
    # Returns: "/cars.json?page=2&foo=bar"

Example 2 — Using a bare path that already has an extension:
    path_with_format(path="/cars.csv", format="json", extra_qs={"foo": "bar"})
    # Returns: "/cars.csv?_format=json&foo=bar"

Example 3 — Removing an existing extension before applying the format:
    path_with_format(path="/cars.csv", format="json", replace_format="csv")
    # Returns: "/cars.json"

Example 4 — No request/query string, only format (path without dot gets extension):
    path_with_format(path="/cars", format="csv")
    # Returns: "/cars.csv"

Example 5 — Incorrect usage that raises:
    # Calling without request or path:
    path_with_format(format="json")
    # Raises: AttributeError (function attempts string operations on None)

## `datasette.utils.__init__.CustomRow` · *class*

## Summary:
A lightweight OrderedDict subclass that mimics sqlite3.Row by supporting both key-based and integer index-based lookups and iteration in column order.

## Description:
CustomRow is used when code needs a mapping-like row object that:
- Preserves insertion order (inherits OrderedDict).
- Allows retrieving a column value by column name (mapping access) or by integer column index (0-based).
- Iterates over values in a pre-defined column order.

Typical scenarios:
- Constructing rows from query results or when building a row-like object for templates or APIs that expect sqlite3.Row semantics.
- When you need deterministic iteration order that follows a separate "columns" list rather than the internal dict order.

Motivation / responsibility boundary:
- Provides a small, dependency-free shim where sqlite3.Row is not available or when you need control over the column order.
- Does not attempt to validate that the provided columns list matches stored keys; it only uses the columns list for index-to-key translation and iteration order.

## State:
Attributes (public):
- columns (Sequence[str] or Sequence[hashable]): The ordered sequence of keys that defines column order and mapping from integer index -> key. Must be indexable (supports __getitem__ by int). No automatic validation is performed against the underlying mapping; values may be missing for columns.
- (inherited) mapping storage (OrderedDict): The actual key->value storage is provided by the OrderedDict base class. All standard dict/OrderedDict methods (get, update, items, keys, values, pop, etc.) behave as they normally do.

Notes / invariants:
- columns is expected to be an ordered, indexable sequence (typically list or tuple).
- The class does not enforce that every name in columns is present in the mapping. If a missing key is accessed, a KeyError is raised.
- The __iter__ method yields values for each name present in columns by looking up self[column] for each column in columns — this means iteration order strictly follows columns, not the OrderedDict insertion order.
- The special truthy check in __init__ (if values:) means that passing an empty mapping (e.g., {}) or an empty sequence will NOT call update — resulting in an empty mapping even if columns are provided. Callers who want an empty mapping populated should pass a non-empty values mapping or call update explicitly after construction.

## Lifecycle:
Creation:
- Instantiate with:
    CustomRow(columns, values=None)
  - columns: required, an indexable sequence of keys (e.g., ['id', 'name']).
  - values: optional, a mapping or iterable acceptable to OrderedDict.update(). If values is falsy (None, empty dict, empty list/tuple), it will not be applied.

Usage:
- Access by key:
    row['name']  -> uses OrderedDict lookup (may raise KeyError if missing)
- Access by integer index:
    row[0] -> resolves key = columns[0] then returns row[key] (may raise IndexError if index out of range, or KeyError if resolved key is not present)
- Iterate:
    for value in row:
        ...
  Iteration yields values in the order given by columns.
- Typical order:
    1. Construct with columns (and optionally values)
    2. Read values using row[key] or row[index], or iterate
    3. Mutate using standard dict/OrderedDict methods if needed

Destruction / cleanup:
- No special cleanup required. No context manager or close() method is provided.

## Method Map:
graph LR
    A[CustomRow.__init__(columns, values=None)] --> B[OrderedDict storage initialized]
    A --> C[set columns attribute]
    C --> D[optional update(values) if values is truthy]
    E[CustomRow.__getitem__(key)] -->|int key| F[columns[key] -> lookup in OrderedDict]
    E -->|non-int key| G[direct OrderedDict lookup]
    H[CustomRow.__iter__()] --> I[yield self[column] for column in columns]

(Above is a simple call/dependency flow: __init__ sets state; __getitem__ uses columns; __iter__ yields values in columns order.)

## Raises:
- __init__:
    - No explicit exceptions are raised by __init__ itself.
    - Passing a non-indexable columns argument (e.g., an int) will cause runtime errors when methods expect indexing; callers should pass an indexable sequence.
- __getitem__(key):
    - IndexError: if key is an int and is out of range for columns (triggered by columns[key]).
    - KeyError: if key is a mapping key (str or other) and not present in the underlying OrderedDict; or if an int maps to a column name that is not present in the mapping.
- __iter__:
    - May raise KeyError (via __getitem__) if a column name listed in columns is missing from the mapping.

## Example:
1) Normal usage
    columns = ['id', 'name', 'age']
    row = CustomRow(columns, {'id': 1, 'name': 'Alice', 'age': 30})
    value_by_key = row['name']       # 'Alice'
    value_by_index = row[1]          # 'Alice'  (columns[1] == 'name')
    for v in row:
        # yields 1, 'Alice', 30 in that order

2) Missing value / KeyError
    columns = ['id','name']
    row = CustomRow(columns, {'id': 2})
    row['name']      # raises KeyError

3) Empty values behavior (subtle)
    # Because __init__ only calls update(values) if values is truthy:
    row = CustomRow(['id','name'], {})   # empty dict is falsy -> update not called
    list(row)                            # iteration yields KeyError on first column lookup
    # To avoid this, either pass a non-empty mapping or call update() after construction:
    row = CustomRow(['id','name'])
    row.update({'id':1,'name':'Bob'})

Notes:
- Since CustomRow inherits from OrderedDict, all standard mapping APIs are available and behave as expected.
- Use CustomRow when you need deterministic iteration and integer-index access similar to sqlite3.Row.

### `datasette.utils.__init__.CustomRow.__init__` · *method*

## Summary:
Initializes a CustomRow by recording the ordered column names and optionally populating the row's mapping storage with provided values, affecting the object's visible mapping state.

## Description:
- Known callers and contexts:
    - Constructed wherever a row-like object is needed that supports both key and integer-index access and deterministic iteration order, for example:
        - converting SQL query results into row objects for templates or JSON APIs,
        - building synthetic rows in application code before returning them to callers,
        - test fixtures that need sqlite3.Row-like behavior.
    - Lifecycle stage: invoked at object creation time to set up the column ordering and (optionally) seed the mapping storage before any reads or further mutations occur.

- Why this logic is a separate method:
    - As the class constructor, it explicitly separates two responsibilities: (1) establish the column-order metadata used by integer-index access and iteration; and (2) optionally populate the underlying mapping storage. Keeping that logic in __init__ centralizes object invariants and makes subsequent methods (like __getitem__ and __iter__) rely on predictable state without duplicating initialization logic.

## Args:
    columns (Sequence[hashable]):
        - Required.
        - An ordered, indexable sequence of column names/keys (commonly list or tuple of strings).
        - Used by integer-index lookups (columns[0] -> first column name) and to define the iteration order.
        - No validation is performed here to ensure the sequence contains unique names or that the mapping contains the same keys.
    values (Optional[Mapping or Iterable[tuple]] = None):
        - Optional.
        - If provided and truthy, passed to the underlying mapping's update() method to populate the row (OrderedDict) with key/value pairs.
        - Accepts any input supported by OrderedDict.update(), such as a mapping, an iterable of (key, value) pairs, or keyword arguments (if the caller invokes update separately).
        - Important behavior: the constructor only calls update(values) when values is truthy. Falsy values (None, {}, [], (), "") are ignored and will not populate the mapping.

## Returns:
    None
    - The constructor returns None as usual; its observable effect is the mutated state of the new CustomRow instance.

## Raises:
    - __init__ itself does not explicitly raise exceptions.
    - Indirect errors that may occur later (not raised by this method) include:
        - IndexError: if callers later access by integer index and columns is not indexable or the index is out of range.
        - KeyError: if code later looks up a column name that is not present in the mapping because values was omitted or did not contain that key.
    - Note: Passing non-indexable objects for columns will not raise here but will cause runtime errors when index-based access is used.

## State Changes:
- Attributes READ:
    - None. __init__ does not read existing self attributes.
- Attributes WRITTEN:
    - self.columns is assigned to the provided columns argument.
    - Underlying mapping storage (inherited OrderedDict contents) may be modified via self.update(values) if values is truthy; this writes key/value pairs into self.

## Constraints:
- Preconditions:
    - The caller must provide an indexable sequence for columns if integer-index access or ordered iteration will be used.
    - If values should populate all column names, callers must provide a non-falsy mapping/iterable containing those keys (or call update after construction).
- Postconditions:
    - After return:
        - self.columns references the same object passed in as columns.
        - If values was truthy, the mapping storage contains the entries provided by values (as per OrderedDict.update semantics).
        - If values was falsy (including empty mapping/sequence), the mapping storage remains untouched by __init__ (empty unless the subclass or other initialization populated it).

## Side Effects:
    - No I/O, no external service calls.
    - Potential mutation of the new instance: writes self.columns and may populate the instance's mapping data via update(values).
    - No mutation of input arguments is performed by this code (it stores a reference to the columns object but does not modify it).
    - Developers should be aware of the subtle behavior that an empty but valid values container (e.g., {}) is falsy and therefore will not be applied; this can leave the new CustomRow mapping empty unless update is invoked after construction.

### `datasette.utils.__init__.CustomRow.__getitem__` · *method*

## Summary:
Lookup a value by column name or by positional index (mapping integer indexes to column names) and return the stored value without modifying the CustomRow.

## Description:
This method implements dual lookup semantics so a CustomRow can be accessed both like a mapping (row["column_name"]) and like a sequence (row[0]). When called with an integer, it treats the integer as an index into self.columns, resolves the corresponding column name, and then performs the mapping lookup. When called with a non-integer, it forwards the key directly to the underlying mapping lookup.

Known callers and context:
- CustomRow.__iter__: iterates over self.columns and calls self[column] where column is each column name (string); this therefore uses the name-based lookup branch of __getitem__, not the integer-index branch.
- Any external consumer that expects sqlite3.Row-like semantics (libraries or application code that sometimes index rows by position and sometimes by name) may call this method implicitly by using subscription syntax on CustomRow instances.

Why this is a separate method:
- It overrides OrderedDict.__getitem__ (CustomRow subclasses collections.OrderedDict) to provide sqlite3.Row-compatible dual lookup behavior in one central place so all callers (iteration, direct indexing, external code) get consistent results and error semantics.

## Args:
    key (int | hashable):
        - If an int: used as an index into self.columns (the sequence provided when the CustomRow was constructed).
            - This includes Python booleans because isinstance(True, int) is True; booleans will therefore be treated as integers (True -> 1, False -> 0).
            - Negative integers are supported when the sequence type in self.columns supports negative indexing (typical when self.columns is a list or tuple).
        - If not an int: the key is forwarded unchanged to the underlying mapping lookup (typically a str column name).

## Returns:
    Any:
        - The value stored in the CustomRow for the resolved column key.
        - For integer keys: resolves column_name = self.columns[key] and then returns OrderedDict.__getitem__(self, column_name).
        - For non-integer keys: returns OrderedDict.__getitem__(self, key).

## Raises:
    IndexError:
        - If key is an int and the index is out of range for self.columns. This originates from indexing the self.columns sequence (self.columns[key]).
    KeyError:
        - If the resolved column name (from integer indexing) is not present in the mapping, or if a non-int key is not present in the mapping. These originate from OrderedDict.__getitem__ (invoked via super()).
    TypeError:
        - If the non-int key is unhashable (e.g., a list) the underlying mapping lookup will raise TypeError.
    Notes on exception provenance:
        - Index-related failures come from self.columns sequence indexing.
        - Mapping/key-related failures come from OrderedDict.__getitem__.
        - The method does not catch or wrap these exceptions; they propagate directly.

## State Changes:
    Attributes READ:
        - self.columns: used to map integer indexes to column names.
        - the underlying OrderedDict contents (via super().__getitem__) to retrieve the value.
    Attributes WRITTEN:
        - None. The method performs no writes to self or to external objects.

## Constraints:
    Preconditions:
        - self.columns must be an indexable sequence (e.g., list or tuple) whose elements are intended to be keys in the underlying mapping.
        - The underlying OrderedDict should contain keys named in self.columns for integer lookups to succeed.
    Postconditions:
        - No mutation to the CustomRow or external state.
        - On success, the returned value is exactly the stored value for the resolved column; on failure, an IndexError, KeyError, or TypeError is raised as described.

## Side Effects:
    - None: the method performs no I/O, no network or filesystem operations, and does not mutate objects outside the CustomRow.

## Notes and examples (behavioral):
    - Integer lookup example (conceptual): given self.columns = ["id", "name"], row[0] resolves "id" then returns row["id"].
    - Boolean keys: True is treated as 1 and False as 0 because booleans are instances of int; using True/False as keys therefore triggers integer-index lookup.
    - Negative indexing: row[-1] will work if self.columns supports negative indices (common when self.columns is a list/tuple).
    - Non-int keys are forwarded unchanged: row["name"] directly performs a mapping lookup.
    - If self.columns and the mapping are out of sync (a column name in self.columns is not present in the mapping), integer-based access raises KeyError.
    - The implementation relies on OrderedDict.__getitem__ (via super().__getitem__) for name-based lookups and to produce the KeyError/TypeError behavior for missing or invalid keys.

### `datasette.utils.__init__.CustomRow.__iter__` · *method*

## Summary:
Yields the row's values in the order specified by the object's columns sequence, producing one value per column without mutating the row.

## Description:
This method implements the Python iteration protocol for CustomRow so that iterating over an instance yields the cell values in column order. It is invoked whenever a CustomRow is the target of an iteration context (for ... in row), or when builtins/consumers convert or consume the row as an iterable (for example: list(row), tuple(row), or any code that iterates rows to serialize or format them).

Why this is a dedicated method:
- The iteration order must match the explicit column order stored in self.columns rather than the underlying mapping order; centralizing this behavior in __iter__ ensures consistent, ordered value iteration across the codebase.
- Implementing __iter__ rather than inlining the logic at call sites allows CustomRow to behave like sqlite3.Row (which supports index/key access and ordered iteration) and makes the object compatible with Python iterable consumers.

## Args:
None.

## Returns:
An iterator (generator) that yields the values stored for each column name in self.columns, in the same sequence as self.columns. Each yielded value has the same type as the value stored in the mapping (typing.Any). The iterator yields one value per entry in self.columns and completes when all columns have been yielded.

Edge-case return behavior:
- If the iterator is consumed normally, it yields each value in order then raises StopIteration when exhausted.
- If an exception occurs while fetching a value for a column (see Raises), iteration will stop at that point and propagate the exception.

## Raises:
KeyError — if any entry in self.columns is not a key in the underlying mapping (the OrderedDict portion of CustomRow). The call path is:
- __iter__ iterates over self.columns and calls self[column];
- CustomRow.__getitem__ (defined on the class) delegates to the underlying mapping via super().__getitem__(key);
- super().__getitem__ will raise KeyError if the requested key is absent.

Note: No other exceptions are explicitly raised by __iter__ itself; other exceptions may be raised indirectly by __getitem__ if that method is modified.

## State Changes:
Attributes READ:
- self.columns — iterated to determine order and keys
- self[...] via __getitem__ (reads values from the underlying mapping)

Attributes WRITTEN:
- None. __iter__ does not modify self or any of its attributes.

## Constraints:
Preconditions:
- self.columns must be an iterable (typically a list or tuple) of keys intended to be present in the row's mapping.
- Each element of self.columns should correspond to a mapping key (commonly a string column name). If elements are not valid keys, KeyError may be raised when the iterator attempts to look them up.

Postconditions:
- After completion, the iterator is exhausted and no attributes of the CustomRow instance have been changed.
- Consumers can rely on the iteration producing values in the exact order of self.columns.

## Side Effects:
- None: no I/O, no external calls, and no mutation of objects outside self are performed by this method.

## `datasette.utils.__init__.value_as_boolean` · *function*

## Summary:
Coerces a textual representation of a boolean into a Python bool, accepting a small set of case-insensitive tokens and raising a specific exception for unrecognized values.

## Description:
Converts an input that represents a boolean into True or False. The function accepts case-insensitive textual tokens representing truthy and falsey values and returns the corresponding Python bool.

Known callers within the codebase and typical calling contexts:
- Configuration and option parsing code that needs to interpret user-supplied boolean values (e.g., CLI flags, query parameters, or configuration file values).
- Web request/query-parameter processing and small utilities that need to normalize user-provided string values into booleans.
Note: Exact file-level call sites are not available in the provided context; the typical trigger is "a string value was supplied where a boolean is expected" during parsing/validation steps.

Why this logic is a separate function:
- Centralizes the canonical set of accepted boolean tokens and the conversion behavior so callers can uniformly interpret user input.
- Provides a single, catchable exception type (ValueAsBooleanError) for callers to handle parsing failures explicitly without conflating other ValueError conditions.

## Args:
    value (str): Input expected to be a string-like object. The function calls value.lower() directly, so the argument must implement lower() (commonly str).
    - Allowed literal (case-insensitive) values:
        - Truthy tokens: "on", "true", "1"
        - Falsey tokens: "off", "false", "0"
    - Notes:
        - The function does not strip whitespace. " true" or "true\n" will not be recognized unless the caller normalizes the string first.
        - Non-string types that implement lower() and return a string-like result are permitted, but passing types without lower() will raise AttributeError before value validation.

## Returns:
    bool: True if the (case-insensitive) token is one of ("on", "true", "1"); False if it is one of ("off", "false", "0").

Possible return scenarios:
- "on", "true", "1" (any casing) -> True
- "off", "false", "0" (any casing) -> False

## Raises:
    ValueAsBooleanError: Raised when the lowercased input is not one of the accepted tokens. Implementation detail: this function raises the ValueAsBooleanError exception class without providing positional arguments (i.e., the exception instance created by this raise will have an empty args tuple). Note that the ValueAsBooleanError class itself is a subclass of ValueError and is designed to accept an optional human-readable message (a common convention); callers who require a descriptive message should catch this exception and raise a new ValueAsBooleanError with an explanatory string if needed.
    AttributeError (implicit): If value does not have a lower() method (for example, None or an int without lower()), calling value.lower() will raise an AttributeError before ValueAsBooleanError can be raised. Callers who need to accept non-string inputs should pre-validate or coerce them.

## Constraints:
Preconditions:
- Caller should pass a string (or an object implementing lower()) representing the boolean. If the input may include leading/trailing whitespace or other formatting, the caller must normalize it (e.g., strip()) before calling.

Postconditions:
- If the function returns normally, the return is a Python bool that reflects the canonical interpretation of the accepted tokens.
- If the function raises ValueAsBooleanError, no boolean interpretation was possible with the accepted token set.

## Side Effects:
- None. The function performs no I/O and mutates no external state.

## Control Flow:
flowchart TD
    Start([Start]) --> Lower[value.lower()]
    Lower --> InAllowed{lowered in allowed_tokens?}
    InAllowed -- No --> Raise[Raise ValueAsBooleanError (no args)]
    InAllowed -- Yes --> IsTruthy{lowered in truthy_tokens?}
    IsTruthy -- Yes --> ReturnTrue([return True])
    IsTruthy -- No --> ReturnFalse([return False])

## Examples:
- Typical outcomes (prose):
    - Input "True" (any casing) -> returns True.
    - Input "off" -> returns False.
    - Input "maybe" -> the function raises ValueAsBooleanError; callers who want an explanatory message should catch this and raise a new ValueAsBooleanError("cannot interpret value 'maybe' as boolean") or otherwise handle the error.
- Example usage pattern (described):
    1. Normalize input if necessary, e.g., s = s.strip().
    2. Attempt conversion: call value_as_boolean(s).
    3. Handle parsing failure by catching ValueAsBooleanError and providing a user-friendly error or fallback value. If a descriptive error message is required, raise a new ValueAsBooleanError with the desired message inside the except block.

Notes for reimplementers:
- Preserve the exact accepted token set and the case-insensitive matching.
- Keep the behavior of raising ValueAsBooleanError on unrecognized tokens; whether to attach a message is a design choice—this implementation raises it without args to signal failure without a message.

## `datasette.utils.__init__.ValueAsBooleanError` · *class*

## Summary:
ValueAsBooleanError is a specialized ValueError used to indicate that a given value could not be interpreted as a boolean.

## Description:
This exception type exists to provide a clear, semantically meaningful error when a utility or parser fails to coerce or interpret an input value as a boolean. It is intended to be raised by functions that convert arbitrary input (strings, numbers, etc.) into booleans when the input does not match any accepted truthy/falsey representation.

Known callers/factories:
- Utility functions that parse boolean-like user input (e.g., parsing CLI options, query parameters, or configuration values). These functions should raise ValueAsBooleanError with a concise diagnostic message when conversion fails.

Motivation:
Using a distinct exception subclass makes it easy for callers to catch boolean-interpretation errors explicitly (except ValueAsBooleanError) while preserving the semantics and behavior of built-in ValueError for other error handling.

## State:
This class defines no new attributes beyond those provided by BaseException/ValueError. Important inherited state and invariants:

- args (tuple):
    - Type: tuple
    - Meaning: positional arguments passed at instantiation; by convention the first element is a human-readable error message (str).
    - Constraints: can contain any picklable objects; for consistent error messages callers should pass a single string as the first positional argument.

- __cause__, __context__, __traceback__:
    - Inherited from BaseException and behave the same (used for exception chaining and debugging).

Class invariants:
- Instances must be usable anywhere a ValueError instance is accepted.
- No additional mutable state is introduced by this subclass.

## Lifecycle:
Creation:
- Instantiate by calling ValueAsBooleanError(*args). Typical usage passes a single descriptive string: ValueAsBooleanError("cannot interpret value 'foo' as boolean").
- No required positional arguments; callers may omit args (resulting in an empty args tuple), but meaningful messages are recommended.

Usage:
- Typically created and immediately raised by a converter when encountering an unrecognized boolean value.
- Callers may catch this specific exception to implement fallback strategies or to return structured error responses.

Destruction / cleanup:
- No special cleanup is required. Instances follow normal Python exception lifecycle and are subject to usual reference-counting / garbage collection. They are picklable if their args are picklable.

Thread-safety:
- Immutable as long as callers do not mutate stored objects inside args. No internal mutable state -> safe to raise across threads in standard Python patterns.

Serialization:
- Instances are pickleable if the objects contained in args are pickleable (same as ValueError behavior).

## Method Map:
graph LR
  A[Instantiate ValueAsBooleanError(*args)] --> B[Raise ValueAsBooleanError]
  B --> C[Optional except ValueAsBooleanError: handle error]
  C --> D[Log / return error response / re-raise]

(Above is a simple invocation flow: creation, raising, optional catching and handling.)

## Raises:
- __init__ does not raise additional exceptions beyond what BaseException/ValueError might raise for pathological inputs (e.g., issues during pickling when args include non-pickleable objects are external concerns). Instantiating ValueAsBooleanError with arbitrary arguments will not itself raise.

## Example:
- Typical creation and raise scenario (described in prose):
  A boolean-parsing function inspects an input string and finds it does not match known true/false tokens. It should raise ValueAsBooleanError with a clear message such as "cannot interpret value 'maybe' as boolean". Callers can then catch except ValueAsBooleanError to provide a user-facing error or fallback behavior.

Notes:
- Reimplementers: to recreate this class, simply subclass ValueError with no additional methods or attributes. Preserve the default exception behavior provided by ValueError/BaseException so standard exception chaining, stringification (using args), and pickling semantics remain intact.

## `datasette.utils.__init__.WriteLimitExceeded` · *class*

## Summary:
A dedicated exception type that signals a write-limit/quota breach.

## Description:
WriteLimitExceeded is a lightweight sentinel exception class (a direct subclass of Exception) intended to be raised by components that detect an attempt to perform writes which would exceed an enforced limit or quota. The class itself contains no enforcement logic; it exists solely to allow code to raise and catch write-limit errors as a distinct type.

Note: This documentation describes the exception type only. This module defines the type; any code that raises or catches it lives elsewhere in the codebase and is not asserted here.

## State:
- Inheritance:
    - Subclasses built-in Exception.
- Instance attributes:
    - args (tuple): standard Exception positional arguments supplied at construction. No additional attributes are added by WriteLimitExceeded.
- Valid values / invariants:
    - There are no class-specific attributes to validate.
    - Any message passed by the raiser should be a human-readable description (e.g., "write limit exceeded: 10 MB") and will appear as the exception's string form.
    - Instances are immutable with respect to class-defined state (they behave like a normal Exception instance).

## Constructor / Parameters:
- Signature: follows Exception.__init__; typical construction forms are:
    - WriteLimitExceeded()                      -> no message
    - WriteLimitExceeded("reason")              -> single-string message
    - WriteLimitExceeded("fmt %s", value)      -> any positional args accepted by Exception
- Constraints:
    - No additional keyword or positional parameters are enforced by this subclass; any arguments are passed through to Exception.__init__.
    - The class constructor does not impose validation on message content or format.

## Lifecycle:
- Creation:
    - Instantiate directly where a write-quota check fails, passing an optional descriptive message.
    - No factories or helpers are required.
- Usage:
    - Typical pattern:
        1. A component detects a write limit breach.
        2. It raises WriteLimitExceeded(...) to abort the current operation.
        3. Callers may catch WriteLimitExceeded specifically to implement custom handling (logging, user-facing error, backoff, abort cleanup).
    - There is no required ordering of method calls on the exception object itself.
- Destruction:
    - No cleanup or finalization is required; exception instances are handled by Python's exception mechanism and garbage collection.

## Method Map:
graph TD
    Detector[Quota/Writer Detector] -->|on breach| Raise[raise WriteLimitExceeded]
    Raise -->|propagate| Handler[Higher-level handler]
    Handler -->|catch| Recover[Recover / report / abort]

(Flow: detection -> raise -> propagate -> catch/handle)

## Behavior / Interaction Notes:
- The class provides no additional API beyond Exception, so handlers should only rely on Exception-standard attributes and methods:
    - str(e) or e.args to obtain the message.
    - isinstance(e, WriteLimitExceeded) for type-checking.
- Since no additional attributes exist, code should not attempt to read non-existent fields from the exception instance.

## Raises:
- Constructing WriteLimitExceeded does not raise any class-specific exceptions; only exceptions that would normally arise from invalid Exception construction would occur (which is uncommon).
- The primary usage is that other code raises instances of this class to signal write-limit conditions.

## Example:
- Raising:
    - Instantiate with an explanatory message and raise to abort an operation when a write quota is exceeded.
- Catching:
    - Catch WriteLimitExceeded specifically to handle quota breaches separately from other errors. When caught, obtain the provided message via str(exception) or exception.args.

(Examples above are descriptive to avoid assuming repository-specific call sites; they show the intended usage patterns for raisers and handlers.)

## `datasette.utils.__init__.LimitedWriter` · *class*

## Summary:
A thin asyncio-compatible wrapper around an async writer that enforces an upper bound on the total number of bytes written.

## Description:
LimitedWriter is intended for use when streaming binary/text data through an existing async writer (an object exposing an awaitable write method) and you must ensure the total payload does not exceed a configured size (given in megabytes). Common usage is to wrap a response/stream writer that accepts bytes and raise a controlled WriteLimitExceeded error if the data would grow beyond the configured limit.

This class does not perform encoding/decoding — it simply counts bytes (len() of each write argument) and delegates the actual write operation to the wrapped writer. It is minimal by design: responsibility is enforcement of a cumulative byte-count limit; it does not manage lifecycle (open/close) of the underlying writer or serialization.

Known callers/factories:
- Any code preparing streamed CSV or similar large exports that must be capped (the surrounding codebase uses this to prevent very large CSV responses). The underlying writer must be an async-compatible writer (i.e., provide an awaitable write method).

Motivation:
Separates size-enforcement logic from the concrete writer implementation so the same enforcement can be applied to multiple writer types without duplicating counting/limit logic.

## State:
Attributes (public):
- writer: typing.Any
  - Description: The wrapped writer object to which bytes are forwarded.
  - Expected shape: exposes an async/awaitable write(bytes_like) method.
  - Invariant: must remain valid for the lifetime of the LimitedWriter instance; LimitedWriter does not close or replace it.

- limit_bytes: int
  - Description: Maximum allowed cumulative bytes before raising WriteLimitExceeded.
  - Computed from __init__ parameter limit_mb as limit_mb * 1024 * 1024.
  - Valid range/values:
    - If limit_mb is 0 -> limit_bytes == 0 and the class's check treats this as "no limit" (see behavior).
    - Non-negative integers and floats are expected. A negative value results in a negative limit_bytes and will cause the first positive write to be considered over the limit.
  - Invariant: numeric value (int or float convertible to int by multiplication) after instantiation.

- bytes_count: int
  - Description: Accumulated count of bytes that have been passed to write() so far.
  - Initial value: 0
  - Behavior: incremented by len(bytes) on every call to write() before limit check and delegation.
  - Invariant: monotonically non-decreasing (unless mutated externally).

Notes on parameter constraints (constructor):
- writer (required): must be an object with an async write method. If it lacks write or the write method is not awaitable, runtime exceptions will occur when write() is called.
- limit_mb (required): numeric (int/float). There is no default; callers must supply a value. Passing 0 disables the enforcement check (effectively unlimited). Passing negative values is allowed by the implementation but will behave like a negative byte limit (practically causing immediate exceed on first positive-length write); callers should avoid negative values.

Class invariants:
- bytes_count is always equal to the sum of len(arg) for every write() call completed or attempted (it is incremented before the underlying writer is awaited, therefore it reflects attempted writes even if the underlying writer later raises).
- limit_bytes remains constant after construction.

## Lifecycle:
Creation:
- Instantiate with two required arguments:
  - writer: an object exposing an async write(bytes_like) method.
  - limit_mb: numeric, megabytes threshold. Example: 5 to limit to 5 MiB.

Usage:
- Call sequence: create -> await write(data) -> await write(more_data) -> ...
- Each await write(...) call does:
  1) Increment bytes_count by len(bytes_arg).
  2) If limit_bytes is truthy (non-zero) and bytes_count > limit_bytes, raise WriteLimitExceeded immediately.
  3) Otherwise, await the underlying writer.write(bytes_arg).
- Important behavioral details:
  - The bytes_count is incremented before checking the limit and before delegating to the underlying writer. If the underlying writer.write raises, bytes_count will already have been incremented.
  - Passing a zero limit_mb disables enforcement because limit_bytes becomes 0 and the code checks 'if self.limit_bytes and ...' (0 is falsy).
  - Concurrent calls from multiple async tasks are not synchronized: simultaneous awaits to write() can produce race conditions in bytes_count (no internal locking). If the consumer may call write concurrently, protect the LimitedWriter with an external asyncio.Lock or other synchronization.

Destruction / cleanup:
- LimitedWriter does not provide a close() method or context-manager support. It does not close or clean up the wrapped writer — the caller is responsible for any teardown.

## Method Map:
flowchart LR
    A[__init__(writer, limit_mb)] --> B[bytes_count = 0]
    B --> C[write(bytes_arg)]
    C --> D[increment bytes_count by len(bytes_arg)]
    D --> E{limit_bytes truthy and bytes_count > limit_bytes?}
    E -- Yes --> F[raise WriteLimitExceeded("CSV contains more than {limit_bytes} bytes")]
    E -- No --> G[await writer.write(bytes_arg)]

## Raises:
- WriteLimitExceeded
  - Trigger: raised by write() when limit_bytes is non-zero (truthy) and after incrementing bytes_count the total exceeds limit_bytes.
  - Message: "CSV contains more than {limit_bytes} bytes" (the class formats the numeric byte limit into the message).
  - Note: WriteLimitExceeded is referenced by name in this class and must be defined/imported elsewhere in the codebase; if it is missing, a NameError will occur when the exception path executes.

- AttributeError / TypeError / RuntimeError
  - Trigger: If the wrapped writer does not expose a write attribute or its write method is not awaitable/correctly implemented, the awaited call may raise AttributeError, TypeError, or other runtime exceptions. These are not swallowed by LimitedWriter.

## Edge cases and constraints:
- Passing limit_mb == 0 disables enforcement (no WriteLimitExceeded will be raised).
- Passing negative limit_mb produces negative limit_bytes; any non-empty write (len(bytes_arg) > 0) will make bytes_count > limit_bytes and cause an immediate WriteLimitExceeded. Callers should provide non-negative limits.
- bytes parameter name shadows the built-in type name bytes; the code uses len(bytes) — the function expects a bytes-like object (bytes, bytearray, memoryview) or anything for which len() returns the number of bytes to be written and that the wrapped writer accepts.
- The bytes_count increment occurs before awaiting the underlying write; if the underlying write fails, bytes_count remains incremented.
- Not safe for concurrent use by multiple coroutines without external synchronization.

## Example:
- Create a LimitedWriter wrapping an async writer and limit to 5 MiB:
  1) Provide a writer object that exposes an async write(bytes_like) method.
  2) Instantiate: limited = LimitedWriter(writer, 5)
  3) Stream data by calling: await limited.write(b"first chunk")
  4) Continue calling await limited.write(...) for further chunks. If the cumulative written bytes exceed 5 * 1024 * 1024 the next write attempt will raise WriteLimitExceeded.
  5) Manage lifecycle of the underlying writer separately (close/cleanup as required).

## Implementation notes for re-implementation:
- Ensure write() is defined as an async function that:
  - Increments a persistent bytes_count by len(argument).
  - Checks the configured limit_bytes (computed from limit_mb * 1024 * 1024).
  - Raises a WriteLimitExceeded exception when appropriate.
  - Awaits and forwards the original bytes to writer.write.
- Consider adding optional synchronization (e.g., an asyncio.Lock) around write() if concurrent writes are expected in your environment.

### `datasette.utils.__init__.LimitedWriter.__init__` · *method*

## Summary:
Initializes a LimitedWriter instance by storing the underlying writer, converting the size limit from megabytes to bytes, and initializing the internal byte counter.

## Description:
This constructor sets up the minimal internal state required for a LimitedWriter wrapper object. It assigns the provided writer to an instance attribute, computes the size limit in bytes from the provided megabyte value, and initializes the bytes counter to zero.

Known callers and context:
- No callers are visible in the provided snippet. Typical usage is to instantiate this object when creating a wrapper around an existing writer-like object to track or enforce a byte-size limit during subsequent write operations.
- This logic is implemented in its own initializer because it performs the basic, single-responsibility task of establishing the object's immutable references and initial counters; keeping it separate ensures other methods (e.g., write/close) can assume these attributes exist.

## Args:
    writer (object):
        The underlying destination for written data. The constructor stores this object on the instance as-is; no interface checks are performed here.
    limit_mb (int | float):
        Numeric size limit in megabytes. The constructor converts this value to bytes (limit_mb * 1024 * 1024) and stores the result.

## Returns:
    None

## Raises:
    This __init__ implementation does not raise any exceptions explicitly. (If non-numeric limit_mb is passed, a TypeError may occur during the multiplication performed by the caller's Python runtime, but that is not raised explicitly here.)

## State Changes:
Attributes READ:
    - None (the initializer does not read any pre-existing instance attributes)

Attributes WRITTEN:
    - self.writer: set to the provided writer argument
    - self.limit_bytes: set to limit_mb * 1024 * 1024 (an integer/float number of bytes)
    - self.bytes_count: set to 0

## Constraints:
Preconditions:
    - None enforced by the method. Callers should provide a sensible writer object and a numeric limit_mb.

Postconditions:
    - After the call, the instance has self.writer, self.limit_bytes, and self.bytes_count attributes set as described above.
    - self.limit_bytes reflects limit_mb converted to bytes using 1024*1024 multiplication.

## Side Effects:
    - No I/O or external service calls are performed.
    - Only mutations are assignments to the instance attributes listed under Attributes WRITTEN.

### `datasette.utils.__init__.LimitedWriter.write` · *method*

## Summary:
Adds the given byte chunk to the running byte tally, enforces a configurable per-stream byte limit, and forwards the chunk to the underlying async writer (mutates the object's bytes_count).

## Description:
This async method is called by streaming/emit code that writes CSV (or other binary) chunks to an output transport. Typical callers are chunked CSV/streaming exporters that produce bytes in slices and call this method once per slice to (1) account for the bytes sent, (2) stop the stream if a hard byte quota is exceeded, and (3) forward the chunk to the underlying writer.

The logic is separated into its own method to centralize byte-counting and quota enforcement in a single place rather than duplicating that logic at every write site; it also encapsulates the interaction with the wrapped async writer.

## Args:
    bytes (bytes | bytearray | memoryview | any object with __len__):
        The next chunk of data to write. The method uses len(bytes) to update the byte counter and passes the object to the underlying writer.write method; therefore the object must support len() and be accepted by the wrapped writer's async write call.
        - No default value; required parameter.
        - Passing None or an object without __len__ will raise a TypeError at runtime when len() is evaluated.

## Returns:
    None
    - The method does not return a value; it awaits the wrapped writer.write call and discards that call's result.

## Raises:
    WriteLimitExceeded
        - Raised immediately after incrementing the internal byte counter when a truthy self.limit_bytes is set and the updated self.bytes_count exceeds self.limit_bytes.
        - The raised exception's message contains the numeric byte-limit value (e.g., "CSV contains more than 1048576 bytes").
    Other exceptions propagated from the wrapped writer.write(bytes)
        - Any exception raised by awaiting self.writer.write(bytes) is propagated to the caller (for example I/O or transport errors).

## State Changes:
    Attributes READ:
        - self.limit_bytes: checked (truthiness and numeric comparison) to decide whether to enforce a quota.
        - self.writer: accessed so its async write method can be invoked.
        - self.bytes_count: read as part of the read-modify-write update (implicitly read during the += operation).
    Attributes WRITTEN:
        - self.bytes_count: incremented by len(bytes) unconditionally at the start of the method.

## Constraints:
    Preconditions:
        - self.writer must implement an awaitable write(bytes) coroutine method that accepts the provided bytes-like object.
        - self.limit_bytes should be an integer (bytes) or a falsy value (0 or None) to indicate no limit. The code treats any truthy value as an active limit.
        - The caller must await this coroutine (it is async).
    Postconditions:
        - If the method returns normally (no exception raised by the limit check or writer.write), self.bytes_count has been increased by len(bytes) and the chunk has been forwarded to the underlying writer (writer.write has been awaited).
        - If WriteLimitExceeded is raised, self.bytes_count has already been incremented (it reflects the value that exceeded the limit). The underlying writer.write is not called in this case.
        - If the underlying writer.write raises, self.bytes_count remains incremented (the increment is not rolled back).

## Side Effects:
    - I/O: awaits and delegates to self.writer.write(bytes); this typically performs network or file I/O.
    - Mutates self.bytes_count (permanent increment even if subsequent write fails).
    - May raise WriteLimitExceeded to abort higher-level streaming logic.
    - May propagate exceptions coming from the wrapped writer, which callers must handle.

## `datasette.utils.__init__.EscapeHtmlWriter` · *class*

## Summary:
A minimal async wrapper that HTML-escapes content with markupsafe.escape() before delegating to an underlying writer's awaitable write method.

## Description:
EscapeHtmlWriter is used to add HTML-escaping behavior to an existing async writer without modifying that writer. It calls markupsafe.escape(content) for every write and then awaits the wrapped writer's write coroutine with the escaped string.

Typical scenarios:
- Wrapping an HTTP response or streaming writer where emitted text must be HTML-escaped.
- Composing middleware-like behavior around objects that expose an awaitable write(content) method.

Known callers/factories:
- None defined in this module; callers are any code that holds an async writer and wishes to ensure content is escaped.

Responsibility boundary:
- This class only performs escaping and delegation. It does not buffer, encode, or manage writer lifecycle (open/close). Any resource cleanup or additional behavior must be handled by the wrapped writer.

## State:
- writer
  - Type: any object with a write attribute that is awaitable/callable (i.e., calling writer.write(...) returns an awaitable that can be awaited).
  - Valid values: any object satisfying the above contract.
  - Invariant: After construction self.writer references the provided object and is used for all write delegations.

Constructor parameters:
- writer (required): the underlying writer to which escaped content will be forwarded. No validation is performed on construction.

Class invariants:
- self.writer is set by __init__ and assumed to provide an awaitable write method.
- Each call to write(...) will synchronously call markupsafe.escape and then await the underlying writer.write with the escaped content.

## Lifecycle:
Creation:
- Instantiate with EscapeHtmlWriter(writer). No defaults or factory helpers provided.

Usage:
- Use the asynchronous method await instance.write(content).
- There is no mandated sequence beyond constructing before writing. Multiple writes can be performed in any order; the wrapper does not provide synchronization beyond awaiting the underlying writer each call.

Destruction / Cleanup:
- No explicit cleanup methods (close(), __aenter__/__aexit__, or __del__) are provided. Manage the wrapped writer's lifecycle externally.

## Method Map:
flowchart LR
    A[Instantiate EscapeHtmlWriter(writer)] --> B[await write(content)]
    B --> C[call markupsafe.escape(content)]
    C --> D[await writer.write(escaped_content)]
    D --> E[underlying writer processes data / raises exceptions]

## Methods (detailed behavior to reimplement exactly):
- __init__(self, writer)
  - Purpose: store the provided writer for later delegation.
  - Inputs:
    - writer: required; any object with an awaitable write method.
  - Behavior:
    - Assigns the provided writer to self.writer.
    - Performs no validation or transformation.
  - Errors:
    - None explicitly raised by __init__ itself.

- async write(self, content)
  - Purpose: escape content for HTML safety and forward it to the wrapped writer.
  - Inputs:
    - content: passed directly to markupsafe.escape(content). Callers should provide values acceptable to markupsafe.escape (commonly str or objects implementing __html__ or __str__).
  - Behavior:
    1. Synchronously call markupsafe.escape(content).
    2. Await self.writer.write(escaped_content).
    3. Do not return the underlying writer.write's return value; the coroutine completes and implicitly returns None.
  - Return:
    - None (implicit). Any value returned by the underlying writer.write is awaited but discarded by this wrapper.
  - Side effects:
    - Delegates writing to the underlying writer with the escaped string.
  - Concurrency:
    - Each call awaits the underlying writer; the wrapper does not add extra concurrency control.
  - Edge cases:
    - If self.writer has no write attribute, AttributeError will occur when attempting to access it.
    - If self.writer.write exists but is not awaitable, awaiting it will raise a TypeError.
    - If markupsafe.escape raises for the provided content, that exception will propagate.
    - Any exception from the underlying writer.write will propagate to the caller.

## Raises:
- __init__: no explicit exceptions.
- write:
  - AttributeError if self.writer is missing write.
  - TypeError if self.writer.write is not awaitable.
  - Any exception propagated from markupsafe.escape(content).
  - Any exception propagated from awaiting self.writer.write(...).

## Example:
# Given an async writer object `async_writer` that provides an awaitable write() method:
writer = async_writer
esc = EscapeHtmlWriter(writer)

# Use the async write method; note the coroutine returns None (underlying writer's return value is discarded).
result = await esc.write('<b>Hello & welcome</b>')
assert result is None

# The underlying writer receives the escaped text (for example '&lt;b&gt;Hello &amp; welcome&lt;/b&gt;').

### `datasette.utils.__init__.EscapeHtmlWriter.__init__` · *method*

## Summary:
Stores the provided writer object on the instance so the EscapeHtmlWriter forwards subsequent write actions to it.

## Description:
This is the initializer invoked when an EscapeHtmlWriter instance is created. It sets up the underlying output target (the "writer") that this wrapper will use when writing escaped HTML. There are no additional initialization steps or validations: the passed object is stored directly.

Known callers and lifecycle:
- Called whenever a new EscapeHtmlWriter is instantiated (e.g., during construction of an output pipeline which wraps a raw writer with escaping behavior).
- Typical lifecycle stage: object construction / setup phase before any write/escape operations are performed.
- No specific call sites are listed in this file; the constructor is meant to be lightweight and used wherever an EscapeHtmlWriter instance is required.

Why this is a separate method:
- As the class constructor, it encapsulates object creation and makes the writer assignment explicit and discoverable. Keeping writer assignment in __init__ follows standard object initialization patterns and separates construction from later write/escape behavior.

## Args:
    writer (Any): The object that this EscapeHtmlWriter will forward output to. The method does not enforce a type; the object is stored as-is. The rest of the EscapeHtmlWriter implementation is responsible for calling appropriate methods on this writer (for example, a callable, a file-like object with a write(str) method, or a buffered output object), so the writer should support whatever interface those methods expect.

## Returns:
    None

## Raises:
    None — this __init__ performs no validation and will not raise any exceptions by itself. Any exceptions triggered by improper usage (for example, later method calls on self.writer failing because it lacks expected methods) will occur outside the constructor.

## State Changes:
    Attributes READ:
        - None (the initializer does not read any instance attributes)
    Attributes WRITTEN:
        - self.writer: set to the provided writer argument

## Constraints:
    Preconditions:
        - The method expects to be called on a valid EscapeHtmlWriter instance (normal Python constructor semantics).
        - No assumptions are made about the writer object's type or methods; callers should ensure the provided writer supports the necessary operations the EscapeHtmlWriter will invoke later.

    Postconditions:
        - After calling this method, self.writer exactly equals the writer argument provided.
        - No other attributes are modified or initialized by this method.

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - The only mutation is storing the reference to the writer on the instance (no mutation of the writer object itself).

### `datasette.utils.__init__.EscapeHtmlWriter.write` · *method*

## Summary:
Writes the given content to the underlying writer after converting it to a safe, HTML-escaped string; the object's writer is invoked asynchronously.

## Description:
This async method takes a content value, HTML-escapes it using markupsafe.escape, and then awaits the underlying writer's asynchronous write method with that escaped text.

Known callers and context:
- No direct callers are defined within this small class definition. This method is intended to be used wherever code in the application needs to stream or emit HTML content to an asynchronous writer while guaranteeing that the emitted text is escaped to avoid HTML injection/XSS. Typical call sites include streaming HTTP response generators, template streaming helpers, or any pipeline that writes chunks of HTML to an async text sink.
- Lifecycle stage: invoked during the output/streaming phase when content is being written to an external sink (response stream, file-like async writer, buffer, etc.)

Why this is a separate method:
- Centralizes the HTML-escaping + write logic so callers do not need to remember to escape content before every write. Encapsulating escaping in one small method reduces duplicated code and lowers the risk of forgetting to escape user-supplied content.

## Args:
    content (Any): Value to be written. The value will be converted/handled by markupsafe.escape which coerces non-string values to a textual representation and returns an HTML-escaped Markup object. Pass strings or objects that produce the intended string representation when escaped.

## Returns:
    Any: The awaited return value of self.writer.write(escaped_content). The exact type/value depends on the underlying writer implementation (commonly None). The method itself is asynchronous and must be awaited by callers.

## Raises:
    Any exception raised by markupsafe.escape: If markupsafe.escape raises an error for the provided content, that exception will propagate.
    Any exception raised by the underlying writer.write: Errors from the writer (I/O, runtime errors, type errors) propagate to the caller.

## State Changes:
    Attributes READ:
        self.writer — the underlying writer object is read to call its write method.
    Attributes WRITTEN:
        None — this method does not modify EscapeHtmlWriter attributes.

## Constraints:
    Preconditions:
        - self.writer must be an object that exposes an asynchronous write method (awaitable), typically defined as async def write(self, text) or an object whose write method returns an awaitable.
        - The caller must await this async write method (i.e., call await escape_html_writer.write(...)).
    Postconditions:
        - The underlying writer.write has been awaited with the HTML-escaped representation of content. The escaped string was produced by markupsafe.escape(content).

## Side Effects:
    - Calls and awaits self.writer.write(...) which likely performs I/O (sending bytes over a socket, writing to a file, buffering into a stream) or mutates external state managed by the writer.
    - No other external services or global state are modified by this method.

## `datasette.utils.__init__.remove_infinites` · *function*

## Summary:
Scan a row of values and replace any built-in float infinities with None; if no replacements are needed the original row object is returned unchanged.

## Description:
This utility inspects each element of the provided iterable "row" and converts any element that is a Python built-in float and is a member of the module-level _infinities container into None. If at least one replacement is required the function returns a newly-allocated list containing the substituted values; otherwise it returns the original row object without allocating a new sequence.

Known callers in provided context:
- No direct call sites were present in the provided file snapshot. In typical usage across a project, this function is called when preparing rows for JSON serialization or for presenting results where Python float infinities (±inf) must be represented as null/None to avoid serialization errors or invalid output.

Why extracted:
- Centralizes the policy for handling float infinities (conversion to None) so callers do not duplicate this logic.
- Allows consistent behavior across serialization/display code paths and makes behavior easier to test and modify.

## Args:
    row (Iterable): An iterable of values representing a row (commonly a list or tuple of column values).

Constraints on the argument:
- The function uses isinstance(item, float) to detect floats. Only Python built-in float instances will be considered for replacement; other numeric types (e.g., decimal.Decimal, numpy.float64) are ignored.
- The function iterates over row. If row is a one-shot iterator or generator, it will be consumed by the function. Passing an iterator may lead to surprising results (see Side Effects and Edge Cases).
- For correct behavior the module-level name _infinities must be defined and must support membership testing (the 'x in _infinities' operation). Commonly this is a set containing float('inf') and float('-inf').

## Returns:
    If no element in row is both a built-in float and a member of _infinities:
        - The same object passed as row is returned (object identity preserved).
    If one or more elements meet the replacement condition:
        - A new list is returned where each such float value has been replaced with None; all other elements are preserved in order.

Notes:
- The returned sequence type differs from input when replacements occur (input tuple -> returned list).
- Because the function may return the original object, callers that require a consistent concrete sequence type should explicitly convert the result (e.g., list(remove_infinites(row))).

## Raises:
    NameError: If the module-level name _infinities is not defined, evaluating membership (c in _infinities) will raise NameError.
    TypeError: If `row` is not iterable, iterating it will raise a TypeError. Additionally, if _infinities exists but does not support membership testing (for example, is None or a non-iterable), evaluating `c in _infinities` may raise a TypeError.

## Constraints:
Preconditions:
- _infinities must exist in the module scope and be a container supporting membership testing (typical expected contents: {float('inf'), float('-inf')}).
- Prefer passing re-iterable sequences (lists, tuples) rather than one-shot iterators or generators.

Postconditions:
- If the function returns a new list, no element in the returned list is both an instance of built-in float and a member of _infinities.
- If the function returns the original row, no such element existed in that row prior to the call (object identity preserved).

## Side Effects:
- Iteration: The function iterates over row to detect matches (using any) and — if replacements occur — iterates again to build the result list. If row is a one-shot iterator or generator, the first pass may consume it and the second pass will see an exhausted iterator, producing an empty list or otherwise surprising result. Therefore, passing generators is discouraged.
- No I/O, no global state mutation, and no external service calls are performed. The only allocation performed is a new list when replacements occur.

## Control Flow:
flowchart TD
    A[Start] --> B{Is row iterable?}
    B -->|No| C[Iteration raises TypeError -> propagate exception]
    B -->|Yes| D[Evaluate any((c in _infinities) if isinstance(c,float) else 0 for c in row)]
    D -->|NameError/TypeError during membership| E[Exception propagated]
    D -->|No matches (any is False)| F[Return original row object (identity preserved)]
    D -->|Any match (any is True)| G[Build new list: for each c in row -> None if isinstance(c,float) and c in _infinities else c]
    G --> H[Return new list]

## Edge cases and important behavior notes:
- NaN (float('nan')) is not considered an infinity and will not be replaced.
- Non-built-in float types (e.g., numpy.float64, Decimal) are not instances of built-in float and therefore will not be replaced; convert/normalize such values before calling if they must be handled.
- Membership uses equality semantics: the values in _infinities should be the actual float infinities (float('inf'), float('-inf')) to match correctly.
- Short-circuiting: the any() call stops at the first truthy match; therefore detection may stop early on large rows.
- Iterators/generators: because the function potentially iterates row twice, passing a one-time iterator can lead to it being consumed by the detection pass, producing an empty or partially consumed result list on the second pass. Use sequences (list/tuple) if you need safe, stable behavior.

## Examples:
Example — replace infinities in a list:
- Given _infinities == {float('inf'), float('-inf')}
- Input: [1.0, float('inf'), "x"]
- Output: [1.0, None, "x"]

Example — preserve tuple without infinities:
- Input: (1, 2, 3)
- Output: the exact same tuple object (no allocation)

Example — avoid passing a generator:
- Bad:
    gen = (x for x in [1.0, float('inf')])
    result = remove_infinites(gen)  # detection consumes generator; second pass yields []
- Good:
    row = [1.0, float('inf')]
    result = remove_infinites(row)  # returns [1.0, None]

## `datasette.utils.__init__.StaticMount` · *class*

## Summary:
A click.ParamType that parses strings of the form "mountpoint:directory" and validates the directory path, returning a (mountpoint, absolute_directory_path) tuple.

## Description:
Use this class when you need a Click command-line option/type that accepts a mapping from a URL/file-system mount point to a filesystem directory and verifies that the directory exists. Typical callers:
- Passed as the `type` argument to click.option or click.Argument (e.g., click.option("--static", type=StaticMount())).
- Code that directly validates a user-provided mount specification by calling the instance's convert method.

Motivation:
- Encapsulates parsing and validation rules for a mount specification in one reusable ParamType so Click will display consistent error messages and convert raw CLI strings into a canonical Python value (mount, absolute_dir).

## State:
- Class attribute:
    - name (str): "mount:directory" — human-readable type name shown by Click.
- Instances:
    - No instance attributes are created by this class (no __init__ defined). The object is stateless beyond the inherited ParamType behavior.
- Invariants:
    - Any successful return value is a 2-tuple (mountpoint, dirpath) where:
        - mountpoint is the substring before the first ':' in the original input (type: str).
        - dirpath is an absolute path (type: str) that exists on disk and is a directory (os.path.exists(dirpath) and os.path.isdir(dirpath) both True).

## Lifecycle:
- Creation:
    - Instantiate with no arguments: StaticMount().
    - Typical factory usage: pass an instance into Click's parameter decorator, for example click.option("--static", type=StaticMount()).
- Usage:
    - The key method is convert(value, param, ctx) which Click calls during parsing.
    - convert expects value to be a string in the form "mount:directory".
    - convert is safe to call multiple times; there is no internal state that changes across calls.
    - Typical sequence:
        1. create StaticMount()
        2. Click calls convert(value, param, ctx) for each CLI-supplied value
        3. If convert returns successfully, the caller receives a (mountpoint, absolute_dir) tuple
- Destruction:
    - No explicit cleanup required. The object holds no resources and does not implement context management.

## Method Map:
graph LR
    A[convert(value,param,ctx)] --> B{value contains ":"?}
    B -- no --> F[self.fail("...format mountpoint:directory")]
    B -- yes --> C[split at first ":" -> (mountpoint, dirpath)]
    C --> D[dirpath = os.path.abspath(dirpath)]
    D --> E{os.path.exists(dirpath) and os.path.isdir(dirpath)?}
    E -- no --> G[self.fail("<value> is not a valid directory path")]
    E -- yes --> H[return (mountpoint, dirpath)]

## Methods (behavior summary):
- convert(value, param, ctx)
    - Inputs:
        - value (str): Expected CLI value, format "mountpoint:directory".
        - param: The Click parameter metadata object passed through by Click (may be None if caller calls convert directly).
        - ctx: The Click context object passed through by Click (may be None if caller calls convert directly).
    - Behavior:
        - If the input does not contain a ":" character, calls self.fail with a message indicating the expected format.
        - Splits value on the first ":" into (mountpoint, dirpath).
        - Normalizes dirpath to an absolute path using os.path.abspath.
        - Validates that the resolved dirpath exists and is a directory via os.path.exists and os.path.isdir.
        - If validation fails, calls self.fail with a message stating the input is not a valid directory path.
        - On success, returns the tuple (mountpoint, dirpath) where dirpath is absolute.
    - Return:
        - tuple[str, str]: (mountpoint, absolute_directory_path)
    - Edge cases & behavior notes:
        - Only the first ":" is used to split; additional ":" characters in either side are preserved in the respective returned values.
        - Symlinks that point to directories will pass os.path.isdir and thus are treated as valid directories.
        - If `value` is not a string (e.g., None or another type), the membership test ":" not in value will raise a TypeError. Callers (e.g., Click) normally supply strings.
        - Calls to self.fail are used to signal invalid input; Click will surface these as parameter parsing errors.

## Raises:
- The method signals invalid inputs by calling self.fail(message, param, ctx). This indicates to Click that parameter parsing should fail. In typical Click usage, this leads to a Click parameter error being raised/handled by Click (e.g., click.BadParameter). The conditions that trigger self.fail here are:
    - value does not contain ":" -> failure message: '"<value>" should be of format mountpoint:directory'
    - dirpath (after abspath) does not exist or is not a directory -> failure message: '<original_value> is not a valid directory path'
- Note: If a non-string is passed as value, a TypeError may be raised by the membership test before the explicit self.fail calls.

## Example:
- Typical use as a Click option:
    - From a CLI command definition:
        - @click.command()
        - @click.option("--static", type=StaticMount(), multiple=True, help="mountpoint:directory")
        - def cli(static):
        -     # `static` is now a tuple of (mountpoint, absolute_dir) tuples
        -     for mountpoint, directory in static:
        -         print(mountpoint, directory)
- Direct call for validation (unit tests or callers outside Click):
    - static_type = StaticMount()
    - result = static_type.convert("assets:/var/www/assets", None, None)
    - # result -> ("assets", "/var/www/assets") where the directory path is absolute

### `datasette.utils.__init__.StaticMount.convert` · *method*

## Summary:
Validate and parse a CLI value of the form mountpoint:directory, returning a (mountpoint, absolute_directory_path) tuple; aborts command parsing with a click parameter error if validation fails.

## Description:
This is the click.ParamType.convert implementation for StaticMount and is invoked by click during CLI argument/option parsing when a parameter uses StaticMount() as its type (for example a --static or --static-mount option). It runs during the command-line parsing stage, before the command's main callback executes.

Having this logic as a dedicated convert method:
- Satisfies click's ParamType API contract (click calls convert to validate/convert raw values).
- Centralizes parsing and filesystem validation for any CLI parameters that accept mountpoint:directory pairs, avoiding duplicated checks and error formatting across commands.

## Args:
    value (str): Raw CLI input string. Expected format is "mountpoint:directory". The method does not strip or otherwise normalize whitespace beyond what click supplies.
    param (click.Parameter): The click Parameter object representing the option/argument — forwarded to self.fail for error reporting.
    ctx (click.Context): The click Context for the invocation — forwarded to self.fail for error reporting.

## Returns:
    tuple[str, str]: (mountpoint, dirpath_abs)
        - mountpoint: the substring before the first ":" in the input (may be the empty string if the input begins with ":").
        - dirpath_abs: the directory substring after the first ":", converted with os.path.abspath to an absolute path.
    Special notes:
        - If the input contains multiple ":" characters, only the first ":" is used to split the value (value.split(":", 1)).
        - dirpath_abs is not expanded for user home (~) or environment variables; tilde/vars will remain unexpanded and are subject to os.path.exists/os.path.isdir checks as-is.
        - If the directory part is empty (e.g., input is "mount:" or ":"), os.path.abspath('') resolves to the current working directory and that path will be validated.

## Raises:
    This method signals invalid input by calling self.fail(...), which integrates with click's error handling and prevents command execution. Conditions and exact messages used:
        - Missing colon (no ":" in value):
            Calls self.fail with message: '"{value}" should be of format mountpoint:directory'
        - Directory part does not exist or is not a directory:
            Calls self.fail with message: '{value} is not a valid directory path'
    Note: self.fail is provided by click.ParamType (StaticMount subclasses click.ParamType); invoking it causes click to report a bad parameter and abort parsing (commonly raising click.BadParameter internally).

## State Changes:
    Attributes READ:
        - self.fail (method): invoked to raise parameter errors; no other self attributes are accessed.
    Attributes WRITTEN:
        - None. The method does not modify self or any other object attributes.

## Constraints:
    Preconditions:
        - value should be a string (click supplies a string for CLI parameters).
        - param and ctx should be the click Parameter and Context objects provided by click; they are only forwarded to self.fail.
    Postconditions:
        - On success, returns a 2-tuple (mountpoint, dirpath_abs).
        - dirpath_abs is an absolute path that existed and was a directory at the time of the check.

## Side Effects:
    - Performs filesystem checks: os.path.exists(dirpath_abs) and os.path.isdir(dirpath_abs) (stat-like system calls).
    - Calls self.fail(...) on invalid input, which triggers click's parameter error handling and prevents further command execution.
    - No file system mutations, network I/O, or modifications to objects outside the click error control flow.

## `datasette.utils.__init__.LoadExtension` · *class*

## Summary:
A small click.ParamType that parses CLI values in the form "path:entrypoint" into a (path, entrypoint) tuple, or returns the original value when no colon is present.

## Description:
LoadExtension is a lightweight parser intended for use as a Click CLI parameter type. It exists to let a command-line option accept either:
- a single path-like string (no colon), which is passed through unchanged, or
- a colon-separated "path:entrypoint" string, which is converted into a two-tuple (path, entrypoint).

Typical scenarios:
- Use as the `type` argument for a Click option that accepts extension specifiers where an optional entrypoint follows the path separated by a colon.
- Called by Click's option parsing pipeline; callers typically do not call convert() directly except in tests or bespoke parsing logic.

Motivation / responsibility boundary:
- Responsibility is strictly parsing: it does not validate that the path exists, that the entrypoint is syntactically valid, or that the pair maps to a real extension. Those concerns remain with the caller.
- It provides minimal, deterministic behavior so command handlers receive either a raw string or a (path, entrypoint) tuple.

## State:
- name (class attribute)
  - Type: str
  - Value: "path:entrypoint?"
  - Purpose: Click uses this for help/messages to indicate the expected form of the parameter.
  - Invariant: constant, does not change per-instance.

There are no instance attributes declared in LoadExtension. It relies on the base class click.ParamType for any internal state.

## Lifecycle:
- Creation:
  - Instantiate with no arguments: LoadExtension()
  - No factory methods are required; simple construction is sufficient.

- Usage:
  - Typical pattern:
    1. Instantiate: loader = LoadExtension()
    2. Provide as Click option type: @click.option("--ext", type=loader)
    3. Click will call loader.convert(value, param, ctx) during parsing.
  - convert() returns either:
    - the original value (unchanged) when the input has no ":" character, or
    - a tuple (path, entrypoint) when the input contains a colon (split at the first colon).
  - No ordering of multiple method calls is required beyond the normal Click lifecycle: convert() may be invoked multiple times by Click for different parsing stages; each call is independent and stateless.

- Destruction / Cleanup:
  - No cleanup required. The class does not open resources or require finalization.

## Method Map:
flowchart LR
    A[Instantiate: LoadExtension()] --> B[Used as Click type]
    B --> C[Click invokes convert(value, param, ctx)]
    C --> D{value contains ":"?}
    D -- yes --> E[return (path, entrypoint) from first split]
    D -- no --> F[return value unchanged]

## API (behavior of public members)
- convert(value, param, ctx)
  - Purpose: Parse a CLI-provided value potentially containing a colon into a (path, entrypoint) pair.
  - Inputs:
    - value: object (typically a str) — the raw value provided by Click from the CLI.
    - param: Click parameter object passed by Click (unused by this implementation; should be accepted).
    - ctx: Click context object passed by Click (unused by this implementation; should be accepted).
  - Returns:
    - If value contains no ":" (the colon character), the method returns value unchanged (exact same object).
    - If value contains ":", it returns a 2-tuple (path, entrypoint) where path is the substring before the first colon and entrypoint is everything after that first colon.
  - Notes / constraints:
    - Splitting is done once (split(":", 1)). Subsequent colons belong to the entrypoint component.
    - The method does not strip surrounding whitespace; "a:b" and " a : b " will be split literally.
    - The method does not validate that path or entrypoint are non-empty; an input of ":entry" yields ("", "entry"), and "path:" yields ("path", "").
    - No conversion to other types (e.g., no Path object) is performed.
  - Edge cases:
    - If value is None or a type that does not support membership ("in") or split(), Python may raise a TypeError or AttributeError. The method does not catch or translate these errors into click.BadParameter.
    - If value is already a non-string sequence (e.g., a tuple) and contains ":" as an element, behavior follows Python membership semantics (":" in value) and may return the sequence unchanged or attempt splitting if membership test passes and the object exposes split(). This class is designed for CLI strings; such non-string inputs are uncommon in normal Click workflows.

## Raises:
- The class itself does not explicitly raise click.BadParameter or other Click-specific exceptions.
- Runtime exceptions possible depending on value's type:
  - TypeError if value is None or a type that does not support the membership test or split operation in the current context.
  - AttributeError if value does not have a split() method but the membership test passes.
- There are no exceptions raised by normal string inputs.

## Example:
1) Direct usage (imperative calls):
- Instantiate:
  loader = LoadExtension()

- Parsing a value without an entrypoint:
  result = loader.convert("some/path/to/ext", None, None)
  # result == "some/path/to/ext"

- Parsing a value with an entrypoint:
  result = loader.convert("some/path/to/ext:main", None, None)
  # result == ("some/path/to/ext", "main")

- Parsing a value with multiple colons:
  result = loader.convert("pkg:sub:callable", None, None)
  # result == ("pkg", "sub:callable")  # split only at the first colon

2) Typical Click integration:
- In a Click-based command:
  @click.command()
  @click.option("--load-extension", type=LoadExtension(), help="Path or path:entrypoint")
  def cli(load_extension):
      # load_extension will be either a str or a (path, entrypoint) tuple
      print(load_extension)

### `datasette.utils.__init__.LoadExtension.convert` · *method*

## Summary:
Parses a CLI argument that may contain a colon-separated path and entrypoint, returning either the original string or a (path, entrypoint) pair.

## Description:
This method implements click.ParamType.convert for the LoadExtension parameter type. It is invoked by the Click command-line argument parsing machinery during option/argument conversion when a parameter is declared to use this ParamType. Typical lifecycle stage: called while Click is converting raw string arguments into Python values just after the command-line is parsed and before command callback execution.

This logic is separated into its own method because Click requires a ParamType subclass to provide a convert method. Keeping the parsing behavior here localizes the "path:entrypoint" parsing rule and avoids duplicating the split logic at call sites.

Known callers:
- The Click library (click.core.ParamType.convert) when Click parses and converts a parameter whose type is an instance of LoadExtension.

## Args:
    value (str): The raw argument value supplied on the command line. Expected to be a string. Examples: "my-extension", "package/module:entrypoint", "path/to/file:handler".
    param (click.Parameter|None): The Click Parameter object describing the option/argument being converted. Provided by Click; not used by this implementation.
    ctx (click.Context|None): The Click Context for the command invocation. Provided by Click; not used by this implementation.

## Returns:
    str | tuple[str, str]:
    - If the input value does not contain the character ":" then the original value is returned unchanged (string).
    - If the input contains ":" the method splits on the first colon only and returns a 2-tuple (path, entrypoint), both elements are strings.
    - Examples:
        * Input "extension" -> "extension"
        * Input "pkg.module:hook" -> ("pkg.module", "hook")
        * Input "file:sub:entry" -> ("file", "sub:entry")
        * Input "file:" -> ("file", "")  (entrypoint becomes an empty string)

## Raises:
    - The method does not explicitly raise any custom exceptions.
    - If a non-string value is passed (so that the containment test ":" not in value or split is invalid), Python will raise a TypeError. Click normally supplies strings, so this is a precondition rather than expected behavior.

## State Changes:
Attributes READ:
    - None (the method does not access self or any instance/class attributes).

Attributes WRITTEN:
    - None (the method does not modify self or other state).

## Constraints:
Preconditions:
    - value should be a string (as supplied by Click during CLI parsing).
    - The method expects param and ctx to be Click-provided objects, but they are unused and may be None in theory.

Postconditions:
    - The return value is guaranteed to be either the original string (if no colon present) or a 2-tuple of strings representing (path, entrypoint) with the entrypoint containing any remaining text after the first colon (including additional colons).

## Side Effects:
    - None. The method performs pure computation and has no I/O, network calls, or mutations of external objects.

## `datasette.utils.__init__.format_bytes` · *function*

## Summary:
Convert a numeric byte count into a concise, human-readable string using the most appropriate unit among bytes, KB, MB, GB, and TB; use integer formatting for raw bytes and one decimal place for larger units.

## Description:
Known callers:
- No direct callers were discovered in the supplied context. Typical callers include code that needs to display file sizes, HTTP Content-Length, database size summaries, or CLI/HTML output that reports byte counts.

Purpose and rationale:
- Centralizes unit-selection and formatting rules for byte quantities so presentation code across the project can show consistent, human-friendly sizes. Keeping this logic in one function prevents duplication and makes it easy to change formatting (decimal precision, unit list) in a single place.

## Args:
    bytes (int | float | str | decimal.Decimal | other numeric-like): A value representing a quantity of bytes.
        - The function begins by calling float(bytes). Therefore the argument must be convertible to a Python float.
        - Accepts integers and floats directly; accepts numeric strings (e.g., "1024") and decimal.Decimal (converted via float()).
        - Passing a bytes object (binary data) is a misuse and will raise a TypeError when float() is called.
        - None or other non-numeric objects will raise TypeError.
        - Negative numbers are allowed as input, but note their treatment below.

    Notes:
        - The parameter name shadows the built-in bytes type; callers should pass a numeric value, not a bytes object.

## Returns:
    str: A human-readable string consisting of a numeric value, a space, and a unit suffix.
        - If the chosen unit is "bytes": the numeric portion is formatted as an integer (no decimal places). Examples: 0 -> "0 bytes", 1023 -> "1023 bytes".
        - For KB, MB, GB, TB: the numeric portion is formatted with one decimal place. Examples: 1536 -> "1.5 KB", 1048576 -> "1.0 MB".
        - Units considered (in order): "bytes", "KB", "MB", "GB", "TB". The function does not produce suffixes larger than "TB".
        - For very large inputs (exceeding 1024**5), the numeric portion may be >= 1024 while the suffix remains "TB" (e.g., 1024**6 -> "1024.0 TB").

        Special float values:
        - float('inf') and float('-inf') will propagate through the loop and be returned with the "TB" suffix, formatted by Python's float formatting (e.g., "inf TB" or "-inf TB").
        - float('nan') will be returned as "nan TB".

## Raises:
    TypeError: When float(bytes) is not valid for the provided type (e.g., passing a bytes object, None, or other non-convertible object).
    ValueError: When float(bytes) receives a string that cannot be parsed as a number (e.g., "abc").
    Notes:
        - These exceptions originate from Python's float() conversion; the function does not explicitly raise them.

## Constraints:
Preconditions:
    - Input must be convertible to float(); otherwise a TypeError or ValueError will occur.
    - Intended for numeric byte counts. Do not pass binary data (a bytes object) or other non-numeric inputs.

Behavioral note about negatives:
    - The comparison used is current < 1024 (not based on absolute value). Therefore any negative input is less than 1024 and the loop breaks immediately, resulting in the "bytes" suffix. Negative inputs are returned as integer bytes (e.g., -1536 -> "-1536 bytes"), not as scaled KB/MB units.

Postconditions:
    - Returns a non-empty string with a numeric portion and one of the suffixes: bytes, KB, MB, GB, TB.
    - If suffix is "bytes", numeric portion is an integer; otherwise numeric portion has one decimal place.

## Side Effects:
    - None. Pure computation and string formatting; no I/O or external state changes.

## Control Flow:
flowchart TD
    Start(["Start"]) --> ToFloat["current = float(bytes)"]
    ToFloat --> ForLoop["for unit in (bytes, KB, MB, GB, TB)"]
    ForLoop --> Check["if current < 1024?"]
    Check -- Yes --> Break["break (use current & unit)"]
    Check -- No --> Divide["current = current / 1024"] --> NextIter["next unit or end"]
    NextIter --> ForLoop
    Break --> IsBytes["unit == 'bytes'?"]
    IsBytes -- True --> ReturnInt["return f\"{int(current)} {unit}\""]
    IsBytes -- False --> ReturnFloat["return f\"{current:.1f} {unit}\""]
    ReturnInt --> End(["End"])
    ReturnFloat --> End

## Examples:
- Typical usage:
    from datasette.utils import format_bytes
    format_bytes(0)           # -> "0 bytes"
    format_bytes(1023)        # -> "1023 bytes"
    format_bytes(1024)        # -> "1.0 KB"
    format_bytes(1536)        # -> "1.5 KB"
    format_bytes(1048576)     # -> "1.0 MB"
    format_bytes(5 * 1024**4) # -> "5.0 TB"

- Large-value behavior (TB is the largest suffix):
    format_bytes(1024**5)     # -> "1.0 TB"
    format_bytes(1024**6)     # -> "1024.0 TB"  (numeric portion may be >= 1024 when input exceeds PB)

- Special float values:
    format_bytes(float('inf'))   # -> "inf TB"
    format_bytes(float('-inf'))  # -> "-inf TB"
    format_bytes(float('nan'))   # -> "nan TB"

- Error handling:
    try:
        format_bytes("not-a-number")
    except ValueError:
        # float() failed to parse the string
        handle_invalid_input()

    try:
        format_bytes(b'\x00\x01')  # a bytes object is invalid
    except TypeError:
        handle_invalid_input()

- Negative values:
    format_bytes(-1536)  # -> "-1536 bytes"  (negative inputs are reported in "bytes" due to the current < 1024 test)

## `datasette.utils.__init__.escape_fts` · *function*

## Summary:
Normalize a user-provided FTS search string by balancing unmatched double quotes, splitting into parts using a module-level regex, removing empty parts, and ensuring each remaining part is wrapped in double quotes so it is safe and predictable to use in an SQLite FTS MATCH expression.

## Description:
This function transforms free-form search input into a quoted-token form expected by SQLite FTS MATCH. It performs three sequential steps:
1. If the total number of double-quote characters (") in the input string is odd, append a closing double-quote to balance them.
2. Split the (possibly adjusted) string using the module-level regular expression object _escape_fts_re (the function calls _escape_fts_re.split(query)).
3. From the split parts, remove falsy parts and the exact two-character string '""'. For each remaining part, if it does not start with a double-quote character, wrap it in double quotes. Join the processed parts with single spaces and return the result.

Known callers:
- No direct call sites were present in the supplied fragment. In common usage this function is invoked when converting user-entered search text into the RHS of an FTS MATCH clause (for example, when preparing SQL that implements search over an FTS-enabled table).

Why this is a separate function:
- Balancing quotes, tokenizing while preserving quoted phrases, filtering empty tokens, and wrapping tokens in quotes are discrete, reusable responsibilities that must be applied consistently. Centralizing them avoids duplicated logic and subtle bugs in multiple places that construct FTS queries.

Dependency:
- A module-level compiled regular expression named _escape_fts_re must be present. The function uses _escape_fts_re.split(query) to obtain parts. The exact tokenization behavior therefore depends on how _escape_fts_re is defined in the module. If that regex is not available, implementers should provide an equivalent that captures quoted phrases and contiguous non-whitespace sequences. A commonly used approach is to use re.findall(r'(".*?"|\S+)', query) with non-greedy quoted matching; this yields quoted phrases and unquoted tokens as atomic units.

## Args:
    query (str): Input search text.
        - Must be a str. The function invokes string methods and passes the value to a regex split that is expected to operate on str.
        - The function does no encoding/decoding; callers must ensure text is a Unicode str.

## Returns:
    str: The normalized FTS query:
        - If the input is empty or yields no retained parts after filtering, returns the empty string.
        - Every returned token is either a preserved token that started with a double-quote in the split result, or a previously unquoted token wrapped in double-quotes by the function.
        - Tokens are joined by single spaces.
    Deterministic examples (these do not depend on the exact _escape_fts_re beyond it treating quoted phrases as atomic):
        - Input: 'apple banana' -> Output: '"apple" "banana"'
        - Input: 'apple "banana split"' -> Output: '"apple" "banana split"'
        - Input: '' -> Output: ''

## Raises:
    - TypeError: Likely raised if a non-str value incompatible with the module regex is passed (for example, if _escape_fts_re is compiled for str and query is bytes, re.split will raise TypeError). Also may occur if code attempts string concatenation with incompatible types.
    - AttributeError: May be raised if query is None or another object lacking required string methods (e.g., if query does not support .count or returned split parts do not support .startswith).
    Notes:
        - The function does not perform explicit type checking; errors result from attempted string operations or regex usage on an inappropriate type.
        - If _escape_fts_re is misconfigured or compiled with an invalid pattern, regex compilation errors occur at the point of regex definition, not inside this function.

## Constraints:
Preconditions:
    - query must be a Python str.
    - The module must provide a valid compiled regex _escape_fts_re designed to operate on str and to yield tokens that represent quoted phrases and contiguous non-whitespace tokens.

Postconditions:
    - The returned string is a str in which the number of double-quote characters is even (quotes are balanced).
    - No global state is modified.

## Side Effects:
    - None. The function performs no I/O, network calls, logging, or mutation of external/global state.

## Control Flow:
flowchart TD
    Start --> CountQuotes
    CountQuotes{query.count('"') % 2 == 1?}
    CountQuotes -- Yes --> AppendQuote["query += '\"'"]
    CountQuotes -- No --> SkipAppend
    AppendQuote --> Split
    SkipAppend --> Split
    Split["bits = _escape_fts_re.split(query)"]
    Split --> Filter["bits = [b for b in bits if b and b != '\"\"']"]
    Filter --> Wrap["For each b: if b.startswith('\"') keep as-is else b = '\"' + b + '\"'"]
    Wrap --> Join["Return ' '.join(mapped bits)"]
    Join --> End

## Implementation guidance:
- Balance quotes first: counting and appending a trailing quote is intentionally performed before tokenization to ensure quoted phrases are properly delimited.
- Tokenization: if _escape_fts_re is not available, prefer re.findall(r'(".*?"|\S+)', query) (non-greedy quoted group) to obtain tokens directly. Using re.split with a capturing pattern can also work but requires careful filtering of empty strings and separators.
- Filtering: the implementation intentionally drops empty tokens and the exact string '""' (an empty quoted phrase). Preserve this behavior unless you have a reason to keep empty quoted phrases.
- Wrapping: only parts that do not already begin with a double-quote are wrapped. Do not attempt to re-parse or remove punctuation inside tokens; this function's scope is balancing, tokenizing, filtering, and quoting.

## Examples:
1) Simple tokens
    Input: 'cat dog'
    Output: '"cat" "dog"'

2) Quoted phrase preserved
    Input: 'cat "black dog"'
    Output: '"cat" "black dog"'

3) Unbalanced quotes corrected before tokenization
    Input: 'name:"open source'
    Processing: a trailing '"' is appended to balance quotes -> 'name:"open source"'
    With a regex that treats quoted phrases as atomic, the quoted phrase is preserved as one token and returned quoted.

## `datasette.utils.__init__.MultiParams` · *class*

## Summary:
A lightweight container representing HTTP/URL-style multi-valued parameters: maps each key to a list of values while exposing convenient single-value accessors and list accessors.

## Description:
MultiParams is used when request/query parameters may have multiple values for the same key (for example, URL query strings like ?tag=python&tag=sqlite). It provides:
- get(name, default=None): return the first value for a key (convenient for single-valued parameters).
- getlist(name): return the full list of values for a key.
- dict-like behaviours: membership testing, indexing to obtain the first value, iteration over keys, len() for number of distinct keys.

Typical instantiation scenarios:
- When parsing a framework-specific query-params structure that already groups values by key, you can pass a dictionary mapping keys to lists/tuples of values.
- When parsing a sequence of (key, value) pairs (for example from parsing raw query strings or form-encoded pairs), you can pass a list or tuple of 2-tuples/2-lists to construct grouped lists of values.

Motivation and responsibility:
- Keeps code that consumes parameters simple by normalizing two common input shapes (dict-of-lists and list-of-pairs) into one internal representation.
- Provides a clear API for retrieving either the first value (common case) or all values (multi-valued case) without requiring callers to handle the normalization themselves.
- It is intentionally small and focused — it does not provide mutating APIs (no add/remove) or encoding/decoding utilities.

## State:
Attributes
- _data (dict[str, list|tuple]): Internal mapping of parameter name -> sequence of values.
  - Keys: typically strings (parameter names).
  - Values: lists (constructed from list-of-pairs input) or the original lists/tuples provided when a dict was used.
  - Invariant: each value in _data is expected to be a sequence (list or tuple). Consumers of MultiParams may assume that _data[name][i] is valid for any valid index i when name exists.
Constructor parameter
- data (dict | list | tuple):
  - If dict: must map keys -> list or tuple of values. Default: none (parameter required).
  - If list or tuple: must be an iterable of pair sequences (each item must itself be a list/tuple of length 2).
  - Constraint: invalid shapes will trigger AssertionError (see Raises). Passing a value that is neither a dict nor a list/tuple will leave the instance without _data and lead to AttributeError on first use; callers must pass one of the accepted shapes.
Class invariants
- After successful initialization, _data exists and is a dict whose values are sequences.
- The order of values for a key preserves the order of appearance from the input:
  - When constructed from a dict, the existing order of each value-sequence is preserved.
  - When constructed from a list-of-pairs, values are appended in the order pairs appear.
- The mapping preserves key insertion order as per standard Python dict semantics (i.e., insertion order in Python 3.7+).

## Lifecycle:
Creation
- Required argument: data (dict mapping keys -> list/tuple of values) OR data as a list/tuple of (key, value) pairs.
- Example valid inputs:
  - {'a': [1, 2], 'b': ['x']}
  - [('a', 1), ('b', 'x'), ('a', 2)]
Usage (typical sequence)
1. Instantiate: mp = MultiParams(data)
2. Query:
   - membership: 'a' in mp
   - first value: value = mp['a']  (raises KeyError if 'a' not present)
   - first value with fallback: value = mp.get('a', default)
   - full list: values = mp.getlist('a')  (returns [] if 'a' not present)
   - iterate: for key in mp: ...
   - keys view: mp.keys()
3. No explicit destruction or cleanup is required. The class holds only in-memory structures and does not implement context manager or close semantics.
Destruction
- Standard Python object lifetime applies; there are no external resources to free.

## Method Map:
Graph of public method/property interactions and typical invocation flow:

mermaid
graph LR
    A[__init__(data)] --> B[_data dict initialized]
    B --> C[__contains__(key)]
    B --> D[__getitem__(key)]
    B --> E[get(name, default)]
    B --> F[getlist(name)]
    B --> G[keys()]
    B --> H[__iter__()]
    B --> I[__len__()]

Notes:
- get() internally performs _data.get(name)[0], guarded by exception handling for missing or non-sequence values.
- __getitem__ directly indexes _data[key][0] and will raise KeyError for missing key.

## Methods and Behavioural Details (for reimplementation):
- __init__(self, data)
  - Accepts either:
    - dict: for each key in data, assert that data[key] is a list or tuple. Then set self._data = data.
    - list or tuple: each item must be a list/tuple of length 2, interpreted as (key, value). Build a dict mapping keys to lists of values in order of appearance and assign to self._data.
  - Edge conditions:
    - If a dict value is not a list/tuple -> AssertionError("dictionary data should be a dictionary of key => [list]")
    - If an item in the list input is not a length-2 list/tuple -> AssertionError("list data should be a list of [key, value] pairs")
    - If data is not a dict, list, or tuple: the constructor does not set _data; subsequent method calls will raise AttributeError. Implementations should either replicate this behavior or prefer to raise TypeError explicitly.
- __repr__(self)
  - Returns a readable representation that includes the internal mapping, e.g. "<MultiParams: {...}>".
- __contains__(self, key)
  - Return True if key in self._data, False otherwise.
- __getitem__(self, key)
  - Return the first value for key: self._data[key][0].
  - Behavior: KeyError if key not present; IndexError if value sequence is empty.
- keys(self)
  - Return an iterable/view of keys (the underlying dict's keys() view).
- __iter__(self)
  - Yield keys in the same order as the internal mapping.
- __len__(self)
  - Return the number of distinct keys (len(self._data)).
- get(self, name, default=None)
  - Return the first value for name if present.
  - Implementation detail: attempt to return self._data.get(name)[0] and catch KeyError and TypeError (TypeError occurs if _data.get(name) is None) to return default.
  - Note: if the stored sequence exists but is empty, indexing [0] will raise IndexError; current implementation does not catch IndexError and it will propagate. Consider handling empty lists if reproducing behavior is undesirable.
- getlist(self, name)
  - Return the entire sequence (list or tuple) associated with name, or an empty list if not present or if the stored value is falsy.
  - Implementation detail: returns self._data.get(name) or [].

Performance characteristics:
- All operations are O(1) average for dict lookups.
- Construction from list-of-pairs is O(n) where n is number of pairs.

## Raises:
- AssertionError:
  - If constructed with a dict where any value is not a list or tuple: assertion message "dictionary data should be a dictionary of key => [list]".
  - If constructed with a list/tuple where any item is not a 2-length list/tuple: assertion message "list data should be a list of [key, value] pairs".
- KeyError:
  - __getitem__ raises KeyError when the key is absent.
- IndexError:
  - __getitem__ may raise IndexError if the stored sequence exists but is empty (i.e., _data[key] == []).
- TypeError / AttributeError:
  - get() handles missing key by catching TypeError when attempting to index None, and returns the default.
  - If __init__ is given an unsupported type for data (neither dict nor list/tuple) the instance will not set _data, causing AttributeError on first use. A reimplementation may choose to raise TypeError in the constructor instead — this class does not.

## Example:
- Constructing from a dict-of-lists:
  mp = MultiParams({'tag': ['python','sqlite'], 'q': ['search']})
  'tag' in mp            # True
  mp['tag']              # 'python'         (first value)
  mp.get('tag')          # 'python'
  mp.getlist('tag')      # ['python','sqlite']
  mp.get('missing', 'x') # 'x'
  len(mp)                # 2
  for k in mp:           # yields 'tag', 'q' (in insertion order)
    ...

- Constructing from list-of-pairs:
  pairs = [('tag','python'), ('q','search'), ('tag','sqlite')]
  mp2 = MultiParams(pairs)
  mp2.getlist('tag')     # ['python', 'sqlite']

Implementation note for reimplementers:
- Preserve the error messages used in the original assertions if you need exact behavior.
- Decide whether to keep the original behavior of leaving _data unset when passed an invalid top-level type (not dict/list/tuple), or to be stricter and raise TypeError for clarity. The original class expects callers to pass correctly-shaped input.

### `datasette.utils.__init__.MultiParams.__init__` · *method*

## Summary:
Initializes the object's internal multi-value parameter map from either a dictionary of key => list/tuple or an iterable of [key, value] pairs, storing the normalized mapping on the instance.

## Description:
This initializer accepts two common representations of multi-valued parameters and normalizes them into a dict that maps each key to a list of values, assigned to self._data.

Known callers and context:
- No explicit callers are provided in the supplied source. Typical callers are factory functions or code that parse HTTP query strings, form-encoded bodies, or other sources that allow multiple values per parameter and want to normalize them into a consistent in-memory representation for downstream processing.
- It is invoked at object construction time (the object's lifecycle initialization stage) to validate and normalize incoming parameter data before other instance methods operate on it.

Why this logic is a separate method:
- Normalization and validation of the incoming data are a distinct responsibility required at object creation. Keeping it in __init__ centralizes type checks and conversion logic so other methods can depend on a predictable structure (a dict mapping keys to lists). It prevents duplication of parsing logic across the class and ensures the instance invariant is established once.

## Args:
    data (dict[list|tuple] | list[tuple|list] | tuple[tuple|list]):
        - If dict: must be a mapping where each value is a list or tuple (e.g., {"k": ["v1","v2"]}).
        - If list or tuple: must be an iterable of 2-item sequences (key, value) pairs (e.g., [["k", "v1"], ["k", "v2"]]).
        - Keys used when converting from a list must be hashable (to be used as dict keys).
        - Values may be any Python object; their types are not restricted by this method.

## Returns:
    None
    - The method does not return a value; its effect is to set instance state (self._data).

## Raises:
    AssertionError:
        - Raised if `data` is a dict and any dict value is not a list or tuple.
          Exact condition: for any key in data, not isinstance(data[key], (list, tuple)).
        - Raised if `data` is a list or tuple and any item is not a 2-length list/tuple.
          Exact condition: for any item in data, not (isinstance(item, (list, tuple)) and len(item) == 2).
    Note: If `data` is neither a dict nor a list/tuple, this initializer does not raise and will not set self._data (see Constraints).

## State Changes:
Attributes READ :
    - None (the method only reads the incoming argument `data`; it does not read any existing instance attributes)

Attributes WRITTEN :
    - self._data : set to a dict mapping each key to a list of values.
        - If input is a dict, the same dict reference is assigned after validation.
        - If input is a list/tuple of pairs, a new dict is created where values are lists of the appended items.

## Constraints:
Preconditions:
    - Caller should pass either:
        * a dict whose every value is a list or tuple, or
        * a list/tuple of 2-item sequences (key, value).
    - When passing the list-of-pairs form, all items must be indexable sequences of length 2.
    - Keys derived from list-of-pairs must be hashable.

Postconditions:
    - If `data` was a valid dict or list/tuple per the preconditions, self._data will be set to a dict mapping each key to a list of its values.
        * For dict input: exact same dict object is assigned to self._data (no copy), assuming it passed validation.
        * For list/tuple input: self._data is a newly constructed dict where values are lists (in insertion order for each key).
    - If `data` was neither dict nor list/tuple, self._data is not set by this method (caller must not rely on its existence).

## Side Effects:
    - No I/O or external service calls.
    - Mutations:
        * For dict input: the original dict object passed in is assigned to self._data (no internal mutation performed by this method), so subsequent external mutations to that dict will be visible via self._data.
        * For list/tuple input: a new dict and new lists are created; no references to the original container objects (beyond individual value objects) are retained except the stored values themselves.

### `datasette.utils.__init__.MultiParams.__repr__` · *method*

## Summary:
Return a concise, human-readable string showing the current internal mapping of parameter keys to their lists of values without modifying the object.

## Description:
This method provides the object's developer-facing representation and is invoked whenever Python requests the object's representation: via the built-in repr() function, when an interactive REPL prints the object, when logging or debugging frameworks include the object, or when formatting with {!r} / {!s} in f-strings. It is implemented as a dedicated __repr__ method to centralize and standardize how the internal _data mapping is displayed across all such callers.

Known callers / contexts:
- repr(my_multi_params)
- f"{my_multi_params!r}" or f"{my_multi_params}" in formatted strings (logging, debugging, interactive shells)
- Logging or debug output that includes the object
- Display in interactive shells and debuggers

Why separate:
- Centralizes presentation logic for debugging/inspection.
- Keeps display formatting out of other methods, avoiding duplication.

## Args:
    None

## Returns:
    str: The exact return value is produced by this f-string expression: "<MultiParams: {self._data}>". The braces are filled with the mapping's standard string representation (equivalent to str(self._data)). Example return value:
    "<MultiParams: {'a': ['1', '2'], 'b': ['3']}>"

    Notes:
    - The ordering of keys in the printed mapping follows the iteration order of the underlying dictionary (insertion order for Python 3.7+).
    - The return value is always a Python str.

## Raises:
    AttributeError: If the instance has no attribute self._data (indicating improper construction), accessing it will raise AttributeError.
    Any exception raised while producing the string representation of self._data (for example if computing the mapping's string representation triggers an exception via contained objects' __str__/__repr__); such exceptions propagate out of this method.

## State Changes:
    Attributes READ:
        - self._data

    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The instance must have been initialized such that self._data exists and is a mapping (the class __init__ sets self._data to a dict mapping keys to lists/tuples).
    Postconditions:
        - The object is not mutated by this call.
        - The returned string accurately reflects the current contents of self._data at the time of the call.

## Side Effects:
    - This method performs no I/O, network calls, or mutations of external objects.
    - Indirect side effects are possible because producing the string representation of self._data will call into the string/representation logic of keys and values; if those implementations perform side effects, those will occur when this method is called.

### `datasette.utils.__init__.MultiParams.__contains__` · *method*

## Summary:
Returns True if the given key is present in the instance's underlying container; does not modify the object's state.

## Description:
Implements the Python membership protocol for the object by delegating the membership test to the instance attribute that holds the data container.

Invocation context:
- This method is called whenever Python's membership operator is used with the object (for example: "key in multi_params").
- It can also be invoked directly by callers performing an explicit membership check.

Why this is a separate method:
- Providing __contains__ allows the object to participate in Python's "in" operator and centralizes membership semantics in one place, delegating to the underlying container.

## Args:
    key (object): The key to test for membership. Any value acceptable to the underlying container's membership test is permitted.

## Returns:
    bool: True if the underlying container (self._data) reports the key is present, False otherwise.

## Raises:
    AttributeError: If the instance does not have the attribute self._data (e.g., the object was not properly initialized).
    Any exception raised by the underlying container's membership operation is propagated unchanged. (Example: TypeError may be raised by some containers if the key is of an unsupported type.)

## State Changes:
    Attributes READ:
      - self._data
    Attributes WRITTEN:
      - None

## Constraints:
    Preconditions:
      - self._data must exist and support Python membership testing (i.e., the "in" operator).
    Postconditions:
      - The object's state is unchanged.
      - The return value equals the result of evaluating "key in self._data" at call time.

## Side Effects:
    - None: no I/O, external calls, or mutations of objects outside self are performed by this method.

### `datasette.utils.__init__.MultiParams.__getitem__` · *method*

## Summary:
Return the first stored item associated with key from the internal mapping so MultiParams supports dict-style subscription without mutating state.

## Description:
This method implements Python's mapping subscription (obj[key]) for MultiParams by returning the element at index 0 of the sequence stored under key in self._data.

Context and role:
- It provides the standard subscription semantics used by any code that indexes a MultiParams instance (i.e., relies on obj[key] access).
- It complements the other mapping-like methods implemented on MultiParams (__contains__, keys, __iter__, __len__, get, getlist) to present a compact, dict-like interface.
- The class constructor (__init__) enforces that, for normal construction paths, values in self._data are lists or tuples; therefore this method normally returns the first element of such a sequence.

Why this is a separate method:
- Subscription access must be provided as a special method to satisfy Python's mapping protocol and to centralize the "first-value" semantics for all index-based lookups.

## Args:
    key (hashable): The key to look up in the internal mapping. Typically a string when used for parameter names. No default.

## Returns:
    Any: The object stored at self._data[key][0].
    - Under normal construction (see __init__), values are lists or tuples, so the returned value is the first element of that list/tuple.
    - The returned value is the exact stored object (not a copy). Mutating a mutable returned value will affect the stored value.

Example:
    If self._data == {"q": ["search", "other"]}, then obj["q"] returns "search".

## Raises:
    KeyError: If key is not present in self._data (raised by self._data[key]).
    IndexError: If self._data[key] exists but is an empty sequence (no element at index 0).
    TypeError: Only possible if the internal invariant is violated (for example, if self._data[key] is not subscriptable due to external mutation), causing self._data[key][0] to be invalid.

Note: For lookup behavior that avoids exceptions, use get(name, default) or getlist(name) provided by MultiParams.

## State Changes:
    Attributes READ:
        self._data

    Attributes WRITTEN:
        none

## Constraints:
    Preconditions:
        - For normal (constructor-created) instances, self._data is a mapping whose values are sequences (list or tuple). The __init__ method asserts this invariant when a dict is passed and constructs list-valued entries when passed a list/tuple of pairs.
        - key must be valid for the mapping (hashable).

    Postconditions:
        - The method does not modify self or self._data.
        - If it returns normally, the first element at self._data[key][0] remains the same immediately after the call.

## Side Effects:
    - None: no I/O, no external service calls. The method only reads from self._data and returns a reference to an element it contains.

### `datasette.utils.__init__.MultiParams.keys` · *method*

## Summary:
Return a live view of the parameter names stored in this instance's internal mapping.

## Description:
Returns the keys view produced by calling keys() on the instance's underlying mapping (self._data). The method exists to expose a mapping-like keys() API so MultiParams can be used where a dict-like keys view is expected.

Known callers and context:
- No other methods inside MultiParams invoke this method.
- The repository-wide callers are not inspected here; this method is a public accessor intended for external callers that need to iterate or inspect parameter names.

Why this is a separate method:
- It provides the standard mapping API (keys()) for MultiParams without copying the keys into a new container. Returning the underlying view is efficient and preserves expected behavior for code that expects a dict-like keys view.

## Args:
None

## Returns:
dict_keys
    - The dict-keys view object returned by self._data.keys().
    - This view is live: it reflects subsequent mutations to self._data.
    - The elements yielded are the keys present in self._data (typically strings), and if there are no keys an empty view is returned.

## Raises:
AttributeError
    - If called on an instance where self._data does not exist (for example, if __init__ was not executed), an AttributeError will occur when accessing self._data.

## State Changes:
Attributes READ:
    - self._data

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - The MultiParams instance must have been initialized so that self._data exists and is a dict-like object (as set by MultiParams.__init__).

Postconditions:
    - No mutation is performed on self; the returned view reflects the current contents of self._data.

## Side Effects:
    - None. The method performs no I/O, network access, or mutations of external objects.

### `datasette.utils.__init__.MultiParams.__iter__` · *method*

## Summary:
Return an iterator that yields the parameter names present in the wrapped data, without modifying the object's state.

## Description:
This method implements the iteration protocol for MultiParams so instances can be used in iteration contexts (for loops, list(), tuple(), or any API that consumes an iterable). It is invoked whenever Python needs an iterator for a MultiParams object — for example:
- for name in multi_params: ...
- list(multi_params) or tuple(multi_params)
- passing the object to APIs that iterate over its items or keys

Typical lifecycle/context: called at the point where callers need to enumerate available parameter names (e.g., when rendering forms, serializing parameter sets, or routing/validation code that inspects which parameter names are present). This logic is a dedicated method to provide the standard iterable interface for the object and to delegate iteration directly to the underlying storage (self._data.keys()), keeping iteration behavior consistent with the underlying mapping.

It is implemented separately (rather than inlining calls to keys()) so that Python's iteration protocol is supported directly and consumers can treat MultiParams as a standard iterable mapping of keys.

## Args:
    None

## Returns:
    iterator: A generator/iterator that yields each key from the underlying self._data.keys() view in the same order produced by the underlying mapping.
    - If the underlying mapping is empty, the iterator yields no values and immediately completes.
    - Key element types: whatever type the keys were provided as when the MultiParams instance was created (commonly str).

## Raises:
    AttributeError: If self._data does not exist or does not have a keys() attribute (this would occur if the object was incorrectly constructed or mutated).
    TypeError: If self._data.keys() returns a non-iterable object (very unusual; implies malformed underlying storage).
    RuntimeError: If the underlying mapping is mutated during iteration in a way that Python's dict iteration forbids, the iteration may raise RuntimeError: "dictionary changed size during iteration" — this is produced by the underlying mapping implementation, not by this method.

## State Changes:
Attributes READ:
    - self._data

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - self._data must be present and implement keys() that returns an iterable view of keys (the class __init__ sets self._data to a dict in normal construction).
    - The keys produced by self._data.keys() should be of the expected type for consumers (commonly strings).

Postconditions:
    - The MultiParams instance is unchanged by iterating.
    - The returned iterator will produce each key from the underlying mapping once, in the same order as the underlying mapping's keys() view.

## Side Effects:
    - None (no I/O or external service calls).
    - Iteration relies on the underlying mapping; if that mapping is mutated concurrently, Python may raise a runtime error. The method itself performs no mutation.

### `datasette.utils.__init__.MultiParams.__len__` · *method*

## Summary:
Return the number of distinct parameter keys stored by this MultiParams instance (i.e., the number of entries in the internal mapping).

## Description:
This method implements the Python container protocol's length operation for MultiParams by delegating to the length of the internal storage (self._data). It is intended to allow callers to use the built-in len() function (for example, len(multi_params)) and to behave like a standard mapping-like container for membership and size checks.

Known callers and invocation contexts:
- The method is invoked whenever built-in len() is called on a MultiParams instance (len(instance)).
- It may be used implicitly by consumers that treat MultiParams as a mapping-like container (e.g., boolean checks like "if multi_params:" or functions that query container size).
- No specific direct call-sites within the provided class source were required; this implements a standard protocol method rather than bespoke business logic.

Why this is a separate method:
- Providing __len__ allows MultiParams to participate in Python's container protocol and be used with len(), size checks, and generic container-handling utilities without inlining logic at call sites.
- Keeping the length logic here centralizes the definition of "size" for MultiParams (the count of distinct keys) and avoids duplicating access to the internal representation elsewhere.

## Args:
This method takes no explicit arguments beyond self.

## Returns:
int: The number of keys stored in self._data.
- Typical value: a non-negative integer (0 when no keys are present).
- Edge cases: returns 0 if self._data is an empty mapping.

## Raises:
This method does not explicitly raise exceptions itself.
- Implicit exceptions: If self._data is missing or not a sized object, calling len(self._data) will raise a TypeError or AttributeError. In the class constructor, self._data is always set to a mapping (dict), so under normal construction this does not occur.

## State Changes:
Attributes READ:
- self._data

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- self must be a properly constructed MultiParams instance whose __init__ has set self._data to a mapping-like object (the class constructor ensures this by assigning a dict).
- self._data must support the built-in len() operation (must be a sized collection).

Postconditions:
- No mutation of self or external state occurs.
- The return value equals the number of top-level keys in the internal mapping representation (not the total number of values across all keys).

## Side Effects:
- None. The method performs no I/O, network calls, or mutations outside of reading self._data.

### `datasette.utils.__init__.MultiParams.get` · *method*

## Summary:
Return the first element from the value-list stored under the given key in the MultiParams mapping, or the provided default when no usable first element exists.

## Description:
This method is the single-item accessor for MultiParams which stores each key mapped to a sequence of values (list/tuple). It is typically used when callers expect only the first value for a multi-valued parameter (for example: the first query parameter value when parsing HTTP request parameters), and want a convenient fallback when the key is absent.

Known callers:
- No explicit callsites were discovered in the provided component snapshot. Typical usage patterns include code that needs the canonical or primary value from a parameter that may be provided multiple times (e.g., query string parameters, form fields, or repeated headers).

Why this is a separate method:
- Encapsulates the "first-value-or-default" pattern so callers do not need to inspect or slice the underlying list themselves.
- Keeps a small, well-documented API surface (get vs getlist) for single-value vs multi-value access.

## Args:
    name (str or hashable): The key to look up in the MultiParams mapping. Expected to be a hashable (commonly a str).
    default (Any, optional): Value returned when no first element can be retrieved. Defaults to None.

## Returns:
    Any: The first item from the sequence stored at self._data[name] when present and subscriptable.
    If the key is missing or the stored value is None, returns the provided default.

    Edge cases:
    - If the key exists and maps to a non-empty sequence, the first element of that sequence is returned.
    - If the key does not exist (or maps to None), the method returns the default.
    - If the key exists but maps to an empty sequence, the method will raise IndexError (see Raises).

## Raises:
    IndexError: If the mapping contains the key but the associated sequence is empty (e.g., []), attempting to access index 0 will raise IndexError; this exception is not caught by the implementation.
    TypeError and KeyError are handled internally by the method and cause it to return the default instead of propagating.

## State Changes:
    Attributes READ:
        self._data
    Attributes WRITTEN:
        None (this method does not modify the object's state)

## Constraints:
    Preconditions:
        - self._data should be a dictionary-like object mapping keys to sequences (list or tuple). The MultiParams constructor enforces this for normal construction paths.
        - name must be a valid key type for the mapping (hashable).
    Postconditions:
        - The object's state is unchanged.
        - The return value is either the first element of the stored sequence for the key, or the supplied default when the key is absent or the stored value is None.

## Side Effects:
    - No I/O or external calls.
    - No mutations to objects outside of self.

### `datasette.utils.__init__.MultiParams.getlist` · *method*

## Summary:
Return the complete sequence of values stored for a given parameter key, without modifying the object.

## Description:
This method looks up the provided key in the MultiParams internal storage and returns the full list/tuple of values associated with that key. It is intended for use when a caller needs all values for a multi-valued parameter (for example, query-string parameters that may appear multiple times). The logic is small and self-contained so callers can explicitly request the full value sequence rather than the single-first-value accessor (get). Keeping this as its own method keeps the API explicit and avoids duplicating the fallback-to-empty-list behavior elsewhere.

Known callers:
- No specific callers were discovered in the supplied source context. Typical usage is in code that consumes MultiParams to read all values for a given parameter name.

Why this is a method:
- Provides a clear, documented API to retrieve all values for a parameter.
- Encapsulates the fallback-to-empty-list behavior in one place so other code does not need to check for missing keys or convert None to [].

## Args:
    name (hashable, typically str):
        The key to look up in the MultiParams storage. Must be a key that was present in the original data used to construct the MultiParams instance. There is no default value.

## Returns:
    list|tuple:
        The stored sequence of values for the given key if present (the same list/tuple object that was stored during initialization).
        If the key is not present, returns an empty list ([]).
        Notes:
            - The method returns the actual stored object (no copy). Mutating the returned list (if it is a list) will mutate self._data.
            - If the stored value was a tuple, a tuple will be returned; if the stored value was a list, a list will be returned.
            - The fallback is always an empty list instance.

## Raises:
    This method does not raise exceptions under normal operation.
    (The class constructor enforces that stored values are lists or tuples, so getlist itself does not need to validate types.)

## State Changes:
    Attributes READ:
        self._data

    Attributes WRITTEN:
        None — this method does not modify any attribute.

## Constraints:
    Preconditions:
        - The MultiParams instance must have been initialized correctly so that self._data is a dict mapping keys to lists or tuples. The constructor enforces this.
        - The provided name should be a key type compatible with the dictionary (typically a string).

    Postconditions:
        - The method returns either a sequence (list or tuple) that reflects the current stored value for the key, or an empty list when the key is absent.
        - The method guarantees it will not alter self._data.

## Side Effects:
    - No I/O or external service calls.
    - Returns a direct reference to an internal container: if the returned object is a list and the caller mutates it, that mutation will be reflected inside the MultiParams instance.

## `datasette.utils.__init__.ConnectionProblem` · *class*

*No documentation generated.*

## `datasette.utils.__init__.SpatialiteConnectionProblem` · *class*

## Summary:
A marker subclass of ConnectionProblem used to represent connection problems that are specific to SpatiaLite. It does not add behavior or state; it exists so callers can distinguish SpatiaLite-related connection failures from other kinds of connection problems.

## Description:
SpatialiteConnectionProblem is a thin specialization of ConnectionProblem (it directly inherits and contains only the pass statement). Its purpose is purely semantic: to allow code to raise or catch a typed exception that identifies the problem as related to SpatiaLite (the spatial extension for SQLite) rather than a generic connection issue.

When to instantiate:
- When detection logic determines a connection failure is specifically caused by SpatiaLite-related issues (for example: missing SpatiaLite extension, incompatible SpatiaLite binary, or SpatiaLite-specific initialization error).
- Typical usage is to raise this exception at the point where SpatiaLite-specific setup/connection fails so callers can handle it separately from other ConnectionProblem instances.

Known callers/factories:
- The class body provides no callers or factories in this module. Look for places elsewhere in the repository where SpatiaLite connection or initialization is performed; those sites may raise this class to signal SpatiaLite-specific failures.

Relationship to ConnectionProblem:
- All operational behavior (attributes, message formatting, representation, and any helper methods) is inherited from ConnectionProblem.
- This class intentionally adds no new attributes, methods, or side effects.

## State:
- New attributes: none. SpatialiteConnectionProblem does not define additional instance attributes.
- Inherited state: any attributes established by ConnectionProblem are present — their names, types, and semantics are exactly those of the superclass.
- __init__ parameters: SpatialiteConnectionProblem does not define its own __init__; it inherits ConnectionProblem.__init__. Callers must supply the same arguments expected by ConnectionProblem.__init__ (see ConnectionProblem documentation for exact parameter names, types, and defaults).
- Class invariants:
  - No invariants are introduced by this subclass beyond those maintained by ConnectionProblem.
  - Any invariant enforced by ConnectionProblem remains applicable.

## Lifecycle:
- Creation:
  - Instantiate by calling SpatialiteConnectionProblem(...) with the same signature as ConnectionProblem.
  - There are no factory methods or additional convenience constructors defined in this subclass.
- Usage:
  - Typical operations are the same as for ConnectionProblem: raise to signal an error, catch to handle, and inspect inherited attributes for details about the failure.
  - Example usage patterns:
    - Raise when a SpatiaLite initialization fails.
    - Catch SpatialiteConnectionProblem specifically to provide SpatiaLite-specific recovery steps (such as disabling spatial features or surfacing a clearer error message).
- Destruction / cleanup:
  - The subclass has no special cleanup responsibilities. Any resource management is the responsibility of calling code or handled by ConnectionProblem if it implements any (e.g., storing context information). This class itself does not implement context manager protocols or close() methods.

## Method Map:
- This subclass defines no methods of its own. The method-call graph is therefore:
  SpatialiteConnectionProblem --> (inherited methods and attributes from) ConnectionProblem

Mermaid diagram (method/flow overview):
graph TD
    A[Caller code] --> B[raise SpatialiteConnectionProblem(...)]
    B --> C[ConnectionProblem.__init__ (inherited)]
    A --> D[except SpatialiteConnectionProblem as e]
    D --> E[handle SpatiaLite-specific recovery]

## Raises:
- The subclass itself does not introduce any new exceptions.
- Instantiation of SpatialiteConnectionProblem will raise whatever exceptions ConnectionProblem.__init__ raises for invalid arguments; consult ConnectionProblem documentation for specific exceptions and conditions.
- Raising this class in application code signals an error condition related to SpatiaLite; code that catches it should expect that it behaves like ConnectionProblem.

## Example:
- Raising a SpatiaLite-specific connection problem:
    raise SpatialiteConnectionProblem("SpatiaLite extension not available on this system")
- Catching only SpatiaLite problems while allowing other connection problems to propagate:
    try:
        connect_using_spatialite()
    except SpatialiteConnectionProblem as e:
        # handle SpatiaLite-specific fallback (e.g., disable spatial features)
        ...
    except ConnectionProblem:
        # handle other connection problems (non-SpatiaLite)
        ...

- Note: Replace the string arguments above with the parameters required by ConnectionProblem.__init__ as documented in the ConnectionProblem component documentation.

## `datasette.utils.__init__.check_connection` · *function*

## Summary:
Validate a SQLite connection by enumerating each table and running PRAGMA table_info on it; raises a typed exception if a SpatiaLite-related module is missing or a generic connection problem is detected.

## Description:
This helper inspects the database schema to verify that basic metadata queries succeed across all tables. It performs two read-only operations: (1) selects table names from sqlite_master where type='table', and (2) for each table runs PRAGMA table_info(<escaped-table-name>) to ensure the connection and any required SQLite extensions respond correctly.

Known callers within the codebase:
- No direct callers were found in the available memory snapshot. Typical call sites (not discovered here) are startup or connection-validation routines that need to detect and report connection issues early (for example: Datasette server startup, connection health checks, or extension initialization code).

Why this is extracted into a separate function:
- Encapsulates schema-checking and SpatiaLite-detection logic in one place so callers can reuse the same detection behavior and handle SpatiaLite-specific failures differently from generic connection errors. This keeps higher-level connection or startup code cleaner and centralizes the mapping from sqlite3.OperationalError messages to the module's typed exceptions.

## Args:
    conn (sqlite3.Connection-like): A live database connection object with an execute(sql: str) -> Cursor method and Cursor.fetchall() -> list behavior.
        - The function calls conn.execute("select name from sqlite_master where type='table'") and expects a cursor with fetchall() to return an iterable of rows where each row's first column is the table name (string).
        - For each table name it calls conn.execute(f"PRAGMA table_info({escape_sqlite(table)});").
        - The object must therefore accept SQL text and return results; duck-typed connection objects meeting that contract are supported.

## Returns:
    None
    - On successful completion (no exceptions raised), the function returns None and guarantees that:
        * The initial schema query succeeded.
        * For every table discovered, the PRAGMA table_info query executed without raising an sqlite3.OperationalError.
    - There are no other explicit return values.

## Raises:
    SpatialiteConnectionProblem
        - Raised when a PRAGMA table_info call raises sqlite3.OperationalError and the underlying error message (e.args[0]) exactly equals "no such module: VirtualSpatialIndex".
        - This identifies a SpatiaLite-specific failure (commonly due to a missing SpatiaLite extension).

    ConnectionProblem
        - Raised when a PRAGMA table_info call raises sqlite3.OperationalError for any other message text.
        - The original sqlite3.OperationalError instance is wrapped as the single argument when constructing the ConnectionProblem.

    Any exception raised by the initial select query or by methods other than the PRAGMA call will propagate unchanged.
        - For example, if conn.execute("select name ...") raises sqlite3.OperationalError, sqlite3.DatabaseError, TypeError, or other errors, they are not caught by check_connection and will propagate to the caller.

## Constraints:
Preconditions:
    - conn must be a valid, open connection to a SQLite database file or in-memory database.
    - The module-level helper escape_sqlite must be defined and callable (it is used to wrap table names safely).
    - Table names returned by sqlite_master should be strings; otherwise, downstream calls may fail.

Postconditions:
    - No mutation of the database schema or data is performed by this function — it only issues read-only SQL statements.
    - If the function returns normally, all tables in sqlite_master were accessible with PRAGMA table_info using the connection provided.
    - If an OperationalError produced by PRAGMA indicates a SpatiaLite issue, the function raises SpatialiteConnectionProblem. If any other OperationalError arises from PRAGMA, ConnectionProblem is raised.

## Side Effects:
    - Executes SQL queries against the provided connection:
        * SELECT name FROM sqlite_master WHERE type='table'
        * PRAGMA table_info(<escaped-table-name>) for each discovered table
    - These SQL statements are read-only; they may still cause the SQLite engine to interact with the database file (I/O) and may trigger extension loading attempts inside SQLite.
    - No global state in Python is mutated by this function.

## Control Flow:
flowchart TD
    Start --> QueryTables[Execute "select name from sqlite_master where type='table'"]
    QueryTables --> TablesList[Fetch all table names]
    TablesList --> ForEach[Iterate tables]
    ForEach --> TryPragma[Try execute PRAGMA table_info(escaped_table)]
    TryPragma --> PragmaOK[No exception: continue]
    TryPragma -->|sqlite3.OperationalError e| CheckMsg{e.args[0] == "no such module: VirtualSpatialIndex"?}
    CheckMsg -->|True| RaiseSpatial[raise SpatialiteConnectionProblem(e)]
    CheckMsg -->|False| RaiseConn[raise ConnectionProblem(e)]
    PragmaOK --> ForEach
    ForEach --> End[Return None]

## Examples:
Example — basic usage with error handling:
    try:
        check_connection(conn)  # conn is a sqlite3.Connection-like object
    except SpatialiteConnectionProblem as e:
        # Detected a missing or broken SpatiaLite module; handle or surface a clear error
        print("SpatiaLite-specific connection problem:", e)
    except ConnectionProblem as e:
        # Generic problem accessing table metadata; treat as connection failure
        print("Database connection problem:", e)
    else:
        # Connection validated successfully; proceed with normal startup
        print("Connection OK")

Notes:
    - Do not rely on this function to catch all possible sqlite3 exceptions; it only converts OperationalError raised during PRAGMA table_info into module-specific exceptions. Errors from the initial table list query or unexpected exception types will propagate and should be handled by the caller if desired.
    - The check is intentionally conservative: it only treats the specific error message "no such module: VirtualSpatialIndex" as a SpatiaLite indicator. If SQLite/SpatiaLite deployments produce different messages, callers may need to adapt detection logic elsewhere.

## `datasette.utils.__init__.BadMetadataError` · *class*

## Summary:
A dedicated Exception subclass (no added behavior) whose name indicates it represents errors related to invalid or malformed metadata.

## Description:
BadMetadataError is a direct subclass of Python's built-in Exception. The class body contains no custom logic, attributes, or methods (it uses pass). Its existence provides a distinct exception type that code may raise to indicate a metadata-related problem; the class itself does not perform validation or enforce any metadata rules.

## State:
- Declared attributes: none (the class defines no new members).
- Inherited attributes (from Exception):
  - args (tuple): positional arguments passed to the constructor; may be empty.
  - __cause__, __context__, __traceback__: standard Python exception attributes for chaining and tracebacks.
- Invariants:
  - Instances are plain Exception instances; no additional instance state or invariants are imposed by this class.

## Lifecycle:
- Creation:
  - Construct using standard Exception semantics:
    - BadMetadataError()
    - BadMetadataError("message")
    - BadMetadataError("message", detail)
  - No custom __init__ is provided; initialization behavior is that of Exception.
- Usage:
  - Typical usage pattern (Python language semantics):
    - raise BadMetadataError("explanatory message")
    - try:
        ...
      except BadMetadataError as e:
        # handle metadata-specific error
- Destruction:
  - No special cleanup is required. Instances are normal objects and are garbage-collected when no longer referenced.

## Method Map:
graph TD
  Raise["raise BadMetadataError(...)"] --> Propagate["exception propagates through stack"]
  Propagate --> Catch["except BadMetadataError: handle or report"]

(This flow is the generic raise/propagate/catch lifecycle for any Exception subclass.)

## Raises:
- Instantiating BadMetadataError follows normal Python object construction and Exception behavior. The class defines no custom raise conditions; it will not itself raise new exception types during normal initialization. Only general Python runtime errors (e.g., MemoryError in extreme cases) would occur during object creation.

## Example:
- Raising:
  - raise BadMetadataError("missing required metadata field 'title'")
- Catching:
  - try:
      process_metadata(m)
    except BadMetadataError as e:
      print("Metadata error:", str(e))

## `datasette.utils.__init__.parse_metadata` · *function*

## Summary:
Parses a metadata string that may be JSON or YAML and returns the parsed value (typically a mapping). Raises a metadata-specific error if the content is neither valid JSON nor valid YAML.

## Description:
This helper centralizes the logic for interpreting metadata text supplied as a single string. It first attempts to parse the input as JSON; if that fails it falls back to YAML parsing using yaml.safe_load. The function exists so callers that accept metadata in either format can use one robust parsing entry point and receive a consistent error type when parsing fails.

Known callers within the provided repository snapshot:
- None found in the provided memory snapshot. Search the codebase for occurrences of parse_metadata to find current call sites.
Typical callers (realistic usage contexts):
- Routines that load metadata files (e.g., plugin or dataset metadata) from disk or network and need to accept either JSON or YAML.
- CLI subcommands that accept metadata text or files from users and must validate/parse that input.

Why this is a separate function:
- It centralizes parsing and error normalization (wraps YAML/JSON parsing errors into BadMetadataError) so calling code does not need to duplicate fallback logic or handle multiple parser exception types.

## Args:
    content (str): Source metadata text to parse.
        - Type: str (calling code should ensure a string is passed).
        - Expected format: JSON object/array/text or YAML document.
        - Interdependencies: None. The function assumes content is a textual representation; non-text inputs (bytes, None, objects) will likely raise unrelated errors from json.loads.

## Returns:
    dict (but may be other types): The parsed metadata value.
        - Typical/expected: a mapping (dict) representing metadata fields.
        - Possible return values:
            * dict: when the JSON/YAML document is a mapping.
            * list/str/int/float/bool: when the document represents a non-mapping YAML/JSON scalar or sequence.
            * None: when the input is empty YAML content (yaml.safe_load returns None for empty input).
        - Note: Although the function annotation is -> dict, callers must tolerate and validate other returned types because yaml.safe_load may produce non-mapping values.

## Raises:
    BadMetadataError: Raised when the input cannot be parsed as valid JSON (json.JSONDecodeError) and parsing as YAML (yaml.safe_load) raises a yaml.YAMLError. The exact message produced by this function is "Metadata is not valid JSON or YAML".
    TypeError / other exceptions from json.loads or yaml.safe_load: If content is not a str (despite annotation), json.loads may raise TypeError and those exceptions are not caught by parse_metadata. These propagate to the caller.

## Constraints:
    Preconditions:
        - content must be a text string (str). Passing other types may produce unexpected exceptions from the underlying parsers.
    Postconditions:
        - On success, the function returns the parsed representation produced by json.loads or yaml.safe_load.
        - On failure to parse as either format, a BadMetadataError is raised and no partial parsing result is returned.

## Side Effects:
    - None. The function performs pure parsing in-memory.
    - No I/O, no filesystem, network, global state, or cache mutations occur.

## Control Flow:
flowchart TD
    A[Start: receive content (str)] --> B{Try parse as JSON}
    B -- JSON parses successfully --> C[Return json.loads(content)]
    B -- JSON parse raises JSONDecodeError --> D{Try parse as YAML}
    D -- YAML parses successfully --> E[Return yaml.safe_load(content)]
    D -- YAML raises YAMLError --> F[Raise BadMetadataError("Metadata is not valid JSON or YAML")]
    C --> G[End]
    E --> G
    F --> G

## Examples:
1) Typical usage when reading a metadata file and validating a mapping result:
    - Read the file contents into a string.
    - Call parse_metadata(content).
    - If BadMetadataError is raised, report the parse failure to the user.
    - After a successful return, verify the returned value is a mapping (dict) before accessing keys; if not, treat it as an invalid metadata structure.

2) Example usage pattern (outline):
    - content = <text loaded from file or user input>
    - try:
        parsed = parse_metadata(content)
      except BadMetadataError as e:
        handle parse error (e.g., show message "Metadata is not valid JSON or YAML")
    - if not isinstance(parsed, dict):
        handle unexpected structure (e.g., require a mapping, not a scalar or list)

Notes and edge cases:
    - Empty string: JSON parsing will fail; yaml.safe_load('') returns None — callers expecting a dict must treat None as invalid.
    - A YAML document containing a single scalar (e.g., "42" or "on") will return a scalar type (int/bool) rather than a dict.
    - The function intentionally normalizes parser failure into BadMetadataError so callers can catch a single exception type for reporting parsing errors.

## `datasette.utils.__init__._gather_arguments` · *function*

## Summary:
Constructs an ordered list of argument values for calling a given function by extracting values from a mapping of keyword names to values; raises a TypeError if any parameter in the function's signature is missing from the mapping.

## Description:
_gather_arguments inspects the signature of the callable `fn` and, in signature parameter order, looks up each parameter name in the provided mapping `kwargs`. It returns a list of values corresponding to the function's parameters in the same order as the signature — this list is suitable to be passed to `fn` as positional arguments (for example, via `fn(*call_with)`).

Known callers within the provided code context:
- No direct callers were discovered in the supplied file-level context for this task. Typical usage pattern in codebases is:
  - A dispatcher or generic call site collects a pool of available values (a dict-like mapping) and uses _gather_arguments to assemble positional arguments before invoking a callable with those values.

Why extracted into its own function:
- Responsibility boundary: isolates the logic of mapping a function signature to an ordered list of argument values from a kwargs mapping. This keeps signature-inspection and argument-ordering centralized and testable, so call sites can focus on higher-level dispatching and invocation behavior.

## Args:
    fn (callable): The function or callable whose signature will be inspected. Must be a Python callable accepted by inspect.signature.
    kwargs (dict[str, any]): A mapping from parameter name (string) to the value that should be supplied for that parameter.

Notes on arguments:
- `fn` must be inspectable by inspect.signature (i.e., standard Python functions, callables with __call__, etc.).
- `kwargs` is treated as a plain mapping; any mapping type with __contains__ and __getitem__ semantics is acceptable (commonly a dict).

## Returns:
    list[any]: A list of values in the exact order of parameters returned by inspect.signature(fn).parameters.keys(), ready to be used as positional arguments when calling `fn` (e.g., `fn(*returned_list)`).

Possible return shapes and edge cases:
- An empty list when `fn` has no parameters.
- A list whose length equals the number of parameters in `fn`.
- Values in the returned list are exactly those retrieved from `kwargs` by parameter name; no defaults from the function signature are applied by this function.

## Raises:
    TypeError:
        - Raised when one or more parameter names from fn's signature are not present as keys in kwargs.
        - Exact message format produced by the implementation:
          "{} requires parameters {}, missing: {}".format(fn, tuple(parameters), set(parameters) - set(kwargs.keys()))
        - In practice this reports the callable object `fn`, a tuple of all parameter names, and a set of missing parameter names.

No other exceptions are explicitly raised by the function; underlying mapping access is guarded by membership checking, so KeyError should not occur inside this function.

## Constraints:
Preconditions:
- `fn` must be a callable that inspect.signature can analyze.
- `kwargs` must be a mapping containing keys that correspond (by name) to all parameters of `fn`.
- The caller must be prepared to receive positional arguments in the order returned (i.e., it should call `fn(*call_with)`), not to call via keywords.

Postconditions:
- If the function returns normally, the returned list length equals the number of parameters in `fn` and each element corresponds to the parameter at the same position in the signature order.
- If any parameter is missing in `kwargs`, a TypeError is raised and nothing is returned.

Behavioral caveats (important):
- Parameters that have default values in `fn` are NOT treated specially: this function requires every parameter name to be present in `kwargs` even if the parameter has a default. Calling with a mapping that omits parameters with defaults will still trigger TypeError.
- VAR_POSITIONAL (*args) and VAR_KEYWORD (**kwargs) parameters appear as parameter names in the signature (their "name" is whatever identifier was used, e.g., "args", "kwargs") and will therefore be expected as keys in `kwargs` as well. This function does not perform special handling to expand or collect values for varargs/ varkw; it treats every signature parameter uniformly by name.
- Positional-only parameters (if present in the signature) are included in the parameter ordering and must be provided in `kwargs` for this function, because this function extracts values by name from `kwargs` and returns them positionally for invocation.

## Side Effects:
- None. The function performs no I/O, does not mutate global state, and does not modify the provided mapping `kwargs`. It calls inspect.signature (introspection) but that has no side effects.

## Control Flow:
flowchart TD
    Start --> InspectSignature[Inspect signature(fn) -> parameter names (ordered)]
    InspectSignature --> Initialize[call_with = []]
    Initialize --> ForEachParam{For each parameter in parameters}
    ForEachParam --> CheckInKwargs{Is parameter in kwargs?}
    CheckInKwargs -->|No| RaiseError[Raise TypeError (missing parameter(s))]
    CheckInKwargs -->|Yes| AppendValue[Append kwargs[parameter] to call_with]
    AppendValue --> ForEachParam
    ForEachParam --> AfterLoop[After all parameters processed]
    AfterLoop --> ReturnList[Return call_with]
    RaiseError --> End
    ReturnList --> End

## Examples:
1) Basic successful assembly and invocation
    def add(a, b):
        return a + b

    mapping = {"a": 2, "b": 3}
    call_with = _gather_arguments(add, mapping)   # returns [2, 3]
    result = add(*call_with)                      # result == 5

2) Missing parameter (raises TypeError)
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}"

    mapping = {"name": "Pat"}                     # NOTE: greeting omitted
    # _gather_arguments(greet, mapping) will raise TypeError
    # because the function requires both 'name' and 'greeting' to be present
    # even though 'greeting' has a default value.

3) Functions with no parameters
    def noop():
        pass

    mapping = {}
    call_with = _gather_arguments(noop, mapping)  # returns []

4) Caution with varargs/varkw
    def f(*args, **kwargs):
        pass

    mapping = {} 
    # _gather_arguments will look for parameter names corresponding to the
    # signature entries ('args' and 'kwargs') and will therefore raise TypeError
    # unless mapping contains keys 'args' and 'kwargs'. This function does not
    # auto-expand a sequence into *args or a mapping into **kwargs.

## Implementation notes (for reimplementation):
- Use inspect.signature(fn).parameters.keys() to obtain parameters in declared order.
- Iterate those parameter names and check membership in kwargs (via "in").
- If any parameter is missing, raise TypeError with the formatted message shown above.
- Otherwise, append kwargs[parameter] to a list and return it after processing all parameters.

## `datasette.utils.__init__.call_with_supported_arguments` · *function*

## Summary:
Invoke a callable by assembling positional arguments from a provided keyword-value mapping and return the callable's result.

## Description:
call_with_supported_arguments builds a positional-argument list for the callable `fn` by delegating the parameter-order extraction to the helper _gather_arguments(fn, kwargs) and then invoking `fn` with those positional arguments (i.e., fn(*call_with)). This function thus performs two simple steps: gather positional arguments in signature order, then call the function.

Known callers within the codebase:
- No direct callers were discovered in the supplied file-level context. Typical usage is from dispatcher/adapter code that has a pool of named values (a dict) and wants to call a variety of callables using values from that pool without manually matching signature order.

Why this is extracted into its own function:
- Separation of concerns: it isolates the invocation step (gather arguments then call) from the argument-gathering logic implemented in _gather_arguments. This keeps caller code concise and centralizes the calling convention (use gathered positional args) in a single place.

## Args:
    fn (callable):
        The function or callable to invoke. Must be inspectable by inspect.signature (regular functions or objects implementing __call__).
    **kwargs:
        Keyword arguments (collected into a dict) that represent a mapping from parameter name to the value to be used for that parameter. These are forwarded to _gather_arguments, which will extract values for every parameter name in `fn`'s signature.

Notes on interdependencies:
- The correctness of the invocation depends on _gather_arguments succeeding: kwargs must contain keys for every parameter name in fn's signature (see _gather_arguments behavior). call_with_supported_arguments does not perform additional filtering or default filling itself.

## Returns:
    Any:
        The return value produced by calling fn(*call_with). It is returned unchanged to the caller.

Possible return behaviors and edge-cases:
- If fn returns None, call_with_supported_arguments returns None.
- If fn raises an exception during execution, that exception propagates unchanged (this function does not catch or wrap exceptions raised by fn).

## Raises:
    TypeError:
        - Propagated from _gather_arguments when one or more parameter names in fn's signature are missing from kwargs. The helper raises a TypeError listing the callable, all parameter names, and the set of missing parameter names.
        - TypeError may also arise from the actual call fn(*call_with) if the assembled positional arguments are incompatible with fn (for example, attempting to pass positional values for parameters that are keyword-only will raise a TypeError at call time).
    Any exception raised by fn:
        - Any exception raised while executing fn will propagate to the caller (call_with_supported_arguments does not swallow exceptions).

## Constraints:
Preconditions:
- fn must be a callable that can be inspected by inspect.signature.
- kwargs must contain entries for every parameter name in fn's signature; _gather_arguments enforces this.
- The assembled positional arguments must be acceptable to fn when passed positionally. In particular, fn should not require keyword-only-only parameters if you intend to supply them positionally via this helper (see Caveats).

Postconditions:
- On successful return, fn has been invoked with positional arguments corresponding to its signature's parameter order, and the return value from fn is returned.
- On failure due to missing parameters or incompatible argument kinds, an exception is raised and no value is returned.

## Side Effects:
- This function performs no I/O itself and does not mutate global state.
- Side effects may occur as a result of calling fn (file I/O, network, database writes, etc.); such side effects are determined entirely by fn.
- No modification of the kwargs mapping is performed; kwargs is forwarded to _gather_arguments which only reads from it.

## Control Flow:
flowchart TD
    Start --> Gather[_gather_arguments(fn, kwargs)]
    Gather -->|raises TypeError| PropagateGatherError[Propagate TypeError -> End]
    Gather -->|returns call_with list| CallFn[Call fn(*call_with)]
    CallFn -->|fn raises exception| PropagateFnError[Propagate exception -> End]
    CallFn -->|fn returns value| Return[Return value -> End]

## Examples:
1) Basic successful invocation (positional parameters)
    def add(a, b):
        return a + b

    result = call_with_supported_arguments(add, a=2, b=3)
    # result == 5

2) Missing parameter (TypeError from _gather_arguments)
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}"

    # greeting omitted: _gather_arguments requires both 'name' and 'greeting'
    try:
        call_with_supported_arguments(greet, name="Pat")
    except TypeError as e:
        # Handle missing-parameter situation
        print("Missing parameters:", e)

3) Caution: keyword-only parameters will not be supplied correctly as positional args
    def kw_only(*, token):
        return token

    # Even if you provide token in kwargs, the helper gathers it and then calls
    # fn(*[token]) which attempts to pass token positionally and raises TypeError.
    try:
        call_with_supported_arguments(kw_only, token="abc")
    except TypeError as e:
        # Expect a TypeError from attempting to give a keyword-only argument positionally
        print("Incompatible parameter kinds:", e)

Implementation note for reimplementation:
- The function is a thin wrapper that calls _gather_arguments(fn, kwargs) and then returns fn(*call_with). It intentionally does not perform additional signature checks, default application, or exception handling for fn.

## `datasette.utils.__init__.async_call_with_supported_arguments` · *function*

## Summary:
Await the result of calling a callable with positional arguments assembled from a name→value mapping, returning the awaited result.

## Description:
Calls a callable by first converting a mapping of candidate values into an ordered positional argument list (using the helper that inspects the callable's signature) and then awaiting the callable invocation. Typical callers are generic dispatchers or request-handling code that have a pool/dict of available values and need to invoke an async handler or a function that returns an awaitable.

Known callers within the codebase:
- No direct callers were discovered in the provided file-level context. Typical usage pattern: a dispatcher collects available values into a mapping and uses this function to invoke an async handler with only the parameters the handler declared.

Why this logic is extracted:
- Responsibility separation: keeps two concerns separate — (1) mapping parameter names to an ordered positional argument list (delegated to the signature-inspection helper), and (2) invoking and awaiting the callable. Extracting the await-and-invoke behavior makes call sites simpler, centralizes error behavior (missing args vs non-awaitable results), and improves testability.

## Args:
    fn (callable): A callable to invoke. It may be:
        - an async function (coroutine function), or
        - a synchronous function that returns an awaitable (an object supporting the await protocol).
      The callable must be inspectable by inspect.signature for the argument-gathering step.
    **kwargs (mapping[str, any]): A mapping whose keys are parameter names and whose values are the values to be supplied for those parameters. Every parameter name present in fn's signature must be present as a key in this mapping (see Constraints).

Notes on interdependencies:
- Argument assembly is delegated to the signature-inspection helper which requires that kwargs contain an entry for every parameter name in fn's signature (including parameters with defaults, *args and **kwargs names, and positional-only parameters). If the mapping omits any signature parameter name, the helper raises TypeError and this function does not call fn.

## Returns:
    any: The value produced by awaiting the result of invoking fn(*call_with).
    - If fn is an async function, this is the value returned by that coroutine when awaited.
    - If fn is a regular function that returns an awaitable, this is the awaited value of that awaitable.
    - The function returns whatever the awaited callable returns; no additional wrapping is applied.

Edge-case returns:
- If fn returns None but is awaitable (e.g., an async function that returns None), the function returns None.
- This function never returns an awaitable object itself; it always awaits and returns the resolved concrete result (or propagates exceptions).

## Raises:
    TypeError:
        - If the argument-gathering helper detects missing parameter names in kwargs (i.e., kwargs does not contain a key for every parameter in fn's signature). The exact message originates from the helper and identifies the missing parameters.
        - If the object produced by calling fn(*call_with) is not awaitable, awaiting it will raise TypeError (await requires an awaitable object).
    Any exception raised synchronously by calling the callable or raised while awaiting the returned awaitable is propagated unchanged.

## Constraints:
Preconditions:
- fn must be a Python callable inspect.signature can analyze.
- kwargs must include keys for every parameter name declared in fn's signature (the helper does not use function defaults).
- The evaluated expression fn(*call_with) must produce an awaitable (coroutine or object implementing __await__), otherwise awaiting will fail.

Postconditions:
- On normal return, the value returned equals the awaited result of fn invoked with the ordered positional arguments derived from kwargs.
- No mutation of kwargs or other global state is performed by this function itself (side effects may occur inside fn).

## Side Effects:
- This function performs no I/O, does not modify globals, and does not mutate the kwargs mapping.
- Any side effects are those caused by the invoked callable fn (e.g., DB writes, network calls) and are not introduced by this utility.

## Control Flow:
flowchart TD
    Start --> Gather[Call helper to gather ordered args from kwargs]
    Gather -->|helper raises TypeError| PropagateMissing[Propagate TypeError -> End]
    Gather --> CallInvoke[Invoke callable: result = fn(*ordered_args)]
    CallInvoke -->|call raises exception| PropagateCallError[Propagate exception -> End]
    CallInvoke --> AwaitResult[Await result]
    AwaitResult -->|result is not awaitable -> TypeError| PropagateAwaitError[Propagate TypeError -> End]
    AwaitResult -->|await completes normally| ReturnValue[Return awaited value -> End]
    AwaitResult -->|await raises exception| PropagateAwaitException[Propagate exception -> End]

## Examples:
1) Typical successful usage (async handler)
    - Prepare a mapping of parameter names to values for a handler that expects those parameters.
    - Call the utility to assemble positional args and await the handler:
      result = await async_call_with_supported_arguments(handler_callable, **mapping)
    - On return, result contains the handler's awaited return value.

2) Callable that is synchronous but returns an awaitable
    - If the callable returns an awaitable, this utility will await that returned awaitable and return its result:
      result = await async_call_with_supported_arguments(sync_returning_awaitable, **mapping)

3) Error handling for missing parameters
    - If mapping omits a required parameter name from the callable's signature, a TypeError is raised before the callable is invoked. Example handling:
      try:
          result = await async_call_with_supported_arguments(handler_callable, **incomplete_mapping)
      except TypeError as e:
          handle_missing_arguments(e)

4) Error handling for non-awaitable results
    - If the callable returns a non-awaitable, awaiting it raises TypeError. Example handling:
      try:
          result = await async_call_with_supported_arguments(bad_callable, **mapping)
      except TypeError as e:
          handle_non_awaitable_result(e)

Notes:
- Because the argument-gathering helper requires keys for all signature parameters (including those with defaults and varargs names), ensure the mapping provides explicit entries for parameters you rely on defaults for, or modify invocation to use a different helper that respects defaults.

## `datasette.utils.__init__.actor_matches_allow` · *function*

## Summary:
Determines whether a given actor satisfies an "allow" policy definition and returns a boolean result indicating permission.

## Description:
This function evaluates an "allow" policy (which may be a boolean, None, or a mapping of actor attributes to allowed values) against an actor representation (typically a mapping of attributes to values) and returns True if the actor matches any of the allow rules.

Known callers within the provided code context:
- No direct callers were present in the provided file fragment. Typical callers (in a web/permission system) are permission-evaluation routines that decide whether an incoming request's actor is allowed to access a resource or perform an action.

Why this logic is extracted into its own function:
- It centralizes policy matching rules (handling booleans, None, unauthenticated allowances, wildcards, single values vs lists) so permission checks elsewhere can be concise and consistent. The function encapsulates conversion/normalization behavior (singletons -> lists, None -> {}) and the matching semantics in one place.

## Args:
    actor (mapping | None):
        - A mapping-like object representing the actor (for example, {"id": 1, "groups": ["editors"]}).
        - The code expects actor to support membership testing (key in actor) and .get(key).
        - If None, it is treated as no actor (unauthenticated). If falsy (e.g., {}), it becomes an empty mapping.
    allow (bool | None | mapping):
        - Policy describing allowed actors.
        - If True: allow everyone (function returns True).
        - If False: deny everyone (function returns False).
        - If None: interpreted as "no policy present" and treated permissively (function returns True).
        - If a mapping: keys are actor attribute names and values are either:
            * a single value (string/number/etc.),
            * a list of allowed values,
            * the literal "*" (string) indicating a wildcard match if the actor has that attribute,
            * or the special key "unauthenticated" with a boolean True to allow missing/None actor.

Notes on interdependencies:
- When allow is a mapping, the function iterates over allow.items() and tries to match any one mapping entry — the policy is satisfied if any single entry matches (logical OR across allow entries).
- The special key "unauthenticated": if actor is None and allow.get("unauthenticated") is True, the function returns True before checking other allow entries.

## Returns:
    bool:
        - True when the actor satisfies the allow policy according to the rules below; otherwise False.
        - Possible return cases:
            * True if allow is True.
            * False if allow is False.
            * True if allow is None.
            * True if actor is None and allow is a mapping with "unauthenticated": True.
            * True if any allow entry matches the actor:
                - If allow[key] == "*" and the actor has that key (regardless of its value).
                - If allow[key] is a value or list and the actor has a matching value for that key (intersection of actor value(s) and allow value(s) is non-empty).
            * False if none of the above conditions match.

## Raises:
    AttributeError:
        - If actor is not None and does not implement .get or membership testing (e.g., passing an integer), trying to call actor.get(...) or "key in actor" will raise AttributeError.
        - If allow is not a mapping, boolean, or None and lacks .items(), calling allow.items() will raise AttributeError.
    TypeError:
        - If actor attribute values contain unhashable items (e.g., lists) the conversion to a set may raise TypeError when trying to create a set of those values. This is a consequence of using set(...) internally.

(These exceptions are not explicitly raised by the function but occur as direct consequences of the operations performed on the provided inputs.)

## Constraints:
Preconditions:
    - Caller should pass allow as one of: bool, None, or a mapping-like object (mapping keys -> value or list or "*").
    - Caller should pass actor as None or a mapping-like object where keys are attribute names and values are singletons or lists of values.
    - Values used for membership/intersection should be hashable when lists are provided (so intersection/set conversion succeeds).

Postconditions:
    - The function returns a boolean and does not mutate actor or allow.
    - No side effects (no I/O, no external state mutation).

## Side Effects:
    - None. The function performs only in-memory, read-only checks on the provided inputs.

## Control Flow:
flowchart TD
    Start --> CheckAllowTrue
    CheckAllowTrue{allow is True?}
    CheckAllowTrue -- Yes --> ReturnTrue1[Return True]
    CheckAllowTrue -- No --> CheckAllowFalse{allow is False?}
    CheckAllowFalse -- Yes --> ReturnFalse1[Return False]
    CheckAllowFalse -- No --> CheckUnauthenticated{actor is None and allow and allow.get("unauthenticated") is True?}
    CheckUnauthenticated -- Yes --> ReturnTrue2[Return True]
    CheckUnauthenticated -- No --> CheckAllowNone{allow is None?}
    CheckAllowNone -- Yes --> ReturnTrue3[Return True]
    CheckAllowNone -- No --> NormalizeActor[actor = actor or {}]
    NormalizeActor --> ForEachAllowEntry[for key, values in allow.items()]
    ForEachAllowEntry --> ValuesWildcard{values == "*" and key in actor?}
    ValuesWildcard -- Yes --> ReturnTrue4[Return True]
    ValuesWildcard -- No --> NormalizeValues[if not list -> wrap as list]
    NormalizeValues --> GetActorValues[actor_values = actor.get(key)]
    GetActorValues --> ActorValuesNone{actor_values is None?}
    ActorValuesNone -- Yes --> ContinueLoop[continue to next allow entry]
    ActorValuesNone -- No --> NormalizeActorValues[if not list -> wrap as list]
    NormalizeActorValues --> ConvertToSet[actor_values = set(actor_values)]
    ConvertToSet --> Intersection{actor_values.intersection(values) non-empty?}
    Intersection -- Yes --> ReturnTrue5[Return True]
    Intersection -- No --> ContinueLoop
    ContinueLoop --> ForEachAllowEntry
    ForEachAllowEntry --> End[after all entries processed]
    End --> ReturnFalse2[Return False]

## Examples:
1) Allow by group membership:
    - Scenario: actor is {"id": 5, "groups": ["editors"]}; allow is {"groups": ["editors", "admins"]}.
    - Outcome: function returns True because the actor's "groups" intersect with the allow list.

2) Allow wildcard for an attribute presence:
    - Scenario: actor is {"id": 5, "roles": ["member"]}; allow is {"roles": "*"}.
    - Outcome: function returns True because allow specifies "*" for the "roles" key and the actor has that key.

3) Unauthenticated allowance:
    - Scenario: actor is None (no logged-in user) and allow is {"unauthenticated": True}.
    - Outcome: function returns True (explicitly allows unauthenticated access).

4) Explicit deny and permissive None:
    - allow = False -> function always returns False.
    - allow = None -> function always returns True (treated as no policy restricting access).

5) Error handling when inputs are malformed:
    - If caller passes a non-mapping actor (e.g., an integer) or non-mapping allow (e.g., an integer) the function will raise an AttributeError when it attempts to call .get or .items(). Callers should validate input types or catch exceptions accordingly.

## `datasette.utils.__init__.resolve_env_secrets` · *function*

## Summary:
Recursively walk a JSON-like data structure and replace sentinel objects {"$env": "NAME"} with values looked up from a provided environment mapping, and {"$file": "PATH"} with the contents of the referenced file.

## Description:
This function is intended to resolve external secrets or file-based values referenced in configuration objects before the configuration is used by the application. It accepts an arbitrarily nested structure made up of dicts, lists, and scalar values and returns a new structure where special sentinel dicts have been replaced with actual values:

- Known callers within the codebase:
    - No direct caller locations were discovered in this inspection. Typical usage is during application startup or configuration loading, immediately after parsing YAML/JSON configuration files and before passing configuration into components that require concrete values (database credentials, API keys, file contents, etc).

- Why this logic is extracted:
    - Separates the concern of resolving external references (environment variables and file contents) from other configuration handling logic.
    - Centralizes the replacement rules and recursion behavior so callers can pass a parsed configuration structure and receive a resolved, ready-to-use copy without mutating the original.

## Args:
    config (Any): A parsed configuration value. Expected to be a JSON/YAML-like structure composed of:
        - dict objects (mappings)
        - list objects (sequences)
        - scalar values (strings, numbers, booleans, None)
      Special sentinel dicts recognized:
        - {"$env": "NAME"} — indicates the value should come from the environment mapping under key "NAME"
        - {"$file": "PATH"} — indicates the value should be the contents of the file at PATH
      Any other dict shapes are processed recursively.
    environ (Mapping[str, Any] or object with get method): A mapping-like object (for example os.environ or a plain dict) that exposes a get(key[, default]) method used to retrieve environment values. The returned environment value is used as-is (no casting or parsing is performed).

## Returns:
    Any: A new structure mirroring the input config but with sentinel dicts replaced:
        - If a dict equals {"$env": "NAME"}: returns environ.get("NAME") — can be None if the key is missing.
        - If a dict equals {"$file": "PATH"}: returns the full contents of the file at PATH as a string.
        - If config is a dict with other keys: returns a dict whose values have been resolved recursively.
        - If config is a list: returns a list with each element resolved recursively.
        - If config is a scalar: returns the scalar unchanged.
    Notes on possible return values:
        - Missing environment keys yield None (no default is injected by this function).
        - File contents are returned as the raw string read from the file (including newlines).
        - The returned structure is newly created for lists/dicts; scalars may be reused.

## Raises:
    - FileNotFoundError / OSError: If a {"$file": "PATH"} sentinel is encountered and opening or reading the file fails (file not found, permission denied, etc). The underlying exception from open/read is propagated.
    - AttributeError or TypeError: If environ does not implement a get method (for example, a non-mapping object without get is supplied), calling environ.get(...) will raise; the function does not validate nor wrap this.
    - RecursionError: For extremely deep nested structures, Python's recursion limit may be hit and a RecursionError can be raised.
    - Any other exceptions thrown by environ.get or file I/O are propagated.

## Constraints:
    Preconditions:
        - config must be a tree of Python objects that are safe to iterate (dicts, lists, scalars). Objects with custom mapping/list semantics may behave unpredictably.
        - environ must expose get(name) (typical: dict-like or os.environ).
        - For {"$file": PATH} sentinels, PATH should be a filesystem path string readable by the process.
    Postconditions:
        - The returned value has the same overall shape as config, except that any sentinel dicts have been replaced.
        - The original config structure is not modified for dicts and lists (new dicts/lists are created during recursion).

## Side Effects:
    - Reads files from disk when encountering {"$file": PATH} sentinels. No file writes are performed.
    - No network I/O.
    - No mutation of global variables or input config objects (new containers are created).
    - Calls environ.get, which may have side effects if a custom mapping implements a side-effecting get — standard dict/os.environ.get is side-effect-free.

## Control Flow:
flowchart TD
    A[Start: resolve_env_secrets(config, environ)]
    A --> B{config is dict?}
    B -- yes --> C{dict keys == ["$env"]?}
    C -- yes --> D[Return environ.get(NAME)]
    C -- no --> E{dict keys == ["$file"]?}
    E -- yes --> F[Open PATH and read; return file contents]
    E -- no --> G[For each key,value -> call resolve_env_secrets(value,environ); assemble new dict; return dict]
    B -- no --> H{config is list?}
    H -- yes --> I[Map resolve_env_secrets over list elements; return new list]
    H -- no --> J[Return config unchanged]
    D --> End
    F --> End
    G --> End
    I --> End
    J --> End

## Examples:
- Resolving an environment-referenced secret:
    Given config = {"database": {"password": {"$env": "DB_PASS"}}} and environ = {"DB_PASS": "s3cr3t"}, the function returns {"database": {"password": "s3cr3t"}}. If "DB_PASS" is not present, the resolved password becomes None.

- Resolving a file reference (with error handling):
    When config contains {"tls_cert": {"$file": "/etc/ssl/cert.pem"}}, the function will attempt to open and read that path. Callers should handle file-related exceptions:
    - Wrap the call in try/except around FileNotFoundError or OSError to provide a fallback or meaningful startup error message.

- Mixed nested example:
    Input: {"service": {"token": {"$env": "TOKEN"}, "notes": ["static", {"$file": "/tmp/msg.txt"}]}}
    Behavior:
        - The token value is replaced with environ.get("TOKEN").
        - The notes list becomes a new list where the file sentinel is replaced by the file contents string.
        - Scalars and other dicts are preserved or recursively transformed.

- Defensive usage notes:
    - Validate that environ contains required keys and provide defaults before or after calling this function if you need non-None values.
    - Consider reading file existence/permissions earlier if you want to surface missing files with clearer errors than the raw OSError.

## `datasette.utils.__init__.display_actor` · *function*

## Summary:
Return a human-readable label for an actor by selecting the first truthy value among common identity keys, falling back to the actor's string representation.

## Description:
This small helper normalizes how an "actor" (a user-like object or mapping) is presented in UIs, logs, templates, or messages by preferring commonly-used identity fields in a fixed priority order.

Known callers within the provided context:
- No direct callers were present in the supplied file fragment. In typical codebases, this helper is called from presentation or logging code that needs a compact, user-facing label for an actor object.

Reason for extracting into its own function:
- Encapsulates the canonical priority order for actor display keys ("display", "name", "username", "login", "id"), ensuring consistent labels across the codebase.
- Keeps presentation logic out of templates and higher-level code, improving maintainability and allowing a single place to adjust ordering or fallback behavior.

## Args:
    actor (mapping-like or object with .get and __getitem__): An object representing an actor. Expected to implement a get(key) method (as mappings do) and also support indexing via actor[key] for the chosen key. Typical concrete types are dict or other mapping-like objects.

Notes on parameter constraints and interdependencies:
- The function tests truthiness using actor.get(key) but returns the value via actor[key]. Therefore both of the following must be valid for successful early returns:
  - actor.get must exist and be callable.
  - actor must support __getitem__ lookup for the same key (actor[key]) without raising.
- If actor does not provide a get attribute, calling this function will raise AttributeError.
- If actor.get(key) returns a truthy value but actor[key] lookup fails (KeyError, TypeError, or similar), that exception will propagate.

## Returns:
- The value stored in actor for the first key in ("display", "name", "username", "login", "id") that yields a truthy result from actor.get(key). The returned value can be of any type (string, number, object) depending on what the actor holds.
- If none of the listed keys exist or all their values are falsy, returns str(actor) — the string representation of the actor (guaranteed to be a str).

Examples of possible return values:
- "Alice" (string) if actor contains {"username": "Alice"}.
- 42 (int) if actor contains {"id": 42} and id is the first truthy key.
- "<Actor object ...>" when all keys are missing/falsy and str(actor) is used.

## Raises:
- AttributeError: If the supplied actor does not have a get attribute (e.g., actor is None or an object without get).
- KeyError: Possible if actor.get(key) is truthy but actor[key] lookup raises KeyError (e.g., a mapping with differing semantics). This exception is not caught by the function and will propagate.
- TypeError: Possible if actor does not support indexing via actor[key] (for example, get exists but __getitem__ is not implemented); this will propagate.
- Any exception raised by actor.get(key) or actor[key] will propagate to the caller.

## Constraints:
Preconditions:
- actor must be a non-None object that provides a callable get(key) method.
- For early (non-str fallback) success, actor must also support item access via actor[key] for the chosen key.

Postconditions:
- The function returns a value that is either:
  - The actor's indexed value for one of the prioritized keys (first truthy key), or
  - The string representation of the actor (str(actor)) when no prioritized key yields a truthy value.
- No mutation is performed on actor by this function.

## Side Effects:
- None within the Python process: this function performs only read-only attribute/mapping lookups and string conversion.
- No I/O, no network calls, no global state mutation, and no logging are performed.

## Control Flow:
flowchart TD
    Start[Start: given actor]
    CheckGet{"actor has get attribute?"}
    IsCallable{"actor.get is callable?"}
    IterateKeys[Loop keys: display,name,username,login,id]
    CallGet["call actor.get(key)"]
    IsTruthy{"result is truthy?"}
    ReturnIndex["return actor[key]"]
    AllFalsy{"no truthy key found"}
    ReturnStr["return str(actor)"]
    ErrorIndex["actor[key] raises -> propagate exception"]
    ErrorGet["actor.get missing or not callable -> AttributeError"]

    Start --> CheckGet
    CheckGet -->|no| ErrorGet
    CheckGet -->|yes| IsCallable
    IsCallable -->|no| ErrorGet
    IsCallable -->|yes| IterateKeys
    IterateKeys --> CallGet
    CallGet -->|truthy| IsTruthy
    IsTruthy -->|yes| ReturnIndex
    ReturnIndex --> End[End]
    IsTruthy -->|no| IterateKeys
    IterateKeys -->|finished| AllFalsy
    AllFalsy --> ReturnStr
    ReturnStr --> End
    ReturnIndex -->|if actor[key] raises| ErrorIndex

## Examples:
1) Typical usage with a mapping:
    actor = {"id": 7, "username": "alice"}
    display_actor(actor) -> "alice"  (because "username" is in the priority list and truthy)

2) When only id is present:
    actor = {"id": 7}
    display_actor(actor) -> 7  (first truthy key is "id"; note return type can be non-str)

3) Fallback to string representation:
    actor = {"email": "a@example.com"}  # none of the prioritized keys are present
    display_actor(actor) -> str(actor)

4) Defensive usage with error handling:
    try:
        label = display_actor(actor)
    except AttributeError:
        # actor had no .get (e.g., None or an unexpected type)
        label = "<unknown actor>"
    except (KeyError, TypeError) as e:
        # actor.get returned truthy but actor[...] lookup failed
        label = str(actor)

Notes:
- If you control the types passed to this helper, prefer passing mapping-like objects (dict) so both actor.get and actor[key] succeed predictably.
- If callers may pass objects without get or without __getitem__, wrap calls in try/except or normalize actor objects beforehand.

## `datasette.utils.__init__.SpatialiteNotFound` · *class*

## Summary:
A dedicated exception type used to signal that the SpatiaLite (Spatialite) extension/library could not be found.

## Description:
This exception exists so calling code can raise and catch a specific, unambiguous error when an attempt to locate or load the SpatiaLite extension fails. It carries no custom behavior beyond what Python's built-in Exception provides; its purpose is semantic: to identify the "spatialite-not-found" condition with a distinct type rather than a generic Exception or RuntimeError. Typical usage is to raise this exception from utility functions that probe for or attempt to load SpatiaLite and to catch this specific exception where higher-level code needs to handle that condition differently (for example, to report a clear error to the user or to fall back to alternative behavior).

## State:
- Inherited state (from built-in Exception):
    - args (tuple): contains any positional arguments supplied when the exception was instantiated (commonly a single human-readable message). Valid values: any picklable Python objects.
    - __cause__, __context__, __traceback__: standard exception attributes provided by Python runtime; not modified by this class.
- This class defines no additional instance attributes or class attributes.
- Invariants:
    - Instances behave exactly like instances of Exception with regard to messaging and pickling: str(instance) reflects the first element of args (if present); instance.args contains the tuple passed at construction.

## Lifecycle:
- Creation:
    - Instantiate by constructing SpatialiteNotFound with zero or more arguments (commonly a single string message). Example in prose: create an instance with a descriptive message indicating which resource or step failed (e.g., a message stating that the SpatiaLite shared library was not found at expected locations).
- Usage:
    - Intended invocation pattern is to raise the exception when SpatiaLite cannot be located or loaded.
    - Callers should catch SpatialiteNotFound when they need to handle this specific failure mode differently from other exceptions.
    - There is no required ordering of method calls; the object is a plain exception object with no lifecycle methods.
- Destruction / cleanup:
    - No special cleanup is required. Instances have no external resources and do not implement context management or close semantics.

## Method Map:
- The class has no custom methods beyond those inherited from Exception.
- Mermaid diagram (method/flow overview):
graph LR
    A[Code that locates/loads SpatiaLite] -->|on failure| B[Instantiate SpatialiteNotFound]
    B --> C[Raise exception]
    C --> D[Caller may catch SpatialiteNotFound]
    D --> E[Handle or surface a clear error / fallback]

## Raises:
- The class definition itself does not raise any exceptions.
- __init__: uses Exception.__init__ by inheritance; constructing an instance will only raise if the Python runtime raises during normal Exception construction (e.g., MemoryError), which is not specific to this class.
- Typical code that uses this class will raise SpatialiteNotFound to indicate the failure to find/load SpatiaLite.

## Example (described in prose):
- To signal the condition: create an instance of SpatialiteNotFound with a short explanatory message (for example, specifying which lookup paths were checked or that the shared library was missing) and raise it from the code that attempted to locate/load SpatiaLite.
- To handle the condition: in higher-level code, catch the SpatialiteNotFound exception type specifically and implement the desired behavior — for example, log or display the detailed message to the user, disable spatial features, or attempt an alternate implementation path.

## `datasette.utils.__init__.find_spatialite` · *function*

## Summary:
Searches a predefined list of filesystem locations and returns the first path that exists; if none exist, signals that SpatiaLite cannot be found.

## Description:
This utility inspects the global SPATIALITE_PATHS sequence and returns the first entry whose path exists on the local filesystem. It is intended as a small, single-responsibility helper used wherever the codebase needs the filesystem path to a SpatiaLite extension before attempting to load or use it.

Known callers within the provided snapshot:
- No specific call sites were identified in the immediate context provided. Typical call sites (outside this snapshot) are initialization routines or components that load SQLite extensions or configure spatial capabilities, which call this function to obtain a valid SpatiaLite extension file path prior to loading it into SQLite.

Why this is a separate function:
- Encapsulates the lookup logic (iterating a prioritized list of candidate locations) so callers do not duplicate the loop and existence-check logic.
- Centralizes the failure mode (raising a single exception type) so callers can handle the missing-extension case consistently.

## Args:
- None

Note: The function reads the global SPATIALITE_PATHS. That global must be an iterable (e.g., list or tuple) of candidate filesystem paths.

## Returns:
- str or os.PathLike: The first candidate from SPATIALITE_PATHS for which os.path.exists(candidate) returns True.
- Behavior details:
  - Iterates SPATIALITE_PATHS in order; returns immediately when it finds an existing path.
  - If a returned value is an os.PathLike object, the caller should accept and handle that type; common usage will treat it as a filesystem path string.

## Raises:
- SpatialiteNotFound: Raised when none of the entries in SPATIALITE_PATHS exist (including the case where SPATIALITE_PATHS is empty or contains only non-existent paths).
  - The exception is raised unconditionally at the end of the search loop if no existing path was found.

## Constraints:
Preconditions:
- SPATIALITE_PATHS must be defined in the same module scope and be iterable.
- Each entry in SPATIALITE_PATHS should be a filesystem path representation acceptable to os.path.exists (typically str, bytes, or objects implementing os.PathLike).

Postconditions:
- On normal return, the returned value references an existing filesystem path (os.path.exists(returned_value) is True).
- If the function returns, callers can rely on the path being present on disk (subject to external concurrent changes).
- If the function raises SpatialiteNotFound, no valid SpatiaLite path was found at call time.

## Side Effects:
- None observable beyond reading global state (SPATIALITE_PATHS) and performing filesystem existence checks using os.path.exists.
- No file or network I/O beyond the filesystem existence queries.
- No mutation of global variables or other external state.

## Control Flow:
flowchart TD
    Start([Start])
    ForEach{Next path from SPATIALITE_PATHS?}
    CheckExists[/os.path.exists(path)/]
    ReturnPath([return path])
    RaiseExc([raise SpatialiteNotFound])
    End([End])

    Start --> ForEach
    ForEach -->|has next| CheckExists
    CheckExists -->|exists| ReturnPath
    ReturnPath --> End
    CheckExists -->|not exists| ForEach
    ForEach -->|no next| RaiseExc
    RaiseExc --> End

## Examples:
1) Typical usage with error handling:
try:
    path = find_spatialite()
except SpatialiteNotFound:
    # fallback: disable spatial features, log and continue, or surface an error to the user
    print("SpatiaLite extension not found; spatial features disabled")
else:
    # path is a filesystem path (string or os.PathLike) that exists
    # proceed to load extension, e.g., sqlite3.enable_load_extension(True) then connection.load_extension(str(path))
    print("Found SpatiaLite at:", path)

2) Caller that wants a boolean check before proceeding:
try:
    sp_path = find_spatialite()
except SpatialiteNotFound:
    has_spatialite = False
else:
    has_spatialite = True

Notes for reimplementation:
- Implement as a straightforward loop over a global iterable SPATIALITE_PATHS, using os.path.exists for each candidate.
- Return the first candidate that os.path.exists returns True for; otherwise raise SpatialiteNotFound.
- Do not attempt to validate the file beyond existence (e.g., do not try to open or inspect the binary); that responsibility belongs to callers that actually load the extension.

## `datasette.utils.__init__.initial_path_for_datasette` · *function*

## Summary:
Choose a recommended navigation path (URL path string) for a Datasette instance that prefers a direct table view when there is exactly one non-internal database containing exactly one table, otherwise choosing the database or instance landing page.

## Description:
Asynchronously inspects the running Datasette application's registered databases (excluding the special "_internal" database) and returns one of three URL paths provided by the Datasette URL helper:
- If there is exactly one non-internal database:
  - Start with the database-level URL for that database.
  - If that database exposes exactly one table (table_names returns an iterable with length 1), return the table-level URL for that table instead.
- If there are zero or more than one non-internal databases, return the instance-level URL.

Known callers within the provided code context:
- No direct callers were discovered in the supplied context. Typical real-world callers include startup handlers, initial request routing or redirect logic, and UI code that must decide an initial page to present when a user visits the Datasette server.

Why this is a separate function:
- Encapsulates a small but frequently-used heuristic so it can be reused and unit-tested independently of routing or startup logic.
- Keeps higher-level code focused on control flow and side effects (redirects) while delegating the navigation-choice policy here.

## Args:
    datasette (object): The Datasette application object. Required attributes and behaviors:
        - datasette.databases: a mapping that supports .items(), yielding (name, db_object) pairs. The special key "_internal" is ignored by this function.
        - db_object: for each database value used, must expose an asynchronous method table_names() which can be awaited to produce an iterable/sequence of table names.
        - datasette.urls: an object exposing callables that return path strings:
            * database(db_name) -> str
            * table(db_name, table_name) -> str
            * instance() -> str
    Interdependencies:
        - The function awaits db_object.table_names(); therefore db_object.table_names must be awaitable and return an iterable whose length can be measured.

## Returns:
    str: A path string returned from one of the datasette.urls helpers:
        - datasette.urls.instance() when there are zero or multiple non-internal databases.
        - datasette.urls.database(db_name) when there is exactly one non-internal database and its table count is not exactly one.
        - datasette.urls.table(db_name, table_name) when there is exactly one non-internal database and it exposes exactly one table.
    Guarantee:
        - The function always returns a string (it always assigns and returns the local variable path).

## Raises:
    AttributeError:
        - If the provided datasette object lacks the expected attributes (for example, missing .databases or .urls) or those attributes do not support the methods used (.items(), callable urls.database/table/instance).
    TypeError:
        - If db.table_names exists but is not awaitable (awaiting it raises a TypeError) or if datasette.databases.items() does not behave like an iterable of pairs.
    Any exception raised by db.table_names():
        - Exceptions from the underlying database table_names() implementation (for example, database connection errors) are propagated unchanged.

## Constraints:
Preconditions:
    - Must be awaited from an async context (it is a coroutine).
    - datasette.databases must be a mapping-like object that yields name, db pairs via .items().
    - Each db object used must implement an async table_names() method.

Postconditions:
    - Returns a path string chosen from datasette.urls.instance(), datasette.urls.database(...), or datasette.urls.table(...).
    - Does not mutate datasette state.

## Side Effects:
    - This function itself performs no explicit I/O or state mutations; its only observable effect is the awaited call to db.table_names(), which may perform I/O or other side effects depending on the database implementation.
    - Any side effects are therefore implementation-dependent (originating in db.table_names or datasette.urls callables) and not caused directly by this helper.

## Control Flow:
flowchart TD
    Start --> Filter["Filter out '_internal' from datasette.databases (databases = dict([...]))"]
    Filter --> CountOne{"len(databases) == 1?"}
    CountOne -->|Yes| PickDB["db_name = only key\npath = datasette.urls.database(db_name)"]
    PickDB --> GetTables["db = only value\ntables = await db.table_names()"]
    GetTables --> OneTable{"len(tables) == 1?"}
    OneTable -->|Yes| TablePath["path = datasette.urls.table(db_name, tables[0])"]
    OneTable -->|No| KeepDB["keep database path"]
    KeepDB --> Return["return path"]
    TablePath --> Return
    CountOne -->|No| InstancePath["path = datasette.urls.instance()\nreturn path"]
    InstancePath --> Return
    Return --> End

## Examples:
Typical usage scenario (prose):
- A web request handler receives an incoming request to the root of the Datasette server and needs to redirect the client to an appropriate landing page. The handler awaits this coroutine with the running Datasette object to obtain the recommended path, and then issues an HTTP redirect to the returned string.
- If calling code wants to be defensive: await this function inside a try/except block; on exception, fall back to datasette.urls.instance() to guarantee a safe redirect target.

Concrete behavior illustrations:
- If datasette.databases contains only {"data": db} (plus possibly "_internal"), and db.table_names() returns ["people"], the function returns the table-level path for "data/people".
- If datasette.databases contains {"a": db1, "b": db2}, the function returns the instance-level path.
- If the single non-internal database exposes zero tables (empty list), the function returns the database-level path (it only chooses the table-level path when the table iterable's length equals exactly 1).

## `datasette.utils.__init__.PrefixedUrlString` · *class*

*No documentation generated.*

### `datasette.utils.__init__.PrefixedUrlString.__add__` · *method*

## Summary:
Returns a new string instance of the same subclass containing the concatenation of this value and the provided operand, preserving the PrefixedUrlString subclass type.

## Description:
This method overrides string addition to ensure that concatenating a PrefixedUrlString with another string produces an instance of the same subclass (type(self)) rather than a plain str. It delegates the actual concatenation to the built-in str.__add__ implementation and then wraps the resulting string in the subclass type.

Known callers and context:
- No specific direct callers were discovered in the inspected code for this repository. 
- Typical call sites: any code that concatenates URL-like values represented by PrefixedUrlString instances with other strings (for example building paths, query fragments, or appending segments). This method is invoked at the moment of using the + operator between a PrefixedUrlString and another operand during URL construction or manipulation.

Rationale for separate method:
- The method exists to preserve the PrefixedUrlString subclass identity through concatenation operations. Without this override, Python's str.__add__ would return a plain str, losing any additional behavior implemented by the PrefixedUrlString subclass (such as overridden attribute access that returns subclass instances). Encapsulating this logic in a dedicated __add__ keeps the behavior consistent and localized.

## Args:
    other (str): The right-hand operand to concatenate. Expected to be a string-compatible value. If a non-string is passed, the underlying string addition will not accept it and a TypeError will be raised.

## Returns:
    PrefixedUrlString (type(self)): A new instance of the same subclass as self containing the concatenated result of self and other. The returned object is a fresh string object (strings are immutable); self is not modified.

    Edge cases:
    - If other is not a str (or string-like acceptable by str.__add__), Python's concatenation will fail and a TypeError is raised by the underlying operation.
    - If the subclass overrides construction behavior (e.g., custom __new__), the returned instance will be produced via type(self)(value) so that subclass construction semantics are preserved.

## Raises:
    TypeError: Triggered when the underlying str.__add__ does not support concatenation with the given other (for example, attempting to add a non-str type). This is not raised explicitly here but propagated from the built-in string concatenation logic.

## State Changes:
Attributes READ:
    - None (does not read or rely on any custom instance attributes; uses only type(self) and Python's built-in str addition)

Attributes WRITTEN:
    - None (does not mutate self or any attributes)

## Constraints:
Preconditions:
    - self must be an instance of PrefixedUrlString (enforced by Python's method dispatch).
    - other should be a str (or an object accepted by str.__add__) for successful concatenation.

Postconditions:
    - Returns a new object of type(type(self)) whose text content equals the concatenation performed by str.__add__.
    - self remains unchanged (strings are immutable).

## Side Effects:
    - None. The method performs no I/O, network calls, or mutations of external objects; it only constructs and returns a new string-like object.

### `datasette.utils.__init__.PrefixedUrlString.__str__` · *method*

## Summary:
Returns the object's textual representation as a plain built-in str (not as a PrefixedUrlString subclass).

## Description:
This method delegates to the base str implementation to produce the textual representation used whenever the object is converted to text. Typical callers include:
- builtin str(obj) when code explicitly converts the instance to a string.
- print(obj), logging functions, and any formatting or serialization facilities that call __str__ to obtain human-readable text.
- string interpolation or formatting paths that fall back to __str__ when no custom __format__ is provided.

It is implemented as a separate method so the class can:
- Explicitly delegate to the underlying str.__str__ behavior (avoiding the wrapper logic in __getattribute__).
- Ensure that textual representation is returned as a plain str rather than wrapped again as PrefixedUrlString. This distinction matters because many of the class's other string methods (exposed via __getattribute__) intentionally wrap returned string results back into PrefixedUrlString; __str__ ensures a simple, standard string is returned for display/serialization.

## Args:
This method takes no arguments other than self.

## Returns:
str: A plain Python str containing the same characters as the PrefixedUrlString instance.
- For an empty PrefixedUrlString returns "".
- For strings containing special characters or unicode, returns the corresponding str with those characters preserved.
- Unlike many other string-returning methods on this class, the return value is not an instance of PrefixedUrlString.

## Raises:
This method does not explicitly raise exceptions. It relies on the base str.__str__ behavior, which does not raise for normal str instances.

## State Changes:
Attributes READ:
- none explicitly read (implicitly reads the object's character data maintained by the str base class)
Attributes WRITTEN:
- none

## Constraints:
Preconditions:
- self must be a valid PrefixedUrlString instance (a subclass of str).
Postconditions:
- The method returns a plain str equal to the textual contents of self.
- No attributes on self are modified.

## Side Effects:
- None. This method performs no I/O, network access, or mutations of objects outside self.
- Note: It intentionally does not return a PrefixedUrlString; callers that rely on wrapper behavior from other methods should not expect that here.

### `datasette.utils.__init__.PrefixedUrlString.__getattribute__` · *method*

## Summary:
Intercepts attribute access for non-dunder names that are defined on the built-in str type and returns a bound proxy method which delegates to the corresponding str implementation while preserving the PrefixedUrlString type for returned string (and shallow string-containing) values.

## Description:
This method is invoked whenever an attribute is accessed on a PrefixedUrlString instance (runtime attribute access). Typical callers are any code paths that call string methods on a PrefixedUrlString, for example:
    - my_prefixed.lower()
    - my_prefixed.split(',')
    - my_prefixed.partition(':')

Lifecycle/context:
    - It runs at the moment of attribute lookup on a PrefixedUrlString object. It does not itself call the looked-up method; instead it returns a bound proxy method which, when later invoked, runs the underlying str implementation and post-processes the result.
    - The method exists to ensure that common string operations performed on PrefixedUrlString instances yield results of the same custom subclass (PrefixedUrlString) instead of plain str, and to convert lists/tuples of strings returned by some str methods into lists/tuples of PrefixedUrlString. This keeps the "prefixed URL string" semantics and type through string transformations without duplicating string method implementations.

Why this is a separate method:
    - Centralizes the "wrap results with type(self)" behavior in a single place rather than repeating wrapping logic across many overridden string methods.
    - Uses dynamic delegation so that new/legacy str methods are automatically supported (no need to explicitly override each str method).

## Args:
    name (str): The attribute name being accessed. Must be a string. Behavior depends on its value:
        - If name starts with "__" (a dunder) OR name is not present in dir(str), normal attribute lookup is performed via the superclass and whatever attribute is returned is returned unchanged.
        - If name does not start with "__" and name is present in dir(str), a bound proxy method is returned (see Returns).

## Returns:
    - If name is a non-dunder attribute found in dir(str):
        A bound callable object (a method) that when invoked will:
            - Call the corresponding str implementation on the current instance (delegation via super()) with the provided args and kwargs.
            - Post-process the returned value as follows:
                * If the str method returns a str -> return a new instance of type(self) constructed from that string (i.e., PrefixedUrlString(...)).
                * If it returns a list -> return a list where each element has been passed through type(self) (list[type(self)(element) for element in value]).
                * If it returns a tuple -> return a tuple where each element has been passed through type(self) (tuple(type(self)(element) for element in value)).
                * Otherwise -> return the original value unchanged.
            - The callable is bound to the instance (method.__get__(self)), so calling it behaves like normal instance method calls.
    - Otherwise (dunder or not a str attribute):
        The result of super().__getattribute__(name) is returned directly (which may be an attribute, property, method, etc., defined on PrefixedUrlString or its superclasses).

Edge-case return behaviors:
    - If a str method returns nested structures (e.g., list of lists), only the top-level list/tuple elements are wrapped; nested elements are not recursively converted.
    - Wrapping list/tuple elements uses type(self)(element) unconditionally; non-string elements will be converted via the string constructor of the subclass (i.e., str(element) then PrefixedUrlString(...)).

## Raises:
    - AttributeError: May be raised by super().__getattribute__(name) when name is a dunder or not otherwise resolvable by the class hierarchy.
    - TypeError or other exceptions: May be raised by the delegated str method when invoked (e.g., wrong argument types), or by inappropriate use of the returned callable (e.g., calling a non-callable attribute if code bypasses the intended usage).
    - The method itself does not introduce new exception types beyond what the underlying attribute lookup and delegated str methods might raise.

## State Changes:
    Attributes READ:
        - None (this method does not read or mutate any self.<attr> instance attributes).
    Attributes WRITTEN:
        - None (no mutation of the instance occurs).

## Constraints:
    Preconditions:
        - Must be called on an instance of PrefixedUrlString (method defined on that class).
        - name must be a str representing the attribute being accessed.
        - If name triggers the delegated path (non-dunder and present in dir(str)), the underlying str implementation must accept the provided args/kwargs when the returned callable is invoked.

    Postconditions:
        - The instance itself is unchanged (immutable as it subclasses str).
        - For delegated str-method calls: returned string results are instances of type(self); lists/tuples returned by str methods are returned as list/tuple with each element converted by type(self).
        - For non-delegated attribute lookups: the attribute value returned is exactly what super().__getattribute__ provides.

## Side Effects:
    - No I/O or network interactions.
    - No mutation of objects external to the returned value (it only constructs new string-subclass instances or collections).
    - Calling the returned bound method may trigger the side effects of the underlying str method (if any), but built-in str methods are generally pure and side-effect free.

## Examples / Typical usage:
    - Accessing and calling a str method:
        When user code calls my_prefixed.upper(), __getattribute__ returns a bound proxy method; invoking it returns a PrefixedUrlString containing the uppercase text.
    - Splitting:
        my_prefixed.split() -> returns a list of PrefixedUrlString items rather than plain str items.

## Implementation notes / gotchas:
    - Only non-dunder attributes listed in dir(str) are proxied; custom attributes added to PrefixedUrlString or other non-str attributes will follow the normal lookup path.
    - Conversion of list/tuple elements is shallow; nested collections are not recursively wrapped.
    - The design relies on dynamic delegation via super() and descriptor binding (method.__get__(self)) to present proper bound methods to callers.

## `datasette.utils.__init__.StartupError` · *class*

## Summary:
Represents an application startup failure. A lightweight, semantic Exception subclass used to indicate fatal errors encountered during Datasette initialization.

## Description:
StartupError is a semantic marker type — it exists so calling code can raise and catch a specific exception that means "the application failed to start" as distinct from other runtime errors. Typical call sites create and raise this exception when configuration validation, plugin loading, database initialization, or other bootstrap tasks fail in a way that prevents the application from continuing.

Because StartupError does not add behavior beyond Python's built-in Exception, it delegates all construction, formatting, and storage of arguments to Exception. Use this type when you want callers (or top-level startup logic) to catch startup-specific failures and surface an appropriate message or non-zero exit code.

## State:
- Inherited attributes (public, from Exception / BaseException):
    - args (tuple): The tuple of positional arguments passed to the constructor. Commonly the first element is a human-readable error message (str).
    - __cause__, __context__, __traceback__ (exception bookkeeping from BaseException): standard fields available on all exceptions.
- Class invariants:
    - No additional instance attributes are added by StartupError. Any state is contained in the inherited Exception attributes (primarily args).
    - The first positional argument (if present) is typically a message string; code that consumes StartupError can assume e.args is a tuple (possibly empty).

## Lifecycle:
- Creation:
    - Instantiate like any Exception: StartupError("explanatory message") or StartupError(message, extra, info=val).
    - There are no custom constructor parameters; all arguments are forwarded to Exception.__init__.
- Usage:
    - Typical flow: raise StartupError(...) during startup or initialization; allow top-level code to catch except StartupError to handle startup failure (log, show message, exit).
    - Access error details via the exception instance (e.g., e.args, str(e)).
    - No special sequencing or setup is required before raising or handling this exception.
- Destruction / Cleanup:
    - No cleanup responsibilities. Instances follow normal Python exception lifecycle and are garbage-collected when out of scope. No context-manager or close() behavior is defined.

## Method Map:
graph LR
    A[Instantiate StartupError] --> B[raise StartupError]
    B --> C[except StartupError as e]
    C --> D[inspect e.args / str(e)]
    C --> E[handle: log / abort startup / return non-zero exit]

(Note: StartupError defines no methods beyond those inherited from Exception / BaseException.)

## Raises:
- StartupError.__init__ itself does not raise exceptions beyond what Exception.__init__ may raise (which in normal use will not raise). Constructing a StartupError with arbitrary objects will simply store them in args; no validation is performed by StartupError.

## Example:
- Raising to signal a fatal startup problem:
    raise StartupError("database schema validation failed: missing table 'users'")

- Catching at top-level startup code:
    try:
        initialize_app()
    except StartupError as e:
        # e.args contains the message(s); str(e) yields a readable message
        print("Startup failed:", e)
        sys.exit(1)

## `datasette.utils.__init__.derive_named_parameters` · *function*

## Summary:
Determine the named parameters referenced by an SQL statement by running EXPLAIN and parsing the result; if EXPLAIN cannot be executed, return the raw regex-based matches as a fallback.

## Description:
This asynchronous helper inspects an SQL string to discover named parameters used in the statement. It first constructs an EXPLAIN <sql> statement (after trimming whitespace and a trailing semicolon) and attempts to execute it against the provided async database object. If EXPLAIN succeeds, the function examines each returned row and collects values from the row's "p4" column for rows whose "opcode" equals "Variable", removing any leading ":" from those p4 values. If the EXPLAIN execution raises sqlite3.DatabaseError, the function falls back to returning the results of a module-level regular-expression scan of the SQL (the raw regex matches).

Known callers:
- None available in the provided context. Search the repository for derive_named_parameters to locate call sites in your codebase.

Why this is a separate function:
- Parsing EXPLAIN output is more accurate than a regex-only approach. Encapsulating EXPLAIN-based extraction plus a conservative regex fallback avoids duplicating this logic and centralizes the normalization behavior for callers.

## Args:
    db (Any): An awaitable/async-capable database object exposing an awaitable execute(sql, params) method. The execute method must accept:
        - sql (str): SQL string to execute (here, the EXPLAIN statement).
        - params (Mapping[str, Any]): a mapping of parameter names to values (this function passes {p: None for p in possible_params}).
      If EXPLAIN succeeds, execute() must return an iterable of row-like mappings indexable by string keys (at least "opcode" and "p4").
    sql (str): SQL statement to inspect. The function will call sql.strip().rstrip(";") prior to building the EXPLAIN statement; therefore sql must be a text string.

Interdependencies:
    - Relies on a module-level regular expression named _re_named_parameter for the fallback extraction. The exact form and behavior of that regex are defined elsewhere in the module; this function returns those raw matches when EXPLAIN fails.

## Returns:
    list[str]: A list of parameter identifiers discovered in the SQL.
    - If EXPLAIN executes successfully: returns a list of the p4 values for rows where row["opcode"] == "Variable", with leading ":" removed from each p4 via .lstrip(":").
    - If EXPLAIN raises sqlite3.DatabaseError: returns the raw matches from _re_named_parameter.findall(sql).
    - If no parameters are found by either method, returns an empty list.
Notes:
    - The function preserves the order and duplicates as they appear in the EXPLAIN output or the regex matches; callers who require unique names or a specific ordering should deduplicate or reorder the result themselves.

## Raises:
    - sqlite3.DatabaseError is caught inside the function and does not propagate.
    - Any other exception raised (for example, due to an adapter that does not implement the expected execute interface, or if sql is not a str and lacks the used string methods) will propagate to the caller.

## Constraints:
Preconditions:
    - sql must be a str (or behave like a str for strip/rstrip calls).
    - db.execute must be awaitable and accept (sql_string, params_mapping).
    - For the EXPLAIN path to be useful, the rows returned by db.execute must be mappings containing at least the keys "opcode" and "p4".

Postconditions:
    - The returned value is a list of strings representing the discovered parameter identifiers (normalized for the EXPLAIN path).
    - No persistent changes are made to the database by this function (EXPLAIN is a read-only operation in SQLite).

## Side Effects:
    - Executes a read-only EXPLAIN <sql> statement against the provided database via db.execute. This may access database schema/metadata but is not intended to modify persistent data.
    - No file, network, stdout, or global-state side effects are performed by the function itself.

## Control Flow:
flowchart TD
    Start[Start: receive db, sql] --> Normalize[Normalize SQL: trimmed_sql = sql.strip().rstrip(";")]
    Normalize --> RegexFind[Compute possible_params = _re_named_parameter.findall(sql)]
    RegexFind --> BuildExplain[Build explain = "explain " + trimmed_sql]
    BuildExplain --> TryExec[Try: await db.execute(explain, {p: None for p in possible_params})]
    TryExec -->|Success| ParseRows[Iterate results rows]
    ParseRows --> CheckOpcode{row["opcode"] == "Variable?"}
    CheckOpcode -->|Yes| Collect[Collect row["p4"].lstrip(":")]
    CheckOpcode -->|No| Skip[Skip row]
    Collect --> ParseRows
    ParseRows --> ReturnExplain[Return collected names list]
    TryExec -->|sqlite3.DatabaseError| ReturnFallback[Return possible_params (regex fallback)]
    ReturnExplain --> End[End]
    ReturnFallback --> End

## Examples:
Typical async usage (normalization of EXPLAIN result):

    async def example(db):
        sql = "SELECT * FROM items WHERE id = :id AND cat = :cat"
        params = await derive_named_parameters(db, sql)
        # When EXPLAIN succeeds, params will be like ['id', 'cat'] (leading ':' removed)
        return params

Handling fallback and normalizing fallback results:

    async def robust_example(db):
        sql = "SELECT * FROM unknown_table WHERE x = :x"
        params = await derive_named_parameters(db, sql)
        # If EXPLAIN failed, params are the raw regex matches from _re_named_parameter
        # Normalize to remove any leading ":" if present:
        normalized = [p.lstrip(":") for p in params]
        # Deduplicate while preserving order if desired:
        seen = set()
        unique = [p for p in normalized if not (p in seen or seen.add(p))]
        return unique

## `datasette.utils.__init__.add_cors_headers` · *function*

## Summary:
Mutates a provided header mapping to add three CORS-related HTTP response headers that enable broad cross-origin access and expose the Link header.

## Description:
This small utility sets three HTTP headers on the provided headers mapping:
- Access-Control-Allow-Origin => "*"
- Access-Control-Allow-Headers => "Authorization"
- Access-Control-Expose-Headers => "Link"

Known callers within the codebase:
- No specific call-sites were retrieved at the time of this documentation generation. Typical callers are request/response builders, middleware, or view functions that assemble HTTP response headers before sending a response.

Why this logic is extracted:
- Centralizes the exact CORS header values used by the application so the same policy can be applied consistently from many places without duplicating literal header keys/values.
- Keeps response-building code cleaner by delegating header population to a dedicated helper responsible only for CORS header composition.

## Args:
    headers (MutableMapping[str, str]):
        A mutable mapping-like object that supports item assignment (implements __setitem__).
        Typical concrete types: built-in dict, frameworks' header containers (objects that behave like dict for assignment).
        The function does not validate key or value types beyond relying on mapping behavior; keys and values are set as strings.

    Interdependencies:
        - The caller is responsible for providing a mutable mapping. If an immutable mapping (e.g., tuple of pairs) or an object without __setitem__ is provided, assignment will fail.

## Returns:
    None

    Behavior:
        - The function returns nothing; its effect is entirely via mutation of the provided headers mapping.
        - After successful execution, the mapping will contain (possibly overwriting existing entries) the three header keys with the exact string values listed above.

## Raises:
    TypeError:
        - Raised indirectly if the provided headers object does not support item assignment (no __setitem__). The function itself does not explicitly raise, but attempting headers["..."] = "..." will propagate the underlying exception (commonly TypeError or AttributeError for incompatible objects).

    Any exception raised by the mapping's __setitem__ implementation will propagate to the caller; the helper does not catch exceptions.

## Constraints:
    Preconditions:
        - headers must be a mutable mapping-like object where assignment to a string key is supported.
        - Caller expects header values to be plain strings; non-string value objects will be stored as-is (mapping implementations may coerce or reject).

    Postconditions:
        - headers contains at least:
            - "Access-Control-Allow-Origin": "*"
            - "Access-Control-Allow-Headers": "Authorization"
            - "Access-Control-Expose-Headers": "Link"
        - Any previous values for those keys are overwritten.
        - No other keys are modified.

## Side Effects:
    - Mutates the passed-in headers mapping in-place.
    - No I/O, network activity, global state mutation, database access, or external service calls are performed.
    - No asynchronous behavior.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckHeaders{headers supports __setitem__?}
    CheckHeaders -- yes --> SetOrigin[Set Access-Control-Allow-Origin = "*"]
    SetOrigin --> SetAllowHeaders[Set Access-Control-Allow-Headers = "Authorization"]
    SetAllowHeaders --> SetExpose[Set Access-Control-Expose-Headers = "Link"]
    SetExpose --> End([Return None])
    CheckHeaders -- no --> Error[Underlying mapping raises TypeError/AttributeError]
    Error --> End

## Examples:
- Typical usage scenario (described):
    1. A response-building function constructs or receives a mutable headers mapping (for example, an empty dict or a framework-specific headers container).
    2. The response builder calls this helper and passes that mapping as the argument.
    3. After the call, the mapping contains the three CORS headers. The response is then sent with those headers included.

- Example outcome (described without raw source):
    Given an initially empty mapping provided by the caller, after invoking the helper the mapping will contain:
        - Access-Control-Allow-Origin: *
        - Access-Control-Allow-Headers: Authorization
        - Access-Control-Expose-Headers: Link

- Error handling guidance:
    - If the headers object might be immutable or not support assignment, wrap the call in the caller's try/except and handle TypeError or AttributeError by converting to an appropriate mutable mapping or by constructing a new mapping containing the existing headers plus these three keys.

## `datasette.utils.__init__.TildeEncoder` · *class*

## Summary:
A dict subclass that lazily computes and memoizes a single-byte "tilde-style" encoded string on first access of a missing key.

## Description:
TildeEncoder provides a per-key cache for encoding individual byte-like keys into strings according to three rules implemented in __missing__:
1. If the key is a member of the module-level container _TILDE_ENCODING_SAFE, the encoding is chr(key).
2. Else if the key equals the module-level name _space, the encoding is the single-character string "+".
3. Otherwise the encoding is "~" followed by the uppercase hexadecimal representation of the key, formatted with at least two digits using "{:02X}".format(key).

When a lookup via __getitem__ encounters a key that is not present in the mapping, dict.__getitem__ delegates to __missing__, which computes, stores (self[key] = value), and returns the encoded string. This class centralizes the per-key encoding logic and provides memoization via the mapping interface.

Note: The class expects the module-level names _TILDE_ENCODING_SAFE and _space to be defined and usable for membership and equality tests, respectively. The class does not itself validate key ranges or types beyond relying on the operations used (membership, equality, chr, and integer-formatting).

## State:
- Inherited state: the mapping storage of dict.
  - Keys: any hashable objects; the implementation assumes keys support membership testing against _TILDE_ENCODING_SAFE and equality testing with _space. The code uses chr(key) and integer hex-formatting, so keys that are integers are required for those operations to succeed without raising.
  - Values: str (each mapped value is the encoded representation for that key).

- Class does not declare additional attributes or an __init__; it uses dict.__init__.

- Invariants:
  - For each key k present in the mapping, the value equals the encoding produced by the three-rule logic described in Description.
  - After __missing__ computes and assigns self[k], subsequent self[k] accesses return the same cached value.

## Lifecycle:
- Creation:
  - Instantiate with TildeEncoder() or any standard dict constructor form (e.g., TildeEncoder(mapping), TildeEncoder(**kwargs)). No constructor-specific behavior is defined.

- Usage:
  - Use indexing (encoder[key]) to obtain an encoded string: if key is present, the stored value is returned; if key is absent, __missing__ is invoked to compute, cache, and return the value.
  - Using dict.get(key, default) will not invoke __missing__; it will return default for absent keys and will not mutate the mapping.
  - To populate or modify the cache explicitly, use standard dict methods (assignment, update, clear, pop, del).

- Destruction:
  - No external resources; normal garbage collection applies. Clearing of cached entries uses regular dict APIs.

## Method Map:
flowchart LR
  Request[Caller performs encoder[key]] --> CheckPresent{key in encoder?}
  CheckPresent -- Yes --> ReturnCached[Return cached value]
  CheckPresent -- No --> MissingInvoked[dict.__missing__ invoked]
  MissingInvoked --> SafeCheck{key in _TILDE_ENCODING_SAFE?}
  SafeCheck -- True --> UseChr[res = chr(key)]
  SafeCheck -- False --> SpaceCheck{key == _space?}
  SpaceCheck -- True --> UsePlus[res = "+"]
  SpaceCheck -- False --> UseHex[res = "~" + "{:02X}".format(key)]
  UseChr --> Store[store self[key] = res]
  UsePlus --> Store
  UseHex --> Store
  Store --> ReturnCached

## Raises:
The method implementation has no explicit raise statements, but the operations performed can raise standard Python exceptions depending on inputs or module-level names:
- NameError: if _TILDE_ENCODING_SAFE or _space are not defined at runtime when accessed.
- TypeError:
  - If key is unhashable (assignment self[key] = res will raise).
  - If membership test `key in _TILDE_ENCODING_SAFE` or equality `key == _space` raises due to incompatible types.
  - If "{:02X}".format(key) is used on a value that cannot be formatted with the integer hexadecimal format specifier.
- ValueError:
  - If chr(key) is invoked with an integer outside the valid Unicode code point range for chr in this interpreter.
Any exception raised by these operations will propagate to the caller.

## Example:
- Create an empty encoder:
  encoder = TildeEncoder()

- Lookup that triggers computation and caching:
  value = encoder[some_key]  # If some_key absent: computes using the three-rule logic, stores encoder[some_key] = value, returns value

- Accessing a cached key:
  same = encoder[some_key]  # Returns the previously stored value without recomputation

Implementation hint:
- Reimplement by subclassing dict and providing __missing__(self, key) that:
  1) checks membership in _TILDE_ENCODING_SAFE and sets res = chr(key) if true,
  2) elif key == _space: res = "+",
  3) else: res = "~{:02X}".format(key),
  4) stores self[key] = res and returns res.

### `datasette.utils.__init__.TildeEncoder.__missing__` · *method*

## Summary:
Compute and cache the tilde-style encoded string for a missing byte key on the mapping, then return that string so subsequent lookups use the cached value.

## Description:
This method implements dict.__missing__ for TildeEncoder. It is called automatically when code accesses self[b] and key b is absent. The method determines the encoded string for a single byte, stores it in the mapping under key b, and returns it. It centralizes per-byte encoding logic and provides memoization so higher-level encoding loops can repeatedly index the encoder without recomputing formatting.

Behavioral precedence:
- Membership in `_TILDE_ENCODING_SAFE` is checked first. If b is in that container, chr(b) is returned.
- Only if b is not in `_TILDE_ENCODING_SAFE` is b compared to `_space` to decide whether to return "+".
- If neither case applies, the byte is formatted as "~{:02X}" (uppercase hex, zero-padded to at least two digits).

Why a separate method:
- Encapsulates encoding rules for a single byte in one place.
- Enables lazy computation plus memoization via the mapping interface.
- Keeps callers simple: they index the encoder for each byte and receive the final string.

## Args:
    b (int): The key to encode. Intended to be an integer representing a single byte (commonly 0..255). b must be hashable (usable as a dict key) and usable in membership tests against `_TILDE_ENCODING_SAFE` and equality checks with `_space`.

## Returns:
    str: The encoded string for b. Exactly one of:
        - chr(b) if b is in `_TILDE_ENCODING_SAFE` (single-character Unicode string).
        - "+" if b == _space and b is not in `_TILDE_ENCODING_SAFE`.
        - "~" + uppercase-hex of b zero-padded to at least two digits using "{:02X}".format(b) otherwise (examples: b==1 -> "~01", b==255 -> "~FF", b==256 -> "~100").
    The returned value is stored in self[b] before being returned.

## Raises:
    The method itself contains no explicit raise statements; the following exceptions can be raised by the built-in operations used here when preconditions are violated:
    - TypeError:
        * If b is unhashable and cannot be used as a dict key (raised when assigning self[b] = ...).
        * If membership testing `b in _TILDE_ENCODING_SAFE` or equality comparison `b == _space` raises TypeError for the given b or container implementation.
        * If formatting with "{:02X}".format(b) cannot operate on b because it does not support integer-formatting rules.
    - ValueError:
        * If chr(b) is called with an integer outside the valid Unicode code point range for chr in this Python runtime.

## State Changes:
    Attributes READ:
        - Module-level `_TILDE_ENCODING_SAFE` (membership tested).
        - Module-level `_space` (equality tested).
    Attributes WRITTEN:
        - self[b] is assigned the computed encoding string (this is the only mutation performed by this method).

## Constraints:
    Preconditions:
        - The TildeEncoder instance is a writable mapping (it subclasses dict).
        - Module-level `_TILDE_ENCODING_SAFE` and `_space` are defined and support membership and equality operations respectively.
        - b should ordinarily be an integer representing a single byte (0..255). Non-integer or out-of-range values are unsupported and may raise the built-in exceptions listed above.
    Postconditions:
        - After the call, self[b] exists and equals the string returned.
        - Future accesses to self[b] will return the cached string without recomputation.

## Side Effects:
    - Mutates only the TildeEncoder mapping by storing self[b] = <encoded string>.
    - No I/O, network access, or mutation of other global state (only reads of module-level constants).

## Examples and edge cases:
    - Normal use:
        If `_space == 32` and `_TILDE_ENCODING_SAFE` contains 65:
            * Accessing self[65] (when absent) -> stores and returns "A" (chr(65)).
            * Accessing self[32] (when absent) -> stores and returns "+".
            * Accessing self[10] (newline, not safe) -> stores and returns "~0A".
    - Precedence example:
        If `_space == 32` but `_TILDE_ENCODING_SAFE` also contains 32, then accessing self[32] returns chr(32) (" ") and not "+" because membership is evaluated before the equality check.

## `datasette.utils.__init__.tilde_encode` · *function*

## Summary:
Encodes a Python Unicode string by UTF-8 encoding it to bytes and mapping each byte to a string fragment produced by a per-byte helper, producing a single concatenated string (example: "/foo/bar" -> "~2Ffoo~2Fbar").

## Description:
- What it does: Converts the input str to UTF-8 bytes, iterates over those bytes (as integer values 0..255), calls a module-local helper named _tilde_encoder for each byte, and concatenates the returned fragments to produce the final encoded string.
- Why this function exists separately: It centralizes the high-level flow (string -> UTF-8 bytes -> per-byte encoding -> join) so callers need only pass a Unicode string. The byte-to-string mapping policy is delegated to _tilde_encoder so that the byte-level escaping rules are defined in one place and can be changed without altering callers.
- Known callers: None were found in the supplied source excerpt. In practice this function is typically used where path segments or identifiers must be represented with a reversible ASCII-safe encoding of arbitrary Unicode.

## Args:
    s (str): Input text to encode. Must be a Python str (Unicode). The function calls s.encode('utf-8') internally.

Notes:
- If a non-str is passed, the call to s.encode('utf-8') will raise an AttributeError (or a different error if the object provides a non-standard encode implementation).

## Returns:
    str: The concatenation of the string fragments returned by _tilde_encoder for each UTF-8 byte of the input. Specific properties depend on _tilde_encoder's behavior:
      - If _tilde_encoder returns ASCII-only fragments for every byte, the overall return value will be ASCII-only.
      - If the input is the empty string (""), s.encode('utf-8') produces an empty bytes sequence, the generator produces no fragments, and the function returns "" (empty string).

Examples:
  - For a typical tilde-escaping helper (see recommended contract below):
      tilde_encode("/foo/bar") -> "~2Ffoo~2Fbar"
      tilde_encode("A") -> "A"
      tilde_encode("✓") -> "~E2~9C~93"  (UTF-8 bytes E2 9C 93)
  - Empty string:
      tilde_encode("") -> ""

## Raises:
- AttributeError: If the caller passes an object without a compatible .encode('utf-8') method (e.g., None), an AttributeError is raised at s.encode('utf-8').
- NameError: If _tilde_encoder is not defined in the module at call time, a NameError is raised when attempting to call it.
- TypeError: If _tilde_encoder returns a non-str for any byte, the str.join call will raise a TypeError when attempting to join non-string fragments.
- Any exception raised by _tilde_encoder for a particular byte (these exceptions propagate up unchanged).

## Constraints:
Preconditions:
  - s must be a Python str (or provide a compatible encode method).
  - A callable named _tilde_encoder must exist in the same module and accept each byte as an int (0..255).

Postconditions:
  - The call returns the joined string of fragments produced by the helper for each UTF-8 byte of the input.
  - No global state is changed by this function.

## Side Effects:
  - None intrinsic to this function: it performs no I/O and does not mutate module-level state. Any side effects originate from _tilde_encoder if that helper performs side effects.

## Control Flow:
flowchart TD
    Start --> EncodeUTF8
    EncodeUTF8 --> BytesSequence
    BytesSequence --> ForEachByte
    ForEachByte --> CallHelper[_tilde_encoder(byte:int)]
    CallHelper -->|returns str fragment| AppendFragment
    AppendFragment --> NextByte
    NextByte -->|more bytes| ForEachByte
    NextByte -->|no more bytes| JoinFragments
    JoinFragments --> ReturnResult
    ReturnResult --> End

## Behavior contract for _tilde_encoder (required to reimplement the overall behavior)
To reimplement tilde_encode faithfully you must also implement a helper named _tilde_encoder with this exact calling convention and return contract:
- Signature: _tilde_encoder(b: int) -> str
  - b is an integer in the range 0..255 (each element yielded by iterating over the bytes object).
- Contract:
  - Must return a Python str for every b.
  - Recommended reversible behavior (matches the example in the function docstring):
      - For a small set of "safe" ASCII bytes, return chr(b) (a one-character string).
        Recommended safe set: ASCII letters (A-Z, a-z), digits (0-9), hyphen (0x2D), underscore (0x5F), period (0x2E). Do NOT include '/' (0x2F) in the safe set — the example encodes it.
      - For all other byte values return "~" + the two-digit uppercase hexadecimal representation of b (format(b, "02X")), e.g., 47 -> "~2F".
      - Ensure "~" itself (0x7E) is encoded as "~7E" to avoid ambiguity.
  - Under this recommended contract, the output of tilde_encode is ASCII-only and reversible: concatenating the bytes decoded from "~XX" escapes and literal characters and decoding as UTF-8 reconstructs the original string.

## Examples (end-to-end)
1) Typical usage with recommended helper:
    # assume _tilde_encoder implemented per contract
    tilde_encode("/foo/bar")  # -> "~2Ffoo~2Fbar"

2) Non-ASCII characters:
    tilde_encode("✓")         # -> "~E2~9C~93"   (E2 9C 93 are UTF-8 bytes)

3) Error handling example:
    try:
        result = tilde_encode(None)
    except AttributeError:
        # NoneType has no .encode method
        handle_input_error()

Notes:
- The function itself is a thin, strict wrapper around byte-level mapping; any guarantees about the character set or reversibility of outputs must be provided by the implementation of _tilde_encoder. The documentation above defines the precise contract you should implement for that helper to obtain the behavior demonstrated in the function's example.

## `datasette.utils.__init__.tilde_decode` · *function*

## Summary:
Decode strings that use tilde (~) as an alternative percent-encoding marker into their normal characters, while preserving any literal percent (%) characters.

## Description:
This utility converts tilde-encoded percent sequences (e.g., "~2F") into their decoded characters by treating "~" like "%" for percent-decoding, without accidentally decoding existing literal "%" characters that should remain unchanged.

Behavior in steps:
1. Generates a random masking token (secure hex string) to temporarily replace any existing "%" characters in the input so they won't be interpreted as percent-escapes.
2. Replaces every "~" with "%" to turn tilde-encoded sequences into standard percent-encoded sequences.
3. Calls urllib.parse.unquote_plus to perform percent-decoding (this also converts '+' to space).
4. Restores the original "%" characters by replacing the masking token back to "%".

Known callers:
    - No direct callers were identified in the provided project context. Typical callers in applications include URL routing/path decoding, REST API path segment parsing, or any subsystem that needs to accept tilde-based percent-encoding from user input or URLs.

Why this is a separate function:
    - Centralizes the non-standard tilde-as-percent decoding logic and the masking/unmasking required to preserve literal "%" characters.
    - Avoids duplicated subtle logic and prevents bugs where literal "%" would be misinterpreted as an encoding marker if callers simply replaced "~" with "%" and decoded.

## Args:
    s (str): The input text containing tilde-encoded sequences and possibly literal '%' characters.
        - Expected type: str (the function uses .replace(), so any object implementing compatible replace semantics may work, but type annotation and intended use are str).
        - Allowed values: any text. Empty string is allowed.
        - Interdependencies: none.

## Returns:
    str: The decoded string with the following guarantees:
        - Every occurrence of "~XX" (where XX are hex digits) will be treated as "%XX" and decoded accordingly by urllib.parse.unquote_plus.
        - '+' characters in the input are decoded to spaces (behavior inherited from unquote_plus).
        - Literal '%' characters present in the original input are preserved and remain as '%' in the output.
        - If tilde sequences are not valid percent-encodings (e.g., "~ZZ"), decoding behavior is delegated to urllib.parse.unquote_plus; the function does not validate hex digits itself.

    Examples of possible return values:
        - "~2Ffoo~2Fbar" -> "/foo/bar"
        - "%2F" -> "%2F" (literal percent preserved)
        - "hello+world" -> "hello world" (plus -> space)
        - "" -> "" (empty input returns empty output)

## Raises:
    - AttributeError: If s is not a string-like object and does not support .replace (for example, passing None or an int will typically raise).
    - Other exceptions: Very unlikely for typical string inputs. The function does not explicitly raise other exceptions; any exception would originate from underlying functions (e.g., unexpected behavior from secrets.token_hex or urllib.parse.unquote_plus), but with normal usage these do not raise.

## Constraints:
Preconditions:
    - Caller should pass a str (or compatible object with .replace). The function assumes the input uses "~" as an encoding marker if encodings are present.
    - Do not rely on this function to validate percent-escape correctness — invalid percent-escapes are handled by urllib.parse.unquote_plus's behavior.

Postconditions:
    - The returned value is a str.
    - Literal '%' characters originally in the input are retained.
    - All tilde-encoded percent sequences have been decoded per urllib.parse.unquote_plus semantics.

Collision risk:
    - The implementation uses a random masking token (secrets.token_hex(16) → a 32-character hex string) to temporarily replace "%" characters. If the random token happens to already appear in the input string, that occurrence will be treated as if it were an original '%' and will be converted to '%' on output — i.e., an accidental collision will incorrectly change that substring. The collision probability is extremely small (2^−128-ish for a 16-byte token), but it is a theoretical possibility. Callers that must be completely collision-proof should instead implement a deterministic escaping scheme or use a two-pass approach that chooses a token guaranteed not to appear in the input.

## Side Effects:
    - None observable: no I/O, no mutation of global state, and no external network calls. The only side effect is local CPU/time used to create a small random token and perform string operations.

## Control Flow:
flowchart TD
    Start([Start: receive s])
    Start --> GenToken[Generate temp token via secrets.token_hex(16)]
    GenToken --> MaskPercent[Replace '%' in s with temp token]
    MaskPercent --> ReplaceTilde[Replace '~' with '%']
    ReplaceTilde --> Unquote[Call urllib.parse.unquote_plus on modified string]
    Unquote --> RestoreToken[Replace temp token back to '%']
    RestoreToken --> Return[Return final decoded string]
    Return --> End([End])

## Examples:
1) Basic usage — path segment decoding
    Input: "~2Fusers~2Falice"
    Output: "/users/alice"
    Use case: decoding path components where "~" was used instead of standard percent-encoding.

2) Preserving literal percent characters
    Input: "version%3A1~2Fbeta"
    Process:
        - '%' is masked so "%3A" remains literal
        - "~2F" decodes to '/'
    Output: "version%3A1/beta"

3) Plus sign handling
    Input: "first+last~20name"
    Behavior:
        - '+' becomes a space
        - "~20" becomes a space as well (if present)
    Output: "first last name"

4) Edge-case: non-string input
    Input: None
    Behavior: Raises AttributeError because NoneType has no 'replace' method.

Notes:
    - If you need to preserve '+' characters (not convert them to spaces), perform a pre-processing step (e.g., replace '+' with '%2B') before calling this function and then decode afterwards.
    - This function is intended for safe convenience in applications that have adopted "~" as an alternative percent-encoding marker; prefer standard percent-encoded inputs where possible.

## `datasette.utils.__init__.resolve_routes` · *function*

## Summary:
Finds the first route whose regular-expression pattern matches the start of the given path and returns the match object together with the associated view object; if none match, returns (None, None).

## Description:
This utility iterates an ordered sequence of route entries (pattern, view) and returns the first successful pattern match for the supplied path. Typical callers prepare a list of routes (each a two-tuple of a compiled regular-expression and an arbitrary "view" object) and use this function to resolve which view should handle an incoming request path.

Known callers within the codebase:
- No direct callers were found in the provided snippet context. In typical applications this function is invoked from request-dispatching or routing code just before invoking an associated view/handler.

Why this is extracted:
- Encapsulates the simple, reusable logic of scanning ordered routes and returning the first match; keeps routing/dispatch code concise and isolates the matching policy (first match wins) so it can be tested and changed independently.

## Args:
    routes (iterable[tuple[re.Pattern, Any]]):
        An ordered iterable of two-item tuples. Each item must be (regex, view) where:
        - regex: a regular-expression object exposing a .match(path) method (typically an object returned by re.compile()).
        - view: an opaque object associated with the pattern (commonly a callable/function, class, or descriptor).
        The function iterates the iterable in order; it expects each element to unpack into exactly two values.
    path (str):
        The input path string to match against each regex. Should be a str (not bytes) compatible with the compiled pattern used in routes.

Notes on interdependencies:
- The function assumes regex.match(path) is a valid call. If patterns were compiled for bytes or the path is an incompatible type, a TypeError may be raised by the underlying regex engine.

## Returns:
    tuple[re.Match|None, Any|None]:
        - If a pattern matches: returns (match_obj, view) where match_obj is the re.Match returned by regex.match(path) and view is the corresponding view object from the matched route tuple.
        - If no pattern matches: returns (None, None).
    Additional details:
        - The match object corresponds to the first route (in iteration order) whose regex.match(path) is truthy; later routes are not consulted.
        - Because .match is used (not .search), matching is attempted from the start of the string according to the regex semantics.

## Raises:
    - ValueError / TypeError / AttributeError:
        - ValueError can occur implicitly if an element of routes does not unpack into two items.
        - AttributeError may occur if an element's first item does not provide a .match attribute.
        - TypeError may be raised by the regex engine if the provided path type is incompatible (for example using bytes patterns against str).
    These exceptions are not explicitly raised by the function but are possible runtime errors propagated from improper input shapes or incompatible pattern/path types.

## Constraints:
Preconditions:
    - routes must be an iterable of 2-tuples (pattern, view). Each pattern must implement .match(path).
    - path must be an appropriate string type that the compiled regex patterns expect.

Postconditions:
    - The returned view is the first view whose corresponding pattern matched the provided path, or None if none matched.
    - No mutation of routes or path occurs; the function is pure with respect to inputs.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state. It only calls .match on pattern objects and returns values.

## Complexity:
    - Time: O(N) in the number of route entries in the worst case (stops early on the first match).
    - Space: O(1) additional space.

## Control Flow:
flowchart TD
    Start --> Iterate[Iterate routes in order]
    Iterate --> TryMatch[Call regex.match(path)]
    TryMatch --> IsMatch{match is not None?}
    IsMatch -->|Yes| ReturnMatch[Return (match, view)]
    IsMatch -->|No| Next[Continue to next route]
    Next --> Iterate
    Iterate --> EndReturn[Finished all routes]
    EndReturn --> ReturnNone[Return (None, None)]

## Examples (prose):
- Given routes prepared in order, e.g. first a route for the API root and then a fallback route, calling this function with an incoming request path returns the match and the specific view that should handle that request. The caller should then check the returned match: if match is not None, it can extract capture groups from match and call/present the associated view; if match is None, the caller should handle the "no route matched" case (for example by returning a 404 response).

- Error handling guidance: upstream code that constructs the routes list should ensure each route tuple is well-formed (pattern, view) and that patterns are compiled for the same string type as request paths; otherwise callers should be prepared to catch TypeError/AttributeError/ValueError propagated from this function.

## `datasette.utils.__init__.truncate_url` · *function*

## Summary:
Truncates a URL-like string to a target maximum length for display, inserting a single-character ellipsis (…); if the string ends with a short dot-suffix (1–4 chars with no slash), the function attempts to preserve that suffix, placing the ellipsis before the dot.

## Description:
This small utility centralizes a display-oriented truncation policy used when long URLs or path-like strings must be shortened for UI, logs, or summaries. It encapsulates two behaviors:
- Simple truncation: keep the first (length - 1) characters and append a single-character ellipsis (…).
- Extension-preserving truncation: when the input ends with a short suffix that looks like a file extension (1–4 characters, no slash), preserve that suffix and place the ellipsis immediately before the dot (resulting in "….[ext]").

Known callers within the repository:
- No direct call-sites were discovered during inspection for this task. The function is intended for use by presentation-layer code that needs consistent, compact string formatting.

Why this is a separate function:
- Enforces a single, testable truncation policy across the codebase,
- Makes it easy to update the truncation rules in one place,
- Avoids duplicating subtle behaviors (such as extension detection) in multiple view/template locations.

## Args:
    url (str):
        The input value to truncate. Must be a sequence supporting len() and slicing (typically a Python str). Passing None or a non-sequence will raise a TypeError when the function attempts len() or slicing.
    length (int or any falsey value):
        The requested maximum length (number of characters) for the returned string, including any ellipsis or preserved extension.
        - If length is falsey (e.g., None, 0, False), the function returns url unchanged (no truncation).
        - When truthy, length is compared against len(url). If len(url) <= length the original string is returned unchanged.
        - The implementation expects an integer when truncation is required; non-integer truthy values may cause TypeError during slicing.
        Important interdependencies:
        - If length is not comparable to an int (for example, a string), the comparison len(url) <= length will raise a TypeError before any truncation is attempted.
        - If length is a float but comparison succeeds, using length as a slice index later will raise a TypeError.

## Returns:
    str:
        - If length is falsey or len(url) <= length: returns url unchanged.
        - If truncation is needed and the extension-preserving branch is taken (final dot + suffix of length 1–4 with no slash), returns:
            rest[: length - 1 - len(ext)] + "…." + ext
          where rest is the portion of url before the final dot and ext is the suffix after it.
        - Otherwise (no short extension detected), returns:
            url[: length - 1] + "…"
        Notes on length of the returned string:
        - Non-extension branch: the returned string length is exactly length (prefix length L-1 plus one-character ellipsis).
        - Extension-preserving branch: when the computed slice index (length - 1 - len(ext)) is non-negative, the returned string length is length + 1 (one character longer than requested). This is due to the code concatenating a two-character sequence "…." (ellipsis + dot) plus the extension length; with a non-negative slice the calculation yields L+1.
        - If (length - 1 - len(ext)) is negative, Python's negative slicing semantics apply and the returned length depends on the original rest value; it may be larger than length and is generally unpredictable relative to length.
        - Therefore, the function does not always guarantee the returned string will be no longer than length when the extension-preserving branch triggers.

## Raises:
    TypeError:
        - If length is a value that cannot be compared to an integer (e.g., a string), the initial comparison len(url) <= length will raise TypeError.
        - If length is truthy but not an integer (e.g., a float), slicing operations that use length as an index (url[:length-1]) will raise TypeError.
        - If url is not a sequence (e.g., None), len(url) raises TypeError.
    (The function contains no explicit raise statements; these are runtime errors from built-in operations.)

## Constraints:
Preconditions:
    - Prefer passing url as a str and length as an int (or a falsey value to disable truncation).
    - To avoid surprising results with the extension-preserving branch, callers should ensure length is an integer and typically length >= len(extension) + 1.
Postconditions:
    - The function returns a str.
    - If the non-extension branch runs, the returned value length == length.
    - If the extension-preserving branch runs:
        * If length - 1 - len(ext) >= 0, the returned length == length + 1.
        * If length - 1 - len(ext) < 0, the returned length depends on the original string and Python negative-slice semantics (not constrained to <= length).

## Side Effects:
    - None. Purely functional string manipulation with no I/O or external state changes.

## Control Flow:
flowchart TD
    A[Start] --> B{length is falsey OR len(url) <= length?}
    B -- Yes --> C[Return url unchanged]
    B -- No --> D[Split url by last '.' into bits = url.rsplit(".", 1)]
    D --> E{bits length == 2 AND 1 <= len(bits[1]) <= 4 AND '/' not in bits[1]?}
    E -- Yes --> F[rest, ext = bits; compute i = length - 1 - len(ext)]
    F --> G{ i >= 0 ? }
    G -- Yes --> H[Return rest[:i] + "…." + ext  (result length = length + 1)]
    G -- No --> I[Return rest[:i] + "…." + ext  (negative slice; length unpredictable)]
    E -- No --> J[Return url[:length-1] + "…"  (result length = length)]
    H --> K[End]
    I --> K[End]
    J --> K[End]

## Examples:
- No truncation (falsey length or long limit):
    - url = "https://example.com/path", length = 30
    - Returns original string unchanged.

- Non-extension truncation (exact length):
    - url = "https://example.com/very/long/path"
    - length = 15
    - Returns url[:14] + "…" e.g. "https://exampl…"
    - Returned length is exactly 15.

- Extension-preserving truncation (common case, but returns length+1):
    - url = "https://example.com/very/long/filename.csv"  (ext = "csv", len=3)
    - length = 20
    - Computed slice index: 20 - 1 - 3 = 16 (non-negative)
    - Returned string length = 20 + 1 = 21; example: rest[:16] + "…." + "csv" => one-character longer than requested.

- Small length and extension branch (negative slice, unpredictable length):
    - url = "filename.csv" (rest="filename", ext="csv", len(ext)=3)
    - length = 2
    - Computed slice index: 2 - 1 - 3 = -2 -> rest[:-2] yields "filena"
    - Result = "filena" + "…." + "csv" (much longer than length 2). This demonstrates that small length values can produce unexpectedly long results when a short extension is present.

- Invalid types:
    - url = "someurl", length = "10" (string)
    - The comparison len(url) <= length raises TypeError.
    - url = "someurl", length = 10.5 (float)
    - The comparison len(url) <= length may succeed, but using length as a slice index later will raise TypeError.

Caller recommendations:
    - Validate inputs before calling: ensure url is a string and length is an integer (or falsey).
    - If you require a strict guarantee that the returned string will not exceed the requested length, avoid relying on this function when the input may have a short dot-suffix; either pre-strip or detect extensions and adjust length accordingly, or use a more predictable truncation strategy.
    - For predictable behavior with preserved extensions, ensure length is an integer and length - 1 - len(extension) >= 0 (i.e., length >= len(extension) + 1); even then, be aware the extension-preserving branch returns one character longer than the requested length due to the "…." insertion.

