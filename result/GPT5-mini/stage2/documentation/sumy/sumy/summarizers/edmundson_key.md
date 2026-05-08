# `edmundson_key.py`

## `sumy.summarizers.edmundson_key.EdmundsonKeyMethod` · *class*

*No documentation generated.*

### `sumy.summarizers.edmundson_key.EdmundsonKeyMethod.__init__` · *method*

## Summary:
Initializes the instance by delegating stemmer validation to the base class and storing the provided bonus_words on the object.

## Description:
Known callers and lifecycle stage:
- Called when an EdmundsonKeyMethod instance is constructed (e.g., by pipeline/factory code that selects this summarizer implementation).
- Invocation occurs at object creation time, before the instance is used to score or summarize documents.

Why this logic is its own method:
- Uses the base-class initializer to centralize and reuse stemmer validation and assignment behavior provided by AbstractSummarizer.
- Keeps subclass construction minimal by separating stemmer setup (handled by the superclass) from subclass-specific state (bonus words) assignment.

## Args:
    stemmer (callable):
        - A callable accepting a single token (string) and returning a stem/canonical form.
        - Validation: responsibility for verifying callability is performed by AbstractSummarizer.__init__; passing a non-callable will trigger a ValueError from the base class.
        - No further checks or transformations are performed here.

    bonus_words (any):
        - The object provided by the caller is stored directly on the instance as-is (no validation or copying).
        - Typical use (outside this constructor): a collection or mapping of tokens used later by the summarizer's scoring logic, but this method does not enforce any type or structure.

## Returns:
    None

## Raises:
    ValueError: If the provided stemmer argument is not callable.
        - This exception is raised by the call to the superclass initializer (AbstractSummarizer.__init__) and propagates out of this constructor.
    (No other exceptions are raised by this method itself; any exceptions raised by the caller-provided bonus_words object are only observed later when that object is used.)

## State Changes:
Attributes READ:
    - None (this constructor does not read existing instance attributes)

Attributes WRITTEN:
    - self._stemmer: set by AbstractSummarizer.__init__ invoked via super(...) (the base initializer validates and assigns this attribute)
    - self._bonus_words: assigned to the bonus_words argument exactly as passed

## Constraints:
Preconditions:
    - The stemmer argument must be a callable (or omitted if a default is provided by the caller before forwarding to this constructor).
    - No precondition is required for bonus_words; any value is accepted and stored.

Postconditions:
    - After successful construction:
        - self._stemmer exists and satisfies the base-class invariant (callable).
        - self._bonus_words is bound to the same object passed as the bonus_words parameter (no copy/modification performed).

## Side Effects:
    - Mutates the instance by assigning attributes (_stemmer via the base initializer, and _bonus_words here).
    - No I/O, network access, or mutation of external objects is performed by this constructor.
    - Because bonus_words is stored by reference, mutations to the passed object after construction will be observable through self._bonus_words.

### `sumy.summarizers.edmundson_key.EdmundsonKeyMethod.__call__` · *method*

## Summary:
Compute significant (bonus) words for the supplied document using the given threshold, then select and return the top sentences as determined by the summarizer's sentence-selection helper. This call does not modify the summarizer's persistent state.

## Description:
This method is the main entry point for producing a short extractive summary from a document instance. It is typically invoked by client code or a summarization pipeline when a consumable summary (a set of sentences) is required from an EdmundsonKeyMethod summarizer instance.

Call flow / lifecycle context:
- A user or pipeline constructs an EdmundsonKeyMethod(some_stemmer, bonus_words) and then calls the instance like a function to produce a summary:
    summary_sentences = edmundson_summarizer(document, sentences_count, weight)
- Within this call:
    1. _compute_significant_words(document, weight) is called to determine the tuple of significant (bonus) words based on term frequencies and the threshold `weight`.
    2. _get_best_sentences(...) (inherited from AbstractSummarizer) is called with the document's sentences, the requested count, a scoring callback (self._rate_sentence), and the computed significant words to choose the best sentences to include in the summary.

