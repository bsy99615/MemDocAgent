# `html.py`

## `sumy.parsers.html.HtmlParser` · *class*

## Summary:
HtmlParser is a document parser that extracts structured text content from HTML documents, organizing them into paragraphs and sentences while identifying significant and stigma words.

## Description:
The HtmlParser class serves as a specialized document parser for HTML content, designed to extract meaningful text elements from web pages or HTML strings. It leverages the breadability library to parse HTML and identify main content areas, then processes this content into structured document objects. The parser is particularly useful for text summarization applications where it's important to distinguish between heading text, regular content, and potentially problematic text elements.

The class provides multiple factory methods for convenient instantiation from different sources: raw HTML strings, local files, or remote URLs. It inherits from DocumentParser which provides basic tokenization capabilities and default word lists for significant and stigma words.

## State:
- `_article`: Article object from breadability library containing parsed HTML content
- `_tokenizer`: Tokenizer instance inherited from DocumentParser for text processing
- `SIGNIFICANT_TAGS`: Tuple of HTML tag names that indicate significant text content: ("h1", "h2", "h3", "b", "strong", "big", "dfn", "em")
- `SIGNIFICANT_WORDS`: Default set of significant words inherited from DocumentParser
- `STIGMA_WORDS`: Default set of stigma words inherited from DocumentParser

## Lifecycle:
- Creation: Instances are created via class methods (from_string, from_file, from_url) or directly with __init__
- Usage: Typically accessed through document property to get structured content, and significant_words/stigma_words properties for keyword extraction
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HtmlParser.from_string] --> B[HtmlParser.__init__]
    B --> C[Article(html_content, url)]
    
    D[HtmlParser.from_file] --> E[HtmlParser.__init__]
    E --> F[Article(html_content, url)]
    
    G[HtmlParser.from_url] --> H[fetch_url(url)]
    H --> I[HtmlParser.__init__]
    I --> J[Article(html_content, url)]
    
    K[HtmlParser.document] --> L[Article.main_text]
    L --> M[Paragraph/Sentence objects]
    K --> N[tokenize_sentences]
    K --> O[is_heading detection]
    
    P[HtmlParser.significant_words] --> Q[Article.main_text]
    Q --> R[_contains_any]
    R --> S[tokenize_words]
    
    T[HtmlParser.stigma_words] --> U[Article.main_text]
    U --> V[_contains_any]
    V --> W[tokenize_words]
```

## Raises:
- IOError: When from_file method attempts to read from a non-existent file
- requests.exceptions.RequestException: When from_url method fails to fetch content from URL
- ValueError: Potentially raised by underlying libraries when invalid HTML is processed

## Example:
```python
# Create parser from HTML string
parser = HtmlParser.from_string("<html><body><h1>Title</h1><p>Content here.</p></body></html>", "http://example.com", tokenizer)

# Extract document structure
doc = parser.document

# Get significant words
significant = parser.significant_words

