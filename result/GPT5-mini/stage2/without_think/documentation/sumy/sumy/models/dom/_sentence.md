# `_sentence.py`

## `sumy.models.dom._sentence.Sentence` · *class*

## Summary:
Represents a single sentence (or heading) of text together with a tokenizer; provides a cached list of word tokens and value semantics (equality, hashing, text representation).

## Description:
The Sentence class encapsulates a piece of text that is treated as an atomic sentence in the document model. It is typically instantiated by higher-level parsers or DOM builders that split documents into sentence objects and supply a tokenizer capable of converting sentence text into words.

Use cases:
- Hold the original text of a sentence while exposing a lazily-computed, cached tokenization via the words property.
- Distinguish headings from normal sentences via the is_heading flag.
- Serve as a hashable, comparable object for sets, dictionaries, or equality checks in algorithms that operate on sentence objects.

Responsibilities and boundaries:
- Responsibility: store sentence text, remember whether it is a heading, and lazily expose tokenized words via the provided tokenizer.
- Boundary: The class does not perform tokenization itself; it delegates tokenization to the supplied tokenizer object. It does not perform I/O, text normalization beyond stripping outer whitespace, or persist lifecycle management.

Known callers/factories:
- Document/DOM builders that produce Sentence instances from parsed text (not shown here).
- Any summarizer or processing pipeline that needs to iterate sentences and access tokens.

## State:
Attributes (private; stored in __slots__):
- _text (str)
  - Type: unicode/str
  - Value: the original sentence text coerced through to_unicode(...) and stripped of leading/trailing whitespace.
  - Invariant: _text is a str-like object and does not contain leading/trailing whitespace (unless to_unicode produces such content).
- _tokenizer (object)
  - Type: an object providing a method to_words(text) -> sequence
  - Constraint: must implement to_words(text). The class calls _tokenizer.to_words(self._text); if that method is missing or raises, words access will propagate that exception.
- _is_heading (bool)
  - Type: bool
  - Value: True when the sentence should be treated as a heading; False otherwise.
  - Invariant: stored as a bool (coerced in __init__).
- _cached_property_words (implementation detail)
  - Type: varies (depends on cached_property implementation)
  - Purpose: reserved slot name used by the cached_property mechanism to store the computed words for the words property. Presence in __slots__ prevents accidental dynamic attribute creation and supports caching.

Class invariants:
- The tuple (bool(_is_heading), _text) uniquely identifies the Sentence for __eq__ and __hash__ purposes.
- After first access, words property value is expected to remain stable for the lifetime of the Sentence (no method mutates _text or _is_heading).

## Lifecycle:
Creation:
- Call Signature: Sentence(text, tokenizer, is_heading=False)
  - text: required; a text-like object that will be coerced via to_unicode(text).strip(). Caller should provide meaningful textual content (str/unicode).
  - tokenizer: required; an object implementing to_words(text) that returns a sequence/list of tokens.
  - is_heading: optional boolean flag (default False); any truthy value will be coerced to bool.

Usage:
- Typical flow:
  1. Instantiate Sentence with text and tokenizer.
  2. Read sentence._text implicitly by using str() or unicode() representations, or use the object in contexts where __repr__ is invoked.
  3. Access sentence.words to obtain the tokenization. The first access invokes tokenizer.to_words(self._text) and subsequent accesses return the cached result (cached_property).
  4. Use sentence.is_heading property to branch logic for headings vs normal sentences.
  5. Use equality (__eq__), inequality (__ne__), and hashing (__hash__) to compare or store Sentence instances in sets/dicts.

- Ordering and required sequencing:
  - No explicit ordering is required aside from creating the object before reading properties.
  - Accessing words before providing a valid tokenizer will raise an error from the tokenizer call.

Destruction:
- No explicit cleanup is required. Sentence does not hold external resources; it relies on normal Python garbage collection. It is not a context manager and has no close or dispose method.