Why this is a separate method:
- It encapsulates the high-level summarization step (compute-significant-words → select-best-sentences) and keeps orchestration separate from the word-frequency logic and sentence-selection implementation. This separation improves readability, allows reuse of the underlying helpers, and keeps this method focused on composing the substeps of the Edmundson keyword-based summarization algorithm.

## Args:
    document (object): Document-like object with at least these attributes:
        - sentences: an iterable/sequence of Sentence-like objects (each should expose .words).
        - words: an iterable of token strings for the whole document.
        The Document is not modified by this method.
    sentences_count (int): Desired number of sentences to return in the summary. Expected to be a non-negative integer. If the document contains fewer sentences than requested, the returned sequence may contain fewer items.
    weight (float): Threshold used to decide which words are "significant" relative to the most frequent bonus word. The implementation compares (word_frequency / max_word_frequency) > weight. Typical/expected values are in the [0.0, 1.0] range:
        - 0.0 will include any word with frequency > 0
        - values closer to 1.0 make the significant-words set smaller
        - values >= 1.0 will normally result in an empty significant-words set

## Returns:
    sequence: A sequence (typically a list or tuple) of sentence objects selected from document.sentences. The concrete ordering and exact container type are determined by _get_best_sentences (inherited from AbstractSummarizer). Possible edge-case return values:
        - An empty sequence if no sentences qualify or the document has no sentences.
        - Fewer than sentences_count items if the document has fewer sentences than requested.

## Raises:
    AttributeError: If the provided document does not expose required attributes such as .words or .sentences, an AttributeError will be raised when attempting to access those attributes (propagated from this method or the helper it calls).
    Any exceptions raised by the delegated helpers (_compute_significant_words, _rate_sentence, or _get_best_sentences) may propagate unchanged (for example, if those helpers validate types or encounter unexpected data).

## State Changes:
Attributes READ:
    - self._bonus_words (indirectly, via _compute_significant_words and _is_bonus_word)
    - methods on self are invoked: self.stem_word (in _compute_significant_words/_rate_sentence), self._compute_significant_words, self._rate_sentence, self._get_best_sentences

Attributes WRITTEN:
    - None. This method does not mutate self or document; it only reads state and delegates work to helper methods.

## Constraints:
Preconditions:
    - document must be a document-like object with .words (iterable of tokens) and .sentences (iterable/sequence of sentence-like objects with .words).
    - sentences_count should be a non-negative integer (the caller is expected to provide an integer).
    - weight should be a numeric value; meaningful behavior is expected when weight is within [0.0, 1.0].

Postconditions:
    - self remains unchanged.
    - A sequence of sentence objects (possibly empty) is returned. Those sentences are drawn from document.sentences and scored using self._rate_sentence with the significant words computed for this call.

## Side Effects:
    - No I/O, network, or file-system operations.
    - No modification of the input document or of self.
    - Delegated helpers will perform CPU-bound computation (token stemming and frequency counting) and allocation of small temporary data structures (e.g., the tuple of significant words).

### `sumy.summarizers.edmundson_key.EdmundsonKeyMethod._compute_significant_words` · *method*

## Summary:
Compute and return a tuple of stemmed "significant" words (from the document) whose frequency relative to the most frequent bonus-word exceeds the provided threshold; does not modify object state.

## Description:
Known callers and lifecycle:
- Called by EdmundsonKeyMethod.__call__(document, sentences_count, weight) during summarization to determine which words should be treated as "bonus" (significant) when selecting best sentences.
- Also called by EdmundsonKeyMethod.rate_sentences(document, weight=0.5) to compute the same set for batch sentence scoring.
- Invocation occurs at the scoring/preparation stage of the summarization pipeline: given a tokenized Document, this method selects significant stems used by the sentence rating step.

