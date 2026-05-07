# `exceptions.py`

## `hypertools._shared.exceptions.HypertoolsError` · *class*

*No documentation generated.*

## `hypertools._shared.exceptions.HypertoolsBackendError` · *class*

*No documentation generated.*

### `hypertools._shared.exceptions.HypertoolsBackendError.__init__` · *method*

## Summary:
Initializes a HypertoolsBackendError instance with a descriptive error message.

## Description:
This method constructs a new HypertoolsBackendError exception object, setting up the error message that will be displayed when the exception is raised. It properly chains the initialization to its parent class and stores the message as an instance attribute for later retrieval.

## Args:
    message (str): A descriptive error message explaining the backend failure that occurred.

## Returns:
    None: This method initializes the object and does not return a value.

## Raises:
    None: This method does not raise any exceptions itself.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.message

## Constraints:
    Preconditions: The message argument must be a string.
    Postconditions: The exception object will have its message attribute set to the provided value.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes object attributes.

## `hypertools._shared.exceptions.HypertoolsIOError` · *class*

*No documentation generated.*

### `hypertools._shared.exceptions.HypertoolsIOError.__init__` · *method*

## Summary:
Initializes a HypertoolsIOError instance with a descriptive error message.

## Description:
This constructor sets up a custom exception that combines the functionality of a HypertoolsError and an OSError. It initializes the parent exception classes with the provided message and stores the message as an instance attribute for later retrieval.

## Args:
    message (str): A descriptive error message explaining the IO-related issue that occurred.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not raise any exceptions itself.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.message

## Constraints:
    Preconditions: The message parameter must be a string.
    Postconditions: The exception instance will have its message stored in self.message and will be properly initialized as both a HypertoolsError and OSError.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

