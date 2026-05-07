# `lexer.py`

## `src.jinja2.lexer._describe_token_type` · *function*

*No documentation generated.*

## `src.jinja2.lexer.describe_token` · *function*

*No documentation generated.*

## `src.jinja2.lexer.describe_token_expr` · *function*

*No documentation generated.*

## `src.jinja2.lexer.count_newlines` · *function*

## Summary:
Counts the number of newline characters in a given string.

## Description:
This utility function takes a string input and returns the count of newline characters contained within it. It leverages a pre-compiled regular expression pattern (`newline_re`) to identify and count newline occurrences. This function is used internally by the Jinja2 lexer for tracking line numbers during template parsing.

## Args:
    value (str): The input string to analyze for newline characters.

## Returns:
    int: The total count of newline characters found in the input string.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
        - The input `value` must be a string type
    Postconditions:
        - Returns a non-negative integer representing newline count
        - Input string is not modified

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input String value] --> B[Apply newline_re.findall(value)]
    B --> C[Calculate length of result]
    C --> D[Return int count]
```

## Examples:
    >>> count_newlines("hello\\nworld")
    1
    >>> count_newlines("line1\\nline2\\nline3")
    2
    >>> count_newlines("no newlines here")
    0
```

## `src.jinja2.lexer.compile_rules` · *function*

*No documentation generated.*

## `src.jinja2.lexer.Failure` · *class*

*No documentation generated.*

### `src.jinja2.lexer.Failure.__init__` · *method*

*No documentation generated.*

### `src.jinja2.lexer.Failure.__call__` · *method*

## Summary:
Raises a template syntax error with the stored message at the specified line number and filename.

## Description:
This method serves as a callable interface for raising template syntax errors. It is typically invoked during Jinja2 template parsing when a syntax violation is detected. The method uses the error class and message previously configured in the Failure instance to construct and raise an appropriate exception.

## Args:
    lineno (int): The line number in the template where the syntax error occurred.
    filename (str): The name of the template file where the syntax error occurred.

## Returns:
    None: This method never returns as it raises an exception.

## Raises:
    TemplateSyntaxError: Raised with the stored message, line number, and filename.

## State Changes:
    Attributes READ: self.message, self.error_class
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Failure instance must have been properly initialized with a message and error class.
    Postconditions: This method always raises an exception and never returns normally.

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state.

## `src.jinja2.lexer.Token` · *class*

*No documentation generated.*

### `src.jinja2.lexer.Token.__str__` · *method*

## Summary:
Returns a human-readable string representation of the token, showing either its value for name tokens or a descriptive label for other token types.

## Description:
This method provides a string representation of the token that helps in debugging and logging token streams. It delegates to the `describe_token` function which determines the appropriate representation based on the token type. For tokens of type `TOKEN_NAME`, it returns the token's value directly. For all other token types, it returns a descriptive label based on the token type.

## Args:
    None

## Returns:
    str: A string representation of the token. For name tokens, this is the token's value; for other tokens, this is a descriptive label indicating the token type.

## Raises:
    None

## State Changes:
    Attributes READ: self.lineno, self.type, self.value
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The token object must be properly initialized with lineno, type, and value attributes.
    Postconditions: The returned string is a valid representation of the token's identity and purpose in the template parsing process.

## Side Effects:
    None

### `src.jinja2.lexer.Token.test` · *method*

*No documentation generated.*

### `src.jinja2.lexer.Token.test_any` · *method*

## Summary:
Tests if the token matches any of the provided expression patterns.

## Description:
This method evaluates whether the current token matches any of the given expression patterns by applying the token's `test` method to each pattern. It's particularly useful for checking multiple possible token types or value patterns in a single operation.

## Args:
    *iterable (str): Variable-length argument list of expression patterns to test against the token.

## Returns:
    bool: True if the token matches any of the provided expressions, False otherwise.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.type, self.value
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The token must have valid type and value attributes.
    Postconditions: Returns a boolean indicating match status.

## Side Effects:
    None.

## `src.jinja2.lexer.TokenStreamIterator` · *class*

*No documentation generated.*

### `src.jinja2.lexer.TokenStreamIterator.__init__` · *method*

*No documentation generated.*

### `src.jinja2.lexer.TokenStreamIterator.__iter__` · *method*

## Summary:
Returns the iterator object itself, enabling the TokenStreamIterator to be used in iteration contexts.

