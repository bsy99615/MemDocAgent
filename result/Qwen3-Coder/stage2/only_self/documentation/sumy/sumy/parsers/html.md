# `html.py`

## `sumy.parsers.html.HtmlParser` · *class*

## Summary:
Parses HTML content into structured document objects for text summarization, extracting significant and stigma words while organizing content into paragraphs and sentences.

## Description:
The HtmlParser class serves as a specialized document parser that converts HTML content into a structured document model suitable for text summarization tasks. It leverages the breadability library to extract readable content from HTML and organizes it into paragraphs and sentences while identifying significant and stigma words based on HTML annotations.

This class provides multiple factory methods for creating instances from different sources (string, file, URL) and implements cached properties for efficient access to extracted word lists and structured document representation.

## State:
- `_article`: Article object from breadability library containing parsed HTML content and metadata
- `SIGNIFICANT_TAGS`: Tuple of HTML tag names that indicate significant content (h1, h2, h3, b, strong, big, dfn, em)
- `SIGNIFICANT_WORDS`: Class constant tuple of significant words inherited from DocumentParser
- `STIGMA_WORDS`: Class constant tuple of stigma words inherited from DocumentParser

## Lifecycle:
- Creation: Instances are created via class methods `from_string()`, `from_file()`, or `from_url()` which internally call `__init__()`
- Usage: Access cached properties `significant_words`, `stigma_words`, and `document` for content analysis
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HtmlParser] --> B[from_string]
    A --> C[from_file]
    A --> D[from_url]
    A --> E[__init__]
    E --> F[_article = Article(html_content, url)]
    A --> G[significant_words]
    A --> H[stigma_words]
    A --> I[document]
    G --> J[_contains_any]
    H --> J
    I --> K[Paragraph]
    I --> L[Sentence]
```

## Raises:
- `requests.exceptions.RequestException`: When fetching content from URL fails
- `AttributeError`: When accessing Article methods that don't exist
- `ValueError`: When HTML content is malformed or invalid

## Example:
```python
# Create parser from HTML string
parser = HtmlParser.from_string("<h1>Title</h1><p>Content here.</p>", "http://example.com", tokenizer)

# Extract significant words
significant = parser.significant_words

# Extract stigma words  
stigma = parser.stigma_words

# Get structured document
doc = parser.document

# Create parser from file
parser2 = HtmlParser.from_file("/path/to/file.html", "http://example.com", tokenizer)

# Create parser from URL
parser3 = HtmlParser.from_url("http://example.com/page.html", tokenizer)
```

### `sumy.parsers.html.HtmlParser.from_string` · *method*

## Summary:
Creates a new HtmlParser instance from HTML string content.

## Description:
This class method serves as a factory constructor for creating HtmlParser instances from raw HTML string content. It provides a convenient way to parse HTML content without needing to manually construct the object or handle file operations.

## Args:
    string (str): Raw HTML content to parse
    url (str): URL associated with the HTML content, used for context and link resolution
    tokenizer (Tokenizer): Tokenizer instance for processing text into sentences and words

## Returns:
    HtmlParser: A new instance of HtmlParser configured with the provided HTML content, URL, and tokenizer

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None (creates new instance, doesn't modify existing state)

## Constraints:
    Preconditions: 
    - string must be a valid HTML string
    - url should be a valid URL string
    - tokenizer must be a valid tokenizer instance
    
    Postconditions:
    - Returns a fully initialized HtmlParser instance
    - The returned instance has its internal article representation set up with the provided HTML content

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser.from_file` · *method*

## Summary:
Creates a new HtmlParser instance by reading HTML content from a file.

## Description:
This class method provides a convenient way to parse HTML content from a local file. It opens the specified file in binary mode, reads its entire content, and constructs a new HtmlParser instance using that content along with the provided tokenizer and URL.

## Args:
    file_path (str): Absolute or relative path to the HTML file to be parsed.
    url (str): The URL associated with the HTML content, used for context and metadata.
    tokenizer (object): A tokenizer instance used to process text into sentences and words.

## Returns:
    HtmlParser: A new instance of HtmlParser initialized with the file's HTML content.

## Raises:
    FileNotFoundError: If the specified file_path does not exist or cannot be accessed.
    IOError: If there are issues reading the file (permissions, disk errors, etc.).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The file_path must point to an existing file that can be read in binary mode
    - The tokenizer must be a valid object with appropriate tokenization methods
    - The url should be a valid string representing the source URL
    
    Postconditions:
    - Returns a fully initialized HtmlParser instance
    - The returned instance contains the HTML content from the file

