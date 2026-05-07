# `tokenizers.py`

## `sumy.nlp.tokenizers.DefaultWordTokenizer` · *class*

## Summary:
A minimal, stateless word tokenizer that delegates tokenization to NLTK's word_tokenize function.

## Description:
DefaultWordTokenizer exists to provide a simple, pluggable tokenizer object within the tokenizers module that performs word-level tokenization by calling nltk.word_tokenize. Instantiate this class when you need a tokenizer object that conforms to the project's tokenizer interface (i.e., exposes a tokenize(text) method) but do not require language-specific or heuristic tokenization beyond what NLTK provides.

Known callers/factories:
- Any component in the codebase that expects a tokenizer instance with a tokenize(text) method may instantiate DefaultWordTokenizer. (Search the codebase for places that construct tokenizers to find explicit callers.)

Motivation and responsibility boundary:
- Responsibility: expose a tokenize(text) method and delegate all tokenization work to the external nltk.word_tokenize function.
- Boundary: This class does not implement tokenization logic itself, does not hold configuration or language state, and does not attempt to manage or verify NLTK resources (e.g., tokenizer models). Those responsibilities remain with callers or external setup code.

## State:
- Attributes: This class defines no instance attributes (no __init__ override). Instances are effectively stateless wrappers.
- Valid values:
    - There are no per-instance state values to constrain.
- Invariants:
    - For any instance `t` of DefaultWordTokenizer, calling `t.tokenize(text)` will always forward the same input `text` to `nltk.word_tokenize` and return the exact result produced by that call (modulo any side effects of NLTK).
    - No method mutates instance state because there is none.

## Lifecycle:
- Creation:
    - How to instantiate: call DefaultWordTokenizer() with no arguments.
    - There are no required constructor parameters or factory methods.
- Usage:
    - Primary method: tokenize(text)
    - Expected call pattern: create an instance once (or per-use) and call `tokenize` whenever tokenization is needed.
    - There is no required ordering between method calls because there is only one public method and the class is stateless.
- Destruction:
    - No explicit cleanup is required. The class does not hold external resources, file handles, or threads. Instances can be garbage-collected normally.

## Method Map:
flowchart LR
    A[Caller] --> B[DefaultWordTokenizer.tokenize(text)]
    B --> C[nltk.word_tokenize(text)]
    C --> D[list of token strings]
    D --> A

## Component: tokenize(text)
- Purpose:
    - Accept a text string and return a list of word tokens as produced by NLTK's word_tokenize.
- Inputs:
    - text (str or unicode): the text to tokenize. Callers should supply a text string; non-string inputs are forwarded to nltk.word_tokenize and may produce errors.
- Outputs:
    - list[str]: the token list returned by nltk.word_tokenize for the given input.
- Behavior details:
    - The method delegates entirely to nltk.word_tokenize and returns whatever that function returns for the provided input.
    - The function performs no additional normalization, filtering, or post-processing on tokens.
    - Language handling, model/resource availability, and tokenization conventions are determined by NLTK's configuration and installed data (e.g., tokenizer models); this class does not alter or check those settings.
- Edge cases and constraints:
    - If the caller passes None or a non-string object, behavior depends on nltk.word_tokenize and may raise an exception; callers should pass valid strings.
    - If required NLTK data (tokenizer models) are not available, nltk.word_tokenize may raise an error; those errors propagate unchanged.
    - Thread-safety: the instance itself holds no state; thread-safety depends on underlying NLTK usage and any global NLTK state.

## Raises:
- This class does not explicitly raise exceptions. Exceptions raised by nltk.word_tokenize (for example, due to invalid input types or missing NLTK resources) are propagated to the caller.

## Example:
Instantiate and use the DefaultWordTokenizer; handle exceptions from the underlying NLTK call as needed.

    tokenizer = DefaultWordTokenizer()
    text = "This is a sentence, with punctuation."
    tokens = tokenizer.tokenize(text)
    # tokens is the list returned by nltk.word_tokenize for the input text

### `sumy.nlp.tokenizers.DefaultWordTokenizer.tokenize` · *method*

## Summary:
Tokenizes a text string into a list of word tokens using NLTK's word-level tokenizer; it does not modify object state.

## Description:
This method delegates tokenization to nltk.word_tokenize and returns the resulting list of tokens. It exists so different tokenizer implementations (for different languages or tokenization strategies) can present a consistent tokenize(text) interface and be swapped by higher-level components without changing call sites.

Known callers:
- No specific callers were found in the inspected source for this method. Typically it is invoked by higher-level NLP pipeline stages that require word-level tokens (for example: sentence-splitting -> word-tokenization steps, summarizers, feature extraction modules, or any component that accepts a Tokenizer-like object and calls its tokenize method).

Lifecycle / pipeline stage:
- Invoked during the tokenization stage of text preprocessing, after text normalization and before tasks that consume token lists (POS tagging, parsing, vectorization, etc.).

Why this is a separate method:
- Encapsulates the choice of NLTK tokenization in one place so other modules depend on the abstract tokenizer API rather than a concrete implementation. This simplifies swapping to a different tokenizer (e.g., language-specific tokenizers) or mocking in tests.

## Args:
    text (str or unicode): Input text to tokenize. Must be a text/string type. Passing non-string objects may raise TypeError from underlying NLTK routines.

## Returns:
    list[str]: A list of word tokens (each token is a str/unicode). For empty input string, an empty list is returned.

## Raises:
    TypeError: If a non-string object is passed and nltk.word_tokenize cannot handle it (e.g., None or a numeric type).
    LookupError: If required NLTK resources (such as the 'punkt' tokenizer models) are not installed, nltk.word_tokenize may raise a LookupError describing the missing resource.
    Any exceptions raised by nltk.word_tokenize (propagated unchanged).

## State Changes:
Attributes READ:
    - None (does not access or read any self.<attr> attributes)

Attributes WRITTEN:
    - None (does not modify any self.<attr> attributes)

## Constraints:
Preconditions:
    - The caller should provide a text-like object (str/unicode). It is the caller's responsibility to ensure the text is in the desired normalized form (encoding, lowercasing, language-specific normalization) before calling this method.

Postconditions:
    - Returns a list of strings representing word tokens extracted from the input.
    - The tokenizer does not change the state of the DefaultWordTokenizer instance.

## Side Effects:
    - No I/O or external network calls are performed directly by this method. It may trigger NLTK resource lookups which will raise exceptions if required corpora/models are missing, but it does not download resources by itself.
    - No mutation of arguments or global state occurs.

## `sumy.nlp.tokenizers.HebrewWordTokenizer` · *class*

## Summary:
A minimal tokenizer class that extracts Hebrew words from an input string by delegating to the external hebrew_tokenizer library and removing ASCII punctuation beforehand.

## Description:
This class provides a single, focused responsibility: take an input string, remove ASCII punctuation (string.punctuation), run the hebrew_tokenizer.tokenize function, and return only the tokens classified as Hebrew by hebrew_tokenizer.groups.Groups. It exists to centralize the small pre-processing (punctuation removal) and the filtering logic so callers can obtain a list of Hebrew-word strings without depending directly on the Groups constants or handling punctuation removal themselves.

Typical call sites:
- Any summarizer, NLP pipeline, or preprocessing step that needs a list of Hebrew words from raw text.
- Callers can invoke the classmethod directly: HebrewWordTokenizer.tokenize(text). There is no need to instantiate the class.

Motivation and boundaries:
- Motivation: provide a simple, tested wrapper over hebrew_tokenizer that strips ASCII punctuation and restricts tokens to Hebrew groups.
- Boundary: This class does not perform normalization (e.g., removing vowels, normalizing final forms), lemmatization, splitting on whitespace beyond what hebrew_tokenizer does, or language detection. It only removes ASCII punctuation and filters token groups.

## State:
- _TRANSLATOR (dict): class-level attribute produced by str.maketrans("", "", string.punctuation).
  - Type: dict (translation table suitable for str.translate)
  - Purpose: maps ASCII punctuation characters (string.punctuation) to None so they are removed when text.translate is called.
  - Invariant: _TRANSLATOR must be a valid translation table produced by str.maketrans; it is immutable after class definition.

There are no instance attributes — all behavior is provided via the classmethod. No external state is cached.

## Lifecycle:
- Creation:
  - No instantiation required. Use the tokenizer by calling the classmethod:
    - HebrewWordTokenizer.tokenize(text)
  - There are no constructor parameters.

- Usage:
  - Input: a text value expected to be a Python string (str/unicode).
  - Processing steps:
    1. The method attempts to import hebrew_tokenizer.tokenize and hebrew_tokenizer.groups.Groups at call time.
    2. It removes ASCII punctuation by applying text.translate(_TRANSLATOR).
    3. It calls hebrew_tokenizer.tokenize on the cleaned text, iterates the returned tuples, and collects the 'word' element for tuples whose token group is one of Groups.HEBREW, Groups.HEBREW_1, or Groups.HEBREW_2.
  - Ordering / sequencing: Single-step call; no required sequencing of multiple method calls.

- Destruction:
  - No cleanup required. The class does not open files, hold network connections, or maintain external resources.

## Method Map:
graph LR
    A[Caller] --> B[HebrewWordTokenizer.tokenize(text)]
    B --> C[import hebrew_tokenizer.tokenize]
    B --> D[import hebrew_tokenizer.groups.Groups]
    B --> E[text.translate(_TRANSLATOR) remove ASCII punctuation]
    B --> F[hebrew_tokenizer.tokenize(cleaned_text) -> iterator of (token, word, start, end)]
    F --> G[Filter tokens where token in (Groups.HEBREW, Groups.HEBREW_1, Groups.HEBREW_2)]
    G --> H[Return list of word strings]

## Behavior (inputs, outputs, edge cases, constraints):
- Inputs:
  - text (str): required. The method expects a Python string. If a non-string without a translate method is provided, an AttributeError will likely be raised by the call to text.translate.
- Outputs:
  - list[str]: A list of word strings extracted from the input, consisting only of words classified as Hebrew by hebrew_tokenizer Groups constants. ASCII punctuation (string.punctuation) from the original text is removed prior to tokenization.
- Filtering:
  - Only tokens whose token value equals Groups.HEBREW, Groups.HEBREW_1, or Groups.HEBREW_2 are kept; all other token groups are discarded.
- Constraints:
  - The method dynamically imports hebrew_tokenizer. If the package is not installed, the method raises a ValueError describing how to install it (see Raises).
  - The tokenizer does not perform additional normalization beyond punctuation removal. If callers require Unicode normalization or Hebrew-specific normalization, they must perform it before or after calling this method.

## Raises:
- ValueError: raised explicitly when the hebrew_tokenizer dependency is not importable. The message instructs the user to install the package via "pip install hebrew_tokenizer".
- AttributeError / TypeError: may be raised implicitly if the provided text is not a string (e.g., None or an object without a translate method); this occurs because the code calls text.translate(...) without type coercion.
- Any exceptions raised by hebrew_tokenizer.tokenize itself will propagate to the caller (e.g., if the external library raises on malformed input).

## Example:
- Typical usage (no instantiation required):
  Call the tokenizer directly with a Unicode string containing Hebrew text; ASCII punctuation will be removed and only Hebrew words returned.
  Example invocation:
    tokens = HebrewWordTokenizer.tokenize("שלום, עולם! This part is English.")
  Expected behavior:
    - ASCII punctuation characters ',' and '!' are removed before tokenization.
    - The returned list contains only the Hebrew words (e.g., ["שלום", "עולם"]) and excludes non-Hebrew tokens.

### `sumy.nlp.tokenizers.HebrewWordTokenizer.tokenize` · *method*

## Summary:
Performs word-level tokenization for Hebrew text and returns a list of Hebrew words; reads the class-level punctuation translator but does not modify object state.

## Description:
This classmethod delegates actual token splitting to the external hebrew_tokenizer package, then filters and returns only tokens classified as Hebrew by hebrew_tokenizer.groups.Groups. It is intended to be invoked during the word-tokenization stage of a language processing pipeline whenever Hebrew word tokens are required (for example: when a tokenizer/normalizer selects a language-specific word tokenizer before feature extraction or summarization). The logic is isolated in its own method because it relies on an optional external dependency (hebrew_tokenizer) and on language-specific filtering rules; keeping it separate avoids inlining third-party import handling and keeps other tokenizers free of Hebrew-specific behavior.

