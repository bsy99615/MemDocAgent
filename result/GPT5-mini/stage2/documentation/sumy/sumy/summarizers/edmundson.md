# `edmundson.py`

## `sumy.summarizers.edmundson.EdmundsonSummarizer` · *class*

## Summary:
Represents an Edmundson-style extractive summarizer that scores sentences using a weighted combination of cue, key, title and location features and selects the top sentences as the summary.

## Description:
Instantiate this class when you need an extractive summarizer that combines multiple heuristic scoring methods (cue words, key words, title-matching, and sentence location) according to configurable non-negative weights. The class aggregates the per-sentence ratings produced by the Edmundson* method classes (EdmundsonCueMethod, EdmundsonKeyMethod, EdmundsonTitleMethod, EdmundsonLocationMethod) and delegates selection of the best sentences to a helper provided by the AbstractSummarizer base class.

Typical callers:
- Application code that constructs a summarizer and calls it with a parsed Document object.
- Higher-level pipelines that assemble a Document (containing .sentences) and pass it to this summarizer.

Motivation and responsibilities:
- Encapsulates the orchestration and weighting of several Edmundson-derived rating heuristics rather than implementing each heuristic in-line.
- Enforces that weights are non-negative and that required word-sets (bonus/stigma/null) are provided before using the corresponding heuristic.
- Converts supplied word collections into stemmed frozensets used by the underlying method classes.

## State:
Public-like properties (accessed via property methods)
- bonus_words (frozenset of str)
  - Backing attribute: _bonus_words
  - Set by: bonus_words.setter
  - Stored form: frozenset(map(self.stem_word, collection))
  - Default: _EMPTY_SET (class-level sentinel)
  - Constraint: When empty, calling methods that require bonus words will raise ValueError (see __check_bonus_words).

- stigma_words (frozenset of str)
  - Backing attribute: _stigma_words
  - Set by: stigma_words.setter
  - Stored form: frozenset(map(self.stem_word, collection))
  - Default: _EMPTY_SET
  - Constraint: When empty, cue-related operations will raise ValueError (see __check_stigma_words).

- null_words (frozenset of str)
  - Backing attribute: _null_words
  - Set by: null_words.setter
  - Stored form: frozenset(map(self.stem_word, collection))
  - Default: _EMPTY_SET
  - Constraint: When empty, title/location related operations will raise ValueError (see __check_null_words).

Private stored configuration
- _stemmer
  - Provided to base class via constructor; used by this class for word stemming via self.stem_word (inherited).
  - Default: null_stemmer (a no-op stemmer imported from nlp.stemmers).

- _cue_weight (float)
  - Default: 1.0
  - Invariant: >= 0.0

- _key_weight (float)
  - Default: 0.0
  - Invariant: >= 0.0

- _title_weight (float)
  - Default: 1.0
  - Invariant: >= 0.0

- _location_weight (float)
  - Default: 1.0
  - Invariant: >= 0.0

Class invariants:
- All four weights are floats and non-negative (enforced by _ensure_correct_weights during __init__).
- word-set attributes (bonus/stigma/null) are frozensets of stemmed tokens once set by their respective setters.
- Methods that depend on specific word-sets will validate those sets before building the corresponding method instance.

## Lifecycle:
Creation:
- Constructor signature:
  - EdmundsonSummarizer(stemmer=null_stemmer, cue_weight=1.0, key_weight=0.0, title_weight=1.0, location_weight=1.0)
  - Required args: none (all params have defaults).
  - Behavior:
    - Calls AbstractSummarizer.__init__(stemmer).
    - Validates that all provided weights are >= 0.0 using _ensure_correct_weights.
    - Stores each weight as float in the corresponding _*_weight attribute.

Usage:
- Typical sequence:
  1. (Optional) Set word sets required by specific heuristics:
     - summarizer.bonus_words = collection
     - summarizer.stigma_words = collection
     - summarizer.null_words = collection
     These setters stem each word via self.stem_word and store a frozenset.
  2. Call the summarizer to obtain a multi-feature summary:
     - summarizer(document, sentences_count)
     The call will:
       - Initialize ratings as defaultdict(int).
       - For each feature (cue, key, title, location), if the corresponding weight > 0.0:
         - Build the corresponding method instance (which validates required word-sets).
         - Obtain per-sentence ratings via method.rate_sentences(document).
         - Merge these ratings into the aggregate using _update_ratings (summing per-sentence values).
       - Delegate selection to _get_best_sentences(document.sentences, sentences_count, ratings) (inherited).
  3. Alternatively, use specialized helper methods:
     - cue_method(document, sentences_count, bonus_word_value=1, stigma_word_value=1)
       Calls the cue-method instance as a summarization method with the provided bonus/stigma numeric weights.
     - key_method(document, sentences_count, weight=0.5)
       Requires bonus_words to be set; returns top-ranked sentences subject to sentences_count which can be:
         - a callable predicate applied to sentences (returns tuple of sentences that match),
         - a percentage string like '20%' (returns that percent of sentences, at least 1),
         - an integer (returns up to that many sentences).
     - location_method(document, sentences_count, w_h=1, w_p1=1, w_p2=1, w_s1=1, w_s2=1)
       Calls the location summarizer with location weights.
     - These helpers build and call the specific Edmundson* method instance and return results from that method.

Sequencing requirements:
- If you intend to use key_method, cue_method, or location/title methods, you must set the corresponding word sets before calling them (otherwise ValueError is raised during instance construction).
- There is no special destruction or cleanup; the class holds no external resources or open handles.

Destruction:
- No explicit cleanup API (no close or context manager). Instances are plain objects managed by the Python GC.

## Method Map:
Flow of main interactions (simplified):
graph TD
    A[__init__] --> B[_ensure_correct_weights]
    A --> C[_cue_weight/_key_weight/_title_weight/_location_weight]
    D[__call__] --> E[ratings = defaultdict(int)]
    E --> F{_cue_weight > 0.0?}
    F -- yes --> G[_build_cue_method_instance]
    G --> H[EdmundsonCueMethod.rate_sentences(document)]
    H --> I[_update_ratings]
    E --> J{_key_weight > 0.0?}
    J -- yes --> K[_build_key_method_instance]
    K --> L[EdmundsonKeyMethod.rate_sentences(document)]
    L --> I
    E --> M{_title_weight > 0.0?}
    M -- yes --> N[_build_title_method_instance]
    N --> O[EdmundsonTitleMethod.rate_sentences(document)]
    O --> I
    E --> P{_location_weight > 0.0?}
    P -- yes --> Q[_build_location_method_instance]
    Q --> R[EdmundsonLocationMethod.rate_sentences(document)]
    R --> I
    I --> S[_get_best_sentences(document.sentences, sentences_count, ratings)]
    S --> T[result]

Notes:
- Helper methods cue_method, key_method, and location_method create method instances via their _build_* factories and call them directly, bypassing weight checks done in __call__.

## Raises:
Constructor and methods may raise:
- ValueError from __init__ via _ensure_correct_weights if any provided weight < 0.0.
- ValueError from __check_bonus_words if bonus_words is empty and an operation requiring bonus words is attempted (e.g., _build_key_method_instance or _build_cue_method_instance).
- ValueError from __check_stigma_words if stigma_words is empty and cue-related operation is attempted.
- ValueError from __check_null_words if null_words is empty and title or location related operations are attempted.
- Note: _build_key_method_instance returns an EdmundsonKeyMethod instance if bonus_words is set; key_method also explicitly checks instance is not None and raises ValueError with a similar message if the instance creation indicates missing bonus words.

## Example:
- Instantiate a summarizer with default stemmer and default weights:
  summarizer = EdmundsonSummarizer()

- Prepare and set the required word sets (collections of tokens or phrases):
  summarizer.bonus_words = ['important', 'key', 'notable']
  summarizer.stigma_words = ['irrelevant', 'ignore']
  summarizer.null_words = ['the', 'a', 'and']

