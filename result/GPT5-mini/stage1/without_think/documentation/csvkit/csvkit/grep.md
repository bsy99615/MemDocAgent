# `grep.py`

## `csvkit.grep.FilteringCSVReader` · *class*

*No documentation generated.*

### `csvkit.grep.FilteringCSVReader.__init__` · *method*

## Summary:
Initialize a FilteringCSVReader instance: attach the underlying row iterator, optionally consume and store the header row as column_names, record matching flags, and normalize user-supplied patterns into predicate callables stored on the instance.

## Description:
This constructor is invoked when a FilteringCSVReader object is instantiated — typically at the start of a CSV filtering pipeline, before any iteration over rows begins. At construction time it performs two responsibilities that must occur once per reader:

- Optionally consumes the first row from the provided reader to treat it as a header (column names) and stores it on the instance.
- Normalizes the caller-supplied patterns into a uniform dictionary of one-argument predicate callables via standardize_patterns, storing that mapping on the instance for use during row testing.

Separating this initialization logic into its own method (the constructor) keeps header handling and pattern normalization centralized and performed only once, rather than repeating that logic during iteration or row testing.

Known callers / lifecycle:
- Callers are instantiators of FilteringCSVReader (code that wraps an existing CSV row iterator with filtering behavior). This occurs during setup of a filtering step, before calls to iter() / next() on the FilteringCSVReader.

Why this is a distinct method:
- It must run exactly once when the reader is created to set up state (consume header row if requested and prepare predicate functions). Inlining this logic in iteration or test_row would cause repeated work or require extra guards; placing it in __init__ ensures a clear initialization phase.

## Args:
    reader (iterator[Sequence[str]]):
        An iterator or other object supporting the iterator protocol that yields CSV rows (typically sequences like list or tuple of column values). The constructor stores this as self.reader and may call next(reader) once if header is True.
    patterns (mapping or iterable):
        User-supplied pattern specifications in one of the forms accepted by standardize_patterns:
        - Preferred: mapping of column identifier -> pattern spec (column identifier may be a column name or integer index).
        - Alternate: iterable/sequence of pattern specs (positional).
        Pattern specs may be callables, regex-like objects, or plain values; falsy values are ignored. See csvkit.grep.standardize_patterns for full semantics and examples.
    header (bool, optional, default=True):
        If True, the constructor consumes the next item from reader and assigns it to self.column_names. If False, the reader is left unconsumed and self.column_names remains None (or the class-level default).
    any_match (bool, optional, default=False):
        When True, test_row will accept a row if any of the column predicates match; when False, all predicates must match (this flag is stored on self.any_match).
    inverse (bool, optional, default=False):
        When True, test logic is inverted (matches become rejects and vice versa); stored on self.inverse.

## Returns:
    None
    - As a constructor, it does not return a value. On success it sets up instance attributes (see State Changes).

## Raises:
    StopIteration
        - If header is True and the provided reader is already exhausted (i.e., next(reader) raises StopIteration), the constructor propagates StopIteration. This indicates there is no header row to consume.
    csvkit.exceptions.ColumnIdentifierError
        - May be raised by standardize_patterns if a pattern mapping key that resolves to a numeric column index conflicts with an existing numeric key (name->index collision). The exact message originates from standardize_patterns: "Column %s has index %i which already has a pattern."
    Any exception raised by standardize_patterns or the reader's iteration
        - Other errors (for example, conversion errors inside pattern_as_function invoked by standardize_patterns, or exceptions raised by the reader when producing rows) propagate through the constructor; they are not caught here.

## State Changes:
Attributes READ:
    - self.column_names (read as the first argument passed into standardize_patterns). Note: if header is True the attribute is assigned before being read; if header is False it will be the class-level default (None) and that None is passed through.

Attributes WRITTEN:
    - self.reader: set to the provided reader iterator.
    - self.header: boolean flag recorded from the header argument.
    - self.column_names: assigned to the first row from reader when header is True; left unchanged (class default None) when header is False.
    - self.any_match: set from the any_match argument.
    - self.inverse: set from the inverse argument.
    - self.patterns: set to the dict returned by standardize_patterns(self.column_names, patterns) — a mapping of column identifiers (indices or keys) to one-argument predicate callables.

## Constraints:
Preconditions:
    - reader must be an iterator (support next()); rows yielded should be sequences (e.g., list/tuple) of column values if downstream code expects indexed access.
    - If header is True, caller should ensure reader yields at least one row; otherwise StopIteration will be raised.
    - patterns must be a mapping or iterable in the forms accepted by standardize_patterns (see its documentation). Patterns that are falsy are filtered out by standardize_patterns.
