# `__main__.py`

## `sumy.evaluation.__main__.build_random` · *function*

## Summary:
Returns a newly constructed RandomSummarizer instance (a summarizer that selects sentences at random); both provided arguments are ignored.

## Description:
Known callers:
- CLI dispatcher / evaluation entrypoint in this module (the function that maps user-selected summarizer names to builder functions, e.g., handle_arguments called from main). Typical trigger: the user or test chooses the "random" summarizer and the dispatcher invokes the corresponding build_* factory to obtain a ready-to-use summarizer.

Why this is a separate function:
- Provides a consistent factory function signature across different summarizer builders (parser, language) so the CLI/dispatcher can uniformly call a builder regardless of summarizer-specific needs.
- Keeps dispatcher code concise by centralizing construction of each summarizer type behind a simple, discoverable function even when no configuration is required.

## Args:
    parser (object): Unused. Accepted for API symmetry with other build_* functions in this module. Any value may be passed (including None); it has no effect on the result.
    language (str): Unused. Accepted for API symmetry and to allow callers to pass the same arguments to all builder functions. Any string (or None) may be passed; it is ignored.

Interdependencies:
- There are no interdependencies between the parameters; neither is inspected or used.

## Returns:
    RandomSummarizer: A fresh instance of the RandomSummarizer class.
    - Semantics: The returned object implements the summarizer interface used elsewhere in the project (callable/iterable that accepts a Document and a sentences_count and yields or returns selected sentences).
    - Edge cases:
        * A new, independent instance is returned on every call.
        * If RandomSummarizer's constructor raises (for example due to resource failures or internal checks), that exception propagates to the caller.

