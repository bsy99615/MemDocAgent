# `html.py`

## `sumy.parsers.html.HtmlParser` · *class*

*No documentation generated.*

### `sumy.parsers.html.HtmlParser.from_string` · *method*

## Summary:
Factory classmethod that constructs and returns a new HtmlParser (or subclass) instance from an in-memory HTML payload and a tokenizer. It initializes the parser's internal Article via the class constructor.

## Description:
- Known callers and context:
    - Companion factory methods in the same class: from_file and from_url. These obtain HTML bytes (from disk or network) and then instantiate the parser via the same constructor path.
    - Typical pipeline stage: called at the start of the parsing pipeline when raw HTML is already available in memory and an HtmlParser instance is required to build the document model (via the document property) or to compute significant/stigma words.
- Why this is a separate method:
    - Provides a clear, source-agnostic factory for the common case "I have HTML in memory → give me a parser".
    - Keeps creation logic for different sources (string/file/URL) separate, centralizing the construction call.

Important detail about argument ordering:
    - The method signature is from_string(cls, string, url, tokenizer) — tokenizer is the third positional parameter.
    - When creating the instance it calls cls(string, tokenizer, url). That is, the method forwards tokenizer as the second positional argument and url as the third to the class constructor. This matches HtmlParser.__init__(self, html_content, tokenizer, url=None) but means callers must supply tokenizer as the third argument to from_string (or use keyword arguments) to avoid confusion.

## Args:
    string (str | bytes):
        HTML content to parse. Forwarded unchanged to the class constructor and ultimately to breadability.readable.Article.
    url (str | None):
        Source URL associated with the HTML content. The parameter is required positionally in from_string but may be None. It is forwarded to Article.
    tokenizer (object):
        Tokenizer instance required by the parser framework. Must be compatible with DocumentParser/HtmlParser expectations. Passing an incompatible object or None may raise during construction or at tokenization time.

## Returns:
    cls (HtmlParser or subclass):
        A newly-constructed parser instance. Observable facts about the returned object:
        - HtmlParser.__init__ assigns self._article = Article(html_content, url), so the returned instance will have _article set.
        - The tokenizer is passed through to the constructor and base class initializer; the exact attribute name used to store it is determined by DocumentParser.
      Cached properties (document, significant_words, stigma_words) are computed lazily on first access and are not populated by this factory method.

## Raises:
    - Propagates any exception raised during construction. from_string does not perform error handling itself.
    - Possible sources of exceptions:
        - Errors from breadability.readable.Article when given the provided content and url (e.g., parsing errors).
        - TypeError, ValueError, or other errors raised by cls.__init__ or DocumentParser.__init__ when tokenizer or arguments are invalid.

## State Changes:
- Attributes READ:
    - None on existing instances — this is a classmethod and does not access instance state.
- Attributes WRITTEN (on the returned instance):
    - _article: set inside HtmlParser.__init__ to Article(html_content, url).
    - Additional attributes may be initialized by cls.__init__ and DocumentParser.__init__ (for example, where the tokenizer is stored), but those names are determined by those constructors.

## Constraints:
- Preconditions:
    - The string argument must be provided and should contain the HTML content to parse.
    - tokenizer must be a valid tokenizer object compatible with the parser framework.
    - url should be a string or None.
    - Callers must respect the method signature ordering (string, url, tokenizer) or use keyword arguments; the method will re-order arguments when calling the constructor.
- Postconditions:
    - Returns an instance of cls whose _article wraps the provided HTML content and url.
    - No cached parsing properties are precomputed by this call.

## Side Effects:
- No file, network I/O, or external service calls are performed directly by from_string.
- Instantiates an Article object in-memory and calls cls.__init__ and DocumentParser.__init__, which allocate memory and may perform in-memory processing of the HTML.
- Any exceptions during those initializations propagate to the caller.

### `sumy.parsers.html.HtmlParser.from_file` · *method*

## Summary:
Creates and returns a new parser instance by reading the entire contents of a local file (binary mode) and passing those bytes to the parser constructor.

## Description:
Known callers and lifecycle:
- No specific internal call sites were identified in the repository for this method. It is intended to be used wherever a HtmlParser is constructed from a local HTML file (for example in tests, scripts, or CLI tools that accept a path to an HTML file).
- Typical pipeline stage: factory/initialization step when preparing an HtmlParser for downstream processing (tokenization, document model construction, summarization).
- Related factory methods: from_string (constructs from an in-memory string) and from_url (fetches remotely then constructs). This method exists to provide a concise, reusable way to create a parser from a file path without requiring callers to open/read files themselves.