## Method Map:
- Diagram (Mermaid flowchart showing dependencies and typical call flow)
graph TD
    A[Sentence.__init__] --> B[_text assigned via to_unicode(...).strip()]
    A --> C[_tokenizer stored]
    A --> D[_is_heading stored]
    E[access .words] --> F[_tokenizer.to_words(_text)]
    F --> G[cached result stored (cached_property)]
    H[access .is_heading] --> D
    I[__eq__] --> J[assert isinstance(Sentence)]
    I --> K[compare _is_heading and _text]
    L[__hash__] --> M[hash((_is_heading, _text))]
    N[__repr__] --> O["Heading" if _is_heading else "Sentence"]
    N --> P[self.__str__()]

Note: the words property delegates to the tokenizer.to_words method; cached_property ensures F is executed at most once and the result reused.

## Methods / Properties (behavioral summary):
- __init__(text, tokenizer, is_heading=False)
  - Behavior: stores the provided tokenizer; coerces text into unicode then strips whitespace and stores into _text; coerces is_heading to bool and stores into _is_heading.
  - Side-effects: may raise exceptions thrown by to_unicode(text) if text cannot be coerced.
- words (cached_property)
  - Behavior: on first access calls self._tokenizer.to_words(self._text) and returns it. Subsequent accesses return the cached value.
  - Return type: whatever the tokenizer returns (typically list[str] or sequence[str]).
  - Side-effects: may raise AttributeError if tokenizer has no to_words, or propagate exceptions raised by tokenizer.to_words.
- is_heading (property)
  - Behavior: returns the boolean flag set at construction.
- __eq__(other)
  - Behavior: asserts that other is a Sentence (AssertionError if not). Then returns True iff both _is_heading and _text are equal (note: _is_heading compared with 'is' identity and _text compared with ==).
  - Note: the assert will raise AssertionError when other is not a Sentence (asserts can be disabled with -O).
- __ne__(other)
  - Behavior: returns the negation of __eq__(other).
- __hash__()
  - Behavior: returns hash((_is_heading, _text)). Allows use in hashed collections consistent with equality.
- __unicode__() / string representation
  - Behavior: returns the underlying text (_text).
- __repr__()
  - Behavior: returns a human-readable representation of the form "<Heading: ...>" or "<Sentence: ...>" depending on is_heading. It calls self.__str__() for the textual part.

## Raises:
- __init__:
  - Any exception raised by to_unicode(text) (e.g., TypeError) will propagate. The class does not catch conversion errors.
- words:
  - AttributeError if tokenizer does not implement to_words.
  - Any exception raised by tokenizer.to_words(text) will propagate to the caller.
- __eq__:
  - AssertionError if the passed value is not an instance of Sentence (assert is used).
  - Note: because assertion is used rather than explicit type checking and exception, this check can be disabled when Python runs with optimizations (-O).
- No other methods explicitly raise exceptions in the class itself.

## Example:
- Creation and typical usage (pseudo-code, showing expected interactions):
1) Instantiate with a tokenizer that exposes to_words(text):
   tokenizer = SomeTokenizer()  # must implement to_words(text) -> list[str]
   s = Sentence("  This is a sentence.  ", tokenizer)  # whitespace will be stripped

2) Access tokenized words:
   tokens = s.words  # calls tokenizer.to_words("This is a sentence.") on first access, then caches result

3) Check heading flag:
   if s.is_heading:
       handle_heading(s)

4) Use as dict key or in sets:
   sentences_set = {s}  # uses __hash__ and __eq__

5) Compare sentences:
   s2 = Sentence("This is a sentence.", tokenizer)
   s == s2  # True (same text and default is_heading False)

Notes and recommendations for implementers:
- Provide a tokenizer whose to_words method is stable and returns an immutable or stable sequence if Sentence instances are used in long-lived caches.
- Avoid mutating the Sentence._text or Sentence._is_heading after creation; the class design assumes immutability for equality/hash stability.
- Be aware the equality method uses an assertion to enforce type: callers should generally pass Sentence instances to avoid an AssertionError in non-optimized runs.

