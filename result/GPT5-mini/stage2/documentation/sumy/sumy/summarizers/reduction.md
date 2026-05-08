# `reduction.py`

## `sumy.summarizers.reduction.ReductionSummarizer` · *class*

*No documentation generated.*

### `sumy.summarizers.reduction.ReductionSummarizer.stop_words` · *method*

## Summary:
Configure the instance's stop-word set by normalizing each supplied token and storing the result as an immutable frozenset on self._stop_words (this is the stop_words property setter).

## Description:
Known callers and context:
- Intended to be called by client or pipeline configuration code before performing summarization (for example, during summarizer construction or setup).
- ReductionSummarizer._to_words_set consults self._stop_words at runtime to filter tokens when building per-sentence word lists; therefore callers should set stop words prior to invoking the summarizer on documents.
- This method is the setter for the stop_words property (declared with @stop_words.setter) so assignment via the property updates the internal set.

Why this is a separate setter:
- Centralizes the canonicalization step (normalize_word) and enforces immutability and efficient membership checks (frozenset) in one place.
- Prevents repeated normalization during runtime filtering by normalizing once at configuration time.

## Args:
    words (iterable):
        - An iterable of tokens to be treated as stop words.
        - Element types: typically str (text) or bytes; any value acceptable to self.normalize_word is valid.
        - Required: yes. Passing None or a non-iterable will cause a runtime TypeError when iteration occurs.
        - Caution: passing a single string will be treated as an iterable of characters (each character will be normalized separately). Use a sequence of tokens (e.g., list of words) when intending word-level stop words.

## Returns:
    None
    - The method performs an in-place configuration change; no value is returned to the caller. The effect is visible through self._stop_words or the stop_words property getter.

## Raises:
    TypeError:
        - If words is not iterable, a TypeError will be raised when the iterable is consumed while building the frozenset.
    Any exception raised by self.normalize_word:
        - normalize_word (provided by AbstractSummarizer) typically converts input to text and lowercases it; errors from that conversion (e.g., Unicode-related errors, AttributeError if input cannot be processed) will propagate unchanged.
    (The setter itself does not explicitly raise custom exceptions.)

## State Changes:
    Attributes READ:
        - None of the instance data attributes are read for decision-making. The method does call the instance method normalize_word but does not read other self.<attr> fields.
    Attributes WRITTEN:
        - self._stop_words: overwritten with a frozenset containing the normalized tokens produced from the input iterable.

## Constraints:
    Preconditions:
        - The instance provides a working normalize_word method (AbstractSummarizer supplies a normalize_word implementation that returns to_unicode(word).lower()).
        - words must be a finite iterable; extremely large iterables will consume memory proportional to the number of unique normalized tokens when the frozenset is built.
    Postconditions:
        - self._stop_words is a frozenset containing the normalized forms of each element from words.
        - Duplicate normalized tokens are eliminated (set semantics).
        - Subsequent calls to ReductionSummarizer._to_words_set will filter tokens by membership in this frozenset until it is changed again.

## Side Effects:
    - No I/O or external service calls.
    - Calls self.normalize_word for every element in words; any side effects or exceptions originating from normalize_word will surface here.
    - Mutates only the instance attribute self._stop_words; the input iterable and external objects are not modified by this method.
    - Performance note: the entire iterable is consumed to materialize the frozenset; memory usage equals the number of unique normalized tokens.

### `sumy.summarizers.reduction.ReductionSummarizer.__call__` · *method*

## Summary:
Computes sentence-level ratings for the given document and returns whatever selection _get_best_sentences produces; does not modify the summarizer instance.

## Description:
This is the public callable entry point used to produce a summary from a Document. It performs two steps:
1. Delegates sentence scoring to rate_sentences(document).
2. Delegates selection of top sentences to _get_best_sentences(document.sentences, sentences_count, ratings) and returns that result.

Known callers / context:
- Client code or pipelines that instantiate a summarizer and invoke it as a callable (e.g., summary_sentences = summarizer(document, N)).
- The method is invoked during the summarization stage where a parsed Document (with sentences) must be reduced to a smaller set of representative sentences.

