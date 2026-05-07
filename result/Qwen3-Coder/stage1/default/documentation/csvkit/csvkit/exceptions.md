# `exceptions.py`

## `csvkit.exceptions.CustomException` · *class*

## Summary:
A custom exception class that provides a simple way to raise exceptions with a customizable message.

## Description:
This class extends Python's built-in Exception class to provide a straightforward mechanism for raising exceptions with user-defined messages. It serves as a base exception type that can be used throughout the csvkit library to signal error conditions in a consistent manner.

The CustomException is designed to be lightweight and focused solely on providing a message-based exception mechanism. It's intended to be instantiated by various components within the csvkit library when they encounter error conditions that need to be communicated to calling code.

## State:
- msg (str): The error message associated with this exception instance. This is the sole attribute of the class and must be a string. It has no specific constraints beyond being a string value.

## Lifecycle:
- Creation: Instances are created by calling `CustomException(message)` where message is a string describing the error condition.
- Usage: Once created, the exception can be raised using the `raise` keyword. The exception will propagate up the call stack until caught by an appropriate exception handler.
- Destruction: No special cleanup is required as Python handles the lifecycle automatically.

## Method Map:
```mermaid
graph TD
    A[CustomException(msg)] --> B{__init__}
    B --> C[__unicode__]
    B --> D[__str__]
    C --> E[Raise Exception]
    D --> E
```

## Raises:
- This class itself does not raise any exceptions during initialization
- The only way it raises an exception is when it's raised by code that catches and re-raises it

## Example:
```python
# Creating and raising the exception
try:
    raise CustomException("CSV file is malformed")
except CustomException as e:
    print(f"Caught exception: {e}")
    # Output: Caught exception: CSV file is malformed
```

### `csvkit.exceptions.CustomException.__init__` · *method*

## Summary:
Initializes a CustomException instance with an error message.

## Description:
Sets the error message for this exception instance. This method is part of the CustomException class which provides a simple wrapper around Python's built-in Exception class to allow for custom error messages.

## Args:
    msg (str): The error message to associate with this exception instance.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.msg

## Constraints:
    Preconditions: The msg parameter should be a string or an object that can be converted to a string.
    Postconditions: After execution, the self.msg attribute will contain the provided message.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `csvkit.exceptions.CustomException.__unicode__` · *method*

## Summary:
Returns the string representation of the custom exception by returning its stored message.

## Description:
This method provides the unicode string representation of the CustomException instance. It is part of the standard Python exception interface and ensures that when the exception is converted to a string (either explicitly or implicitly), it returns the stored error message.

## Args:
    None

## Returns:
    str: The message string stored in self.msg

## Raises:
    None

## State Changes:
    Attributes READ: self.msg
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The instance must have been initialized with a msg parameter, meaning self.msg must be set
    Postconditions: The returned value is identical to the message originally provided during initialization

## Side Effects:
    None

### `csvkit.exceptions.CustomException.__str__` · *method*

## Summary:
Returns the string representation of the custom exception by returning its stored message.

## Description:
This method provides the string representation of a CustomException instance, which is used when the exception is printed or converted to a string. It returns the message stored in the exception's msg attribute, making error messages more readable and informative.

## Args:
    None

## Returns:
    str: The message string stored in self.msg

## Raises:
    None

## State Changes:
    Attributes READ: self.msg
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The exception instance must have a msg attribute containing a string
    Postconditions: The returned value is identical to the message originally provided during exception creation

## Side Effects:
    None

## `csvkit.exceptions.ColumnIdentifierError` · *class*

## Summary:
A custom exception raised when a column identifier cannot be resolved or is invalid in CSV processing operations.

## Description:
The ColumnIdentifierError is a specialized exception that indicates problems with column identification during CSV processing. This exception is typically raised when attempting to reference a column by name or index that does not exist, or when the column identifier format is invalid for the operation being performed.

This exception inherits from CustomException, providing a consistent error handling pattern throughout the csvkit library. It serves as a clear indicator to calling code that a column-related issue has occurred, allowing for graceful error recovery or informative error messages to be presented to users.

## State:
- Inherits all attributes from CustomException, specifically the msg attribute (str) that contains the error message
- No additional attributes are defined in this class
- The msg parameter follows the same constraints as CustomException: it must be a string describing the column identifier problem

## Lifecycle:
- Creation: Instantiate using `ColumnIdentifierError(message)` where message describes the specific column identifier issue
- Usage: Raise the exception using `raise ColumnIdentifierError("message")` when column resolution fails
- Destruction: Handled automatically by Python's exception mechanism