## Args:
    text (str): Input text to tokenize. Must be a Python string (unicode). The method calls str.translate on this value, so it must support that operation.

## Returns:
    list[str]: A list of word strings returned by hebrew_tokenizer.tokenize(text) for which the token group is one of Groups.HEBREW, Groups.HEBREW_1, or Groups.HEBREW_2.
    - Empty list when input contains no matching Hebrew tokens (including when text is empty or when all tokens are filtered out).
    - Words are returned exactly as produced by the hebrew_tokenizer.tokenize function (after the ASCII punctuation removal performed by the translator).

## Raises:
    ValueError: If the optional dependency hebrew_tokenizer is not installed. The method raises this exact ValueError with the message:
        "Hebrew tokenizer requires hebrew_tokenizer. Please, install it by command 'pip install hebrew_tokenizer'."
    Any exception raised by hebrew_tokenizer.tokenize (or by str.translate if text is an unsupported type) is not caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        self._TRANSLATOR (accessed as cls._TRANSLATOR): used to remove ASCII punctuation from the input via text.translate.
    Attributes WRITTEN:
        None — this method does not modify class or instance attributes.

## Constraints:
    Preconditions:
        - hebrew_tokenizer must be importable; otherwise a ValueError is raised.
        - text must be a str (or an object exposing str.translate); passing None or a non-string that lacks translate will raise an exception (propagated).
    Postconditions:
        - The returned list contains only word strings whose corresponding token group is one of Groups.HEBREW, Groups.HEBREW_1, or Groups.HEBREW_2 as determined by hebrew_tokenizer.
        - The input text has effectively been processed with the class translator that removes ASCII punctuation before tokenization (no persistent change to the input argument itself).

## Side Effects:
    - Imports the hebrew_tokenizer package at call time; this may trigger module import-time side effects of that package.
    - No I/O is performed by this method itself.
    - No mutation of objects outside of local variables and read-only access to cls._TRANSLATOR.

## `sumy.nlp.tokenizers.JapaneseWordTokenizer` · *class*

## Summary:
Provides Japanese word/token segmentation by delegating to the tinysegmenter library; exposes a single tokenize(text) method as a lightweight adapter.

## Description:
This class is a minimal adapter around tinysegmenter.TinySegmenter.tokenize. It exists to provide a consistent tokenizer interface for components that expect a tokenizer object with a tokenize(text) method. Instantiate this class when you need simple, per-call word segmentation of Japanese text in pipelines such as token-based preprocessing, indexing, or extractive summarization.

Known callers/factories:
- Any pipeline or component that expects a tokenizer object implementing tokenize(text). No explicit factory exists in this module; callers create JapaneseWordTokenizer() directly.

Responsibility boundary:
- The class is responsible only for delegating tokenization to tinysegmenter and mapping an ImportError into a clearer ValueError. It does not perform language normalization, sentence splitting, POS tagging, or caching of the underlying segmenter instance.

## State:
- Attributes:
    - This class defines no persistent or public instance attributes; it is effectively stateless.
- __init__ parameters:
    - None. Use the default constructor with no arguments.
- Valid input:
    - text: expected to be a text string (str/unicode). The method forwards this value directly to tinysegmenter.TinySegmenter.tokenize.
- Return value:
    - A sequence (as produced by tinysegmenter) of token strings; the exact container type and token encoding depend on tinysegmenter. The method returns whatever tinysegmenter.TinySegmenter.tokenize(text) returns.
- Class invariants:
    - No invariants are required or maintained by this class—each tokenize call is independent and creates its own segmenter instance.

## Lifecycle:
- Creation:
    - Instantiate with no arguments: create a JapaneseWordTokenizer object using the default constructor.
- Usage:
    - Call tokenize(text) one or more times in any order. Each call will:
        1. Attempt to import the tinysegmenter module.
        2. Construct a new tinysegmenter.TinySegmenter() instance.
        3. Call that instance's tokenize(text) and return the result.
    - There is no required sequencing between calls.
- Performance considerations:
    - Because tokenize constructs a new TinySegmenter on every call, repeated high-frequency tokenization may pay a runtime cost from repeated construction and import checks. For high-throughput scenarios, consider constructing tinysegmenter.TinySegmenter() once (using tinysegmenter directly) and calling its tokenize method repeatedly to avoid repeated allocation/import overhead.
- Destruction / Cleanup:
    - No special cleanup is necessary. The class does not retain external resources or file handles.

## Method Map:
flowchart LR
    A[JapaneseWordTokenizer instance] --> B[tokenize(text)]
    B --> C{import tinysegmenter}
    C -->|success| D[TinySegmenter() created]
    D --> E[call TinySegmenter.tokenize(text)]
    E --> F[return tokens to caller]
    C -->|ImportError| G[raise ValueError("Japanese tokenizer requires tinysegmenter...")]

## Raises:
- ValueError:
    - Raised when the tinysegmenter module cannot be imported. Message: "Japanese tokenizer requires tinysegmenter. Please, install it by command 'pip install tinysegmenter'."
    - This behavior is implemented by catching ImportError during the internal import and translating it to ValueError.
- Propagated exceptions from tinysegmenter:
    - Any exceptions raised during construction of tinysegmenter.TinySegmenter() or its tokenize(text) method are not caught by this class and will propagate to the caller unchanged.
- Input-related errors:
    - The method does not validate the type or contents of text. Passing non-text inputs (for example, None or bytes in certain Python versions) may cause exceptions raised by tinysegmenter (such as TypeError) — those exceptions will propagate.

## Example (prose):
- Typical use: create an instance with the default constructor, then call tokenize with a Japanese text string. The return will be the token sequence produced by tinysegmenter.TinySegmenter.tokenize for that string.
- Performance note: for many repeated tokenization calls, prefer creating tinysegmenter.TinySegmenter directly and reusing it to avoid repeated allocation and import overhead.

### `sumy.nlp.tokenizers.JapaneseWordTokenizer.tokenize` · *method*

## Summary:
Delegates Japanese word tokenization to the TinySegmenter library by performing a runtime import, instantiating TinySegmenter, and returning whatever result TinySegmenter.tokenize produces; does not modify the tokenizer instance.

## Description:
This method implements Japanese tokenization by importing tinysegmenter inside the method (so the dependency is optional), creating a tinysegmenter.TinySegmenter instance, and invoking its tokenize method on the provided text. The method centralizes dependency handling and the direct invocation of the external tokenizer so callers or higher-level tokenization orchestration do not need to manage the import or error messaging.

Known callers and context:
- Intended to be called by higher-level tokenization or language-dispatching components in an NLP pipeline when Japanese word tokenization is required. Specific callers are outside this file and are not defined here.
- Typically used as the leaf implementation for the word-tokenization step after any sentence-splitting stage.

Why this is a separate method:
- Keeps optional dependency handling (ImportError -> ValueError with a user-friendly message) localized.
- Encapsulates language-specific invocation of an external tokenizer so the rest of the codebase can remain dependency-agnostic.

## Args:
    text (any): Passed directly to tinysegmenter.TinySegmenter.tokenize. The method performs no type checking or normalization itself; valid types and accepted values are determined by tinysegmenter.

## Returns:
    Any: Exactly the value returned by tinysegmenter.TinySegmenter.tokenize(text). Callers should consult tinysegmenter documentation for the concrete return type and semantics.

## Raises:
    ValueError: If the tinysegmenter module cannot be imported. The exact message raised is:
        "Japanese tokenizer requires tinysegmenter. Please, install it by command 'pip install tinysegmenter'."
    Any exception raised by tinysegmenter.TinySegmenter() or tinysegmenter.TinySegmenter.tokenize(text) is propagated unchanged.

## State Changes:
    Attributes READ:
        - None. The method does not access any self.<attr> attributes.
    Attributes WRITTEN:
        - None. The method does not modify self or any external object attributes.

## Constraints:
    Preconditions:
        - tinysegmenter must be available in the runtime environment to avoid a ValueError.
        - The caller should pass a value acceptable to tinysegmenter.TinySegmenter.tokenize; this method does not validate or coerce the input.

    Postconditions:
        - On success, the return value equals the direct result of TinySegmenter.tokenize(text).
        - No instance-level or module-level state is changed by this call.

## Side Effects:
    - Performs a runtime import of the tinysegmenter module.
    - Instantiates tinysegmenter.TinySegmenter (in-memory object).
    - No file or network I/O is performed by this method itself beyond Python's import mechanism.
    - No mutation of arguments or global program state beyond the usual effects of importing a module and creating an object.

## `sumy.nlp.tokenizers.ChineseWordTokenizer` · *class*

## Summary:
A tiny adapter-style tokenizer that delegates Chinese word segmentation to the optional third-party jieba library and returns the iterable of tokens produced by jieba.cut.

## Description:
ChineseWordTokenizer exists to provide a pluggable, language-specific tokenizer that centralizes optional-dependency handling for Chinese segmentation. It should be instantiated when a processing pipeline needs a tokenizer object for Chinese text; higher-level code typically chooses this class when the document language is detected as Chinese and then calls its tokenize method to obtain word tokens.

Motivation and responsibility boundary:
- Keeps the dynamic import and error message for jieba in one place so the rest of the codebase does not need to know about jieba.
- Acts purely as an adapter: it does not implement tokenization logic itself, it forwards the input to jieba.cut and returns that result.
- It does not persist state, manage resources, or perform language detection — those responsibilities belong to other parts of the pipeline.

Known callers / typical factories:
- Language-aware tokenizer factory or pipeline components that map language codes to tokenizer instances.
- Any code that needs to split Chinese text into words and can accept an iterable of tokens.

## State:
- Attributes: none (no instance attributes are read or written by this class).
- __init__ parameters: none (the class has no explicit constructor; instantiate with no arguments).
- Valid values / invariants:
    - There is no internal mutable state; repeated calls to tokenize do not affect future calls.
    - The only implicit invariant is that the jieba package must be importable before tokenize returns successfully.

## Lifecycle:
- Creation:
    - Instantiate with no arguments. No configuration or setup steps are required at construction time.
- Usage:
    - Call tokenize(text) with a textual input (str / unicode). The method dynamically attempts to import jieba and then calls jieba.cut(text).
    - The returned value is the iterable yielded by jieba.cut; callers should iterate over it or convert it to a list to materialize tokens.
    - Typical sequence: create instance → call tokenize(text) → iterate tokens.
- Destruction / cleanup:
    - No explicit cleanup is required. The class does not open files, network connections, or hold resources that need closing.
    - There is no context-manager support or close method.

## Method Map:
flowchart LR
    A[ChineseWordTokenizer] --> B[tokenize(text)]
    B --> C{import jieba?}
    C -- success --> D[jieba.cut(text) -> iterable of token strings]
    C -- ImportError --> E[raise ValueError advising pip install jieba]
    D --> F[caller iterates or materializes tokens]
    E --> G[caller receives ValueError]

(Interpretation: tokenize tries to import jieba; on success it returns the iterable from jieba.cut(text); on import failure it raises a ValueError.)

## Raises:
- ValueError: Raised when the local dynamic import of the jieba module fails. The error message guides the user to install jieba:
    "Chinese tokenizer requires jieba. Please, install it by command 'pip install jieba'."
- Propagated exceptions: tokenize does not catch exceptions raised by jieba.cut itself. Any exceptions thrown by jieba (for example, due to invalid input types) will propagate to the caller. Callers should validate inputs if they need to guarantee a specific error behavior.

## Example (prose):
- Creation: construct a ChineseWordTokenizer instance with no constructor arguments.
- Typical call sequence:
    1. Ensure the runtime environment has the jieba package installed; otherwise, calling tokenize will raise a ValueError advising installation.
    2. Call tokenize with a Unicode/text string containing Chinese content.
    3. Receive an iterable from tokenize; iterate over it to process tokens one by one, or convert it to a concrete sequence (for example, by materializing to a list) if random access or repeated traversal is required.
- Error handling:
    - If the environment lacks jieba, catch ValueError and instruct users to install jieba.
    - If inputs may be non-text (None, bytes, or other types), validate or coerce them before calling tokenize, since errors from jieba.cut will propagate.