Why this logic is its own method:
- The computation is a distinct, reusable piece used by multiple public methods (__call__ and rate_sentences). Isolating it improves clarity, avoids duplicated logic, and centralizes behavior related to how "significant" bonus-words are determined (stemming, filtering, counting, thresholding).

## Args:
    document (object):
        - Required.
        - Any object that exposes an iterable attribute `.words` (e.g., a Document with tokenized words).
        - Each element yielded from `document.words` is passed to self.stem_word; therefore elements must be acceptable inputs to that stemmer.
    weight (float):
        - Required.
        - A numeric threshold compared against the ratio frequency/max_frequency.
        - Typical/expected range: 0.0 <= weight < 1.0. (Behavior is defined for other numeric values: if weight < 0, most words will qualify; if weight >= 1.0 no words will qualify because frequency/max <= 1.0.)

## Returns:
    tuple:
        - A tuple of words (the stems returned by self.stem_word) that satisfy the selection criterion:
            frequency / max_word_frequency > weight
        - If no bonus words are present in the document (after stemming and filtering), returns an empty tuple ().
        - Order: the tuple contains the qualifying words in the iteration order produced by iterating word_counts.items(); no stable sort or ordering guarantee beyond the iteration order of the underlying mapping is provided.

## Raises:
    - AttributeError:
        - If `document` has no `.words` attribute (attribute access fails) or if an item from `document.words` causes an AttributeError inside self.stem_word or self._is_bonus_word.
    - Any exception raised by self.stem_word (e.g., UnicodeDecodeError, ValueError) or by self._is_bonus_word will propagate unchanged.
    - TypeError or other arithmetic exceptions:
        - If `weight` is not a numeric type usable in the comparison (for example, if weight is a non-numeric object), a TypeError may be raised during the expression `frequency/max_word_frequency > weight`.
    - Note: the method itself does not explicitly raise custom exceptions; it allows underlying exceptions to propagate to the caller.

## State Changes:
    Attributes READ:
        - self._bonus_words (accessed indirectly via self._is_bonus_word)
        - self.stem_word (method is invoked for each token; the method is read/called)
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - `document.words` must be iterable (list, tuple, generator, etc.). Each yielded token must be acceptable to self.stem_word.
        - The instance must have a working stemmer via self.stem_word and a bonus-word set via self._bonus_words (or equivalent) so _is_bonus_word can test membership.
        - `weight` should be a numeric value; typical callers provide a float in [0.0, 1.0).
    Postconditions:
        - Returns a tuple containing zero or more stemmed words (the same type returned by the configured stemmer).
        - No attributes on self are changed.
        - If the returned tuple is non-empty, every returned word satisfies:
            count(word) / max_count > weight
          where count(word) is the number of occurrences (after stemming and filtering) and max_count is the highest such count across bonus-words.

## Side Effects:
    - No I/O or external service calls are made.
    - Potential iterator consumption: the method maps and filters over `document.words` and passes the resulting sequence to Counter. If `document.words` is a generator or iterator, it will be fully consumed by this method; callers should not expect to reuse the same iterator after calling this function.
    - Memory/time: builds a Counter of all (stemmed & filtered) bonus-words — memory proportional to the number of distinct bonus-word stems and time proportional to the number of tokens examined.

### `sumy.summarizers.edmundson_key.EdmundsonKeyMethod._is_bonus_word` · *method*

## Summary:
Performs a membership check to determine whether the provided token exists in the object's bonus-words container and returns the boolean result; does not modify object state.

## Description:
This is a small, internal predicate (indicated by the leading underscore in the name) that centralizes the "contains" test against self._bonus_words. The method body performs a single membership operation and returns its result; its purpose is to provide a semantically named helper so callers do not repeat the raw membership expression.

## Args:
    word (any): The token to test for membership.
        - Expected: an object compatible with the container stored in self._bonus_words (commonly a str when bonus words are strings).
        - If self._bonus_words is a set or dict, the token must be hashable.

## Returns:
    bool-like: The result of evaluating the Python expression "word in self._bonus_words".
    - In standard containers (set, list, dict) this is a boolean True or False.
    - More generally, returns whatever the container's membership operation yields.