Postconditions:
    - After successful construction:
        * self.reader references the original reader (advanced by one element if header was True).
        * If header was True, self.column_names contains the first row yielded by reader (the header); otherwise it remains None.
        * self.patterns is a dict mapping column indices or original keys to predicate callables suitable for testing cell values.
        * self.any_match and self.inverse reflect the behavior that test_row will apply when filtering rows.
        * The instance is ready for iteration: __iter__ and __next__ will use these prepared attributes.

## Side Effects:
    - Consumes the first element from the provided reader when header=True (mutates reader state / advances the iterator).
    - Calls standardize_patterns(self.column_names, patterns) which constructs callables; standardize_patterns may raise ColumnIdentifierError or other exceptions which will propagate.
    - No file I/O or external network calls are performed by this constructor itself.
    - No mutation of objects outside of the instance other than advancing the provided reader iterator.
    
See also:
    - csvkit.grep.standardize_patterns for the exact normalization rules, accepted pattern formats, returned mapping shape, and the conditions that raise ColumnIdentifierError.

### `csvkit.grep.FilteringCSVReader.__iter__` · *method*

## Summary:
Returns the object itself to satisfy the Python iterator protocol so the instance can be used directly in iteration contexts without creating a separate iterator object. This preserves the instance's internal iteration state.

## Description:
- Known callers and contexts:
    - The built-in iter() function when an iteration is started (for example, implicitly by a for ... in ... loop).
    - Any code that explicitly requests an iterator for this object (e.g., list(filtering_reader), next(iter(filtering_reader)), enumerate(filtering_reader)).
    - This method is invoked at the start of an iteration pipeline stage where the FilteringCSVReader provides filtered rows on demand; it is the entry point that allows the object to participate in Python's iterator protocol.

- Why this logic is a separate method:
    - Implementing __iter__ as a separate method is required by Python's iterator protocol. Returning self makes the FilteringCSVReader both the iterable and its iterator because it maintains iteration state (e.g., the underlying reader position and returned_header flag). Keeping this as a dedicated method clarifies intent and separates the protocol entry point from the iteration mechanics implemented in __next__.

## Args:
    self (FilteringCSVReader): Instance to be used as the iterator. No additional parameters.

## Returns:
    FilteringCSVReader: Returns the same instance (self). This instance must implement __next__ (it does) so callers can repeatedly call next() to obtain rows. No other return values are possible.

## Raises:
    None. This method does not raise exceptions. Any exceptions during iteration will originate from subsequent calls to __next__ (for example, StopIteration when the underlying reader is exhausted).

## State Changes:
- Attributes READ:
    - None explicitly by this method. (The returned self may later have its attributes read by __next__.)
- Attributes WRITTEN:
    - None. Calling __iter__ does not modify any attributes such as returned_header or reader position.

## Constraints:
- Preconditions:
    - The instance must be fully initialized: it should have a valid reader attribute and a working __next__ implementation (provided by the class).
    - If a fresh iteration is required, the caller must ensure a new FilteringCSVReader instance is created; calling __iter__ on the same instance does not reset iteration state.
- Postconditions:
    - The same instance (self) is returned and is ready to be used as an iterator.
    - No attributes are modified by this call; iteration state (e.g., returned_header) remains unchanged.

## Side Effects:
    - None directly. There is no I/O or external interaction triggered by __iter__ itself. Side effects such as reading from the underlying CSV reader occur later when __next__ is called.

### `csvkit.grep.FilteringCSVReader.__next__` · *method*

## Summary:
Yield the next output row for this filtered CSV iterator: first emit the stored header row once if present, then consume rows from the underlying reader until one satisfies the instance's predicate logic and return it, updating internal iteration state.

## Description:
- Known callers and lifecycle:
    - Invoked by the Python iterator protocol (for ... in ..., list(iter(...)), next(iterator)) after a FilteringCSVReader is constructed. Typical use is during the data-consumption stage of a CSV filtering pipeline: the caller repeatedly requests the next accepted row until iteration ends.
- Header semantics and why this belongs in __next__:
    - The header row (self.column_names) is consumed from the underlying reader during construction (__init__). __next__ is responsible only for returning that stored header exactly once (if present) and for driving the filtering loop that repeatedly calls next(self.reader) and self.test_row(row).
    - If self.column_names is falsy (None or an empty sequence) — for example because header handling was disabled at construction — __next__ does not emit a header and proceeds directly to testing and returning data rows.
- Relationship to test_row:
    - For each candidate row returned by the underlying reader, __next__ calls self.test_row(row) to determine acceptance. test_row implements the any_match and inverse logic and consults the normalized predicate functions stored in self.patterns. This separation keeps the iteration mechanism (repeat-until-accepted) in __next__ and the predicate semantics inside test_row.

## Args:
    None

