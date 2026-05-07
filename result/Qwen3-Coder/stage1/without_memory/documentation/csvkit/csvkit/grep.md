# `grep.py`

## `csvkit.grep.FilteringCSVReader` · *class*

*No documentation generated.*

### `csvkit.grep.FilteringCSVReader.__init__` · *method*

*No documentation generated.*

### `csvkit.grep.FilteringCSVReader.__iter__` · *method*

## Summary:
Makes the FilteringCSVReader instance iterable by returning itself.

## Description:
This method implements the iterator protocol for the FilteringCSVReader class, allowing instances to be used in for-loops and other iteration contexts. It enables the class to act as an iterator that yields filtered CSV rows one at a time.

The method is part of a larger filtering mechanism that processes CSV data based on pattern matching criteria defined during initialization. When called, it returns the instance itself, making it compatible with Python's iterator protocol.

## Args:
    None

## Returns:
    FilteringCSVReader: The instance itself, enabling iteration over filtered CSV rows.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The FilteringCSVReader instance must be properly initialized with a CSV reader and filtering patterns.
    Postconditions: The instance becomes ready to be iterated over using the standard Python iteration protocol.

## Side Effects:
    None

### `csvkit.grep.FilteringCSVReader.__next__` · *method*

## Summary:
Returns the next filtered row from the CSV reader, including the header row exactly once.

## Description:
This method implements the iterator protocol for the FilteringCSVReader class. It first returns the column names (header row) exactly once, then iterates through subsequent rows from the underlying CSV reader, filtering them based on configured patterns. The filtering logic is handled by the `test_row` method.

## Args:
    None

## Returns:
    list[str]: A row from the CSV data, either the header row (once) or a filtered data row.

## Raises:
    StopIteration: When there are no more rows to process from the underlying reader.

## State Changes:
    Attributes READ: self.column_names, self.returned_header, self.reader, self.test_row
    Attributes WRITTEN: self.returned_header (set to True after returning header)

## Constraints:
    Preconditions: 
    - The underlying `self.reader` must be iterable and support `next()` calls
    - `self.column_names` may be None or contain column names
    - `self.test_row` method must be implemented and callable
    
    Postconditions:
    - If `self.column_names` exists, the header is returned exactly once
    - All returned rows pass the filtering criteria defined by `self.patterns`
    - `self.returned_header` is set to True after the header is returned

## Side Effects:
    I/O: Reads from the underlying CSV reader via `next(self.reader)`
    Mutation: Modifies `self.returned_header` attribute to track header consumption

### `csvkit.grep.FilteringCSVReader.test_row` · *method*

## Summary:
Tests whether a CSV row matches the configured filtering patterns and returns a boolean indicating inclusion/exclusion.

## Description:
Determines if a given CSV row should be included in the filtered output based on the patterns configured during initialization. This method implements the core filtering logic for the FilteringCSVReader class, supporting both positive and negative matching (inverse flag), as well as "any match" vs "all match" semantics.

The method processes each pattern in self.patterns, applying the pattern test to the corresponding column value in the row. When a pattern fails to match (or matches when inverse is enabled), the decision is made immediately based on the any_match flag. If no patterns match (or all match when any_match is False), the final decision is made based on the inverse flag.

## Args:
    row (list): A list representing a CSV row, where each element corresponds to a column value.

## Returns:
    bool: True if the row should be included in the output, False if it should be excluded.

## Raises:
    None explicitly raised, but may propagate exceptions from pattern functions.

## State Changes:
    Attributes READ: self.patterns, self.any_match, self.inverse
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.patterns must be properly initialized with pattern functions
    - row must be iterable with appropriate length for pattern indices
    - self.any_match and self.inverse must be boolean values
    Postconditions:
    - Returns a boolean value indicating row inclusion status

## Side Effects:
    None - This method is pure and has no side effects beyond returning a boolean value.

## `csvkit.grep.standardize_patterns` · *function*

*No documentation generated.*

## `csvkit.grep.pattern_as_function` · *function*

*No documentation generated.*

## `csvkit.grep.regex_callable` · *class*

*No documentation generated.*

### `csvkit.grep.regex_callable.__init__` · *method*

*No documentation generated.*

### `csvkit.grep.regex_callable.__call__` · *method*

*No documentation generated.*

