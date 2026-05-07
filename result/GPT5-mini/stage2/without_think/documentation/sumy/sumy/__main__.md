# `__main__.py`

## `sumy.__main__.main` · *function*

## Summary:
Parses CLI arguments, prepares the summarization pipeline via handle_arguments, streams generated summary sentences to stdout, and returns an integer exit code (0 on success).

## Description:
Known callers:
- CLI invocation of the package/module (module-level entrypoint). Typical usage is when a user runs the package as a command-line program (for example via python -m sumy or an installed console_script), which triggers this function to parse arguments and run the summarizer pipeline.
- No other internal modules call this function directly in the codebase; it is intended as the command-line entrypoint.

Context and responsibility:
- This function is the top-level CLI runner. It is responsible only for:
  - Parsing command-line arguments (delegated to docopt using the module docstring and module __version__),
  - Delegating argument interpretation and resource construction to handle_arguments(...) which returns (summarizer, parser, items_count),
  - Iterating the summarizer to obtain sentences and printing them to standard output in a Python-version-appropriate encoding,
  - Returning an integer exit code on normal completion.
- Rationale for extraction: The logic for mapping parsed CLI options into concrete parser/summarizer/tokenizer/stemmer/stop-words objects and input resolution is intentionally delegated to handle_arguments so that main stays small and focused on high-level orchestration and output.

## Args:
    args (list[str] | None):
        - The argv-like list of command-line tokens (typically sys.argv[1:]) passed to docopt.
        - If None (the default), docopt will be invoked with None for argv, allowing docopt to use its default behavior for validating/parsing from the process arguments.
        - Interdependencies:
            * The shape and keys of the mapping returned by docopt are determined by the module-level docstring that main passes into docopt; handle_arguments expects the docopt-produced mapping to include keys documented by the CLI (see handle_arguments for the full required keys and semantics).

## Returns:
    int:
        - The function returns 0 to indicate successful completion after all summary sentences have been printed.
        - In normal (successful) flow the only explicit return value is 0. If an exception occurs during argument parsing, resource preparation, summarization, or I/O, that exception propagates and the function does not return 0.

## Raises:
    - Any exception raised by docopt when parsing/validating CLI input (e.g., parse errors or usage/version handling). These exceptions are not caught in main and will propagate.
    - Any exception propagated from handle_arguments(...). handle_arguments performs input-source resolution, file/network I/O, parser/stemmer/tokenizer construction, stop-words loading and summarizer building; it can raise ValueError, StopIteration (no summarizer selected), FileNotFoundError/OSError (file I/O), network/request exceptions from fetch_url, LookupError from missing stop-words data, and other exceptions raised by parser/tokenizer/stemmer/build_summarizer. All such exceptions propagate out of main.
    - Exceptions raised during iteration of the summarizer(generator/callable) or while printing (for example encoding/decoding errors) will propagate.

## Constraints:
Preconditions:
    - The module-level docstring (__doc__) and __version__ must be present and valid for docopt invocation.
    - handle_arguments must accept the dict returned by docopt and return a triple (summarizer, parser, items_count).
    - summarizer must be an iterable/callable that yields sentence-like objects when called as summarizer(parser.document, items_count).

Postconditions:
    - On normal completion, all summary sentences yielded by the summarizer have been written to stdout (one per iteration) and the function returns 0.
    - No exceptions are caught by main; any raised during parsing, preparation, summarization, or printing will escape to the caller.

## Side Effects:
    - Standard output: prints each sentence produced by the summarizer to stdout. Printing uses to_unicode(...) on Python 3 and to_bytes(...) on Python 2 code-paths, so output encoding behavior depends on PY3 and the conversion helpers.
    - Delegated I/O: handle_arguments may have caused network I/O (fetch_url) or file I/O (reading input or stop-words files); those side effects occur before main begins printing.
    - No global state mutation is performed directly by main; side effects stem from handle_arguments or the summarizer/parser implementations.

## Control Flow:
flowchart TD
    A[Start] --> B[Call docopt(to_string(__doc__), args, version=__version__)]
    B --> C{docopt succeeded?}
    C -- No --> D[docopt raises -> propagate exception -> End]
    C -- Yes --> E[Call handle_arguments(parsed_args)]
    E --> F{handle_arguments succeeded?}
    F -- No --> G[exception from handle_arguments -> propagate -> End]
    F -- Yes --> H[(summarizer, parser, items_count)]
    H --> I[Call summarizer(parser.document, items_count) -> iterable]
    I --> J[For each sentence in iterable]
    J --> K{PY3 True?}
    K -- Yes --> L[print(to_unicode(sentence))]
    K -- No --> M[print(to_bytes(sentence))]
    L --> J
    M --> J
    J --> N[All sentences printed]
    N --> O[return 0]