## Returns:
    Sequence-like object (the same type yielded by the underlying reader):
    - If a stored header exists and has not yet been returned, returns that header object (exactly self.column_names).
    - Otherwise returns the next row from self.reader for which self.test_row(row) evaluates to acceptance according to the instance's patterns and flags.
    - Iteration termination is reported by raising StopIteration; no sentinel return values are used.

## Raises:
    StopIteration
        - Raised when the underlying iterator self.reader is exhausted. This originates from next(self.reader) and propagates to the caller to signal end of iteration.
    Any exception raised by the underlying reader or predicates
        - Exceptions raised while producing a row (from self.reader) or by predicate callables executed as part of self.test_row(row) propagate unchanged.
    Note:
        - The explicit final raise StopIteration() present in the implementation is unreachable in normal execution because the while True loop depends on next(self.reader) to eventually raise StopIteration; the practical effect is that StopIteration will be raised when the reader is exhausted.

## State Changes:
- Attributes READ (directly by __next__):
    - self.column_names (to decide whether to emit the stored header)
    - self.returned_header (to check whether the header has already been returned)
    - self.reader (consumed via next(self.reader) to obtain candidate rows)
- Attributes READ (indirectly via self.test_row):
    - self.patterns, self.any_match, self.inverse (test_row reads these to evaluate predicates)
- Attributes WRITTEN:
    - self.returned_header is set to True when the stored header is returned.
- No other instance attributes are modified by __next__.

## Constraints:
- Preconditions:
    - The instance must be properly initialized: self.reader must be an iterator (support next()) and self.test_row must accept the row objects produced by that reader.
    - If a header row was expected (header=True during construction), self.column_names should contain that header prior to the first call to __next__, and returned_header should be False.
    - Rows produced by self.reader should be sequence-like and indexable to match typical predicate expectations; otherwise predicates may raise.
- Postconditions:
    - If a stored header was emitted, returned_header will be True after the call and the underlying reader's position will remain at the first data row (the header was already consumed in __init__).
    - After returning a data row, the underlying reader will have been advanced through that row; subsequent calls to __next__ continue from the next position.
    - When the underlying reader is exhausted, StopIteration will be raised to the caller.
- Important edge case:
    - If the underlying reader never yields a row that satisfies test_row and also never becomes exhausted (for example, an infinite generator that always produces rows but none match), __next__ will block/loop indefinitely. Callers should ensure patterns are reachable for their data or that the underlying reader will eventually terminate.

## Side Effects:
    - Consumes (advances) items from self.reader by repeatedly calling next(self.reader) until a matching row is found or the reader raises StopIteration.
    - Mutates self.returned_header by setting it to True when emitting the stored header.
    - Invokes predicate callables through self.test_row(row); such callables may have arbitrary side effects or raise exceptions that will propagate.
    - Does not perform file I/O or network I/O itself; any such actions would come from the underlying reader or predicate functions.

## Usage notes:
    - To understand which rows are accepted, consult the documentation for test_row and for standardize_patterns (which defines how user-supplied patterns are normalized into predicate callables). __next__ assumes those predicates are already prepared and focuses solely on emitting the stored header (once) and returning subsequent rows that pass the predicates.
    - Typical iteration pattern: construct FilteringCSVReader with an underlying CSV row iterator, then iterate over it; the first yielded value may be the header (if header handling was enabled) followed by filtered data rows.

### `csvkit.grep.FilteringCSVReader.test_row` · *method*

## Summary:
Evaluate the configured per-column test functions against a single CSV row and return a boolean decision; this method does not modify the object's state.

## Description:
This method is invoked as part of the row-filtering step in a CSV-reading/filtering pipeline: for each row, the filtering logic calls this method to determine whether the row satisfies the configured patterns and should be accepted or rejected. It is extracted into its own method to encapsulate the matching policy (any-vs-all and inversion semantics) separately from iteration and I/O, making the filtering behavior easy to reason about and reuse.

Known callers and context:
- Called by higher-level filtering/iteration code that evaluates each CSV row (e.g., the iteration or read loop of a FilteringCSVReader). It operates during the per-row evaluation step of the pipeline.

Why this is a separate method:
- Encapsulates the evaluation rules (index access fallback, per-column test invocation, any/all match logic, inversion) so callers do not need to duplicate or understand those details.
- Keeps iteration/I/O code focused on row retrieval, while this method handles decision logic.

## Args:
    row (Sequence): A sequence-like container representing a CSV row (typically a list or tuple of strings). The method indexes into row using integer indices from self.patterns; if an index is out of bounds an empty string is used instead.

