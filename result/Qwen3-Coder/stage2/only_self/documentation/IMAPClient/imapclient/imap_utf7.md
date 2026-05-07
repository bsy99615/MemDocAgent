# `imap_utf7.py`

## `imapclient.imap_utf7.encode` · *function*

## Summary:
Encodes a string or bytes object into IMAP UTF-7 format for safe transmission in IMAP protocol.

## Description:
Implements IMAP UTF-7 encoding as specified in RFC 3501, converting Unicode strings into a US-ASCII compatible format that can be safely transmitted over IMAP connections. This function handles both string inputs (which are encoded) and bytes inputs (which are returned unchanged). The encoding process converts non-ASCII characters into base64-encoded sequences while preserving ASCII printable characters directly.

## Args:
    s (Union[str, bytes]): Input string or bytes to encode. Strings are encoded using IMAP UTF-7 rules, while bytes are returned unchanged.

## Returns:
    bytes: IMAP UTF-7 encoded representation of the input. For string inputs, returns bytes containing the encoded data. For bytes inputs, returns the original bytes unchanged.

## Raises:
    None explicitly raised by this function, though underlying operations may raise exceptions from string handling or encoding.

## Constraints:
    Preconditions:
    - Input must be either a string or bytes object
    - String inputs should contain valid Unicode characters
    
    Postconditions:
    - Output is always bytes
    - ASCII printable characters (0x20-0x7E) are preserved directly in the output
    - Non-ASCII characters are encoded using base64 UTF-7 encoding
    - The special character '&' is encoded as "&-" to avoid conflicts with base64 encoding markers

## Side Effects:
    None - This is a pure function with no external state mutations or I/O operations.

## Control Flow:
```mermaid
flowchart TD
    A[Start with input s] --> B{Is s bytes?}
    B -- Yes --> C[Return s unchanged]
    B -- No --> D[Initialize result buffer and b64 buffer]
    D --> E[Process each character in s]
    E --> F{Character is ASCII printable (0x20-0x7E)?}
    F -- Yes --> G[Consume b64 buffer if not empty]
    G --> H{Character is '&' (0x26)?}
    H -- Yes --> I[Append "&-" to result]
    H -- No --> J[Append character to result]
    F -- No --> K[Add character to b64 buffer]
    K --> L[End of string?]
    L -- No --> E
    L -- Yes --> M[Consume remaining b64 buffer]
    M --> N[Return encoded bytes]
```

## Examples:
    # Encode a simple ASCII string
    encoded = encode("INBOX")
    # Returns: b'INBOX'
    
    # Encode a string with non-ASCII characters
    encoded = encode("Inbox with café")
    # Returns: b'Inbox with caf&AOk-'
    
    # Encode bytes (returns unchanged)
    encoded = encode(b"already encoded bytes")
    # Returns: b"already encoded bytes"

## `imapclient.imap_utf7.decode` · *function*

## Summary:
Decodes IMAP UTF-7 encoded byte sequences into standard UTF-8 strings by processing base64-encoded sections marked with ampersand (&) and dash (-) delimiters.

## Description:
This function implements IMAP UTF-7 decoding logic that transforms byte sequences containing base64-encoded UTF-7 data into properly decoded UTF-8 strings. It specifically handles the IMAP UTF-7 encoding convention where non-ASCII characters are represented using base64 encoding enclosed between '&' and '-' characters.

The function processes input bytes character by character, maintaining a buffer for base64 data. When encountering the '&' character (ASCII 38) at the start of a sequence, it begins collecting base64 data. When encountering the '-' character (ASCII 45) that terminates a base64 sequence, it decodes the buffered data using the base64_utf7_decode helper function and appends the result to the output.

This logic is extracted into its own function to separate the concerns of IMAP UTF-7 decoding from other IMAP operations, providing a clean interface for handling mailbox names and other UTF-7 encoded data in IMAP protocols.

## Args:
    s (Union[bytes, str]): Input data to decode, either as bytes (for IMAP UTF-7 encoded data) or string (already decoded). The bytes should contain valid IMAP UTF-7 encoded data.

## Returns:
    str: Decoded UTF-8 string representation of the input data. If input is already a string, it is returned unchanged.

## Raises:
    UnicodeDecodeError: When base64_utf7_decode fails to decode base64 data segments
    TypeError: When base64_utf7_decode receives invalid input type (propagated from helper function)

## Constraints:
    Preconditions:
        - Input must be either bytes or string type
        - If input is bytes, it should contain valid IMAP UTF-7 encoded data
        - AMPERSAND_ORD and DASH_ORD constants must be defined in the module
        - base64_utf7_decode function must be available in the module scope
    Postconditions:
        - Output is a properly decoded UTF-8 string
        - All base64-encoded sections are correctly processed
        - Any remaining unprocessed buffer data is handled appropriately

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start decode function] --> B{Input is bytes?}
    B -->|No| C[Return input as-is]
    B -->|Yes| D[Initialize result list and empty buffer]
    D --> E[Process each byte in input]
    E --> F{Byte equals AMPERSAND_ORD (38) AND buffer empty?}
    F -->|Yes| G[Add '&' to buffer]
    F -->|No| H{Byte equals DASH_ORD (45) AND buffer not empty?}
    H -->|Yes| I{Buffer length = 1?}
    I -->|Yes| J[Append "&" to result]
    I -->|No| K[Decode buffer data and append to result]
    J --> L[Clear buffer]
    K --> L
    L --> M{More bytes?}
    M -->|Yes| E
    M -->|No| N[Process remaining buffer if any]
    N --> O[Join result list and return]
