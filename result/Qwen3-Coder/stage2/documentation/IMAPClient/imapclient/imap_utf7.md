# `imap_utf7.py`

## `imapclient.imap_utf7.encode` · *function*

## Summary:
Encodes a string or bytes object into IMAP UTF-7 encoded bytes for safe use in IMAP folder names.

## Description:
Converts a string or bytes object into IMAP UTF-7 encoded bytes. This encoding is necessary because IMAP servers require folder names to be represented using a specific UTF-7 encoding scheme that can represent Unicode characters using ASCII-compatible sequences. The function handles both ASCII printable characters directly and non-ASCII characters by buffering them and encoding them using base64-UTF7 encoding.

This function is extracted from inline logic to provide a clean interface for IMAP folder name encoding while maintaining proper separation of concerns between character classification and base64 encoding operations.

## Args:
    s (Union[str, bytes]): The input string or bytes to encode. If bytes are provided, they are returned unchanged.

## Returns:
    bytes: The IMAP UTF-7 encoded bytes representing the input string. Non-ASCII characters are encoded using base64-UTF7 encoding.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - Input must be either a string or bytes object
    - String input should contain valid Unicode characters
    
    Postconditions:
    - Output is always bytes
    - All non-ASCII characters are properly encoded using base64-UTF7
    - The resulting bytes are safe for use in IMAP folder names

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start encode(s)] --> B{Is s bytes?}
    B -->|Yes| C[Return s unchanged]
    B -->|No| D[Initialize res, b64_buffer]
    D --> E[Process each character in s]
    E --> F{Character in ASCII range 0x20-0x7E?}
    F -->|Yes| G[Consume b64_buffer if exists]
    G --> H{Character is '&' (0x26)?}
    H -->|Yes| I[Append b"&-"]
    H -->|No| J[Append character directly]
    F -->|No| K[Add character to b64_buffer]
    K --> L[End of string?]
    L -->|No| E
    L -->|Yes| M[Consume remaining b64_buffer]
    M --> N[Return bytes(res)]
```

## Examples:
```python
# Encode ASCII string
encoded = encode("Inbox")
# Returns: b'Inbox'

# Encode string with non-ASCII characters
encoded = encode("Folder with äöü")
# Returns: b'Folder with &AP8A8Q-'

# Pass bytes directly (no encoding)
result = encode(b'already_bytes')
# Returns: b'already_bytes'
```

## `imapclient.imap_utf7.decode` · *function*

## Summary:
Decodes IMAP UTF-7 encoded byte sequences into standard UTF-8 strings by processing base64-encoded sections marked with ampersand (&) and dash (-) delimiters.

## Description:
This function implements the decoding logic for IMAP UTF-7 encoding, which is used in email systems to represent Unicode characters in folder names and other metadata that must be ASCII-compatible. The function processes byte sequences where Unicode characters are encoded using a modified base64 scheme delimited by '&' (start) and '-' (end) characters.

The function handles two main cases:
1. Non-base64 characters are converted directly to Unicode characters
2. Base64-encoded sections (between & and -) are decoded using a helper function

This logic is extracted into its own function to separate the concerns of IMAP UTF-7 parsing from higher-level IMAP operations, making the code more modular and testable.

## Args:
    s (Union[bytes, str]): Input string or bytes to decode. If already a string, it is returned unchanged.

## Returns:
    str: Decoded UTF-8 string with all IMAP UTF-7 encoded sections properly converted to Unicode characters.

## Raises:
    None explicitly raised by this function, though underlying base64_utf7_decode may raise UnicodeDecodeError.

## Constraints:
    Preconditions:
        - Input must be either bytes or string type
        - Valid IMAP UTF-7 encoding format with proper & and - delimiters
        
    Postconditions:
        - Returns a properly decoded UTF-8 string
        - All base64-encoded sections are processed correctly

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start decode] --> B{Input is bytes?}
    B -->|No| C[Return input as-is]
    B -->|Yes| D[Initialize result list and buffer]
    D --> E[Process each byte]
    E --> F{Byte is & and buffer empty?}
    F -->|Yes| G[Add & to buffer]
    F -->|No| H{Byte is - and buffer not empty?}
    H -->|Yes| I{Buffer length == 1?}
    I -->|Yes| J[Append "&" to result]
    I -->|No| K[Decode buffer content and append to result]
    J --> L[Clear buffer]
    K --> L
    H -->|No| M{Buffer not empty?}
    M -->|Yes| N[Add byte to buffer]
    M -->|No| O[Convert byte to char and append to result]
    L --> P[Continue processing]
    P --> Q{More bytes?}
    Q -->|Yes| E
    Q -->|No| R[Process remaining buffer if any]
    R --> S[Join result list and return]
```