## Returns:
    bool: The boolean decision produced by the configured tests and the object's matching semantics.
    - If self.any_match is True:
        - Returns (not self.inverse) immediately if any test returns a truthy value.
        - If no tests return truthy, returns self.inverse after checking all patterns.
    - If self.any_match is False (i.e., require all tests to match):
        - Returns self.inverse immediately if any test returns a falsy value.
        - If all tests return truthy, returns (not self.inverse) after checking all patterns.
    - Special case: if self.patterns is empty:
        - If self.any_match is True: returns self.inverse.
        - Otherwise (any_match False): returns not self.inverse.

## Raises:
    Any exception raised by the user-provided test callables will propagate (the method does not catch exceptions from test(value)).
    The method handles IndexError when accessing row[idx] by treating missing indices as the empty string; other exceptions from row indexing (if row implements non-standard behavior) may propagate.

## State Changes:
    Attributes READ:
        - self.patterns: iterated via items() to obtain (idx, test) pairs
        - self.any_match: read to determine any-vs-all semantics
        - self.inverse: read to determine final boolean inversion behavior
    Attributes WRITTEN:
        - None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - self.patterns must be an iterable/dict-like object where items() yields (idx, test) pairs.
        - Each idx should be suitable for indexing into row (commonly an integer). The method tolerates IndexError by substituting ''.
        - Each test must be callable and accept a single argument (the extracted value). Tests should return a truthy or falsy value to indicate match/no-match.
        - row must support __getitem__ indexing semantics; missing indices should raise IndexError (the method catches IndexError to supply '').

    Postconditions:
        - No attributes on self are changed.
        - A boolean is returned according to the described any/all + inversion rules.
        - If a test callable raised an exception, that exception will propagate to the caller.

## Side Effects:
    - The method itself performs no I/O and has no side effects on external services.
    - However, calling the user-provided test callables may produce side effects (mutating external state, performing I/O, etc.); such side effects are not suppressed or managed by this method.

## `csvkit.grep.standardize_patterns` · *function*

## Summary:
Normalize a user-supplied collection of search patterns into a dictionary that maps column indices or explicit keys to one-argument predicate callables.

## Description:
This utility accepts either a mapping of column identifiers to pattern specifications or a sequence of patterns and returns a dictionary whose values are normalized predicate callables (created via pattern_as_function). It is intended to centralize the logic for interpreting flexible "patterns" (callables, regex-like objects, or plain values) and resolving column-name keys into numerical column indices when a list of column names is provided.

Known callers within the codebase:
- No direct callers were discovered in the local scan. Typical usage is from higher-level grep/filter code that needs to accept user-provided patterns keyed by column name or index and run them against CSV rows.

Why this logic is extracted:
- Responsibility boundary: convert heterogeneous, user-facing pattern specifications into a uniform mapping of column identifiers -> predicate(callable). Extracting this behavior keeps the rest of the grep/filter pipeline focused on applying predicates to values, not on interpreting user input formats.

## Args:
    column_names (list[str] or None):
        - A list (or other sequence) of column names in canonical order, or a falsy value (None or empty list) to indicate no name-to-index resolution is required.
        - If provided and non-empty, any pattern key that equals an item in this sequence will be replaced by that item's numeric index (first occurrence).
    patterns (mapping or iterable):
        - Preferred form: a mapping (e.g., dict) where each key is a column identifier (column name or integer index or any other key the caller intends) and each value is a pattern specification.
        - Alternate form: an iterable/sequence of pattern specifications (e.g., a list/tuple). When an iterable is supplied, patterns are treated positionally (index -> pattern).
        - Pattern specification values follow the contract used by pattern_as_function: they may be callables (returned unchanged), regex-like objects (adapted), or simple values (converted into membership predicates). Falsy values (None, empty string, False, 0, etc.) are filtered out and ignored.

    Interdependencies:
        - If patterns is a mapping, the function first iterates patterns.items(). If that raises AttributeError (patterns has no items), the function falls back to treating patterns as an iterable and enumerating it.
        - When column_names is provided, name keys present in patterns are resolved to numeric indices using column_names.index(key); this resolution can collide with existing numeric keys in the original patterns mapping (see Raises).

## Returns:
    dict:
        - A dictionary mapping keys to one-argument predicate callables (the predicates are the results of pattern_as_function applied to pattern values).
        - Possible forms of keys in the returned dict:
            * Integer column indices (int) when a pattern key matched an entry of column_names and was resolved to that index.
            * Original keys from the input mapping for keys that do not match any entry in column_names (this includes numeric keys that were provided explicitly).
            * For iterable input (fallback path), keys are integer indices (0-based) produced by enumerate(patterns).
        - Values are callables f(x) that accept a single argument and return a truthy/falsey result (exact behavior of each callable depends on pattern_as_function: it may return booleans or other truthy/falsey objects like regex match objects).

