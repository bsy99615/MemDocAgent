# `luhn.py`

## `sumy.summarizers.luhn.LuhnSummarizer` · *class*

## Summary:
Implements the Luhn text summarization algorithm that identifies important sentences based on significant words and their distribution patterns.

## Description:
The LuhnSummarizer applies the Luhn algorithm for automatic text summarization. It identifies significant words using term frequency analysis and rates sentences based on how these significant words are distributed in chunks with acceptable gaps. This class is designed to be instantiated and used as a summarization tool for extracting the most important sentences from a document.

The algorithm works by:
1. Identifying significant words using Term Frequency analysis
2. Grouping words into chunks separated by gaps of non-significant words
3. Rating chunks based on the density of significant words
4. Assigning sentence scores based on maximum chunk ratings

## State:
- max_gap_size: int, default 4 - Maximum number of consecutive non-significant words allowed in a chunk before ending it
- significant_percentage: int, default 1 - Percentage of most frequent terms to consider as significant (1 = 100%)
- _stop_words: frozenset - Set of normalized stop words to exclude from significant word identification
- _stemmer: callable - Stemmer function inherited from AbstractSummarizer for word stemming

## Lifecycle:
- Creation: Instantiate with optional stemmer parameter (inherits from AbstractSummarizer)
- Usage: Call instance with document and desired sentence count (document, sentences_count)
- Destruction: No special cleanup required, relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[LuhnSummarizer.__call__) --> B[_get_significant_words]
    B --> C[TfDocumentModel]
    A --> D[_get_best_sentences]
    D --> E[rate_sentence]
    E --> F[_get_chunk_ratings]
    F --> G[_get_chunk_rating]
    G --> H[__remove_trailing_zeros]
```

## Raises:
- ValueError: When stemmer is not callable during initialization (inherited from AbstractSummarizer)
- NotImplementedError: From parent class if not properly overridden (though this is overridden in LuhnSummarizer)

## Example:
```python
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

# Create summarizer instance
summarizer = LuhnSummarizer()

# Configure stop words if needed
summarizer.stop_words = ['the', 'and', 'or']

# Parse document
parser = PlaintextParser.from_file("document.txt", Tokenizer("english"))
document = parser.document

# Generate summary
summary = summarizer(document, sentences_count=3)
for sentence in summary:
    print(sentence)
