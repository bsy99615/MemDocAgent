# `imap_utf7.py`

## `imapclient.imap_utf7.encode` · *function*

## Summary:
Encodes a string or bytes object using IMAP UTF-7 encoding, converting non-ASCII characters to base64 representation while preserving ASCII characters as-is.

## Description:
This function implements IMAP UTF-7 encoding as specified in RFC 3501. It processes input character by character, maintaining a buffer for non-ASCII characters that are then encoded using base64 UTF-7 encoding. ASCII characters in the range 0x20-0x7E are preserved directly, except for the '&' character which is specially encoded as "&-". The function is designed to handle both string and bytes inputs gracefully.

## Args:
    s (Union[str, bytes]): Input string or bytes to encode. If bytes are provided, they are returned unchanged.

## Returns:
    bytes: The IMAP UTF-7 encoded representation of the input string. Non-ASCII characters are encoded using base64 UTF-7 format, while ASCII characters remain unchanged.

## Raises:
    None explicitly raised by this function, though underlying operations may raise exceptions during encoding.

## Constraints:
    Preconditions:
    - Input must be either a string or bytes object
    - String input should contain valid Unicode characters
    
    Postconditions:
    - Output is always bytes
    - ASCII characters in range 0x20-0x7E are preserved as-is (except '&' becomes "&-")
    - Non-ASCII characters are encoded using base64 UTF-7 format

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start encode(s)] --> B{isinstance(s, str)?}
    B -- No --> C[return s]
    B -- Yes --> D[Initialize res, b64_buffer]
    D --> E[for each character c in s]
    E --> F{ord(c) in range 0x20-0x7E?}
    F -- Yes --> G[consume_b64_buffer(b64_buffer)]
    G --> H{c == '&'?}
    H -- Yes --> I[res.extend(b"&-")]
    H -- No --> J[res.append(ord(c))]
    F -- No --> K[b64_buffer.append(c)]
    E --> L{end of string?}
    L -- No --> E
    L -- Yes --> M[consume_b64_buffer(b64_buffer)]
    M --> N[return bytes(res)]
```

## Examples:
    >>> encode("Hello World")
    b'Hello World'
    
    >>> encode("Hello & World")
    b'Hello &- World'
    
    >>> encode("café")
    b'caf&AOk-'
    
    >>> encode(b"already bytes")
    b'already bytes'
```

## `imapclient.imap_utf7.decode` · *function*

## Summary:
Decodes IMAP UTF-7 encoded byte sequences into standard Unicode strings.

## Description:
Converts IMAP UTF-7 encoded bytes or strings back to their original Unicode representation. This function handles the special encoding scheme used by IMAP servers where non-ASCII characters are represented using base64-encoded sequences prefixed with '&' and terminated with '-'. The function is part of the IMAP UTF-7 encoding/decoding utilities.

## Args:
    s (Union[bytes, str]): Input string or bytes to decode. If already a string, it is returned unchanged.

## Returns:
    str: Decoded Unicode string with IMAP UTF-7 encoded sequences converted to proper Unicode characters.

## Raises:
    Exception: May raise exceptions from the underlying base64_utf7_decode function when encountering malformed base64 sequences.

## Constraints:
    Preconditions:
    - Input must be either bytes or string type
    - Valid IMAP UTF-7 encoding format
    
    Postconditions:
    - Returns a properly decoded Unicode string
    - Non-IMAP UTF-7 content is preserved as-is

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start decode] --> B{Input is bytes?}
    B -- No --> C[Return input as-is]
    B -- Yes --> D[Initialize result list and buffer]
    D --> E[Process each byte]
    E --> F{Byte == '&' AND buffer empty?}
    F -- Yes --> G[Add '&' to buffer]
    F -- No --> H{Byte == '-' AND buffer has content?}
    H -- Yes --> I{Buffer length == 1?}
    I -- Yes --> J[Append "&" to result]
    I -- No --> K[Decode buffer content and append to result]
    J --> L[Clear buffer]
    K --> L
    H -- No --> M{Buffer has content?}
    M -- Yes --> N[Add byte to buffer]
    M -- No --> O[Convert byte to char and append to result]
    L --> P{More bytes?}
    P -- Yes --> E
    P -- No --> Q[Handle remaining buffer content]
    Q --> R[Decode remaining buffer and append to result]
    R --> S[Join and return result]
