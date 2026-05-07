# `edmundson_cue.py`

## `sumy.summarizers.edmundson_cue.EdmundsonCueMethod` · *class*

## Summary:
A concrete summarizer implementing Edmundson's cue-based scoring: ranks sentences by the difference between counted bonus-word hits and stigma-word hits (weighted), and selects top sentences via the base class selection helper.

## Description:
EdmundsonCueMethod scores sentences using two lexicons: bonus_words (words that increase sentence score) and stigma_words (words that decrease sentence score). For each sentence it stems tokens using the summarizer's configured stemmer, counts how many stems appear in each lexicon, computes a numeric score = (bonus_count * bonus_word_weight) - (stigma_count * stigma_word_weight), and delegates selection of the top-k sentences to the AbstractSummarizer._get_best_sentences helper.

Scenarios to instantiate:
- When building an extractive summarizer that selects sentences according to explicit cue-word lexicons (e.g., positive/negative indicator lists, topic-specific boosters, or stop-word-like stigmas).
- Typical factory/pipeline code constructs an instance by supplying a stemmer and two lexicon containers and then calls the instance to produce a summary for a parsed document.

Motivation and responsibility boundary:
- Encapsulates Edmundson's cue-word scoring strategy (lexicon-based, stemmed membership counts) as a reusable Summarizer implementation.
- Leaves sentence selection policy (how many sentences to pick / percentage rules) to the shared _get_best_sentences helper provided by AbstractSummarizer.
- Does not perform tokenization, sentence parsing, or any I/O; it expects a parsed Document with sentence objects.

## State:
Attributes (instance-level)
- _stemmer (callable) — inherited from AbstractSummarizer
  - Type: callable(str) -> any
  - Constraint: must be callable; AbstractSummarizer.__init__ enforces this and raises ValueError if not.
  - Invariant: remains callable for the instance lifetime unless mutated externally.
  - Purpose: used by stem_word to normalize tokens before membership checks.

- _bonus_words
  - Type: container supporting membership test (e.g., set, list, dict keys). Recommended: set of strings.
  - Expected contents: tokens in the same normalized/stemmed form returned by stem_word (i.e., stems).
  - Valid values: any object for which "token in _bonus_words" is meaningful.
  - Invariant: treated as a read-only lexicon by the class (class methods do not mutate it).
  - Usage: each stemmed token from a sentence is tested for membership; when present, it increments the bonus count.

- _stigma_words
  - Type: same as _bonus_words
  - Expected contents: stems that penalize sentences when present.
  - Invariant: read-only membership container used for stigma counts.

Class invariants:
- _stemmer is callable (ensured by parent).
- _bonus_words and _stigma_words are membership containers consistent with the output type of stem_word (i.e., they should contain stems, not raw tokens).
- Methods do not mutate the lexicon containers or base-class state.

## Lifecycle:
Creation
- Required constructor arguments:
  - stemmer: callable to produce stems from normalized tokens (forwarded to AbstractSummarizer.__init__).
  - bonus_words: membership container of stems that award positive points.
  - stigma_words: membership container of stems that award negative points.
- Behavior:
  - The constructor delegates stemmer validation to AbstractSummarizer.__init__; if stemmer is not callable, ValueError("Stemmer has to be a callable object") is raised.

Usage
- Typical invocation order:
  1. Instantiate the summarizer with a stemmer and two lexicons.
  2. Prepare a parsed Document object whose .sentences is an iterable of sentence objects.
     - Each sentence object must expose .words: an iterable of tokens acceptable to stem_word (i.e., convertible to unicode and normalizable).
  3. Produce a summary by calling the instance:
     - The callable form: instance(document, sentences_count, bonus_word_weight, stigma_word_weight)
       - document: parsed document with .sentences
       - sentences_count: selection policy accepted by AbstractSummarizer._get_best_sentences (commonly an int or "30%")
       - bonus_word_weight, stigma_word_weight: numeric weights (int or float); no enforced sign or range
     - Internally, __call__ rates sentences via _rate_sentence (which uses stem_word and _count_words) and delegates selection to _get_best_sentences.
  4. Optionally compute scores for all sentences without selecting top ones by calling rate_sentences(document, bonus_word_weight=1, stigma_word_weight=1) which returns a mapping sentence -> score.