### `sumy.models.dom._sentence.Sentence.__init__` · *method*

## Summary:
Initializes a Sentence instance by storing a normalized unicode text string, retaining a tokenizer reference, and recording whether the sentence is a heading — establishing the immutable-ish internal state used by the rest of the Sentence API.

## Description:
This constructor is invoked whenever a Sentence object is created to represent a piece of text in the document model. In this codebase, Sentence instances are typically constructed by higher-level DOM/model-building code under sumy.models.dom when converting parsed document fragments into Sentence objects.

The method centralizes minimal normalization and coercion logic (text -> unicode and trimmed; is_heading -> bool) so that other methods and properties (for example, the cached words property) can rely on a consistent internal representation. The constructor intentionally does not perform tokenizer-interface validation or heavier parsing; those responsibilities belong to tokenizer implementations and the code that orchestrates sentence creation.

Example (descriptive):
- Creating a sentence with text "  Hello.  " yields self._text == "Hello." and self._is_heading == False.
- Creating a sentence with is_heading truthy sets self._is_heading to True.

## Args:
    text (any): Raw sentence content passed through to_unicode(text) and then .strip(). The exact accepted inputs and conversion behavior depend on the to_unicode implementation imported from _compat. After conversion, leading and trailing whitespace are removed; a whitespace-only input becomes an empty string.
    tokenizer (object): Reference to a tokenizer object stored on the instance. The constructor does not call any tokenizer methods; later use of the tokenizer is expected by Sentence.words which calls tokenizer.to_words(self._text). No interface checks are performed here.
    is_heading (bool, optional): Flag indicating heading status. Defaults to False. The value is coerced via bool(is_heading) so any truthy/falsy input will be normalized to True/False.

## Returns:
    None: As an initializer, __init__ returns None. On success, the instance attributes listed under State Changes are set.

## Raises:
    Any exception raised by to_unicode(text) or by calling .strip() on the result will propagate out of __init__. No exceptions are explicitly raised in this method. Examples of propagated errors:
        - TypeError or AttributeError if the object returned by to_unicode does not support .strip()
        - Any custom exception thrown by to_unicode when given an unsupported input
    The constructor itself does not catch or wrap these exceptions.

## State Changes:
    Attributes READ:
        - None (no existing self.* attributes are read)
    Attributes WRITTEN:
        - self._text: set to the result of to_unicode(text).strip() (a unicode string with no leading/trailing whitespace; may be empty)
        - self._tokenizer: set to the tokenizer reference provided
        - self._is_heading: set to bool(is_heading)
    Notes:
        - The class defines __slots__ = ("_text", "_cached_property_words", "_tokenizer", "_is_heading",) so no other instance attributes can be added dynamically.
        - The cached attribute _cached_property_words is not initialized here; it will be set when the cached_property words is accessed.

## Constraints:
    Preconditions:
        - No precondition is enforced in code beyond accepting the provided arguments. However:
            * For correct later behavior, tokenizer should implement a to_words(text) method; __init__ does not validate this.
            * text should be a value acceptable to to_unicode; otherwise, to_unicode may raise.
    Postconditions:
        - After __init__ returns without raising, self._text is a unicode string (result of normalization) with leading/trailing whitespace removed.
        - self._tokenizer is the same object passed in.
        - self._is_heading is a boolean (True or False).
        - No additional instance attributes exist beyond those in __slots__.

## Side Effects:
    - No I/O, network activity, or global state mutation.
    - The only side effects are mutations to the newly created Sentence instance attributes listed above. The tokenizer object is referenced but not modified by this method.

### `sumy.models.dom._sentence.Sentence.words` · *method*

## Summary:
Returns the tokenized words for this sentence by delegating to the sentence's tokenizer and caches the result on first access.

## Description:
This attribute computes and returns the sequence of word tokens for the sentence text. It is implemented as a cached property: on first access the tokenizer is invoked and its result is stored so subsequent accesses return the cached value without calling the tokenizer again.

