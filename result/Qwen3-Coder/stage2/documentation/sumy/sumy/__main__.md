# `__main__.py`

## `sumy.__main__.main` · *function*

## Summary:
Entry point for the sumy command-line interface that processes document summarization requests from command-line arguments.

## Description:
This function serves as the primary command-line interface for the sumy library, parsing user-provided arguments to configure document summarization parameters and execute the summarization process. It leverages docopt for argument parsing, processes the arguments to set up the appropriate summarizer and parser components, and outputs the resulting summary sentences to standard output.

## Args:
    args (list[str], optional): Command-line arguments to parse. If None, sys.argv[1:] is used. Defaults to None.

## Returns:
    int: Exit status code (0 for successful execution).

## Raises:
    None explicitly raised by this function, though underlying operations may raise exceptions during argument parsing, document fetching, or summarization.

## Constraints:
    Preconditions:
    - The `__doc__` variable must contain a valid docopt-formatted string for argument parsing
    - `__version__` must be defined in the module scope
    - Required summarizer and parser components must be importable
    
    Postconditions:
    - Standard output contains formatted summary sentences
    - Function returns integer exit code indicating successful completion

## Side Effects:
    - Parses command-line arguments using docopt
    - May read from filesystem when --file argument is provided
    - May make HTTP requests when --url argument is provided
    - Prints summary sentences to standard output (stdout)
    - May read from stdin when no explicit input source is specified

## Control Flow:
```mermaid
flowchart TD
    A[main() called] --> B[Parse CLI args with docopt]
    B --> C[Process arguments to configure components]
    C --> D[Get summarizer, parser, items_count]
    D --> E[Iterate over summarizer results]
    E --> F{PY3?}
    F -->|Yes| G[Print sentence with to_unicode]
    F -->|No| H[Print sentence with to_bytes]
    G --> I[Return 0]
    H --> I
```

## Examples:
    # Basic usage with default input (stdin)
    # $ echo "This is a test document." | python -m sumy --length 3 --luhn
    
    # Summarize from a file
    # $ python -m sumy --file document.txt --length 5 --text-rank
    
    # Summarize from a URL
    # $ python -m sumy --url https://example.com/article --length 10% --lsa
```

## `sumy.__main__.handle_arguments` · *function*

## Summary:
Processes command-line arguments to configure and initialize the document summarization pipeline components.

## Description:
This function takes parsed command-line arguments and constructs the necessary components for document summarization including the appropriate parser, summarizer, and item count configuration. It handles multiple input sources (URL, file, text, stdin) and selects the correct parser and summarizer based on user-provided arguments. The function acts as a central configuration manager that prepares all required components before the actual summarization process begins.

## Args:
    args (dict): Dictionary of parsed command-line arguments containing keys like '--url', '--file', '--text', '--format', '--length', '--language', '--stopwords'
    default_input_stream (file-like object): Input stream to read from when no explicit input source is provided. Defaults to sys.stdin.

## Returns:
    tuple: A tuple containing three elements:
        - summarizer (AbstractSummarizer): Configured summarizer instance ready for document processing
        - parser: Initialized parser instance containing document content and tokenization
        - items_count (ItemsCount): Configuration object for determining how many items (sentences/words) to include in the summary

## Raises:
    ValueError: When an unsupported document format is specified in --format argument

## Constraints:
    Preconditions:
    - args dictionary must contain all expected keys with appropriate values
    - If --format is specified, it must be one of the supported formats in PARSERS constant
    - The selected summarizer method flag (e.g., --luhn, --text-rank) must be present in args
    
    Postconditions:
    - Returns properly initialized components for summarization pipeline
    - All components are configured with appropriate language settings and stop words
    - Parser is initialized with document content and tokenizer

## Side Effects:
    - Reads from file system when --file argument is provided
    - Makes HTTP request when --url argument is provided
    - Reads from input stream when no explicit input source is specified

## Control Flow:
```mermaid
flowchart TD
    A[handle_arguments called] --> B{--url provided?}
    B -->|Yes| C[Select parser from PARSERS]
    C --> D[Fetch URL content]
    B -->|No| E{--file provided?}
    E -->|Yes| F[Select parser from PARSERS]
    F --> G[Read file content]
    E -->|No| H{--text provided?}
    H -->|Yes| I[Select parser from PARSERS]
    I --> J[Use text content]
    H -->|No| K[Read from default_input_stream]
    D --> L[Create ItemsCount]
    G --> L
    J --> L
    K --> L
    L --> M{Stopwords specified?}
    M -->|Yes| N[Read custom stopwords file]
    M -->|No| O[Get default stopwords by language]
    N --> P[Initialize parser with content and tokenizer]
    O --> P
    P --> Q[Create stemmer]
    Q --> R[Select summarizer class from AVAILABLE_METHODS]
    R --> S[Build configured summarizer]
    S --> T[Return (summarizer, parser, items_count)]
```

## Examples:
    # Example usage with URL input
    args = {
        '--url': 'https://example.com/article',
        '--format': 'html',
        '--length': 5,
        '--language': 'english',
        '--luhn': True
    }
    summarizer, parser, items_count = handle_arguments(args)
    
    # Example usage with file input
    args = {
        '--file': '/path/to/document.txt',
        '--length': '10%',
        '--language': 'english',
        '--text-rank': True
    }
    summarizer, parser, items_count = handle_arguments(args)

## `sumy.__main__.build_summarizer` · *function*

## Summary:
Creates and configures a summarizer instance with appropriate parameters based on the summarizer type.

## Description:
This function serves as a factory for creating summarizer objects. It instantiates a summarizer of the specified class with a stemmer, then configures it with the appropriate stop words and additional parameters based on the summarizer type. The function handles special configuration requirements for EdmundsonSummarizer differently from other summarizer types.

## Args:
    summarizer_class (type): The class of the summarizer to instantiate (e.g., LuhnSummarizer, TextRankSummarizer, etc.)
    stop_words (frozenset): Set of stop words to be used for filtering
    stemmer (Stemmer): Stemmer instance to be used for word stemming
    parser: Parser instance containing document-specific data (like significant_words for EdmundsonSummarizer)

## Returns:
    AbstractSummarizer: Configured summarizer instance ready for use in document summarization

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - summarizer_class must be a valid summarizer class that accepts a stemmer in its constructor
    - stop_words must be a frozenset of words
    - stemmer must be a valid Stemmer instance
    - parser must have the appropriate attributes for the specific summarizer being created
    
    Postconditions:
    - Returns a configured summarizer instance
    - For EdmundsonSummarizer, the returned instance will have null_words, bonus_words, and stigma_words set
    - For other summarizers, the returned instance will have stop_words set

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[build_summarizer called] --> B[Instantiate summarizer_class(stemmer)]
    B --> C{Is EdmundsonSummarizer?}
    C -->|Yes| D[Set null_words = stop_words]
    D --> E[Set bonus_words = parser.significant_words]
    E --> F[Set stigma_words = parser.stigma_words]
    C -->|No| G[Set stop_words = stop_words]
    F --> H[Return summarizer]
    G --> H
```

## Examples:
    # Creating a Luhn summarizer
    luhn_summarizer = build_summarizer(LuhnSummarizer, stop_words, stemmer, parser)
    
    # Creating an Edmundson summarizer
    edmundson_summarizer = build_summarizer(EdmundsonSummarizer, stop_words, stemmer, parser)
```