## Notes and implementation hints:
- This class deliberately does a dynamic import inside tokenize so that the package is optional at install time; keep that behavior if reimplementing.
- Prefer returning the raw jieba.cut iterable (lazy behavior) rather than eagerly materializing tokens, to keep memory usage low for large inputs.
- Do not add internal state or side effects — the class is intended to remain a stateless adapter.

### `sumy.nlp.tokenizers.ChineseWordTokenizer.tokenize` · *method*

## Summary:
Delegates Chinese word tokenization to the optional jieba library and returns an iterable of token strings; does not modify the object's state.

## Description:
This method is a thin adapter around the third-party jieba tokenizer. It performs a dynamic import of jieba (so the dependency is optional at install time) and then calls jieba.cut(text) to obtain tokens.

Known callers and lifecycle:
- No internal call sites were found in the local code presented. In typical usage within a text-processing pipeline, this method is invoked at the tokenization stage when Chinese text must be split into words — for example by higher-level code that selects a tokenizer based on document language and then calls its tokenize method.
- It exists as a separate method to centralize the optional-dependency handling (import and error message) and to provide a clear, pluggable tokenizer implementation for Chinese without inlining jieba-specific logic throughout the codebase.

Why this logic is a separate method:
- Keeps optional-dependency import/localization in one place.
- Allows swapping or mocking the tokenizer in tests and makes the Chinese-specific behavior discoverable as part of the tokenizer interface.

## Args:
    text (str or unicode): The input text to tokenize. The value is forwarded directly to jieba.cut; therefore it should be a textual string type appropriate for jieba (str or unicode in Python 2/3 contexts). No transformation is performed by this method.

## Returns:
    iterable[str]: An iterable (typically a generator) that yields token strings produced by jieba.cut(text). The iterable may be lazy — callers should iterate over it or convert it to a list to materialize tokens.
    Edge cases:
    - If `text` is an empty string, callers should expect an iterable that yields no tokens (empty iterable), depending on jieba's behavior.
    - The exact string type (str vs. unicode) corresponds to what jieba.cut returns for the installed jieba version and Python runtime.

## Raises:
    ValueError: Raised when the jieba library is not importable. The exact condition is an ImportError raised during the attempt to import jieba; the method intercepts that and raises a ValueError with guidance to install jieba:
        "Chinese tokenizer requires jieba. Please, install it by command 'pip install jieba'."

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> attributes).
    Attributes WRITTEN:
        - None (this method does not modify any self.<attr> attributes).

## Constraints:
    Preconditions:
        - The caller should pass a textual string (str/unicode). Non-text inputs are forwarded to jieba.cut and may raise errors or produce unexpected tokens depending on jieba's handling.
        - The jieba package must be installed and importable; otherwise the method raises ValueError.
    Postconditions:
        - No mutation of the tokenizer object (self) occurs.
        - Returns an iterable yielding tokens corresponding to the input text as produced by jieba.cut.

## Side Effects:
    - Performs a dynamic import of the jieba module; this may import and initialize that package the first time it is called.
    - Raises a ValueError if jieba is missing (no external I/O is performed by this method itself).
    - Does not perform file, network I/O, or modify external objects; side effects are limited to the import system and the returned iterable's consumption (which depends on jieba internals).

## `sumy.nlp.tokenizers.KoreanSentencesTokenizer` · *class*

*No documentation generated.*

### `sumy.nlp.tokenizers.KoreanSentencesTokenizer.tokenize` · *method*

## Summary:
Splits Korean text into a sequence of sentences using KoNLPy's Kkma sentence splitter; does not modify the tokenizer object's state.

## Description:
This method performs sentence segmentation for Korean text by dynamically importing konlpy and delegating to Kkma.sentences(text). It is intended to be called during the preprocessing / sentence-splitting stage of a text-processing pipeline (for example, prior to tokenization or summarization). No internal callers are declared in this file; typical callers are higher-level components that need language-specific sentence boundaries.

Keeping this logic in a dedicated method isolates the konlpy dependency and centralizes Korean-specific error handling (raising a clear ValueError when konlpy is missing) rather than inlining the import or Kkma usage across the codebase.

## Args:
    text (str): Unicode string containing the Korean text to segment. The method forwards this value directly to Kkma.sentences. The argument must be text-like (str or unicode); passing None or non-string types will result in errors propagated from konlpy.