Destruction / cleanup
- No special cleanup required by this class.
- If lexicon containers or the stemmer hold external resources, the caller/subclass is responsible for their lifecycle.

## Method Map:
graph TD
    Init[__init__(stemmer, bonus_words, stigma_words)] --> SetState[_bonus_words/_stigma_words + super().__init__(stemmer)]
    Call[__call__(document, sentences_count, bonus_weight, stigma_weight)] --> GetBest[_get_best_sentences(...)]
    GetBest --> RateFunc[_rate_sentence bound as rating(sentence, bonus_weight, stigma_weight)]
    RateFunc --> RateSentence[_rate_sentence(sentence, bonus_weight, stigma_weight)]
    RateSentence --> StemMap[map(self.stem_word, sentence.words)]
    StemMap --> Count[_count_words(stem_iterator)]
    Count --> CountsReturn[(bonus_count, stigma_count)]
    CountsReturn --> ComputeScore[score = bonus_count*bonus_weight - stigma_count*stigma_weight]
    RateSentence --> ReturnScore[return float/int score]
    Call --> ReturnSelection[returns tuple of selected sentence objects]

## Behavior of public and helper methods (summary of contracts)
- __init__(stemmer, bonus_words, stigma_words)
  - Effects: stores _bonus_words and _stigma_words and delegates stemmer validation to AbstractSummarizer.
  - Raises: ValueError if stemmer is not callable (raised by AbstractSummarizer.__init__).

- __call__(document, sentences_count, bonus_word_weight, stigma_word_weight)
  - Inputs:
    - document: object exposing .sentences (iterable of sentence objects).
    - sentences_count: selection policy accepted by _get_best_sentences (commonly int or "30%").
    - bonus_word_weight, stigma_word_weight: numbers (int or float).
  - Behavior:
    - Calls _get_best_sentences(document.sentences, sentences_count, self._rate_sentence, bonus_word_weight, stigma_word_weight)
    - Returns: whatever _get_best_sentences returns — specifically a tuple of selected sentence objects in original document order.
  - Exceptions:
    - Propagates exceptions from _get_best_sentences (AssertionError, KeyError, TypeError, ValueError) and from _rate_sentence (see below).

- _rate_sentence(sentence, bonus_word_weight, stigma_word_weight)
  - Inputs:
    - sentence: object exposing .words (iterable of tokens).
    - bonus_word_weight, stigma_word_weight: numeric weights.
  - Behavior:
    - Stems tokens: words = map(self.stem_word, sentence.words)
    - Counts matches: calls _count_words(words) to obtain (bonus_count, stigma_count)
    - Computes numeric score: bonus_count * bonus_word_weight - stigma_count * stigma_word_weight
    - Returns: numeric score (int or float depending on counts and weights)
  - Exceptions:
    - Propagates exceptions from stem_word (e.g., normalization/stemmer errors).
    - If sentence.words is not iterable, TypeError will be raised when iterating.
    - If weights are non-numeric such that arithmetic fails, a TypeError may be raised.

- _count_words(words)
  - Inputs:
    - words: an iterable of stemmed token values (iterator or sequence).
  - Behavior:
    - Iterates the provided iterable once, increments counters when a token is found in _bonus_words / _stigma_words.
    - Returns a 2-tuple: (bonus_words_count:int, stigma_words_count:int)
  - Notes:
    - The method uses membership tests (token in lexicon); lexicons should provide efficient membership semantics (set recommended).
    - The method consumes its iterator argument; callers should not expect reuse of the iterator.

- rate_sentences(document, bonus_word_weight=1, stigma_word_weight=1)
  - Inputs:
    - document: object with .sentences
    - bonus_word_weight, stigma_word_weight: numeric weights, defaulting to 1
  - Behavior:
    - Returns a dict mapping each sentence object in document.sentences to its numeric score computed by _rate_sentence.
  - Exceptions:
    - If sentence objects are unhashable, using them as dict keys will raise TypeError.
    - Propagates exceptions from _rate_sentence and its callees.