## Side Effects:
    I/O operations: Reads the entire file content from disk
    Memory allocation: Loads entire file content into memory as bytes

### `sumy.parsers.html.HtmlParser.from_url` · *method*

## Summary:
Creates an HTML parser instance by fetching and parsing content from a remote URL.

## Description:
This class method serves as a factory for creating HtmlParser instances from web URLs. It performs an HTTP GET request to retrieve HTML content, then initializes a new HtmlParser object with the fetched content, tokenizer, and URL. This approach centralizes URL fetching logic while maintaining clean separation between network operations and parsing logic.

## Args:
    url (str): The URL from which to fetch HTML content for parsing.
    tokenizer: An object capable of tokenizing text into sentences and words, typically passed to the HtmlParser constructor.

## Returns:
    HtmlParser: A new instance of HtmlParser initialized with content fetched from the specified URL.

## Raises:
    requests.exceptions.RequestException: When the HTTP request fails due to network issues, invalid URL, or server errors.
    requests.exceptions.HTTPError: When the HTTP response indicates an error status code (4xx or 5xx responses).
    requests.exceptions.ConnectionError: When connection to the remote server cannot be established.
    requests.exceptions.Timeout: When the HTTP request times out.

## State Changes:
    None: This method does not modify any existing object state; it creates and returns a new instance.

## Constraints:
    Preconditions:
        - The URL must be a valid HTTP/HTTPS address that returns HTML content.
        - The tokenizer parameter must be compatible with HtmlParser's requirements.
    Postconditions:
        - Returns a fully initialized HtmlParser instance ready for document processing.
        - The returned instance will have its internal article representation populated with content from the URL.

## Side Effects:
    - Makes an external HTTP request to fetch content from the provided URL.
    - May involve network I/O and potential delays depending on network conditions and server response time.

### `sumy.parsers.html.HtmlParser.__init__` · *method*

## Summary:
Initializes an HtmlParser instance by setting up the parent DocumentParser with a tokenizer and creating a breadability Article object for HTML content processing.

## Description:
This method serves as the constructor for HtmlParser objects, establishing the foundational components needed for HTML parsing operations. It initializes the parent DocumentParser class with the provided tokenizer and creates an Article object from the breadability library to process the HTML content. This method is typically called internally by factory methods like from_string(), from_file(), and from_url() rather than being invoked directly.

The initialization process sets up the parser's ability to extract meaningful content from HTML documents and prepares the internal Article object for subsequent content analysis operations.

## Args:
    html_content (str): Raw HTML content to be parsed and processed
    tokenizer (Tokenizer): Tokenizer instance used for sentence and word tokenization
    url (str, optional): URL associated with the HTML content, used for resolving relative links and metadata extraction

## Returns:
    None: This method initializes the object's state but does not return a value

## Raises:
    AttributeError: When accessing methods or properties of the Article object that don't exist
    ValueError: When HTML content is malformed or invalid for the Article parser

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._article: Set to a new Article object initialized with html_content and url parameters

## Constraints:
    Preconditions:
    - html_content must be a valid string containing HTML markup
    - tokenizer must be a properly initialized tokenizer instance
    - url, if provided, must be a valid string or None

    Postconditions:
    - self._article is initialized as an Article object from breadability
    - Parent DocumentParser is properly initialized with the provided tokenizer

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only creates internal objects.

### `sumy.parsers.html.HtmlParser.significant_words` · *method*

## Summary:
Extracts and returns significant words from the main text content of an HTML document.

## Description:
This method processes the main text content of an HTML document to identify and extract words that are marked with significant HTML tags such as headings (h1-h3) and emphasis tags (b, strong, etc.). It serves as a utility for retrieving important textual elements that are semantically meaningful in the document structure. When no significant words are found in the document content, it falls back to returning a predefined collection of significant words.

## Args:
    None explicitly required (uses self)