## Raises:
    - This function does not raise exceptions itself. Any exception raised by RandomSummarizer() during construction is propagated unchanged (type and message are determined by RandomSummarizer's implementation).

## Constraints:
Preconditions:
    - None required. The function makes no assumptions about parser or language values; they may be None or any object.

Postconditions:
    - On successful return, a RandomSummarizer instance has been allocated and returned.
    - No global state is modified by this function.

## Side Effects:
    - Object creation: instantiates a RandomSummarizer (memory allocation and any initialization performed by that class).
    - No I/O (file, network, stdout) is performed by this function itself.
    - No global variables, caches, or external services are modified by this function.

## Control Flow:
flowchart TD
    Start --> Instantiate[Call RandomSummarizer() to construct instance]
    Instantiate -->|Success| Return[Return new RandomSummarizer instance]
    Instantiate -->|Constructor raises Exception| Propagate[Propagate exception to caller]
    Return --> End
    Propagate --> End

## Examples (usage in prose):
- Dispatcher usage:
  When the CLI/dispatcher resolves the user choice "random" it calls this builder with the parser and language arguments it has available; the call returns a RandomSummarizer instance which the dispatcher then invokes on a parsed document to produce random sentence selections.

- Simple error handling guidance:
  If the caller wants to guard against possible constructor errors, wrap the call in a try/except:
  * Try to obtain the summarizer via this factory; if an exception is raised by the RandomSummarizer constructor, catch it and handle/report it (for example, fall back to a different summarizer or present a clear error to the user).

## `sumy.evaluation.__main__.build_luhn` · *function*

## Summary:
Create and return a Luhn summarizer configured for the given language: attaches a Stemmer and loads language-specific stop words.

## Description:
This factory function constructs a LuhnSummarizer and configures it for a particular natural language. It instantiates a Stemmer for the requested language, passes that stemmer to the LuhnSummarizer constructor, and loads the language stop-words via get_stop_words into the summarizer's stop_words property.

Known callers:
    - No direct callers are present in the provided snippet. This function is designed as a small factory used by higher-level code (for example CLI or evaluation drivers) when a configured LuhnSummarizer instance is required.

Why this is a separate function:
    - Encapsulates the language-specific construction and configuration steps (stemmer creation + stop-words loading) so caller code can request a ready-to-use LuhnSummarizer without repeating these setup steps or knowing the specifics of how stop-words and stemming are wired into the summarizer.

## Args:
    parser (any):
        - Present for API compatibility with other builder functions in the module.
        - Note: This parameter is unused in the function body (ignored).
    language (str):
        - Language identifier (e.g., "english", "polish"). It will be normalized internally by the Stemmer and get_stop_words helpers.
        - Must be a value accepted by Stemmer and by the stop-words data loader.

## Returns:
    LuhnSummarizer
    - A ready-to-use LuhnSummarizer instance configured as follows:
        * Its stemmer is the callable produced by Stemmer(language) (used internally by the summarizer to stem words).
        * Its stop_words attribute is set to a frozenset of normalized stop words returned by get_stop_words(language).
    - The returned summarizer can be called with (document, sentences_count) to produce a summary (behavior implemented by LuhnSummarizer).

## Raises:
    LookupError:
        - If Stemmer(language) fails because there is no stemmer available for the requested language, Stemmer.__init__ raises LookupError.
        - If get_stop_words(language) cannot locate stop-words data for the language, it raises LookupError.
    (These exceptions are propagated directly; build_luhn does not catch them.)

## Constraints:
    Preconditions:
        - The provided language must be supported by the Stemmer mechanism (either a special stemmer or an available NLTK stemmer class).
        - Stop-words data for the language must exist in the package data (data/stopwords/<language>.txt).
    Postconditions:
        - The returned LuhnSummarizer has a working stemmer (callable) and stop_words set to a frozenset of normalized stop words.
        - No modifications to caller-provided objects (parser) are made.

## Side Effects:
    - Reads package data for stop-words via get_stop_words (this operation uses pkgutil.get_data internally and may perform I/O to access installed package resources).
    - May raise LookupError as described in "Raises".
    - No writes to files, no network calls, and no modification of global interpreter state are performed by build_luhn itself.

## Control Flow:
flowchart TD
    Start --> CreateStemmer[Create Stemmer(language)]
    CreateStemmer --> CreateSummarizer[Instantiate LuhnSummarizer(stemmer)]
    CreateSummarizer --> LoadStopWords[Call get_stop_words(language)]
    LoadStopWords --> SetStopWords[Assign summarizer.stop_words = stop_words]
    SetStopWords --> ReturnSummarizer[Return configured summarizer]
    CreateStemmer -->|Stemmer raises LookupError| Error1[Raise LookupError]
    LoadStopWords -->|get_stop_words raises LookupError| Error2[Raise LookupError]

## Examples:
    Typical usage (happy path):
        try:
            summarizer = build_luhn(None, "english")
            summary_sentences = summarizer(document, 3)
        except LookupError as e:
            # Handle missing stemmer or stop-words for the language
            print("Language configuration error:", e)

    Example showing error handling for unsupported language:
        try:
            summarizer = build_luhn(None, "some-unsupported-lang")
        except LookupError:
            # Report or fallback to a default summarizer
            summarizer = build_random_summarizer(None, "english")

## `sumy.evaluation.__main__.build_edmundson` · *function*

## Summary:
Constructs and configures an Edmundson summarizer for a given language and document parser, returning a ready-to-use summarizer whose word sets (null/bonus/stigma) are populated and stemmed.

## Description:
This function centralizes the creation and configuration of an EdmundsonSummarizer for a particular language and parser. Typical callers are CLI or evaluation code that need a configured summarizer before producing summaries — for example: a command-line evaluation tool that builds a summarizer from a parser (HtmlParser or PlaintextParser) and a language identifier, then applies it to a parsed document to produce top-ranked sentences.

The logic is extracted into its own function to:
- Encapsulate construction and consistent configuration of three interdependent word-sets (null, bonus, stigma) and the language stemmer in a single place.
- Keep higher-level code (CLI/evaluation pipeline) simpler and avoid repeating identical setup steps across different entry points.

## Args:
    parser (object): A document parser instance that exposes at least two attributes:
        - significant_words: an iterable (typically tuple) of words considered "bonus" (important) for Edmundson weighting.
        - stigma_words: an iterable (typically tuple) of words considered "stigma" (negative weight) for Edmundson weighting.
      Typical concrete types: instances of sumy.parsers.html.HtmlParser or sumy.parsers.plaintext.PlaintextParser.
      Note: Both attributes must be present and be iterable of strings; otherwise an AttributeError or TypeError may occur.
    language (str): Language identifier used to select a Stemmer and stop-words. It is passed to:
        - Stemmer(language) to create a language-specific stemmer callable.
        - get_stop_words(language) to load language-specific null/stop words.
      Accepted forms follow the project's normalize_language rules (e.g., 'english', 'en', case-insensitive forms supported by the Stemmer and stop-word loader).

Interdependencies:
    - The parser must have significant_words and stigma_words that are iterables of words; build_edmundson will stem the words using the summarizer's stemmer.
    - The language value must be supported by both the Stemmer factory and the stop-words data; if either is missing, errors are raised.

## Returns:
    EdmundsonSummarizer: A configured instance with the following guarantees:
        - summarizer._stemmer is initialized for the requested language (via Stemmer(language)).
        - summarizer.null_words is set to the set of stop-words for the language (each word stemmed) — stored internally as a frozenset.
        - summarizer.bonus_words is populated from parser.significant_words (each word stemmed) — stored as a frozenset.
        - summarizer.stigma_words is populated from parser.stigma_words (each word stemmed) — stored as a frozenset.
    Edge cases:
        - If parser.significant_words or parser.stigma_words is empty, the summarizer will receive an empty frozenset for that attribute; some Edmundson methods later may raise ValueError when those sets are required for a particular method (the summarizer defers validation until methods that need non-empty sets are invoked).

## Raises:
    AttributeError:
        - If the parser argument does not expose significant_words or stigma_words attributes.
    LookupError:
        - If a stemmer is not available for the given language (raised by the Stemmer constructor).
        - If stop-words are not available for the given language (raised by get_stop_words when package data is missing).
    TypeError:
        - If any of the attributes used as collections (significant_words, stigma_words) are not iterable, or if get_stop_words returns a non-iterable, mapping to frozenset may raise TypeError.
    Any exception raised by underlying constructors or helpers (propagated): e.g., errors raised by Stemmer, get_stop_words, or EdmundsonSummarizer initializer.

## Constraints:
Preconditions:
    - parser must be a parsed-document provider object with attributes:
        - significant_words: iterable of strings (or empty iterable)
        - stigma_words: iterable of strings (or empty iterable)
    - language must be an identifier recognized by both Stemmer(...) and get_stop_words(...).

Postconditions:
    - The returned summarizer is an EdmundsonSummarizer instance configured with:
        - a language-specific stemmer,
        - null_words, bonus_words, and stigma_words set to frozensets of stemmed tokens.
    - No network calls or global state mutations are performed by this function itself (aside from loading package data for stop-words).

## Side Effects:
    - I/O: get_stop_words loads stop-word data via package data access (pkgutil.get_data) from the package resources. This reads local package files (not a network operation).
    - No writes to disk, no network requests, no modification of global variables in this function.
    - Object creation: instantiates a Stemmer and an EdmundsonSummarizer (memory allocation and initialization side effects).

## Control Flow:
flowchart TD
    Start --> CreateStemmer[Create Stemmer(language)]
    CreateStemmer --> CreateSummarizer[Instantiate EdmundsonSummarizer(stemmer)]
    CreateSummarizer --> LoadStopWords[Call get_stop_words(language)]
    LoadStopWords --> SetNullWords[Set summarizer.null_words (stemmed frozenset)]
    CreateSummarizer --> GetParserBonus[Read parser.significant_words]
    GetParserBonus --> SetBonusWords[Set summarizer.bonus_words (stemmed frozenset)]
    CreateSummarizer --> GetParserStigma[Read parser.stigma_words]
    GetParserStigma --> SetStigmaWords[Set summarizer.stigma_words (stemmed frozenset)]
    SetNullWords --> ReturnSummarizer[Return configured summarizer]
    SetBonusWords --> ReturnSummarizer
    SetStigmaWords --> ReturnSummarizer
    LoadStopWords -->|LookupError| ErrorStopWords[Error: stop-words unavailable]
    CreateSummarizer -->|Stemmer LookupError| ErrorStemmer[Error: stemmer unavailable]
    GetParserBonus -->|AttributeError/TypeError| ErrorParser[Error: parser missing attributes or not iterable]
    ErrorStopWords --> EndError[Raise LookupError]
    ErrorStemmer --> EndError
    ErrorParser --> EndError
    ReturnSummarizer --> End[Success]

## Examples (usage in prose):
- Typical flow in an evaluation pipeline:
    1. Create a tokenizer and parser for the input text (for plaintext, use the PlaintextParser.from_string variant; for HTML, use HtmlParser.from_string or HtmlParser.from_url).
    2. Call this function with the parser instance and a language id (for example, "english").
    3. The function returns an EdmundsonSummarizer with its null_words set from the language stop-words and bonus/stigma sets populated from the parser's significant and stigma words.
    4. Use the returned summarizer to produce a summary by invoking it on the parser.document with the desired sentences_count parameter.

- Error handling guidance:
    - Catch LookupError to handle missing language resources (either stemmer or stop-words).
    - Catch AttributeError or TypeError when caller-provided parser does not expose required attributes or provides them in an unexpected form.

## `sumy.evaluation.__main__.build_lsa` · *function*

## Summary:
Constructs and returns a configured LSA summarizer instance for the given language — a LsaSummarizer that uses a language-specific stemmer and has its stop-words set.

## Description:
This function encapsulates the small, repeatable construction steps required to obtain a ready-to-use LsaSummarizer for a particular language:
- It instantiates a language-aware Stemmer and passes it into LsaSummarizer's constructor.
- It loads stop-words for the language and assigns them to the summarizer's stop_words property (which normalizes and freezes them internally).

Known callers within the codebase:
- Typical usage is from a command-line entrypoint or evaluation script that chooses a summarizer by name (for example: when the user requests the "lsa" summarizer). A direct call site was not discovered by the repository search performed during documentation generation; however, the function is defined in the evaluation CLI module and is intended for that purpose.

Why this logic is extracted:
- Keeps summarizer construction logic isolated from CLI parsing and other code paths. This enforces a single responsibility: create and configure an LsaSummarizer for a language. This makes tests, reuse, and swapping summarizers simpler and avoids duplication.

## Args:
    parser (object):
        - Type: parser-like object (e.g., PlaintextParser or HtmlParser instances found elsewhere in the project).
        - Usage: Present in the signature for API symmetry with other builder functions; not used by this function's implementation.
        - Allowed values: Any object; the function does not introspect or call methods on it.
    language (str):
        - Type: string identifying the language (language code or name). It is passed to Stemmer and get_stop_words.
        - Accepted form: any string accepted by the project's language normalization functions (e.g., "english", "en", "polish").
        - Interdependencies: The language must be supported by both the Stemmer facility and the stop-words data; otherwise the underlying constructors will raise (see Raises).

## Returns:
    LsaSummarizer instance:
        - A fully returned object of type LsaSummarizer configured to use:
            * a Stemmer constructed for the requested language (used for normalization/stemming during summarization),
            * a stop_words set populated from the language-specific stop-words resource.
        - Edge cases:
            * The returned summarizer may still fail later when invoked if required numeric libraries (NumPy) are missing — that failure occurs at summarizer-call time, not during build_lsa execution.

## Raises:
    LookupError:
        - Condition: Raised by the Stemmer constructor when there is no stemmer available for the requested language.
        - Condition: Raised by get_stop_words if packaged stop-words data for the given language is not available (get_stop_words wraps package resource access and raises LookupError when data cannot be read).
    Any exceptions propagated from package resource access:
        - Underlying pkgutil.get_data may raise IOError which get_stop_words converts into LookupError; build_lsa does not catch these, so they propagate.
    Note: build_lsa itself does not raise the LsaSummarizer dependency check error; the LsaSummarizer will raise ValueError (about NumPy) when you later call the summarizer if NumPy is missing.

## Constraints:
Preconditions:
    - The language argument should correspond to a supported language for both the Stemmer and the packaged stop-words data.
    - No other preconditions are required (parser may be any object; it is ignored).

Postconditions:
    - The returned LsaSummarizer has been instantiated with a Stemmer for the specified language.
    - summarizer.stop_words has been assigned a frozenset of normalized stop-words (the LsaSummarizer setter normalizes words before freezing).
    - No global state is modified by this function beyond creating and returning the configured summarizer.

## Side Effects:
    - Reads packaged stop-words data (package resource access via get_stop_words). This is read-only I/O into package data and may fail if the resource is absent.
    - Instantiates objects (Stemmer and LsaSummarizer) but does not mutate global variables, files, network, or external services.
    - No stdout/stderr output is produced by build_lsa itself.

## Control Flow:
flowchart TD
    Start[Start] --> CreateStemmer[Create Stemmer(language)]
    CreateStemmer -->|Stemmer ctor may raise LookupError| StemmerError[LookupError: No stemmer]
    CreateStemmer --> InstantiateSummarizer[Instantiate LsaSummarizer with Stemmer]
    InstantiateSummarizer --> FetchStopWords[Call get_stop_words(language)]
    FetchStopWords -->|pkg resource missing -> LookupError| StopWordsError[LookupError: Stop-words unavailable]
    FetchStopWords --> SetStopWords[Set summarizer.stop_words = fetched list]
    SetStopWords --> ReturnSummarizer[Return configured LsaSummarizer]
    ReturnSummarizer --> End[End]
    %% Note: LsaSummarizer call-time dependency check (NumPy) is not performed here; if NumPy missing, the summarizer will raise ValueError when invoked.

## Examples:
Typical (described steps, not executable definition):
1. A CLI or evaluation harness determines the user requested the "lsa" summarizer and parsed the language argument "english".
2. The harness calls build_lsa(parser, "english"):
   - Stemmer("english") is created and passed into LsaSummarizer.
   - get_stop_words("english") loads the English stop-words text and the summarizer's stop_words setter normalizes and freezes them.
3. The harness receives the returned LsaSummarizer instance and later calls it with a Document and a desired sentences_count. If NumPy is missing, that summarizer invocation will raise ValueError indicating NumPy is required.

Notes and implementation hints for reimplementation:
- Ensure the Stemmer constructor invoked with the language normalizes/accepts the same language forms used by the rest of the system.
- get_stop_words should raise a LookupError when the stop-words resource for the language is unavailable.
- LsaSummarizer.stop_words should accept an iterable of words; its setter should normalize each word and store them in a frozenset (this is what makes assigning safe and idempotent).
- Do not perform heavy dependency checks (like NumPy presence) in build_lsa; leave those to LsaSummarizer when the summarizer is actually invoked so errors are raised at use-time.

## `sumy.evaluation.__main__.build_text_rank` · *function*

## Summary:
Creates and returns a TextRankSummarizer instance configured with a language-specific Stemmer and stop-words.

## Description:
This function instantiates a TextRankSummarizer using a Stemmer configured for the provided language, then assigns the language's stop-words set to the summarizer and returns it.

Callers (observed in provided context):
- No direct callers are present in the provided function body or dependency snippets. The function is implemented as a builder/helper to be invoked by higher-level code that selects and configures a summarizer for a given language.

Why this logic is separated:
- Encapsulates instantiation and language-specific configuration (stemmer + stop-words) for TextRank so that summarizer construction is centralized and consistent.

## Args:
    parser:
        - Type: any (e.g., HtmlParser or PlaintextParser) or None
        - Notes: This parameter is present in the function signature but is not used by the function body. Callers may pass a parser for API symmetry with other builder functions; the value is ignored here.
    language:
        - Type: str
        - Description: Language identifier used to select the stemming implementation and the packaged stop-words file (e.g., 'english', 'en').
        - Allowed values: any language supported by the Stemmer implementation and with a corresponding stop-words file in the package data. The language value is normalized by Stemmer and get_stop_words.

## Returns:
    TextRankSummarizer
    - A configured TextRankSummarizer instance:
        * It was instantiated with Stemmer(language) as its stemmer provider.
        * Its stop_words attribute has been set to the frozenset returned by get_stop_words(language) (TextRankSummarizer.stop_words setter normalizes and freezes the set).
    - Note: This function does not execute or validate runtime dependencies required by TextRank (for example, NumPy). Any errors due to missing runtime dependencies will occur when the summarizer is called, not during build.

## Raises:
    LookupError
    - Raised by Stemmer(language) if no stemmer is available for the normalized language.
      Condition: Stemmer raises LookupError("Stemmer is not available for language %s." % language) when it cannot locate a suitable stemmer implementation.
    LookupError
    - Raised by get_stop_words(language) if the packaged stop-words resource for the normalized language cannot be read.
      Condition: get_stop_words raises LookupError("Stop-words are not available for language %s." % language) when pkgutil.get_data cannot load the stop-words file.
    (No other exceptions are raised by this function itself. Runtime errors from TextRankSummarizer (e.g., ValueError for missing NumPy) occur when the returned summarizer is invoked.)

## Constraints:
Preconditions:
- The language argument must be supported by the project's Stemmer (registered special stemmers or an NLTK stemmer class must exist) and there must be a stop-words file packaged for that normalized language name.

Postconditions:
- The returned object is a TextRankSummarizer instance with its stemmer set and stop_words assigned (a frozenset of normalized stop words).

## Side Effects:
- Reads packaged stop-words data via get_stop_words (which uses pkgutil.get_data to access package resources).
- Allocates a Stemmer instance and a TextRankSummarizer instance.
- Mutates the new summarizer instance by setting its stop_words attribute.
- No network I/O or filesystem writes are performed by this function.

## Control Flow:
flowchart TD
    Start --> CreateStemmer[Call Stemmer(language)]
    CreateStemmer -->|LookupError| ErrStemmer[Raise LookupError: stemmer not available]
    CreateStemmer --> InstantiateSummarizer[TextRankSummarizer(Stemmer)]
    InstantiateSummarizer --> FetchStopWords[get_stop_words(language)]
    FetchStopWords -->|LookupError| ErrStopWords[Raise LookupError: stop-words missing]
    FetchStopWords --> SetStopWords[Set summarizer.stop_words = stop_words]
    SetStopWords --> Return[Return configured TextRankSummarizer]
    ErrStemmer --> EndErr
    ErrStopWords --> EndErr
    Return --> EndOK

## Examples:
- Typical builder usage (outline):
    try:
        summarizer = build_text_rank(parser=None, language='english')
    except LookupError as e:
        # Handle unsupported language or missing stop-words resource
        print("Configuration error:", e)
    else:
        # Use summarizer later: summarizer(document, sentences_count)
        # Note: invoking summarizer may raise ValueError if runtime dependencies (e.g., NumPy) are missing.
        pass

## `sumy.evaluation.__main__.build_lex_rank` · *function*

## Summary:
Creates and returns a LexRank summarizer instance configured for the given language (stemmer and stop-words applied).

## Description:
This helper constructs a LexRankSummarizer and configures it with a language-specific Stemmer and stop-word list. It is defined in the evaluation CLI module and intended to be used by that module's CLI/dispatcher to instantiate a ready-to-use summarizer for LexRank when the user selects the LexRank algorithm.

Why this is a separate function:
- Encapsulates creation and configuration of the LexRank summarizer (instantiation, selection of stemmer, loading stop-words) so the CLI/dispatcher can remain concise and consistent with other build_* factory functions.
- Keeps language-specific initialization details (which may raise language-related errors) in one place rather than duplicated at call sites.

Known callers:
- Intended caller: the CLI/dispatcher code in the same module (sumy.evaluation.__main__) that selects a summarizer implementation based on user input. (The function itself is defined in that module; call sites in the repository may invoke it when LexRank is selected.)

## Args:
    parser (object):
        - Parser or parse-result object supplied by the CLI/dispatcher.
        - NOTE: This parameter is accepted to keep the build_* function signature consistent across summarizer factories. It is not used by this function.
    language (str):
        - Language identifier (e.g., 'english', 'en', 'french').
        - Will be normalized by the Stemmer and get_stop_words utilities.
        - Must be a value recognized by the Stemmer implementation and for which stop-words data exists in the package.

## Returns:
    LexRankSummarizer:
        - A LexRankSummarizer instance constructed with a Stemmer(language).
        - Its stop_words attribute is set to a frozen set of normalized stop-words for the given language.
        - The summarizer is ready to be called on a document object to produce sentence rankings.

## Raises:
    LookupError:
        - If Stemmer initialization fails because a stemmer for the requested language is not available. (Raised by Stemmer.__init__.)
    LookupError:
        - If stop-words data for the requested language cannot be found in the package data. (Raised by get_stop_words; it wraps missing-data conditions.)

    Any LookupError raised here originates from the underlying utilities (Stemmer and get_stop_words). This function does not catch these errors.

## Constraints:
Preconditions:
    - The caller should supply a language string that the project supports (or that can be normalized to a supported language).
    - The package must include stop-words files under data/stopwords/<language>.txt for the requested language.

Postconditions:
    - The returned LexRankSummarizer has:
        * its stemmer set to Stemmer(language) (used for stemming words during summarization),
        * its stop_words attribute set to a frozenset of normalized stop-words for that language.

## Side Effects:
    - Reads package data for stop-words via pkgutil.get_data (i.e., access to packaged resource files). This is file/package data I/O, not network I/O.
    - Mutates the returned summarizer object by setting its stop_words attribute.
    - No global variables or external services are modified by this function.

## Control Flow:
flowchart TD
    Start --> InstantiateStemmer[Instantiate Stemmer(language)]
    InstantiateStemmer --> CreateSummarizer[Create LexRankSummarizer(stemmer)]
    CreateSummarizer --> LoadStopWords[Call get_stop_words(language)]
    LoadStopWords --> SetStopWords[Set summarizer.stop_words]
    SetStopWords --> Return[Return summarizer]
    InstantiateStemmer -->|Stemmer raises LookupError| RaiseStemmerError[Raise LookupError]
    LoadStopWords -->|stop words missing| RaiseStopWordsError[Raise LookupError]

## Examples:
Example: create a LexRank summarizer for English and handle missing resources

    try:
        summarizer = build_lex_rank(parser=None, language='english')
    except LookupError as e:
        # Stemmer or stop-words file for the language is not available.
        # Handle by informing the user or falling back to a different language/algorithm.
        print("Cannot construct LexRank summarizer:", e)
    else:
        # `summarizer` is ready to be called with a document and sentence count:
        # summary_sentences = summarizer(document, sentences_count)
        pass

## `sumy.evaluation.__main__.build_sum_basic` · *function*

## Summary:
Constructs and returns a SumBasicSummarizer configured for the given language: the summarizer is initialized with a language-specific stemmer and its stop-word set is populated.

## Description:
This factory function creates a SumBasicSummarizer using a Stemmer for the requested language and sets the summarizer's stop_words from the language stop-words data.

Known callers:
- The evaluation/CLI construction code in this module (the command-line entrypoint that builds summarizers based on user-selected algorithm). Typically invoked when the "sum_basic" summarizer is selected from CLI options or a factory dispatch table.

Why this logic is extracted:
- It encapsulates the language-specific initialization and stop-word-loading steps for SumBasicSummarizer so CLI/factory code can construct configured summarizers via a consistent API (same signature used by other build_* factory functions). Separating this logic avoids duplication and centralizes error handling and configuration for this summarizer type.

## Args:
    parser (object):
        - Type: parser instance (e.g., HtmlParser or PlaintextParser) or any value.
        - Purpose: Present for a uniform factory signature with other build_* functions. This function does not use or mutate this argument.
        - Allowed values: any Python object; None is acceptable.
    language (str):
        - Type: language identifier (e.g., "english", "en", "czech"); passed through language-normalization used by Stemmer and get_stop_words.
        - Allowed values: any string recognized by the Stemmer and for which stop-words data exists in the package.
        - Effects: determines which stemmer implementation is used and which stop-words file is loaded.

## Returns:
    SumBasicSummarizer
    - A newly constructed SumBasicSummarizer instance that:
        * Uses a Stemmer(language) provided at construction (the summarizer will call this stemmer for per-word stemming).
        * Has its stop_words attribute set to a frozenset of normalized stop-words for the requested language (the setter normalizes each stop-word via the summarizer's normalize_word and stores them as a frozenset).
    - There is no other side channel return value; the summarizer is ready to be called for summarization tasks.

## Raises:
    LookupError:
        - Raised if a Stemmer cannot be created for the requested language (Stemmer raises LookupError when no appropriate stemmer implementation is available).
        - Raised if stop-words data for the requested language is not available (get_stop_words raises LookupError when pkgutil.get_data cannot find the stop-words file).
    Note:
        - Underlying pkgutil I/O errors are translated into LookupError by get_stop_words, so callers should catch LookupError for both missing stemmer and missing stop-words cases.
        - No other exceptions are raised explicitly by build_sum_basic itself, but other unexpected runtime errors from the Stemmer constructor or stop-words parsing may propagate.

## Constraints:
Preconditions:
    - The caller should pass a language string that is valid for both the Stemmer and the packaged stop-words.
    - The environment must have the stop-words data installed in the package (sumy/data/stopwords/<language>.txt) and, for some languages, the required NLTK stemmer available (or a special stemmer provided in the package).

Postconditions:
    - On successful return, the returned SumBasicSummarizer is configured with:
        * stemmer: the Stemmer(language) instance used by the summarizer to stem words.
        * stop_words: a frozenset of normalized stop-words for the language.
    - The function does not modify the parser argument or any global state beyond the normal package data access performed when loading stop-words.

## Side Effects:
    - I/O: get_stop_words reads the packaged stop-words data (via pkgutil.get_data). This is local package data access (no network).
    - State mutation: the returned summarizer's internal state is mutated (stop_words is set) before return.
    - No stdout/stderr, network calls, database writes, or global variable modifications are performed by this function itself.

## Control Flow:
flowchart TD
    Start --> InstantiateStemmer[Create Stemmer(language)]
    InstantiateStemmer -->|Stemmer init ok| InstantiateSummarizer[SumBasicSummarizer(stemmer)]
    InstantiateStemmer -->|Stemmer LookupError| RaiseStemmerError[Raise LookupError]
    InstantiateSummarizer --> LoadStopWords[Call get_stop_words(language)]
    LoadStopWords -->|Stop-words found| SetStopWords[Set summarizer.stop_words = stop_words]
    LoadStopWords -->|Stop-words missing| RaiseStopWordsError[Raise LookupError]
    SetStopWords --> ReturnSummarizer[Return configured summarizer]
    RaiseStemmerError --> End
    RaiseStopWordsError --> End
    End

## Examples:
1) Typical usage (happy path)
    summarizer = build_sum_basic(None, "english")
    # summarizer is a SumBasicSummarizer configured with an English Stemmer
    # and its stop_words populated; ready to be called: summary = summarizer(document, 3)

2) Handling missing stemmer or stop-words
    try:
        summarizer = build_sum_basic(None, "unknown-language")
    except LookupError as e:
        # Language not supported (no stemmer or stop-words file)
        handle_configuration_error(e)