## Raises:
- From __init__:
  - ValueError("Stemmer has to be a callable object") if stemmer is not callable (raised by AbstractSummarizer.__init__).

- From runtime methods (propagated, not newly created here):
  - Any exception raised by stem_word (e.g., unicode conversion errors or stemmer exceptions).
  - AssertionError / KeyError / TypeError / ValueError potentially raised by AbstractSummarizer._get_best_sentences when selection/rating contract is violated (for example, passing a mapping as rating while also supplying *args, or providing incompatible count).
  - TypeError if sentence.words is not iterable, or if weights are non-numeric in arithmetic.
  - TypeError if using rate_sentences with unhashable sentence objects (dict key requirement).

## Example (usage pattern described in prose)
1. Construct:
   - Provide a stemmer callable and two lexicon containers holding stems (recommended: sets).
   - Example parameters (conceptual): stemmer_callable, bonus_words_set, stigma_words_set.
   - The constructor will validate the stemmer's callability.

2. Produce a summary:
   - Prepare a parsed document whose .sentences is an iterable of sentence objects; each sentence must expose .words (an iterable of raw tokens acceptable to the stemmer).
   - Invoke the summarizer as a callable with:
     - document
     - a selection policy (commonly an integer number of sentences to select, or a percentage string accepted by the shared ItemsCount wrapper)
     - a numeric bonus_word_weight and stigma_word_weight
   - The call returns a tuple of selected sentence objects in their original document order.

3. Inspect scores:
   - Use rate_sentences(document) to obtain a mapping from each sentence to its numeric score (useful for debugging or custom selection strategies).

Cleanup:
- No explicit cleanup required; no context-manager protocol. If external resources are used by the stemmer or lexicon objects, handle their lifecycle outside this class.

### `sumy.summarizers.edmundson_cue.EdmundsonCueMethod.__init__` · *method*

## Summary:
Initializes summarizer state by delegating stemmer validation to the base class and storing the bonus- and stigma-word lexicons on the instance.

## Description:
This constructor is called when a concrete Edmundson cue-based summarizer instance is created (typically by pipeline/factory code that selects and configures a summarizer). It runs during object construction, before any summarization methods (__call__, rate_sentences, etc.) are used.

Known callers and context:
- Factory or pipeline code that constructs an EdmundsonCueMethod with a chosen stemmer and two lexicon containers.
- Tests or library user code that instantiates the summarizer as part of preparing a summarization pipeline.
- The normal lifecycle: instantiate (this __init__), then call the instance with a parsed Document to produce summaries.

Why this logic is a separate method:
- Delegates stemmer validation to AbstractSummarizer.__init__, centralizing stemmer-related checks and behavior in the base class.
- Keeps construction responsibilities clear: base class handles normalization/stemmer wiring; this subclass stores algorithm-specific lexicons.
- Separates concerns so subclasses and the base class can be maintained/tested independently.

## Args:
    stemmer (callable): A callable that accepts a single normalized token and returns its stem. Must be callable; AbstractSummarizer.__init__ enforces this and raises ValueError if it is not.
    bonus_words (container): A membership container (e.g., set, list, dict keys) of normalized/stemmed tokens that increase a sentence's score. Recommended: set of strings matching the stemmer output.
    stigma_words (container): A membership container of normalized/stemmed tokens that decrease a sentence's score. Recommended: set of strings matching the stemmer output.

## Returns:
    None

## Raises:
    ValueError: If stemmer is not callable. (Raised by AbstractSummarizer.__init__, with message "Stemmer has to be a callable object".)
    (Note: this constructor does not itself call the stemmer; other runtime exceptions will only occur later when stemmer or lexicon usage happens.)

## State Changes:
Attributes READ:
    - None (the constructor does not read existing instance attributes).

Attributes WRITTEN:
    - self._stemmer: set by AbstractSummarizer.__init__ invoked via super(...).__init__(stemmer).
    - self._bonus_words: set to the provided bonus_words container.
    - self._stigma_words: set to the provided stigma_words container.