Why this is a separate method:
- Encapsulates file I/O and instance construction in a single, well-named classmethod for convenience and to keep caller code small and consistent with other HtmlParser factory methods.
- Keeps file-reading concerns (binary mode, reading whole content) out of higher-level code and centralizes how the parser is instantiated from on-disk HTML.

## Args:
    file_path (str | os.PathLike):
        Path to the file to open. Will be passed to Python's built-in open() as the first argument.
    url (str | None):
        The URL to associate with the document content (used by Article and by HtmlParser.__init__). May be None if not known.
    tokenizer (object):
        Tokenizer object required by the parser. Must satisfy the tokenizer interface expected by DocumentParser/HtmlParser (the object passed is forwarded to the parser constructor and ultimately used by methods such as tokenize_words and tokenize_sentences).

## Returns:
    object:
        An instance of cls (typically HtmlParser or a subclass) constructed with:
        - html_content: the raw bytes read from the file (result of file.read())
        - tokenizer: the tokenizer argument passed through
        - url: the url argument passed through

    Edge cases:
    - If the file is empty, the returned instance is constructed with empty bytes (b""), and downstream behavior depends on the parser/Article handling of empty content.
    - If cls.__init__ or Article(...) raises, no instance is returned.

## Raises:
    FileNotFoundError:
        If the file at file_path does not exist (raised by open()).
    OSError (includes IOError):
        For other I/O errors while opening or reading the file (permission errors, device errors).
    TypeError:
        If file_path is of an unsupported type for open() (e.g., None).
    Exception:
        Any exception raised during cls(...) construction (including exceptions from Article parsing) will propagate to the caller.

## State Changes:
Attributes READ:
    - None on an existing instance (this is a classmethod and does not read instance attributes).

Attributes WRITTEN:
    - None on an existing instance (this creates and returns a new instance; any attributes set occur inside cls.__init__, not inside this method).

## Constraints:
Preconditions:
    - file_path must refer to a readable file path accessible to the process.
    - tokenizer must satisfy the parser/tokenizer interface expected by HtmlParser (i.e., be usable by DocumentParser and HtmlParser methods).
    - Caller should expect the entire file to be loaded into memory; extremely large files may exhaust memory.

Postconditions:
    - The returned object's constructor was invoked with html_content equal to the raw bytes read from the file, tokenizer equal to the tokenizer argument, and url equal to the url argument.
    - No modifications are made to cls or other global state by this method itself.

## Side Effects:
    - Performs file I/O: opens file_path in binary mode ("rb") and reads its entire contents into memory.
    - Memory usage: loads the whole file contents into a bytes object; large files can cause high memory consumption.
    - May propagate exceptions from file I/O or from cls(...) (including Article-related parsing side effects performed in __init__).

### `sumy.parsers.html.HtmlParser.from_url` · *method*

## Summary:
Fetches the resource at the given URL, then constructs and returns a new parser instance by calling cls(data, tokenizer, url). Does not modify existing parser instances.

## Description:
This method performs two simple, observable actions: (1) calls fetch_url(url) to obtain the remote document content and (2) calls cls(data, tokenizer, url) and returns the constructed object. The first parameter is named cls and is passed to cls(...) — therefore the implementation expects the caller to supply a class or class-like callable as that first argument.

Why this logic is separated:
- Centralizes the "fetch then construct" pattern so callers can obtain a ready-to-use parser instance with a single call.
- Keeps network I/O (fetch_url) and construction logic in one place rather than duplicating that flow wherever a parser is needed.

