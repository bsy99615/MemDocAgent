# `edmundson_title.py`

## `sumy.summarizers.edmundson_title.EdmundsonTitleMethod` · *class*

## Summary:
EdmundsonTitleMethod is a concrete summarizer that implements the Edmundson "title method": it ranks sentences by how many stemmed words they share with the document's headings (excluding configured null/stop words) and selects the top sentences using the AbstractSummarizer selection helper.

## Description:
This class is a concrete subclass of AbstractSummarizer that produces an extractive summary by favoring sentences containing heading/title words. It is intended to be instantiated where a summarizer that privileges document headings (titles) is required — for example, when titles/headings are known to be highly informative for the summary.

Typical callers:
- Summarization pipelines that instantiate a chosen summarizer class and call it with a parsed document and desired sentence count.
- Any code that already expects AbstractSummarizer instances and wants the Edmundson title-based behavior.

Why this abstraction:
- Encapsulates a single scoring heuristic (title-word overlap) and reuses AbstractSummarizer._get_best_sentences for selection and ordering.
- Keeps scoring logic and heading-derived-significant-word preparation together so that other components can reuse the underlying rate_sentences API (returns a mapping of sentence->score).

Behavioral summary (what it does):
- Computes a set of significant words by collecting words from document.headings, normalizing/stemming them, and excluding configured null words.
- Scores each sentence as the count of stemmed words in the sentence that appear in the significant-words set.
- Selects top sentences via AbstractSummarizer._get_best_sentences so that selected sentences are returned in original document order.

Notes about ffilter:
- The source calls ffilter(self._is_null_word, ...) to filter heading words. In this code ffilter is used to exclude null words: implementers must ensure the equivalent helper removes items for which the predicate returns True (i.e., keep items where predicate(word) is False). This is required for _compute_significant_words to return non-null (meaningful) words.

## State:
Instance attributes
- _stemmer (callable)
  - Type: callable(str) -> any (inherited from AbstractSummarizer)
  - Constraints: must be callable; AbstractSummarizer.__init__ enforces this and raises ValueError if not callable.
  - Semantics: called by stem_word to convert a normalized token into a canonical form used for comparisons.

- _null_words
  - Type: any iterable or container supporting membership testing (ideally a set for O(1) membership): e.g., set[str], frozenset[str], list[str]
  - Expected contents: normalized/stemmed token forms that should be considered "null" (stop words) for the title matching algorithm.
  - Important invariant: membership tests in _is_null_word use the same token form produced by stem_word; therefore, callers should pass null_words whose elements are comparable to stem_word outputs (recommended: stem the canonical stop-words with the same stemmer before passing them).
  - Mutability: The class does not mutate _null_words; if a mutable container is provided, external mutation will affect behavior (no copy is made). Prefer an immutable container (frozenset) to preserve invariants.

Class invariants
- self._stemmer is callable for the instance lifetime.
- self._null_words remains a membership-testable container consistent with stem_word outputs.
- _compute_significant_words always returns a frozenset (possibly empty) of stems derived from document.headings after excluding null words.

## Lifecycle:
Creation
- Constructor signature: EdmundsonTitleMethod(stemmer, null_words)
  - stemmer: required. Passed to AbstractSummarizer.__init__ which enforces callability.
  - null_words: required. Must be a container usable with "word in null_words".
  - There are no default values in this class — both parameters must be provided by the caller.

Usage
1. Instantiate: provide a callable stemmer and a null_words container (preferably pre-normalized/stemmed).
2. Invoke the instance as a callable: summary = instance(document, sentences_count)
   - document: an object with at least:
     - headings: iterable of heading objects, each exposing .words (an iterable of tokens)
     - sentences: iterable of sentence objects, each exposing .words (an iterable of tokens)
   - sentences_count: passed through to AbstractSummarizer._get_best_sentences (int, percentage string like "30%", or a callable/ItemsCount-compatible value).
3. Internal call sequence when invoked:
   - __call__ → _compute_significant_words(document) → _get_best_sentences(sentences, sentences_count, self._rate_sentence, significant_words)
   - _get_best_sentences will enumerate, rate using _rate_sentence, sort by rating, pick top N, and restore original document order in the returned sequence.
4. Alternative usage:
   - Use rate_sentences(document) to get a dict mapping each sentence to its numeric score without selecting top sentences.