## Raises:
    ColumnIdentifierError:
        - Raised when a mapping key k resolves (via column_names.index(k)) to an integer idx that is already present as a key in the original patterns mapping. In that case the function raises:
            ColumnIdentifierError("Column %s has index %i which already has a pattern." % (k, idx))
        - This prevents ambiguous double-assignment of a pattern to the same column via both name and numeric index.

    Note on AttributeError handling:
        - The function intentionally catches AttributeError raised while attempting to treat patterns as a mapping (for example, if patterns has no .items attribute). In that case the function falls back to treating patterns as an iterable and does not propagate that AttributeError. Other exceptions raised during the conversion (for example, unexpected exceptions from pattern_as_function) will propagate.

## Constraints:
    Preconditions:
        - pattern_as_function must be available in the module scope to convert individual pattern values into callables.
        - If patterns is intended as a mapping, it should implement the items() method. If not, the function will attempt to treat it as an iterable.
        - When column_names is provided, its elements must be comparable to the mapping keys (the comparison uses equality and index lookup).
    Postconditions:
        - The returned value is always a dict whose values are callables that accept one argument.
        - When column_names was provided, any mapping keys equal to a column name are replaced by that column's numerical index in the returned dict (unless that index conflicts with an explicit key in the input mapping, in which case an error is raised).

## Side Effects:
    - None. The function performs no I/O and does not mutate external state. It only constructs and returns a new dictionary of callables.

## Control Flow:
flowchart TD
    Start[Start: standardize_patterns(column_names, patterns)] --> TryBlock[Attempt to treat patterns as mapping]
    TryBlock --> MapComp[Convert values: {k: pattern_as_function(v) for k,v in patterns.items() if v}]
    MapComp --> CheckNames{not column_names?}
    CheckNames -- Yes --> ReturnMap[Return the converted mapping (keys unchanged)]
    CheckNames -- No --> BuildP2[Create new dict p2 and iterate for k in patterns]
    BuildP2 --> InColumnNames{k in column_names?}
    InColumnNames -- Yes --> ResolveIdx[idx = column_names.index(k)]
    ResolveIdx --> ConflictCheck{idx in patterns?}
    ConflictCheck -- Yes --> RaiseErr[Raise ColumnIdentifierError]
    ConflictCheck -- No --> AssignIdx[p2[idx] = patterns[k]]
    InColumnNames -- No --> AssignKey[p2[k] = patterns[k]]
    AssignIdx --> ContinueLoop
    AssignKey --> ContinueLoop
    ContinueLoop --> LoopEnd[After loop: return p2]
    MapComp -- AttributeError --> ExceptPath[Except AttributeError]
    ExceptPath --> EnumerateFallback[Return {i: pattern_as_function(x) for i,x in enumerate(patterns)}]
    EnumerateFallback --> End[End]

## Examples:
- Example 1: mapping keyed by column names and indices (happy path)
    Inputs:
        column_names = ['id', 'name', 'email']
        patterns = {
            'name': 'gmail.com',              # substring pattern -> converted to predicate
            2: re.compile(r'@example\.org'),  # numeric key already provided -> kept as-is (value converted)
            'unused': None                    # falsy -> filtered out
        }
    Behavior:
        - 'name' is found in column_names at index 1 -> becomes key 1 in the result.
        - 2 remains as key 2 in the result.
        - 'unused' is ignored because its value is falsy.
    Result (conceptual):
        {
            1: <callable produced from 'gmail.com'>,
            2: <callable produced from re.compile(r'@example\.org')>
        }

- Example 2: conflict between name and explicit numeric key (error)
    Inputs:
        column_names = ['id', 'name', 'email']
        patterns = {'name': 'x', 1: 'y'}
    Behavior:
        - 'name' resolves to index 1.
        - Since 1 is already a key in patterns, the function raises:
            ColumnIdentifierError("Column name has index 1 which already has a pattern.")

- Example 3: iterable (positional) patterns fallback
    Inputs:
        column_names = None
        patterns = ['foo', re.compile(r'\d+'), lambda s: len(s) > 3]
    Behavior:
        - The function catches AttributeError when attempting patterns.items() and falls back to enumerate.
        - Returns {0: predicate_from('foo'), 1: predicate_from(re.compile(...)), 2: <same lambda>}

- Error handling guidance:
    - Wrap calls to the returned predicates in try/except if candidate values may not support the membership test or the adapted regex object lacks the expected method. The function itself will only raise ColumnIdentifierError for name/index conflicts; other runtime exceptions can arise when the predicates are invoked.

## `csvkit.grep.pattern_as_function` · *function*

## Summary:
Convert an input "pattern" into a one-argument predicate callable: return the input unchanged if it is already callable; wrap regex-like objects with an adapter; otherwise produce a membership-check predicate that tests whether the pattern is contained in the candidate value.