Known callers:
- No direct callers were found in the available repository memory. Typical callers are components that need token-level access to a sentence (for example: summarizers, sentence scorers, token-based filters, or any pipeline stage that iterates or analyzes sentence words).

Lifecycle / pipeline stage:
- Invoked when a consumer (summarizer, analyzer, or downstream processing step) needs the tokenized form of a Sentence instance. This usually occurs during text analysis or summarization phases after the DOM/text parsing stage that constructed Sentence objects.

Rationale for being a separate method/property:
- Tokenization is conceptually a separate concern from sentence storage. Exposing it as a cached property centralizes the single responsibility (tokenization + caching) and avoids repeated, potentially expensive calls to the tokenizer from multiple consumers.

## Args:
- None. Accessed as a (cached) attribute on Sentence instances.

## Returns:
- The exact value returned by self._tokenizer.to_words(self._text).
- No additional transformation is applied by Sentence.words; consumers should expect the tokenizer's native return type (commonly a list or iterable of strings), and handle it accordingly.
- Edge cases:
    - If self._text is an empty string, the returned value is whatever the tokenizer returns for empty input (often an empty list).
    - If the tokenizer returns None (non-standard), that value is propagated.

## Raises:
- This method does not explicitly raise its own exceptions.
- Any exception raised by the tokenizer.to_words call (for example TypeError, ValueError, or tokenizer-specific errors) is propagated to the caller.

## State Changes:
Attributes READ:
- self._text
- self._tokenizer

Attributes WRITTEN:
- The cached_property mechanism writes the computed result into the object's cache attribute (the class defines a slot named _cached_property_words, which is used to store the cached value). The method body itself does not assign, but the cached_property decorator performs the write on first access.

## Constraints:
Preconditions:
- self._tokenizer must implement a callable method to_words(text) that accepts the sentence text (already normalized to unicode by Sentence.__init__).
- self._text is expected to be a unicode string (Sentence.__init__ ensures this by calling to_unicode and strip).

Postconditions:
- After the first access, the tokenized result is cached on the instance (subsequent attribute accesses return the cached value without invoking tokenizer.to_words again).
- The returned value equals the tokenizer.to_words result for the current self._text at the time of first access.

## Side Effects:
- Mutates the Sentence instance by storing the tokenization result in the instance cache (via the cached_property mechanism).
- Does not perform I/O or call external services directly; any such side effects would be caused by the tokenizer implementation and are propagated.

### `sumy.models.dom._sentence.Sentence.is_heading` · *method*

## Summary:
Provides read-only access to the sentence's heading flag; returns whether this Sentence was marked as a heading without modifying object state.

## Description:
This property returns the boolean value that indicates whether the Sentence instance represents a heading. It is a lightweight, public accessor that exposes the instance's internal _is_heading flag without allowing mutation.

Known callers and context:
- Typically read by higher-level DOM/model-building code and by any external consumer that needs to distinguish headings from normal sentences (for example, when filtering, grouping, or rendering document parts).
- Internal methods on the class (for example, __eq__, __repr__) access the private attribute _is_heading directly rather than going through this property; external code should use this property as the stable public API.

Rationale for being a separate property:
- Encapsulates the internal attribute and provides a clear, documented public API for consumers.
- Keeps external code from depending on the private attribute name and allows the class to change internal representation later without breaking callers.

## Args:
    None (accessed as a read-only property; do not pass arguments)

## Returns:
    bool: True if the Sentence instance was created/marked as a heading; False otherwise.
    - The value returned is exactly the value of the instance attribute self._is_heading (which __init__ coerces to a boolean).

## Raises:
    None: This accessor does not raise exceptions itself. Exceptions could only occur if the instance is in an invalid state (for example, if _is_heading is missing because __init__ was not called or the instance was corrupted), but in normal usage no exceptions are raised.

## State Changes:
    Attributes READ:
        - self._is_heading
    Attributes WRITTEN:
        - None (this property is read-only and does not modify any attributes)

