# `html.py`

## `sumy.parsers.html.HtmlParser` · *class*

## Summary:
Parses HTML content into a structured document model, extracting significant words and organizing text into paragraphs and sentences.

## Description:
The HtmlParser class serves as a specialized document parser for HTML content, converting raw HTML into a structured representation suitable for text analysis and summarization tasks. It leverages the breadability library to extract readable content from HTML and organizes it into paragraphs and sentences while identifying significant and stigma words.

This class is typically instantiated through factory methods (from_string, from_file, from_url) rather than direct construction, making it easy to create parsers from various HTML sources.

## State:
- `_article`: Article object from breadability library containing parsed HTML content
- `_tokenizer`: Tokenizer instance inherited from DocumentParser for text processing
- `SIGNIFICANT_TAGS`: Tuple of HTML tags considered significant for word extraction
- `SIGNIFICANT_WORDS`: Class-level tuple of significant words inherited from DocumentParser
- `STIGMA_WORDS`: Class-level tuple of stigma words inherited from DocumentParser

## Lifecycle:
- Creation: Use class methods from_string, from_file, or from_url to instantiate
- Usage: Access cached properties significant_words, stigma_words, and document; the document property excludes preformatted text blocks (marked with "pre" annotation)
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
    I --> K[ObjectDocumentModel]
    I --> L[Paragraph]
    I --> M[Sentence]
```

## Raises:
- IOError: When from_file method fails to read from the specified file path
- requests.exceptions.RequestException: When from_url method fails to fetch content from the URL
- ValueError: When the HTML content cannot be processed by breadability.Article

## Example:
```python
# Create parser from URL
parser = HtmlParser.from_url("https://example.com/article", tokenizer)

# Extract significant words
significant = parser.significant_words

# Build document structure
doc = parser.document

# Create parser from file
parser2 = HtmlParser.from_file("/path/to/file.html", "https://example.com", tokenizer)