## `sumy.evaluation.__main__.build_kl` · *function*

## Summary:
Constructs and returns a Kullback–Leibler (KL) based summarizer configured for the given language: the summarizer is initialized with a language-specific stemmer and its stop-word set.

## Description:
This small factory extracts the common construction steps required to prepare a KLSummarizer for use:
- It creates a Stemmer configured for the requested language and passes it to the KLSummarizer constructor.
- It loads the language-specific stop words and assigns them to the summarizer.stop_words attribute.

Known callers and typical usage context:
- Intended to be called by the CLI/main dispatch inside the sumy.evaluation.__main__ module (the module that parses user arguments and constructs the requested summarizer). Typical trigger: user selects the KL summarizer via command-line options or a programmatic mapping of summarizer names to builder functions.
- Kept as a separate function to centralize and standardize how KLSummarizer instances are configured (stemmer + stop words) so other code paths can reuse the same construction logic without duplication.

Responsibility boundary:
- Only creates and configures a KLSummarizer instance. It does not parse input documents, run summarization, or perform any post-construction validation beyond raising errors from underlying helpers (Stemmer and get_stop_words).

## Args:
    parser (object):
        - Type: any object (typically a parser/placeholder passed by the caller).
        - Purpose: Present for signature compatibility with other builder functions in the module. It is not used by this function and can be None.
    language (str):
        - Type: unicode/str
        - Allowed values: any language identifier accepted by Stemmer and get_stop_words (these normalize the language name internally).
        - Default: none (required positional parameter)
        - Notes: The language value is normalized internally (see Stemmer and get_stop_words). If the language is unknown to either helper, a LookupError is raised (see Raises).