## Raises:
    - Any exception raised by evaluating "word in self._bonus_words" will be propagated to the caller.
      Common examples include:
        * TypeError if self._bonus_words is None or an unsupported type for the "in" operator, or if the token is unhashable for set/dict membership.
        * Any exception raised by a custom __contains__ implementation on the container.
    - The method does not catch or alter exceptions.

## State Changes:
    Attributes READ:
        - self._bonus_words
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - self._bonus_words must be initialized to a container that supports membership testing before calling this method.
        - For predictable results, callers should ensure any normalization (case folding, lemmatization) applied to bonus words is also applied to the token prior to calling.
    Postconditions:
        - No mutation of self or external state.
        - The return value reflects the container's membership semantics at the time of the call.

## Side Effects:
    - None (no I/O, no external calls, no mutation of external objects).

## Example:
- If self._bonus_words == {"important"}:
    - _is_bonus_word("important") -> True
    - _is_bonus_word("Important") -> False (unless normalization is applied before calling)

### `sumy.summarizers.edmundson_key.EdmundsonKeyMethod._rate_sentence` · *method*

## Summary:
Counts how many tokens in a sentence, after normalization/stemming, appear among the provided significant stems; does not modify the object state.

## Description:
Known callers and lifecycle context:
- EdmundsonKeyMethod.__call__: used as the per-sentence rating callable after _compute_significant_words produces the significant stems; its integer scores are consumed by AbstractSummarizer._get_best_sentences to select top sentences for the summary.
- EdmundsonKeyMethod.rate_sentences: called directly to compute a mapping of each sentence to its integer rating (useful for inspection or tests).
- This logic is separated into its own method so it can be passed as a callable to the generic selection helper (_get_best_sentences), reused by multiple callers, and tested independently.

## Args:
    sentence (object):
        - Must provide a public iterable attribute `words` (e.g., sentence.words).
        - Each token in sentence.words must be acceptable to self.stem_word (commonly a text token).
    significant_words (iterable):
        - An iterable or container of stemmed tokens used for membership testing.
        - Typical forms: tuple, list, set. For best performance, callers typically pass a set because membership tests are O(1).

## Returns:
    int:
        - The number of tokens in sentence.words whose stem (produced by self.stem_word) is found in significant_words.
        - Always non-negative. Returns 0 when sentence has no words or none of the stems match.
        - Duplicate tokens (or distinct tokens that map to the same stem) are counted repeatedly.

## Raises:
    - AttributeError: if the provided sentence object has no attribute `words`.
    - TypeError:
        - if sentence.words is not iterable (e.g., None or a non-iterable object),
        - or if significant_words is not iterable nor supports membership testing (e.g., None).
    - Propagated exceptions from self.stem_word(token):
        - Any exception raised by normalize_word or the configured stemmer will propagate (examples include UnicodeError when normalizing bytes, ValueError or custom exceptions raised by a custom stemmer).
    Notes: The method itself does not wrap or convert exceptions; callers should expect stemmer- and iterable-related exceptions to propagate.

## State Changes:
    Attributes READ:
        - self.stem_word (method) — invoked for every token; stem_word typically uses self._stemmer from AbstractSummarizer.
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - The instance must have a working stem_word method (AbstractSummarizer guarantees this when constructed with a callable stemmer).
        - sentence must expose an iterable `words`.
        - significant_words must be suitable for membership tests (implement __contains__ or be iterable). Passing a set yields best performance.
    Postconditions:
        - No mutation of self or of the passed sentence/significant_words is performed by this method.
        - Return value is an int >= 0 reflecting the count described above.

## Side Effects:
    - No I/O, logging, or network activity performed by this method.
    - No mutation of the sentence object or of significant_words.
    - Calls self.stem_word for each token; if a custom stemmer has side effects, those side effects will occur (they are not caused by this method itself).
    - Implementation note: map(self.stem_word, sentence.words) returns an iterator in Python 3 and will be consumed by sum immediately; the method performs a single-pass evaluation over the tokens.

