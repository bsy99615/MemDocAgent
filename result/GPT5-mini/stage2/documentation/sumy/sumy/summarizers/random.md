# `random.py`

## `sumy.summarizers.random.RandomSummarizer` · *class*

## Summary:
Implements a simple summarizer that assigns each sentence a random unique integer score and returns the top-selected sentences (preserving original document order) without mutating the summarizer instance.

## Description:
RandomSummarizer is a concrete, minimal Summarizer implementation intended for testing, baseline comparisons, or situations where a nondeterministic selection is acceptable. It is typically instantiated by pipeline code that chooses a summarizer implementation and invoked as a callable with a parsed document and a selection policy (sentences_count).

Responsibilities and boundaries:
- Responsibility: produce a summary by randomly ranking sentences and delegating selection/ordering to the generic selection helper provided by AbstractSummarizer.
- Boundary: does not implement sentence-selection logic (ranking beyond random assignment) or any token-level processing; it only produces per-sentence random ratings and relies on AbstractSummarizer._get_best_sentences to apply the count policy and restore original order.

Known callers / typical usage contexts:
- Summarization pipeline code and test harnesses that construct a concrete summarizer and call it with (document, sentences_count).
- Any code exercising summarizer implementations via the common callable interface.

## State:
Attributes defined by RandomSummarizer:
- None. RandomSummarizer does not introduce instance attributes.

Inherited attributes relevant to usage:
- _stemmer (callable)
  - Type: callable
  - Default: inherited from AbstractSummarizer constructor (null_stemmer) if not provided during instantiation.
  - Invariant: must remain callable; RandomSummarizer does not rely on it but inherits it from the base class.

Class invariants:
- No RandomSummarizer-specific invariants beyond those established by AbstractSummarizer (for example, _stemmer is callable).
- Methods do not mutate instance attributes; repeated calls reuse the same instance safely (aside from global random module state).

## Lifecycle:
Creation:
- Instantiate using the base-class constructor signature:
  - Typical: summarizer = RandomSummarizer()
  - With custom stemmer (optional): summarizer = RandomSummarizer(stemmer=my_callable)
- There is no RandomSummarizer.__init__; it inherits AbstractSummarizer.__init__, which validates the optional stemmer argument (raises ValueError if not callable).

Usage (typical sequence and required ordering):
1. Prepare a parsed document object whose attribute document.sentences is a finite, sized, sequence-like iterable of sentence objects (supports len() and iteration).
   - Each sentence object must be hashable (so it can be used as a dict key).
2. Call the summarizer instance with (document, sentences_count).
   - __call__ performs the following steps:
     a. Read sentences = document.sentences.
     b. Call self._get_random_ratings(sentences) to obtain a dict mapping sentence -> random integer rating.
     c. Call AbstractSummarizer._get_best_sentences(sentences, sentences_count, ratings) to select and order the top sentences.
   - The returned value is a tuple of sentence objects in their original document order.
3. No explicit cleanup is required; RandomSummarizer does not open files or network resources.

Destruction:
- No special destruction or cleanup is required. There is no context-manager or close() method implemented.

## Method Map:
graph LR
    A[__call__(document, sentences_count)] --> B[_get_random_ratings(sentences)]
    B --> C[random.shuffle(list_of_ints)]
    A --> D[AbstractSummarizer._get_best_sentences(sentences, sentences_count, ratings)]
    D --> E[Create per-sentence infos (sentence,order,rating)]
    E --> F[Sort infos by rating desc]
    F --> G[Apply count policy -> selected infos]
    G --> H[Sort selected infos by order asc]
    H --> I[Return tuple(selected sentences)]

Notes:
- _get_random_ratings is internal and pure w.r.t. instance state (it mutates only local data and the global random state).
- _get_best_sentences is provided by AbstractSummarizer and performs selection and ordering.