Why this logic is a separate method:
- Provides a concise, uniform callable API for summarizers.
- Keeps orchestration (score then select) separate from the concrete scoring and selection implementations, enabling easy subclassing and testing of components independently.

## Args:
    document (object): Required. An object representing the document to summarize. Must provide a .sentences iterable/sequence. Each sentence is expected to satisfy the assumptions of rate_sentences (for example, having a .words iterable).
    sentences_count (int): Number of sentences intended for the summary. This method forwards the value to _get_best_sentences and does not itself validate or coerce it.

## Returns:
    Any: The return value is exactly the return value from _get_best_sentences(document.sentences, sentences_count, ratings).
    Notes:
        - In typical implementations, this will be a sequence (e.g., list) of sentence objects selected as the summary.
        - This method places no additional constraints or guarantees on the returned value beyond propagating whatever the selection routine returns.

## Raises:
    AttributeError: If document does not have a .sentences attribute (accessing document.sentences will raise).
    Exception: Any exception raised by rate_sentences(document) or by _get_best_sentences(document.sentences, sentences_count, ratings) will propagate to the caller. This method does not catch or transform those exceptions.

## State Changes:
Attributes READ:
    - None directly by this method. It calls instance methods which may read instance attributes (e.g., stop words, stemmer settings).

Attributes WRITTEN:
    - None. This method does not modify self or assign to instance attributes.

## Constraints:
Preconditions:
    - document must have a .sentences iterable.
    - Each sentence in document.sentences must meet the expectations of rate_sentences (for example, exposing .words for tokenization).
    - callers should provide an appropriate sentences_count; this method performs no validation.

Postconditions:
    - The exact return value is the result from _get_best_sentences; no further transformations are applied.
    - The summarizer instance remains unchanged by this call.

## Side Effects:
    - This method itself performs no I/O or external calls.
    - Any side effects originate from rate_sentences or _get_best_sentences and will propagate unchanged.

### `sumy.summarizers.reduction.ReductionSummarizer.rate_sentences` · *method*

## Summary:
Compute and return a score mapping for each sentence in the document by summing pairwise similarity ranks between sentences; does not modify the summarizer's internal state.

## Description:
This method is called during the summarization pipeline to produce numeric ratings used to select the best sentences for the final summary. Known caller: ReductionSummarizer.__call__ invokes rate_sentences(document) as the step that computes sentence scores before _get_best_sentences selects top sentences. The logic is separated into its own method because it encapsulates the pairwise scoring algorithm (iterating sentence pairs, converting sentences to processed word-sets, and accumulating symmetric scores). Separating it aids clarity, testing, and reuse and keeps the core __call__ flow focused on orchestration.

## Args:
    document (object): An object that exposes an attribute `sentences`, an iterable of sentence-like objects. Each sentence object must be usable as a dictionary key (i.e., hashable) and must expose a `words` iterable (strings or tokens) consumed by helper methods.

## Returns:
    collections.defaultdict(float): A mapping from sentence objects to non-negative float scores.
    - If document.sentences contains at least two sentences, every sentence that participates in one or more pairwise comparisons will appear as a key in the returned mapping (possibly with value 0.0).
    - If document.sentences has fewer than two sentences, the returned mapping will be empty.
    - Each value is the sum of pairwise ranks computed by _rate_sentences_edge(words1, words2) between that sentence and every other sentence. The per-pair rank is a float >= 0.0 (see _rate_sentences_edge for exact computation and edge cases).

## Raises:
    AttributeError: If `document` has no attribute `sentences`.
    TypeError: If a sentence object is unhashable and cannot be used as a dictionary key.
    Any exception raised by the helper methods (for example, if normalize_word or stem_word raise) will propagate.