## Constraints:
Preconditions:
    - The caller must pass a callable for stemmer; otherwise AbstractSummarizer.__init__ will raise ValueError.
    - bonus_words and stigma_words should be containers that support membership testing (token in container). If they are not (e.g., None), later methods that perform membership checks will raise TypeError or similar.

Postconditions:
    - After return, self._stemmer is assigned and is callable.
    - After return, self._bonus_words references the provided bonus_words object.
    - After return, self._stigma_words references the provided stigma_words object.
    - No further validation of lexicon contents is performed; methods that use these attributes expect their items to be compatible with the output of stem_word.

## Side Effects:
    - No I/O, network, or global state mutation performed.
    - No mutation of provided lexicon containers is performed by the constructor (they are stored by reference).
    - Any resource management for stemmer or lexicon objects (if they require it) is the caller's responsibility.

### `sumy.summarizers.edmundson_cue.EdmundsonCueMethod.__call__` · *method*

## Summary:
Delegates to the shared selection helper to produce a summary: it scores each sentence with the local cue-based rating function (using the provided bonus and stigma weights) and returns the highest-rated sentences in their original document order.

## Description:
This method is the concrete callable entry-point for the Edmundson cue-based summarizer. It is intended to be called by summarization pipelines or client code after a document has been parsed into sentence objects. Typical callers:
- High-level summarization pipeline code that constructs an EdmundsonCueMethod and invokes it to produce a summary.
- Unit tests and example scripts that validate cue-based scoring and sentence selection.

Role and rationale:
- It composes algorithm-specific scoring (self._rate_sentence) with the reusable selection/sorting logic in AbstractSummarizer._get_best_sentences instead of reimplementing sorting/selection. This keeps scoring separate from selection mechanics and reuses tested helper code.

Call flow:
- Called as instance(document, sentences_count, bonus_word_weight, stigma_word_weight)
- Forwards document.sentences, sentences_count, and the callable rating self._rate_sentence to _get_best_sentences
- Passes bonus_word_weight and stigma_word_weight as positional arguments that _get_best_sentences will forward to the rating callable when evaluating each sentence
- Returns the result tuple produced by _get_best_sentences

## Args:
    document (object): Parsed document containing an iterable attribute `sentences`. Each sentence should be an object with:
        - .words: an iterable of tokens (strings/bytes) that stem_word can process.
    sentences_count (int | str | callable): Selection policy accepted by AbstractSummarizer._get_best_sentences:
        - int: select this many top sentences (non-negative).
        - str like "30%": percentage selector interpreted by ItemsCount.
        - callable: selector function that accepts sorted sentence infos and returns selected infos.
    bonus_word_weight (int | float): Numeric multiplier applied to the count of matched bonus words when scoring a sentence. May be negative or zero.
    stigma_word_weight (int | float): Numeric multiplier applied to the count of matched stigma words when scoring a sentence. May be negative or zero.

## Returns:
    tuple: A tuple of sentence objects selected as the summary, ordered by their original position in document.sentences.
        - Empty tuple if no sentences are selected or document.sentences is empty.
        - If sentences_count requests more items than available, the selection callable typically returns all available sentences.
        - The returned objects are the same sentence instances from the input document (no copies).

## Raises:
    AttributeError: If `document` does not expose `sentences`, or if a sentence lacks the expected `.words` attribute used later by _rate_sentence.
    AssertionError: May propagate from _get_best_sentences if an internal invariant is violated (e.g., rating provided as a mapping while also passing args).
    KeyError: Not applicable here because this method passes a callable rating, but may still propagate from downstream helpers in other contexts.
    Any exception raised by:
        - self._rate_sentence (including exceptions from stem_word, normalize_word, or the configured stemmer),
        - AbstractSummarizer._get_best_sentences or the selection callable (ItemsCount or custom selector).
    All such exceptions propagate unchanged.

## State Changes:
    Attributes READ (directly or indirectly):
        - self._bonus_words: read by self._rate_sentence to count matching bonus tokens.
        - self._stigma_words: read by self._rate_sentence to count matching stigma tokens.
        - self._stemmer (via stem_word): invoked indirectly when _rate_sentence stems tokens.
    Attributes WRITTEN:
        - None. This method does not modify instance attributes or the input document.