### `sumy.summarizers.edmundson_key.EdmundsonKeyMethod.rate_sentences` · *method*

## Summary:
Computes and returns a mapping from each sentence in the document to an integer score that counts how many of the sentence's (stemmed) words are considered "significant" for the document; does not modify the object state.

## Description:
This convenience routine performs two steps: it derives the document's significant words by delegating to the class helper that computes significant words, then it rates every sentence in the document by delegating to the per-sentence rating helper.

Known callers and context:
- Not referenced by other methods inside the shown EdmundsonKeyMethod implementation; it serves as a public/utility API to obtain sentence scores for an entire document (for example, for debugging, ranking, or to supply scores to an external selector).
- Typical pipeline stage: called after a Document object has been produced by a parser and before selecting/ordering sentences for a summary (i.e., the scoring stage of the summarization pipeline).

Why this is a separate method:
- Encapsulates the common two-step operation (compute significant words → rate each sentence) so callers can get all sentence scores in one call rather than repeating the two steps.
- Keeps the higher-level control flow separate from the low-level scoring logic implemented in _compute_significant_words and _rate_sentence, improving reuse and testability.

## Args:
    document (object): Required. An object representing the parsed document with at least:
        - document.words: an iterable of word tokens (strings) for the whole document.
        - document.sentences: an iterable of sentence objects. Each sentence object must expose .words (an iterable of word tokens).
      No specific concrete class is required, but the attributes above must exist.
    weight (float, optional): Threshold in the (recommended) range [0.0, 1.0] used by the significant-word computation to filter frequent words. Default is 0.5.
        - Semantics: words whose frequency / max_word_frequency is strictly greater than weight are considered significant by the helper.

## Returns:
    dict: A mapping {sentence_object: score} where:
        - sentence_object is each item from document.sentences (the method uses the sentence objects themselves as dictionary keys).
        - score is int: the number of words in that sentence (after stemming via the class's stemmer) that are present in the significant words set computed for the document.
      Edge cases:
        - If document.sentences is empty, an empty dict is returned.
        - If there are no significant words (the helper returns an empty tuple), every sentence receives score 0.

## Raises:
    AttributeError: If the provided document lacks the required attributes (document.words or document.sentences), or if any sentence lacks .words. These come from trying to access those attributes.
    TypeError: If a sentence object is unhashable and therefore cannot be used as a dict key; this will be raised by the dict assignment operation.
    Any exceptions raised by the helper methods (self._compute_significant_words or self._rate_sentence) will propagate unchanged.

## State Changes:
Attributes READ:
    - self._bonus_words (indirectly): accessed by _compute_significant_words.
    - Any attributes/methods used by stem_word or other helpers (e.g., methods on AbstractSummarizer) are read indirectly via helper calls.
Attributes WRITTEN:
    - None. This method does not modify self or the document objects.

## Constraints:
Preconditions:
    - document must provide:
        - document.words: iterable of strings (used by _compute_significant_words).
        - document.sentences: iterable of sentence objects that expose .words (iterable of strings).
    - Each sentence object must be usable as a dictionary key (i.e., hashable). If not, a TypeError will be raised.
    - weight should be a numeric value; the intended semantics assume 0.0 <= weight <= 1.0 though values outside this range are technically allowed (comparison is performed as frequency/max > weight).

Postconditions:
    - The returned dictionary contains one entry per sentence in document.sentences (or is empty if document.sentences is empty).
    - The object state (self) is unchanged by this call.
    - The numeric score for each sentence equals the integer count returned by _rate_sentence for that sentence and the significant words computed by _compute_significant_words(document, weight).

## Side Effects:
    - No I/O or network activity.
    - Calls helper methods that perform stemming and membership checks; these may execute pure CPU work but do not mutate external state.
    - The method may raise exceptions that propagate from attribute accesses or from helper methods.