## Constraints:
    Preconditions:
        - The Sentence instance should have been initialized (__init__ sets self._is_heading). The class defines __slots__ including "_is_heading", so normal instances will have this attribute after construction.
    Postconditions:
        - No mutation to the instance occurs.
        - The return value will be a boolean reflecting the instance's heading flag.

## Side Effects:
    - None. No I/O, no external calls, no mutation of self or other objects.

### `sumy.models.dom._sentence.Sentence.__eq__` · *method*

## Summary:
Compare this Sentence with another and return True only if they have identical normalized text and the same heading flag; the call is read-only and does not mutate either object.

## Description:
Implements the equality test used by the == operator for Sentence objects. Known direct caller in this class: Sentence.__ne__ (which returns not self.__eq__(sentence)). Equality here is defined by two concrete checks performed in order:
1. The other object is asserted to be an instance of Sentence (isinstance check).
2. The heading flag is compared by identity (self._is_heading is sentence._is_heading).
3. The stored, normalized text values are compared by value (self._text == sentence._text).

This behavior is provided in a dedicated method so that all equality comparisons are centralized and align with the complementary implementations of __ne__ and __hash__ in the same class.

## Args:
    sentence (Sentence or subclass): The object to compare against. The method uses isinstance to accept Sentence or any subclass.

## Returns:
    bool: True if and only if both these conditions are met:
        - self._is_heading is sentence._is_heading
        - self._text == sentence._text
    Otherwise returns False.

## Raises:
    AssertionError: If the provided 'sentence' is not an instance of Sentence and Python assertions are enabled (the method contains an assert isinstance(sentence, Sentence)).
    AttributeError: If assertions are disabled (e.g., python -O) and the provided object does not have the required attributes (_is_heading or _text); attempting to access them will raise AttributeError.
    Note: The method does not catch or translate these exceptions.

## State Changes:
    Attributes READ:
        self._is_heading
        self._text
        sentence._is_heading
        sentence._text
    Attributes WRITTEN:
        None — no attributes on self or the other object are modified.

## Constraints:
    Preconditions:
        - Typical use expects both objects were constructed by Sentence.__init__, which sets _text via to_unicode(text).strip() and _is_heading to a boolean value.
        - If a non-Sentence object is passed while assertions are enabled, an AssertionError is raised before attribute access.
    Postconditions:
        - No mutation occurs to either object.
        - A boolean return value is produced reflecting equality according to the two checks above.

## Side Effects:
    - None: no I/O, no external calls, and no mutations beyond reading the listed attributes.

### `sumy.models.dom._sentence.Sentence.__ne__` · *method*

## Summary:
Return the logical negation of the sentence equality check, producing True when the other object is not considered equal by the Sentence equality rules.

## Description:
This method implements the != operator for Sentence instances by delegating to the class's equality logic and negating its result. It is invoked by Python when code compares two Sentence objects using the != operator, and may also be called directly by other code that explicitly tests inequality.

Known callers and context:
- Python runtime when evaluating left_operand != right_operand where left_operand is a Sentence instance.
- Any library or application code in the summarization/document model pipeline that checks whether two Sentence objects differ (for example, deduplication or change detection steps).
- It delegates entirely to Sentence.__eq__ and therefore participates in the same lifecycle stage as equality checks (comparison step during document processing or analysis).

Why this logic exists as its own method:
- Providing __ne__ ensures that inequality uses the exact inverse of the canonical equality implementation (__eq__). Defining it explicitly avoids relying on Python's default fallback behavior and keeps equality/inequality consistent and centralized within the class.

## Args:
    sentence (Sentence or subclass)
        The object to compare against. The method expects a Sentence instance (or subclass). No default value.

## Returns:
    bool
        True if and only if Sentence.__eq__(sentence) would return False. The result is the boolean negation of whatever __eq__ returns. If __eq__ raises an exception, this method does not intercept it and no boolean is returned.

