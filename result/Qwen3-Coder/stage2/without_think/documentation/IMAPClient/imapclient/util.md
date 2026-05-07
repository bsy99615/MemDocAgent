# `util.py`

## `imapclient.util.to_unicode` · *function*

## Summary:
Converts bytes to ASCII-encoded unicode string with graceful fallback handling for non-ASCII characters.

## Description:
This utility function normalizes input that can be either bytes or string into a unicode string. When the input is bytes, it attempts ASCII decoding, falling back to ignoring invalid characters if strict ASCII decoding fails. This ensures consistent string handling in environments where byte sequences might contain non-ASCII data.

## Args:
    s (Union[bytes, str]): Input that can be either bytes or string to be converted to unicode string

## Returns:
    str: Unicode string representation of the input, with bytes decoded using ASCII encoding

## Raises:
    None explicitly raised, but UnicodeDecodeError may occur internally during decoding operations

## Constraints:
    Preconditions:
    - Input must be either bytes or str type
    - If input is bytes, it should ideally contain only ASCII characters for clean conversion
    
    Postconditions:
    - Return value is always a unicode string
    - Non-ASCII bytes are handled gracefully via fallback mechanism

## Side Effects:
    - Writes warning message to module logger when fallback decoding occurs due to UnicodeDecodeError
    - No external state mutations or I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Input: Union[bytes,str]] --> B{Is instance bytes?}
    B -- Yes --> C[Try decode("ascii")]
    C --> D{UnicodeDecodeError?}
    D -- Yes --> E[Warning: fallback to ignore]
    E --> F[decode("ascii", "ignore")]
    D -- No --> G[Return decoded string]
    B -- No --> H[Return input as-is]
    F --> I[Return fallback result]
    G --> I
    H --> I
```

## Examples:
    # Normal string input
    result = to_unicode("hello")  # Returns "hello"
    
    # ASCII bytes input
    result = to_unicode(b"hello")  # Returns "hello"
    
    # Non-ASCII bytes with fallback
    result = to_unicode(b"hello\xff")  # Returns "hello" with warning logged
```

## `imapclient.util.to_bytes` · *function*

## Summary:
Converts a string or bytes object to bytes using the specified character encoding.

## Description:
This utility function provides a safe way to convert string objects to bytes, handling both string and bytes inputs gracefully. When given a string, it encodes the string using the specified character set. When given bytes, it returns the bytes unchanged. This abstraction simplifies working with IMAP protocol data that may arrive in either string or bytes format.

## Args:
    s (Union[bytes, str]): Input data that can be either a string or bytes object to be converted to bytes.
    charset (str): Character encoding to use when encoding strings. Defaults to "ascii".

## Returns:
    bytes: The input data converted to bytes. If input was already bytes, returns it unchanged.

## Raises:
    UnicodeEncodeError: When the string contains characters that cannot be encoded with the specified charset.

## Constraints:
    Preconditions:
        - The charset parameter must be a valid character encoding recognized by Python's encode() method
        - Input s must be either a string or bytes object
    
    Postconditions:
        - Always returns a bytes object
        - If input was bytes, the returned bytes are identical to the input
        - If input was string, the returned bytes represent the encoded string

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start to_bytes(s, charset)] --> B{isinstance(s, str)?}
    B -- Yes --> C[s.encode(charset)]
    B -- No --> D[s (already bytes)]
    C --> E[Return encoded bytes]
    D --> E
    E --> F[End]
```

## Examples:
    # Convert string to bytes with default ascii encoding
    result = to_bytes("hello")
    # Returns: b'hello'
    
    # Convert string to bytes with utf-8 encoding
    result = to_bytes("café", "utf-8")
    # Returns: b'caf\xc3\xa9'
    
    # Pass bytes unchanged
    result = to_bytes(b"hello")
    # Returns: b'hello'
```

## `imapclient.util.assert_imap_protocol` · *function*