```

## Examples:
    # Decode simple ASCII text
    result = decode(b"Hello World")
    # Returns "Hello World"
    
    # Decode IMAP UTF-7 encoded data
    result = decode(b"Mailbox&AP8-")
    # Returns "Mailbox\u00f6" (where \u00f6 is the umlaut character)
    
    # Handle mixed content
    result = decode(b"Folder&AP8-Name")
    # Returns "Folder\u00f6Name"
    
    # String input (no change)
    result = decode("Already decoded")
    # Returns "Already decoded"
```

## `imapclient.imap_utf7.base64_utf7_encode` · *function*

## Summary:
Encodes a list of UTF-8 strings into a base64-encoded UTF-16BE byte sequence using IMAP-specific encoding rules.

## Description:
This function performs IMAP UTF-7 encoding by joining a list of string segments, converting them to UTF-16BE byte encoding, and then applying base64 encoding with IMAP-specific transformations. It's used to encode mailbox names containing non-ASCII characters according to IMAP standards.

## Args:
    buffer (List[str]): A list of string segments to be encoded. These typically represent parts of a mailbox name that need UTF-7 encoding.

## Returns:
    bytes: The base64-encoded representation of the UTF-16BE encoded input strings, with IMAP-specific formatting applied (newlines and padding stripped, forward slashes replaced with commas).

## Raises:
    None explicitly raised, but may raise exceptions from underlying operations like string concatenation or encoding.

## Constraints:
    Preconditions:
    - Input buffer should contain valid UTF-8 strings
    - The function assumes proper UTF-16BE encoding requirements for IMAP compatibility
    
    Postconditions:
    - Output is always bytes representing properly formatted IMAP UTF-7 encoded data
    - The result follows IMAP's base64 encoding conventions (no newlines, no padding, comma instead of slash)

## Side Effects:
    None - This is a pure function with no external state mutations or I/O operations.

## Control Flow:
```mermaid
flowchart TD
    A[Start with List[str] buffer] --> B[Join all strings]
    B --> C[Encode as UTF-16BE bytes]
    C --> D[Base64 encode with binascii.b2a_base64]
    D --> E[Strip trailing newline and equals signs]
    E --> F[Replace forward slashes with commas]
    F --> G[Return resulting bytes]
```

## Examples:
    # Basic usage with single string
    result = base64_utf7_encode(["Hello"])
    # Returns: b'SGVsbG8=' (base64 of "Hello" in UTF-16BE)
    
    # Usage with multiple strings
    result = base64_utf7_encode(["Hello", " ", "World"])
    # Returns: b'SGVsbG8gV29ybGQ=' (base64 of "Hello World" in UTF-16BE)
```

## `imapclient.imap_utf7.base64_utf7_decode` · *function*

## Summary:
Decodes a base64-encoded UTF-7 string by transforming the input bytearray into a proper UTF-7 format and then decoding it.

## Description:
This function processes a bytearray representing a modified base64-encoded string and converts it into a properly formatted UTF-7 encoded string. It prepends a "+" character and appends a "-" character to the input, replacing commas with forward slashes, then decodes the result using UTF-7 encoding. This is typically used in IMAP protocol implementations where UTF-7 encoding is required for mailbox names containing non-ASCII characters.

In IMAP UTF-7 encoding, base64 data is represented with a "+" prefix and "-" suffix, with commas replaced by forward slashes. This function performs the reverse transformation to recover the original UTF-7 string.

## Args:
    s (bytearray): Input bytearray containing base64-encoded data with comma separators

## Returns:
    str: Decoded UTF-7 string representation of the input data

## Raises:
    UnicodeDecodeError: When the transformed byte sequence cannot be decoded using UTF-7 encoding
    TypeError: When the input is not a bytearray

## Constraints:
    Preconditions:
        - Input must be a valid bytearray
        - The bytearray should represent valid base64 data with comma separators
    Postconditions:
        - Output is a properly decoded UTF-7 string
        - The transformation maintains the semantic meaning of the original encoded data

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input bytearray s] --> B{Transform s}
    B --> C[Prepend b"+" to s]
    C --> D[Replace b"," with b"/" in s]
    D --> E[Append b"-" to s]
    E --> F[Decode using utf-7 encoding]
    F --> G[Return decoded string]
```

## Examples:
    # Basic usage - decode base64 data
    input_data = bytearray(b"SGVsbG8")  # "Hello" in base64
    result = base64_utf7_decode(input_data)
    # Result would be the UTF-7 decoded version of "+SGVsbG8-"
    
    # Empty bytearray case
    empty_input = bytearray()
    result = base64_utf7_decode(empty_input)
    # Result would be the UTF-7 decoded version of "+-"
    
    # With comma separators
    input_with_commas = bytearray(b"SGVsbG8,sGVsbG8")  # "Hello,Hello" in base64
    result = base64_utf7_decode(input_with_commas)
    # Result would be the UTF-7 decoded version of "+SGVsbG8/sGVsbG8-"