Destruction / cleanup
- No cleanup is required by this class (no files, sockets, or external resources). It does not implement context manager methods or close().

Sequence requirements and ordering
- The only required precondition is that the provided document has .headings and .sentences attributes with their .words accessible as iterables of tokens.
- Methods may be called in any order by user code, but typical flows are:
  - __call__ (preferred) or rate_sentences (if caller wants full scoring map).
- There is no internal mutable state modified by scoring methods; the class is safe for repeated calls with different documents provided the same stemmer and null_words semantics apply.

## Method Map:
graph TD
    A[__init__(stemmer,null_words)] --> B[_stemmer (via AbstractSummarizer)]
    A --> C[_null_words set]
    D[__call__(document,sentences_count)] --> E[_compute_significant_words(document)]
    E --> F[collect heading.words]
    F --> G[map self.stem_word over words]
    G --> H[ffilter(self._is_null_word, stems)  // exclude null words]
    H --> I[frozenset(significant_words)]
    D --> J[_get_best_sentences(sentences,sentences_count,self._rate_sentence, significant_words)]
    K[_rate_sentence(sentence, significant_words)] --> L[map self.stem_word over sentence.words]
    L --> M[count membership w in significant_words]
    J --> N[return selected sentences in original order]
    O[rate_sentences(document)] --> E
    O --> P[build and return dict sentence->score]

(Note: ffilter is expected to exclude items for which predicate returns True.)

## Raises:
Exceptions that may be raised directly or propagate from dependencies.

- During construction:
  - ValueError: if stemmer is not callable (raised by AbstractSummarizer.__init__).

- During _compute_significant_words:
  - AttributeError: if document.headings is missing or heading objects do not have a .words attribute.
  - Any exception raised by self.stem_word (e.g., errors in normalizing/stemming a token) propagates.
  - Any exception raised by ffilter or attrgetter (if provided with invalid inputs) propagates.

- During __call__ or rate_sentences:
  - Same as above plus:
  - Errors from AbstractSummarizer._get_best_sentences:
    - AssertionError if a mapping is passed as rating incorrectly (not applicable here because rating is callable).
    - Any exceptions raised by the rating callable (_rate_sentence) will propagate.
    - Any exceptions from ItemsCount/count callable may propagate if sentences_count is an invalid type/value.

Edge behavior specifics:
- If the document has no headings or all heading words are excluded by null_words, _compute_significant_words returns an empty frozenset. In that case, all sentences score 0 and selection falls back to the selection policy implemented by _get_best_sentences (usually top-N ties — ordering behavior is implementation-defined by the selection helper).
- Duplicate heading words are deduplicated by frozenset; repeated occurrences in headings do not increase influence beyond presence/absence when building significant_words.
- Repeated occurrences of a significant word within a sentence are counted multiple times (the score is the sum of occurrences where the stem appears in the significant set).
- Membership comparisons are exact equality on the output of self.stem_word; ensure null_words uses comparable token forms.

## Example:
- Preparation:
  - Choose or provide a stemmer callable compatible with AbstractSummarizer expectations (it receives normalized tokens).
  - Prepare null_words as a set of stemmed tokens (recommended).
  - Ensure document exposes .headings (iterable of heading objects with .words) and .sentences (iterable of sentence objects with .words).

- Typical usage steps (descriptive):
  1. Create summarizer instance by providing a stemmer and null_words.
     summarizer = EdmundsonTitleMethod(stemmer, null_words)
  2. Call the instance with a parsed document and desired sentences_count:
     summary_sentences = summarizer(document, 5)   # request top 5 sentences
  3. If you need scores for all sentences rather than selection:
     scores = summarizer.rate_sentences(document)  # returns dict mapping sentence -> int score

Remarks for implementers reproducing this component:
- Reimplement stem-word comparisons exactly as in AbstractSummarizer: call self.stem_word(token) for normalization and stemming.
- Ensure ffilter-like behavior excludes predicate-true items (i.e., treat predicate as "is null" and keep items where predicate returns False).
- Use frozenset for significant words for O(1) membership checks and deterministic, hashable grouping.
- Use AbstractSummarizer._get_best_sentences to perform selection and ordering so this class remains compact and focuses only on scoring logic.

### `sumy.summarizers.edmundson_title.EdmundsonTitleMethod.__init__` · *method*

## Summary:
Initializes an EdmundsonTitleMethod instance by delegating stemmer validation/assignment to the AbstractSummarizer and storing the provided null-words container on the instance.

## Description:
- Known callers and lifecycle stage:
    - Called by any summarization pipeline or factory that constructs a concrete summarizer instance before it is used to produce summaries. Typical callers:
        - Pipeline code that selects and constructs a summarizer implementation (e.g., EdmundsonTitleMethod(stemmer, null_words)).
        - Tests or examples that instantiate the summarizer prior to calling the instance with a document and sentence-count.
    - Lifecycle: this method is executed only at object construction time. After it returns, the instance is ready for use (e.g., __call__ or rate_sentences).

- Why this logic is its own method:
    - Keeps simple construction-time initialization localized: validation and assignment of the stemmer are handled by the shared AbstractSummarizer.__init__, while null-words configuration is stored by the concrete subclass. This separation enforces the base-class contract for stemming behavior while allowing subclass-specific configuration (null words) to be set without duplicating base-class validation.

## Args:
    stemmer (callable): A callable that accepts a single normalized token (string) and returns a stem or canonical form. No default — must be provided. AbstractSummarizer.__init__ enforces that this argument is callable and will raise ValueError otherwise.
    null_words (iterable or container): Container of tokens representing "null" or stop words for title/headings matching. Expected to support membership testing using "in" (e.g., set, frozenset, list, tuple). No default — must be provided.

## Returns:
    None. This is an initializer; it does not return a value.

## Raises:
    ValueError: If stemmer is not callable. This is raised by AbstractSummarizer.__init__ invoked by this constructor.
    TypeError or other exceptions: If the constructor is called with the wrong number/type of positional arguments (standard Python call errors), those will propagate. The method does not perform validation on null_words itself; later operations that assume membership-testing on null_words may raise TypeError if null_words does not support "in".

## State Changes:
- Attributes READ:
    - None from the instance are read explicitly by this method.
    - (Indirect) AbstractSummarizer.__init__ will validate the stemmer argument but the subclass __init__ itself does not read instance attributes.

- Attributes WRITTEN:
    - self._stemmer (written indirectly by AbstractSummarizer.__init__ called via super). Guaranteed to be a callable after construction if no exception was raised.
    - self._null_words (assigned directly): stores the provided null_words object by reference.

## Constraints:
- Preconditions:
    - stemmer must be a callable accepting a single token argument. If not, AbstractSummarizer.__init__ will raise ValueError.
    - null_words should be a container that supports membership testing ("token in null_words") using the same token form that will be produced by self.stem_word during later scoring. It is the caller's responsibility to provide a container whose elements are comparable to stemmer(normalized_token).
- Postconditions:
    - On successful return:
        - self._stemmer exists and is callable (set by AbstractSummarizer.__init__).
        - self._null_words references the provided object (no copy performed).
    - No other instance attributes are modified.

## Side Effects:
    - No I/O operations, network calls, or external service interactions.
    - Stores a direct reference to null_words; if null_words is a mutable container and is mutated by the caller after construction, the instance's behavior will change accordingly (no defensive copy is made).
    - Any exception raised by AbstractSummarizer.__init__ (e.g., ValueError for non-callable stemmer) will propagate to the caller.

## Implementation notes for reimplementers:
    - Call the base-class constructor with the stemmer to reuse its callability check and to set _stemmer consistently.
    - Assign null_words to an instance attribute without modifying or copying it; documenters recommend passing an immutable container (frozenset) or a pre-stemmed set for stable behavior.
    - Do not attempt to validate that null_words elements are pre-stemmed here — that validation is not performed in the original implementation and is the caller's responsibility.

### `sumy.summarizers.edmundson_title.EdmundsonTitleMethod.__call__` · *method*

## Summary:
Orchestrates the Edmundson title-word summarization: builds a frozenset of significant (stemmed) heading words, rates each sentence using that set, and returns the top sentences selected by the shared selection helper (preserving original document order).

## Description:
This concrete __call__ implements the public summarization entry point for the EdmundsonTitleMethod summarizer. It is invoked by client code or a summarization pipeline after a document has been parsed and tokenized into headings and sentences. Typical lifecycle stage: document has been constructed (with headings and sentences) and the pipeline requests a summary by calling summarizer_instance(document, sentences_count).

Why this is a separate method:
- It defines the public contract (accepts a document and a sentences_count) and coordinates three algorithmic steps (extract title words, score sentences, select top sentences), delegating reusable tasks (stemming, selection) to helpers. Keeping this orchestration in __call__ preserves the AbstractSummarizer contract and isolates algorithm-specific composition from helper implementations.

Call flow (explicit):
1. Read document.sentences into a local variable `sentences`.
2. Compute significant_words by calling self._compute_significant_words(document). The returned object is a frozenset of stemmed tokens derived from document.headings (possibly empty).
3. Invoke AbstractSummarizer._get_best_sentences with:
    - sentences (iterable of sentence objects),
    - sentences_count (selection policy),
    - rating callable: self._rate_sentence,
    - positional arg: significant_words
   Internally _get_best_sentences will call self._rate_sentence(sentence, significant_words) for each sentence.
4. Return the tuple produced by _get_best_sentences — the selected sentence objects in document order.

## Args:
    document (object):
        A parsed document-like object with:
        - document.sentences: a finite iterable (list/tuple/generator) of sentence objects.
        - document.headings: an iterable (may be empty) of heading objects.
        - Each sentence and heading object must expose attribute `words` (an iterable of tokens acceptable to normalization/stemming).
        No additional validation is performed by this method; attribute access errors will propagate.
    sentences_count (int or callable):
        Selection request forwarded unchanged to _get_best_sentences. Acceptable forms:
        - int n: commonly interpreted by helper ItemsCount to mean "top n".
        - A callable selector that accepts an iterable of per-sentence info objects (as required by _get_best_sentences).
        The method does not coerce or validate this argument itself; refer to AbstractSummarizer._get_best_sentences for full semantics.

## Returns:
    tuple:
        A tuple of sentence objects selected from document.sentences, ordered by their original position in the document. If no sentences are selected (e.g., empty input or selector chooses none), an empty tuple is returned.

## Raises:
    Propagated exceptions only (this method does not raise new exceptions itself). Common sources:
    - AttributeError / TypeError if document, its headings, sentences, or their .words attributes are missing or of unexpected types.
    - Exceptions from the stemmer invoked during _compute_significant_words/_rate_sentence (e.g., from normalize/stem functions).
    - AssertionError, KeyError, ValueError, TypeError from AbstractSummarizer._get_best_sentences or the provided count/rating callables.
    All such errors are propagated unchanged.

## State Changes:
Attributes READ:
    - self._null_words (indirectly, via _compute_significant_words and _is_null_word)
    - self._stemmer (indirectly, via self.stem_word called inside helpers)
    - self.stem_word (method invoked by helpers)
Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - The instance must have been constructed with a callable stemmer (enforced by AbstractSummarizer.__init__).
    - document.headings and document.sentences must be present and finite; if they are generator objects they will be fully consumed.
    - sentence and heading objects must expose .words iterables.
    - sentences_count must be meaningful to _get_best_sentences (see that helper's contract).

Postconditions:
    - The returned tuple contains zero or more sentences drawn from document.sentences in original document order.
    - No mutation of the summarizer instance or the document is performed by this method.

## Edge cases and notes:
    - Empty headings: _compute_significant_words will yield an empty frozenset; in that case _rate_sentence will score every sentence as zero, and the selection helper will decide which (if any) sentences to return based on the count policy.
    - Empty sentences iterable: returns an empty tuple.
    - Iterables are consumed: passing generators for headings or sentences will exhaust them.
    - The rating callable receives significant_words as a single positional argument after the sentence (i.e., called as _rate_sentence(sentence, significant_words)).
    - Because this method delegates heavy work, any custom behavior must be provided by overriding the helpers (_compute_significant_words, _rate_sentence) or by providing compatible count/rating callables.

## Side Effects:
    - Exhausts/consumes the provided document.sentences and document.headings iterables.
    - No I/O, network or external system calls are performed directly. Any such side effects may occur if user-provided stemmer, rating, or count callables perform them; those side effects will propagate.

### `sumy.summarizers.edmundson_title.EdmundsonTitleMethod._compute_significant_words` · *method*

## Summary:
Collects all words from the document's headings, stems each token, applies the module-level ffilter using the instance null-word predicate, and returns the unique results as an immutable frozenset; the method does not modify object state.

## Description:
Known callers and context
- EdmundsonTitleMethod.__call__(document, sentences_count) invokes this method during summarization to build the set of heading-derived keywords used for sentence scoring.
- EdmundsonTitleMethod.rate_sentences(document) also calls this method when producing per-sentence ratings.
- This method runs at the feature-extraction / scoring stage before sentence ranking and selection.

Why this is a separate method
- The sequence (collect → flatten → stem → filter → deduplicate) is reused by multiple methods; extracting it centralizes the logic for easier reuse and unit testing.
- Encapsulates heading-based token extraction so callers do not need to repeatedly express the same pipeline.

Implementation summary (call sequence reflected in the source)
1. Map attrgetter("words") over document.headings to obtain an iterable of heading.words iterables.
2. Flatten those iterables with itertools.chain by unpacking the mapped iterables into chain(*heading_words).
3. Map self.stem_word over the flattened token stream to obtain stems (each element is exactly whatever self.stem_word returns).
4. Pass the stem sequence to ffilter(self._is_null_word, ...). The method uses the module-level ffilter with the predicate self._is_null_word; the frozenset contains exactly the elements yielded by this ffilter call (see Constraints for notes about predicate polarity).
5. Return frozenset(significant_words).

## Args:
    document (object): Parsed document expected to expose:
        - headings: an iterable of heading objects.
          Each heading object must have a "words" attribute which itself is an iterable of tokens acceptable to self.stem_word.
    No default values.

## Returns:
    frozenset:
        - A frozenset of unique elements produced by self.stem_word for heading tokens that are included by ffilter(self._is_null_word, ...).
        - If no items are yielded through the pipeline (for example, if ffilter yields nothing), an empty frozenset() is returned.
        - Element types are exactly the return values of self.stem_word (no coercion to str is performed).

## Raises:
    AttributeError:
        - If document has no "headings" attribute, or if a heading object lacks a "words" attribute.
    TypeError:
        - If any heading.words is not iterable (iterating or chaining will raise TypeError).
        - If document.headings is empty, the code calls itertools.chain(*heading_words); unpacking an empty iterable results in chain() being called with zero arguments and raises TypeError. (Callers should ensure document.headings is non-empty or handle this exception.)
    Any exception propagated from:
        - self.stem_word(token): exceptions from normalization or the configured stemmer.
        - self._is_null_word(token): though in this class _is_null_word is implemented as a simple membership test (word in self._null_words), any unexpected error will propagate.
    Note: This method does not catch exceptions; they propagate to the caller.

## State Changes:
Attributes READ:
    - self._null_words (indirectly via self._is_null_word)
    - self._stemmer (indirectly via self.stem_word)
    - document.headings and each heading.words

Attributes WRITTEN:
    - None. The method does not mutate self or the document.

## Constraints:
Preconditions:
    - The instance must have been constructed with a callable stemmer so that self.stem_word is callable (AbstractSummarizer enforces this).
    - document.headings must be an iterable of heading-like objects; each heading must expose an iterable words attribute.
    - Tokens yielded from heading.words must be acceptable inputs for normalize_word/stem_word.

Postconditions:
    - The instance state is unchanged.
    - The returned frozenset contains exactly the unique values yielded by ffilter(self._is_null_word, map(self.stem_word, chain(*map(attrgetter("words"), document.headings)))).

Notes about ffilter and predicate polarity:
    - This method delegates filtering to the module-level ffilter called with predicate self._is_null_word. The frozenset contains whatever elements ffilter yields; implementers reproducing this behavior should consult the concrete ffilter implementation in this codebase to determine whether the predicate selects or excludes items (i.e., whether ffilter keeps items where predicate returns True or where it returns False).
    - In this class, _is_null_word is implemented as "return word in self._null_words", so the predicate tests membership in the instance null-word set.
    - To reproduce the exact project behavior, use the same ffilter utility with the same predicate.
    
## Side Effects:
    - No I/O or network activity.
    - No mutation of input objects; document and heading objects are iterated but not modified.
    - No global state is modified.

### `sumy.summarizers.edmundson_title.EdmundsonTitleMethod._is_null_word` · *method*

## Summary:
Return whether a given word belongs to the set/collection of null words configured for this summarizer instance.

## Description:
This predicate is used when computing "significant" words for the title-based Edmundson summarizer. Known callers:
- EdmundsonTitleMethod._compute_significant_words — passed as the predicate to ffilter to include/exclude heading words during the preprocessing stage of summarization.
Invocation context: called while the summarizer processes document headings inside the summarization pipeline (EdmundsonTitleMethod.__call__), specifically when building the set of words considered significant for sentence scoring.

Why this is a separate method:
- It encapsulates the membership logic so it can be passed as a first-class predicate to filtering utilities (ffilter) and keeps _compute_significant_words concise.
- Centralizes the null-word membership check so changes to null-word semantics (e.g., normalization or logging) can be made in one place.

## Args:
    word (str): A single word (typically already stemmed) to test for membership in the null-words collection. Expected to be a hashable object when the underlying collection requires it.

## Returns:
    bool: True if the provided word is present in self._null_words, False otherwise.

## Raises:
    None explicitly.
    - The method performs a direct membership test (word in self._null_words). Any exceptions raised by that operation (for example, TypeError if the types are incompatible with membership testing for the configured collection) are not caught here and will propagate.

## State Changes:
    Attributes READ:
        self._null_words
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - self._null_words must be set on the instance (initialized in __init__) and should be a container that supports the membership operator ('in') — common choices are set, frozenset, list, or tuple.
        - word should be of a type compatible with membership testing against self._null_words (commonly a string or a stem token).

    Postconditions:
        - No changes to the instance state or the input arguments.
        - A boolean value reflecting the membership test is returned.

## Side Effects:
    - None. The method performs a pure membership check and does not perform I/O, logging, or mutate external state.

### `sumy.summarizers.edmundson_title.EdmundsonTitleMethod._rate_sentence` · *method*

## Summary:
Count how many words in the given sentence have stems that appear in the provided set of significant stems; does not modify object state.

## Description:
Known callers and invocation context:
- EdmundsonTitleMethod.__call__: passes this method as the rating callable to AbstractSummarizer._get_best_sentences during the summarization pipeline. At that stage the method is invoked repeatedly to score sentences so top sentences can be selected for the final summary.
- EdmundsonTitleMethod.rate_sentences: iterates all sentences in a document and calls this method to produce a mapping of sentence -> integer rating (used for diagnostics or alternative selection strategies).
- Abstract lifecycle stage: invoked during the "score each sentence" step of the summarizer's __call__ implementation, after significant_words have been computed (from document headings) and before top-N selection.

Why this is a separate method:
- Encapsulates the per-sentence scoring rule (count of matching heading-derived stems) so the same logic can be reused by the batch scorer (rate_sentences) and the ranking helper (_get_best_sentences) without duplication.
- Improves testability and separation of concerns: the method focuses only on computing a numeric score for a single sentence given a precomputed set of significant stems.

## Args:
    sentence (object): An object representing a sentence. Required to expose a public attribute or property .words which is an iterable of tokens (commonly strings or bytes). Each token will be passed to self.stem_word.
    significant_words (collections.abc.Container): A container (e.g., frozenset or set) containing stem values (the same kind that self.stem_word returns). The method uses membership testing (token_stem in significant_words).

## Returns:
    int: Non-negative integer equal to the number of tokens in sentence.words whose stem (self.stem_word(token)) is present in significant_words.
    - Typical values: 0 (no matches) up to len(list(sentence.words)) (all tokens match).
    - Edge-case: returns 0 for an empty sentence.words iterable.

## Raises:
    Any exception raised by self.stem_word(token) is propagated to the caller (for example, exceptions from normalization or the configured stemmer).
    TypeError is raised if sentence has no .words attribute or if sentence.words is not iterable.
    TypeError (or other exceptions) may be raised if membership testing fails because the stem returned by self.stem_word is unhashable or if significant_words does not support membership testing.

## State Changes:
    Attributes READ:
        - self._stemmer (indirectly, via calling self.stem_word) — the configured stemmer callable is consulted when stemming tokens.
    Attributes WRITTEN:
        - None. This method does not modify the instance or inputs.

## Constraints:
    Preconditions:
        - The instance must have been constructed with a callable stemmer (AbstractSummarizer.__init__ enforces this).
        - sentence must provide an iterable .words attribute.
        - Items returned by self.stem_word(token) must be comparable for membership against significant_words (typically hashable if significant_words is a set/frozenset).
        - significant_words should be a container supporting membership testing (e.g., set, frozenset, or other container).

    Postconditions:
        - No attributes on self or on the sentence/significant_words objects are modified.
        - The return value is an integer >= 0 representing the match count.

## Side Effects:
    - None within this method: no I/O or external service calls are made.
    - The only external call is to self.stem_word(token); any side effects are those of the configured stemmer callable (if it has side effects), and are not caused by this method itself.

### `sumy.summarizers.edmundson_title.EdmundsonTitleMethod.rate_sentences` · *method*

## Summary:
Compute and return a per-sentence score mapping where each sentence is scored by how many stemmed heading-derived "significant" words it contains; does not modify object state.

## Description:
This method is a convenience/utility that evaluates every sentence in the supplied document and returns a dictionary mapping each sentence object to an integer score. It is typically invoked in the sentence-scoring stage of the summarization pipeline when a caller needs the raw scores for all sentences (for example, for debugging, analysis, or custom selection logic). Within this class, the public call operator (__call__) uses a different internal path (_get_best_sentences with _rate_sentence) and therefore does not rely on rate_sentences; having this method separate provides:
- A straightforward way to obtain the complete score map (useful for testing or external code).
- A single place that enumerates sentences and applies the per-sentence rating logic, avoiding duplication.

Known callers / usage context:
- External consumers of EdmundsonTitleMethod that need the full sentence->score mapping.
- Diagnostic/testing code that verifies how sentences were scored.
- Not called by this class's __call__ implementation (which uses a different flow).

## Args:
    document (object): Document-like object with the following expected attributes:
        - sentences: an iterable of sentence objects. Each sentence object must be usable as a dictionary key (hashable) and must expose an iterable attribute 'words' (sequence of strings/tokens).
        - headings: (indirectly required) iterable of heading objects each exposing a 'words' attribute; used by the called helper _compute_significant_words.
    No default values.

## Returns:
    dict: A mapping {sentence_object: score_int} where:
        - score_int (int) is >= 0 and equals the count of stemmed words in sentence.words that appear in the frozenset returned by _compute_significant_words(document).
        - The returned dict contains an entry for every element yielded by document.sentences.
        - If document.sentences is empty, returns an empty dict.

Edge-case return values:
    - If no significant words are found, all scores will be 0 (but present for each sentence).
    - If document.sentences contains duplicate object instances, later entries overwrite earlier ones per normal dict semantics.

## Raises:
    This method does not explicitly raise new exceptions; however it will propagate exceptions raised by:
        - document attribute access (AttributeError) if document lacks expected attributes.
        - Iteration over document.sentences or sentence.words if those iterables raise.
        - Any exceptions from self._compute_significant_words or self._rate_sentence (e.g., TypeError if sentence objects are unhashable when used as dict keys).

## State Changes:
Attributes READ:
    - self._null_words (read indirectly by _compute_significant_words)
    - any attributes used by the helper methods invoked (for example, self.stem_word via AbstractSummarizer when those helpers are executed)
Attributes WRITTEN:
    - None. This method does not modify self or modify the passed document.

## Constraints:
Preconditions:
    - document must have attribute 'sentences' that yields sentence objects.
    - Each sentence object must have an iterable attribute 'words' (strings/tokens).
    - Sentence objects must be hashable (suitable as dict keys).
    - document must have attribute 'headings' with heading objects exposing 'words' (required by _compute_significant_words).

Postconditions:
    - The returned dict contains one entry per element in document.sentences.
    - For every returned score value s: s is equal to sum(w in significant_words for w in map(self.stem_word, sentence.words)), where significant_words is the frozenset produced by _compute_significant_words(document).
    - No mutation to self or document is performed by this method.

## Side Effects:
    - No I/O is performed.
    - No external service calls.
    - No mutation of objects outside of creating and returning the mapping (the method only allocates and returns a new dict).
    - Underlying helper methods may perform reads of self._null_words and call self.stem_word, but they do not mutate shared state.

