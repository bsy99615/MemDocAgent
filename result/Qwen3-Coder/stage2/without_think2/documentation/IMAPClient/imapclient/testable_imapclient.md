# `testable_imapclient.py`

## `imapclient.testable_imapclient.TestableIMAPClient` · *class*

## Summary:
TestableIMAPClient is a subclass of IMAPClient designed for testing purposes, providing a mockable IMAP4 implementation that replaces the real IMAP connection with a testable mock object.

## Description:
This class extends the standard IMAPClient to facilitate unit testing by substituting the actual IMAP4 connection with a MockIMAP4 instance. It is specifically intended for use in test environments where real network connections to IMAP servers should be avoided. The class acts as a factory for creating mock IMAP4 objects, enabling comprehensive testing of IMAP-related functionality without external dependencies.

## State:
- host (inherited from IMAPClient): str, set to "somehost" in initialization
- _create_IMAP4 method: callable, returns a MockIMAP4 instance for testing purposes
- All other attributes inherited from IMAPClient remain unchanged

## Lifecycle:
- Creation: Instantiated with no arguments, automatically initializes with host="somehost"
- Usage: Used primarily in test suites where IMAP operations need to be mocked; the _create_IMAP4 method is invoked internally during connection setup to create a mock IMAP4 object for testing IMAP operations without network dependencies
- Destruction: Inherits standard object cleanup behavior from IMAPClient

## Method Map:
```mermaid
graph TD
    A[TestableIMAPClient.__init__] --> B[TestableIMAPClient._create_IMAP4]
    B --> C[MockIMAP4()]
```

## Raises:
- No explicit exceptions raised during __init__
- Exceptions from parent IMAPClient.__init__ may propagate if host parameter validation fails

## Example:
```python
# Create testable IMAP client
test_client = TestableIMAPClient()

# The client uses MockIMAP4 internally for testing
mock_imap4 = test_client._create_IMAP4()  # Returns MockIMAP4 instance

# This allows testing IMAP operations without network connectivity
```

### `imapclient.testable_imapclient.TestableIMAPClient.__init__` · *method*

## Summary:
Initializes a TestableIMAPClient instance with a fixed host value for testing purposes.

## Description:
This method initializes the TestableIMAPClient by calling the parent IMAPClient constructor with a predetermined host value "somehost". As a subclass of IMAPClient, this initialization ensures the object is properly configured for testing scenarios where real IMAP server connections are undesirable. The fixed host value provides consistent test behavior while maintaining full compatibility with the IMAPClient interface.

## Args:
    None

## Returns:
    None

## Raises:
    Exception: May raise exceptions from the parent IMAPClient.__init__ method if host parameter validation fails

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - host: Set to "somehost" (inherited from IMAPClient)

## Constraints:
    Preconditions: None
    Postconditions: The instance is properly initialized with host="somehost"

## Side Effects:
    None

### `imapclient.testable_imapclient.TestableIMAPClient._create_IMAP4` · *method*

## Summary:
Creates and returns a new MockIMAP4 instance for testing IMAP operations without network dependencies.

## Description:
This method serves as a factory for creating mock IMAP4 client instances used exclusively in testing scenarios. It encapsulates the creation logic to enable dependency injection and mocking capabilities within the TestableIMAPClient class. The method is called during test setup phases when a mock IMAP connection is required to simulate real IMAP server interactions.

## Args:
    None

## Returns:
    MockIMAP4: A new instance of the MockIMAP4 class, which provides a testable substitute for the real IMAPClient.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns a valid MockIMAP4 instance that inherits from unittest.mock.Mock

## Side Effects:
    None

## `imapclient.testable_imapclient.MockIMAP4` · *class*

## Summary:
A mock implementation of an IMAP4 client used for testing purposes, inheriting from Python's unittest.mock.Mock class.

## Description:
This class provides a testable substitute for the real IMAPClient from the imapclient library. It simulates the behavior of an IMAP4 connection for unit testing without requiring actual network communication. The class is designed to capture sent commands and simulate basic IMAP protocol interactions while maintaining compatibility with the expected interface of the real IMAPClient.