## Returns:
    list[str]: A sequence (list) of sentence strings as produced by konlpy.tag.Kkma.sentences. For inputs that contain no sentence boundaries, an empty list or a list with a single element (depending on Kkma's behavior) may be returned — the exact structure follows konlpy's implementation.

## Raises:
    ValueError: If konlpy is not installed (ImportError when importing konlpy.tag.Kkma). The raised ValueError contains a message instructing to install konlpy via pip.
    Any exception raised by konlpy during Kkma() initialization or when calling Kkma.sentences(text) is propagated to the caller (e.g., runtime errors from konlpy or underlying libraries).

## State Changes:
    Attributes READ:
        - None: the method does not read any attributes on self.
    Attributes WRITTEN:
        - None: the method does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - The caller must provide a text-like object (preferably a Python str / unicode). The method assumes konlpy is available; if it is not, the method will raise ValueError.
    Postconditions:
        - The method returns a list of sentence strings produced by Kkma and leaves the tokenizer instance unchanged.

## Side Effects:
    - Dynamically imports konlpy when called; failing import triggers a ValueError.
    - Instantiates a konlpy.tag.Kkma object each call, which may perform non-trivial initialization inside konlpy (potentially expensive in time or memory).
    - No I/O (file, network) or mutation of external objects is performed directly by this method; any such behavior would be a side effect of konlpy itself and will be propagated.

## `sumy.nlp.tokenizers.KoreanWordTokenizer` · *class*

## Summary:
KoreanWordTokenizer is a minimal tokenizer abstraction that extracts Korean noun tokens from an input text using KoNLPy's Kkma morphological analyzer.

## Description:
This class provides a thin wrapper around KoNLPy's Kkma.nouns(...) method to obtain noun tokens from Korean text. It is intended for use by higher-level text-processing components that need Korean noun extraction for tasks such as keyword extraction, indexing, or summarization. The class deliberately delays importing konlpy until tokenize(...) is called so that the optional heavy dependency is only required at runtime when actually used.

Typical usage scenarios:
- When language detection or caller logic determines the text is Korean and only noun tokens are required.
- In pipelines where a lightweight adapter is preferred so that the rest of the system can remain independent of konlpy unless Korean processing is invoked.

Responsibility boundary:
- Only extracts nouns (as returned by Kkma.nouns). It does not perform sentence segmentation, normalization, stop-word removal, stemming, or full tokenization beyond Kkma's noun extraction.
- Does not cache or persist any analyzer state between calls.

Known callers / factories:
- Any language-specific tokenizer selector in the application that delegates to this class when processing Korean text. (No factory functions are defined on the class itself.)

## State:
- This class defines no persistent instance attributes (no __init__ arguments). Each call to tokenize creates its own Kkma analyzer instance.
- Implicit types:
  - Input: text (expected type: str/unicode). The caller should provide Python text strings (str in Py3, unicode in Py2 compatibility contexts).
  - Output: list[str] — list of noun tokens extracted by Kkma; tokens are returned as Unicode strings.
- Valid values and invariants:
  - text may be an empty string; the method will return an empty list if no nouns are found.
  - The class maintains no cross-call state: successive calls are independent and do not alter internal state.
  - The only invariant the class enforces is that tokenize either returns a list of noun strings or raises an exception (see Raises).

## Lifecycle:
- Creation:
  - Instantiate with no arguments: tokenizer = KoreanWordTokenizer()
  - No required configuration or factory methods.
- Usage:
  - Call tokenize(text) as many times as needed. Each call:
    1. Attempts to import konlpy.tag.Kkma.
    2. On success, constructs a new Kkma() analyzer.
    3. Calls analyzer.nouns(text) and returns the resulting list.
  - There is no required ordering between multiple tokenize calls; calls are idempotent in the sense they do not change class state.
- Destruction:
  - No explicit cleanup or teardown is required. No file handles or context-managed resources are opened by this class.
  - If the Kkma analyzer allocates external resources internally, they are managed by konlpy/Kkma and are not exposed here.

## Method Map:
flowchart TD
    A[KoreanWordTokenizer.tokenize(text)] --> B{Import konlpy.tag.Kkma}
    B -- Import success --> C[Instantiate Kkma() -> kkma]
    C --> D[Call kkma.nouns(text)]
    D --> E[Return list of noun strings]
    B -- ImportError --> F[Raise ValueError("Korean tokenizer requires konlpy...")]

(Interpretation: tokenize tries to import Kkma, on success creates Kkma and returns kkma.nouns(text); on ImportError it raises a ValueError advising to install konlpy.)

## Raises:
- ValueError
  - Trigger: konlpy is not installed or import of konlpy.tag.Kkma fails.
  - Message: "Korean tokenizer requires konlpy. Please, install it by command 'pip install konlpy'."
- Any exception raised by Kkma() construction or kkma.nouns(text)
  - Trigger: runtime errors originating from konlpy or the underlying Java/Python bridge used by konlpy (e.g., JVM errors, unexpected input types).
  - These exceptions are not caught by the class and will propagate to the caller.
- Type-related errors:
  - If text is not a string-like object, Kkma.nouns may raise a TypeError or Unicode-related error; such errors are propagated.

## Example:
- Instantiate the tokenizer:
  - Create an instance with no arguments: tokenizer = KoreanWordTokenizer()
- Typical call sequence:
  - Call tokenize with a Korean text string: tokens = tokenizer.tokenize("한국어 문장 예시")
  - tokens is a list of noun strings extracted by Kkma (possibly empty).
- Error handling:
  - If konlpy is not installed, calling tokenize will raise a ValueError. Callers should either ensure konlpy is installed in the runtime environment or catch ValueError and handle the absence of the dependency (for example, fall back to a different tokenizer or skip Korean processing).

### `sumy.nlp.tokenizers.KoreanWordTokenizer.tokenize` · *method*

## Summary:
Extracts noun tokens from the supplied Korean text by delegating to konlpy.tag.Kkma.nouns(...) and returns that result. The method does not modify the tokenizer object's attributes.

## Description:
This method performs a lazy (runtime) import of konlpy.tag.Kkma, constructs a Kkma instance, and immediately calls its nouns(text) method, returning the value produced by that call. It is implemented as a dedicated method to:
- Centralize the konlpy dependency and the language-specific noun-extraction logic in one place.
- Defer importing konlpy until Korean tokenization is actually requested (the import is attempted inside the method).

Typical call context:
- Invoked during the tokenization stage of a text-processing pipeline when Korean word (noun) tokens are required (for example, by higher-level summarizers, indexers, or language-specific dispatchers).
- Usually called after language normalization and sentence segmentation steps.

Why this is a separate method:
- Keeps the konlpy-specific import and object construction localized so other modules do not need to import konlpy directly.
- Allows callers to choose whether to accept per-call Kkma construction or to cache a Kkma instance for repeated calls.

## Args:
    text (str or unicode): The input text supplied to Kkma.nouns. The method forwards this argument unchanged to Kkma.nouns.

## Returns:
    The raw return value of konlpy.tag.Kkma.nouns(text).
    - The exact type and structure of the return value are those defined by konlpy and are not enforced by this method.
    - Callers should treat the return value as opaque output from the konlpy library; in typical usage this is a sequence of token strings, but the concrete type/contents are determined by konlpy's implementation.

## Raises:
    ValueError: Raised when konlpy cannot be imported. The method converts ImportError into:
        "Korean tokenizer requires konlpy. Please, install it by command 'pip install konlpy'."
    Any exception raised by Kkma() construction or by Kkma.nouns(text) is NOT caught and will propagate to the caller (for example, TypeError if an invalid argument is passed, or any runtime error originating in konlpy).

## State Changes:
    Attributes READ:
        - None (the method does not access any self.<attr> fields)
    Attributes WRITTEN:
        - None (the method does not modify any self.<attr> fields)

## Constraints:
    Preconditions:
        - The caller must provide a text argument appropriate for konlpy.tag.Kkma.nouns; passing non-string values may raise an exception propagated from konlpy.
        - konlpy must be installable/importable in the runtime environment; otherwise the method raises ValueError as described above.
    Postconditions:
        - Returns the result of Kkma.nouns(text).
        - No attributes on self are changed by this call.

## Side Effects:
    - Performs a runtime import of konlpy (if not already imported) and instantiates a new Kkma object on every call (the source contains kkma = Kkma()).
    - No file, network, or external I/O is performed by this method itself; any such behavior would be caused by the konlpy library and will propagate accordingly.
    - Recommended caller practice: if tokenizing many texts in a loop, consider creating and reusing a single Kkma instance (e.g., store it on self) to avoid repeated construction overhead.

## `sumy.nlp.tokenizers.GreekSentencesTokenizer` · *class*

## Summary:
A stateless classmethod tokenizer that segments Greek text into sentence strings by combining NLTK's Greek sentence tokenizer with an additional split on semicolon-like punctuation.

## Description:
This class provides a single utility, tokenize, to convert Greek text into a flat list of sentence fragments suitable for downstream tasks (e.g., summarization, sentence scoring, or sentence-level preprocessing).

Design responsibility:
- Two-stage sentence segmentation:
  1. Use NLTK's language-aware sentence tokenizer (nltk.sent_tokenize with language='greek') to obtain high-level sentence boundaries.
  2. Further split each NLTK sentence on semicolon-like characters that often function as sentence terminators in Greek: the ASCII semicolon ';' and the Greek punctuation ';' (U+037E). The split preserves the terminating semicolon at the end of the preceding fragment.
- Stateless utility: no instance or class state is maintained; behavior is deterministic given the same input and the same NLTK resources.

Intended callers:
- Primarily designed to be invoked by higher-level language/tokenization selection logic that dispatches tokenization by language (i.e., when language == 'greek').
- It can also be called directly by client code as GreekSentencesTokenizer.tokenize(text).

Motivation for separation:
- Greek punctuation semantics (semicolon and the Greek question-mark-like punctuation) are handled more accurately by applying this two-stage approach rather than relying solely on a single tokenizer.

## State:
Attributes:
- None. The class defines no instance or persistent class attributes; it is stateless.

__init__ parameters:
- There is no __init__; instantiation is unnecessary. Use the classmethod directly.

Parameter naming note:
- The tokenize method is declared as a classmethod and uses a first parameter named 'self' in the source; this parameter represents the class object but is unused by the implementation. Callers should invoke the method on the class (GreekSentencesTokenizer.tokenize(...)) and need not supply a class or instance.

Class invariants:
- For identical input strings and identical NLTK resources/configuration, tokenize produces the same list of sentence strings.
- The method performs no I/O or external state mutation.

## Lifecycle:
Creation:
- No creation/instantiation required. Call the classmethod directly:
  - GreekSentencesTokenizer.tokenize(text)

Usage:
- Input: text (str/unicode) — a string containing Greek text.
- Sequence:
  1. Call tokenize(text).
  2. Internally, nltk.sent_tokenize(text, language='greek') produces initial sentences.
  3. Each sentence is split by the regex (?<=[;;])\s+ to break after ';' or ';' when followed by whitespace.
  4. Empty fragments are removed; remaining fragments are stripped of surrounding whitespace.
  5. The flattened list of stripped fragments is returned.
- Methods may be called repeatedly in any order; each call is independent.

Destruction:
- No cleanup required; no context manager or close method.

## Method Map:
graph LR
    Caller --> Tokenize[GreekSentencesTokenizer.tokenize(text)]
    Tokenize --> NLTK[nltk.sent_tokenize(text, language='greek')]
    NLTK --> ForEach[for each top-level sentence]
    ForEach --> RegexSplit[re.split(r'(?<=[;;])\s+', sentence)]
    RegexSplit --> Filter[filter out empty fragments]
    Filter --> Strip[strip() each fragment]
    Strip --> Collect[collect fragments into list]
    Collect --> Return[return list[str]]

## Detailed behavior of tokenize(text)
Inputs:
- text (str/unicode): Greek text to segment. Must be a text string; passing non-text types or None may raise TypeError when processed.

Outputs:
- list[str]: Flattened list of sentence fragments. Each item is a substring of the input with leading/trailing whitespace removed. Semicolon characters that trigger splits remain at the end of the preceding fragment.

Step-by-step algorithm:
1. Call nltk.sent_tokenize(text, language='greek') to obtain preliminary sentences.
2. For each sentence returned:
   a. Apply re.split(r'(?<=[;;])\s+', sentence) to split on whitespace sequences that immediately follow ';' or ';'. The positive lookbehind keeps the punctuation on the left fragment.
   b. Remove empty strings from the split result.
   c. Strip whitespace from each fragment.
3. Flatten all fragments across sentences into a single list and return.

Edge cases and constraints:
- Empty input string: typically returns an empty list (dependent on NLTK behavior).
- Semicolons not followed by whitespace (e.g., immediately followed by end-of-string or another punctuation) will not cause an additional split.
- Multiple consecutive whitespace characters after a semicolon are treated as a single split boundary.
- The method preserves the punctuation characters ';' and ';' on the left fragment due to the lookbehind in the regex.

## Raises:
- LookupError: If required NLTK resources (e.g., 'punkt') are missing, nltk.sent_tokenize may raise LookupError; ensure appropriate NLTK models are installed (e.g., nltk.download('punkt')).
- TypeError: If text is not a string-like object (e.g., None or a non-text type), operations in nltk.sent_tokenize, re.split, or str.strip may raise TypeError.
- Propagated exceptions: Any exceptions raised by nltk.sent_tokenize or the regex engine (re) can propagate; the method does not perform internal exception handling.

## Example:
- Typical invocation from language dispatch logic:
  If your pipeline selects a tokenizer by language:
  if language == 'greek':
      sentences = GreekSentencesTokenizer.tokenize(text)

- Direct usage example:
  GreekSentencesTokenizer.tokenize("Αυτό είναι ένα τεστ. Δοκιμή; Επόμενη πρόταση; Και άλλη μία.")
  Possible return (illustrative):
  ["Αυτό είναι ένα τεστ.", "Δοκιμή;", "Επόμενη πρόταση;", "Και άλλη μία."]

Notes:
- Ensure NLTK sentence models are available in the runtime (download 'punkt' if necessary) before calling tokenize.

### `sumy.nlp.tokenizers.GreekSentencesTokenizer.tokenize` · *method*

## Summary:
Splits Greek text into a list of sentence strings by first using NLTK's sentence tokenizer for Greek and then further splitting on Greek semicolon characters; returns trimmed, non-empty sentences.

## Description:
This method is invoked during text preprocessing when the pipeline needs sentence-level segmentation for Greek-language input (for example, as part of a summarization or NLP preprocessing step that normalizes and tokenizes input text). It is a dedicated method because Greek punctuation semantics require two-stage handling: (1) NLTK's language-aware sentence tokenization to handle ordinary sentence boundaries, and (2) an additional split on semicolon-like punctuation used in Greek (the standard ASCII semicolon ';' and the Greek question mark ';') which often appears as a sentence terminator in Greek texts and may not always be handled as an independent sentence boundary by NLTK alone.

Known callers / context:
- The tokenizer is intended to be called by higher-level language/tokenization selection logic that dispatches based on language == 'greek'.
- It is called at the sentence segmentation step of the text processing pipeline, prior to token-level processing or summarization.

## Args:
    text (str): Input text to segment. Must be a (unicode) string. Passing None or non-string objects is unsupported and will typically raise a TypeError from the underlying NLTK tokenizer.

## Returns:
    list[str]: A list of sentence strings.
        - Each element is stripped of leading/trailing whitespace.
        - Empty strings are discarded; result contains only non-empty sentences.
        - If the input is an empty string or contains only whitespace, returns an empty list.

## Raises:
    TypeError: If `text` is not a string-like object and NLTK's tokenizer fails when called.
    LookupError (nltk.data.LookupError or subclass): If the NLTK punkt models for Greek are not installed and nltk.sent_tokenize cannot find the tokenizer resources.
    Any exception raised by nltk.sent_tokenize may propagate (e.g., unexpected input handling).

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> fields)
    Attributes WRITTEN:
        - None (this method does not modify any self.<attr> fields)

## Constraints:
    Preconditions:
        - NLTK must be available and have the punkt tokenizer models for Greek installed (nltk.download('punkt') or equivalent with Greek support).
        - `text` must be a str/unicode object.
    Postconditions:
        - Returns a flat list of non-empty, trimmed sentence strings.
        - All original content is preserved except for surrounding whitespace trimming and the insertion of additional boundaries where Greek semicolon/question-mark punctuation is used to split sentences.

## Side Effects:
    - No I/O is performed.
    - No mutation of objects outside of the returned list occurs.
    - Relies on NLTK library functions (calls nltk.sent_tokenize), which may trigger NLTK internal lookups (but does not itself perform file writes).

## Implementation notes (for reimplementation):
    - Call nltk.sent_tokenize(text, language='greek') to obtain an initial list of sentence segments.
    - For each segment, split further using a regex that finds whitespace sequences immediately following ';' or ';' (the regex used here is (?<=[;;])\s+). Use re.split to produce pieces.
    - Filter out empty pieces (e.g., with filter(None, ...)).
    - Strip leading/trailing whitespace from each piece and collect into a single flat list to return.

## `sumy.nlp.tokenizers.ArabicWordTokenizer` · *class*

## Summary:
Delegates Arabic word tokenization to the pyarabic library via a lazy import and returns the library's tokenization result.

## Description:
ArabicWordTokenizer is a minimal adapter that encapsulates the optional dependency on the external pyarabic package. It provides a single responsibility: given an input text, attempt to import pyarabic.araby.tokenize at call time and delegate tokenization to it. This design avoids hard-importing pyarabic at module import time and centralizes the dependency check and error message in one place.

Typical scenarios:
- Use when you need word-level tokenization for Arabic text inside a language-aware NLP pipeline (e.g., text normalization, summarization, indexing).
- Instantiate and call tokenize(text) wherever a language-specific tokenizer object is expected by the pipeline.
- Useful when pyarabic is an optional dependency: code can catch the ValueError to provide a fallback or user-facing instruction to install pyarabic.

Known callers/factories:
- No explicit callers in the provided repository snapshot. This class is intended to be instantiated directly where Arabic word tokenization is required.

## State:
Attributes
- This class defines no instance attributes (no __init__ parameters and no self.<attr> usage). It is stateless from the perspective of the visible API.

__init__ parameters
- No explicit __init__ method is defined; the default constructor requires no arguments.

Valid values / invariants
- There are no per-instance invariants beyond the absence of persistent state.
- The only runtime requirement is that pyarabic.araby be importable when tokenize() is invoked; otherwise the method raises a ValueError.

Class invariants
- Calling tokenize() must not mutate the tokenizer instance.
- Repeated calls are independent and rely only on the provided text and the availability of pyarabic.

## Lifecycle:
Creation
- Instantiate with no arguments:
  - Example: create an instance (see Example section).
- No factory methods are required or provided.

Usage
- Primary method: tokenize(text)
  - Must be called with a single argument text (string-like). The text is forwarded to pyarabic.araby.tokenize without preprocessing by this class.
  - The method performs a lazy import of pyarabic.araby.tokenize on each call (or uses the already-imported module from previous calls).

Typical invocation order
1. Create instance (no args).
2. Call tokenize(text) as needed.
3. Repeat step 2 as required by the pipeline.

Destruction / cleanup
- No explicit cleanup is required. The class does not hold resources, open files, or network connections.
- It is not a context manager and does not implement close().

## Method Map:
(Flow of a typical tokenize invocation)

mermaid
graph TD
    A[Caller] --> B[ArabicWordTokenizer.tokenize(text)]
    B --> C{Attempt import}
    C -->|ImportError| D[Raise ValueError with install message]
    C -->|Success| E[Call pyarabic.araby.tokenize(text)]
    E --> F[Return pyarabic result]
    D --> G[Caller handles ValueError or aborts]

## Behavior and return value:
- Inputs:
  - text: expected to be a string (str or unicode). The method does not coerce or validate types; non-string inputs are forwarded and may cause errors inside pyarabic.
- Outputs:
  - Returns exactly whatever pyarabic.araby.tokenize(text) returns. Callers should generally expect an iterable (commonly a list) of token strings representing word-level tokens of the input text.