## Raises:
    Any exception raised by Sentence.__eq__ is propagated unchanged. Concretely:
        - AssertionError: If __eq__ contains an assert isinstance(sentence, Sentence) and assertions are enabled, passing a non-Sentence will raise AssertionError.
        - AttributeError or other exceptions: If assertions are disabled (python -O) and the provided object lacks attributes used by __eq__, attribute access in __eq__ may raise AttributeError; other exceptions thrown by __eq__ also propagate.
    This method does not raise additional exceptions on its own.

## State Changes:
    Attributes READ:
        - (Indirectly, via delegated call to __eq__): self._is_heading, self._text, sentence._is_heading, sentence._text
    Attributes WRITTEN:
        - None — this method performs no mutation on self or the other object.

## Constraints:
    Preconditions:
        - The instance (self) should be a valid Sentence object constructed by Sentence.__init__ (so _text and _is_heading exist).
        - The provided argument should be a Sentence or subclass for assertions in __eq__ to pass; otherwise an AssertionError (if assertions are enabled) or attribute-access errors may occur.

    Postconditions:
        - No mutation to self or the argument occurs.
        - A boolean value is returned when __eq__ completes normally; that boolean is the negation of __eq__'s return value.

## Side Effects:
    - None: the method performs no I/O, no external service calls, and no mutations beyond reading attributes through the delegated __eq__ call.

### `sumy.models.dom._sentence.Sentence.__hash__` · *method*

## Summary:
Returns an integer hash computed from the sentence's heading flag and text so Sentence instances can be used as keys in dictionaries or members of sets without violating equality/hash consistency.

## Description:
This method is invoked by Python's hashing machinery whenever an instance needs to be hashed — for example, when hash(instance) is called, when an instance is used as a dictionary key, or when it is inserted into a set. Typical lifecycle usage is during collection operations (deduplication, set membership, using Sentence as dict keys) in higher-level processing pipelines that group or index sentences.

The hashing logic is extracted into its own method to provide an explicit, language-level hook that:
- Ensures hash() is consistent with the class's __eq__ implementation (both use the same fields: _is_heading and _text).
- Allows Sentence objects to be used reliably in hashed collections across the codebase without duplicating hashing logic.

## Args:
None.

## Returns:
int
    The integer hash of a 2-tuple consisting of (self._is_heading, self._text). The returned value is whatever Python's built-in hash produces for that tuple (can be positive or negative). If both fields are their normal types (bool and str/unicode), this will always be an int.

## Raises:
TypeError
    If either component used in the tuple is not hashable, Python's built-in hash will raise TypeError. In this class, _is_heading is set to a bool in __init__ and _text is coerced to unicode, so under normal construction this exception should not occur.

## State Changes:
Attributes READ:
    - self._is_heading
    - self._text

Attributes WRITTEN:
    - None (this method does not modify any attributes)

## Constraints:
Preconditions:
    - The instance must have been initialized so that self._is_heading and self._text exist (satisfied by Sentence.__init__ which sets these attributes).
    - To preserve correct behavior when used as a dict key or member of a set, callers must avoid mutating self._text or self._is_heading while the object is stored in hashed collections. Mutating these fields after insertion will violate the hash/equality contract and can corrupt collection invariants.

Postconditions:
    - The method returns an integer value deterministically derived from the current values of self._is_heading and self._text.
    - It does not modify the instance or any external state.

## Side Effects:
    - None. The method performs no I/O, calls no external services, and mutates no objects (other than reading self attributes).

### `sumy.models.dom._sentence.Sentence.__unicode__` · *method*

## Summary:
Return the sentence's canonical text content as a Unicode string.

## Description:
This method provides the canonical textual representation stored on the Sentence instance. It is the single-point accessor that yields the exact string stored in the instance's internal _text attribute.

Known callers and context:
- Anything that needs the Sentence's text representation should use this method (for example, code that prints, logs, or serializes a Sentence).
- Within this class file, __repr__ obtains a printable representation by calling __str__(); __unicode__ is the canonical source of the underlying text returned by any textual conversion implementations.