## Description:
This small utility normalizes disparate kinds of "patterns" into a consistent callable predicate that accepts a single argument and returns a truthy/falsey result.

Known callers within this repository:
- No direct callers were discovered during the local scan. This function is intended for use wherever higher-level "grep" or filter logic needs to accept flexible pattern arguments (user-provided predicate functions, compiled regular-expression objects, or simple substring values).

Why the logic is extracted:
- Responsibility boundary: pattern normalization. Converting several user-facing pattern types into a single callable predicate keeps calling code simple and focused on filtering logic. Extracting this conversion reduces duplication and centralizes detection/adapter behavior (callable passthrough, regex adaptation, substring matching).

## Args:
    obj (any): The pattern or predicate supplied by the caller. Allowed values and how they are interpreted:
        - If obj is already callable (callable(obj) is True): it is returned unchanged and expected to accept one positional argument (the value to test) and return a truthy/falsey result.
        - If obj is not callable and has an attribute named 'match' (hasattr(obj, 'match') is True): the object is treated as a "regex-like" object and is adapted via regex_callable. Note: regex_callable will forward calls to the wrapped object's search method at runtime.
        - Otherwise: obj is treated as a membership/substring value; the function returns a callable that tests "obj in x" when invoked.

    Interdependencies:
        - The "hasattr(obj, 'match')" test is used to detect regex-like objects, but the adapter used (regex_callable) delegates to a search method at call time. If an object has match but no search attribute, the returned callable will raise AttributeError when invoked. Callers should prefer passing fully-compatible regex/search objects (e.g., typical compiled regex pattern objects) or plain callables.

## Returns:
    callable: A one-argument callable predicate f(x) with the following possible behaviors:
        - If the input was callable: the same callable object passed through unchanged.
        - If the input had a 'match' attribute: an adapter produced by regex_callable(obj). When called, this adapter will invoke obj.search(x) and return whatever that method returns (commonly a match object or None for re.Pattern-like objects).
        - Otherwise: a lambda predicate that returns the result of the membership test (obj in x). Typical return values for this predicate are booleans (True/False) but when the delegated callable returns non-boolean values (e.g., a match object), those are returned as-is.

    Edge-case return values:
        - When the regex-adapter is used, the returned callable may return non-boolean objects (e.g., match object or None). Calling code should evaluate truthiness as appropriate.
        - The membership predicate returns the raw result of the membership operation; its type depends on the semantics of the container or value tested.

## Raises:
    - No exceptions are raised directly by pattern_as_function itself.
    - Exceptions may arise later when the returned callable is invoked:
        - AttributeError: If the object passed the 'match' test but lacks a search attribute, calling the adapter will raise AttributeError when attempting to access or call search.
        - Any exception raised by an underlying callable when invoked (for example, TypeError when performing "obj in x" if x does not support membership tests with obj, or exceptions raised by obj.search) will propagate to the caller.

## Constraints:
    Preconditions:
        - There are no strict preconditions enforced by pattern_as_function. However, practical expectations:
            * If you pass a callable, it should accept a single positional argument.
            * If you pass a regex-like object, it should ideally implement a search(string) method compatible with the adapter (see the "Raises" section for the mismatch caveat).
            * If you pass a non-callable value, the values you will later supply as x to the returned predicate must support the 'in' operator with that value.
    Postconditions:
        - The function always returns a callable object which can be invoked with a single argument. No global state is changed.

## Side Effects:
    - None. pattern_as_function performs attribute checks and returns a callable; it does not perform I/O, mutate external state, or call the provided pattern at creation time.

## Control Flow:
flowchart TD
    A[Start: pattern_as_function(obj)] --> B{callable(obj)?}
    B -- Yes --> C[Return obj unchanged]
    B -- No --> D{hasattr(obj,'match')?}
    D -- Yes --> E[Return regex_callable(obj) — adapter will delegate to obj.search when called]
    D -- No --> F[Return lambda x: obj in x]
    C --> G[End]
    E --> G
    F --> G

## Examples:
- Using an existing predicate function:
    1. Caller provides a function-like predicate that accepts one argument (for example, a function that tests whether a line contains at least three comma-separated fields).
    2. Passing that function into pattern_as_function returns the same function unchanged, so the caller can apply it directly to candidate values.

- Using a compiled/regex-like object:
    1. Provide a compiled regular-expression object (a typical object created by a regex library that implements match/search semantics).
    2. pattern_as_function detects the presence of a 'match' attribute and returns an adapter that will, when invoked, call the underlying pattern's search method and return its result (a match object or None).
    3. Note: because the detection checks for 'match' but the adapter calls 'search', ensure the supplied regex-like object implements search to avoid runtime AttributeError when the adapter is invoked.