## Description:
This method implements Python's iterator protocol by returning the iterator instance itself. It allows TokenStreamIterator objects to be used in for-loops and other iteration contexts. The method is called automatically when an iterator is needed, such as when a for-loop is executed on a TokenStreamIterator instance.

## Args:
    None

## Returns:
    TokenStreamIterator: The iterator instance itself, enabling iteration over tokens.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The TokenStreamIterator instance must be properly initialized with a valid TokenStream.
    Postconditions: The returned object is identical to self, maintaining the iterator's identity.

## Side Effects:
    None

### `src.jinja2.lexer.TokenStreamIterator.__next__` · *method*

*No documentation generated.*

## `src.jinja2.lexer.TokenStream` · *class*

*No documentation generated.*

### `src.jinja2.lexer.TokenStream.__init__` · *method*

*No documentation generated.*

### `src.jinja2.lexer.TokenStream.__iter__` · *method*

## Summary:
Returns an iterator over the tokens in this token stream, enabling iteration through all tokens in sequence.

## Description:
This method implements Python's iterator protocol by returning a `TokenStreamIterator` instance that wraps this token stream. It allows the `TokenStream` to be used in for-loops and other iteration contexts. The iterator handles the internal state management for traversing tokens, including detecting end-of-stream conditions and managing token consumption.

## Args:
    None

## Returns:
    TokenStreamIterator: An iterator object that can be used to iterate over all tokens in this stream.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `TokenStream` object must be properly initialized with a token generator and valid name/filename parameters.
    Postconditions: The returned `TokenStreamIterator` is initialized with this `TokenStream` instance.

## Side Effects:
    None

### `src.jinja2.lexer.TokenStream.__bool__` · *method*

*No documentation generated.*

### `src.jinja2.lexer.TokenStream.eos` · *method*

## Summary:
Returns True when the token stream has no more tokens available, indicating end-of-stream.

## Description:
The eos property provides a convenient way to check if the token stream has been exhausted. It returns True when the stream is empty (no more tokens to process) and False when tokens are still available. This method leverages the TokenStream's `__bool__` implementation which considers the stream non-empty when there are pushed tokens or when the current token is not EOF.

## Args:
    None

## Returns:
    bool: True if the token stream is at end-of-stream (no more tokens), False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: self._pushed, self.current, self.closed
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Returns a boolean value indicating stream status

## Side Effects:
    None

### `src.jinja2.lexer.TokenStream.push` · *method*

## Summary:
Adds a token to the front of the token stream's pushed-back queue for later consumption.

## Description:
This method appends a token to the internal `_pushed` deque, making it available for immediate consumption by the next call to `__next__`. It is primarily used by the `look()` method to temporarily push back a token after examining it without consuming it permanently. This enables lookahead functionality in the lexer without permanently removing tokens from the stream.

## Args:
    token (Token): The token to add to the pushed-back queue

## Returns:
    None: This method does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: `self._pushed` (appends to the deque)

## Constraints:
    Preconditions: The token parameter must be a valid Token instance
    Postconditions: The token is appended to the left end of `self._pushed` deque

## Side Effects:
    None: This method has no side effects beyond modifying the internal `_pushed` deque

### `src.jinja2.lexer.TokenStream.look` · *method*

*No documentation generated.*

### `src.jinja2.lexer.TokenStream.skip` · *method*

## Summary:
Advances the token stream by skipping a specified number of tokens.

## Description:
Moves the internal pointer of the token stream forward by the specified number of tokens. This method is commonly used during template parsing to skip over unwanted tokens such as whitespace or comments. The method calls `next(self)` internally to advance through the token stream, which in turn calls `self.__next__()`.

## Args:
    n (int): Number of tokens to skip. Defaults to 1. Must be non-negative.

## Returns:
    None: This method does not return a value.

## Raises:
    TemplateSyntaxError: Raised if attempting to skip past the end of the token stream (EOF) during advancement.

## State Changes:
    Attributes READ: self.current, self._pushed, self._iter
    Attributes WRITTEN: self.current (modified during token advancement), self.closed (may be set to True)

## Constraints:
    Preconditions: The token stream must be open (self.closed must be False).
    Postconditions: The internal token position is advanced by n positions, or until EOF is reached. If EOF is reached, the stream is closed.

## Side Effects:
    Mutates the internal state of the TokenStream by advancing the current token pointer.
    May close the token stream if EOF is encountered during advancement.