# Get stigma words  
stigma = parser.stigma_words
```

### `sumy.parsers.html.HtmlParser.from_string` · *method*

## Summary:
Creates a new HtmlParser instance from HTML string content.

## Description:
This class method serves as a factory constructor for HtmlParser instances, enabling creation of parser objects directly from HTML string content rather than from files or URLs. It's typically used in the document parsing pipeline when HTML content is already available as a string in memory. The method acts as a convenience wrapper that properly orders parameters for the HtmlParser constructor.

## Args:
    cls: The HtmlParser class (automatically passed by Python's @classmethod decorator)
    string (str): The HTML content as a string to parse
    url (str): The URL associated with the HTML content, used for resolving relative links and metadata
    tokenizer: A tokenizer object used for sentence and word tokenization

## Returns:
    HtmlParser: A new instance of HtmlParser configured with the provided HTML content

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None (the returned instance will have its own state)

## Constraints:
    Preconditions: 
    - The `string` parameter must be a valid HTML string
    - The `url` parameter should be a valid URL string or None
    - The `tokenizer` parameter must be a valid tokenizer object with appropriate methods
    
    Postconditions:
    - Returns a fully initialized HtmlParser instance
    - The returned instance will have its internal Article object populated with the provided HTML content

## Side Effects:
    None directly caused by this method, though the underlying Article constructor may perform I/O operations when processing the HTML content

### `sumy.parsers.html.HtmlParser.from_file` · *method*

## Summary:
Creates a new HtmlParser instance by reading HTML content from a file.

## Description:
This class method provides a convenient way to instantiate an HtmlParser object from an HTML file. It opens the specified file in binary mode, reads its entire content, and uses that content to construct a new HtmlParser instance. This method is part of the factory pattern implementation for creating parser instances from different sources (file, string, URL).

## Args:
    file_path (str): Absolute or relative path to the HTML file to parse.
    url (str): URL associated with the HTML content, used for article extraction.
    tokenizer (object): Tokenizer instance used for processing text content.

## Returns:
    HtmlParser: A new instance of HtmlParser initialized with the file's HTML content.

## Raises:
    FileNotFoundError: If the specified file_path does not exist or cannot be opened.
    IOError: If there are issues reading from the file.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - file_path must be a valid path to an existing file
        - url should be a valid string or None
        - tokenizer must be a valid tokenizer object
    Postconditions:
        - Returns a properly initialized HtmlParser instance
        - The returned instance contains the HTML content from the file

## Side Effects:
    - Performs file I/O operation to read the HTML file
    - May trigger network requests if the file path refers to a remote resource

### `sumy.parsers.html.HtmlParser.from_url` · *method*

## Summary:
Creates an HTML parser instance by fetching and parsing content from a remote URL.

## Description:
This class method serves as a factory for creating HtmlParser instances from web URLs. It retrieves HTML content from the specified URL using HTTP GET request and initializes a new HtmlParser object with the fetched content, tokenizer, and URL. This approach abstracts away the complexity of fetching web content and provides a clean interface for parsing remote HTML documents.

## Args:
    url (str): The URL from which to fetch HTML content
    tokenizer (Tokenizer): A tokenizer instance used for processing text content

## Returns:
    HtmlParser: A new instance of HtmlParser initialized with content from the URL

## Raises:
    Exception: When URL fetching fails due to network issues, invalid URLs, or HTTP errors

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The URL must be a valid HTTP/HTTPS address
    - The tokenizer must be a valid tokenizer instance
    - The URL must be accessible and return valid HTML content
    
    Postconditions:
    - Returns a fully initialized HtmlParser instance
    - The returned instance contains parsed HTML content from the URL

## Side Effects:
    - Makes an HTTP GET request to the specified URL
    - Performs network I/O operations
    - May raise network-related exceptions

### `sumy.parsers.html.HtmlParser.__init__` · *method*

## Summary:
Initializes an HTML parser instance that extracts readable content from HTML documents using the breadability library.

## Description:
Configures the HTML parser with the provided HTML content and tokenizer, preparing it for document analysis operations. This method serves as the constructor that initializes the parser's internal state by creating a breadability Article object for content extraction.

## Args:
    html_content (str): Raw HTML content to parse and extract readable text from.
    tokenizer (object): Tokenizer instance used for sentence and word tokenization.
    url (str, optional): URL associated with the HTML content, used for resolving relative links and metadata. Defaults to None.

## Returns:
    None: This method initializes the object state and does not return a value.

## Raises:
    None explicitly raised: The method delegates to parent class and breadability library which may raise exceptions, but these are not caught or re-raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._article: Set to a new Article instance created from html_content and url
        - self._tokenizer: Set via parent class initialization (inherited from DocumentParser)

## Constraints:
    Preconditions:
        - html_content must be a valid string containing HTML markup
        - tokenizer must be a valid object with to_sentences and to_words methods
        - url, if provided, must be a valid string or None
    Postconditions:
        - self._article is initialized as an Article object
        - self._tokenizer is properly set from the parent class initialization

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal state.

### `sumy.parsers.html.HtmlParser.significant_words` · *method*

## Summary:
Extracts significant words from the main text of an HTML document based on semantic importance tags, returning a cached result.

## Description:
Returns a cached tuple of significant words identified from the main content of an HTML document. This method analyzes paragraphs and extracts words from text segments that are annotated with significant HTML tags such as headings (h1-h3) and emphasis elements (b, strong, etc.). When no significant words are found in the document's main text, it falls back to a predefined set of significant words. This is a cached property, meaning the computation is performed only once and subsequent calls return the cached result.

## Args:
    None

## Returns:
    tuple[str]: A tuple containing significant words extracted from the document's main text, or the fallback SIGNIFICANT_WORDS tuple if no significant words are found.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._article (accesses main_text property)
    - self.SIGNIFICANT_TAGS (used in _contains_any check)
    - self.SIGNIFICANT_WORDS (fallback return value)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self._article must be initialized with valid HTML content
    - self._article.main_text must be accessible and iterable
    
    Postconditions:
    - Returns a tuple of strings (words)
    - If significant words are found, they come from text annotated with significant tags
    - If no significant words are found, returns the predefined SIGNIFICANT_WORDS tuple

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser.stigma_words` · *method*