```

### `sumy.summarizers.luhn.LuhnSummarizer.stop_words` · *method*

## Summary:
Configures the set of stop words to be excluded from text analysis during summarization.

## Description:
Sets the internal frozenset of stop words that will be filtered out when processing documents for summarization. This method normalizes each input word to lowercase and stores them as a frozenset for efficient lookup during text processing.

## Args:
    words (iterable): An iterable of word strings to be treated as stop words.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._stop_words

## Constraints:
    Preconditions: The `words` parameter must be iterable containing string-like objects.
    Postconditions: self._stop_words is updated to a frozenset of normalized versions of the input words.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `sumy.summarizers.luhn.LuhnSummarizer.__call__` · *method*

## Summary:
Processes a document to generate a summary by selecting the most important sentences based on significant word frequency and distribution.

## Description:
This method implements the core Luhn summarization algorithm by identifying significant words in the document and then ranking sentences based on how many of these significant words they contain. It serves as the main interface for generating document summaries.

## Args:
    document (Document): The input document containing sentences to summarize
    sentences_count (int): The number of sentences to include in the final summary

## Returns:
    tuple[Sentence]: A tuple of Sentence objects representing the most important sentences in the document

## Raises:
    None explicitly raised, but may propagate exceptions from underlying methods like _get_significant_words or _get_best_sentences

## State Changes:
    Attributes READ: 
    - self._stop_words
    - self.significant_percentage
    - self.rate_sentence
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - Document must have a valid structure with sentences and words attributes
    - Sentences_count must be a non-negative integer
    - The document should contain sufficient content for meaningful summarization
    
    Postconditions:
    - Returns exactly sentences_count sentences (or fewer if document is too short)
    - Sentences are ordered as they appear in the original document

## Side Effects:
    None - This method is pure and does not cause any I/O operations or external service calls

### `sumy.summarizers.luhn.LuhnSummarizer._get_significant_words` · *method*

## Summary:
Extracts significant words from a collection by normalizing, stemming, filtering stop words, and selecting most frequent terms based on configured percentage threshold.

## Description:
This method processes a collection of words through several transformations to identify the most significant terms for text summarization. It normalizes each word to lowercase, stems words to their root forms, removes stop words, creates a term frequency model, selects the most frequent terms according to the configured percentage, and filters for terms that appear more than once. This method is used internally by the Luhn summarizer algorithm to identify key terminology that should be considered when rating sentences for inclusion in the summary.

## Args:
    words (list[str]): Collection of words to process for significance extraction

## Returns:
    tuple[str]: Tuple of significant words that meet the frequency criteria

## Raises:
    ValueError: When `most_frequent_terms` is called with negative count value (though this shouldn't occur due to calculation)

## State Changes:
    Attributes READ: 
        - self._stop_words: Used to filter out common words
        - self.significant_percentage: Used to calculate number of terms to select
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - Input words should be valid string representations
        - `self.significant_percentage` should be a positive value between 0 and 1
        - `self._stop_words` should be a frozenset of normalized words
    Postconditions:
        - Returned tuple contains only words that appear more than once in the original word collection
        - Returned tuple length is at most `int(len(words) * self.significant_percentage)` 
        - All returned words are normalized and stemmed versions of input words

## Side Effects:
    None

### `sumy.summarizers.luhn.LuhnSummarizer.rate_sentence` · *method*

*No documentation generated.*

### `sumy.summarizers.luhn.LuhnSummarizer._get_chunk_ratings` · *method*

## Summary:
Identifies contiguous chunks of significant words in a sentence and computes their ratings.

## Description:
Processes a sentence to detect sequences of consecutive significant words separated by gaps of non-significant words. Each detected chunk is then rated using the class's chunk rating algorithm. This method is used internally by the Luhn summarization algorithm to evaluate sentence quality based on significant word clustering. It is called by the `rate_sentence` method during the sentence scoring phase of summarization.

## Args:
    sentence (Sentence): The sentence object containing words to process
    significant_stems (set): Set of word stems considered significant for summarization

## Returns:
    tuple[float]: A tuple of floating-point ratings for each identified chunk, where each rating represents the significance of that word cluster

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.max_gap_size, self.stem_word
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Sentence must have a `words` attribute containing word objects
    - Significant_stems must be a set-like object supporting membership testing
    - self.max_gap_size must be a positive integer
    
    Postconditions:
    - Returns a tuple of non-negative floating-point numbers
    - Each rating reflects the density of significant words in its respective chunk

## Side Effects:
    None

### `sumy.summarizers.luhn.LuhnSummarizer._get_chunk_rating` · *method*

## Summary:
Calculates a normalized significance rating for a chunk of words in a sentence based on the proportion of significant words.

## Description:
This method computes a numerical rating for a chunk of words that represents the relative importance of significant words within that chunk. It's used as part of the Luhn algorithm for text summarization to evaluate sentence quality. The method removes trailing zeros from the chunk (representing insignificant words) before calculation, and applies a special case for single significant words.

The rating formula is: (significant_words²) / words_count when significant_words > 1, and 0 when significant_words = 1. This prevents over-weighting single significant words while still giving meaningful scores to chunks with multiple significant words.

## Args:
    chunk (list[int]): A list of integers representing word significance (1 for significant, 0 for insignificant) in a sentence chunk.

## Returns:
    float: The calculated chunk rating, which represents the normalized significance of the chunk. Returns 0 when there is exactly one significant word in the chunk, otherwise returns (significant_words^2) / words_count.

## Raises:
    AssertionError: When the chunk contains no words after removing trailing zeros (words_count <= 0).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The chunk must contain at least one word after processing (after removing trailing zeros)
    - Each element in chunk must be either 0 or 1
    
    Postconditions:
    - Returns 0 when significant_words == 1
    - Returns a positive float when significant_words > 1
    - The result is bounded by the ratio of significant words to total words, squared

## Side Effects:
    None

### `sumy.summarizers.luhn.LuhnSummarizer.__remove_trailing_zeros` · *method*

## Summary:
Removes trailing zero elements from a collection, returning a new collection with trailing zeros excluded.

## Description:
This private method removes trailing zero elements from the input collection by iterating from the end toward the beginning until a non-zero element is found. It's designed to clean up numerical collections that may contain trailing zeros, commonly encountered in TF-IDF weight calculations or similar text processing operations.

The method is typically used internally by the Luhn summarization algorithm to optimize storage and processing of numerical representations of document features.

## Args:
    collection (list or array-like): A sequence containing numeric values that may have trailing zeros at the end.

## Returns:
    list or array-like: A new collection with trailing zeros removed. If the input contains only zeros, returns an empty collection. If no trailing zeros exist, returns a copy of the original collection.

## Raises:
    None explicitly raised. However, the method assumes the input supports indexing and slicing operations.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - Input collection must support indexing via square bracket notation (collection[index])
        - Input collection must support slicing operations (collection[:index + 1])
        - Input collection must be iterable and have a defined length
    
    Postconditions:
        - The returned collection will not contain trailing zero elements
        - The returned collection will be a shallow copy of the input (no mutation of original)
        - Empty collections or collections with only zeros will return empty collections

## Side Effects:
    None. This is a pure function that doesn't perform I/O operations or mutate external state.