## Examples:
1) Typical CLI-style invocation (conceptual):
    - User executes the package from the shell (this causes main to be invoked as the CLI entrypoint).
    - main parses CLI arguments with docopt, delegates setup to handle_arguments, prints the summarized sentences to stdout, and exits with code 0 on success.

2) Programmatic invocation from Python:
    - Callers can invoke main with an explicit argv list (list of strings) for testing:
      * Example concept: main(['--luhn', '--length', '5', '--file', 'document.txt', '--language', 'english'])
    - If the CLI arguments are invalid or resources fail to load, an exception will be raised; callers should wrap main(...) in a try/except if they want to convert exceptions into custom error codes or messages.

Notes:
    - main intentionally does not catch exceptions so that error diagnosis (tracebacks and exception types) is available to the caller or the process manager; higher-level code that mounts main as an entrypoint (e.g., a console script wrapper) may choose to catch exceptions and map them to process exit codes or user-friendly messages.

## `sumy.__main__.handle_arguments` · *function*

## Summary:
Parses CLI-like arguments to select and prepare a parser, stop-words, stemmer and summarizer instance and returns (summarizer, parser, items_count) ready for use by the summarization pipeline.

## Description:
Known callers:
- The CLI entrypoint (the module main function that parses command-line arguments via docopt) calls this function once arguments are parsed and before running the summarizer pipeline. Typical trigger: user invokes the CLI with one summarization method flag (e.g., --luhn) and one source option (--url, --file, --text, or none to use stdin).

Why this logic is extracted:
- Encapsulates argument validation, input-source resolution, resource preparation (stop-words, tokenizer, stemmer) and summarizer selection in one place so the main CLI code remains focused on argument parsing and result output. Keeps responsibility for mapping docopt-style args to runtime objects separate from summarizer implementations.

## Args:
    args (dict[str, Any]):
        - The dictionary produced by docopt (or equivalent) containing parsed CLI options and flags.
        - Required keys referenced by the function:
            '--format' : Optional[str|None] - requested document format name (e.g. 'html' or 'plaintext'). If provided, must be a key in the global PARSERS mapping or a ValueError is raised.
            '--url' : Optional[str|None] - when present and non-None, function will fetch document bytes from this URL.
            '--file' : Optional[str|None] - when present and non-None, function will open and read the named file in binary mode.
            '--text' : Optional[str|None] - when present and non-None, function will use this string as the document content.
            '--length' : Any - passed verbatim to ItemsCount(value) to construct the items_count callable (see ItemsCount behaviour: accepts numeric values or strings such as '10' or '20%').
            '--language' : str - language identifier forwarded to Tokenizer and Stemmer and used by get_stop_words when no custom stopwords file is provided.
            '--stopwords' : Optional[str|False] - when truthy, treated as a filename and passed to read_stop_words(filename); when falsy, get_stop_words(language) is used instead.
        - Additionally, the function expects one of the method flags whose names are the keys of the global AVAILABLE_METHODS mapping to be present and truthy (e.g., '--luhn' or similar). The code selects the summarizer class by scanning AVAILABLE_METHODS and picking the first name where args[name] is true.

    default_input_stream (file-like object, optional):
        - Default: sys.stdin
        - A file-like object exposing read() to obtain document content when neither --url, --file nor --text is specified.
        - read() may return a str or bytes; the chosen parser must accept whatever type is produced.

## Returns:
    tuple (summarizer, parser, items_count)
        - summarizer: an instance of the summarizer class selected from AVAILABLE_METHODS, after being passed through build_summarizer(summarizer_class, stop_words, stemmer, parser). The summarizer is ready for use by the pipeline but may have been mutated by build_summarizer (e.g., stop-word or Edmundson-specific attribute assignments).
        - parser: an instance of the parser class constructed as parser(document_content, Tokenizer(language)). This is the parser object the summarizer will use; its type depends on PARSERS and the selected input source/format.
        - items_count: an ItemsCount instance (callable) constructed with args['--length'] that can be invoked with a sequence to slice the number/percentage of items requested.

All possible normal return flows:
- When input is a URL: parser = PARSERS[document_format or "html"], document_content fetched via fetch_url.
- When input is a file: parser = PARSERS[document_format or "plaintext"], document_content read from file in binary mode.
- When input is provided via --text: parser = PARSERS[document_format or "plaintext"], document_content taken from args['--text'].
- When no explicit input provided: parser = PARSERS[document_format or "plaintext"], document_content read from default_input_stream.read().

