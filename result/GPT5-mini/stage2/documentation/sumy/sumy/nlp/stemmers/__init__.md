# `__init__.py`

## `sumy.nlp.stemmers.__init__.null_stemmer` · *function*

## Summary:
Converts the input to the module's canonical text type (unicode) and returns a lower-cased string — a simple "no-op" stemmer suitable as a fallback.

## Description:
Known callers and usage context:
    - In the current repository snapshot, there are no guaranteed direct callers declared in this file. The function is designed to be used wherever code expects a stemmer callable (callable that accepts a single token-like value and returns a string). Typical usage is as a default or fallback stemmer passed into tokenization/stemming pipelines or set as the language-agnostic stemmer when language-specific stemmers are unavailable.
    - The function is a minimal, pluggable implementation of the stemmer interface so higher-level code can uniformly invoke a stemmer without conditional logic.

Why this logic is a standalone function:
    - Encapsulates the "normalize to unicode and lowercase" policy so callers can treat it as a standard stemmer implementation.
    - Centralizes conversion to the module's canonical text type by delegating to the compatibility helper, avoiding repeated decoding/lowercasing logic across the codebase.
    - The function performs a lazy import of the compatibility helper to avoid import-time coupling and potential circular imports.

## Args:
    object (any):
        - The value to be converted and lower-cased.
        - Expected inputs:
            * unicode (module canonical text type): returned lower-cased.
            * bytes: decoded to unicode (UTF-8) by to_unicode, then lower-cased.
            * Any other Python object: passed to to_unicode for conversion; the result is then lower-cased.
        - Note: the parameter name is exactly "object" (it shadows the built-in name).

## Returns:
    unicode:
        - The lower-cased unicode text corresponding to the input.
        - Guarantees:
            * The returned value is the module's canonical text type (as produced by to_unicode) and has .lower() applied.
        - Examples of outcomes:
            * "Running" -> "running"
            * b'CAF\xc3\x89' (UTF-8 bytes for "CAFÉ") -> "café"
            * 123 -> "123" (assuming to_unicode returns "123")

## Raises:
    - UnicodeDecodeError:
        * Trigger: input is bytes and cannot be decoded as UTF-8 by the to_unicode helper.
    - Any exception raised by to_unicode or its delegated conversion logic (for example, exceptions from instance_to_unicode or user-defined conversion hooks).
    - AttributeError:
        * Trigger: if to_unicode violates its contract and returns a value that does not implement .lower(); this is unlikely if to_unicode functions correctly but documented for completeness.
    - Behavior: null_stemmer does not catch these exceptions — they propagate to the caller.

## Constraints:
    Preconditions:
        - The compatibility helper to_unicode (imported inside the function) must exist and adhere to its contract: returning a unicode text type for non-bytes and properly decoding bytes using UTF-8 or delegating to instance conversion.
        - Callers should assume any bytes supplied are UTF-8 encoded; otherwise, UnicodeDecodeError may occur.
    Postconditions:
        - On successful return, the caller receives a unicode value that is the lowercase form of the input's text representation.
        - No module-level state or external resources are modified.

## Side Effects:
    - None directly: the function performs no I/O, network calls, or global state mutation.
    - Indirect side effects are possible if to_unicode delegates to user-defined conversion methods that have side effects (those side effects originate from the conversion routines, not from null_stemmer itself).

## Control Flow:
flowchart TD
    A[Start: null_stemmer(object)] --> B[Import to_unicode from ..._compat (lazy import)]
    B --> C[Call to_unicode(object)]
    C --> D{to_unicode succeeded?}
    D -->|Yes| E[Call .lower() on the returned unicode]
    E --> F[Return lower-cased unicode]
    D -->|No (exception)| G[Propagate exception to caller]

## Examples:
- Plain text input:
    result = null_stemmer("Running")       # returns "running"

- Bytes input (UTF-8):
    result = null_stemmer(b'CAF\xc3\x89') # returns "café"

- Arbitrary object:
    result = null_stemmer(42)             # returns "42" (if to_unicode yields "42")

- Handling decoding errors:
    try:
        result = null_stemmer(b'\xff')    # may raise UnicodeDecodeError
    except UnicodeDecodeError:
        result = ""                       # fallback handling

- Typical fallback usage:
    # Pass as a default stemmer when configuring a pipeline that accepts a stemmer callable
    pipeline.set_stemmer(null_stemmer)

## `sumy.nlp.stemmers.__init__.Stemmer` · *class*

*No documentation generated.*

### `sumy.nlp.stemmers.__init__.Stemmer.__init__` · *method*

## Summary:
Initializes the Stemmer instance for the requested language by selecting and storing an appropriate stemmer callable on the object (self._stemmer). If a special or built-in stemmer is available it is used; otherwise a LookupError is raised.

## Description:
Known callers and lifecycle context:
    - Typically called when a text-processing pipeline or summarizer component is being configured or constructed and needs a language-specific stemmer (e.g., during pipeline initialization or when a user requests a Stemmer for a particular language).
    - Call sites are expected to create a Stemmer(language) once per pipeline or per language and then call the stored stemmer callable via self._stemmer(token) when stemming tokens.

Why this is a separate method:
    - Encapsulates the language-selection and instantiation logic for stemmers in a single place so the rest of the codebase can rely on a uniform attribute (self._stemmer) that is always set to a callable.
    - Keeps initialization logic (normalization of language names, fallback behavior, special-case handling, and dynamic class lookup/instantiation) out of higher-level code, avoiding duplication and conditional branching elsewhere.

