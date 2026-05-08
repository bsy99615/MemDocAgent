# `cleanup.py`

## `csvkit.cleanup.join_rows` · *function*

## Summary:
Merge multiple CSV-style rows into a single logical row by concatenating the first cell of each following row onto the last cell of the base row (separated by joiner) and appending the remaining cells; returns the combined, shallow-copied first-row sequence extended in-place.

## Description:
Known callers:
    - No direct callers were found in the provided repository snapshot. Typical usage is in CSV cleanup stages where a single logical CSV record has been split across multiple parsed rows (for example, when a field contained a newline and parsing produced separate physical rows) and the fragments must be recombined.

Why this logic is extracted:
    - The function defines a precise policy for reassembling split rows (normalizing empty rows, concatenating the first element of each subsequent row onto the last element of the base row using a joiner, and appending remaining cells). Extracting this behavior keeps higher-level cleanup code simpler, centralizes the merge policy for testing, and enables reuse.

## Args:
    rows (iterable of indexable, sliceable sequences): An iterable (e.g., list or iterator) that yields row-like sequences (commonly lists of cell values). Each inner sequence represents CSV cells in order. The function converts the iterable to a list internally.
        - Requirements:
            * The iterable must yield at least one row (otherwise rows[0] raises IndexError).
            * The first yielded row (rows[0]) must be a mutable, list-like sequence that supports slicing, item assignment, and the extend method (the implementation performs rows[0][:] and then uses fixed_row[-1] += ... and fixed_row.extend(...)). A plain list is the canonical and expected type.
            * All inner rows must be indexable (support row[0]) and sliceable (support row[1:]).
            * Inner elements that will be concatenated should be string-like or otherwise safe for formatted conversion and addition with the last cell; otherwise a runtime error may occur.
    joiner (any): A value inserted between the existing last cell and the first cell of each subsequent row when concatenating. The implementation uses f-string formatting (f"{joiner}{row[0]}"), so non-string joiner values will be converted via their __format__ implementation. It is recommended to pass a str for predictable results. Defaults to a single space ' '.

Notes on interdependencies:
    - The implementation assumes the first row is list-like (supports extend and item assignment); using immutable or non-list-like types for the first row will typically raise at runtime.
    - The function does not coerce element types beyond f-string formatting and Python's augmented assignment semantics; callers should ensure element types are compatible with the intended concatenation.

## Returns:
    list-like sequence: A shallow copy of rows[0] (via rows[0][:]) that is mutated during construction by augmented assignment on its last element and by extend to append elements from subsequent rows. For the canonical case where rows[0] is a list, the return value is a list.
    Construction rules:
        - fixed_row = rows[0][:]
        - For each subsequent row r:
            * If len(r) == 0, treat r as [''].
            * Compute suffix = f"{joiner}{r[0]}" and perform fixed_row[-1] += suffix.
            * Call fixed_row.extend(r[1:]) to append remaining cells.
    Return shapes and notes:
        - Single-row input: returns a shallow copy of that row (same length and element references).
        - Multiple rows: the final length equals len(rows[0]) + sum(max(0, len(r) - 1) for r in rows[1:]) when rows[0] is list-like.
        - If rows[0] is empty and there are no subsequent rows, the function returns an empty shallow copy of the first row's type; if rows[0] is empty but there are subsequent rows, an IndexError will be raised when attempting to access fixed_row[-1].

## Raises:
    IndexError:
        - If the top-level iterable yields no rows, the initial access rows[0] raises IndexError.
        - If rows[0] is an empty sequence (e.g., []) and there exists at least one subsequent row, the function raises IndexError when it attempts to access fixed_row[-1] during the first merge step.
    TypeError:
        - If rows[0] is an immutable sequence (e.g., tuple) or otherwise does not support item assignment, performing fixed_row[-1] += ... will raise TypeError (e.g., "'tuple' object does not support item assignment").
        - If the in-place addition to fixed_row[-1] is incompatible with the types involved (for example, fixed_row[-1] is None and cannot be added to a string), a TypeError may be raised.
    AttributeError:
        - If fixed_row (the shallow copy of rows[0]) does not implement extend, fixed_row.extend(...) will raise AttributeError. Note: in typical failure ordering, the augmented-assignment step occurs before extend, so TypeError for item assignment is the more likely first error when rows[0] is not a mutable list-like object.