## Method Map:
```mermaid
graph TD
    A[ColumnIdentifierError(message)] --> B{__init__ inherits from CustomException}
    B --> C[Raise Exception]
```

## Raises:
- This class does not raise any exceptions itself
- It inherits the standard Exception behavior from CustomException
- When raised, it propagates up the call stack until caught by an appropriate exception handler

## Example:
```python
# Example of raising ColumnIdentifierError
try:
    # Attempting to access a non-existent column
    column_data = csv_reader.get_column('non_existent_column')
except ColumnIdentifierError as e:
    print(f"Column error: {e}")
    # Output: Column error: Column 'non_existent_column' not found

# Another scenario
try:
    # Invalid column index
    column_data = csv_reader.get_column(-1)
except ColumnIdentifierError as e:
    print(f"Column error: {e}")
    # Output: Column error: Invalid column index '-1'
```

## `csvkit.exceptions.CSVTestException` · *class*

## Summary:
A custom exception class for CSV validation errors that provides contextual information about the specific line and row where the error occurred.

## Description:
CSVTestException is designed to be raised during CSV file validation or testing processes when a data inconsistency or formatting issue is detected. This exception extends CustomException and provides additional context by storing the line number and row data that caused the validation failure, making debugging easier for developers working with CSV processing.

The exception is typically instantiated by CSV validation routines when they encounter malformed data, missing fields, or other inconsistencies in CSV files. It serves as a specialized error reporting mechanism that helps pinpoint exactly where in the CSV file an issue occurred.

## State:
- line_number (int): The line number in the CSV file where the validation error occurred. Must be a positive integer representing the actual line position in the file.
- row (list or dict): The row data that triggered the validation error. This could be a list of field values or a dictionary mapping column names to values, depending on how the CSV was parsed.
- msg (str): The error message describing the specific validation failure. Must be a string explaining what went wrong.

## Lifecycle:
- Creation: Instantiate using `CSVTestException(line_number, row, msg)` where line_number is the line position, row contains the problematic data, and msg describes the error.
- Usage: Raise the exception using `raise CSVTestException(...)` to signal validation failures during CSV processing.
- Destruction: Automatically handled by Python's exception handling mechanism.

## Method Map:
```mermaid
graph TD
    A[CSVTestException(line_number, row, msg)] --> B{__init__}
    B --> C[super().__init__(msg)]
    B --> D[line_number = line_number]
    B --> E[row = row]
    C --> F[Raise Exception]
```

## Raises:
- This class does not raise any exceptions during initialization
- The only way it raises an exception is when it's raised by code that catches and re-raises it

## Example:
```python
# Example of creating and raising a CSVTestException
try:
    # Simulate finding an invalid row at line 5
    problematic_row = ['field1', 'field2', None]
    raise CSVTestException(5, problematic_row, "Missing required field in row")
except CSVTestException as e:
    print(f"Error on line {e.line_number}: {e.msg}")
    print(f"Problematic row data: {e.row}")
    # Output: Error on line 5: Missing required field in row
    #         Problematic row data: ['field1', 'field2', None]
```

### `csvkit.exceptions.CSVTestException.__init__` · *method*

## Summary:
Initializes a CSV test exception with line number, row data, and error message.

## Description:
Constructs a CSVTestException instance that captures contextual information about a CSV validation failure, including the line number where the error occurred, the row data that caused the issue, and a descriptive error message. This exception is designed for use in CSV processing pipelines where detailed error reporting is needed.

## Args:
    line_number (int): The line number in the CSV file where the validation error occurred.
    row (list): The row data that triggered the validation error.
    msg (str): A descriptive error message explaining the nature of the validation failure.

## Returns:
    None: This method initializes the exception object and does not return a value.

## Raises:
    None: This method does not raise any exceptions itself.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.line_number: Stores the line number where the CSV validation error occurred
        - self.row: Stores the row data that caused the validation error

## Constraints:
    Preconditions: 
        - line_number should be a positive integer representing a valid line in the CSV file
        - row should be a list-like object containing the CSV row data
        - msg should be a string describing the validation error
    Postconditions:
        - The exception object will have self.line_number set to the provided line_number
        - The exception object will have self.row set to the provided row
        - The exception object will inherit the msg attribute from the parent CustomException class

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

## `csvkit.exceptions.LengthMismatchError` · *class*

## Summary:
A custom exception raised when a CSV row contains a different number of columns than expected during validation.

## Description:
LengthMismatchError is specifically designed to handle CSV validation scenarios where a row's column count doesn't match the expected column count. This exception extends CSVTestException and provides detailed context about the mismatch, including the line number, actual row data, and expected vs. actual column counts.