# Create parser from string
parser3 = HtmlParser.from_string("<html><body>Content</body></html>", "https://example.com", tokenizer)
```

### `sumy.parsers.html.HtmlParser.from_string` · *method*

## Summary:
Creates an HtmlParser instance from HTML string content.

## Description:
This class method serves as a factory constructor for HtmlParser objects, providing a convenient way to create parser instances directly from HTML string content. It follows the factory pattern to enable uniform instantiation from different input sources (string, file, URL).

## Args:
    cls: The HtmlParser class (automatically passed by Python's @classmethod decorator)
    string (str): The HTML content as a string to parse
    url (str): The URL associated with the HTML content, used for context and link resolution
    tokenizer (Tokenizer): A tokenizer instance for processing text into sentences and words

## Returns:
    HtmlParser: A new instance of HtmlParser initialized with the provided HTML string, tokenizer, and URL

## Raises:
    None explicitly raised - any exceptions would originate from the underlying Article class or parent DocumentParser initialization

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._article (initialized via Article constructor)

## Constraints:
    Preconditions: 
    - The string parameter must contain valid HTML content
    - The tokenizer parameter must be a valid tokenizer instance
    - The url parameter should be a valid URL string or None
    
    Postconditions:
    - Returns a fully initialized HtmlParser instance
    - The instance's _article attribute is set to an Article object created from the HTML string

## Side Effects:
    None - this method is pure and doesn't perform I/O operations or mutate external state

### `sumy.parsers.html.HtmlParser.from_file` · *method*

## Summary:
Creates a new HTML parser instance from the contents of a local file.

## Description:
This class method provides a convenient way to instantiate an HtmlParser object by reading HTML content from a local file. It opens the specified file in binary mode, reads all bytes, and passes them to the HtmlParser constructor along with the provided URL and tokenizer.

## Args:
    file_path (str): Absolute or relative path to the HTML file to parse.
    url (str): The URL associated with the HTML content, used for context and metadata.
    tokenizer (object): A tokenizer object used for processing text into sentences and words.

## Returns:
    HtmlParser: A new instance of the HtmlParser class initialized with the file's content.

## Raises:
    FileNotFoundError: If the specified file_path does not exist.
    IOError: If there are issues reading the file.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The file_path must point to an existing file
    - The file must be readable
    - The tokenizer must be a valid object with appropriate methods
    
    Postconditions:
    - Returns a fully initialized HtmlParser instance
    - The returned instance contains the HTML content from the file

## Side Effects:
    I/O operations: Reads the entire file content from disk

### `sumy.parsers.html.HtmlParser.from_url` · *method*

## Summary:
Creates an HTML parser instance by fetching and parsing content from a remote URL.

## Description:
This class method serves as a factory for creating HtmlParser instances from web URLs. It performs an HTTP GET request to retrieve HTML content, then initializes a new HtmlParser object with the fetched data, tokenizer, and URL. This approach centralizes URL fetching logic while maintaining consistency with other HtmlParser construction methods like from_string() and from_file().

## Args:
    url (str): The web address to fetch HTML content from
    tokenizer: A tokenizer instance used for processing text content

## Returns:
    HtmlParser: A new instance of HtmlParser initialized with content from the specified URL

## Raises:
    requests.exceptions.RequestException: When the HTTP request fails due to network issues, invalid URL, or server errors
    requests.exceptions.HTTPError: When the server responds with an HTTP error status code

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The URL must be a valid web address that can be accessed via HTTP/HTTPS
    - The tokenizer parameter must be a valid tokenizer instance
    Postconditions:
    - Returns a fully initialized HtmlParser instance ready for document processing

## Side Effects:
    - Makes an external HTTP request to fetch content from the provided URL
    - May block execution until the HTTP request completes
    - Depends on network connectivity and server availability

### `sumy.parsers.html.HtmlParser.__init__` · *method*

## Summary:
Initializes an HtmlParser instance by setting up the document parser base and creating a breadability Article object for HTML content processing.

## Description:
The HtmlParser.__init__ method serves as the constructor for HTML document parsers, establishing the foundational structure for processing HTML content. It initializes the parent DocumentParser class with the provided tokenizer and creates a breadability Article object to parse the HTML content, enabling subsequent text extraction and document structuring operations.

This method is typically called internally by factory methods like from_string, from_file, and from_url rather than being invoked directly by users.

## Args:
    html_content (str): Raw HTML content to be parsed and processed
    tokenizer (Tokenizer): Tokenizer instance used for text processing operations
    url (str, optional): URL associated with the HTML content, used for resolving relative links and metadata

## Returns:
    None: This method initializes the instance and does not return a value

## Raises:
    None explicitly raised in this method
    However, underlying exceptions from breadability.Article or DocumentParser.__init__ may propagate

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._article: Set to a new Article(html_content, url) instance
    - self._tokenizer: Inherited from DocumentParser.__init__ (not directly written but used)

## Constraints:
    Preconditions:
    - html_content must be a valid string containing HTML markup
    - tokenizer must be a valid Tokenizer instance
    - url, if provided, must be a valid string or None
    
    Postconditions:
    - self._article is initialized as a breadability.Article instance
    - self._tokenizer is properly set up through DocumentParser inheritance

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `sumy.parsers.html.HtmlParser.significant_words` · *method*

## Summary:
Returns a cached tuple of significant words extracted from HTML content by identifying text with specific semantic tags.

## Description:
This cached property processes HTML content to identify and extract significant words from text elements that are annotated with semantic tags indicating importance. It scans through the article's main text content, checking each text segment's annotations against a predefined set of significant tags. When matching annotations are found, the associated text is tokenized into words and collected. If significant words are found, they are returned as a tuple; otherwise, a fallback set of significant words from the base class is returned.

The property is part of the HTML parsing pipeline and serves as a key component for extracting meaningful content from web pages for summarization purposes. It's designed to work with the breadability library's Article object to parse HTML content and identify important textual elements. The result is cached for performance optimization.

## Args:
    None

## Returns:
    tuple[str]: A tuple containing significant words extracted from HTML content with semantic tags. Returns a fallback tuple of significant words from the base class if no significant words are found in the HTML content.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self._article (Article object containing parsed HTML content)
    - self.SIGNIFICANT_TAGS (tuple of HTML tag names considered significant)
    - self.SIGNIFICANT_WORDS (fallback tuple of significant words from base class)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self._article must be initialized with valid HTML content
    - self._article.main_text must be accessible and contain text segments with annotations
    - self.SIGNIFICANT_TAGS must be defined as a tuple of strings
    - self.SIGNIFICANT_WORDS must be defined as a tuple of strings
    
    Postconditions:
    - Returns a tuple of strings (words) or the fallback SIGNIFICANT_WORDS tuple
    - Property is idempotent - repeated accesses return the same cached result

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser.stigma_words` · *method*