## Constraints:
Preconditions:
    - The iterable must yield at least one row.
    - The first row should be a mutable, list-like sequence (supporting slicing, item assignment, and extend).
    - Cells expected to be concatenated should be string-like or otherwise safe for formatted conversion and addition.

Postconditions:
    - The returned object is a newly constructed shallow copy of the first row (created by slicing) that has been extended with data from subsequent rows. The original input rows and their container are not mutated by the function.
    - Elements appended into the returned sequence are the same object references as supplied from input rows (shallow-copy semantics). If any element object is mutable and subsequently modified by the caller, that modification will be observable via the returned sequence.

## Side Effects:
    - No network, file I/O, or global-state mutation.
    - The function mutates an internal shallow copy (fixed_row) during assembly and returns it. It does not mutate the original first-row object.
    - Augmented assignment (+=) may invoke an element's __iadd__ which can mutate the element in-place if that type defines in-place mutation semantics (e.g., bytearray); for immutable strings this creates a new string assigned into fixed_row.

## Control Flow:
flowchart TD
    A[Start: receive rows iterable] --> B[Convert iterable to list rows]
    B --> C{rows empty?}
    C -->|Yes| D[Access rows[0] -> IndexError]
    C -->|No| E[fixed_row = rows[0][:] (shallow copy)]
    E --> F{fixed_row empty AND rows length > 1?}
    F -->|Yes| G[Attempt fixed_row[-1] -> IndexError]
    F -->|No| H[Iterate over rows[1:]]
    H --> I{row is empty?}
    I -->|Yes| J[row := ['']]
    I -->|No| K[row unchanged]
    J --> L[fixed_row[-1] += f"{joiner}{row[0]}"]
    K --> L
    L --> M[fixed_row.extend(row[1:])]
    M --> N{more rows?}
    N -->|Yes| H
    N -->|No| O[Return fixed_row]

## Examples:
Example 1 — Basic merge (canonical usage with lists):
    Input:
        rows = [['id', 'first', 'last'], ['Middle', 'Suffix']]
    Call:
        result = join_rows(rows)
    Return:
        ['id', 'first', 'last Middle', 'Suffix']

Example 2 — Empty intermediate row:
    Input:
        rows = [['a', 'b'], []]
    Call:
        result = join_rows(rows, joiner='|')
    Return:
        ['a', 'b|']

Example 3 — Single-row input:
    Input:
        rows = [['only', 'row']]
    Call:
        result = join_rows(rows)
    Return:
        ['only', 'row']

Example 4 — Empty first row with subsequent rows (error example):
    Input:
        rows = [[], ['x']]
    Call:
        join_rows(rows)
    Behavior:
        - fixed_row becomes a shallow copy of rows[0] (an empty list)
        - On processing the next row, accessing fixed_row[-1] raises IndexError
    Result:
        IndexError is raised; callers should normalize or validate the first row before calling.

Example 5 — Non-list first-row type causing TypeError or AttributeError:
    Input:
        rows = [('a', 'b'), ('c',)]
    Call:
        join_rows(rows)
    Behavior:
        - rows[0][:] yields a tuple; attempting fixed_row[-1] += ' c' will raise TypeError due to lack of item assignment on tuple (likely before any call to extend).
    Recommendation:
        - Convert to lists before calling: join_rows([list(r) for r in rows])

Example 6 — Type-related runtime error:
    Input:
        rows = [[None], ['x']]
    Call:
        join_rows(rows)
    Behavior:
        - Attempting None += ' x' (or formatting None into a string) results in a TypeError; ensure cell values are strings before calling.

## `csvkit.cleanup.RowChecker` · *class*

*No documentation generated.*

### `csvkit.cleanup.RowChecker.__init__` · *method*

## Summary:
Initializes a RowChecker by attaching a CSV-reader-like iterator, consuming its first item as the column header names (or an empty list if the reader is empty), and initializing internal counters and the error list.

## Description:
Known callers and context:
    - No direct call sites were found in the provided scan of the codebase. In typical usage this constructor is called at the start of a CSV cleanup/validation pipeline to wrap a CSV reader (an iterator over rows) before invoking the RowChecker.checked_rows() generator to validate and possibly repair row length mismatches.
    - Lifecycle stage: invoked once when preparing to validate/clean a CSV stream; it performs one-time setup (header extraction) so subsequent row checks operate with the header information.