```

## Examples:
    >>> decode(b"Hello &AMU-World")
    'Hello üWorld'
    >>> decode("Hello World")
    'Hello World'

## `imapclient.imap_utf7.base64_utf7_encode` · *function*

## Summary:
Encodes a list of strings into UTF-7 base64 representation suitable for IMAP protocol.

## Description:
Converts a list of Unicode strings into a base64-encoded byte sequence using UTF-16BE encoding, with IMAP-specific formatting adjustments. This function implements part of the IMAP UTF-7 encoding standard where forward slashes are replaced with commas and trailing padding characters are stripped.

## Args:
    buffer (List[str]): A list of strings to encode. These strings are joined together before encoding.

## Returns:
    bytes: The base64-encoded representation of the joined strings, with IMAP-specific formatting applied.

## Raises:
    None explicitly raised, but may raise exceptions from underlying operations:
    - UnicodeEncodeError: If strings in buffer contain characters that cannot be encoded in UTF-16BE
    - TypeError: If buffer contains non-string elements

## Constraints:
    Preconditions:
    - Input buffer must be a list of strings
    - Strings in buffer should be valid Unicode sequences
    
    Postconditions:
    - Output is always bytes containing only base64 characters and commas
    - No newline or equals signs in the returned bytes

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input List[str]] --> B{Join strings}
    B --> C[Encode as UTF-16BE]
    C --> D[Base64 encode]
    D --> E{Strip padding}
    E --> F{Replace "/" with ","}
    F --> G[Return bytes]
```

## Examples:
    >>> base64_utf7_encode(["Hello", "World"])
    b'SGVsbG8Vd29ybGQ='
    
    >>> base64_utf7_encode(["Test"])
    b'VGVzdA=='
```

## `imapclient.imap_utf7.base64_utf7_decode` · *function*

## Summary:
Decodes a base64-UTF7 encoded bytearray into a UTF-8 string by preparing the data format for UTF-7 decoding.

## Description:
This function transforms a bytearray that represents base64-UTF7 encoded data into a properly formatted UTF-7 string by adding start and end markers and converting commas to slashes, then decodes it using UTF-7 encoding. This is part of the IMAP UTF-7 encoding standard where base64-encoded Unicode characters are represented with "+" as start marker, "-" as end marker, and "/" as base64 padding character.

## Args:
    s (bytearray): The base64-UTF7 encoded data to decode, typically containing comma-separated base64 components

## Returns:
    str: The decoded UTF-8 string representation of the base64-UTF7 encoded data

## Raises:
    UnicodeDecodeError: When the transformed byte sequence cannot be decoded using UTF-7 encoding

## Constraints:
    Preconditions:
        - Input must be a valid bytearray containing base64-compatible data
        - The bytearray should represent valid base64-UTF7 encoded content
    Postconditions:
        - Returns a properly decoded UTF-8 string
        - The input bytearray is not modified

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input bytearray s] --> B{Prepare UTF-7 format}
    B --> C[Prepend b"+"]
    C --> D[Replace b"," with b"/"]
    D --> E[Append b"-"]
    E --> F[Decode using "utf-7"]
    F --> G[Return decoded string]
```

## Examples:
    # Basic usage
    data = bytearray(b"SGVsbG8")  # "Hello" in base64
    result = base64_utf7_decode(data)
    # Result would be "Hello" after proper UTF-7 decoding
    
    # With comma-separated components
    data = bytearray(b"SGVsbG8sV29ybGQ")  # "Hello,World" in base64
    result = base64_utf7_decode(data)
    # Result would handle comma conversion properly