This exception is typically raised by CSV validation routines when processing CSV files that have inconsistent row lengths, helping developers quickly identify malformed rows in their data files. The exception serves as a specialized error reporting mechanism that makes debugging CSV parsing issues more straightforward.

## State:
- line_number (int): The line number in the CSV file where the column count mismatch occurred. Must be a positive integer representing the actual line position in the file.
- row (list or dict): The row data that caused the column count mismatch. This could be a list of field values or a dictionary mapping column names to values.
- expected_length (int): The number of columns that were expected in the row. Must be a positive integer.
- msg (str): The error message describing the specific column count mismatch. Automatically generated as "Expected %i columns, found %i columns".

## Lifecycle:
- Creation: Instantiate using `LengthMismatchError(line_number, row, expected_length)` where line_number is the line position, row contains the problematic data, and expected_length specifies the expected column count.
- Usage: Raise the exception using `raise LengthMismatchError(...)` to signal column count mismatches during CSV processing.
- Destruction: Automatically handled by Python's exception handling mechanism.

## Method Map:
```mermaid
graph TD
    A[LengthMismatchError(line_number, row, expected_length)] --> B{__init__}
    B --> C[msg = 'Expected %i columns, found %i columns' % (expected_length, len(row))]
    B --> D[super().__init__(line_number, row, msg)]
    D --> E[CSVTestException.__init__]
    E --> F[Raise Exception]
    G[LengthMismatchError.length] --> H{property}
    H --> I[len(self.row)]
```

## Raises:
- This class does not raise any exceptions during initialization
- The only way it raises an exception is when it's raised by code that catches and re-raises it

## Example:
```python
# Example of creating and raising a LengthMismatchError
try:
    # Simulate finding a row with 3 columns when 4 were expected at line 10
    problematic_row = ['field1', 'field2', 'field3']
    raise LengthMismatchError(10, problematic_row, 4)
except LengthMismatchError as e:
    print(f"Error on line {e.line_number}: {e.msg}")
    print(f"Row had {e.length} columns instead of {e.expected_length}")
    # Output: Error on line 10: Expected 4 columns, found 3 columns
    #         Row had 3 columns instead of 4
```

### `csvkit.exceptions.LengthMismatchError.__init__` · *method*

## Summary:
Initializes a LengthMismatchError exception with line number, row data, and expected column count to report column count mismatches in CSV processing.

## Description:
This method constructs a LengthMismatchError exception that indicates a CSV row contains a different number of columns than expected during validation or processing. The exception is typically raised when validating CSV data integrity, particularly when rows don't conform to the expected schema.

The method formats a descriptive error message indicating both the expected column count and the actual column count found in the problematic row. This allows calling code to provide meaningful diagnostic information to users about CSV parsing issues.

This method is part of the csvkit.exceptions module and inherits from CSVTestException, which in turn inherits from CustomException. It's designed to be used specifically for reporting column count mismatches in CSV data validation workflows.

## Args:
    line_number (int): The line number in the CSV file where the mismatch occurred
    row (list): The row data that caused the mismatch, typically containing column values
    expected_length (int): The expected number of columns for the row

## Returns:
    None: This method initializes the exception object and does not return a value. The initialized exception instance is available through standard exception handling mechanisms.

## Raises:
    None: This method does not raise any exceptions itself

## State Changes:
    Attributes READ: 
    - self.row (accessed via len(row) to determine actual column count)
    
    Attributes WRITTEN:
    - self.line_number (set from the line_number parameter)
    - self.row (set from the row parameter)
    - self.msg (set via the formatted message)

## Constraints:
    Preconditions:
    - line_number must be a positive integer representing a valid line in the CSV file
    - row must be iterable (typically a list) containing column data
    - expected_length must be a non-negative integer representing the expected column count
    
    Postconditions:
    - The exception instance will have self.line_number set to the provided line_number
    - The exception instance will have self.row set to the provided row
    - The exception instance will have self.msg set to a formatted error message

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes and creates a formatted string message. The method relies on the parent class constructor chain to properly initialize the exception hierarchy.

### `csvkit.exceptions.LengthMismatchError.length` · *method*

## Summary:
Returns the number of columns in the CSV row that caused a length mismatch error.

## Description:
This property provides access to the actual column count of the problematic CSV row that triggered a LengthMismatchError. It is used primarily for error reporting and debugging purposes to show the discrepancy between expected and actual column counts in CSV validation.

The method is called during CSV validation processes when a row doesn't match the expected column structure. It allows consumers of the exception to programmatically access the row's actual length without having to manually calculate it from the row data.

## Args:
    None

## Returns:
    int: The number of elements in the row list/dict that caused the validation error.

## Raises:
    None

