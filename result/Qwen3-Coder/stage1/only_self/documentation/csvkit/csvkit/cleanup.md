# `cleanup.py`

## `csvkit.cleanup.join_rows` · *function*

## Summary:
Combines multiple rows of data into a single row by joining fields from consecutive rows.

## Description:
Joins multiple rows of data together by appending the last field of the previous row with the first field of the next row, using a specified delimiter. This function is typically used in CSV processing to handle multi-line field values that have been split across multiple rows.

## Args:
    rows (iterable): An iterable of row data, where each row is a list-like object containing field values.
    joiner (str): A string used to join fields between rows. Defaults to a single space character (' ').

## Returns:
    list: A single merged row containing all fields from the input rows, with appropriate joining of fields between rows.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
    - The input `rows` must be iterable and contain at least one row
    - Each row in `rows` should be indexable (support indexing operations)
    
    Postconditions:
    - The returned list contains all fields from all input rows
    - Fields from consecutive rows are joined using the specified joiner
    - The first row's fields remain unchanged in their original positions
    - The last field of each row (except the last row) gets joined with the first field of the next row

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start join_rows] --> B[Convert rows to list]
    B --> C[Copy first row to fixed_row]
    C --> D[For each remaining row in rows]
    D --> E{Is row empty?}
    E -->|Yes| F[Set row = ['']]
    E -->|No| G[Continue with original row]
    G --> H[Append joiner + row[0] to fixed_row[-1]]
    H --> I[Extend fixed_row with row[1:]]
    I --> J[Continue to next row]
    J --> D
    D --> K[Return fixed_row]
```

## Examples:
    >>> join_rows([['a', 'b'], ['c', 'd']])
    ['a', 'b c', 'd']
    
    >>> join_rows([['hello', 'world'], ['foo', 'bar']], joiner='|')
    ['hello', 'world|foo', 'bar']
    
    >>> join_rows([['single']])
    ['single']
    
    >>> join_rows([['a', 'b'], [], ['c', 'd']])
    ['a', 'b c', 'd']
```

## `csvkit.cleanup.RowChecker` · *class*

*No documentation generated.*

### `csvkit.cleanup.RowChecker.__init__` · *method*

## Summary:
Initializes a RowChecker object with a CSV reader and sets up tracking attributes for validation errors and row processing statistics.

## Description:
The RowChecker.__init__ method prepares the object for CSV row validation and cleanup operations. It reads the column names from the provided CSV reader (handling empty files gracefully) and initializes tracking variables for monitoring validation errors and row joining operations.

## Args:
    reader: A CSV reader object that provides access to CSV data rows. Expected to be an iterator that yields rows.

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.reader: Assigned the input reader parameter
    - self.column_names: Set to the first row from the reader, or empty list if reader is empty
    - self.errors: Initialized as an empty list to track validation errors
    - self.rows_joined: Initialized to 0 to count joined rows
    - self.joins: Initialized to 0 to count join operations

## Constraints:
    Preconditions:
    - The reader parameter should be a valid CSV reader object that implements the iterator protocol
    - The reader should be able to yield rows when next() is called
    
    Postconditions:
    - self.reader is assigned the input reader
    - self.column_names contains either the first row from the reader or an empty list
    - All tracking attributes (errors, rows_joined, joins) are initialized to appropriate default values

## Side Effects:
    None

### `csvkit.cleanup.RowChecker.checked_rows` · *method*

## Summary:
Generates validated CSV rows while attempting to fix length mismatches by joining adjacent rows.

## Description:
Processes rows from a CSV reader, validating that each row contains the expected number of columns matching the header. When a row has a different column count, it attempts to join it with subsequent rows to create a properly formatted row. This method serves as a robust CSV row validator that can recover from certain formatting issues while maintaining error tracking.

## Args:
    None explicitly taken as arguments (uses self state)

## Returns:
    Generator yielding list[str]: Validated rows with proper column counts, potentially joined from multiple input rows when length mismatches occur.

## Raises:
    LengthMismatchError: When a row has a different number of columns than expected, and cannot be joined with subsequent rows.
    CSVTestException: When other CSV validation errors occur during row processing.

## State Changes:
    Attributes READ: self.column_names, self.reader, self.errors, self.rows_joined, self.joins
    Attributes WRITTEN: self.errors, self.rows_joined, self.joins

## Constraints:
    Preconditions:
    - self.column_names must be initialized (set during RowChecker.__init__)
    - self.reader must be a valid CSV reader object with line_num attribute
    - self.errors, self.rows_joined, self.joins must be initialized as mutable objects
    
    Postconditions:
    - All yielded rows will have the same length as self.column_names
    - Error tracking is maintained in self.errors
    - Join statistics are updated in self.rows_joined and self.joins

## Side Effects:
    - Reads from the CSV reader (modifies reader state)
    - Modifies self.errors by appending new error instances
    - Modifies self.rows_joined and self.joins counters when row joins occur
    - May consume multiple rows from the underlying CSV reader when performing joins