## Returns:
    KLSummarizer
    - A new instance of sumy.summarizers.kl.KLSummarizer configured with:
        * an instance of Stemmer(language) passed into the constructor (used by the summarizer to normalize/stem words),
        * stop_words assigned from get_stop_words(language) (used by KLSummarizer to filter content words).
    - Edge cases:
        * The returned summarizer.stop_words will be whatever get_stop_words returns (commonly an iterable or set of words).
        * No additional wrapping or caching is performed; callers receive a fresh instance.

## Raises:
    LookupError
    - Raised by Stemmer(language) when a stemmer is not available for the requested language.
      Condition: Stemmer.__init__ fails to find or construct a stemmer for the normalized language.
    LookupError
    - Raised by get_stop_words(language) when the stop-words resource for the language cannot be loaded from package data.
      Condition: pkgutil.get_data fails to find/read the "data/stopwords/<language>.txt" resource.

(No other exceptions are explicitly raised by this function; any other runtime error would originate from the imported constructors or resource loading code called here.)

## Constraints:
Preconditions:
- The caller must pass a language identifier that the bundled Stemmer or stop-words data recognizes; otherwise, a LookupError will be raised.
- The runtime environment must have access to the package resource files (stop-words) packaged under sumy/data/stopwords/.

Postconditions:
- On successful return:
    * A KLSummarizer instance is returned whose internal stemmer will stem words using the requested language rules.
    * summarizer.stop_words is set to the stop-words loaded for the language.