Why this logic is in its own method:
    - Encapsulates initialization concerns (attaching the reader, extracting header, and resetting counters/errors) separately from the row-processing logic in checked_rows(). This keeps row validation focused on streaming behavior while ensuring header extraction and state reset occur exactly once when the wrapper is created.

## Args:
    reader (iterator):
        - A CSV-reader-like iterator that yields row objects (commonly lists or tuples of strings).
        - The constructor calls next(reader) once to obtain column names; therefore the reader must implement the iterator protocol (__iter__/__next__).
        - Practical expectations (not strictly enforced): the reader exposes a numeric attribute line_num used by checked_rows() for line tracking. If line_num is absent, checked_rows() may raise AttributeError when it accesses reader.line_num.

## Returns:
    None
    - Standard constructor behavior: always returns None. The observable effect is on the new object's state (see State Changes).

## Raises:
    - Any exception raised by next(reader) other than StopIteration will propagate (for example, TypeError if reader is not an iterator, or any reader-specific errors).
    - StopIteration is explicitly handled and treated as an empty input; it does NOT raise and instead sets column_names to an empty list.

## State Changes:
    Attributes READ:
        - None of self's attributes are read during initialization.
        - The constructor calls next(reader), which reads from the provided reader object (external state).

    Attributes WRITTEN:
        - self.reader: set to the provided reader iterator.
        - self.column_names: set to the first yielded row from reader, or [] if reader is exhausted.
        - self.errors: initialized to an empty list.
        - self.rows_joined: initialized to 0 (int).
        - self.joins: initialized to 0 (int).

## Constraints:
    Preconditions:
        - The caller should provide an iterator. If a non-iterator is passed, next(reader) will raise and that exception will propagate.
        - If the downstream checked_rows() method will be used, the reader is expected to be in the state immediately after the header row (i.e., the first row has been consumed by this constructor).
        - For useful diagnostics, the reader should preferably expose a numeric line_num attribute; otherwise line-number-based error messages in checked_rows() will not be available.

    Postconditions:
        - After __init__ returns, the RowChecker instance holds:
            * reader referencing the same iterator, already advanced past the header (if any).
            * column_names set to the header row (first yielded item) or [] when the reader had no items.
            * errors is an empty list ready to accumulate CSVTestException instances.
            * rows_joined == 0 and joins == 0.

## Side Effects:
    - Consumes the first item from the provided reader (calls next(reader)); this advances the reader and may change any reader-internal counters (e.g., line_num).
    - Does not perform I/O, logging, or external service calls.
    - Does not mutate objects other than assigning attributes on self and advancing the provided reader.

### `csvkit.cleanup.RowChecker.checked_rows` · *method*

## Summary:
Iterate over the reader yielding validated row sequences; detect rows whose length differs from the header length, record those mismatches, and attempt to repair sequences of short rows by joining them into a single valid row. Mutates the checker's error list and join counters and consumes the reader as it iterates.

## Description:
Known callers and invocation context:
    - No direct callers were found in the provided repository snapshot. Typical usage is to instantiate RowChecker with a CSV reader and iterate this generator as the CSV-cleaning stage that validates and optionally repairs parsed rows after the header has been consumed.
    - Lifecycle stage: called after RowChecker(...) construction (which consumes the header row) and used when streaming or processing the remaining CSV rows. The method is intended to be iterated by consumer code that wants validated rows (and access to RowChecker state such as errors and join statistics).

Why this logic is a separate method:
    - The method encapsulates non-trivial control flow for detection, accumulation, and repair of split logical records (rows whose physical parsed lines have the wrong number of columns). Extracting this as a dedicated generator keeps higher-level code simpler, centralizes the repair policy, and allows consumers to iterate a single unified stream of corrected rows while inspecting accumulated errors and metrics on the RowChecker instance.

## Args:
    None.

## Returns:
    generator that yields sequences (row-like iterables, typically lists of cell values).
    - Yields the original row object (as read from the reader) when its length equals the header column count.
    - When a sequence of shorter rows is successfully merged into a row whose length equals the header count (via join_rows), yields the merged row (the merged result returned by join_rows).
    - If the reader is exhausted without producing any valid rows, the generator yields nothing.
    - Note: yielded rows follow the same "row" shape produced by the underlying reader or by join_rows (commonly list-like sequences). Consumers should expect indexable, sliceable sequences.