## Constraints:
    Preconditions:
        - document.sentences must be a finite iterable (generator or list is acceptable).
        - Each sentence must have a `.words` iterable whose elements are acceptable to normalize_word and the configured stemmer.
        - bonus_word_weight and stigma_word_weight should be numeric; non-numeric types will lead to downstream errors when used in arithmetic.
        - sentences_count must be valid for _get_best_sentences (int, percentage string, or callable selector).

    Postconditions:
        - The method returns a tuple of sentence objects selected by rating and restored to document order, per the AbstractSummarizer._get_best_sentences contract.
        - The instance state and input document are unchanged.

## Side Effects:
    - Calls _get_best_sentences and _rate_sentence for scoring/selection; these calls can trigger the configured stemmer and normalization logic.
    - No file, network, or external I/O is performed by this method itself. Any I/O would come from user-supplied stemmers or selection callables.
    - Exceptions from user-provided callables propagate to the caller.

## Edge cases and examples:
    - Empty document.sentences -> returns ().
    - Sentence with empty sentence.words -> _rate_sentence will count zero bonus/stigma matches, yielding a score of 0 (unless weights are non-zero and other signal exists).
    - Negative weights -> negative bonus_word_weight will penalize sentences containing bonus words (allowed; behavior depends on caller intent).
    - sentences_count greater than number of sentences -> selection callable generally returns all sentences.

Example usage:
    summary_sentences = edmundson_instance(document, 3, bonus_word_weight=2, stigma_word_weight=1)
    # Returns up to 3 highest-scoring sentences as a tuple, ordered by original document order.

### `sumy.summarizers.edmundson_cue.EdmundsonCueMethod._rate_sentence` · *method*

## Summary:
Compute a numeric cue-based score for a sentence by counting configured bonus and stigma word occurrences (after stemming) and returning weighted difference; does not modify object state.

## Description:
This method is invoked during the scoring stage of the Edmundson cue-based summarizer. Known callers:
- EdmundsonCueMethod.__call__: used as the rating callable passed to the top-sentence selection routine when building a summary.
- EdmundsonCueMethod.rate_sentences: iterates document sentences and returns a mapping of sentence -> score.

Context/lifecycle:
- Called for each sentence when the summarizer computes per-sentence ratings prior to selecting the best sentences.
- It stems each token in the sentence and delegates membership counting to _count_words so that scoring (weights * counts) is kept separate from counting logic.

Why separate:
- Keeps scoring logic (application of weights) isolated from counting and stemming concerns.
- Allows reuse by rate_sentences and by selection helpers that require a rating function.
- Improves testability: counting and weighting are independent, simpler units to test.

## Args:
    sentence (object):
        A sentence-like object that exposes an iterable of tokens at attribute 'words' (i.e., sentence.words). The iterable may be any iterable or iterator of token values (strings or objects acceptable to the stemmer).
    bonus_word_weight (number):
        Numeric weight applied to each occurrence of a bonus word. Typical types: int or float. No implicit constraints are enforced by this method.
    stigma_word_weight (number):
        Numeric weight applied to each occurrence of a stigma word. Typical types: int or float.

## Returns:
    number:
        The computed score equal to (bonus_words_count * bonus_word_weight) - (stigma_words_count * stigma_word_weight).
        - If both counts are zero, returns 0 (or 0.0 if weights are floats).
        - Exact return type depends on operand types (e.g., int if all operands are ints, float otherwise).
        - For empty sentence.words the method returns 0 or 0.0 depending on weight types.

## Raises:
    AttributeError:
        If the provided sentence object has no attribute 'words' (accessing sentence.words triggers this).
    TypeError:
        - If sentence.words is not iterable (map will raise TypeError).
        - If membership testing in _count_words fails due to unhashable/unexpected token types, that TypeError (or other membership-related exception) will propagate.
        - If the provided weight arguments are not compatible with numeric multiplication with the integer counts (e.g., unsupported operand types for *), the resulting TypeError will propagate.
    Any exception raised by:
        - AbstractSummarizer.stem_word (for example, exceptions from normalize_word or from the configured stemmer callable).
        - EdmundsonCueMethod._count_words (membership-related errors or other exceptions that arise while iterating/counting).
    (This method does not raise new exception types of its own; it propagates exceptions from called helpers and Python operations.)

