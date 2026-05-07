# `fixed.py`

## `csvkit.convert.fixed.fixed2csv` · *function*

*No documentation generated.*

## `csvkit.convert.fixed.FixedWidthReader` · *class*

*No documentation generated.*

### `csvkit.convert.fixed.FixedWidthReader.__init__` · *method*

*No documentation generated.*

### `csvkit.convert.fixed.FixedWidthReader.__iter__` · *method*

## Summary:
Makes the FixedWidthReader instance iterable by returning itself as the iterator.

## Description:
This method implements the iterator protocol by returning the instance itself, allowing the FixedWidthReader to be used in for-loops and other iteration contexts. It enables the class to function as both an iterable and an iterator.

## Args:
    None

## Returns:
    FixedWidthReader: The instance itself, making it iterable.

## Raises:
    None

## State Changes:
    Attributes READ: self.parser, self.header, self.file
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The FixedWidthReader instance must be properly initialized with a file handle and schema.
    Postconditions: After calling this method, the instance can be used in iteration contexts.

## Side Effects:
    None

### `csvkit.convert.fixed.FixedWidthReader.__next__` · *method*

## Summary:
Returns the next row from a fixed-width formatted file, handling header row processing separately from data rows.

## Description:
Implements the iterator protocol for FixedWidthReader, yielding column headers on the first call and parsed data rows on subsequent calls. This method separates header processing from data parsing to support CSV-like iteration patterns where the first row contains column names.

## Args:
    None

## Returns:
    list[str]: On first call, returns the column headers as a list of strings. On subsequent calls, returns a parsed data row as a list of strings.

## Raises:
    StopIteration: When the input file is exhausted.

## State Changes:
    Attributes READ: self.header, self.parser, self.file
    Attributes WRITTEN: self.header (set to False after first call)

## Constraints:
    Preconditions: 
    - FixedWidthReader must be initialized with a valid file handle and schema
    - The file handle must be iterable and support next() calls
    - self.parser must be a valid FixedWidthRowParser instance
    
    Postconditions:
    - On first call, self.header is set to False
    - Returns either headers list or parsed data row list

## Side Effects:
    I/O: Reads from the input file handle (self.file) via next() calls
    Mutates: Modifies self.header state from True to False after first invocation

## `csvkit.convert.fixed.FixedWidthRowParser` · *class*

*No documentation generated.*

### `csvkit.convert.fixed.FixedWidthRowParser.__init__` · *method*

*No documentation generated.*

### `csvkit.convert.fixed.FixedWidthRowParser.parse` · *method*

## Summary:
Parses a fixed-width formatted line into a list of field values based on predefined field specifications.

## Description:
Extracts field values from a fixed-width formatted input line by slicing substrings according to field position and length specifications defined in the parser's schema. This method is part of the fixed-width file parsing pipeline and is typically called during data processing when converting fixed-width records to structured data.

## Args:
    line (str): A fixed-width formatted string containing data fields

## Returns:
    list[str]: A list of field values with leading/trailing whitespace removed from each field

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.fields
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The input line must be long enough to accommodate all field specifications
    - self.fields must be populated with valid field definitions containing start and length attributes
    - Each field definition must have start and length attributes that are integers
    
    Postconditions:
    - Returns a list of strings with whitespace stripped from each field
    - The returned list length matches the number of fields defined in self.fields

## Side Effects:
    None

### `csvkit.convert.fixed.FixedWidthRowParser.parse_dict` · *method*

## Summary:
Converts a fixed-width line into a dictionary mapping column headers to parsed values.

## Description:
Transforms a raw text line into a dictionary by pairing each parsed field value with its corresponding header name. This method serves as a convenience interface for converting structured fixed-width data into a more accessible dictionary format.

## Args:
    line (str): A single line of fixed-width formatted text to parse.

## Returns:
    dict: A dictionary where keys are column headers and values are the parsed field values from the input line.

## Raises:
    None explicitly raised, but may propagate exceptions from underlying parsing operations.

## State Changes:
    Attributes READ: self.headers, self.parse
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.headers must be a sequence of strings representing column names
    - self.parse must be callable and return a sequence of values matching the length of self.headers
    - line must be a string compatible with the field definitions
    
    Postconditions:
    - Returns a dictionary with exactly one entry for each header
    - Dictionary keys match the order of headers returned by self.headers
    - Values correspond to the parsed content of each field in the input line

## Side Effects:
    None

### `csvkit.convert.fixed.FixedWidthRowParser.headers` · *method*

*No documentation generated.*

## `csvkit.convert.fixed.SchemaDecoder` · *class*

*No documentation generated.*

### `csvkit.convert.fixed.SchemaDecoder.__init__` · *method*

*No documentation generated.*

### `csvkit.convert.fixed.SchemaDecoder.__call__` · *method*

*No documentation generated.*