- Produce a multi-feature summary:
  summary_sentences = summarizer(document, 3)
  # Where `document` is an object with attribute `sentences` (a sequence of sentence objects).
  # The summarizer aggregates ratings from enabled methods (weights > 0.0) and returns the top 3 sentences.

- Call a specialized method:
  cue_summary = summarizer.cue_method(document, 2, bonus_word_value=2, stigma_word_value=1)
  key_summary = summarizer.key_method(document, '30%', weight=0.7)
  location_summary = summarizer.location_method(document, 2, w_h=2, w_p1=1, w_p2=1, w_s1=1, w_s2=1)

- Error case:
  If you call summarizer.key_method(...) before setting summarizer.bonus_words (non-empty), a ValueError will be raised instructing you to set the attribute.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.__init__` · *method*

## Summary:
Sets up a new EdmundsonSummarizer by delegating stemmer initialization to the base class, validating the four heuristic weights, and storing each weight as a float on the instance.

## Description:
Known callers and lifecycle stage:
- Invoked during construction of an EdmundsonSummarizer instance (e.g., summarizer = EdmundsonSummarizer()) by application code or pipeline/factory code that selects and constructs a concrete summarizer.
- Happens once at object creation time before any summarization or method calls on the instance.

Why this logic is in __init__:
- Centralizes initial validation and normalization of the summarizer's core configuration: stemmer setup (shared by all summarizers) and enforcement/normalization of the four Edmundson weights. Ensures the instance invariant (callable stemmer, non-negative float weights) holds immediately after construction.

## Behavior and Call Order:
1. Calls AbstractSummarizer.__init__(stemmer) via super(...).__init__(stemmer) to validate and store the stemmer callable as self._stemmer. If `stemmer` is not callable, AbstractSummarizer.__init__ raises ValueError.
2. Calls self._ensure_correct_weights(cue_weight, key_weight, title_weight, location_weight) which enforces that each weight is non-negative. If any supplied weight is negative, this helper raises ValueError.
3. Converts each provided weight to float and assigns them to the instance backing attributes:
   - self._cue_weight = float(cue_weight)
   - self._key_weight = float(key_weight)
   - self._title_weight = float(title_weight)
   - self._location_weight = float(location_weight)

## Args:
    stemmer (callable, optional)
        - Callable that accepts a single token (string) and returns a stem/normalized form.
        - Default: null_stemmer (imported from nlp.stemmers).
        - Requirement: must be callable; otherwise a ValueError is raised by AbstractSummarizer.__init__.
    cue_weight (numeric, optional)
        - Weight for cue-word based scoring.
        - Default: 1.0
        - Must be convertible to float and >= 0.0.
    key_weight (numeric, optional)
        - Weight for key-word based scoring.
        - Default: 0.0
        - Must be convertible to float and >= 0.0.
    title_weight (numeric, optional)
        - Weight for title-matching scoring.
        - Default: 1.0
        - Must be convertible to float and >= 0.0.
    location_weight (numeric, optional)
        - Weight for sentence-location based scoring.
        - Default: 1.0
        - Must be convertible to float and >= 0.0.

## Returns:
    None

## Raises:
    ValueError:
        - If `stemmer` is not callable. Raised by AbstractSummarizer.__init__ with message: "Stemmer has to be a callable object".
        - If any supplied weight is negative (< 0.0). Raised by self._ensure_correct_weights when non-negativity is violated.
    TypeError or ValueError:
        - When converting weight arguments with float(...), non-numeric or otherwise invalid inputs may raise TypeError or ValueError from the built-in float conversion.

## State Changes:
    Attributes READ:
        - None directly by this constructor prior to assignment; helper/base-class methods invoked do not depend on pre-existing instance attributes.
    Attributes WRITTEN:
        - self._stemmer
            - Assigned by AbstractSummarizer.__init__(stemmer) called via super.
        - self._cue_weight (float)
            - Set to float(cue_weight).
        - self._key_weight (float)
            - Set to float(key_weight).
        - self._title_weight (float)
            - Set to float(title_weight).
        - self._location_weight (float)
            - Set to float(location_weight).

## Constraints:
    Preconditions:
        - `stemmer` must be callable (or omitted to accept the default null_stemmer).
        - Each weight must be a value acceptable to float(...) (e.g., int or float) and should be >= 0.0 to pass _ensure_correct_weights.
    Postconditions:
        - self._stemmer is set to the provided callable.
        - Each _*_weight attribute exists and is a float.
        - The invariant that each stored weight is non-negative holds on successful return.

## Side Effects:
    - Mutates the instance by assigning self._stemmer and self._cue_weight/_key_weight/_title_weight/_location_weight.
    - No external I/O, network calls, or mutation of objects outside self.
    - If a validation error occurs (ValueError/TypeError), the instance initialization fails and the partially-initialized object may be discarded.

### `sumy.summarizers.edmundson.EdmundsonSummarizer._ensure_correct_weights` · *method*

## Summary:
Validates that each provided weight is non-negative; if any weight is negative, raises a ValueError. This method performs validation only and does not modify object state.

## Description:
Known callers and context:
    - EdmundsonSummarizer.__init__: Called during object construction to validate the cue, key, title, and location weight arguments before they are stored on the instance. It is invoked as the first step in the constructor's validation flow.
    - No other callers exist in the class source; the method is intended as a small reusable validator that can be called wherever weight validation is needed.

Why this logic is a separate method:
    - Encapsulates the single responsibility of validating weight values so the constructor (and any future callers) can remain concise and focused on initialization.
    - Improves reuse and testability: validation behavior is centralized, reducing duplication and making it easier to change or unit-test validation rules.

## Args:
    *weights (float|int): One or more numeric weight values to validate. Each element must be comparable with 0.0 (typically an int or float). No default; passing no arguments is allowed (results in a no-op).

## Returns:
    None. The function performs validation and does not return a value.

## Raises:
    ValueError: Raised when any provided weight is strictly less than 0.0. The exact raised message is "Negative weights are not allowed."
    TypeError: May be raised by the underlying comparison operation if a non-comparable (e.g., None or an unrelated object) is passed; this is not explicitly handled by the method but is a possible runtime error.

## State Changes:
    Attributes READ:
        - None. The method does not read any self.<attr> fields.
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - Each weight argument should be a numeric type that supports comparison with a float (int or float recommended).
        - Typical expected values are >= 0.0; negative values are invalid.
    Postconditions:
        - If the method returns normally, all supplied weights were >= 0.0.
        - No mutation of the object or other program state occurs.

## Side Effects:
    - None: the method has no I/O, does not call external services, and does not mutate objects outside of its local scope.

## Edge cases and notes:
    - Calling with zero arguments is valid and performs no checks (no-op).
    - Passing exactly 0.0 is allowed.
    - The method enforces strict non-negativity; any value less than 0.0 triggers the ValueError.
    - Because comparisons are used directly, passing non-numeric or otherwise non-comparable objects will raise a TypeError from the comparison operation.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.bonus_words` · *method*

## Summary:
Sets the summarizer's set of "bonus" words by stemming each entry from the given collection and storing them as an immutable frozenset on the instance.