## State Changes:
Attributes READ:
    - self._stemmer (indirectly) — read when stem_word is invoked for each token.
    - self._bonus_words — read by _count_words to test membership.
    - self._stigma_words — read by _count_words to test membership.
Attributes WRITTEN:
    - None (the method does not modify any attributes on self).

## Constraints:
Preconditions:
    - The instance must be a properly-constructed EdmundsonCueMethod: AbstractSummarizer.__init__ must have set a callable stemmer.
    - self._bonus_words and self._stigma_words must be initialized and support membership testing (the in operator).
    - sentence must provide a 'words' attribute that is an iterable of tokens acceptable to normalize_word/stemmer.

Postconditions:
    - The method returns a numeric score as described in Returns.
    - No attributes of self are changed.
    - If the provided sentence.words was an iterator/generator, it will be consumed by this call (forwarding that consumed iterator to _count_words).

## Side Effects:
    - Consumes/iterates sentence.words; if sentence.words is a one-time iterator or generator, it will be exhausted by this method.
    - Calls self.stem_word for each token, which invokes the configured stemmer callable; any side effects from that stemmer (if it has them) will occur.
    - No I/O, network calls, or mutations of external objects are performed by this method itself.

### `sumy.summarizers.edmundson_cue.EdmundsonCueMethod._count_words` · *method*

## Summary:
Counts how many items from the provided iterable appear in the object's bonus and stigma collections and returns the two counts; does not modify object state.

## Description:
This helper computes the number of words in a single sentence that match the configured bonus and stigma word collections. Known callers:
- _rate_sentence: passes a stemmed iterable of words for a sentence and uses the returned counts to compute a sentence score.
- rate_sentences and __call__ (indirectly): these higher-level routines ultimately invoke _rate_sentence for each sentence.

This logic is separated into its own method to:
- Keep _rate_sentence focused on scoring logic (weights * counts) rather than membership counting.
- Make the counting behavior reusable and easier to unit-test in isolation.
- Allow different iterables (lists, generators, map objects) to be handled uniformly.

## Args:
    words (Iterable[str] or Iterator[str]):
        An iterable producing word tokens (typically stemmed strings). The method will iterate over this object once; if an iterator is passed it will be consumed.

## Returns:
    tuple[int, int]:
        A pair (bonus_words_count, stigma_words_count).
        - bonus_words_count: non-negative integer count of items from words that are present in self._bonus_words.
        - stigma_words_count: non-negative integer count of items from words that are present in self._stigma_words.
        If words is empty, both counts are 0. Duplicate occurrences in words are counted multiplicatively (each occurrence is counted).

## Raises:
    TypeError (propagated):
        May be raised if membership testing between items from words and the configured collections is invalid (for example, if either collection expects hashable items and a non-hashable item is tested, or if self._bonus_words / self._stigma_words do not support membership testing).
    (No explicit exceptions are raised by this method itself.)

## State Changes:
Attributes READ:
    - self._bonus_words
    - self._stigma_words

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - self._bonus_words and self._stigma_words must be initialized (e.g., set or list) and support membership testing using the in operator.
    - Items produced by words must be comparable (via equality or hashing as appropriate) to items stored in the bonus/stigma collections.

Postconditions:
    - Returns a tuple of two integers reflecting the counts described above.
    - Does not modify self or any external object.

## Side Effects:
    - No I/O or external service calls.
    - If words is a stateful iterator/generator, it will be advanced/exhausted by this method (consumer-visible mutation of the iterator).

### `sumy.summarizers.edmundson_cue.EdmundsonCueMethod.rate_sentences` · *method*

## Summary:
Compute and return a mapping from each sentence in the document to its Edmundson cue score, leaving the summarizer instance and the document unmodified.