## Detailed behavior of public methods and helpers:
- __call__(document, sentences_count)
  - Inputs:
    - document: an object with attribute sentences, a sized, iterable sequence of sentence objects.
    - sentences_count: passed through to AbstractSummarizer._get_best_sentences (commonly an int, a percentage string like "30%", or a selector callable).
  - Output:
    - tuple of sentence objects selected from document.sentences, ordered by their original position in the document.
  - Side effects:
    - Calls random.shuffle inside _get_random_ratings, which mutates the global random module state.
    - Does not modify the summarizer instance or the sentence objects.
  - Important constraints:
    - document.sentences must be repeatable (sequence-like). Passing a one-time generator is unsafe because AbstractSummarizer._get_best_sentences enumerates the sentences.
    - Sentence objects must be hashable because they are used as keys in the ratings dict.

- _get_random_ratings(sentences)
  - Inputs:
    - sentences: sized iterable (supports len() and iteration) of sentence objects.
  - Output:
    - dict mapping sentence -> int
      - For unique, hashable sentence objects the dict contains exactly len(sentences) keys with values equal to a permutation of range(len(sentences)) (i.e., integers 0..n-1).
      - If the input contains duplicate objects that are equal and hash-equal, later duplicates overwrite earlier mappings; the returned dict will have fewer keys than len(sentences).
  - Side effects:
    - Mutates an internal local list of integers via random.shuffle and therefore consumes/modifies global random module state.
  - Edge cases:
    - Empty input returns an empty dict.
    - If sentences does not support len(), a TypeError will occur when length is requested.
    - If any sentence is unhashable, constructing the dict will raise TypeError.

## Raises:
Exceptions that may be raised directly or propagate to callers and why:
- From instantiation (inherited from AbstractSummarizer.__init__):
  - ValueError if a non-callable value is provided for stemmer when constructing the instance.

- From __call__:
  - AttributeError if the document has no attribute sentences.
  - TypeError if document.sentences does not support len() or is otherwise not a sized iterable (this originates from _get_random_ratings calling len()).
  - TypeError if any sentence object is unhashable (raising when building the dict).
  - Any exceptions raised by AbstractSummarizer._get_best_sentences:
    - AssertionError if a mapping rating was used but args/kwargs were incorrectly supplied (not applicable here since _get_random_ratings returns a mapping and no extra args/kwargs are forwarded).
    - KeyError if a sentence present in the sentences sequence is not found in the ratings mapping (should not occur because ratings are built from the same sequence, except when duplicate/equal objects collapse keys).
    - Any exception raised by a user-supplied selector callable (sentences_count) will propagate.

- From _get_random_ratings:
  - TypeError if len(sentences) fails (e.g., generator without __len__).
  - TypeError if any sentence is unhashable.
  - (Standard library random.shuffle does not normally raise for this usage; other unexpected exceptions may propagate.)

## Example:
1) Instantiate the summarizer (using the default stemmer from the base class):
   summarizer = RandomSummarizer()

2) Prepare a parsed document whose document.sentences is a list or tuple of Sentence objects (each Sentence must be hashable; see Sentence.__hash__).

3) Produce a summary of 3 sentences:
   summary_sentences = summarizer(document, 3)
   - result: a tuple of up to 3 Sentence objects in the original document order.

4) Use a percentage-based policy:
   summary_sentences = summarizer(document, "30%")
   - selection policy is interpreted by AbstractSummarizer._get_best_sentences (ItemsCount behavior).

Notes on reproducibility:
- To obtain reproducible random selections, set the random module state externally before calling (for example, random.seed(some_value)). RandomSummarizer itself does not set or reset randomness.

Implementation hints for re-creation:
- Implement __call__ to read document.sentences, call an internal method that returns a mapping sentence->rating, and then forward to a reusable selection helper that accepts either a mapping or rating callable.
- Implement _get_random_ratings by creating a list(range(n)), shuffling it with random.shuffle, and zipping it with the sentences to create the mapping. Be careful to use a sized sequence for len() and to handle duplicate/hashing behavior explicitly in the documentation above.