### `src.jinja2.lexer.TokenStream.next_if` · *method*

*No documentation generated.*

### `src.jinja2.lexer.TokenStream.skip_if` · *method*

## Summary:
Attempts to consume the current token if it matches the specified expression, returning whether a token was consumed.

## Description:
This method provides a convenient way to conditionally skip tokens during lexical analysis. It checks if the current token matches the given expression and, if so, advances the token stream by consuming that token. This is commonly used in parsing operations where certain syntax elements (like punctuation or keywords) need to be consumed when encountered.

The method is typically called during template parsing to handle optional syntax elements or to advance past tokens that are expected but not required for further processing.

## Args:
    expr (str): The token expression to match against the current token's type or type:value combination.

## Returns:
    bool: True if the current token matched the expression and was consumed, False otherwise.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self.current, self._pushed
    Attributes WRITTEN: self.current (when a token is consumed via next())

## Constraints:
    Preconditions: The TokenStream must be in a valid state (not closed) and have a current token available.
    Postconditions: If True is returned, the current token position has advanced by one token.

## Side Effects:
    Mutates the TokenStream's internal state by advancing the token position when a match occurs.

### `src.jinja2.lexer.TokenStream.__next__` · *method*

*No documentation generated.*

### `src.jinja2.lexer.TokenStream.close` · *method*

*No documentation generated.*

### `src.jinja2.lexer.TokenStream.expect` · *method*

## Summary:
Validates that the current token matches an expected expression and advances to the next token.

## Description:
This method ensures that the current token in the token stream matches the specified expected expression. If the token matches, it consumes the current token and advances to the next one. If it doesn't match, it raises a TemplateSyntaxError with a descriptive message indicating what was expected versus what was found.

The method is commonly used during template parsing to enforce syntax rules and ensure tokens appear in the correct order. It's particularly useful in grammar parsers where specific token sequences must be validated.

## Args:
    expr (str): The expected token expression to match against the current token. This can be a token type or a token type with a specific value (e.g., "name:variable_name").

## Returns:
    Token: The next token in the stream after validation.

## Raises:
    TemplateSyntaxError: When the current token does not match the expected expression. Two variants:
        - If the end of file is encountered unexpectedly: "unexpected end of template, expected {expr!r}."
        - If any other token is encountered: "expected token {expr!r}, got {describe_token(self.current)!r}"

## State Changes:
    Attributes READ: self.current, self.name, self.filename
    Attributes WRITTEN: self.current (modified via next(self))

## Constraints:
    Preconditions: 
        - The TokenStream must be in a valid state (not closed)
        - The current token must be available for testing
    Postconditions:
        - If successful, the current token is advanced to the next token in the stream
        - If unsuccessful, no state change occurs (token remains unchanged)

## Side Effects:
    - Advances the token stream by consuming the current token
    - May raise TemplateSyntaxError which terminates parsing

## `src.jinja2.lexer.get_lexer` · *function*

*No documentation generated.*

## `src.jinja2.lexer.OptionalLStrip` · *class*

*No documentation generated.*

### `src.jinja2.lexer.OptionalLStrip.__new__` · *method*

## Summary:
Creates a tuple instance containing the specified members for optional left strip operations in Jinja2 template parsing.

## Description:
This method implements the constructor for the OptionalLStrip class, which is a tuple subclass used in Jinja2's template lexer. It creates an immutable tuple containing the provided members, typically representing token patterns or parsing rules for optional left strip operations during template compilation.

## Args:
    cls (type): The class being instantiated
    *members: Variable length argument list of elements to include in the tuple
    **kwargs: Additional keyword arguments (ignored in current implementation)

## Returns:
    OptionalLStrip: A new instance of the OptionalLStrip class containing the specified members

## Raises:
    TypeError: If the parent tuple constructor raises a TypeError due to invalid arguments

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - cls must be the OptionalLStrip class or its subclass
    - members must be valid arguments for tuple construction
    
    Postconditions:
    - Returns an immutable tuple instance containing all provided members
    - The returned instance maintains tuple immutability

## Side Effects:
    None

## `src.jinja2.lexer._Rule` · *class*

*No documentation generated.*

## `src.jinja2.lexer.Lexer` · *class*

*No documentation generated.*

### `src.jinja2.lexer.Lexer.__init__` · *method*

*No documentation generated.*