## Raises:
    ValueError
        - Raised immediately if args['--format'] is not None and not a key in the global PARSERS mapping. The function message identifies allowed PARSERS keys and the given format.
    StopIteration
        - Raised by the next(...) call if none of the names in AVAILABLE_METHODS are truthy in args (i.e., no summarizer method flag was selected). This indicates the caller did not select any available summarization method.
    FileNotFoundError / IOError / OSError
        - Possible when attempting to open args['--file'] in binary mode; errors propagate from built-in open().
    requests.exceptions.RequestException (or subclass)
        - Possible when fetch_url(args['--url']) is called; fetch_url will propagate network/HTTP errors (for example on non-2xx responses).
    LookupError
        - get_stop_words(language) raises LookupError if stop-words data for the requested language is not available.
    Any exception raised by parser instantiation, Tokenizer(language) or Stemmer(language)
        - These constructors may raise exceptions for invalid inputs; they are propagated.
    Any exception raised by build_summarizer (including AttributeError, TypeError)
        - build_summarizer instantiates and mutates the summarizer and may raise if inputs are incompatible (see build_summarizer contract).

## Constraints:
Preconditions:
    - The globals PARSERS and AVAILABLE_METHODS must be mappings: PARSERS keys are valid document format identifiers mapping to parser classes; AVAILABLE_METHODS keys correspond to option names in args and their values are summarizer classes/callables.
    - args must include the keys referenced above (common docopt output satisfies that).
    - If using Edmundson-specific behaviors later, the parser object returned must supply attributes expected by build_summarizer (significant_words, stigma_words) — but that check occurs inside build_summarizer.

Postconditions:
    - The returned summarizer is constructed and configured by build_summarizer with the chosen stemmer, stop-words, and parser.
    - The returned parser is an instantiated parser(document_content, Tokenizer(language)) ready to expose parsed document tokens/words.
    - The returned items_count is callable and encapsulates the requested slice/percentage semantics for summary length.

## Side Effects:
    - Network I/O: If args['--url'] is provided, fetch_url performs an HTTP GET (requests) and can perform network I/O and raise related exceptions.
    - File I/O: If args['--file'] or args['--stopwords'] are provided, the function opens the specified files in binary mode and reads them.
    - Standard input: In the fallback branch, default_input_stream.read() is called (sys.stdin by default), consuming input from stdin.
    - Object mutation: build_summarizer may mutate the summarizer instance (for example, assigning stop_words or Edmundson-specific attributes). No global state is modified by handle_arguments itself.

## Control Flow:
flowchart TD
    A[Start] --> B[document_format = args['--format']]
    B --> C{document_format provided and not in PARSERS?}
    C -- Yes --> D[Raise ValueError]
    C -- No --> E{args['--url'] is not None?}
    E -- Yes --> F[parser = PARSERS[document_format or 'html']]
    F --> G[document_content = fetch_url(args['--url'])]
    E -- No --> H{args['--file'] is not None?}
    H -- Yes --> I[parser = PARSERS[document_format or 'plaintext']]
    I --> J[open file rb -> document_content = file.read()]
    H -- No --> K{args['--text'] is not None?}
    K -- Yes --> L[parser = PARSERS[document_format or 'plaintext']]
    L --> M[document_content = args['--text']]
    K -- No --> N[parser = PARSERS[document_format or 'plaintext']]
    N --> O[document_content = default_input_stream.read()]
    G --> P[items_count = ItemsCount(args['--length'])]
    J --> P
    M --> P
    O --> P
    P --> Q[language = args['--language']]
    Q --> R{args['--stopwords'] truthy?}
    R -- Yes --> S[stop_words = read_stop_words(args['--stopwords'])]
    R -- No --> T[stop_words = get_stop_words(language)]
    S --> U[parser = parser(document_content, Tokenizer(language))]
    T --> U
    U --> V[stemmer = Stemmer(language)]
    V --> W[summarizer_class = next(cls for name,cls in AVAILABLE_METHODS.items() if args[name])]
    W --> X[summarizer = build_summarizer(summarizer_class, stop_words, stemmer, parser)]
    X --> Y[return (summarizer, parser, items_count)]