### `sumy.summarizers.random.RandomSummarizer.__call__` · *method*

## Summary:
Uses a random-permutation scoring of the document's sentences and returns the top-selected sentences (preserving original document order) without mutating the summarizer instance.

## Description:
This method is the public callable entry-point of the RandomSummarizer instance that produces a summary from a parsed document. It is typically invoked by higher-level summarization pipeline code immediately after document parsing/tokenization; callers provide the parsed document and a selection policy (sentences_count) and expect an ordered collection of sentence objects forming the summary.

Call flow / responsibilities:
- Retrieves the sequence of sentences from document.sentences.
- Delegates scoring to the instance helper _get_random_ratings, which assigns each sentence a random integer score.
- Delegates selection and ordering to AbstractSummarizer._get_best_sentences, which selects top-rated sentences according to sentences_count and restores their original document order.

Why a separate method:
- Keeps the orchestration (prepare sentences → score → select) explicit and concise for this concrete summarizer.
- Reuses the generic selection behavior implemented in AbstractSummarizer._get_best_sentences rather than duplicating selection/sorting logic.
- Keeps scoring logic (_get_random_ratings) separated so it can be overridden, tested, or reused independently.

Known callers / lifecycle stage:
- Summarization pipeline code that instantiates a concrete Summarizer and calls it with (document, sentences_count).
- Any integration tests or tools that exercise concrete summarizers through their callable interface.
- It is invoked at the summarizer execution stage — after a Document object has been created/parsed and before post-processing/formatting of the returned sentences.

## Args:
    document (object): Parsed document object exposing a sequence of sentence objects at attribute `sentences`.
        - Required shape/behavior:
            * document.sentences must be a finite, indexable/sequence-like iterable (it is used with len() and iterated multiple times).
            * Each sentence object must be hashable (used as keys in the random ratings mapping).
    sentences_count (int | callable | other count policy):
        - Passed through to AbstractSummarizer._get_best_sentences.
        - Common values:
            * int: number of sentences to select
            * callable: a selector callable that accepts an iterable of per-sentence info objects and returns selected infos
            * string percentage (e.g., "30%") or other forms supported by ItemsCount in the shared selection helper
        - No default — caller must supply a value appropriate for the selection policy.

## Returns:
    tuple: A tuple of selected sentence objects (the exact objects from document.sentences), ordered by their original document order.
    - If no sentences are selected, returns an empty tuple.
    - The selection and ordering behavior follow AbstractSummarizer._get_best_sentences semantics.

## Raises:
    AttributeError: If `document` does not have a `sentences` attribute.
    TypeError: If `document.sentences` does not support len() (e.g., is a lazy generator without __len__) or is otherwise not a sequence-like iterable required by _get_random_ratings.
    TypeError: If any sentence objects are not hashable (they are used as keys when building the ratings dict).
    AssertionError / KeyError: Any exceptions raised by AbstractSummarizer._get_best_sentences when processing the provided ratings and count policy may propagate. For example:
        - AssertionError if _get_best_sentences detects an invalid mix of mapping rating and forwarded args (not applicable here since no extra args are passed).
        - KeyError if a sentence expected by a mapping-based rating is missing (should not occur because ratings are built from the same sentences sequence).
    Any exception raised by _get_random_ratings (e.g., from random.shuffle or incorrect input) or by _get_best_sentences (e.g., from user-provided selector callables) is propagated to the caller.

## State Changes:
    Attributes READ:
        - None of the instance's stored attributes are read (this method only calls instance helper methods).
    Attributes WRITTEN:
        - None. The summarizer instance is not mutated by this call.

## Constraints:
    Preconditions:
        - document.sentences must be a finite sequence (supporting len() and iteration) and must be safe to iterate multiple times.
        - Each sentence object must be hashable so it can serve as a dict key when building random ratings.
        - sentences_count must be a value accepted by AbstractSummarizer._get_best_sentences (commonly an int, a selector callable, or a string percent handled by ItemsCount).
    Postconditions:
        - Returns a tuple of zero or more sentence objects from the input document that were selected as the top items according to a random ranking policy and the provided sentences_count.
        - The order of sentences in the returned tuple matches their original order in document.sentences.
        - The RandomSummarizer instance and the input sentence objects are not modified by this method.