Typical call sites (inferred):
- Higher-level code that starts from a URL and needs a parser instance for that remote document.
- Factory or convenience helpers that accept a URL and forward to this routine.
(Note: these call sites are inferred from the method's behavior; they are not enumerated in the source snippet.)

## Args:
    cls (type or callable): A class or callable used to construct the parser instance. The method will call cls(data, tokenizer, url).
    url (str): URL string identifying the remote HTML document to fetch. Must be acceptable to the project's fetch_url utility.
    tokenizer (object): Tokenizer object (or other parse-time dependency) forwarded unchanged to the constructor.

## Returns:
    object: The result of cls(data, tokenizer, url). The concrete type and initialization behavior depend on cls.__init__ / cls.__call__.
    Edge cases:
    - If fetch_url(url) returns None, an empty string, or otherwise unexpected data, this method still calls cls with that value; resulting behavior is determined by cls.
    - If cls returns None (unusual), that is returned to the caller unchanged.

## Raises:
    - Any exception raised by fetch_url(url) (e.g., network, HTTP, or utility-specific exceptions) is propagated.
    - Any exception raised by calling cls(data, tokenizer, url) (e.g., constructor validation errors) is propagated.
    This method does not catch or wrap exceptions.

## State Changes:
    Attributes READ:
        - None on existing instances (method does not reference self or instance attributes).
    Attributes WRITTEN:
        - None on existing instances. A new object is created and returned.

## Constraints:
    Preconditions:
        - The first argument passed as cls must be callable with three positional arguments: (data, tokenizer, url).
        - url should be a valid URL for fetch_url; tokenizer should meet the expectations of cls.
    Postconditions:
        - If no exception is raised, the returned value is the object produced by cls(data, tokenizer, url).
        - No mutation of caller-local state or existing parser instances is performed by this method itself.

## Side Effects:
    - Performs network I/O by calling fetch_url(url). This may incur latency and network-related exceptions.
    - Any additional side effects are possible only via fetch_url or cls (for example, cls.__init__ may perform file or DB I/O); this method does not itself perform those actions.
    
## Usage notes:
    - If this method is intended to be used as a conventional class-level factory, it can be invoked with the class object as the first argument; for example, provide the parser class as the cls parameter so that cls(...) constructs an instance.
    - Callers that already have the HTML/data can bypass this method and call cls(data, tokenizer, url) directly to avoid an extra fetch.

### `sumy.parsers.html.HtmlParser.__init__` · *method*

## Summary:
Initializes a HtmlParser instance by delegating tokenizer setup to the base DocumentParser and creating a breadability Article from provided HTML content (stored on the instance).

## Description:
This constructor is called when a caller instantiates HtmlParser to parse or analyze HTML input as part of a parsing/summarization pipeline. Typical usage is at the start of a document parsing step where a tokenizer is already selected and raw HTML content (and optionally the source URL) is available.

The method delegates tokenizer-related initialization to the superclass (DocumentParser) so that all tokenizer handling and related state live in the parent class. It isolates the Article construction into the constructor so that the Article object (which encapsulates extraction/cleanup of readable HTML) is available as a stable attribute for subsequent parsing operations on this parser instance.

Known callers and lifecycle stage:
- Any code that needs to create an HtmlParser to convert HTML into the library's DOM model (for example, before converting to ObjectDocumentModel or before summarization). The constructor is invoked once at parser instantiation — the beginning of the HTML parsing stage of the pipeline.

This logic is a constructor because:
- Parent-class initialization (tokenizer) must run before this parser is used.
- The parsed/cleaned representation (Article) is a long-lived, per-instance artifact required by other HtmlParser methods; creating it here centralizes initialization and avoids re-parsing.

## Args:
    html_content (str or bytes):
        Raw HTML content to be processed. This value is passed directly to breadability.readable.Article.
        - Required: must be provided (the constructor does not validate it).
        - Typical values: an HTML document string returned from an HTTP fetch or loaded from disk.
    tokenizer (object):
        Tokenizer instance or object expected by the base DocumentParser. This argument is forwarded unchanged to the superclass constructor.
        - The class expects a tokenizer compatible with DocumentParser (i.e., providing the API DocumentParser uses).
    url (str, optional):
        Optional base URL for the content (used by Article for resolving relative links and for metadata). Defaults to None.

## Returns:
    None
    - As a constructor, it does not return a value; it initializes instance state.

## Raises:
    - No explicit exceptions are raised by this constructor itself.
    - Any exception raised by DocumentParser.__init__(tokenizer) will propagate.
    - Any exception raised by breadability.readable.Article(html_content, url) (e.g., if the content cannot be parsed) will propagate to the caller.
    - Because there is no validation in this constructor, passing invalid types (e.g., tokenizer=None when DocumentParser requires a concrete tokenizer) may cause errors from the delegated calls.

## State Changes:
    Attributes READ:
        - None explicitly read from self in this method prior to assignment (the call to the superclass constructor may read or initialize attributes defined by DocumentParser, but this constructor does not reference any pre-existing self.<attr> directly).
    Attributes WRITTEN:
        - self._article: assigned to an instance of breadability.readable.Article created with (html_content, url).
        - Any attributes set by DocumentParser.__init__ (via the super call) — those are initialized by the parent constructor, not by this method directly.

## Constraints:
    Preconditions:
        - tokenizer: must be a valid tokenizer accepted by DocumentParser.__init__.
        - html_content: should be a string or bytes containing HTML; passing None or an incompatible type is not validated here and may lead to exceptions from Article.
        - url (if provided): should be a str representing a URL or None.
    Postconditions:
        - After this call, self is ready for HtmlParser instance methods that operate on self._article.
        - self._article is set (assuming Article construction succeeded) to the Article instance produced by breadability.readable.Article(html_content, url).
        - The tokenizer-related state from DocumentParser is initialized (assuming parent initialization succeeded).

## Side Effects:
    - Constructs a breadability Article from the provided HTML; this triggers whatever CPU/memory operations and internal parsing breadability.Article performs.
    - There is no explicit I/O (file or network) in this constructor itself; any I/O-like side effects depend on the behavior of breadability.readable.Article or DocumentParser.__init__ and will be propagated.
    - No mutation of global state is performed directly by this method; it only mutates instance state (self._article and whatever the superclass sets).

### `sumy.parsers.html.HtmlParser.significant_words` · *method*

## Summary:
Compute and return a tuple of token strings extracted from HTML fragments annotated with any "significant" tags; if no tokens are found, return the parser's fallback SIGNIFICANT_WORDS. The result is computed lazily and cached for subsequent accesses.

## Description:
This cached property iterates over self._article.main_text (the Article-produced annotated paragraphs). For each text fragment whose annotations contain any tag from SIGNIFICANT_TAGS (for example, heading and emphasis tags such as "h1", "em", "strong"), it calls tokenize_words on the fragment text and accumulates the returned tokens in document order. If at least one token is accumulated, the method returns a new tuple(tokens). If no tokens are produced from any matching fragments, it returns self.SIGNIFICANT_WORDS instead.

Known callers and lifecycle:
- Accessed by downstream consumers that need a compact set of "significant" tokens extracted from HTML during parsing/analysis stages (e.g., feature extraction for summarization or ranking).
- Evaluated lazily on first access (because of cached_property) and reused on subsequent accesses.

Why this is its own property:
- Encapsulates the selection (based on annotations), tokenization, fallback logic, and caching in one place so other components can simply consume a ready-to-use tuple of significant tokens.

## Args:
    None.

## Returns:
    tuple[str]: A tuple of token strings in the order they were discovered.
    - If one or more tokens are produced by tokenize_words across matching fragments, returns tuple(tokens).
    - If no tokens are produced (i.e., the accumulated list would be empty), returns self.SIGNIFICANT_WORDS (the parser's predefined fallback tuple).
    - The fallback is returned by reference; callers may observe that returned is self.SIGNIFICANT_WORDS when no tokens are found.
    - Tokens are not deduplicated or normalized by this property; duplicates and original token casing are preserved as returned by the tokenizer.

## Raises:
    - This property does not raise exceptions intentionally. However, exceptions from called components propagate:
        * Any exception raised while iterating self._article.main_text (e.g., malformed Article structure) will propagate.
        * Any exception from self._contains_any (e.g., TypeError if annotations is of an unexpected type) will propagate.
        * Any exception from tokenize_words / the tokenizer implementation will propagate.
    - No exception is raised specifically to indicate "no tokens found" — the fallback tuple is returned instead.

## State Changes:
    Attributes READ:
        - self._article (reads self._article.main_text; expects an iterable of paragraphs)
        - self.SIGNIFICANT_TAGS (used to select annotated fragments)
        - self.SIGNIFICANT_WORDS (fallback value if no tokens are found)
        - self._contains_any (predicate used to test annotations)
        - self.tokenize_words (tokenizer wrapper used to obtain tokens)

    Attributes WRITTEN:
        - The cached_property mechanism will record the computed value so subsequent attribute access does not recompute it. The exact storage behavior depends on the cached_property implementation, but callers should expect the computed tuple to be cached on the instance after first access.

## Constraints:
    Preconditions:
        - self._article must be initialized (set in __init__) and expose main_text as an iterable of paragraphs.
        - Each paragraph must be an iterable of (text, annotations) pairs where:
            * text is str.
            * annotations is either None or a container supporting membership testing for tag name strings (e.g., list, tuple, set). _contains_any explicitly treats None as "no annotations".
        - A tokenizer must be available (self._tokenizer) and tokenize_words must return an iterable of str tokens for a given text fragment.

    Postconditions:
        - After successful evaluation, the instance will present a cached tuple value for the significant_words property equal to the returned value.
        - The returned tuple is either a new tuple of tokens or a reference to self.SIGNIFICANT_WORDS when no tokens were found.
        - No other instance attributes are modified.

## Side Effects:
    - Caching: on first access the value will be cached (written) by the cached_property decorator; this avoids re-running tokenization. The method body does not explicitly assign to attributes.
    - No I/O, network, or external service calls are performed by this method itself.
    - The tokenizer may perform language-specific splitting or normalization; any such behavior is provided by tokenize_words and not performed here.

## Performance notes:
    - Complexity is proportional to the number and size of annotated fragments in Article.main_text and to the tokenizer's cost. Tokenization can be non-trivial for long fragments; avoid repeated accesses before caching.

## Example usage:
    # Access lazily computed cached tuple of significant tokens
    tokens = parser.significant_words
    # tokens is a tuple[str]; if no annotated significant fragments produced tokens,
    # tokens is equal to parser.SIGNIFICANT_WORDS

### `sumy.parsers.html.HtmlParser.stigma_words` · *method*

## Summary:
Returns a tuple of tokenized words extracted from HTML fragments marked with "stigmatized" tags (commonly "a", "strike", "s"); if no such words are found, returns the parser's default STIGMA_WORDS. Because this property is computed with cached_property, the result is stored on the parser instance after the first access.

## Description:
Known callers and lifecycle:
- Called when client code accesses HtmlParser.stigma_words (it's defined as a cached property on the HtmlParser class).
- The computation runs during the parser's analysis stage when the Article object has been constructed (typically immediately after HtmlParser initialization if the caller requests this property). It is run once and cached for subsequent accesses.
- This property is intended for consumers that need words coming specifically from HTML fragments annotated with stigmatized tags (for downstream scoring, feature extraction, or keyword analysis).

Why this is a separate method/property:
- Encapsulates the traversal of the Article.main_text annotated structure, tag-based selection, and tokenization logic in a single place. Keeping it separate avoids duplicating the tag-filtering + tokenization logic in other properties or modules and allows using a sensible default (DocumentParser.STIGMA_WORDS) when no matching fragments exist.

## Args:
    None

## Returns:
    tuple[str]:
        - A tuple of token strings collected, in document order, from all text fragments whose annotations contain any of the stigmatized tag names ("a", "strike", "s").
        - If no such fragments are found or no tokens are produced by the tokenizer, returns self.STIGMA_WORDS (a tuple defined on the parent DocumentParser class).
        - Edge cases:
            * If Article.main_text is empty or contains no annotated fragments with the stigmatized tags, the return value is self.STIGMA_WORDS.
            * If tokenize_words yields an empty sequence for all matched fragments, the method still treats that as "no words found" and returns self.STIGMA_WORDS.

## Raises:
    - Any exceptions raised by the underlying tokenizer via tokenize_words (propagated).
    - Any exceptions raised by membership testing in _contains_any if the annotations objects do not support membership testing (e.g., TypeError) — these are propagated.
    - No exceptions are raised explicitly by this method.

## State Changes:
    Attributes READ:
        - self._article (expects an Article-like object with a main_text iterable)
        - self.STIGMA_WORDS (fallback tuple from the DocumentParser parent)
    Attributes WRITTEN:
        - None directly by this method's body. However, because stigma_words is declared with @cached_property in HtmlParser, the cached_property wrapper will write the computed tuple to an instance attribute so subsequent accesses return the cached value.

## Constraints:
    Preconditions:
        - self._article must be initialized (HtmlParser.__init__ sets it to an Article instance).
        - self._article.main_text must be an iterable of "paragraph" values where each paragraph is itself iterable yielding (text, annotations) pairs.
            * text must be a string suitable for passing into tokenize_words.
            * annotations must be either None or a container that supports membership testing for tag names (e.g., sequences or sets of tag-name strings).
        - self._contains_any and self.tokenize_words must be present and behave as small helpers:
            * _contains_any(sequence, *tags) should return True if any tag is present in sequence, handling sequence == None safely.
            * tokenize_words(text) must return an iterable of token strings.

    Postconditions:
        - Returns a tuple of strings (either tokens collected from stigmatized fragments, or self.STIGMA_WORDS).
        - If accessed via the class-level cached_property, a cached attribute containing the returned tuple will be set on the instance so subsequent accesses reuse the computed value.

## Side Effects:
    - No I/O, network calls, or external service interactions are performed by this method.
    - Calls into self.tokenize_words; any side effects of the tokenizer (if present) will be incurred.
    - The cached_property wrapper (declared on the class) will store the computed tuple on the parser instance after the first computation, mutating the instance attribute namespace.
    - Does not mutate self._article or any paragraph/annotation objects itself.

### `sumy.parsers.html.HtmlParser._contains_any` · *method*

## Summary:
Checks whether any of the provided items appear in a given sequence and returns a boolean result; used as a small, side-effect-free helper during parsing.

## Description:
Known callers and lifecycle:
- Called by the cached property significant_words while iterating annotated paragraphs to decide whether a text fragment is marked with any of the "significant" HTML tags (SIGNIFICANT_TAGS).
- Called by the cached property stigma_words while iterating annotated paragraphs to detect "stigma" tags such as "a", "strike", or "s".
- These callers invoke the method during the parser's analysis phase when extracting tokenized words from annotated HTML content (i.e., when the parser reads Article.main_text and computes cached properties).

Why this is a separate method:
- Encapsulates a common membership check (including a None guard) used in multiple properties for clarity and to avoid duplicating the None-handling and membership loop.
- Keeps the calling code concise and semantically clearer (reads like a predicate).

## Args:
    sequence (Iterable or None): The container to check for membership. Must be None or an object that supports Python's membership operator (the "in" test), e.g., list, tuple, set, dict keys view, or str.
    *args (object): One or more items to test for presence in sequence. In the HtmlParser context these are typically tag name strings (e.g., "h1", "a"), but any objects comparable by membership are accepted.

## Returns:
    bool: True if at least one of the items in *args is found in sequence; False otherwise.
    Edge-case returns:
    - Returns False immediately if sequence is None.
    - Returns False if no args are supplied (the method checks each provided item; if none are provided the loop is skipped and False is returned).

## Raises:
    TypeError: May be raised if sequence is neither None nor a type that supports membership testing (for example, an int). This exception is not raised directly by the method but can be propagated from Python's membership operation when it is unsupported for the provided sequence.

## State Changes:
    Attributes READ:
        None (the method does not read any self.<attr> fields)
    Attributes WRITTEN:
        None (the method does not modify any self.<attr> fields)

## Constraints:
    Preconditions:
        - sequence must be either None or an object that supports the "in" membership test (iterable or container).
        - Items passed in *args should be of types for which membership checks against sequence are meaningful (in the parser, usually strings representing tag names).
    Postconditions:
        - The object's state (self) is unchanged.
        - The method returns a boolean that accurately reflects whether any of the provided items are contained in sequence.

## Side Effects:
    - None. No I/O, no network calls, no external service interactions, and no mutations to objects outside self.
    - Any exceptions from membership tests (e.g., TypeError) are propagated to the caller.

### `sumy.parsers.html.HtmlParser.document` · *method*

## Summary:
Constructs and returns an ObjectDocumentModel by converting the breadability-parsed article (self._article.main_text) into a list of Paragraph objects composed of Sentence objects; headings are preserved as heading Sentences and non-heading text is tokenized into sentences.

## Description:
This method is invoked during the parsing stage when an HtmlParser instance converts a parsed Article into the parser's internal document model. Typical callers are higher-level parsing routines that orchestrate fetching/reading HTML and then call HtmlParser.document to obtain a structured representation for further processing (summarization, analysis, etc.).

It is implemented as a separate method because transforming the article's annotated structure into the ObjectDocumentModel requires several distinct steps (iterating annotated paragraphs, treating headings specially, aggregating plain text segments, tokenizing aggregated text into sentences, and assembling the model). Encapsulating this logic keeps tokenization/assembly concerns isolated from network fetching, article extraction, and other parser responsibilities.

## Args:
This is an instance method and takes no arguments beyond self. It relies on the following attributes/methods to exist on self:
    - self._article (breadability.readable.Article-like): must have a main_text attribute described below.
    - self._tokenizer: tokenizer object passed to Sentence instances.
    - self.tokenize_sentences(text: str) -> Iterable[str]: method that splits a block of text into sentence strings.

Expected shapes/types:
    - self._article.main_text: an iterable of paragraphs, where each paragraph is itself an iterable of (text, annotations) pairs.
        * text: str (one segment of the paragraph)
        * annotations: None or a collection (e.g., list/set) of tag names such as "h1", "h2", "h3", "pre" etc.

## Returns:
    ObjectDocumentModel
    - Constructed with a list of Paragraph objects (one Paragraph per input paragraph).
    - Each Paragraph contains a list of Sentence objects. For each paragraph:
        * Any (text, annotations) segment annotated with "h1", "h2", or "h3" is converted into a Sentence with its is_heading flag set to True.
        * All non-pre segments (those without an annotations collection containing "pre") are concatenated (with spacing rules described below) into a single block, then tokenized using self.tokenize_sentences. Each resulting sentence string is wrapped in a Sentence (is_heading defaults to False).
    - Edge-case returns:
        * If the input has zero paragraphs (an empty iterable), an ObjectDocumentModel containing an empty paragraphs list is returned.

## Raises:
    - IndexError: If any text segment is an empty string, the code accesses text[0] when deciding spacing; this raises IndexError. Caller should ensure text segments are non-empty strings or the implementation should guard against empty strings.
    - TypeError: If self._article or self._article.main_text is None or not iterable, iteration will raise TypeError. Also, if paragraph elements are not 2-tuples (text, annotations), unpacking will raise an error.
    - Any exception raised by:
        * self.tokenize_sentences (e.g., ValueError for invalid input),
        * the Sentence constructor,
        * the Paragraph constructor,
        * the ObjectDocumentModel constructor,
      will propagate to the caller.

## State Changes:
Attributes READ:
    - self._article (read to obtain main_text)
    - self._tokenizer (passed to Sentence constructors)
    - self.tokenize_sentences (invoked to split concatenated paragraph text)

Attributes WRITTEN:
    - None. The method does not modify self attributes.

## Constraints:
Preconditions:
    - self._article must be set and have a main_text attribute that is an iterable producing paragraph-like iterables.
    - Each paragraph produced by main_text must be an iterable of (text: str, annotations: Optional[Collection[str]]) pairs.
    - self.tokenize_sentences must accept a single str and return an iterable of str.
    - Sentence, Paragraph, and ObjectDocumentModel constructors must accept the calls used herein:
        * Sentence(text: str, tokenizer, is_heading: bool = False)
        * Paragraph(list_of_sentences)
        * ObjectDocumentModel(list_of_paragraphs)

Postconditions:
    - The returned ObjectDocumentModel contains one Paragraph per input paragraph.
    - Within each Paragraph:
        * Heading segments (annotations containing "h1", "h2", or "h3") appear as individual Sentence objects with is_heading=True in the same order they appeared among segments.
        * All non-pre segments are concatenated in original segment order, tokenized by self.tokenize_sentences, and included as Sentence objects (is_heading=False) following any heading Sentences for that paragraph.
    - No attributes on self are modified.

## Behavior details / Implementation notes (important for reimplementation):
    - Iteration order is preserved: paragraphs and segments within paragraphs are processed in the order they appear.
    - For segments that are headings (annotations contains any of "h1","h2","h3"): that segment is not merged into the paragraph text buffer; instead a Sentence is created immediately with is_heading=True.
    - For segments annotated with "pre": they are skipped entirely (neither added to the current_text buffer nor converted to heading Sentences).
    - Spacing concatenation rule for non-heading, non-pre segments:
        * Maintains a local current_text string per paragraph.
        * For each segment text, if the first character of the segment (text[0]) is a punctuation character (from string.punctuation), the segment is concatenated without a leading space; otherwise it is concatenated with a single leading space.
        * Note: The original implementation unconditionally checks text[0] — if text is an empty string this causes IndexError (see Raises). A robust reimplementation should guard against empty text segments (e.g., treat empty text as no-op or skip).
    - After processing all segments in a paragraph, current_text is passed to self.tokenize_sentences; the returned sentence strings are each wrapped with Sentence(s, self._tokenizer) and appended to the paragraph's sentence list.
    - The method assumes Sentence/Paragraph/ObjectDocumentModel handle any needed normalization and internal validations.

## Side Effects:
    - No I/O is performed by this method.
    - No network or external service calls.
    - The only mutations are creation of new Sentence/Paragraph/ObjectDocumentModel objects; no mutation of external objects passed by the caller occurs (unless constructors have side effects).