- No global state is modified by this function (it only constructs and returns an object).

## Side Effects:
- Package resource access: get_stop_words uses pkgutil.get_data to read stop-words packaged with the library. This is read-only I/O of package resources.
- No network I/O, file-system writes, stdout output, or global variable mutation are performed by this function itself.
- Side effects (exceptions) are propagated from Stemmer or get_stop_words when they fail to find appropriate resources.

## Control Flow:
flowchart TD
    A[Start build_kl(parser, language)] --> B[Call Stemmer(language)]
    B -->|Stemmer created| C[Instantiate KLSummarizer(stemmer)]
    B -->|Stemmer LookupError| E[Raise LookupError -> exit]
    C --> D[Call get_stop_words(language)]
    D -->|stop words loaded| F[Assign summarizer.stop_words]
    D -->|get_stop_words LookupError| E[Raise LookupError -> exit]
    F --> G[Return configured KLSummarizer]

## Examples:
Example 1 — typical usage from a CLI dispatcher (pseudo-code):
    # Dispatcher determines user requested summarizer type 'kl' and language 'english'
    summarizer = build_kl(parser=None, language='english')
    # later: summarizer(document, sentences_count) to produce a summary

Example 2 — handling language errors:
    try:
        summarizer = build_kl(None, 'unknown-language')
    except LookupError as e:
        # Inform user that the requested language is not supported
        print("Language not supported:", e)