## Description:
This setter is typically called during summarizer configuration by user code or higher-level pipeline setup, e.g. immediately after constructing an EdmundsonSummarizer and before invoking it on a Document. It centralizes the logic of normalizing (via the summarizer's stem_word method) and freezing the bonus-word list so other Edmundson sub-methods can perform fast membership checks.

Known callers / lifecycle stage:
- External configuration code: callers set summarizer.bonus_words = collection to supply words that should increase sentence scores.
- The summarizer's sub-method builders and runtime (e.g., _build_cue_method_instance, _build_key_method_instance) expect this attribute to be populated before summarization; these builders will check the resulting _bonus_words via __check_bonus_words.
- It is separated as its own setter to ensure normalization and immutability are applied consistently in one place rather than duplicated in multiple builders or methods.

Why this logic is a separate method:
- Normalization (stemming) must be applied uniformly to every configured word; isolating it in a setter ensures all callers benefit from consistent preprocessing.
- Storing a frozenset enforces immutability and provides O(1) membership tests for downstream scoring methods.
- Keeping it as a distinct setter improves API clarity (property semantics) and allows validation checks elsewhere to assume a canonical internal representation.

## Args:
    collection (iterable):
        An iterable of word-like items (commonly strings) to be treated as bonus words.
        - Expected element type: values accepted by self.stem_word (typically str).
        - The iterable may be empty to indicate "no bonus words".
        - Passing a non-iterable (e.g., None) will raise a TypeError when attempted to iterate.

## Returns:
    None
    - The setter does not return a value; its observable effect is the mutation of the instance attribute self._bonus_words.

## Raises:
    - Any exception raised by iterating over collection will propagate (e.g., TypeError if collection is not iterable).
    - Any exception raised by self.stem_word for an element will propagate (for example, if stem_word expects a str and receives another type).
    - Any exception raised by frozenset construction will propagate (for example, if stem_word returns an unhashable object, frozenset(...) will raise TypeError).

## State Changes:
    Attributes READ:
        - self.stem_word (the instance method is invoked for each item in collection)
    Attributes WRITTEN:
        - self._bonus_words is set to a frozenset containing the stemmed results of the input collection

## Constraints:
    Preconditions:
        - The instance must have a working stem_word method (normally provided by AbstractSummarizer or the configured stemmer).
        - collection must be an iterable of items acceptable to self.stem_word.
        - Elements (after stemming) must be hashable to be held in a frozenset.

    Postconditions:
        - After the call, self._bonus_words is a frozenset containing one entry for each element yielded by collection after mapping through self.stem_word. If collection is empty, self._bonus_words becomes an empty frozenset.
        - Subsequent checks (e.g., __check_bonus_words) will treat an empty frozenset as "not set" (falsy), matching existing class expectations.

## Side Effects:
    - Mutates the instance attribute self._bonus_words only.
    - No I/O, networking, or mutations of objects outside the summarizer instance are performed.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.stigma_words` · *method*

## Summary:
Sets the summarizer's stigma-word set by normalizing and stemming each token in the provided collection, storing the result as an immutable frozenset on the instance.

## Description:
This property setter is used when configuring the summarizer before running it. It converts every element in the supplied iterable into a canonical stem using the instance's stem_word helper and stores the resulting stems as a frozenset in self._stigma_words. The prepared set is later used by scoring algorithms (for example, the cue-based method) to penalize sentences that contain stigma words.

Known callers and lifecycle stage:
- Typically called by client code or configuration pipelines during setup, e.g. summarizer.stigma_words = [...]
- Indirectly relied on by _build_cue_method_instance which calls __check_stigma_words to enforce the set is non-empty before constructing the cue method.
- Should be called before invoking the summarizer instance (before __call__) if stigma words are required by the chosen scoring methods.

Why this is a dedicated setter:
- Centralizes token canonicalization (normalize + stem) so downstream scoring compares against a consistent representation.
- Deduplicates entries via set semantics and enforces immutability by storing a frozenset to avoid accidental external mutation.
- Keeps configuration logic separate from scoring implementation for clarity and reuse.

## Args:
    collection (iterable): Iterable of tokens (commonly str or bytes) to be treated as stigma words.
        - Each element is passed to stem_word(self, token), which first normalizes the token (to text and lowercased) and then applies the configured stemmer.
        - Allowed values: any iterable whose elements are accepted by normalize_word and the configured stemmer.
        - Common pitfall: Passing a single string (e.g., "not") will iterate characters and produce stems for 'n', 'o', 't'. To set a single token, pass a one-element iterable such as ["not"].

## Returns:
    None: This is a property setter. Its observable effect is the updated self._stigma_words attribute.

## Raises:
    TypeError:
        - If collection is not iterable (e.g., None or a non-iterable object), attempting to iterate it will raise TypeError (or a similar iteration-related exception) when map() consumes the collection.
    Any exception raised by normalization or the configured stemmer:
        - Exceptions from normalize_word (e.g., UnicodeDecodeError) or from the custom stemmer callable will propagate unchanged.
        - The setter does not catch these exceptions.

## State Changes:
    Attributes READ:
        - self._stemmer (indirectly, via self.stem_word): the configured stemmer callable is used during stemming.
        - self.stem_word (method): invoked for each element in collection.
    Attributes WRITTEN:
        - self._stigma_words: replaced with a frozenset containing the stems of the provided tokens.

## Constraints:
    Preconditions:
        - The instance must have been constructed with a callable stemmer (this is enforced by AbstractSummarizer.__init__).
        - collection must be an iterable whose elements are acceptable to normalize_word and the stemmer.
    Postconditions:
        - self._stigma_words is a frozenset containing the result of stem_word applied to each element of collection.
        - Duplicate stems are removed due to set semantics.
        - If collection is empty, self._stigma_words becomes an empty frozenset; subsequent operations that require a non-empty stigma set (e.g., methods that call __check_stigma_words) will raise ValueError.

## Side Effects:
    - No direct I/O or external calls are performed by the setter itself.
    - Side effects may arise from the configured stemmer callable if that callable performs I/O or other external operations; such side effects will occur during stem_word invocations and are not suppressed by the setter.
    - No other instance attributes are modified.

## Example usage and common pitfalls:
    - Typical usage:
        summarizer.stigma_words = ["undesirable", "irrelevant"]
      After this assignment, self._stigma_words contains the stems of "undesirable" and "irrelevant".

    - Pitfall (incorrect for single token):
        summarizer.stigma_words = "undesirable"
      This will iterate the string and stem individual characters. To set one token, use:
        summarizer.stigma_words = ["undesirable"]

### `sumy.summarizers.edmundson.EdmundsonSummarizer.null_words` · *method*

## Summary:
Configure the instance's null-word set by stemming each entry of the given iterable and storing the results as an immutable set on the instance.

## Description:
This is the property setter invoked when assigning to the instance attribute null_words (the class defines null_words as a property with this setter). For each element in the provided collection it calls self.stem_word and collects the results into a frozenset stored on self._null_words.

Known code interactions:
- The setter populates self._null_words which is later checked by __check_null_words(). __check_null_words() raises ValueError if self._null_words is empty; those checks are performed by _build_title_method_instance and _build_location_method_instance before constructing their respective method instances. Therefore, callers of title- or location-based methods will observe a ValueError if this setter was not used to set a non-empty collection.

This logic is implemented as a setter to centralize normalization (stemming) and enforce a canonical, hashable representation (frozenset) for membership checks elsewhere in the class.

## Args:
    collection (iterable): An iterable of items (typically strings). Each item will be passed to self.stem_word. The iterable may be empty.

## Returns:
    None: This setter does not return a value. Its effect is to assign to self._null_words.

## Raises:
    TypeError: If collection is not iterable, a TypeError will be raised when attempting to iterate or map.
    TypeError: If any value returned by self.stem_word is unhashable, constructing frozenset(...) will raise TypeError.
    Any exception raised by self.stem_word (e.g., ValueError, TypeError) will propagate out of this setter.

Note:
    This method does not itself raise ValueError when the resulting set is empty; an empty frozenset is allowed here. The ValueError for empty null-words is raised later by __check_null_words() when relevant summarization builders are invoked.

## State Changes:
Attributes READ:
    self.stem_word (method) — called for each element in collection

Attributes WRITTEN:
    self._null_words — replaced with a frozenset containing the stemmed results of the provided collection

## Constraints:
Preconditions:
    - The instance must provide a callable stem_word that accepts elements of collection.
    - Items returned by stem_word must be hashable to be stored in a frozenset.

Postconditions:
    - self._null_words is a frozenset of stemmed items (duplicates removed).
    - If collection is empty, self._null_words is an empty frozenset.

## Side Effects:
    - Mutates only the instance attribute self._null_words.
    - This setter does not perform I/O or call external services itself; however, any side effects produced by self.stem_word (if present) will occur when called.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.__call__` · *method*

## Summary:
Aggregates per-sentence numeric scores produced by enabled Edmundson sub-methods (cue, key, title, location), sums them into a single rating mapping, and returns the top sentences selected by the shared selection helper in the original document order.

## Description:
This method is the public entry point that produces an Edmundson-style summary from a parsed Document. It is typically invoked by application code or summarization pipelines after document parsing/tokenization, when a desired sentences_count policy is provided.

What it does and why it's separate:
- Orchestrates which Edmundson sub-methods participate based on the instance weights, invokes their per-sentence scoring routines (rate_sentences), accumulates scores additively, and delegates selection and ordering to AbstractSummarizer._get_best_sentences.
- Keeping this coordination logic central avoids duplicating composition steps and ensures a consistent accumulation and selection policy across the sub-methods.

Typical callers / lifecycle stage:
- Called by user code or pipeline components after constructing an EdmundsonSummarizer and preparing a Document object (containing sentences, paragraphs, headings, etc.). It is the final summarization step that produces the selected sentence objects.

## Args:
    document (object):
        A parsed Document object expected to satisfy the assumptions of the Edmundson*Method implementations:
        - document.sentences: iterable/sequence of sentence objects in document order (required)
        - document.words, document.headings, document.paragraphs: used by specific sub-methods
        The method does not validate the full Document shape; sub-methods and the selection helper will rely on expected attributes and may raise errors if absent or malformed.
    sentences_count (int or callable or other policy supported by _get_best_sentences):
        A selection policy that determines how many sentences to return. Accepts forms documented by AbstractSummarizer._get_best_sentences (commonly an int, a callable selector, or percent-strings handled by ItemsCount).

## Returns:
    tuple: A tuple of selected sentence objects (the same objects from document.sentences), ordered by their original position in the document. If no sentences are selected (e.g., count resolves to zero), an empty tuple is returned. Selection and ordering follow AbstractSummarizer._get_best_sentences semantics.

## Raises:
    ValueError:
        - Raised by builder helpers if a required word set is not configured while the corresponding weight is > 0.0:
            * _build_cue_method_instance() raises ValueError if bonus_words or stigma_words are not set.
            * _build_key_method_instance() raises ValueError if bonus_words are not set.
            * _build_title_method_instance() or _build_location_method_instance() raise ValueError if null_words are not set.
    AssertionError:
        - If _update_ratings is given a new_ratings mapping whose length is different from the existing accumulated ratings when the accumulator is non-empty. Concretely, the method asserts that the accumulator is empty or has the same number of keys as new_ratings; a mismatch triggers AssertionError.
    Any exception raised by called helpers or sub-methods:
        - Exceptions from the following calls propagate unchanged:
            * _build_*_method_instance() constructors and their validations
            * method.rate_sentences(document) for each enabled sub-method
            * _update_ratings(ratings, new_ratings)
            * AbstractSummarizer._get_best_sentences(document.sentences, sentences_count, ratings)
        Examples: TypeError, KeyError, IndexError, ValueError, or errors from user-supplied stemmers or document accessors.

## State Changes:
    Attributes READ:
        - self._cue_weight, self._key_weight, self._title_weight, self._location_weight
        - self._bonus_words, self._stigma_words, self._null_words (accessed by the _build_*_method_instance helpers)
        - self._stemmer (indirectly via builders/sub-methods if they use stemming)
    Attributes WRITTEN:
        - None. This method does not mutate the summarizer instance attributes. All accumulation happens in local variables. (Sub-method implementations may mutate objects passed to them; that is outside the summarizer's own attribute changes.)

## Constraints:
    Preconditions:
        - The provided document must be a parsed Document with document.sentences (finite iterable). The method consumes the sentence iterable via the selection helper.
        - If a particular sub-method weight is > 0.0, the corresponding required word set must be configured prior to calling:
            * cue and key weights require bonus_words to be set (cue also requires stigma_words).
            * title and location weights require null_words to be set.
        - At least one of the weights may be > 0.0 to make the summarization meaningful; however, technically all weights can be 0.0 and the method will still call the selection helper with a default-initialized ratings mapping (a defaultdict(int)), resulting in uniform zero scores for all sentences.
        - The per-sub-method rate_sentences implementations are expected to return a mapping with exactly one entry per sentence in document.sentences. _update_ratings asserts either the accumulator is empty or matches the length of each new mapping; if a sub-method returns a mapping with a different length, AssertionError will be raised.
    Postconditions:
        - The instance retains its original configuration; no instance attributes are modified.
        - The returned tuple contains sentences selected from the input document and ordered by original document order.

## Implementation notes / important behaviors to preserve when reimplementing:
    - Ratings accumulator type: the method initializes ratings as collections.defaultdict(int). This is important because:
        * Missing keys return 0 when looked up, so the selection helper may treat any missing per-sentence entries as zero rather than raising KeyError.
        * The accumulator holds numeric sums of ratings; for each enabled sub-method its per-sentence numeric ratings are added to the accumulator.
    - Enabling vs. scaling:
        * Instance weights (self._*_weight) are used only as thresholds to enable or disable the corresponding sub-method. The weights are not multiplied with sub-method outputs in this orchestration code — reimplementations must not unintentionally scale sub-method outputs unless explicitly intended.
    - Sub-method invocation:
        * For each enabled method, the implementation calls method.rate_sentences(document) without additional parameters. For sub-methods that expose optional parameters (e.g., key or cue methods accept weighting parameters), this __call__ uses their default parameter values.
    - Accumulation behavior:
        * The method calls _update_ratings(ratings, new_ratings) to add per-sentence scores. The helper asserts length compatibility (empty accumulator or same number of entries), and then adds numeric values entry-wise.
    - Selection:
        * After accumulation, the method calls AbstractSummarizer._get_best_sentences(document.sentences, sentences_count, ratings) to select and return the top sentences. The ratings mapping (defaultdict(int)) is accepted by the selection helper as a mapping-like rating provider.

## Side Effects:
    - No direct I/O or network calls.
    - Constructs sub-method instances when their weights are > 0.0 (via _build_*_method_instance); those constructors perform validations and may raise ValueError if required word sets are missing.
    - Calls rate_sentences(document) on each enabled sub-method; those calls compute and return per-sentence numeric ratings and may raise errors based on document contents or stemmer behavior.
    - Calls _get_best_sentences which consumes the sentences iterable, sorts by rating, applies the count policy, and returns the selected sentences in original order.

### `sumy.summarizers.edmundson.EdmundsonSummarizer._update_ratings` · *method*

## Summary:
Accumulates numeric ratings from a new mapping into an existing per-sentence ratings mapping, mutating and returning the provided mapping.

## Description:
This helper merges per-sentence scores produced by one Edmundson scoring method (e.g., cue, key, title, location) into the running aggregate used by the summarizer. Known callers:
- EdmundsonSummarizer.__call__: invoked repeatedly during summarization to accumulate ratings returned by each method.rate_sentences(document) call. It is called during the summarization pipeline after each individual scoring method computes its per-sentence ratings.

This logic is factored into its own method to centralize validation (length consistency) and the accumulation operation so multiple scoring methods can be combined consistently and the aggregation behavior can be changed in one place if needed.

## Args:
    ratings (collections.abc.MutableMapping): A mutable mapping from sentence -> numeric score that will be updated in-place. In normal use this is a collections.defaultdict(int) created by the caller (EdmundsonSummarizer.__call__). The mapping must support indexing assignment and in-place addition (ratings[sentence] += rating).
    new_ratings (collections.abc.Mapping): A mapping from sentence -> numeric score produced by a single scoring method (e.g., method.rate_sentences(document)). Values are expected to be numeric (int or float) or otherwise support addition with the corresponding ratings[sentence] value.

## Returns:
    collections.abc.MutableMapping: The same object passed as ratings, after being mutated so each sentence's value equals its original value plus the corresponding value from new_ratings. The method returns the mapping for convenience (the caller typically rebinds to the returned value).

## Raises:
    AssertionError: If len(ratings) != 0 and len(ratings) != len(new_ratings). The method asserts that either ratings is empty (first aggregation) or that the two mappings have the same number of entries before merging.
    KeyError: If the provided ratings mapping does not contain a sentence key present in new_ratings and is not a defaultdict-like mapping that supplies a default value for missing keys, indexing ratings[sentence] may raise KeyError.
    TypeError: If the values in ratings and new_ratings do not support in-place addition with each other (for example, attempting to add a non-numeric type).

## State Changes:
Attributes READ:
    - None: this method does not read or depend on any self.<attr> attributes.

Attributes WRITTEN:
    - None: this method does not modify any self.<attr> attributes.

Note: although no self attributes are changed, the method mutates the ratings mapping passed as an argument (see Side Effects).

## Constraints:
Preconditions:
    - ratings must be a mutable mapping supporting ratings[sentence] += value.
    - new_ratings must be an iterable mapping of (sentence, numeric value) pairs; the method iterates new_ratings.items().
    - Either ratings is empty (len(ratings) == 0) or len(ratings) == len(new_ratings). The assertion enforces this precondition.

Postconditions:
    - For every (sentence, value) in new_ratings, ratings[sentence] will be increased by value.
    - The method returns the same mapping object passed as ratings.

## Side Effects:
    - Mutates the provided ratings mapping in-place by adding values from new_ratings. This may create new keys in ratings if it is a defaultdict or otherwise provides defaults; if it is a plain dict and a sentence key is missing, a KeyError may be raised.
    - No I/O, no network calls, and no modifications to objects other than the provided mappings.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.cue_method` · *method*

## Summary:
Delegates to a cue-based Edmundson summarization method to select the top sentences from the given document using bonus and stigma word weights; does not modify the summarizer's internal state.

## Description:
This is a public convenience wrapper that constructs an EdmundsonCueMethod instance (after validating that bonus and stigma word sets are configured) and delegates the actual ranking and selection to that instance.

Known callers and context:
- Intended to be called by user code or higher-level orchestration when the caller wants a summary produced solely by the cue-word heuristic (bonus/stigma words).
- It is separate from the main __call__ pipeline of EdmundsonSummarizer, which can combine cue, key, title and location methods. Use this method when only the cue-based component is required or when you want to supply explicit bonus/stigma weights for a single run.

Why this is a separate method:
- Encapsulates the process of building and validating a cue-method instance and forwarding arguments; keeps the public API small and focused.
- Allows callers to supply per-call bonus/stigma weights without changing the summarizer's configured weights or combining with other Edmundson sub-methods.
- Keeps input validation and instance creation centralized (the method ensures required word sets exist before the cue-method runs).

## Args:
    document (object): Document-like object expected to expose a .sentences sequence (each sentence exposing .words). No specific document class is required, but missing attributes will raise attribute-access errors when the delegate runs.
    sentences_count (int|callable|str): Controls how many sentences to return. The delegate (_get_best_sentences) accepts:
        - an integer number of sentences,
        - a callable predicate (keeps sentences where predicate(sentence) is True),
        - or a percentage string like '30%' to select that proportion of sentences.
        The precise accepted variants mirror those handled by the summarizer's _get_best_sentences helper.
    bonus_word_value (int|float, optional): Weight applied to occurrences of configured bonus words when scoring sentences. Defaults to 1.
    stigma_word_value (int|float, optional): Weight applied to occurrences of configured stigma words when scoring sentences (subtracted from bonus score). Defaults to 1.

## Returns:
    tuple: Sequence (typically a tuple) of selected sentence objects returned by the underlying EdmundsonCueMethod/_get_best_sentences. The sequence contains the top-ranked sentences according to the cue heuristic and the provided weights. The tuple may be empty (for example, if sentences_count resolves to 0 or there are no sentences).

## Raises:
    ValueError: If the summarizer's bonus words set is empty. Exact message:
        "Set of bonus words is empty. Please set attribute 'bonus_words' with collection of words."
    ValueError: If the summarizer's stigma words set is empty. Exact message:
        "Set of stigma words is empty. Please set attribute 'stigma_words' with collection of words."
    AttributeError (indirect): If the provided document does not expose the expected .sentences (or sentence objects lack .words), the delegation will raise attribute-access errors when attempting to rate sentences.

## State Changes:
    Attributes READ:
        self._stemmer
        self._bonus_words
        self._stigma_words
    Attributes WRITTEN:
        None — this method does not mutate any attributes on self.

## Constraints:
    Preconditions:
        - self._bonus_words must be a non-empty collection (truthy). Otherwise a ValueError is raised (see Raises).
        - self._stigma_words must be a non-empty collection (truthy). Otherwise a ValueError is raised (see Raises).
        - document must provide a .sentences iterable; each sentence must provide .words for token iteration.
    Postconditions:
        - The summarizer instance remains unchanged (no attribute mutations).
        - Returns a sequence (tuple) of sentences selected by the cue-based ranking using the provided bonus_word_value and stigma_word_value.

## Side Effects:
    - No I/O, network, or external service calls occur.
    - No mutation of objects outside self is performed by this method itself; however, the returned sentence objects are references to items from document.sentences (no copies are made by this wrapper).

### `sumy.summarizers.edmundson.EdmundsonSummarizer._build_cue_method_instance` · *method*

## Summary:
Creates and returns a configured EdmundsonCueMethod instance after validating that bonus and stigma word sets are present; does not modify the summarizer's state.

## Description:
- Known callers:
    - EdmundsonSummarizer.__call__: invoked when the summarizer is producing a rating component (when cue_weight > 0.0) as part of the full summarization pipeline.
    - EdmundsonSummarizer.cue_method: invoked when a caller requests only the cue-based summarization method directly.
- Context:
    - This method is called during the summarization lifecycle at the stage where component rating methods (cue/key/title/location) are assembled and used to compute sentence ratings.
- Why this is a separate method:
    - Centralizes validation (ensuring required word sets are set) and object construction in one place so callers can obtain a ready-to-use EdmundsonCueMethod without duplicating validation logic.
    - Keeps the public entry points (__call__, cue_method) concise and separates responsibility for building the method instance from using it.

## Args:
    None

## Returns:
    EdmundsonCueMethod
    - A newly constructed EdmundsonCueMethod initialized as EdmundsonCueMethod(self._stemmer, self._bonus_words, self._stigma_words).
    - Under normal conditions this is a non-null object ready to rate sentences.
    - There are no alternative return values; if preconditions fail, the method raises instead of returning.

## Raises:
    ValueError
    - Raised if self._bonus_words is empty or falsy. Exact message raised by the check:
      "Set of bonus words is empty. Please set attribute 'bonus_words' with collection of words."
    - Raised if self._stigma_words is empty or falsy. Exact message raised by the check:
      "Set of stigma words is empty. Please set attribute 'stigma_words' with collection of words."
    - Note: The bonus-words check runs first, so if both are empty the bonus-words message is raised.

## State Changes:
- Attributes READ:
    - self._stemmer (used to pass to the EdmundsonCueMethod constructor)
    - self._bonus_words (passed through to EdmundsonCueMethod)
    - self._stigma_words (passed through to EdmundsonCueMethod)
- Attributes WRITTEN:
    - None (this method does not modify any attribute of self)

## Constraints:
- Preconditions:
    - self._bonus_words must be a non-empty collection (truthy). In this class, bonus_words is stored as a frozenset of stemmed words via the bonus_words setter.
    - self._stigma_words must be a non-empty collection (truthy). In this class, stigma_words is stored as a frozenset of stemmed words via the stigma_words setter.
    - self._stemmer must be initialized (the class constructor assigns a stemmer; default is null_stemmer).
- Postconditions:
    - If the method returns normally, the returned object is an EdmundsonCueMethod whose internal attributes (_bonus_words and _stigma_words) refer to the same frozenset objects held by the summarizer, and whose stemmer is the summarizer's stemmer.
    - The summarizer's own attributes remain unchanged.

## Side Effects:
    - Instantiates an EdmundsonCueMethod object (memory allocation).
    - No I/O, no network calls, and no modifications to external objects beyond creating the new instance.
    - May raise ValueError (see Raises) preventing construction.

## Implementation notes (for reimplementation):
    - Call the internal validators __check_bonus_words() and __check_stigma_words() in that order to reproduce exact raising behavior and messages.
    - Return EdmundsonCueMethod(self._stemmer, self._bonus_words, self._stigma_words).
    - Do not alter or re-stem the stored sets; pass them through as-is.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.key_method` · *method*

block and contains only the documentation text.

Action: WRITE
<DOCUMENTATION>
## Summary:
Runs the Edmundson "key words" sub-method to obtain a ranked sequence of sentences and returns a subset according to the provided sentences_count policy; does not mutate the summarizer instance.

## Description:
This convenience method builds a key-method instance, invokes it to obtain a ranked sequence of sentences (ranked_sentences), and then applies the sentences_count selection policy to that ranked sequence, returning the selected sentences as a tuple.

Known callers / typical use:
- Called directly by client code that wants a summary produced only by the "key" heuristic.
- Not used by EdmundsonSummarizer.__call__ when composing multi-heuristic summaries; __call__ uses the key sub-component's rate_sentences method instead to merge numeric ratings.
- Invocation time: at summarization time when a parsed document (with .sentences and .words) is available.

Why a separate method:
- Encapsulates building the key-method instance, invoking it, and applying the flexible selection logic (callable, integer, or percentage) in one place, avoiding duplication of selection/parsing logic.

## Args:
    document (object): Parsed document expected to provide:
        - document.sentences: ordered iterable of sentence objects
        - document.words: iterable of document-level tokens
      Sentence objects must be hashable (for rating maps) and expose .words for token access.
    sentences_count (int | callable | str):
        - int: number of top-ranked sentences to return (will be capped to available sentences).
        - callable: predicate invoked as predicate(sentence) -> truthy/falsey; all ranked sentences for which predicate returns truthy are returned (in ranked order).
        - str: percentage string ending with '%' (e.g., "30%"); computed as max(1, int(len(ranked_sentences) * percent/100)).
    weight (float, optional): forwarded as the second positional argument when calling the underlying key-method instance; defaults to 0.5.

## Returns:
    tuple: Selected sentence objects as an ordered tuple.
        - Callable policy: tuple of sentences from ranked_sentences for which sentences_count(sentence) is truthy, preserving the underlying ranked order.
        - Percentage string: computes count = max(1, int(len(ranked_sentences) * percent/100)) and returns the first count items.
        - Integer-like value: returns the first min(int(sentences_count), len(ranked_sentences)) items.
        - If ranked_sentences is empty, returns an empty tuple.

Important expectations about ranked_sentences:
    - The underlying instance(document, weight) is expected to return a finite, ordered sequence supporting len() and slicing, because this method uses len(ranked_sentences) for percentage calculation and ranked_sentences[:count] for slicing.
    - If ranked_sentences is an iterator without __len__ or slicing, percentage and slicing operations will raise TypeError or AttributeError.

## Raises:
    ValueError: If no key-method instance could be built:
        - Raised explicitly by this method with the message: "Bonus words must be set before calling the key method."
          (This happens when self._build_key_method_instance() returns None.)
    TypeError: If the returned instance is not callable or has an incompatible signature when invoked as instance(document, weight).
    Any exception propagated from:
        - self._build_key_method_instance() (for example ValueError thrown internally when bonus words are not set).
        - The underlying instance when invoked (exceptions from its internal logic, from the configured stemmer, or from its use of _get_best_sentences).
        - Converting sentences_count to int or parsing percentage values (ValueError or TypeError for invalid inputs).
    Note: this method does not catch these exceptions; they propagate to the caller.

## State Changes:
Attributes READ:
    - Calls self._build_key_method_instance(), which inspects internal state and expects:
        - self._bonus_words to be set and non-empty
        - self._stemmer usable by the constructed EdmundsonKeyMethod
    - No other self attributes are read directly in this method body.

Attributes WRITTEN:
    - None. The method does not modify any self.<attr> fields.

## Constraints:
Preconditions:
    - self._bonus_words must be set (non-empty) or _build_key_method_instance() will raise.
    - document must provide .sentences and .words as required by the underlying key-method logic.
    - sentences_count must be either callable, an int-convertible value, or a percentage string ending with '%'.
    - The underlying key-method instance must accept the call instance(document, weight) and return an ordered, finite sequence of sentences.

Postconditions:
    - The returned tuple contains sentences drawn from the underlying ranked sequence produced by the key-method instance.
    - The summarizer instance's state remains unchanged.

## Side Effects:
    - No file, network, or external I/O is performed by this method.
    - The method invokes the configured stemmer and algorithms inside the key-method instance; those perform in-memory computation and return results.

### `sumy.summarizers.edmundson.EdmundsonSummarizer._build_key_method_instance` · *method*

## Summary:
Constructs and returns a new EdmundsonKeyMethod configured with this summarizer's stemmer and bonus-words collection; validates bonus-words before construction and does not mutate the summarizer.

## Description:
Known callers and pipeline context:
- __call__(document, sentences_count) when self._key_weight > 0.0:
  - The returned object is used via its rate_sentences(document) method to produce per-sentence ratings that are merged into the summarization pipeline.
- key_method(document, sentences_count, weight=0.5):
  - The returned object is invoked (callable) to produce a ranked sequence of sentences (key-based ranking). key_method expects the builder to return a usable EdmundsonKeyMethod instance.

Lifecycle stage:
- This builder is invoked at runtime during summarization when key-based scoring is required (either as part of the full-weighted fusion in __call__ or when the key-specific helper key_method is called).

Why this is a separate method:
- Encapsulates validation (ensuring bonus words are present) and the construction of the EdmundsonKeyMethod in a single place so multiple call sites reuse the same logic and error messaging. Keeping construction isolated reduces duplication and centralizes the precondition check.

## Args:
    None

## Returns:
    EdmundsonKeyMethod
    - A newly constructed EdmundsonKeyMethod instance created as EdmundsonKeyMethod(self._stemmer, self._bonus_words).
    - This method never returns None; it either returns the instance or raises an exception.

## Raises:
    ValueError
    - Raised when the summarizer's bonus-words collection is empty or falsy.
    - Exact message (raised by the internal check): "Set of bonus words is empty. Please set attribute 'bonus_words' with collection of words."

## State Changes:
Attributes READ:
    - self._stemmer: used as the first argument when constructing the EdmundsonKeyMethod.
    - self._bonus_words: used as the second argument when constructing the EdmundsonKeyMethod; also validated via __check_bonus_words().

Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - The summarizer must have bonus words set (self._bonus_words must be truthy). The bonus_words property setter in this class converts an input collection into a frozenset of stemmed words; callers must have invoked that setter prior to calling this builder when key scoring is required.
    - self._stemmer must be a callable (this is established by AbstractSummarizer.__init__, which must have been run during object construction).

Postconditions:
    - On successful return, a valid EdmundsonKeyMethod instance is produced and returned; no mutation occurs on self.
    - If the precondition on bonus words is not met, a ValueError is raised and no instance is created.

## Side Effects:
    - Constructs (instantiates) an EdmundsonKeyMethod object. Any side effects of that class's constructor (internal allocations or initialization logic within EdmundsonKeyMethod) may occur, but this method performs no I/O and does not call external services directly.
    - No global state is modified and no attributes on self are changed.

## Notes and implementation details:
    - The method delegates the "bonus words must be present" check to self.__check_bonus_words(), which raises the ValueError with the exact message documented above when the bonus set is empty.
    - The implementation immediately returns the EdmundsonKeyMethod instance constructed with the summarizer's stemmer and bonus words. Any code appearing after the return is unreachable and has no effect on behavior.
    - Consumers expect the returned object to support both rate_sentences(document) (used by __call__) and callable invocation (used by key_method) per existing call sites.

### `sumy.summarizers.edmundson.EdmundsonSummarizer._build_title_method_instance` · *method*

## Summary:
Creates and returns a new EdmundsonTitleMethod instance configured with this summarizer's stemmer and current null-words set; does not mutate the summarizer.

## Description:
Known callers and contexts:
- EdmundsonSummarizer.__call__: invoked when the summarizer is run and title-based weighting (_title_weight) is greater than 0. The returned instance is used to rate sentences (rate_sentences) and contribute to combined sentence ratings.
- EdmundsonSummarizer.title_method: used by the convenience wrapper to obtain a callable summarization method that will be invoked with (document, sentences_count).

Lifecycle stage:
- This method is part of the summarizer's runtime pipeline where per-technique helper objects are constructed just before they are used to score or select sentences.

Why this is a separate method:
- Encapsulates precondition checking (null-words presence) and instantiation in one place.
- Follows the pattern used by other Edmundson _build_* factory helpers (cue/key/location), centralizing validation and construction so callers don't need to duplicate checks.

## Args:
None.

## Returns:
EdmundsonTitleMethod
- A freshly constructed instance of EdmundsonTitleMethod initialized with:
  - stemmer: the summarizer's self._stemmer (typically the stemmer passed to the summarizer constructor; default is null_stemmer).
  - null_words: the summarizer's self._null_words (a frozenset of stemmed words).
- Edge cases:
  - This method never returns None.
  - If preconditions are not met (see Raises), no instance is returned.

## Raises:
ValueError
- Raised when the summarizer's null-words set is empty. Trigger condition: self.__check_null_words() detects that self._null_words is empty and raises ValueError with the message "Set of null words is empty. Please set attribute 'null_words' with collection of words."

## State Changes:
Attributes READ:
- self._stemmer
- self._null_words

Attributes WRITTEN:
- None (the method does not modify the summarizer's attributes)

## Constraints:
Preconditions:
- self._null_words must be a non-empty collection (the class uses a frozenset for null words; they are normally set via the null_words setter which stems input words).
- self._stemmer should be a valid stemmer instance (the summarizer sets a default null_stemmer if none is provided).

Postconditions:
- If no exception is raised, the caller receives a new EdmundsonTitleMethod instance whose internal _stemmer and _null_words fields are references to self._stemmer and self._null_words respectively.
- The summarizer's internal state remains unchanged.

## Side Effects:
- May raise ValueError (see Raises) — a control-flow effect visible to callers.
- No I/O, no network calls, and no mutation of objects outside of creating the EdmundsonTitleMethod instance.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.location_method` · *method*

## Summary:
Delegates to a location-based Edmundson summarization callable (constructed by _build_location_method_instance) to produce an extractive summary; does not mutate the summarizer object.

## Description:
This method constructs a location-method summarizer instance by calling self._build_location_method_instance(), then immediately invokes that callable with the provided arguments and returns its result. The constructed instance is expected to implement __call__(document, sentences_count, w_h, w_p1, w_p2, w_s1, w_s2); the repository includes EdmundsonLocationMethod with that signature which computes significant words, rates sentences, and selects the top sentences.

Known callers and lifecycle:
- Part of the public EdmundsonSummarizer API; called when a location-based extractive summary is requested from an EdmundsonSummarizer instance.
- Invocation occurs at summarization/runtime; it is not used during object construction.
- Other summarization strategies in the same module (cue/key/title variants) follow the same build-and-delegate pattern.

Why separate:
- Separates construction/configuration of the concrete location-method instance from invocation so subclasses may override _build_location_method_instance to provide custom stemmers, null-word sets, or reuse instances without changing invocation code.

## Args:
    document (Document):
        Document-like object to summarize. Must provide:
        - headings: iterable of heading objects (each exposing .words)
        - paragraphs: iterable of paragraph objects (each exposing .sentences)
        - sentences: iterable of sentence objects (used by the underlying selector)
        - sentence and word objects must expose .words (iterable of strings)
    sentences_count (int):
        Maximum number of sentences to return. Passed through unchanged to the underlying callable. Expected to be an integer; this method does not validate range.
    w_h (int|float, optional):
        Weight applied to heading-derived score. Default: 1
    w_p1 (int|float, optional):
        Weight added if a sentence is in the first paragraph. Default: 1
    w_p2 (int|float, optional):
        Weight added if a sentence is in the last paragraph. Default: 1
    w_s1 (int|float, optional):
        Weight added if a sentence is the first in its paragraph. Default: 1
    w_s2 (int|float, optional):
        Weight added if a sentence is the last in its paragraph. Default: 1

## Returns:
    Any:
        The value returned by the callable produced by _build_location_method_instance. In the standard implementation (EdmundsonLocationMethod.__call__), this is the result of _get_best_sentences(document.sentences, sentences_count, ratings) — typically an ordered collection (e.g., list) of sentence objects with length at most sentences_count. This method does not transform or validate the returned value.

## Raises:
    - AttributeError: If self has no attribute _build_location_method_instance (attribute lookup failure) — raised by Python when attempting to call a missing attribute.
    - TypeError: If _build_location_method_instance returns a non-callable object, or if the returned callable is invoked with incompatible argument types.
    - Any exception raised during construction by _build_location_method_instance or during execution of the returned callable (e.g., if the document does not expose required attributes). All such exceptions are propagated unchanged.

## State Changes:
    Attributes READ:
        - self._build_location_method_instance (method attribute is accessed and invoked)
    Attributes WRITTEN:
        - None. The method does not assign to any attributes on self.

## Constraints:
    Preconditions:
        - The summarizer instance must implement _build_location_method_instance() and it must return a callable accepting the same positional parameters as this method.
        - document must conform to the minimal Document interface described above.
        - sentences_count should be an int for meaningful behavior (this method does not perform type coercion or validation).
    Postconditions:
        - self remains unmodified by this call.
        - The return value equals whatever the constructed callable returns; no additional guarantees beyond that.

## Side Effects:
    - No I/O or external network activity is performed by this wrapper itself.
    - Any side effects produced by _build_location_method_instance or by the delegated callable (for example, internal caching performed by the builder or callable) will be observed by callers because this method forwards the call directly.

### `sumy.summarizers.edmundson.EdmundsonSummarizer._build_location_method_instance` · *method*

## Summary:
Creates and returns a new EdmundsonLocationMethod instance configured with the summarizer's stemmer and null-words set; no object state is modified.

## Description:
This helper constructs the location-based summarization method used to score sentences by document/headings/paragraph/sentence positions. Known callers:
- EdmundsonSummarizer.__call__ — invoked during the summarization pipeline when the instance's location_weight is greater than 0.0; used to obtain a method instance whose rate_sentences method will produce location-based ratings.
- EdmundsonSummarizer.location_method — invoked when a caller directly requests the location method (and then calls the returned instance with weights and document).

This logic is factored into its own method to centralize the validation (null words check) and the creation of the EdmundsonLocationMethod object. That keeps construction consistent with the other Edmundson*Method builders (cue/key/title) and avoids duplicating the null-word precondition in multiple places.

## Args:
    None

## Returns:
    EdmundsonLocationMethod
    - A newly created instance initialized with:
        - stemmer = self._stemmer (the summarizer's stemmer object, often null_stemmer by default)
        - null_words = self._null_words (a frozenset of stemmed "null" words)
    - The returned instance is fresh on each call (not cached).

## Raises:
    ValueError
    - Raised when the summarizer's null-words set is empty. This happens because the method calls self.__check_null_words(), which raises ValueError with the message:
      "Set of null words is empty. Please set attribute 'null_words' with collection of words."
    - No other exceptions are raised directly by this method (constructor of EdmundsonLocationMethod is expected to accept the provided arguments).

## State Changes:
    Attributes READ:
    - self._stemmer — used to initialize the returned EdmundsonLocationMethod.
    - self._null_words — validated via __check_null_words() and passed to the new instance.

    Attributes WRITTEN:
    - None — this method does not modify any attribute on self.

## Constraints:
    Preconditions:
    - self must be an initialized EdmundsonSummarizer instance.
    - self._null_words must be a non-empty collection (frozenset) of stemmed words; otherwise the method will raise ValueError.
    - self._stemmer should be a valid stemmer object compatible with AbstractSummarizer/EdmundsonLocationMethod (the class uses this stemmer for stemming words).

    Postconditions:
    - If no exception is raised, the method returns an EdmundsonLocationMethod instance whose internal stemmer and null-words reference the values taken from self at call time.
    - The summarizer's attributes remain unchanged.

## Side Effects:
    - No I/O, network, or filesystem activity.
    - No mutation of external objects.
    - Calling this method invokes the constructor of EdmundsonLocationMethod (which itself calls its superclass constructor to set up its stemmer), but that construction is confined to the newly returned object and does not mutate self or global state.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.__check_bonus_words` · *method*

## Summary:
Validate that the summarizer has a non-empty collection of bonus words and raise a clear error if it does not; does not modify object state.

## Description:
Known callers:
- _build_cue_method_instance — invoked before creating an EdmundsonCueMethod instance.
- _build_key_method_instance — invoked before creating an EdmundsonKeyMethod instance.
Indirect callers / pipeline context:
- cue_method and key_method call the above builders and therefore trigger this validation when higher-level callers request cue- or key-based summarization.
- __call__ invokes the builders when the corresponding weights (_cue_weight or _key_weight) are greater than 0.0 during the summarization pipeline.

Why this is a separate method:
- Centralizes a single validation check used by multiple builder methods so the same error message and precondition are enforced consistently.
- Keeps builder methods focused on construction logic and avoids duplicating validation logic across methods.

## Args:
None.

## Returns:
None. The method either returns None after successful validation or raises an exception.

## Raises:
ValueError: Raised when the internal bonus-words collection is empty or falsy.
- Condition: self._bonus_words is falsy (e.g., empty set, empty frozenset, None).
- Exact message produced: "Set of bonus words is empty. Please set attribute 'bonus_words' with collection of words."

## State Changes:
Attributes READ:
- self._bonus_words

Attributes WRITTEN:
- None (the method does not modify any attributes)

## Constraints:
Preconditions:
- The caller expects that bonus words have been set previously (typically via the bonus_words property setter). The setter in this class converts a provided collection into a frozenset of stemmed words.

Postconditions:
- On successful return (no exception), self._bonus_words is guaranteed to be truthy (non-empty) for the rest of the call path.
- No mutation of self occurs.

## Side Effects:
- None. The method performs no I/O, does not call external services, and mutates no objects outside self.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.__check_stigma_words` · *method*

## Summary:
Validates that the summarizer has a non-empty collection of stigma words and raises a clear error if it does not; does not modify object state.

## Description:
Known callers and context:
- Called directly by _build_cue_method_instance() when preparing an EdmundsonCueMethod instance.
- Indirectly invoked as part of:
  - cue_method() (which calls _build_cue_method_instance()), and
  - __call__() when the cue weight is enabled (the summarizer's main execution path).
This method runs during summarizer configuration/initialization checks immediately before creating a cue-based summarization method.

Why this is a separate method:
- Encapsulates a single validation step with a consistent error message used in multiple call sites.
- Keeps _build_cue_method_instance() and higher-level flows concise and avoids duplicating the same check in more than one place.
- Being a private, name-mangled method, it centralizes precondition enforcement for building cue-related components.

## Args:
    None

## Returns:
    None
    - The method returns None on success (no exception). It does not return a value and serves solely to validate state.

## Raises:
    ValueError:
        - Trigger condition: self._stigma_words is falsy (for example, an empty frozenset, empty collection, None, or any other value that evaluates to False).
        - Exact message produced by the implementation:
          "Set of stigma words is empty. Please set attribute 'stigma_words' with collection of words."

## State Changes:
    Attributes READ:
        - self._stigma_words
    Attributes WRITTEN:
        - None (this method does not modify any attributes)

## Constraints:
    Preconditions:
        - The object must have the attribute self._stigma_words defined (the class initializes it at construction).
        - Typical expected type is a collection/frozenset of stemmed words (the property's setter converts inputs to a frozenset), but the method only checks truthiness and does not enforce element types.
    Postconditions:
        - If the method returns without raising, self._stigma_words is guaranteed to be truthy (i.e., not empty) at the point of return.
        - The method does not alter self._stigma_words or any other object state.

## Side Effects:
    - None. The method performs no I/O, makes no external service calls, and does not mutate objects outside of self.

### `sumy.summarizers.edmundson.EdmundsonSummarizer.__check_null_words` · *method*

## Summary:
Validates that the instance has a truthy collection of null words and raises a ValueError with a clear message if the collection is empty; does not mutate object state.

## Description:
This small internal helper performs a presence check on the instance attribute _null_words. It centralizes the guard used before any summarizer processing that depends on a configured null-words collection.

Callers / invocation context:
- No callers are present in the provided snippet. The method is intended to be called by other methods of the summarizer implementation at setup time or immediately before operations that require access to the null-words collection (for example: filtering, scoring, or feature extraction that excludes null words).
- It is implemented as a private method (name-mangled) and therefore intended for internal use only.

Why this is a separate method:
- Keeps a single, consistent validation and error message in one place.
- Prevents code duplication across multiple entry points that require the null-words collection.

## Args:
    None

## Returns:
    None
    - The function returns normally (None) when validation passes.

## Raises:
    ValueError: Raised when self._null_words is present but falsey (for example: empty set(), empty list [], empty tuple (), empty dict {}, empty string '', or None). The exact message raised is:
        "Set of null words is empty. Please set attribute 'null_words' with collection of words."
    AttributeError: If the instance does not have an attribute named _null_words, attempting to access self._null_words will raise AttributeError before the ValueError check.

## State Changes:
    Attributes READ:
        self._null_words
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - The caller should ensure the instance defines an attribute named _null_words (commonly set by the class's configuration or initializer).
        - The attribute should be a collection-like object containing words (typical types: set, list, tuple). The method itself does not enforce element types.

    Postconditions:
        - If the method returns without raising, self._null_words is truthy (i.e., it evaluates to True in a boolean context and therefore is non-empty).
        - No attributes of the instance are modified.

## Side Effects:
    - No I/O or network interactions.
    - The only effect observable outside the method is that it may raise an exception which interrupts the caller's flow.

## Implementation notes / edge cases:
    - The check uses Python truthiness: any empty or falsey value leads to ValueError. A non-empty string is truthy (and will pass), but a string is generally not a suitable "collection of words" (it will be treated as a sequence of characters), so callers should prefer container types like set or list.
    - The error message references 'null_words' (without the leading underscore). This implies the class may expose a public configuration attribute or property named 'null_words' that sets the internal _null_words; callers should set the public API expected by the class rather than directly manipulating underscored internals.
    - Because the method name begins with double underscores, it is name-mangled by Python (e.g., _EdmundsonSummarizer__check_null_words) and is intended to be private to the class.