## State Changes:
    Attributes READ: self.row
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The LengthMismatchError instance must have been properly initialized with a row parameter
    Postconditions: The returned value is always a non-negative integer representing the length of the stored row

## Side Effects:
    None

## `csvkit.exceptions.InvalidValueForTypeException` · *class*

## Summary:
An exception raised when a value cannot be converted to a specified data type at a given index.

## Description:
This exception is thrown when attempting to convert a value to a specific data type fails during CSV processing operations. It provides detailed information about the conversion failure, including the index of the problematic value, the value itself, and the target type that failed to convert.

The exception is typically raised by CSV processing utilities when encountering data that doesn't conform to expected types, such as trying to parse a non-numeric string into an integer field or converting a date string to a datetime type when the format is invalid.

## State:
- index (int): The zero-based index position where the conversion failure occurred
- value (str): The string value that could not be converted to the target type
- normal_type (str): The target data type that the conversion was attempted for

## Lifecycle:
- Creation: Instantiate with `InvalidValueForTypeException(index, value, normal_type)` where index is an integer, value is a string, and normal_type is a string describing the expected type
- Usage: Raise the exception using `raise InvalidValueForTypeException(...)` to signal a type conversion failure
- Destruction: Automatically handled by Python's exception handling mechanism

## Method Map:
```mermaid
graph TD
    A[InvalidValueForTypeException(index, value, normal_type)] --> B{__init__}
    B --> C[Set index, value, normal_type attributes]
    B --> D[Build error message]
    D --> E[Call super().__init__(msg)]
    E --> F[Raise Exception]
```

## Raises:
- This class does not raise any exceptions itself during initialization
- It raises the exception when it is raised by code that catches and re-raises it

## Example:
```python
# Example of creating and raising the exception
try:
    # Attempting to convert a non-numeric string to integer
    raise InvalidValueForTypeException(5, "not_a_number", "int")
except InvalidValueForTypeException as e:
    print(f"Conversion failed at index {e.index}: {e.value} cannot be converted to {e.normal_type}")
    # Output: Conversion failed at index 5: not_a_number cannot be converted to int
```

### `csvkit.exceptions.InvalidValueForTypeException.__init__` · *method*

## Summary:
Initializes an exception for invalid type conversion with index, value, and expected type information.

## Description:
Constructs an InvalidValueForTypeException instance that records the position, value, and expected type that caused a conversion failure. This method serves as the constructor for the exception class, setting up the error context and formatting an informative error message.

## Args:
    index (int): The zero-based index where the invalid value was encountered.
    value (str): The string value that could not be converted to the expected type.
    normal_type (str): The target type that the value was expected to be converted to.

## Returns:
    None: This method initializes the exception object and does not return a value.

## Raises:
    None: This method does not raise any exceptions itself.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.index, self.value, self.normal_type

## Constraints:
    Preconditions: All arguments must be provided and of the correct types (index should be int, value and normal_type should be str).
    Postconditions: The exception instance will have self.index, self.value, and self.normal_type set to the provided values, and the error message will be properly formatted.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes instance attributes and constructs a string message.

## `csvkit.exceptions.RequiredHeaderError` · *class*

## Summary:
A custom exception indicating that a required header field is missing from a CSV file.

## Description:
The RequiredHeaderError exception is raised when a CSV processing operation encounters a situation where a required header field is absent from the input data. This exception serves as a specialized error type that allows callers to distinguish between different kinds of CSV processing failures, particularly those related to missing header fields.

This exception inherits from CustomException, which provides a basic message-based exception mechanism. The purpose of creating this specific subclass is to enable more granular error handling in CSV processing workflows where missing headers represent a distinct failure mode from other types of CSV parsing errors.

## State:
- Inherits all state from CustomException parent class
- The exception instance contains a message describing the missing header issue
- No additional attributes are defined in this class

## Lifecycle:
- Creation: Instantiated by calling `RequiredHeaderError(message)` where message describes the missing header
- Usage: Raised using the `raise` keyword when header validation fails
- Destruction: Handled automatically by Python's exception mechanism

## Method Map:
```mermaid
graph TD
    A[RequiredHeaderError(message)] --> B{__init__ inherited from CustomException}
    B --> C[Raise Exception]
```

## Raises:
- This class itself does not raise exceptions during initialization
- The exception is raised when code detects a missing required header and executes `raise RequiredHeaderError(...)`

## Example:
```python
# Example usage in CSV processing
try:
    if 'email' not in csv_headers:
        raise RequiredHeaderError("Required header 'email' is missing from CSV file")
except RequiredHeaderError as e:
    print(f"Header validation failed: {e}")
    # Output: Header validation failed: Required header 'email' is missing from CSV file
```