## Args:
    language (str):
        - The requested language name or code (string-like). It is first passed through normalize_language(language) which standardizes the representation.
        - Allowed values: any value accepted by normalize_language. Practically, values should map to either:
            * a key (lower-cased) in self.SPECIAL_STEMMERS, or
            * a language whose capitalized form + "Stemmer" names a class available on the module referenced as nltk_stemmers_module (e.g., "English" -> "EnglishStemmer").
        - This argument is required; there is no default.

## Returns:
    None
        - The method returns None like any Python constructor, but as a side-effect it sets self._stemmer to a callable (see Postconditions).

## Raises:
    LookupError:
        - Raised when no appropriate stemmer class exists on nltk_stemmers_module for the normalized language.
        - Exact trigger: getattr(nltk_stemmers_module, stemmer_classname) raises AttributeError (meaning the expected class name does not exist), which is caught and re-raised as LookupError with the message "Stemmer is not available for language %s." % language.

    Propagated exceptions (not explicitly caught):
        - Any exception raised by normalize_language(language) (e.g., TypeError if it rejects the provided type).
        - Any exception raised when accessing self.SPECIAL_STEMMERS if that attribute is missing or not subscriptable (e.g., AttributeError, TypeError).
        - Exceptions raised by stemmer_class() during instantiation, or by attribute access when retrieving .stem from the instance.
        - NameError if required globals (e.g., null_stemmer or nltk_stemmers_module) are not defined at runtime.

## State Changes:
    Attributes READ:
        - self.SPECIAL_STEMMERS (used to check for and retrieve language-specific custom stemmer callables)
    Attributes WRITTEN:
        - self._stemmer (assigned either to null_stemmer, a callable from self.SPECIAL_STEMMERS, or the .stem callable of an instantiated NLTK stemmer class)

## Constraints:
    Preconditions:
        - normalize_language is available and returns a string-like normalized language token.
        - self.SPECIAL_STEMMERS, if present, should be a mapping that accepts lower-cased language keys and yields a stemmer callable when indexed.
        - The global/module symbol nltk_stemmers_module must reference a module object that may expose classes named <Language>Stemmer (capitalized language + "Stemmer").
        - null_stemmer must be available as a callable fallback.

    Postconditions:
        - On successful completion (no exception raised), self._stemmer is a callable intended to accept a single token (string-like) and return the stemmed string representation of that token.
        - If the language matched a special stemmer, self._stemmer refers to the value from self.SPECIAL_STEMMERS[language.lower()].
        - If the language did not match a special stemmer, self._stemmer refers to stemmer_class().stem where stemmer_class is the class obtained from nltk_stemmers_module using the constructed class name.

## Side Effects:
    - Instantiates a stemmer class (stemmer_class()) in the fallback/NLTK-path; that class's __init__ may itself perform work (side-effects such as internal state initialization). No file I/O or network I/O is performed by this method itself.
    - No global state is modified by this method other than the instance attribute self._stemmer.
    - No exceptions are swallowed except AttributeError from getattr on nltk_stemmers_module which is converted to LookupError; all other exceptions propagate to the caller.

### `sumy.nlp.stemmers.__init__.Stemmer.__call__` · *method*

## Summary:
Delegates stemming of a single token to the configured underlying stemmer and returns the stemmed form without modifying the Stemmer instance state.

## Description:
This method allows a Stemmer instance to be used like a function: calling the instance with a word forwards the call to the concrete stemmer function or method selected during Stemmer construction.

Known callers and typical context:
- Any text-processing code that needs to obtain a stem for an individual token can call a Stemmer instance directly (for example, token normalization steps in a pipeline, feature extraction, or summarization preprocessing).
- It is used at runtime after a Stemmer has been constructed with a language; the Stemmer.__init__ selects an appropriate callable and assigns it to self._stemmer. This method is invoked during token-level processing phases when each token must be converted to its stem.

Why this is its own method:
- Exposes a concise, idiomatic callable interface (instance(...) syntax) so callers need not reference internal attributes.
- Keeps the delegation logic centralized and minimal (single-point dispatch) rather than duplicating calls to different stemmer functions throughout the codebase.
- Encapsulates the behavior so changing how the underlying stemmer is stored or invoked requires modifying only this method.

## Args:
    word (str or unicode-like): The token to be stemmed. The method does no validation itself; it forwards the value to the underlying stemmer callable. The exact accepted types/encoding depend on the configured stemmer implementation (commonly str/unicode).

## Returns:
    object: The return value is whatever the configured underlying stemmer callable returns for the given input. In practice this is typically a string (the stemmed form of the input token), but it may vary if a custom stemmer is used. No post-processing is applied by this method.

## Raises:
    TypeError: If self._stemmer is not callable, Python will raise a TypeError when attempting to call it.
    Any exception raised by the underlying stemmer callable: this method does not catch exceptions; they propagate to the caller (e.g., ValueError, UnicodeError, or other implementation-specific exceptions raised by special stemmers).

## State Changes:
    Attributes READ:
        self._stemmer
    Attributes WRITTEN:
        None — the method does not modify any attribute on self.

## Constraints:
    Preconditions:
        - The Stemmer instance must have been initialized so that self._stemmer is set to a callable (this is the responsibility of Stemmer.__init__).
        - The provided word must be suitable for the underlying stemmer (commonly a text string in the expected encoding/format).
    Postconditions:
        - No mutation to the Stemmer instance occurs.
        - The method returns the direct result of invoking the underlying stemmer callable with the provided word.

## Side Effects:
    - No direct I/O or external service calls are made by this method itself.
    - Side effects (if any) are those performed by the underlying stemmer callable; this method merely forwards the argument and result.