## Summary:
Extracts annotated words from HTML content that have specific formatting tags and returns them as a tuple, falling back to predefined stigma words when none are found.

## Description:
This method identifies words in HTML content that are marked with specific annotations ("a", "strike", "s") and tokenizes them into individual words. These words are typically considered to have special significance in the document's context. When no annotated words are found, it returns a fallback set of stigma words defined in the parent class.

## Args:
    None

## Returns:
    tuple[str]: A tuple of word strings extracted from annotated HTML content, or the fallback STIGMA_WORDS tuple if no annotated words are found.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self._article.main_text
    - self.STIGMA_WORDS
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self._article must be properly initialized with HTML content
    - self._article.main_text must be iterable and contain tuples of (text, annotations)
    - Annotations in main_text should be iterable or None
    Postconditions:
    - Returns a tuple of strings (never None)
    - If annotated words exist, returns those words; otherwise returns fallback STIGMA_WORDS

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser._contains_any` · *method*

## Summary:
Checks if any of the provided items exist within a given sequence.

## Description:
This utility method determines whether any of the specified items from the variable arguments exist within the provided sequence. It's designed to simplify common membership testing operations where multiple potential matches need to be checked against a collection.

The method is used internally by the HtmlParser class to efficiently check for the presence of specific HTML tags or attributes in annotation metadata extracted from web content.

## Args:
    sequence (Iterable): The sequence to search within, typically a collection of HTML tags or annotations.
    *args (str): Variable number of items to check for membership in the sequence.

## Returns:
    bool: True if any of the items in args are found in sequence, False otherwise. Returns False immediately if sequence is None.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - sequence can be any iterable type (list, tuple, set, etc.) or None
    - args can contain any hashable items to check for membership
    
    Postconditions:
    - Returns boolean value indicating membership result
    - Returns False when sequence is None regardless of args content

## Side Effects:
    None

### `sumy.parsers.html.HtmlParser.document` · *method*

## Summary:
Converts HTML article content into a structured document model with properly categorized sentences and headings.

## Description:
Processes the main text content from a parsed HTML article, separating headings (h1-h3) from regular text, and tokenizing text into sentences. Headings are identified by their HTML annotations and treated as special Sentence objects with is_heading=True. Regular text is concatenated and then split into sentences using the tokenizer. The resulting content is organized into Paragraph objects within an ObjectDocumentModel.

This method serves as the core parsing logic for converting HTML content into a structured representation suitable for text summarization and analysis workflows. It's implemented as a cached property to avoid recomputation.

## Args:
    None (uses instance state)

## Returns:
    ObjectDocumentModel: A structured document model containing paragraphs with sentences and headings, organized for downstream processing.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._article, self._tokenizer
    Attributes WRITTEN: None (this is a getter method)

## Constraints:
    Preconditions: 
    - self._article must be initialized with valid HTML content
    - self._tokenizer must be a valid tokenizer instance
    - self._article.main_text must be iterable and contain tuples of (text, annotations)
    
    Postconditions:
    - Returns a valid ObjectDocumentModel instance
    - All headings (h1-h3) are properly marked as is_heading=True in Sentence objects
    - Regular text is properly tokenized into sentences
    - Preformatted text (pre tags) is excluded from processing

## Side Effects:
    None (pure function with respect to external state)