- Using a simple substring value:
    1. Provide a string or other value that is not callable and lacks 'match'.
    2. pattern_as_function returns a predicate that performs the membership check "obj in x" when called; typical usage is to test whether the substring appears in x.

- Error-handling guidance:
    - Wrap invocation of the returned predicate in try/except if inputs may be malformed:
        * Catch AttributeError to detect the case when an object passed detection lacked a search method.
        * Catch TypeError to handle cases where the candidate value x does not support membership testing with the provided pattern.

## `csvkit.grep.regex_callable` · *class*

## Summary:
A lightweight callable wrapper that delegates calls to a provided regular-expression-like object's search method, returning that search result.

## Description:
This class wraps an object that implements a search(string) method (typically a compiled regular expression such as the value returned by re.compile). Instantiating regex_callable with such an object produces a callable that, when invoked with an argument, forwards the argument to the wrapped object's search method and returns whatever that method returns (usually a match object or None).

Typical scenarios:
- Use when an API expects a callable predicate but you already have a compiled regular-expression object.
- Use when you want a simple function-like adapter around objects that provide search semantics.

Known callers/factories:
- Commonly created by calling regex_callable(re.compile(pattern)), or by passing any object that implements a search(string) method.
- There are no special factory functions inside this module; creation is direct via the constructor.

Motivation and responsibility:
- Provides a tiny adapter that makes regex-style search objects usable where a plain callable is required. It enforces the single responsibility of forwarding the call to the underlying object's search method without adding behavior.

## State:
- Attributes:
    - pattern (object): Required. Any object that exposes a search(string) method which accepts one argument (commonly a string-like value). Typical accepted type is re.Pattern (the result of re.compile), but any duck-typed object with search is valid.
        - Valid values: any non-None object implementing a callable attribute named search.
        - Invariant: pattern is stored as-is and is not mutated by this class.
- __init__ parameters:
    - pattern: No default. Caller must supply an object with a search method. No type coercion is performed.
- Class invariants:
    - After construction, self.pattern is exactly the supplied object.
    - The instance contains no other mutable state; method calls do not modify stored attributes.

## Lifecycle:
- Creation:
    - Instantiate by calling regex_callable(pattern).
    - Required argument: pattern must be provided; there is no default or factory in the class itself.
- Usage:
    - Treat instances as a function: instance(arg).
    - The canonical method sequence is:
        1. Construct instance with a search-capable object.
        2. Invoke the instance any number of times with arguments appropriate for the underlying pattern.search.
    - There is no required ordering beyond constructing before calling.
- Destruction / cleanup:
    - No special cleanup required. The object holds only references and does not manage external resources. It is not a context manager and has no close or cleanup method.

## Method Map:
flowchart LR
    A[Constructor: __init__(pattern)] --> B[Instance created with .pattern]
    B --> C[Callable: __call__(arg)]
    C --> D[Delegates to pattern.search(arg)]
    D --> E[Returns underlying match object or None]

## Methods (behavioral summary):
- __init__(pattern)
    - Purpose: Store the provided pattern-like object for later delegation.
    - Input: pattern — object with a search(string) method.
    - Output: None (constructs and returns an instance).
    - Side effects: assigns self.pattern = pattern.
    - Edge behavior: Does not validate the presence of a search attribute at construction time.

- __call__(arg)
    - Purpose: Delegate to the wrapped object's search method and return its result.
    - Input: arg — the single positional argument forwarded to pattern.search.
    - Output: The direct result of pattern.search(arg). For typical regex pattern objects, this is an re.Match instance when a match is found, or None when no match is found.
    - Edge behavior:
        - If self.pattern has no search attribute, invoking the instance will raise AttributeError.
        - If pattern.search raises (for example because arg has an incompatible type), that exception propagates unchanged.

## Raises:
- __init__: The constructor does not explicitly raise any exceptions. It will accept and store any value for pattern.
- __call__: May raise exceptions raised by attempting to access or call the underlying search attribute:
    - AttributeError: if the stored pattern object has no attribute named search.
    - Any exception raised by the underlying pattern.search implementation (for instance TypeError if the provided arg is of an unexpected type) will propagate to the caller.

## Example:
- Typical creation:
    1. Compile a regular expression using the standard library: pattern = re.compile(r"\d+")
    2. Create the adapter: rc = regex_callable(pattern)
    3. Use as a callable: match = rc("123 abc")  (match is a match object or None)
- Notes on usage:
    - You may pass any object with a compatible search method instead of a re.Pattern.
    - Because no validation occurs at construction time, errors from a missing search method or from invalid argument types will surface only when the adapter is invoked.