Notes:
- The parser argument is preserved for symmetry with other builder functions and is intentionally ignored here. Callers that pass a parser object can rely on consistent builder function signatures across different summarizer types.

## `sumy.evaluation.__main__.evaluate_cosine_similarity` · *function*

## Summary:
Compute the TF-based cosine similarity between two collections of sentences by flattening each collection into a term-frequency document model and returning their cosine similarity score.

## Description:
This function flattens the .words sequences of two sentence-collections into two token sequences, builds TfDocumentModel instances from those token sequences, and delegates the vector similarity computation to the centralized cosine_similarity routine.

Known callers within the codebase:
- Intended for evaluation workflows and CLI evaluation scripts that compare an evaluated summary (or selected sentences) to a reference summary. No direct internal callers were present in the provided sources.

Why this logic is extracted:
- Encapsulates the conversion step (sentences → TF document model) and reuse of the central cosine similarity implementation. This separation prevents duplicating TF-model construction logic and enforces a clear responsibility boundary: sentence-level aggregation vs. model-level similarity.

## Args:
    evaluated_sentences (iterable): Iterable/sequence of sentence-like objects for the evaluated text. Each sentence object must expose a .words attribute that is a sequence of token strings (tokens).
    reference_sentences (iterable): Iterable/sequence of sentence-like objects for the reference text. Same requirements as evaluated_sentences.

Interdependencies and important notes:
- The function concatenates the .words sequences from all sentences in each argument to form one document worth of tokens per side.
- Do NOT pass raw strings in place of sentence objects or in .words; a raw string is iterable by character and will be interpreted incorrectly. Each .words must be a sequence of token strings (e.g., list/tuple of tokens).
- Token normalization: TfDocumentModel lowercases tokens (using unicode.lower) and counts term frequencies. Callers should provide already-tokenized words (strings) rather than raw text.

## Returns:
    float: Cosine similarity of the two TF document vectors built from the provided sentence collections.
    - Range and interpretation: For valid non-empty TF vectors, returns a value between 0.0 and 1.0 inclusive. 0.0 indicates no overlapping terms; values closer to 1.0 indicate stronger alignment in term-frequency profiles.
    - The function never returns NaN or infinite values for valid inputs; degenerate cases raise errors (see Raises).

## Raises:
    ValueError: If TfDocumentModel construction fails for either input, for example:
        - If a sentence .words is not a sequence (TfDocumentModel enforces that words is a Sequence or string with tokenizer).
        - If a string is passed as the words argument without providing a tokenizer (TfDocumentModel requires tokenizer when words is a raw string).
    ValueError: If either resulting TfDocumentModel has zero magnitude (empty document). The underlying cosine_similarity raises:
        "Document model can't be empty. Given <evaluated_model> & <reference_model>"
    ValueError: If cosine_similarity's type check fails (if the models passed are not TfModel instances), with message:
        "Arguments has to be instances of 'sumy.models.TfDocumentModel'"
    Note: The function itself performs no additional validation — ValueError messages may originate from TfDocumentModel or cosine_similarity and are propagated unchanged.

## Constraints:
Preconditions:
- Each element of evaluated_sentences and reference_sentences must have a .words attribute that is a non-empty sequence of token strings.
- At least one token must be present in each combined document (i.e., evaluated_sentences combined and reference_sentences combined) to avoid the empty-document error.

Postconditions:
- On success, returns a float cosine similarity; inputs are not modified.

## Side Effects:
- None. All computation is in-memory:
    - No file, network, or stdout/stderr I/O.
    - No mutation of global state or of the input sentence objects.
    - No external service calls.

## Control Flow:
flowchart TD
    A[Start: receive evaluated_sentences, reference_sentences]
    A --> B{Inputs iterable of sentence-like objects with .words?}
    B -->|No| E[Error during TfDocumentModel construction -> ValueError]
    B -->|Yes| C[Flatten .words from evaluated_sentences -> evaluated_words]
    C --> D[Flatten .words from reference_sentences -> reference_words]
    D --> F[Construct TfDocumentModel(evaluated_words)]
    F --> G[Construct TfDocumentModel(reference_words)]
    G --> H[Call cosine_similarity(evaluated_model, reference_model)]
    H --> I{cosine_similarity checks types and magnitude}
    I -->|type check fail| J[Raise ValueError about TfDocumentModel instances]
    I -->|denominator == 0.0| K[Raise ValueError("Document model can't be empty...")]
    I -->|ok| L[Return float numerator/denominator]
    L --> M[End]