## Summary:
Validates IMAP protocol compliance by raising a ProtocolError when server responses violate expected protocol behavior.

## Description:
This utility function serves as a protocol validation checkpoint that ensures IMAP server responses conform to expected protocol standards. When a protocol violation is detected, it raises a descriptive ProtocolError with contextual information about the violation.

The function extracts protocol validation logic into a dedicated utility to maintain clean separation between core IMAP operations and protocol compliance checking, making the codebase more modular and easier to test.

## Args:
    condition (bool): The boolean expression that must evaluate to True for protocol compliance
    message (Optional[bytes]): Optional server response message that provides additional context about the protocol violation

## Returns:
    None: This function does not return any value when the condition is met

## Raises:
    exceptions.ProtocolError: Raised when the condition evaluates to False, indicating an IMAP protocol violation

## Constraints:
    Preconditions:
    - The condition parameter must be a boolean value
    - If message is provided, it must be bytes that can be decoded with ASCII encoding
    
    Postconditions:
    - When condition is True, the function completes normally without raising an exception
    - When condition is False, the function raises ProtocolError with descriptive message

## Side Effects:
    None: This function performs no I/O operations or external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[assert_imap_protocol called] --> B{condition == False?}
    B -->|Yes| C[Construct base error message]
    C --> D{message provided?}
    D -->|Yes| E[Append message to error message (with formatting bug)]
    E --> F[Raise ProtocolError]
    D -->|No| G[Raise ProtocolError with base message]
    B -->|No| H[Return normally]
```

## Examples:
```python
# Valid protocol response - no exception raised
assert_imap_protocol(True)

# Invalid protocol response with message
server_response = b"BAD unexpected response"
assert_imap_protocol(False, server_response)
# Raises: exceptions.ProtocolError("Server replied with a response that violates the IMAP protocol: Server replied with a response that violates the IMAP protocol: BAD unexpected response")
```

## `imapclient.util.chunk` · *function*

## Summary:
Splits a sequence into fixed-size chunks and yields each chunk as a separate sequence.

## Description:
This utility function divides an input sequence into smaller subsequences of a specified maximum size. It's commonly used to process large datasets in manageable batches or to comply with API limitations that restrict batch sizes. The function returns a generator that yields chunks one at a time, making it memory-efficient for large sequences.

## Args:
    lst: A sequence (tuple, list, or other sliceable sequence) to be chunked
    size: Positive integer specifying the maximum number of elements in each chunk

## Returns:
    An iterator that yields subsequences of the original sequence, each with at most `size` elements

## Raises:
    ZeroDivisionError: When `size` is zero
    ValueError: When `size` is negative (though this depends on Python's range behavior)

## Constraints:
    Precondition: `size` must be a positive integer (greater than 0)
    Postcondition: Each yielded chunk will contain at most `size` elements from the original sequence

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[chunk function called] --> B{size > 0?}
    B -- No --> C[Raises ZeroDivisionError or undefined behavior]
    B -- Yes --> D[Initialize i=0]
    D --> E{i < len(lst)?}
    E -- No --> F[Stop iteration]
    E -- Yes --> G[Yield lst[i:i+size]]
    G --> H[i += size]
    H --> E
```

## Examples:
```python
# Basic usage with a list
data = [1, 2, 3, 4, 5, 6, 7, 8]
for chunk in chunk(data, 3):
    print(chunk)
# Output: [1, 2, 3], [4, 5, 6], [7, 8]

# Usage with tuple
words = ('apple', 'banana', 'cherry', 'date')
for chunk in chunk(words, 2):
    print(chunk)
# Output: ('apple', 'banana'), ('cherry', 'date')

# Empty list
for chunk in chunk([], 5):
    print(chunk)
# No output (empty iterator)

# Single element chunks
numbers = [1, 2, 3]
for chunk in chunk(numbers, 1):
    print(chunk)
# Output: [1], [2], [3]
```