- Side effects:
  - Performs a dynamic import the first time (or on each call) which loads the pyarabic module into the runtime.
  - No I/O, no mutation of the instance, and no global state changes beyond the import.

## Raises:
- ValueError: Raised when pyarabic cannot be imported. Exact message:
    "arabic tokenizer requires pyarabic. Please, install it by command 'pip install pyarabic'."
  Trigger condition: ImportError raised while trying to import pyarabic.araby.tokenize.
- Any exception raised by pyarabic.araby.tokenize(text) is propagated unchanged. Typical propagated errors may include TypeError or ValueError if the argument is invalid for the external function.

## Edge cases and constraints:
- Missing dependency: callers should be prepared to catch ValueError and provide an alternative path or an installation instruction to the user.
- Non-string input: this class does not validate input types; passing bytes, None, or other types will be forwarded and may cause runtime errors in pyarabic.
- Mixed-language text: behavior is delegated to pyarabic; this adapter does not attempt to detect or restrict input language.

## Example:
1) Instantiate and use (narrative form)
- Create the tokenizer instance with no arguments.
- Call tokenize(text) with an Arabic string.
- If pyarabic is not installed, the call raises ValueError with the installation message; handle it to provide a fallback or notify users.

2) Example sequence (conceptual)
- tokenizer = ArabicWordTokenizer()
- tokens = tokenizer.tokenize("النص العربي هنا")
- If the environment lacks pyarabic, the tokenize call raises ValueError with the exact install message shown above.

## Notes:
- This class intentionally contains minimal logic. Its purpose is to isolate the optional pyarabic dependency and to present a unified tokenizer interface for Arabic word tokenization within the larger system.

### `sumy.nlp.tokenizers.ArabicWordTokenizer.tokenize` · *method*

## Summary:
Delegates Arabic word tokenization to the pyarabic library and returns its result; does not modify the tokenizer instance.

## Description:
- Known callers:
    - No explicit callers were found within the scanned repository code. This method is intended to be used anywhere an Arabic word tokenizer is required (for example, in text-processing or summarization pipelines that accept a language-specific tokenizer).
- Lifecycle / pipeline context:
    - Invoked at the tokenization stage of an NLP pipeline when Arabic input text must be split into word tokens.
- Why this is a separate method:
    - Encapsulates the optional dependency on the pyarabic library and performs a lazy import. Keeping the logic in a dedicated method isolates the optional-dependency check and delegation, avoiding a hard import at module load time and making error handling for missing dependency uniform and localized.

## Args:
    text (str | unicode): Input text to tokenize. Should contain Arabic (or mixed) text to be tokenized into words. The method does no explicit type coercion; non-string inputs will be passed directly to pyarabic.araby.tokenize and may raise errors there.

## Returns:
    object: The exact return value produced by pyarabic.araby.tokenize(text). Callers should generally expect an iterable (commonly a list) of token strings representing word-level tokens of the input text. The method performs no post-processing of the returned value.

## Raises:
    ValueError: Raised when the pyarabic package is not available in the environment. Exact message:
        "arabic tokenizer requires pyarabic. Please, install it by command 'pip install pyarabic'."
    Any exception raised by pyarabic.araby.tokenize(text) (e.g., TypeError, ValueError) is propagated unchanged.

## State Changes:
    Attributes READ:
        - None (method does not access any self.<attr> attributes).
    Attributes WRITTEN:
        - None (method does not modify the tokenizer instance).

## Constraints:
    Preconditions:
        - pyarabic (module pyarabic.araby) must be installed and importable; otherwise the method raises ValueError.
        - The caller should pass a string-like object appropriate for pyarabic.araby.tokenize; the method itself performs no validation.
    Postconditions:
        - If no ImportError occurs, the method returns whatever pyarabic.araby.tokenize(text) returns and leaves self unchanged.

## Side Effects:
    - No I/O or external service calls performed by this method itself.
    - Performs a dynamic import of pyarabic.araby when first called (lazy import). This has the side effect of loading that module into the Python runtime and may execute import-time code from pyarabic.

## `sumy.nlp.tokenizers.ArabicSentencesTokenizer` · *class*

## Summary:
A minimal wrapper providing an Arabic sentence tokenizer that delegates sentence splitting to pyarabic.araby.sentence_tokenize.

## Description:
This class exists solely to provide a consistent tokenizer interface (tokenize(text)) for Arabic sentence segmentation within the codebase while performing a lazy import of the external pyarabic dependency. It does not perform normalization, language detection, or fallback tokenization; it simply imports and calls pyarabic.araby.sentence_tokenize when tokenize is invoked.

Instantiate this class when you need to split Arabic text into sentences and want the dependency on pyarabic deferred until tokenization time. Typical callers are higher-level preprocessing or summarization components that select a tokenizer by language and call tokenize(text).

## State:
- Instance attributes: none. The class defines no __init__ and holds no internal state.
- __init__ parameters: none (default constructor).
- Valid inputs: the tokenize method expects a text-like object (Python str / unicode). The class performs no encoding conversions.
- Class invariants:
  - The instance has no mutable state; repeated calls to tokenize are independent and stateless.
  - tokenize always attempts a dynamic import of pyarabic.araby.sentence_tokenize on each invocation (import behavior is determined by the Python import system).

## Lifecycle:
- Creation:
  - Use the default constructor: tokenizer = ArabicSentencesTokenizer()
  - No arguments or configuration are required.
- Usage:
  - Call tokenizer.tokenize(text) with a single argument named text (str/unicode).
  - The method dynamically imports pyarabic.araby.sentence_tokenize and delegates to it.
  - Any exception raised by pyarabic.araby.sentence_tokenize will propagate to the caller.
- Destruction:
  - No cleanup or resource management is required; there is no close(), context manager, or other teardown API.

## Method Map:
flowchart TD
    Client --> TokenizeCall[ArabicSentencesTokenizer.tokenize(text)]
    TokenizeCall --> TryImport{Import pyarabic.araby.sentence_tokenize}
    TryImport -- success --> Delegate[Call sentence_tokenize(text)]
    TryImport -- ImportError --> RaiseValErr[Raise ValueError with install hint]
    Delegate --> ReturnResult[Return result to client]

## Methods
- tokenize(text)
  - Purpose: Split the provided text into sentences by delegating to pyarabic.araby.sentence_tokenize.
  - Signature:
    - text (str): Input text to be tokenized into sentences. Parameter name and count must match the implementation: one positional parameter named text.
  - Return:
    - Returns exactly whatever pyarabic.araby.sentence_tokenize(text) returns; the wrapper does not transform or inspect the returned value.
  - Behavior:
    - Attempts "from pyarabic.araby import sentence_tokenize" at call time.
    - If the import succeeds, calls sentence_tokenize(text) and returns its result.
    - If the import raises ImportError, the method raises ValueError with this exact message:
        "arabic tokenizer requires pyarabic. Please, install it by command 'pip install pyarabic'."
    - Any exception raised by sentence_tokenize(text) (other than ImportError during import) is not caught and will propagate to the caller.
  - Edge cases and constraints:
    - The method does not verify that the input text is Arabic; it forwards the text to pyarabic and relies on that library's behavior.
    - The method performs no preprocessing (trimming, normalization) on the input.

## Raises:
- ValueError:
  - Trigger: ImportError occurs when attempting to import pyarabic.araby.sentence_tokenize inside tokenize.
  - Message: "arabic tokenizer requires pyarabic. Please, install it by command 'pip install pyarabic'."
- Propagated exceptions:
  - Any exception raised by pyarabic.araby.sentence_tokenize(text) after a successful import will propagate; this wrapper does not catch those exceptions.

## Example:
- Typical usage:
    tokenizer = ArabicSentencesTokenizer()
    arabic_text = "مرحباً. كيف حالك؟ هذا اختبار."
    try:
        sentences = tokenizer.tokenize(arabic_text)
        for s in sentences:
            # process each sentence (the exact type/structure of items in sentences
            # is determined by pyarabic.araby.sentence_tokenize)
            print(s)
    except ValueError as err:
        # pyarabic is not installed; err.args[0] contains the installation hint
        print("Dependency missing:", err)

- Notes:
    - Do not rely on this class to provide fallback behavior if pyarabic is unavailable; handle ValueError externally if a fallback is desired.

### `sumy.nlp.tokenizers.ArabicSentencesTokenizer.tokenize` · *method*

## Summary:
Performs sentence segmentation on the provided input by delegating to pyarabic.araby.sentence_tokenize; does not modify the tokenizer instance.

## Description:
This method performs a lazy import of pyarabic.araby.sentence_tokenize and immediately delegates sentence splitting to it. The import is deferred until this method is called so that the optional pyarabic dependency is only required when Arabic sentence tokenization is used.

Known callers and context:
- The source file does not define any direct callers. This method is intended to be called by higher-level components that need Arabic sentence segmentation (for example, during preprocessing or sentence-splitting stages of an NLP pipeline). This is an intent statement; no call sites are present in this module.

Why this is a separate method:
- Encapsulates the optional dependency on pyarabic and presents a stable tokenizer method on the ArabicSentencesTokenizer class.
- Keeps the import lazy to avoid forcing users to install pyarabic unless Arabic tokenization is used.

## Args:
    text (object): The argument passed through to pyarabic.araby.sentence_tokenize. The method implementation does not validate the type; supplying a non-string may cause pyarabic to raise an exception.

## Returns:
    object: The direct return value of pyarabic.araby.sentence_tokenize(text). The exact type and content depend on the pyarabic implementation; this wrapper does not transform or validate the returned value.

## Raises:
    ValueError: Raised if importing pyarabic.araby.sentence_tokenize fails (pyarabic is not installed). The exact message raised is:
        "arabic tokenizer requires pyarabic. Please, install it by command 'pip install pyarabic'."
    Any exception raised by pyarabic.araby.sentence_tokenize (e.g., TypeError, ValueError from that function) is not caught and will propagate to the caller.

## State Changes:
Attributes READ:
    - None (this method does not access any self.<attr> attributes)

Attributes WRITTEN:
    - None (this method does not modify the instance state)

## Constraints:
Preconditions:
    - There is no enforced precondition in this wrapper beyond callable availability of pyarabic.araby.sentence_tokenize. Callers should ensure the argument is appropriate for pyarabic.araby.sentence_tokenize to avoid downstream exceptions.

Postconditions:
    - The instance state is unchanged.
    - The method returns whatever pyarabic.araby.sentence_tokenize(text) returns (or raises an exception if import fails or the delegate raises).

## Side Effects:
    - No I/O, network access, or mutation of external objects is performed by this wrapper itself.
    - Side effects (if any) are solely those produced by pyarabic.araby.sentence_tokenize when it is invoked.

## `sumy.nlp.tokenizers.Tokenizer` · *class*