## Summary:
Extracts words from HTML text that have specific annotation tags ("a", "strike", "s") and returns them as a tuple, falling back to predefined stigma words when none are found.

## Description:
This method processes the main text content of an HTML document to identify and extract words that are annotated with specific HTML tags: "a" (anchor/link), "strike" (strikethrough), or "s" (strike-through). These annotations typically indicate text that should be treated specially in text summarization or analysis contexts. The extracted words are tokenized and returned as a tuple. When no such annotated words are found, the method returns the predefined STIGMA_WORDS collection.

The method is part of the HTML parsing pipeline and is cached for performance optimization. It's similar in functionality to the significant_words property but targets different HTML annotation patterns.

## Args:
    None

## Returns:
    tuple[str]: A tuple containing extracted stigma words from annotated HTML text, or the predefined STIGMA_WORDS tuple if no annotated words are found.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self._article (accessed via self._article.main_text)
    - self.STIGMA_WORDS (accessed as fallback)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self._article must be properly initialized with HTML content
    - self._article.main_text must be accessible and iterable
    - The tokenizer must be properly initialized
    
    Postconditions:
    - Returns a tuple of strings (words) or the predefined STIGMA_WORDS tuple
    - The returned tuple contains only words that were originally annotated with "a", "strike", or "s"

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser._contains_any` · *method*

## Summary:
Checks if any of the provided items exist in a given sequence.

## Description:
This utility method determines whether any of the specified items are contained within the provided sequence. It's designed to simplify membership testing for multiple values against a collection, particularly useful when processing HTML annotations where multiple tag types need to be checked.

The method is called during HTML parsing operations to identify significant words and stigma words based on HTML annotation tags.

## Args:
    sequence (Iterable): The sequence to search within, typically a collection of HTML annotation tags.
    *args (str): Variable number of string arguments representing items to search for in the sequence.

## Returns:
    bool: True if any of the items in args are found in sequence, False otherwise. Returns False immediately if sequence is None.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - sequence can be any iterable or None
    - args can be any number of string arguments
    
    Postconditions:
    - Returns boolean value indicating membership of any arg in sequence
    - Returns False when sequence is None regardless of args content

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser.document` · *method*

## Summary:
Converts HTML content into a structured document model by parsing text segments, identifying headings, and tokenizing sentences.

## Description:
Processes the HTML content stored in the parser's article object to create a hierarchical document structure. This method extracts text segments with their associated annotations, identifies heading elements (h1-h3), filters out preformatted text blocks, and converts remaining text into tokenized sentences. The resulting structure is returned as an ObjectDocumentModel containing paragraphs of sentences.

The method specifically handles:
- Text segments with HTML annotations to identify headings (h1, h2, h3)
- Exclusion of preformatted text blocks (marked with "pre" annotation)
- Proper spacing and punctuation handling for concatenated text
- Tokenization of remaining text into sentences using the provided tokenizer

## Args:
    None

## Returns:
    ObjectDocumentModel: A structured document model containing paragraphs of sentences, with headings properly identified and preformatted text excluded.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._article (accesses main_text property)
    - self._tokenizer (used for sentence tokenization)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self._article must be initialized with valid HTML content
    - self._tokenizer must be a valid tokenizer instance
    
    Postconditions:
    - Returns an ObjectDocumentModel with properly structured paragraphs
    - Heading sentences are marked with is_heading=True
    - Preformatted text blocks are excluded from processing
    - All sentences are properly tokenized using the provided tokenizer
    - Text concatenation maintains proper spacing and punctuation

## Side Effects:
    None