## State Changes:
    Attributes READ:
        - self._to_words_set (method): called per sentence to produce processed word lists (indirectly reads self._stop_words and uses normalize_word/stem_word).
        - self._rate_sentences_edge (method): called for each sentence pair to compute the pairwise rank.
        - (Indirectly) self._stop_words: accessed by _to_words_set while filtering words.
    Attributes WRITTEN:
        - None. The method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - `document.sentences` must be iterable.
        - Each sentence in `document.sentences` must be hashable (can be used as a dict key) and must expose a `.words` iterable.
        - The helper methods _to_words_set(sentence) and _rate_sentences_edge(words1, words2) must accept the provided sentence/word-list types and behave as documented in their own components.
    Postconditions:
        - The returned mapping sums, for every sentence that participated in at least one pair, the symmetric pairwise ranks contributed by comparisons with other sentences.
        - No attributes on self are modified.
        - Values in the returned mapping are floats >= 0.0. If all pairwise ranks evaluate to 0.0, the corresponding sentence keys may still exist (if there was at least one pair) with value 0.0; if there were no pairs (fewer than 2 sentences) the mapping is empty.

## Side Effects:
    - Allocates and returns a new defaultdict(float) (no persistent mutation).
    - No I/O, no network or external service calls.
    - Does not mutate sentence objects or any external state; only references sentences as dictionary keys.

### `sumy.summarizers.reduction.ReductionSummarizer._to_words_set` · *method*

## Summary:
Converts a Sentence into an ordered list of stemmed tokens by normalizing each word, filtering out stop-words, and applying the configured stemming function; does not mutate the summarizer instance.

## Description:
This method is called by ReductionSummarizer.rate_sentences during the sentence-rating stage of the reduction summarization pipeline. rate_sentences invokes _to_words_set for every sentence in the document to produce token lists used when computing pairwise sentence similarity scores.

The logic is separated into its own method to encapsulate token preprocessing (normalization, stop-word filtering, stemming) so it can be reused, tested in isolation, and kept distinct from the sentence-rating logic.

## Args:
    sentence (sumy.models.dom._sentence.Sentence): An object exposing a .words attribute (an iterable/sequence of raw word tokens, typically strings). The method expects sentence.words to yield the tokens to be normalized and stemmed.

## Returns:
    list[str]: A list of stemmed tokens (strings) in the same relative order as the source tokens after filtering.
    - Possible values:
        * Empty list: when sentence.words is empty or when all normalized tokens are filtered out by stop-words.
        * Non-empty list: contains one stemmed string per input token that passed the stop-word filter.
    - Duplicates are preserved (the method does not deduplicate tokens).

## Raises:
    AttributeError:
        - If the provided sentence does not have a .words attribute.
    Any exception raised by self.normalize_word or self.stem_word:
        - Errors originating from the normalizer or stemmer (e.g., TypeError for unexpected token types) are propagated to the caller.

## State Changes:
    Attributes READ:
        - self._stop_words: consulted to filter out normalized tokens (expected to be a set/frozenset of normalized stop-word strings).
        - self.normalize_word (method): called for each token from sentence.words to produce a normalized form for filtering/stemming.
        - self.stem_word (method): called for each normalized token that is not a stop-word to produce the returned stem.
        - sentence.words: read to obtain the source tokens.

    Attributes WRITTEN:
        - None on the summarizer instance (self). This method does not modify self.
        - Note: reading sentence.words may cause the Sentence instance to compute and cache its token list (Sentence.words is a cached_property), so the Sentence object may be mutated via its own caching mechanism.

## Constraints:
    Preconditions:
        - self._stop_words must be an iterable containing normalized word strings (the stop_words setter in this class normalizes inputs).
        - self.normalize_word and self.stem_word must be callable and accept a single token (string-like) and return a string-like value.
        - sentence.words must be an iterable of tokens appropriate for normalize_word.
    Postconditions:
        - Returns a list of stemmed tokens corresponding to the normalized, non-stop tokens from sentence.words.
        - The summarizer instance (self) remains unchanged.

## Side Effects:
    - No I/O or external service calls are performed.
    - The only observable side effect may be on the Sentence instance: accessing sentence.words can trigger tokenizer processing and populate Sentence's internal cache for words (i.e., caching behavior of the Sentence.words property).
    - The method may propagate exceptions from normalize_word/stem_word or from accessing sentence.words.

### `sumy.summarizers.reduction.ReductionSummarizer._rate_sentences_edge` · *method*