## Examples (realistic numeric example described in prose):
- Given two simple sentence collections:
    * evaluated_sentences contains one sentence whose .words = ['A', 'B', 'A']
    * reference_sentences contains one sentence whose .words = ['A', 'C']
  TfDocumentModel behavior (lowercasing and counting) produces:
    * evaluated model term counts: {'a': 2, 'b': 1}
    * reference model term counts: {'a': 1, 'c': 1}
  Cosine similarity computation:
    * numerator = evaluated.term_frequency('a') * reference.term_frequency('a') = 2 * 1 = 2
    * evaluated magnitude = sqrt(2^2 + 1^2) = sqrt(5)
    * reference magnitude = sqrt(1^2 + 1^2) = sqrt(2)
    * cosine = 2 / (sqrt(5) * sqrt(2)) = 2 / sqrt(10) ≈ 0.6324555
  This example shows how token multiplicity affects similarity: shared repeated tokens increase the numerator and the evaluated magnitude.

- Error-handling guidance:
    * Validate before calling: ensure each .words is a non-empty sequence of token strings and that each document (collection) contains at least one token. If empty documents are possible in your pipeline, catch ValueError around the call and handle it (skip, supply a default, or report).

## `sumy.evaluation.__main__.evaluate_unit_overlap` · *function*

## Summary:
Compute a case-insensitive term-overlap similarity (a Jaccard-like score in [0.0, 1.0]) between two sets of sentences by flattening their token sequences, building term-frequency document models, and delegating the numeric similarity calculation to the model-level unit overlap routine.

## Description:
This function converts two iterables of sentence-like objects into TfDocumentModel instances and returns the unit overlap similarity between them.

- It flattens tokens by reading the .words attribute from each sentence-like object in evaluated_sentences and reference_sentences and concatenating those token sequences.
- It constructs TfDocumentModel instances from the flattened token tuples.
- It calls unit_overlap(evaluated_model, reference_model) to compute the similarity; that function performs validation (including an empty-document check) and computes the overlap score.

Known callers within the repository:
- Defined in the evaluation CLI module. No other direct callers were found in the codebase snapshot; it is intended for evaluation pipelines or CLI commands that compare generated summaries (evaluated_sentences) to reference summaries.

Why separated:
- Separation of concerns: this function handles the "sentence list → TfDocumentModel" conversion while unit_overlap implements the pure model-to-model metric. This keeps token extraction, model construction, and the metric distinct for reuse and simpler testing.

## Args:
    evaluated_sentences (iterable): Iterable of sentence-like objects for the evaluated summary. Each element must have a .words attribute that is itself an iterable/sequence of token strings (e.g., list or tuple of str). Generators or other lazy iterables are accepted but will be fully consumed.
    reference_sentences (iterable): Iterable of sentence-like objects for the reference summary, same requirements as evaluated_sentences.

Notes:
- The function does not accept raw strings as top-level arguments for sentences; each sentence object must expose .words. If you start with raw text, tokenize it into sentence-like objects where .words is a sequence of tokens.
- If an element's .words is a string (e.g., "hello world"), it will be treated as a sequence of characters and flattened character-by-character (not automatically tokenized into words). To avoid this, ensure .words is a sequence of tokens (["hello", "world"]) rather than a single string.
- Token comparison is case-insensitive: TfDocumentModel lowercases terms internally before counting, so 'Cat' and 'cat' are treated as the same term.

## Returns:
float
- A similarity score in the interval [0.0, 1.0], computed as:
  common_terms_count / (len(terms1) + len(terms2) - common_terms_count)
  where terms1 and terms2 are the distinct lowercase terms from evaluated_sentences and reference_sentences respectively.
- Return semantics:
  - 1.0 indicates identical sets of distinct terms (after lowercasing).
  - 0.0 indicates no shared terms.
  - If one document has zero distinct terms and the other has >0, the result is 0.0.
  - If both documents have zero distinct terms, unit_overlap raises ValueError (see Raises).

## Raises:
ValueError:
- Propagated from unit_overlap when both documents contain no terms: "Documents can't be empty. Please pass the valid documents."
- Propagated from unit_overlap if arguments are not the expected TfModel instances (should not occur because this function constructs TfDocumentModel instances).

AttributeError:
- If any element in evaluated_sentences or reference_sentences lacks a .words attribute, attempting to access s.words will raise AttributeError.

TypeError:
- If evaluated_sentences or reference_sentences is not iterable, the generator expression that extracts s.words will raise TypeError (object is not iterable).

Other exceptions:
- TfDocumentModel.__init__ may raise ValueError in its own admission if provided with a non-sequence/non-string words parameter. Because this function passes a tuple of tokens to TfDocumentModel, that ValueError should not be triggered under normal circumstances unless tokens flattening yields a non-sequence type.

## Constraints:
Preconditions:
- Each sentence-like object must expose .words and .words must be an iterable of token strings (preferably a sequence like list/tuple).
- The function assumes tokens are already produced by a tokenizer; it will not split raw text into tokens.

Postconditions:
- On success, returns a float similarity and does not mutate input sentence objects or global state.

## Side Effects:
- None: no file or network I/O, no global state mutation. Only local objects (TfDocumentModel instances) are created and discarded.

## Control Flow:
flowchart TD
    Start([Start])
    ValidateInputs{evaluated_sentences & reference_sentences iterable?}
    ExtractEvalWords[Flatten s.words for each s in evaluated_sentences -> evaluated_words tuple]
    ExtractRefWords[Flatten s.words for each s in reference_sentences -> reference_words tuple]
    BuildEvalModel[Create TfDocumentModel(evaluated_words)]
    BuildRefModel[Create TfDocumentModel(reference_words)]
    CallUnitOverlap[Call unit_overlap(evaluated_model, reference_model)]
    ReturnResult[/Return float similarity/]
    AttrError((AttributeError if s lacks .words))
    TypeError((TypeError if inputs not iterable))
    ValueErrorEmpty((ValueError if both documents empty) )

    Start --> ValidateInputs
    ValidateInputs -->|not iterable| TypeError
    ValidateInputs -->|iterable| ExtractEvalWords --> ExtractRefWords
    ExtractEvalWords -->|missing .words| AttrError
    ExtractRefWords -->|missing .words| AttrError
    ExtractEvalWords --> BuildEvalModel --> BuildRefModel --> CallUnitOverlap --> ReturnResult
    CallUnitOverlap -->|both empty| ValueErrorEmpty

## Examples:
1) Basic usage with simple sentence-like objects
- Construct sentence-like objects where each has a .words sequence:
  evaluated_sentences = [Sentence(words=("the", "cat"))]
  reference_sentences = [Sentence(words=("cat",))]
- Call evaluate_unit_overlap(evaluated_sentences, reference_sentences)
- Result: 0.5 (terms {'the','cat'} vs {'cat'}, common=1, union=2 → 1/2 = 0.5)