## Summary:
A language-aware sentence-and-word tokenizer abstraction that selects language-specific tokenizers (special-case implementations or NLTK's Punkt) and exposes simple to_sentences and to_words methods returning tuples of normalized strings.

## Description:
Tokenizer centralizes sentence and word tokenization for multiple languages. Construct it with a language name (string) and it will:
- Normalize the language name and map language aliases (e.g., "slovak" -> "czech").
- Select a sentence tokenizer: either a language-specific special tokenizer (preconfigured RegexpTokenizer or language-specific class) or an NLTK Punkt tokenizer loaded from tokenizers/punkt/<language>.pickle.
- Select a word tokenizer: either a language-specific special word tokenizer or a DefaultWordTokenizer fallback.

Typical usage scenarios:
- Create a Tokenizer for a document language, call to_sentences(paragraph) to split a paragraph into sentences, then call to_words(sentence) for token lists to feed downstream processing (lemmatization, stop-word removal, summarization).
- The class is used where language-specific quirks (abbreviations, punctuation rules, script-specific segmentation) must be handled automatically.

Known callers/factories:
- The constructor is the main factory: Tokenizer(language).
- Consumers typically instantiate one Tokenizer per language and reuse it for many paragraphs/sentences.

Responsibility boundary:
- Tokenizer selects and composes sentence- and word-tokenizer implementations and provides normalized string outputs.
- It does not perform normalization of tokens beyond trimming whitespace and filtering out non-word tokens; it delegates segmentation to provided tokenizer implementations.

## State:
Public attributes / properties:
- language (str, read-only): The normalized language name provided at construction (e.g., "english", "czech").

Internal attributes (implementation details required to reimplement correctly):
- _language (str): Same value as language property; normalized form returned by normalize_language(language).
  - Valid values: normalized language strings expected by the available tokenizers (no explicit runtime check beyond normalize_language).
- _sentence_tokenizer (object): The selected sentence tokenizer instance. Must implement tokenize(text: str) -> list/tuple of strings.
  - Valid types: NLTK Punkt sentence tokenizer, nltk.RegexpTokenizer, or language-specific tokenizer classes (e.g., KoreanSentencesTokenizer) included in the codebase.
  - Invariant: _sentence_tokenizer.tokenize must accept a Unicode/str paragraph and return an iterable of sentence strings.
- _word_tokenizer (object): The selected word tokenizer instance. Must implement tokenize(text: str) -> list/tuple of token strings.
  - Valid types: DefaultWordTokenizer or language-specific word tokenizers (e.g., HebrewWordTokenizer, ChineseWordTokenizer).
  - Invariant: _word_tokenizer.tokenize must accept a Unicode/str sentence and return an iterable of token strings.

Class-level constants (state that affects behavior):
- _WORD_PATTERN (compiled re.Pattern): r"^[^\W\d_](?:[^\W\d_]|['-])*$" with re.UNICODE.
  - Meaning: A token is considered a word if it starts with a Unicode letter (not a digit or underscore or other non-word) and subsequent characters are Unicode letters or the characters ' or -. This filters out tokens that are not alphabetic-like words.
- LANGUAGE_ALIASES (dict): Maps some language names to other tokenization languages (e.g., "slovak" -> "czech").
- LANGUAGE_EXTRA_ABREVS (dict): Per-language lists of abbreviation strings. Used to augment NLTK Punkt tokenizer parameters (if present) to avoid splitting sentences on those abbreviations.
- SPECIAL_SENTENCE_TOKENIZERS (dict): Language -> tokenizer instance used instead of Punkt for sentence splitting for certain languages.
- SPECIAL_WORD_TOKENIZERS (dict): Language -> tokenizer instance used instead of the DefaultWordTokenizer for word splitting.

Class invariants:
- After construction, _sentence_tokenizer and _word_tokenizer are non-null and implement tokenize(text) to return sentence/token lists.
- language property equals the normalized language used to select tokenizers.
- _WORD_PATTERN remains the single source of truth for filtering tokens returned by to_words.

## Lifecycle:
Creation:
- Instantiate with a single required argument:
    Tokenizer(language: str)
  - The provided language is normalized via utils.normalize_language. The constructor maps aliases via LANGUAGE_ALIASES before selecting internal tokenizers.

Usage:
- Typical method sequence:
    1. tokenizer = Tokenizer("english")
    2. sentences = tokenizer.to_sentences(paragraph)   # returns tuple of stripped sentence strings
    3. for s in sentences:
           words = tokenizer.to_words(s)               # returns tuple of tokens matching _WORD_PATTERN
- to_sentences(paragraph: str) uses the internal sentence tokenizer's tokenize method. If the tokenizer exposes a _params attribute (as NLTK Punkt tokenizers do), Tokenizer merges any per-language extra abbreviations from LANGUAGE_EXTRA_ABREVS into tokenizer._params.abbrev_types before tokenization. The paragraph is converted to Unicode using to_unicode() prior to tokenization. The returned sentences are stripped of surrounding whitespace.
- to_words(sentence: str) uses the internal word tokenizer's tokenize on the Unicode-converted sentence, then filters tokens using the class-level _is_word predicate (based on _WORD_PATTERN). The returned value is a tuple of tokens that match the word pattern.

Destruction / cleanup:
- No explicit cleanup required. The class does not open external resources that require closing.
- Tokenizer is not a context manager and provides no close() method.

## Method Map:
A simplified method-call graph (Mermaid flowchart). Typical invocation order is shown.

graph LR
    A[__init__(language)] --> B[normalize_language(language)]
    A --> C[_get_sentence_tokenizer(tokenizer_language)]
    A --> D[_get_word_tokenizer(tokenizer_language)]
    C -->|special| E[SPECIAL_SENTENCE_TOKENIZERS[language]]
    C -->|punkt| F[nltk.data.load("tokenizers/punkt/<lang>.pickle")]
    F -->|may raise| G[LookupError / zipfile.BadZipfile -> re-raised as LookupError]
    D -->|special| H[SPECIAL_WORD_TOKENIZERS[language]]
    D -->|default| I[DefaultWordTokenizer()]
    J[to_sentences(paragraph)] --> K[if _sentence_tokenizer._params: update abbrev_types]
    J --> L[_sentence_tokenizer.tokenize(to_unicode(paragraph))]
    L --> M[strip each sentence] --> N[tuple of sentences]
    O[to_words(sentence)] --> P[_word_tokenizer.tokenize(to_unicode(sentence))]
    P --> Q[filter tokens with _is_word] --> R[tuple of words]
    S[_is_word(word)] --> T[_WORD_PATTERN.match(word) -> bool]

## Methods / Behavior Summary:
- __init__(language: str)
    - Normalizes language via normalize_language(language).
    - Uses LANGUAGE_ALIASES to map the normalized language to a tokenizer language identifier.
    - Calls internal helpers to select sentence and word tokenizers.
    - Raises: LookupError when NLTK Punkt models are missing or corrupted for non-special languages (see _get_sentence_tokenizer).

- language (property) -> str
    - Read-only property returning the normalized language string.

- to_sentences(paragraph: str) -> tuple[str, ...]
    - Converts paragraph to Unicode (to_unicode).
    - If the _sentence_tokenizer has a _params attribute, merges per-language extra abbreviation strings (LANGUAGE_EXTRA_ABREVS.get(self._language, [])) into _sentence_tokenizer._params.abbrev_types to avoid incorrect sentence splits.
    - Calls _sentence_tokenizer.tokenize on the Unicode paragraph.
    - Strips whitespace from each returned sentence.
    - Returns a tuple of sentence strings in the same order as the tokenizer produced them.
    - Edge cases:
        - If paragraph is empty or contains only whitespace, the behavior depends on the underlying tokenizer; the method will still attempt to call tokenize and return the tokenizer's result (often an empty tuple/list).
        - If the sentence tokenizer lacks tokenize or returns unexpected types, a runtime exception will propagate.

- to_words(sentence: str) -> tuple[str, ...]
    - Converts sentence to Unicode (to_unicode) and calls _word_tokenizer.tokenize.
    - Filters tokens using the static _is_word method; only tokens matching _WORD_PATTERN are returned.
    - Returns a tuple of filtered tokens.
    - Edge cases:
        - Hyphenated or apostrophed tokens are allowed if they follow the pattern rules (start with a letter and contain letters or ' or -).
        - Tokens that are purely numbers, punctuation, or include underscores are filtered out.

- _is_word(word: str) -> bool (static)
    - Uses the compiled _WORD_PATTERN to determine whether a token is considered a word. Returns True for matches, False otherwise.
    - Note: This method relies on Unicode-aware classification (re.UNICODE) to decide what counts as a letter.

## Raises:
- __init__:
    - LookupError raised by _get_sentence_tokenizer when:
        * NLTK Punkt tokenizer data for the requested language cannot be loaded, either because the resource is missing (nltk.data.load raises LookupError) or because the pickle resource is invalid (zipfile.BadZipfile). The class re-raises a LookupError with a message indicating missing NLTK tokenizers or unsupported language and includes the original exception message.

- to_sentences / to_words:
    - No explicit exceptions raised by Tokenizer, but underlying tokenizers may raise exceptions (TypeError, AttributeError, etc.) which propagate. Callers should ensure inputs are str/unicode and that required tokenizer resources are installed.

## Example:
- Create an English tokenizer and process a paragraph into words:

tokenizer = Tokenizer("english")
paragraph = "Dr. Smith arrived at 10 a.m. He said: 'Hello — world!'"
sentences = tokenizer.to_sentences(paragraph)
# sentences -> tuple of sentence strings with surrounding whitespace removed

for s in sentences:
    words = tokenizer.to_words(s)
    # words -> tuple of tokens matching the alphabetic-like word pattern
    # e.g., ("Dr", "Smith", "arrived", "at", "He", "said", "Hello", "world")

# No cleanup required; tokenizer can be reused for multiple paragraphs.

### `sumy.nlp.tokenizers.Tokenizer.__init__` · *method*

## Summary:
Prepare this Tokenizer instance for use by normalizing the provided language identifier and selecting/initializing the language-appropriate sentence and word tokenizer objects stored on the instance.

## Description:
This initializer is executed when a Tokenizer is constructed, typically at the start of a text-processing pipeline step that requires language-aware tokenization (prior to calling to_sentences or to_words). It centralizes the logic needed to choose the correct tokenizer implementations so subsequent tokenization calls can assume fully-initialized tokenizer objects.

Why this logic is a dedicated method:
- Language normalization and tokenizer selection are non-trivial, reused operations that may involve loading external data (NLTK punkt pickles) or selecting special, language-specific tokenizer classes. Running this once in __init__ avoids repeating expensive/fragile setup in other methods.

Known callers / lifecycle context:
- Any component that constructs a Tokenizer for processing text (examples: summarizers, extractors, or tests) will call this constructor as part of constructing a Tokenizer object. The constructor runs once per instance before methods like to_sentences and to_words are called.

## Args:
    language (str): Required.
        - A language identifier accepted by normalize_language. Accepts full language names (e.g., "english"), or ISO codes such as alpha-2 ("en") or alpha-3 ("eng") that normalize_language may convert to a canonical language name.
        - The provided value is normalized (via normalize_language) and stored on the instance.
        - Common examples:
            - "en", "eng", or "english" -> normalized to a canonical form used by the Tokenizer.
            - "slovak" -> becomes "czech" for tokenizer selection due to LANGUAGE_ALIASES.

## Returns:
    None: As an initializer, it does not return a value. On successful completion, the instance fields necessary for tokenization are set.

## Raises:
    LookupError: Propagated if sentence-tokenizer selection fails for a non-special language. Specific behavior:
        - If the normalized/aliased tokenizer_language is present in SPECIAL_SENTENCE_TOKENIZERS, selection succeeds without attempting to load external data.
        - Otherwise, __init__ calls _get_sentence_tokenizer which attempts to load NLTK punkt data via nltk.data.load(path). If this load raises LookupError (missing NLTK data) or zipfile.BadZipfile (corrupt data), _get_sentence_tokenizer re-raises a LookupError with an explanatory message. That LookupError propagates out of __init__.
    Notes:
        - __init__ does not catch these exceptions; callers should be prepared to handle LookupError when constructing Tokenizer for languages that rely on NLTK punkt data.

## State Changes:
    Attributes READ:
        - normalize_language (function): called to canonicalize the provided language identifier.
        - self.LANGUAGE_ALIASES (dict): consulted via .get(...) to map some languages to alternate tokenizer languages (e.g., "slovak" -> "czech").
        - self.SPECIAL_SENTENCE_TOKENIZERS (class dict): checked indirectly by _get_sentence_tokenizer to decide whether to use a special tokenizer.
        - self.SPECIAL_WORD_TOKENIZERS (class dict): checked indirectly by _get_word_tokenizer to decide whether to use a special word tokenizer.
        - self._get_sentence_tokenizer (method): invoked to obtain the sentence tokenizer instance.
        - self._get_word_tokenizer (method): invoked to obtain the word tokenizer instance.

    Attributes WRITTEN (with types and descriptions):
        - self._language (str): set to the normalized language identifier returned by normalize_language.
        - self._sentence_tokenizer (object): set to a tokenizer object that implements a .tokenize(text) method. Possible sources:
            - A language-specific tokenizer from SPECIAL_SENTENCE_TOKENIZERS (no external load).
            - An NLTK punkt tokenizer loaded via nltk.data.load for tokenizer_language (may involve file I/O and can raise LookupError).
        - self._word_tokenizer (object): set to a tokenizer object that implements a .tokenize(text) method. Possible sources:
            - A language-specific tokenizer from SPECIAL_WORD_TOKENIZERS.
            - A DefaultWordTokenizer() instance when no special word tokenizer is defined (current implementation path and not expected to raise during construction).

## Constraints:
    Preconditions:
        - The caller should supply a non-empty string accepted by normalize_language. Passing None or a non-string may cause normalize_language or subsequent lookups to behave unexpectedly.
        - If the resolved tokenizer_language is not covered by SPECIAL_SENTENCE_TOKENIZERS, the environment must have the appropriate NLTK punkt data installed (nltk_data/tokenizers/punkt/<language>.pickle), otherwise a LookupError will be raised.

    Postconditions:
        - self._language contains the normalized language identifier.
        - Tokenizers required by to_sentences and to_words are initialized on the instance:
            - self._sentence_tokenizer: ready to tokenize strings into sentences (via .tokenize).
            - self._word_tokenizer: ready to tokenize sentences into word-like tokens (via .tokenize).
        - If tokenizer selection failed (e.g., missing NLTK data for that language), an exception has been raised and the instance constructor did not complete successfully.

## Side Effects:
    - May read files from the local NLTK data installation when loading punkt tokenizers via nltk.data.load (file I/O).
    - Does not perform network I/O.
    - Does not mutate global state beyond reading class-level dictionaries. It only mutates instance attributes on self.

## Implementation call flow (explicit):
    1. language = normalize_language(language)
    2. self._language = language
    3. tokenizer_language = self.LANGUAGE_ALIASES.get(language, language)
    4. self._sentence_tokenizer = self._get_sentence_tokenizer(tokenizer_language)
        - If tokenizer_language in SPECIAL_SENTENCE_TOKENIZERS -> that special tokenizer is returned immediately.
        - Else -> attempt to load nltk.data.load("tokenizers/punkt/<tokenizer_language>.pickle"); failures produce LookupError.
    5. self._word_tokenizer = self._get_word_tokenizer(tokenizer_language)
        - If tokenizer_language in SPECIAL_WORD_TOKENIZERS -> that tokenizer is returned.
        - Else -> DefaultWordTokenizer() is returned (current behavior).

## Examples / Usage notes:
    - Constructing a Tokenizer for English or its code variants: supply "english", "en", or "eng"; normalize_language will resolve codes and __init__ will initialize the default NLTK-based tokenizers for English (assuming NLTK punkt data is installed).
    - For "slovak", the constructor uses LANGUAGE_ALIASES to select the "czech" tokenizer implementation.
    - To avoid LookupError on construction for non-special languages, ensure the appropriate NLTK punkt pickle for the language is available in the NLTK data directory.

### `sumy.nlp.tokenizers.Tokenizer.language` · *method*

## Summary:
Returns the tokenizer's configured language as a read-only, normalized string; does not modify object state.

## Description:
This property exposes the language value that was set when the Tokenizer was constructed (via Tokenizer.__init__). It is typically used by external callers to inspect which language the tokenizer was configured for (for example, when wiring/token selection or logging). Internal tokenization methods in this class generally access the underlying attribute _language directly, so this property primarily exists as the public, read-only accessor for external code and for nicer introspection.

Known callers and context:
- External client code and pipelines that need to check or log the Tokenizer's language after instantiation (e.g., before selecting language-specific processing steps).
- It is not required by the internal tokenization methods (to_sentences, to_words) which access the backing attribute directly; therefore the property is used for API clarity rather than internal mechanics.
- Lifecycle stage: called after Tokenizer(...) construction during configuration, validation, or runtime inspection; not part of the paragraph/sentence tokenization hot path.

Why a separate property:
- Provides a stable public getter and read-only view of the configured language without exposing the private attribute name.
- Keeps the public API consistent and allows future logic (validation, lazy computation) to be added to the accessor without changing callers.

## Args:
None.

## Returns:
str: The language identifier stored on the tokenizer instance.
- Typical values are canonical language names produced by normalize_language (examples: "english", "german", "chinese", "japanese"), matching the names used by the Tokenizer to select special tokenizers and NLTK punkt models.
- The exact returned string is the value of the private attribute self._language as set during __init__ (i.e., normalize_language(language) passed to the constructor).
- Edge cases: if the instance was not properly initialized and _language is absent, accessing this property will raise an AttributeError.

## Raises:
AttributeError: If the Tokenizer instance has not had __init__ run successfully and the private attribute _language does not exist. There are no other explicit exceptions raised by this accessor.

## State Changes:
Attributes READ:
- self._language

Attributes WRITTEN:
- None. This property does not modify any attributes.

## Constraints:
Preconditions:
- Tokenizer.__init__(language) must have been executed successfully so that self._language exists and reflects the normalized language.
- The language string is expected to be the normalized form produced by normalize_language used in __init__.

Postconditions:
- After calling this property, the Tokenizer instance remains unchanged.
- The returned value equals the internal self._language string (no copying or transformation occurs at access time).

## Side Effects:
- None. This accessor performs no I/O, logging, or external service calls and does not mutate objects outside self.

### `sumy.nlp.tokenizers.Tokenizer._get_sentence_tokenizer` · *method*

## Summary:
Returns a sentence-level tokenizer object appropriate for the requested language by either selecting a predefined special-case tokenizer or loading the corresponding NLTK punkt resource; the method itself does not mutate the Tokenizer instance.

## Description:
Known callers and lifecycle:
- Tokenizer.__init__: Invoked during Tokenizer construction to obtain the sentence tokenizer. Tokenizer.__init__ normalizes the language and resolves aliases before calling this method; the returned tokenizer is typically assigned to self._sentence_tokenizer.
- Tokenizer.to_sentences: Uses the returned tokenizer to split text into sentences. Note: to_sentences may mutate the returned tokenizer (it updates _params.abbrev_types when the tokenizer exposes a `_params` attribute), so callers should expect that the returned tokenizer instance can be further configured after retrieval.

Why this is a separate method:
- Encapsulates selection logic (special-case tokenizers vs. NLTK punkt resources) and centralized error handling for missing or corrupt NLTK data files.
- Keeps __init__ concise, makes selection logic testable in isolation, and provides a single override point for subclasses that need custom selection behavior.

## Args:
    language (str or str-like):
        - A normalized language identifier (examples: 'english', 'german', 'japanese', 'chinese', 'korean', 'hebrew', 'arabic', 'ukrainian', 'greek').
        - The method converts this value with the module helper to_string before constructing the resource path; callers (Tokenizer.__init__) are expected to pass a language that has already been normalized and alias-resolved via normalize_language and LANGUAGE_ALIASES.

## Returns:
    tokenizer (object):
        - A language-appropriate tokenizer object.
        - Two possible outcomes:
            1. A special-case tokenizer from Tokenizer.SPECIAL_SENTENCE_TOKENIZERS[language] (returned immediately for keys listed below). Examples include nltk.RegexpTokenizer instances and language-specific tokenizer classes such as KoreanSentencesTokenizer.
            2. An NLTK tokenizer loaded with nltk.data.load(path), where path is constructed as "tokenizers/punkt/<language>.pickle" (both the format string and the language token are passed through to_string before formatting).
        - The returned object must implement .tokenize(text) since Tokenizer.to_sentences calls this method. Optionally the tokenizer may have a _params attribute with an abbrev_types mapping that Tokenizer.to_sentences extends.

## Known SPECIAL_SENTENCE_TOKENIZERS keys:
    - 'ukrainian', 'hebrew', 'japanese', 'chinese', 'korean', 'greek', 'arabic'
    (If language matches one of these keys, the corresponding object is returned immediately.)

## Raises:
    LookupError:
        - Raised when an NLTK punkt resource cannot be loaded or is corrupt.
        - This method catches both LookupError and zipfile.BadZipfile exceptions raised by nltk.data.load(path) and re-raises a LookupError with the message:
          "NLTK tokenizers are missing or the language is not supported.\nOriginal error was:\n" followed by the original exception's string representation.
        - Trigger conditions:
            * The punkt resource for the requested language (tokenizers/punkt/<language>.pickle) is not installed or discoverable by nltk.data.
            * The resource exists but is corrupt/unreadable, causing zipfile.BadZipfile while NLTK attempts to load it.

## State Changes:
    Attributes READ:
        - self.SPECIAL_SENTENCE_TOKENIZERS (class attribute): consulted to check for special-case tokenizers.
    Attributes WRITTEN:
        - None. The method returns a tokenizer but does not assign or mutate self attributes. (Callers commonly assign the return value to self._sentence_tokenizer.)

## Constraints:
    Preconditions:
        - The caller should provide a language string that is already normalized and alias-resolved (Tokenizer.__init__ performs normalize_language and the LANGUAGE_ALIASES lookup prior to calling this method).
        - The _compat.to_string helper must be available and accept the provided language value; its behavior affects the type (text or bytes) of the constructed path.
        - The nltk package (and its data loading mechanism) must be importable in the runtime environment for languages that are not in SPECIAL_SENTENCE_TOKENIZERS.

    Postconditions:
        - On success, the method returns a tokenizer object appropriate for the language that supports .tokenize(text).
        - On failure to find or load the NLTK punkt resource, the method raises a LookupError and no tokenizer is returned.

## Side Effects:
    - I/O: Calling nltk.data.load(path) may perform filesystem/resource I/O to locate and read the punkt pickle file.
    - Exceptions: May raise LookupError (re-raised with augmented message); underlying exceptions from nltk.data.load or zipfile are not propagated directly but their string is included in the raised LookupError message.
    - External mutation: The method itself does not mutate external objects, but the tokenizer returned may be mutated later by Tokenizer.to_sentences (it may update tokenizer._params.abbrev_types if present).

## Implementation notes (for reimplementation):
    - Path construction: the code builds the resource path with two conversions via to_string:
        path = to_string("tokenizers/punkt/%s.pickle") % to_string(language)
      Ensure to_string is used both on the format string and on the language token to preserve the repository's compatibility policy for text vs bytes.
    - Loading: Use nltk.data.load(path) to obtain the punkt tokenizer. Catch LookupError and zipfile.BadZipfile and re-raise a LookupError with the human-facing message shown above to keep error reporting consistent with the rest of the Tokenizer class.

## Example usage (behavioral):
    - If language == 'japanese' (a special-case key), this method returns the pre-registered RegexpTokenizer for Japanese without calling NLTK.
    - If language == 'english' and the resource tokenizers/punkt/english.pickle is present, the method returns the loaded NLTK PunktSentenceTokenizer.
    - If the english pickle is missing or corrupt, the method raises LookupError with the original error text appended.

### `sumy.nlp.tokenizers.Tokenizer._get_word_tokenizer` · *method*

## Summary:
Selects and returns a word-level tokenizer object appropriate for the specified language; intended for assignment to Tokenizer._word_tokenizer (the method itself does not modify the Tokenizer instance).

## Description:
Known callers:
- Tokenizer.__init__: invoked during Tokenizer construction to obtain the word tokenizer used by to_words immediately after language normalization and sentence-tokenizer selection.

Context / lifecycle stage:
- Called at initialization time to decide which tokenizer implementation will be used for subsequent word-tokenization operations.

Why this is a separate method:
- Centralizes language-to-tokenizer selection logic so the constructor remains concise.
- Makes it easy to override selection behavior in subclasses or to extend supported languages by updating SPECIAL_WORD_TOKENIZERS.
- Improves testability by isolating the lookup/fallback behavior.

## Args:
    language (str): Normalized language identifier (e.g., 'english', 'japanese'). Tokenizer.__init__ calls normalize_language before passing the value; callers should pass a normalized string.

## Returns:
    object: A tokenizer instance that implements a tokenize(text) method.
    - If language is present in self.SPECIAL_WORD_TOKENIZERS, returns the mapping value for that language (typically a pre-instantiated language-specific tokenizer).
    - Otherwise returns a newly constructed DefaultWordTokenizer() instance.
    - Edge cases:
        - The returned object will be whatever the mapping contains; callers should only rely on the public tokenizer interface (tokenize).
        - The method never intentionally returns None.

## Raises:
    - This method itself does not raise any specific exceptions in normal operation.
    - Lookup of a key in self.SPECIAL_WORD_TOKENIZERS is a simple dictionary access; it will not raise unless the mapping object is malformed.
    - Constructing DefaultWordTokenizer() is a trivial, non-I/O operation (the DefaultWordTokenizer is a stateless wrapper around nltk.word_tokenize) and does not raise by design.
    - Errors related to tokenization (for example, missing NLTK resources or invalid input types) occur when the returned tokenizer's tokenize method is later invoked; such errors are raised by that tokenizer implementation (e.g., by nltk.word_tokenize) and propagate to the caller at tokenization time, not during this selection method.

## State Changes:
Attributes READ:
    - self.SPECIAL_WORD_TOKENIZERS (membership check and retrieval)

Attributes WRITTEN:
    - None. The method does not modify self; callers are expected to assign the return value to an attribute (e.g., self._word_tokenizer).

## Constraints:
Preconditions:
    - language is expected to be a normalized language string (Tokenizer.__init__ normalizes before calling).
    - self.SPECIAL_WORD_TOKENIZERS must be a mapping from language strings to tokenizer instances.

Postconditions:
    - Returns a tokenizer object appropriate for the language.
    - Self remains unchanged; after the caller stores the returned tokenizer, Tokenizer.to_words will use it for tokenization.

## Side Effects:
    - May instantiate DefaultWordTokenizer() when no special tokenizer is registered; this construction is lightweight and performs no I/O.
    - No network, file, or external-service calls are performed by this method.
    - No mutation of objects outside self is performed by this method.

### `sumy.nlp.tokenizers.Tokenizer.to_sentences` · *method*

## Summary:
Converts a paragraph into a tuple of sentence strings by delegating to the configured sentence tokenizer, normalizing the input to unicode, optionally extending tokenizer abbreviation rules, and stripping surrounding whitespace from each resulting sentence.

## Description:
- Purpose and role:
    - Segments a single paragraph of text into individual sentences using this Tokenizer instance's underlying sentence-tokenizer object.
    - This is a focused utility method so sentence-tokenizer configuration (such as adding language-specific extra abbreviations) and input normalization are applied consistently in one place before tokenization.

- Typical callers and pipeline stage:
    - Called by higher-level NLP pipeline components that need sentence-level segmentation (for example: parsers, sentence extractors, summarizers, or any preprocessing stage that expects sentences).
    - Invoked at the sentence segmentation step immediately after paragraph-level text is obtained and before token-level processing.

- Why this logic is a separate method:
    - Keeps tokenizer configuration (extra abbreviations) and consistent unicode normalization in one location rather than duplicating that logic in many callers.
    - Encapsulates the contract: input -> normalized sentences (stripped), while allowing different underlying sentence tokenizers to be swapped in on the Tokenizer instance.

## Args:
    paragraph (str | bytes | object convertible to text):
        The paragraph to segment into sentences. The method accepts any object that the helper to_unicode(...) can convert into a native unicode/string type.

## Returns:
    tuple[str]:
        A tuple of sentence strings. Each sentence has been produced by the underlying tokenizer and then had leading and trailing whitespace removed.
        - If the underlying tokenizer returns an empty list (e.g., for an empty or whitespace-only paragraph), this method returns an empty tuple.
        - Returned strings are native text/unicode (same type as to_unicode produces in this runtime).

## Raises:
    - This method does not explicitly raise exceptions itself. However it may propagate exceptions raised by:
        - to_unicode(paragraph) if the conversion fails for the provided input type or encoding.
        - self._sentence_tokenizer.tokenize(...) if the configured tokenizer detects invalid input or encounters an internal error.
        - If the method attempts to update tokenizer parameters and those objects do not support the expected operations, attribute-related exceptions (AttributeError) or type errors may propagate.

## State Changes:
- Attributes READ:
    - self._sentence_tokenizer : the configured sentence tokenizer object (inspected to decide whether to update params and used to perform tokenization)
    - self.LANGUAGE_EXTRA_ABREVS : mapping of language -> iterable of extra abbreviation types (read to obtain extra abbreviations for this language)
    - self._language : language key used to lookup extra abbreviations

- Attributes WRITTEN / Mutated:
    - self._sentence_tokenizer._params.abbrev_types (if present):
        - When the underlying tokenizer object has a _params attribute, this method updates its abbrev_types using .update(...) with any language-specific additions.
        - Note: this mutates the tokenizer's internal parameters (a side-effect on the tokenizer object stored on self).

## Constraints:
- Preconditions (caller must ensure):
    - self._sentence_tokenizer must exist and implement a tokenize(text) method that accepts text produced by to_unicode(paragraph).
    - If the tokenizer exposes a _params attribute, it must have an abbrev_types attribute supporting .update(iterable) (e.g., a set or dict-like structure).
    - to_unicode(paragraph) must be able to convert the supplied paragraph argument to text. Supplying arbitrary non-text objects may raise during conversion.

- Postconditions (guarantees after call):
    - Returns a tuple of text strings with leading/trailing whitespace removed.
    - If applicable, the tokenizer's _params.abbrev_types will include any language-specific extra abbreviations present in self.LANGUAGE_EXTRA_ABREVS[self._language].
    - No other attributes on self are modified by this method.

## Side Effects:
- Mutates the internal state of the underlying sentence tokenizer by updating its _params.abbrev_types when _params exists — this is persistent on the tokenizer object and affects subsequent tokenizations.
- No I/O, network, or external service calls are performed by this method itself; any side effects arise from the behavior of the injected tokenizer implementation.

### `sumy.nlp.tokenizers.Tokenizer.to_words` · *method*

## Summary:
Produce a tuple of validated word tokens from a sentence by converting the input to text, running the configured word tokenizer, and filtering out tokens that are not recognized as words; the method does not modify the tokenizer instance.

## Description:
This method is used during the word-tokenization step of a text-processing pipeline immediately after sentences have been segmented (for example, after calling Tokenizer.to_sentences). Typical callers include summarizers, feature extractors, and any component that needs language-aware word tokens for indexing, analysis, or further NLP processing. The logic is separated into this method to (1) centralize Unicode normalization, (2) encapsulate delegation to the language-appropriate tokenizer instance (self._word_tokenizer), and (3) apply a single, consistent validation rule (Tokenizer._is_word) across all tokens.

Known callers / lifecycle stage:
- Components that operate at the sentence level call this to obtain word tokens from each sentence (e.g., summarizers, extractors, tests).
- It is typically invoked after text has been split into sentences by Tokenizer.to_sentences.

Why this is a dedicated method:
- Avoids duplicating conversion, tokenization, and filtering logic across the codebase.
- Ensures consistent application of the word validation predicate and makes unit testing of the pipeline step straightforward.

## Args:
    sentence (str or unicode): The sentence to tokenize. The argument is converted using to_unicode() before tokenization; callers may pass native Python strings. Supplying an object that to_unicode cannot convert will raise an exception propagated from to_unicode.

## Returns:
    tuple[str]: A tuple of Unicode text tokens that passed Tokenizer._is_word filtering.
    - Order-preserving: tokens appear in the same order produced by self._word_tokenizer.tokenize.
    - Duplicates preserved: if the tokenizer returns repeated tokens, duplicates remain in the result (subject to filtering).
    - Empty result: returns an empty tuple () when no tokens pass the filter.
    - Token content: returned tokens are exactly as produced by the underlying tokenizer (no additional normalization is performed here beyond to_unicode on the input).

## Raises:
    - Exceptions raised by to_unicode(sentence) (for example, TypeError for incompatible types) are propagated.
    - Exceptions raised by self._word_tokenizer.tokenize(text) are propagated (tokenizers may raise ValueError, TypeError, or tokenizer-specific exceptions).
    - Exceptions raised by Tokenizer._is_word when evaluating a token (for example, TypeError if a tokenizer returns a non-text object incompatible with the regex engine) are propagated.
    - The method does not raise additional exceptions itself; it forwards errors from the conversion, tokenizer, and predicate.

## State Changes:
    Attributes READ:
        - self._word_tokenizer: used via its tokenize(text) method to produce candidate tokens.
        - Tokenizer._WORD_PATTERN / self._is_word: consulted (indirectly) for validating each token.
        - to_unicode (module-level helper): called to convert the input sentence to a Unicode string.
    Attributes WRITTEN:
        - None. The method does not modify any instance or class attributes.

## Constraints:
    Preconditions:
        - The Tokenizer instance must have been initialized so self._word_tokenizer exists (this is ensured by Tokenizer.__init__).
        - The provided sentence must be convertible to a Unicode/text string by to_unicode.
        - The underlying word tokenizer must accept a text string in its tokenize method and return an iterable of tokens.

    Postconditions:
        - The returned tuple contains only tokens for which Tokenizer._is_word(token) returned True.
        - The Tokenizer instance and global state are unchanged by this method itself (aside from effects possibly caused by the underlying tokenizer implementation).

## Side Effects:
    - Direct: calls to to_unicode() and self._word_tokenizer.tokenize(); no file I/O or network I/O performed by this method itself.
    - Indirect: any side effects of the underlying word tokenizer (for example, caching, logging, or modification of external objects) may occur and are not controlled by this method.

## Example (illustrative):
    - Input: sentence = "Hello, world!"
      Underlying tokenizer might produce: ["Hello", ",", "world", "!"]
      After filtering with _is_word, returns: ("Hello", "world")
    - Input: sentence = "O'Reilly is here."
      Possible return: ("O'Reilly", "is", "here")

### `sumy.nlp.tokenizers.Tokenizer._is_word` · *method*

## Summary:
Checks whether a token should be considered a valid word by matching it against the class-level word regular expression; this is a pure predicate and does not modify tokenizer state.

## Description:
This predicate is applied to candidate tokens produced by the configured word tokenizer and is used to filter out non-word tokens before returning results. Known callers:
- Tokenizer.to_words: used as the filtering predicate in tuple(filter(self._is_word, words)). It runs immediately after word tokenization in the sentence-to-words pipeline.

Why this is a separate method:
- Centralizes the word-validation logic so the same rule (_WORD_PATTERN) is consistently applied across the tokenizer.
- Makes the test reusable, overrideable, and easier to unit-test independently of tokenizer implementations.
- Implemented as a static method because it relies solely on the class-level compiled pattern (Tokenizer._WORD_PATTERN) rather than instance-specific state.

## Args:
    word (str): A single token string to test. The method expects a text string (str/unicode). Tokens are typically produced by the word tokenizer and are usually normalized/decoded to Unicode by the caller.

## Returns:
    bool: True if the token matches Tokenizer._WORD_PATTERN, False otherwise.
    Edge-case behavior:
    - The empty string returns False.
    - Tokens starting with a digit, underscore, or other non-letter character return False.
    - Tokens containing digits anywhere return False (the pattern excludes digits).
    - Tokens containing only letters, or letters with internal apostrophes or hyphens that conform to the pattern, return True.

## Raises:
    TypeError: If `word` is not a string type compatible with the compiled regular expression (for example, passing None or a bytes object when the pattern expects a str). This arises from the underlying regex engine when match() is called with an inappropriate type.

## State Changes:
    Attributes READ:
        - Tokenizer._WORD_PATTERN (class attribute): the compiled regular expression used for matching.
    Attributes WRITTEN:
        - None. The method does not modify instance or class state.

## Constraints:
    Preconditions:
        - Tokenizer._WORD_PATTERN must be a compiled regular expression object with a match() method (the class defines it as such).
        - `word` should be a text string (preferably Unicode); callers normally ensure this by converting input with to_unicode before tokenization.
    Postconditions:
        - The method returns a boolean value and leaves tokenizer state unchanged.

## Side Effects:
    - None. No I/O, no network, and no mutations of external objects occur.

## Regex explanation (precise behavior):
    - Pattern: ^[^\W\d_](?:[^\W\d_]|['-])*$ (compiled with re.UNICODE)
    - Interpretation:
        * ^ … $ anchors the match to the entire token.
        * [^\W\d_] selects a character that is not a "non-word" character, not a digit, and not underscore — effectively a Unicode letter (so the token must start with a letter).
        * (?:[^\W\d_]|['-])* allows zero or more characters that are either letters (same class as above) or an internal apostrophe (') or hyphen (-).
    - Practical consequence: words must start with a letter; subsequent characters may be letters, apostrophes, or hyphens; digits and underscores are disallowed anywhere.

## Examples:
    - "Hello"     -> True
    - "O'Reilly"  -> True
    - "co-operate"-> True
    - "don't"     -> True
    - "123abc"    -> False
    - "_hidden"   -> False
    - ""          -> False
    - "a2b"       -> False