## Examples:
1) Using a local file and a concrete summarizer flag (happy path)
    - args example (conceptual):
        {'--format': 'plaintext', '--file': 'doc.txt', '--url': None, '--text': None,
         '--length': '5', '--language': 'english', '--stopwords': None,
         '--luhn': True, '--lex': False, ...}
    - Outcome:
        - Opens 'doc.txt' in binary mode, reads bytes into document_content.
        - Uses PARSERS['plaintext'] to create the parser when instantiating parser(document_content, Tokenizer('english')).
        - ItemsCount created from '5'.
        - stop_words loaded via get_stop_words('english').
        - summarizer_class chosen from AVAILABLE_METHODS where args[method] is True (here '--luhn').
        - summarizer is built via build_summarizer and function returns (summarizer, parser, items_count).

2) Reading from a URL and explicit format omitted
    - args:
        {'--format': None, '--url': 'http://example.com', '--file': None, '--text': None, ...}
    - Outcome:
        - document_format is None, so PARSERS['html'] is used for URL input.
        - fetch_url performs an HTTP GET; returned content (bytes) is passed to the chosen parser.

3) Error cases
    - Unsupported format:
        - If args['--format'] is 'xml' and PARSERS does not contain 'xml', a ValueError is raised immediately.
    - No summarizer selected:
        - If none of the keys in AVAILABLE_METHODS are truthy in args, the next(...) expression raises StopIteration; callers should ensure a method option is provided or catch this error and present a friendly message.

Notes:
- The function assumes caller-provided args adheres to docopt's structure; accurate error handling for missing keys is the caller's responsibility.
- build_summarizer may perform additional validation and mutations; failures originating there will propagate out of handle_arguments.

## `sumy.__main__.build_summarizer` · *function*

## Summary:
Creates a summarizer instance with the supplied stemmer and configures its word-collection attributes; uses a specialized assignment path for the EdmundsonSummarizer and a generic path for all other summarizers.

## Description:
This function centralizes the construction and initial configuration of summarizer objects used by the CLI or other orchestration code that selects a summarizer class and a parser. Typical callers: the program entrypoint which parses user arguments, creates a parser (HtmlParser or PlaintextParser), obtains stop words and a stemmer, then calls this function to build the configured summarizer before running the summarization pipeline.

Responsibility boundary:
- Encapsulates how parser-derived word lists and global stop words are mapped onto particular summarizer implementations.
- Does not perform validation of inputs beyond attempting construction and attribute assignment; any validation or normalization is left to the summarizer constructor and property setters.

Important implementation note (behavior observed in code):
- The branch that configures EdmundsonSummarizer uses an identity check: the condition is "summarizer_class is EdmundsonSummarizer". Only when the exact class object EdmundsonSummarizer is provided will the function follow the Edmundson-specific configuration path. Passing a subclass of EdmundsonSummarizer will follow the non-Edmundson path.

## Args:
    summarizer_class (type): Class or callable used to instantiate the summarizer. The function calls summarizer_class(stemmer). It's expected that the constructor accepts the stemmer as the first argument.
    stop_words (iterable[str] | frozenset[str] | None): Collection of stop words used by most summarizers, or assigned to EdmundsonSummarizer.null_words. The function does not validate that stop_words is non-empty or even iterable; such issues will surface when the summarizer or its setters operate on the value.
    stemmer (nlp.stemmers.Stemmer): Stemmer instance passed to the summarizer constructor. The summarizer (or its property setters) may call stemmer methods; provide an object compatible with the summarizer's expectations.
    parser (object | None): Parser instance (e.g., HtmlParser, PlaintextParser) required when summarizer_class is EdmundsonSummarizer; the function reads parser.significant_words and parser.stigma_words. The function does not check parser type — it accesses those attributes directly.

Interdependencies and notable behaviors:
- If summarizer_class is exactly EdmundsonSummarizer:
  - summarizer.null_words = stop_words
  - summarizer.bonus_words = parser.significant_words
  - summarizer.stigma_words = parser.stigma_words
  These assignments invoke EdmundsonSummarizer property setters (which stem words and store them as frozensets).
- Otherwise:
  - summarizer.stop_words = stop_words
  This is a direct attribute assignment; if the summarizer class exposes a property named stop_words the setter will run, otherwise a new attribute may be set on the instance (unless the class prevents new attributes, which would raise an AttributeError).

## Returns:
    object: The configured summarizer instance returned by summarizer_class(stemmer) after performing attribute assignments described above.