2) Disjoint token sets
- evaluated_sentences tokens = {'a','b'}, reference_sentences tokens = {'x','y'}
- Result: 0.0

3) Both empty → error
- If both evaluated_sentences and reference_sentences flatten to no tokens (every .words empty), calling this function raises ValueError from unit_overlap stating documents cannot be empty.

Usage guidance:
- Ensure you pass sequences of tokens for .words (not raw strings). If you only have raw text, run a tokenizer and build sentence-like objects with .words before calling this function.

## `sumy.evaluation.__main__.main` · *function*

## Summary:
Run the evaluation CLI entry point: parse command-line arguments, build a summarizer and documents, execute available evaluation metrics, print each metric's float result to stdout, and return process exit code 0.

## Description:
This function is the command-line entry point for the evaluation subcommand/module. It performs three high-level responsibilities:
1. Parse CLI arguments using docopt and the module's __doc__ and __version__.
2. Prepare the summarizer, input document, item count, and reference summary via handle_arguments.
3. Produce an evaluated summary from the summarizer, construct the reference sentences, run each configured evaluation function, print results, and exit.

Known callers within a typical codebase / invocation contexts:
- Invoked directly when the package/module is executed as a script (python -m sumy.evaluation) or via an installed console script that calls this entry point.
- Not intended to be called as a library function for programmatic evaluation; it is a top-level CLI handler.

Why this logic is isolated:
- CLI parsing, argument validation and the orchestration of summarization + metric invocation is a cross-cutting concern that ties several components (argument parsing, summarizers, parsers, evaluation functions). Extracting it into main enforces a clear boundary between interactive/CLI behavior and the core summarization/evaluation logic so the latter can be reused programmatically without CLI side effects.

## Args:
    args (list[str] | None): Optional list of strings representing CLI arguments (as sys.argv[1:]).
        - If None (the default), docopt reads arguments from sys.argv.
        - The function forwards these to docopt(to_string(__doc__), args, version=__version__) to produce a mapping of options and flags.
        - Typical values: None (use process args) or a list like ["--language", "english", "INPUT_FILE"] for testing.

## Returns:
    int: Process exit code. The function always returns 0 on normal completion (after printing all evaluation metric results).
    - There are no alternative return values in the implementation; exceptional conditions raise exceptions instead of returning non-zero.

## Raises:
    SystemExit: Raised by docopt if the parsed arguments are invalid or if --help/--version triggers a docopt exit path. This is the primary immediate exception coming from argument parsing.
    Any exceptions propagated from handle_arguments: handle_arguments is called to construct the summarizer and input documents; if it raises (e.g., due to missing input, I/O error when fetching URL, or invalid parameter combinations), those exceptions propagate up unchanged.
    Any exceptions from the summarizer or evaluation functions: When summarizer(document, items_count) or evaluate(...) is executed, any runtime exceptions raised by those components propagate out of main and terminate the function unless caught elsewhere (the function does not catch them).

## Constraints:
Preconditions:
    - The module-level variables referenced by docopt must be defined: __doc__ must contain a valid docopt usage string and __version__ must be present for the version argument to work.
    - handle_arguments(...) must exist and return a 4-tuple of (summarizer, document, items_count, reference_summary) with expected types:
        - summarizer: callable(document, items_count) -> list-like evaluated sentences
        - document: object exposing .sentences (iterable of sentence objects)
        - items_count: ItemsCount-like object or integer accepted by summarizer
        - reference_summary: str containing the reference summary text (plaintext)
    - AVAILABLE_EVALUATIONS must be an iterable of tuples (name, evaluate_document, evaluate_fn) where:
        - name: str label for the metric
        - evaluate_document: bool; if True the metric expects to compare evaluated_sentences against the source document's sentences; if False compare to reference_sentences
        - evaluate_fn: callable(evaluated_sentences, target_sentences) -> float
Postconditions:
    - All configured evaluations are attempted sequentially and each metric's numeric result is printed as a single line "name: <float>" on stdout.
    - The function returns integer 0 on successful completion (unless an exception interrupts execution).

## Side Effects:
    - Stdout: prints one line per configured evaluation metric in AVAILABLE_EVALUATIONS in the format "%s: %f" where %s is the metric name and %f is the floating-point result (default formatting from %f).
    - No files or network I/O are performed directly by main, but handle_arguments or the summarizer may perform I/O (fetching URLs, reading files) — such effects are delegated and may occur indirectly.
    - No global state is mutated by this function itself beyond any side effects invoked by called components.
    - Exits are not performed within main; it returns 0. If docopt triggers usage/help, a SystemExit may terminate the process before main returns.

## Control Flow:
flowchart TD
    A[start main(args)] --> B[call docopt(to_string(__doc__), args, version=__version__)]
    B --> C[call handle_arguments(args) => summarizer, document, items_count, reference_summary]
    C --> D[call summarizer(document, items_count) => evaluated_sentences]
    D --> E[PlaintextParser.from_string(reference_summary, Tokenizer(args["--language"])) => reference_document]
    E --> F[reference_sentences = reference_document.document.sentences]
    F --> G{iterate AVAILABLE_EVALUATIONS}
    G -->|for each (name, evaluate_document, evaluate_fn)| H{evaluate_document?}
    H -->|True| I[result = evaluate_fn(evaluated_sentences, document.sentences)]
    H -->|False| J[result = evaluate_fn(evaluated_sentences, reference_sentences)]
    I --> K[print "name: %f" % result]
    J --> K
    K --> G
    G --> L[return 0]
    B -.-> M[docopt raises SystemExit] --> M[exit with SystemExit]

## Examples:
Example 1 — run with programmatic argument list (useful in tests):
    try:
        ret = main(["--language", "english", "input.txt", "--some-other-flag"])
    except SystemExit as e:
        # docopt may raise SystemExit for invalid args or help/version requests
        handle_docopt_exit(e)
    else:
        assert ret == 0  # normal completion; evaluation results have been printed

Example 2 — typical CLI run (shell):
    $ python -m sumy.evaluation --language english input.txt
    # Output lines printed to stdout:
    # ROUGE-1: 0.451234
    # BLEU: 0.123456
    # ...

Notes and implementation hints:
    - main delegates parsing of inputs and construction of the summarizer and documents to handle_arguments; ensure handle_arguments returns the specified tuple with types compatible with the downstream calls.
    - The function assumes evaluated_sentences and reference/document sentences are in the format expected by evaluation functions (commonly sequences of sentence objects or plain strings). Evaluation functions are responsible for converting or validating sentence representations.
    - Keep main lightweight: avoid catching broad exceptions here so that failures in data preparation or evaluation fail loudly and produce stack traces for debugging.

## `sumy.evaluation.__main__.handle_arguments` · *function*

*No documentation generated.*