### `src.jinja2.lexer.Lexer._normalize_newlines` · *method*

## Summary:
Normalizes line endings in template source text to use the environment's configured newline sequence.

## Description:
This method standardizes line endings in template source text by replacing all newline sequences with the environment's configured newline sequence. It ensures consistent line ending handling regardless of the input format (Windows \r\n, Unix \n, or Mac \r).

The method is called during template tokenization when processing data tokens and string literals to normalize their content before further processing. This prevents inconsistencies in how newlines are handled throughout the template processing pipeline.

## Args:
    value (str): The input string containing potentially mixed newline sequences to normalize.

## Returns:
    str: A string with all newline sequences replaced by the environment's configured newline sequence.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self.newline_sequence
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input value must be a string.
    Postconditions: The returned string will have consistent line endings matching the environment configuration.

## Side Effects:
    None - This method is pure and does not cause any I/O or external service calls.

### `src.jinja2.lexer.Lexer.tokenize` · *method*

## Summary:
Converts a Jinja2 template source string into a stream of tokens for parsing.

## Description:
The tokenize method processes a Jinja2 template source string and converts it into a TokenStream containing structured tokens that represent the template's syntax elements. This method serves as the entry point for the lexical analysis phase of template processing, breaking down the template into meaningful components that can be parsed by the Jinja2 parser.

This method is separated from the core tokenization logic to provide a clean interface that handles the orchestration between the token iteration process and the token wrapping process, ensuring proper construction of the final TokenStream object.

## Args:
    source (str): The Jinja2 template source code to tokenize
    name (Optional[str]): Name of the template for error reporting purposes
    filename (Optional[str]): Filename of the template for error reporting purposes  
    state (Optional[str]): Initial parsing state ('variable', 'block', or None for root)

## Returns:
    TokenStream: An iterator over tokens representing the parsed template structure

## Raises:
    TemplateSyntaxError: When encountering invalid syntax in the template source

## State Changes:
    Attributes READ: None - this method doesn't read any instance attributes directly
    Attributes WRITTEN: None - this method doesn't modify any instance attributes

## Constraints:
    Preconditions: 
    - source must be a valid string
    - state, if provided, must be either 'variable', 'block', or None
    
    Postconditions:
    - Returns a TokenStream object with properly formatted tokens
    - All tokens in the stream are valid Jinja2 syntax elements

## Side Effects:
    None - this method is pure and doesn't cause any external I/O or state changes beyond returning a TokenStream

### `src.jinja2.lexer.Lexer.wrap` · *method*

## Summary:
Processes and normalizes a stream of raw token tuples into properly formatted Token objects with type transformations and value parsing.

## Description:
The wrap method serves as a post-processing step in Jinja2's template tokenization pipeline. It takes raw token streams produced by the lexer's token iteration process and applies necessary transformations to convert them into standardized Token objects. This includes handling special token types, normalizing whitespace, parsing numeric values, processing string literals with escape sequences, and validating identifiers.

This method is called internally by the Lexer.tokenize method during the template compilation process. It's separated from the main token iteration logic to keep the core parsing algorithm clean and focused on lexing, while providing a dedicated place for token normalization and transformation.

## Args:
    stream (Iterable[Tuple[int, str, str]]): An iterable of token tuples containing (line_number, token_type, value_string)
    name (Optional[str]): Name of the template being processed, used for error reporting
    filename (Optional[str]): Filename of the template being processed, used for error reporting

## Returns:
    Iterator[Token]: An iterator of properly formatted Token objects with transformed values and normalized content

## Raises:
    TemplateSyntaxError: When encountering invalid identifiers or malformed string literals during token processing

## State Changes:
    Attributes READ: self._normalize_newlines, self.newline_sequence
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The input stream must contain valid token tuples with line numbers, token types, and string values
    - The token types must be recognized by the method's transformation logic
    - If name or filename are provided, they should be valid string values or None
    
    Postconditions:
    - All returned tokens will be properly formatted Token instances
    - Invalid identifiers will raise TemplateSyntaxError before yielding any tokens
    - String literals will have proper Unicode escape sequence handling
    - Numeric values will be converted to appropriate Python types (int/float)

## Side Effects:
    None - This method is purely functional and doesn't cause any I/O operations or external service calls. It only processes input and yields output tokens.

### `src.jinja2.lexer.Lexer.tokeniter` · *method*

*No documentation generated.*

