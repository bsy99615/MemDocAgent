# `cleanup.py`

## `csvkit.cleanup.join_rows` · *function*

*No documentation generated.*

## `csvkit.cleanup.RowChecker` · *class*

*No documentation generated.*

### `csvkit.cleanup.RowChecker.__init__` · *method*

*No documentation generated.*

### `csvkit.cleanup.RowChecker.checked_rows` · *method*

## Summary:
Generates validated and potentially joined CSV rows while tracking processing errors and join statistics.

## Description:
Processes rows from a CSV reader, validating that each row matches the expected column count. When length mismatches occur, attempts to join consecutive rows to form valid rows. This method serves as the core validation and correction mechanism for CSV data cleaning, allowing recovery from malformed rows while maintaining metadata about processing operations.

## Args:
    None - operates on instance state

## Returns:
    Generator yielding list[str]: Validated CSV rows, potentially joined from multiple input rows when length mismatches are detected

## Raises:
    LengthMismatchError: When a row has a different number of columns than expected
    CSVTestException: When other CSV validation issues are encountered

## State Changes:
    Attributes READ: self.column_names, self.reader
    Attributes WRITTEN: self.errors, self.rows_joined, self.joins

## Constraints:
    Preconditions: 
    - self.column_names must be initialized (set during RowChecker.__init__)
    - self.reader must be a valid CSV reader iterator
    - self.reader.line_num must be accessible
    
    Postconditions:
    - All yielded rows will have length equal to len(self.column_names)
    - Error tracking is updated with any encountered validation issues
    - Join statistics (rows_joined, joins) are incremented when row joining occurs

## Side Effects:
    - Mutates self.errors by appending new error instances
    - Mutates self.rows_joined and self.joins by incrementing counters
    - Reads from CSV reader, advancing its position
    - May yield modified rows that combine data from multiple input rows