Why this logic is a dedicated method:
- Centralizes the mapping from the Sentence's internal storage (_text) to the exported text representation, allowing subclasses or compatibility shims (e.g., str/unicode wrappers) to override or call a single, well-defined method.
- Keeps the access to the stored text explicit and trivial to mock or override in tests.

## Args:
    None

## Returns:
    str: The exact value of self._text (already normalized in the constructor to a Unicode string and stripped of surrounding whitespace). Possible values include any Unicode text assigned when the Sentence was constructed; never None for properly constructed instances.

## Raises:
    None: This method performs a direct attribute return and does not raise exceptions itself. (If the instance was improperly constructed or mutated such that _text is missing, Python's normal AttributeError may occur.)

## State Changes:
    Attributes READ:
        self._text

    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - The instance must have a valid _text attribute (the class constructor sets _text via to_unicode(text).strip()).
    Postconditions:
        - Calling the method does not modify the instance.
        - The return value equals the current value of self._text.

## Side Effects:
    - None. This method performs no I/O, external calls, or mutations of objects outside self.

### `sumy.models.dom._sentence.Sentence.__repr__` · *method*

## Summary:
Returns a short, compatibility-aware textual representation of the Sentence that labels it as a Heading or Sentence and embeds the object's string form; does not modify the object's state.

## Description:
This method is the implementation of the object's programmer-facing representation used by Python's built-in repr() and by debugging/logging/inspection code. Typical callers and contexts:
- The built-in repr() when a Sentence instance is printed, logged, or displayed in a REPL.
- Logging or debugging output in code that inspects DOM sentence objects.
- Any internal code that needs a compact, human-readable summary of a Sentence for diagnostics.

Why this logic is a separate method:
- It centralizes formatting of the object summary (type label + textual content) so all callers get a consistent representation.
- It delegates the runtime string/bytes selection to the shared to_string helper to follow the library's PY3/bytes compatibility policy, keeping compatibility concerns out of callers and other methods.

## Args:
    None

## Returns:
    str or bytes:
        - The formatted representation of the form "<Heading: X>" if the sentence is marked as a heading, otherwise "<Sentence: X>" where X is the result of calling self.__str__().
        - The exact returned Python type follows to_string's contract: on a PY3 (text-first) runtime this will be the module text type (typically str); on a non-PY3 (bytes-first) compatibility mode it will be bytes.
        - Edge cases:
            * If the sentence text is empty, the inner part may be empty (e.g. "<Sentence: >").
            * If self.__str__() raises or produces unusual values, those are passed into the formatting and then converted by to_string (or the conversion exception is propagated).

## Raises:
    - Any exception raised by self.__str__(): propagated to the caller.
    - Any exception raised by to_string(...) (which itself delegates to to_unicode or to_bytes): propagated to the caller.
    - Practical note: if Sentence does not provide a safe __str__ implementation and Python's inherited __str__ resolves back to __repr__, calling self.__str__() from inside __repr__ can produce unbounded recursion and ultimately raise RecursionError. This is a potential failure mode unless a compatible __str__ (for example provided by a unicode_compatible decorator or an explicit __str__ implementation) is present.

## State Changes:
    Attributes READ:
        - self._is_heading (bool): used to choose the label "Heading" vs "Sentence".
        - Indirectly reads whatever attributes self.__str__() accesses (commonly self._text). In the current class, __unicode__ returns self._text, so in typical setups the text is read via the string conversion path.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - The instance must be a properly-initialized Sentence with a defined _is_heading attribute (the class sets this in __init__).
        - For safe, non-recursive operation, a sane __str__ implementation must be available (either an explicit __str__ method or a compatibility decorator that provides one by delegating to __unicode__).

    Postconditions:
        - The Sentence instance is unchanged.
        - The caller receives a single textual/bytes value representing the object summary according to the library's compatibility settings.

## Side Effects:
    - No I/O, network, or global state mutation.
    - The only observable effects are the value returned and any exceptions propagated from the string-conversion helpers (self.__str__ and to_string).