## Returns:
    tuple[str]: A tuple containing significant words extracted from the document's main text. Returns either the extracted words or falls back to the class's predefined SIGNIFICANT_WORDS collection if no significant words are found.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._article (accesses main_text property)
    - self.SIGNIFICANT_TAGS (used to filter annotations)
    - self.SIGNIFICANT_WORDS (used as fallback return value)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self._article must be initialized with valid HTML content
    - self._article.main_text must be accessible and properly structured
    - SIGNIFICANT_TAGS must be defined as a sequence of tag names
    Postconditions:
    - Returns a tuple of strings representing significant words
    - If no significant words are found, returns the predefined SIGNIFICANT_WORDS collection (which contains Czech words like "významný", "vynikající", etc.)

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser.stigma_words` · *method*

## Summary:
Extracts words from HTML paragraphs containing specific formatting annotations, returning them as a tuple or falling back to predefined stigma words.

## Description:
This method processes the main text content of an HTML document to identify and extract words from paragraphs that contain specific formatting annotations such as anchor tags ("a"), strike-through ("strike"), or underline ("s"). These annotations typically indicate emphasized or stylized text that may be considered stigma-related in the context of text summarization. When matching annotations are found, the extracted words are returned as a tuple; otherwise, it returns the predefined STIGMA_WORDS constant tuple.

## Args:
    None explicitly taken (uses self)

## Returns:
    tuple[str]: A tuple of extracted words if any matching annotations are found, otherwise returns the predefined STIGMA_WORDS constant tuple containing ("nejhorší", "zlý", "šeredný").

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._article (accesses main_text attribute)
    - self.STIGMA_WORDS (fallback value)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The HtmlParser instance must have been initialized with valid HTML content
    - The _article attribute must be properly populated with parsed HTML content
    - The tokenizer must be properly configured
    
    Postconditions:
    - Returns a tuple of strings representing extracted words or fallback stigma words
    - The returned tuple is immutable (frozen)

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser._contains_any` · *method*

## Summary:
Checks if any of the provided items exist within a given sequence.

## Description:
This utility method evaluates whether any of the specified items are contained within the provided sequence. It's designed to provide a concise way to test multiple potential matches against a single sequence without requiring multiple explicit membership tests.

## Args:
    sequence (Any): The sequence to search within. Can be any iterable object.
    *args (Any): Variable number of items to check for existence in the sequence.

## Returns:
    bool: True if any of the items in args are found in sequence, False otherwise. Returns False immediately if sequence is None.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The sequence argument should be iterable or None.
    Postconditions: The method returns a boolean value indicating membership status.

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser.document` · *method*

## Summary:
Processes HTML content into a structured document model by parsing paragraphs, separating headings from regular text, and tokenizing sentences.

## Description:
Converts HTML content stored in the parser's article into a structured document model suitable for further text processing. This method analyzes the annotated text from the article, identifies heading elements (h1-h3), excludes preformatted text blocks, and tokenizes remaining content into sentences. The resulting document model provides convenient access to paragraphs, sentences, headings, and words through cached properties.

This method is separated from other parsing logic to encapsulate the specific transformation from raw annotated text to structured document objects, making the parsing pipeline modular and testable.

## Args:
    None

## Returns:
    ObjectDocumentModel: A document model containing processed paragraphs with properly categorized sentences (headings vs regular text) and tokenized content. Each paragraph contains sentences that are either regular text or headings, with all text properly tokenized.

## Raises:
    TypeError: If any paragraph in the main_text contains non-tuple elements or if Sentence construction fails due to invalid parameters.
    AttributeError: If self._article or self._tokenizer are not properly initialized.

## State Changes:
    Attributes READ:
    - self._article: Used to access main_text content containing (text, annotations) tuples
    - self._tokenizer: Used for sentence and word tokenization
    
    Attributes WRITTEN:
    - None (this is a pure transformation method)

## Constraints:
    Preconditions:
    - self._article must be initialized with valid HTML content and contain main_text attribute
    - self._tokenizer must be a valid tokenizer instance with to_sentences method
    - self._article.main_text must be iterable where each element is a sequence of (text, annotations) tuples
    - Each annotations element must be iterable or None
    - Text elements must be convertible to unicode strings
    
    Postconditions:
    - Returns a valid ObjectDocumentModel instance with populated paragraphs
    - All returned sentences maintain their heading status (is_heading flag)
    - All paragraphs contain properly tokenized sentences
    - Headings (h1-h3) are preserved as Sentence objects with is_heading=True
    - Preformatted text (pre tags) is excluded from sentence processing
    - Regular text is concatenated with appropriate spacing based on punctuation

## Side Effects:
    None