### `csvkit.grep.regex_callable.__init__` · *method*

## Summary:
Store the provided pattern-like object on the instance for later delegation so the object can be used as a callable adapter that forwards calls to the pattern's search method.

## Description:
- Known callers and context:
    - Constructed directly by client code, typically as regex_callable(re.compile(...)) or regex_callable(some_searchable_object).
    - Used during setup/initialization of a pipeline or predicate sequence where a callable is required but the code author has a compiled regular expression (or any object exposing a search(string) method).
    - Lifecycle stage: invoked at creation time (before any __call__ use). No internal factories in this module call it; creation is direct and typically occurs once per adapter instance.

- Why this logic is its own method:
    - The constructor performs a single responsibility: capture and persist the wrapped pattern/searchable object. Separating this trivial storage into __init__ preserves clear class invariants and keeps creation semantics explicit (no lazy initialization or validation), letting the small adapter remain predictable and minimal.

## Args:
    pattern (object):
        - Required positional argument; no default.
        - Expected: any object that exposes a callable attribute named search which accepts a single positional argument (commonly a string) and returns a match-like object or None.
        - Note: The constructor does not validate the presence or callability of the search attribute. Supplying an incompatible value (including None) will not raise at construction time but will cause AttributeError or other exceptions when the instance is later invoked.

## Returns:
    None
    - The constructor returns None as usual for instance initializers. After returning, the instance is created with its state updated (see State Changes).

## Raises:
    - The constructor does not explicitly raise exceptions.
    - Implicitly, Python will raise TypeError if called with the wrong number of arguments (e.g., omitted pattern).
    - No validation is performed here, so any errors relating to the wrapped object's capabilities (missing search attribute, non-callable search, or exceptions raised by search) will surface only when the instance is used (not at construction).

## State Changes:
- Attributes READ:
    - None (the constructor does not read any existing self attributes).
- Attributes WRITTEN:
    - self.pattern: set to the supplied pattern argument (exact object reference, stored as-is).

## Constraints:
- Preconditions:
    - Callers must supply the pattern argument (no default). For correct subsequent usage, the supplied object should implement a callable search(string) method.
    - There is no runtime check here; the responsibility for providing a compatible object lies with the caller.

- Postconditions:
    - After __init__ returns, self.pattern is guaranteed to reference precisely the object passed as pattern (object identity preserved).
    - No other attributes are added or mutated by this method.
    - The instance is ready for use as a callable adapter; however, invoking it may raise errors if the stored object lacks a proper search method.

## Side Effects:
    - No I/O or external service calls.
    - Only side effect is mutation of the new instance state by assigning self.pattern to the provided object reference. No global state is modified.

### `csvkit.grep.regex_callable.__call__` · *method*

## Summary:
Delegates to the stored regular-expression object's search method to test the given input and returns the match result; does not modify the object's state.

## Description:
This method is the callable interface of the regex_callable object. It is intended to be used wherever a predicate or callable that performs a regular-expression search is required (for example, passed into filtering/selection steps in a grep-like pipeline). In that lifecycle stage it is invoked for each candidate string to decide whether the pattern appears in the candidate.

The logic is implemented as its own method to provide a concise, reusable callable object that encapsulates a compiled pattern (self.pattern) and can be passed directly to higher-order functions (filter, map, list comprehensions, iterator pipelines) or stored as a predicate without re-binding the pattern on every invocation.

## Args:
    arg (any): The value to search. Typically a str (or bytes when the compiled pattern expects bytes). There is no type coercion performed; the value is forwarded directly to self.pattern.search.

## Returns:
    re.Match or None: The Match object returned by the underlying pattern.search when a match is found, or None when no match exists. The exact return type is the match object type provided by the regular expression implementation used to construct self.pattern.

## Raises:
    AttributeError: If self.pattern does not have a search attribute (e.g., pattern was set to an object without .search).
    TypeError: If the underlying pattern.search raises TypeError because arg is of an incompatible type (e.g., passing None or an unsupported type to a compiled regex that expects str/bytes).
    Any exception raised by the underlying self.pattern.search is propagated unchanged.

## State Changes:
    Attributes READ:
        self.pattern
    Attributes WRITTEN:
        (none) — this method does not modify any attributes of the instance.

## Constraints:
    Preconditions:
        - The instance must have a valid self.pattern attribute set (the class __init__ sets this).
        - self.pattern must expose a .search(callable_arg) method that accepts the provided arg (commonly a compiled re.Pattern).
    Postconditions:
        - The instance remains unchanged.
        - The method returns exactly whatever self.pattern.search(arg) returns (match object or None) or propagates its exception.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self (except insofar as the underlying .search implementation itself may have side effects, which is unusual for regex search functions).