## Summary:
Computes a non-negative float score representing similarity between two token sequences by counting exact token matches and normalizing by the sum of logarithms of their lengths; it does not modify the object's state.

## Description:
This method is intended to rate the "edge" or similarity between two sentences (represented as sequences of tokens) during the reduction-style summarization process. Typical callers are other methods in the same ReductionSummarizer class that build a sentence-similarity graph or iterate over sentence pairs to compute edge weights before selecting sentences for the summary. The logic is isolated in its own method because:
- It encapsulates the particular matching-and-normalization formula used for edge scoring,
- It is reused for every sentence pair and benefits from unit testing in isolation,
- Separating it keeps higher-level graph-building code simpler and focused on control flow.

## Args:
    words1 (iterable): A sequence or iterable of tokens (commonly strings) representing the first sentence. Tokens are compared using equality (==). The implementation expects that len(words1) can be called when a match is found; providing a sized sequence (list, tuple) is the common usage.
    words2 (iterable): A sequence or iterable of tokens representing the second sentence. Same conventions as words1.

Allowed values/assumptions:
    - Items in the sequences can be any Python objects comparable with ==.
    - Duplicates are allowed and counted; the code counts every pairwise equality between elements of words1 and words2.
    - Both arguments should be finite iterables; very large inputs will increase CPU cost.

## Returns:
    float: A non-negative similarity score computed as (rank / norm) when applicable, otherwise 0.0.
    - rank is the integer count of pairwise equal token comparisons (sum_{w1 in words1} sum_{w2 in words2} 1{w1==w2}).
    - norm is math.log(len(words1)) + math.log(len(words2)).
    - If no matching token pairs are found (rank == 0), returns 0.0 immediately.
    - If norm == 0.0 (e.g., when len(words1) == len(words2) == 1), the method returns 0.0 to avoid division by zero.
    - Otherwise returns rank / norm (a positive float).

Examples of edge-case returns:
    - Two empty iterables or two iterables with no equal tokens -> 0.0.
    - Both single-token identical sequences -> norm == 0.0, method returns 0.0 despite a match.

## Raises:
    AssertionError: Raised if rank != 0 but either len(words1) == 0 or len(words2) == 0. (Per code, this assertion is present after computing rank; in practical, correct inputs this situation is impossible because a nonzero rank implies both sequences had at least one element.)
    TypeError: May be raised by len(...) if the provided iterable does not support __len__ when the code reaches the len() calls (this occurs only when rank != 0 because len() is not invoked if rank == 0).
    Other exceptions: Unlikely; math.log will not raise for positive integer lengths (math.log(1) == 0). If a non-positive integer length somehow appears, math.log will raise ValueError, but that should not occur for well-formed sequences.

## State Changes:
    Attributes READ:
        - None (the method does not read or depend on any self.<attr> fields).
    Attributes WRITTEN:
        - None (the method does not modify any self.<attr> fields).

## Constraints:
    Preconditions:
        - words1 and words2 must be iterables of comparable tokens.
        - For predictable behavior and to avoid TypeError on len(...), prefer sized iterables (list, tuple). If an iterable is not sized, ensure that it will never produce a matching token with the other iterable (since len() is only required when rank != 0).
    Postconditions:
        - The method returns a float >= 0.0.
        - The object's state is unchanged.

## Side Effects:
    - None. The method performs pure computation without I/O, external service calls, or mutations to objects outside of local variables.

## Performance:
    - Time complexity: O(len(words1) * len(words2)) due to the pairwise nested loop.
    - Memory complexity: O(1) extra space (only local counters and temporary numbers).

## Implementation notes and pitfalls:
    - The method counts every pairwise equality; repeated tokens are counted multiplicatively (e.g., words1 = ['a','a'], words2 = ['a'] yields rank == 2).
    - Normalization uses natural logarithm; when both lengths are 1 the normalization sum is 0, and the implementation intentionally returns 0.0 to avoid division by zero.
    - If callers need a symmetric measure that caps matches or treats duplicates differently, they should transform inputs or implement an alternative scorer.