## State:
- use_uid: bool, always set to True, indicating UID-based operations are enabled
- sent: bytes, accumulates all data sent through the send() method
- tagged_commands: dict, stores command-tag mappings (type not specified, but likely used for tracking IMAP command responses)
- _starttls_done: bool, tracks whether STARTTLS has been completed (initially False)

## Lifecycle:
- Creation: Instantiated like any Mock object, accepts arbitrary arguments and keyword arguments
- Usage: Typically used in test contexts where IMAP operations need to be mocked; methods like send() and _new_tag() are called during IMAP protocol simulation
- Destruction: Inherits standard Mock cleanup behavior

## Method Map:
```mermaid
graph TD
    A[MockIMAP4.__init__] --> B[MockIMAP4.send]
    A --> C[MockIMAP4._new_tag]
    B --> D[Updates self.sent]
    C --> E[Returns "tag"]
```

## Raises:
- No explicit exceptions raised by __init__
- All methods are designed to be safe for mocking purposes

## Example:
```python
# Create mock instance
mock_client = MockIMAP4()

# Send data (simulates sending IMAP command)
mock_client.send(b"LOGIN user password\r\n")

# Check what was sent
print(mock_client.sent)  # b"LOGIN user password\r\n"

# Get new tag
tag = mock_client._new_tag()  # Returns "tag"
```

### `imapclient.testable_imapclient.MockIMAP4.__init__` · *method*

## Summary:
Initializes a MockIMAP4 instance with default mock behaviors and state tracking attributes.

## Description:
This method sets up the mock IMAP client by initializing its parent class and configuring several internal state variables that enable mocking of IMAP protocol interactions. It establishes default behavior for UID usage and initializes tracking mechanisms for sent commands and tagged operations.

## Args:
    *args (Any): Variable length argument list passed to the parent IMAPClient constructor
    **kwargs (Any): Arbitrary keyword arguments passed to the parent IMAPClient constructor

## Returns:
    None: This method does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.use_uid: Set to True to enable UID-based operations
    - self.sent: Initialized as empty bytes to accumulate sent command data
    - self.tagged_commands: Initialized as empty dictionary to track tagged IMAP commands
    - self._starttls_done: Initialized as False to track TLS negotiation status

## Constraints:
    Preconditions: None
    Postconditions: 
    - The parent IMAPClient is properly initialized with provided arguments
    - All mock tracking attributes are initialized with appropriate default values
    - The instance is ready to intercept and record IMAP protocol interactions

## Side Effects:
    None: This method performs no external I/O or service calls

### `imapclient.testable_imapclient.MockIMAP4.send` · *method*

## Summary:
Accumulates outgoing data sent to the IMAP server by appending it to an internal buffer.

## Description:
This method serves as a mock implementation of the IMAP client's send operation, capturing all data sent to the server for testing purposes. It appends the provided byte data to an internal buffer (`self.sent`) that can be inspected by tests to verify communication with the mock server.

## Args:
    data (bytes): The raw byte data to be sent to the IMAP server.

## Returns:
    None: This method does not return any value.

## Raises:
    No exceptions are explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.sent

## Constraints:
    Preconditions: The object must be properly initialized as a MockIMAP4 instance.
    Postconditions: The `self.sent` attribute will contain the concatenation of all previously sent data and the new data provided.

## Side Effects:
    Mutation: Modifies the `self.sent` attribute by appending the input data.

### `imapclient.testable_imapclient.MockIMAP4._new_tag` · *method*

## Summary:
Returns a fixed string "tag" used for identifying IMAP protocol commands in mock testing scenarios.

## Description:
This method generates a placeholder tag string that would normally be unique for each IMAP command sent to a server. In the context of MockIMAP4, which is designed for testing IMAP client functionality without network communication, this method provides a consistent return value to simulate the tag generation process. The method is called during IMAP command construction when a new tag is required for protocol compliance.

## Args:
    self: The MockIMAP4 instance

## Returns:
    str: The literal string "tag" used as a placeholder identifier for IMAP commands

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "tag"

## Side Effects:
    None