## Description:
This convenience method iterates document.sentences and computes a numeric cue-based rating for each sentence by delegating to the instance method that implements the Edmundson cue scoring logic. Known callers and context:
- External callers (analysis, debugging, evaluation code, or UI tooling) that need per-sentence scores for inspection or downstream processing.
- Not used by the class's __call__ path (the summarizer's runtime selection uses _rate_sentence directly with _get_best_sentences); rate_sentences exists to expose the complete sentence→score mapping as a simple API.

Why this is a separate method:
- Provides a reusable, explicit operation for obtaining all sentence scores in one pass rather than forcing callers to call the lower-level _rate_sentence for each sentence themselves.
- Keeps score-collection logic decoupled from selection/aggregation (_get_best_sentences) so callers can inspect or persist raw scores without performing selection.

## Args:
    document (object): A parsed document object exposing an iterable attribute `sentences`. Each sentence object is expected to expose an iterable attribute `words` (tokens). The method does not validate types beyond relying on these attributes being present and iterable.
    bonus_word_weight (int|float, optional): Multiplier applied to the count of bonus words when computing a sentence score. Defaults to 1. Typical use: non-negative numeric values; no runtime type enforcement is performed.
    stigma_word_weight (int|float, optional): Multiplier applied to the count of stigma words when computing a sentence score. Defaults to 1. Typical use: non-negative numeric values; no runtime type enforcement is performed.

## Returns:
    dict: A mapping where each key is a sentence object from document.sentences and the corresponding value is that sentence's numeric Edmundson cue score.
    - Score formula (as computed transitively by _rate_sentence):
        score = (bonus_words_count * bonus_word_weight) - (stigma_words_count * stigma_word_weight)
    - Possible values:
        - Integer if weights are integers and counts are integer.
        - Float if any weight is float.
    - Edge cases:
        - Returns an empty dict when document.sentences is empty.
        - If duplicate sentence objects (identical object identity) appear, later entries will overwrite earlier ones because dict keys must be unique.

## Raises:
    TypeError: If a sentence object is unhashable (cannot be used as a dict key) the dict construction will raise TypeError.
    Any exception raised by self._rate_sentence, or by methods it calls (for example stem_word / normalize_word), is propagated unchanged. Typical propagated exceptions include:
        - Exceptions from the configured stemmer callable (e.g., ValueError, TypeError).
        - Exceptions from token normalization (e.g., Unicode-related errors) when tokens cannot be normalized.
    No exceptions are explicitly raised by rate_sentences itself.

## State Changes:
    Attributes READ:
        - self._bonus_words (used transitively by _count_words through _rate_sentence)
        - self._stigma_words (used transitively by _count_words through _rate_sentence)
        - self._stemmer (used transitively by stem_word called inside _rate_sentence)
    Attributes WRITTEN:
        - None. The method does not mutate self or the document; it only calls pure/mutable-safe helpers to compute scores.

## Constraints:
    Preconditions:
        - document must have an attribute `sentences` that is iterable.
        - Each sentence in document.sentences must have an attribute `words` that is iterable of tokens.
        - Tokens yielded by sentence.words must be acceptable inputs to the project's normalize/stem pipeline (to_unicode, .lower(), and the configured stemmer).
        - The summarizer instance must have been constructed correctly (self._stemmer callable and self._bonus_words/self._stigma_words initialized).
    Postconditions:
        - Returns a dict mapping each iterated sentence to a numeric score computed as described.
        - No mutation of the summarizer instance or the document is performed by this method.

## Side Effects:
    - No I/O performed and no external services contacted.
    - May execute arbitrary user-provided code indirectly via the configured stemmer callable (side effects from a non-pure stemmer will occur and will propagate).
    - No mutation of objects outside self is performed by this method itself, but objects reachable from stemmer or token normalization may be affected if those callables have side effects.

## Implementation notes / performance:
    - Time complexity: O(S * W * M) where S is the number of sentences, W is the average words per sentence, and M is the average cost of membership checks against _bonus_words/_stigma_words and the cost of the stemmer. If _bonus_words/_stigma_words are sets, membership is O(1); if lists, membership is O(size).
    - Memory: builds and returns a dict with one entry per input sentence; for large documents consider streaming scoring or using a mapping-like interface instead of materializing the entire dict.