Possible return shapes:
- An EdmundsonSummarizer instance with null_words, bonus_words, stigma_words properties set (these properties are converted by the summarizer's setters to frozensets of stemmed words).
- An instance of another summarizer class with a stop_words attribute set to the provided stop_words (either via property setter or direct attribute assignment).

The function never returns None unless the constructor itself returns None (which would be highly unusual).

## Raises:
The function does not raise new exceptions intentionally; it propagates exceptions that occur during instantiation or attribute assignment. Observed/likely exceptions include:
    TypeError: If the summarizer_class constructor signature is incompatible with the provided stemmer.
    Any exception raised by summarizer_class.__init__ (for example ValueError if the summarizer enforces constructor invariants).
    AttributeError: If the Edmundson-specific branch is taken but parser lacks significant_words or stigma_words attributes, or if assignment to summarizer.stop_words is not allowed by the summarizer class (for example because __slots__ prevents new attributes).
    TypeError or other exceptions from property setters if stop_words or parser-provided collections are not acceptable (e.g., non-iterable) for the summarizer's setter logic.
Additionally, downstream usage:
    ValueError (raised later by EdmundsonSummarizer methods): EdmundsonSummarizer will raise ValueError when its internal checks detect an empty bonus/null/stigma set at method invocation time (the function itself only assigns values).

## Constraints:
Preconditions (caller responsibilities):
- Provide a summarizer_class whose constructor accepts a stemmer as the first parameter.
- If using EdmundsonSummarizer exactly, provide a parser with attributes significant_words and stigma_words; these should be iterables of strings.
- Be aware that stop_words may be assigned verbatim; if downstream summarizer logic expects a non-empty iterable, ensure stop_words meets that expectation.

Postconditions:
- The returned summarizer is constructed with the supplied stemmer.
- The returned summarizer has been mutated to include the stop/bonus/null/stigma word assignments as described; any invalid assignments will have raised an exception before return.

## Side Effects:
- Mutates the returned summarizer instance (assigns attributes or invokes property setters).
- No file, network, or standard I/O occurs inside this function.
- No global state is modified.

## Control Flow:
flowchart TD
    A[Start] --> B[Call summarizer_class(stemmer)]
    B --> C{summarizer_class is EdmundsonSummarizer?}
    C -- Yes --> D[Assign summarizer.null_words = stop_words]
    D --> E[Assign summarizer.bonus_words = parser.significant_words]
    E --> F[Assign summarizer.stigma_words = parser.stigma_words]
    F --> H[Return summarizer]
    C -- No --> G[Assign summarizer.stop_words = stop_words]
    G --> H[Return summarizer]

## Examples:
1) Non-Edmundson summarizer
    - Input:
        summarizer_class = LexRankSummarizer
        stop_words = ('a','the','is')
        stemmer = some_stemmer
        parser = PlaintextParser.from_string(...)
    - Behavior:
        - Calls LexRankSummarizer(some_stemmer)
        - Sets summarizer.stop_words = ('a','the','is') (this invokes the summarizer's stop_words setter if present)
        - Returns the summarizer instance

2) EdmundsonSummarizer (exact class)
    - Input:
        summarizer_class = EdmundsonSummarizer
        stop_words = ('a','the')
        stemmer = some_stemmer
        parser = HtmlParser.from_string(html, url, tokenizer)
    - Behavior:
        - Calls EdmundsonSummarizer(some_stemmer)
        - Calls summarizer.null_words = ('a','the')  (EdmundsonSummarizer.null_words setter will stem and frozenset the collection)
        - Calls summarizer.bonus_words = parser.significant_words
        - Calls summarizer.stigma_words = parser.stigma_words
        - Returns the EdmundsonSummarizer instance
    - Important: If parser.significant_words or parser.stigma_words are empty, EdmundsonSummarizer property setters accept them, but subsequent calls to EdmundsonSummarizer methods may raise ValueError if those sets are required and empty.

3) Edge cases to handle at call site:
    - Passing a subclass of EdmundsonSummarizer: this function will not use the Edmundson-specific branch due to identity comparison; the subclass will receive stop_words via the generic branch unless the caller passes the exact base class.
    - Providing stop_words = None: the function will assign None; this will either succeed (if the summarizer accepts None) or cause errors later when the summarizer tries to iterate or stem items.
    - Missing parser when using EdmundsonSummarizer: trying to access parser.significant_words will raise AttributeError; ensure parser is non-None and has the required attributes before calling.

Usage recommendation:
- Callers that wish to support subclasses of EdmundsonSummarizer should either pass the base class object explicitly or perform their own subclass detection and configuration prior to calling this function.
- Validate inputs (stop_words and parser) at the call site if you need fail-fast behavior with clearer error messages.