## Raises:
    - Exceptions raised by join_rows (for example IndexError, TypeError, AttributeError) or other unexpected runtime errors may propagate out of the generator. The method itself intentionally catches and records CSVTestException and LengthMismatchError but does not catch arbitrary exceptions originating from join_rows or other runtime failures.
    - The method does not re-raise LengthMismatchError or CSVTestException it catches; those are appended to self.errors instead and the iteration continues.

## Behavior detail and edge cases:
    - Header length: the expected column count is determined by len(self.column_names) captured at call time.
    - For each row read from self.reader:
        * If len(row) == expected length: the row is yielded and any accumulated short-row error buffer (joinable_row_errors) is cleared.
        * If len(row) != expected length: a LengthMismatchError(line_number, row, expected_length) is instantiated and handled:
            - The error object is appended to self.errors.
            - If the row is longer than the expected length (len(row) > expected length): the implementation does not attempt to join it with prior short rows; joinable_row_errors is cleared.
            - If the row is shorter than the expected length (len(row) < expected length): the error is appended to joinable_row_errors and the code repeatedly:
                + Calls join_rows([error.row for error in joinable_row_errors], joiner=' ') to attempt to produce a combined row.
                + If the combined row length < expected length: stop attempting with the current accumulated set (break the inner loop) and continue reading more rows (more errors may be appended later).
                + If the combined row length == expected length: increments self.rows_joined by the number of errors used, increments self.joins by 1, yields the combined row, removes each used error from joinable_row_errors and from self.errors, then stops the inner loop for this pass.
                + If the combined row length > expected length: drop the oldest accumulated error (joinable_row_errors = joinable_row_errors[1:]) and try again with the remaining accumulated errors; this loop repeats until joinable_row_errors becomes empty or a valid merged row is produced.
        * If a CSVTestException is raised during per-row processing, the exception is appended to self.errors and any accumulated joinable_row_errors buffer is cleared; iteration continues.
    - line_number handling: at the start of the generator, line_number is set from self.reader.line_num; after each row-processing iteration the method updates line_number = self.reader.line_num so that subsequent LengthMismatchError instances reflect the reader's current line number at the time they are detected.
    - The method consumes the underlying reader (advances it as rows are iterated). Once exhausted, iteration ends.

## State Changes:
    Attributes READ:
        - self.column_names (to compute expected column count)
        - self.reader (iteration and self.reader.line_num for tracking)
    Attributes WRITTEN / MUTATED:
        - self.errors: appended with LengthMismatchError or CSVTestException instances; some LengthMismatchError instances are removed from self.errors when their associated rows are successfully joined.
        - self.rows_joined: incremented by the number of formerly-split rows that were merged when a join succeeds (using len(joinable_row_errors) at the time of a successful merge).
        - self.joins: incremented by 1 for each successful merge operation.
    Other observable mutations:
        - The underlying reader is consumed (its iteration pointer and line_num advance), which is an observable external state change.

## Constraints:
    Preconditions:
        - self.reader must be an iterator that yields row-like sequences (indexable and sliceable). The reader must expose a line_num attribute that reflects the current read position when consulted.
        - self.column_names should already be set (RowChecker.__init__ consumes the header row and sets column_names; this method assumes the header has been consumed).
    Postconditions:
        - After a full iteration, self.errors contains any LengthMismatchError or CSVTestException objects that were not successfully resolved by joining; errors removed during successful joins will not remain in self.errors.
        - self.rows_joined and self.joins reflect the number of rows merged and number of join operations performed during iteration.
        - The reader is exhausted (if iteration is carried to completion by the consumer).

## Side Effects:
    - Mutates the RowChecker instance as described under "State Changes".
    - Consumes the provided reader (advances it).
    - Potentially invokes join_rows, which may raise exceptions (these exceptions are not caught by this method and therefore may propagate to callers).
    - No file or network I/O is performed by this method itself; side effects are limited to in-memory state mutations and propagation of exceptions.

## Implementation notes for reimplementation:
    - Implement as a generator method (uses yield).
    - Maintain a small buffer (joinable_row_errors) of recent LengthMismatchError objects whose rows are shorter than the expected length; attempt to repair by repeatedly calling join_rows on the buffered rows until a valid-length row is produced or the buffer is emptied or considered insufficient.
    - Correctly maintain and update self.errors, self.rows_joined, self.joins, and line_number at the same points shown above so error objects and line numbers remain meaningful to consumers.