## Side Effects:
    - Consumes and mutates the global random generator state by calling random.shuffle (this affects subsequent uses of the random module).
    - No I/O or network calls are performed.
    - The method delegates to _get_best_sentences which fully consumes the provided sentences iterable; therefore document.sentences must be repeatable (sequence-like). Passing a one-time generator may cause errors or unexpected behavior.

### `sumy.summarizers.random.RandomSummarizer._get_random_ratings` · *method*

## Summary:
Assigns a unique random integer rating to each element of the provided sequence of sentences and returns a mapping from each sentence to its assigned rating. The method does not modify object state.

## Description:
This helper produces a randomized "ranking" for a collection of sentences by generating the integers 0..n-1 (where n is the number of items), shuffling those integers, and pairing each sentence with one shuffled integer. It is intended to be used inside the RandomSummarizer implementation when a random scoring of sentences is required (for example, as the scoring step prior to selecting top-rated sentences in a random summarization pipeline). The logic is factored into its own method so that the random-assignment behavior is isolated (making it easier to override in subclasses, mock in tests, or replace with deterministic behavior during testing).

Known callers / context:
- Internal use within RandomSummarizer during the summarization pipeline to obtain sentence ratings before selection or aggregation steps.

Why separate:
- Encapsulates randomness and pairing logic in one place for clarity, testability, and possible overriding.

## Args:
    sentences (sequence): A sized, iterable sequence (supports len() and iteration) of sentence objects to be rated.
        - Required properties:
            * len(sentences) must be valid (i.e., the object must support __len__).
            * Sentences must be hashable (since they become dictionary keys).
        - Typical concrete types: list or tuple of sentence objects.

## Returns:
    dict: A mapping from each sentence (an element from the input sequence) to an integer rating.
        - Keys: elements from the input sequence (must be hashable).
        - Values: integers in the range [0, n-1], where n == len(sentences).
        - Uniqueness: the generated integer ratings are unique across the original positions (the list of integers 0..n-1 is shuffled before pairing). However, if the input sequence contains duplicate elements (equal and hash-equal), later duplicates will overwrite earlier entries in the returned dict; in that case the returned dict will have fewer keys than n and some integer values from the shuffled set may not appear in the final mapping.
        - Edge-case: If sentences is empty, returns an empty dict.

## Raises:
    TypeError:
        - If sentences does not support len() (e.g., a generator without __len__), calling len(sentences) will raise TypeError.
        - If any element in sentences is unhashable (for example, a list or dict), attempting to use it as a dict key will raise TypeError.
    (No other exceptions are raised directly by this method; exceptions may propagate from random.shuffle if the environment's random implementation raises, but standard library random.shuffle does not raise for the usage here.)

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> attributes).
    Attributes WRITTEN:
        - None (this method does not modify self or any self.<attr> attributes).

## Constraints:
    Preconditions:
        - sentences must be a sized iterable (implements __len__ and __iter__).
        - Elements of sentences must be hashable to serve as dictionary keys.
    Postconditions:
        - The returned dict maps (a subset of) the input elements to integers in 0..n-1.
        - For inputs with all unique, hashable elements, the returned dict contains exactly n keys and each number in 0..n-1 appears exactly once among the values (in a random order).
        - The method does not change the RandomSummarizer instance state.

## Side Effects:
    - Uses the standard library random.shuffle to shuffle an internal list of integers; this mutation is local to the method (it mutates a local list variable and does not mutate inputs).
    - No I/O, no external service calls, and no mutations of objects outside self (input sequence objects themselves are not modified by this method).
    - Behavior is nondeterministic: repeated calls with the same input will generally produce different mappings unless the random module’s state is controlled externally (e.g., by seeding).