## Examples:
    # Decode simple ASCII string (no encoding needed)
    result = decode("Hello World")
    # Returns: "Hello World"
    
    # Decode IMAP UTF-7 encoded string
    result = decode(b"INBOX&AOQ-")  # "INBOXÖ" in UTF-7
    # Returns: "INBOXÖ"
```

## `imapclient.imap_utf7.base64_utf7_encode` · *function*

## Summary:
Encodes a list of strings into UTF-7 base64 representation for IMAP compatibility.

## Description:
Converts a list of string segments into a UTF-7 encoded byte sequence suitable for IMAP folder names. This function implements the base64-UTF7 encoding scheme used in IMAP protocols to represent Unicode characters in folder names.

## Args:
    buffer (List[str]): A list of string segments to encode. These typically represent parts of a folder name that may contain non-ASCII characters.

## Returns:
    bytes: A base64-encoded byte sequence representing the UTF-7 encoded folder name. The result has newlines and padding characters stripped, and forward slashes replaced with commas.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - Input buffer should contain valid string elements
    - The function assumes UTF-16BE encoding is appropriate for the input strings
    
    Postconditions:
    - Output is always a valid base64-encoded byte string
    - Forward slashes in base64 output are replaced with commas
    - Padding characters and newlines are stripped from the result

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Input List[str]] --> B[Join strings]
    B --> C[Encode as UTF-16BE]
    C --> D[Base64 encode]
    D --> E[Strip newlines and '=' chars]
    E --> F[Replace '/' with ',']
    F --> G[Return bytes]
```

## Examples:
```python
# Basic usage
result = base64_utf7_encode(["Inbox", "Subfolder"])
# Returns: b'SW5ib3gLU3ViamZvbGRlcg=='

# With special characters
result = base64_utf7_encode(["Folder", "with_umlauts_äöü"])
# Returns: b'Rm9sZGVyV2l0aF91bWxhdXRzX8O2w7bDtw=='
```

## `imapclient.imap_utf7.base64_utf7_decode` · *function*

## Summary:
Decodes a modified base64-encoded bytearray into a UTF-7 decoded string by converting comma separators to slash separators and wrapping with plus/minus delimiters.

## Description:
This function implements a specific decoding routine for IMAP UTF-7 encoding where comma characters are used as separators instead of the standard forward slash. The function transforms the input bytearray by replacing commas with slashes, adds "+" prefix and "-" suffix to form a valid UTF-7 encoded sequence, and then decodes it using UTF-7 encoding.

The function is designed to handle IMAP-specific character encoding where certain Unicode characters are represented using a modified base64 encoding scheme that uses commas instead of slashes for padding. This is commonly used in IMAP folder names and other email-related metadata that contains non-ASCII characters.

## Args:
    s (bytearray): Input byte sequence containing comma-separated base64-like data that needs to be converted to UTF-7 format

## Returns:
    str: Decoded string representing the original Unicode characters in UTF-7 format

## Raises:
    UnicodeDecodeError: When the transformed byte sequence cannot be decoded using UTF-7 encoding (this occurs if the input data is malformed or incompatible with UTF-7 encoding)

## Constraints:
    Preconditions:
        - Input must be a valid bytearray object
        - The bytearray should contain data compatible with the modified base64 UTF-7 encoding scheme
    
    Postconditions:
        - Output string will be properly UTF-7 decoded
        - The transformation preserves the semantic meaning of the original encoded data

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start base64_utf7_decode] --> B[Input bytearray s]
    B --> C[Replace commas with slashes in s]
    C --> D[Prepend "+" to result]
    D --> E[Append "-" to result]
    E --> F[Decode UTF-7 bytes to string]
    F --> G[Return decoded string]
```

## Examples:
    # Basic usage
    input_data = bytearray(b"SGVsbG8sV29ybGQ")  # "Hello,World" in base64
    result = base64_utf7_decode(input_data)
    # Result would be the UTF-7 decoded version of the input
    
    # With actual comma-separated data
    input_data = bytearray(b"SGVsbG8sV29ybGQs")  # Note the trailing comma
    result = base64_utf7_decode(input_data)
    # Processes the comma-separated base64 data and returns UTF-7 decoded string

