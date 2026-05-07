# `lsa.py`

## `sumy.summarizers.lsa.LsaSummarizer` · *class*

## Summary:
Implements Latent Semantic Analysis (LSA) for automatic text summarization by decomposing term-document matrices using Singular Value Decomposition.

## Description:
The LsaSummarizer class applies Latent Semantic Analysis to extract the most important sentences from a document. It constructs a term-document matrix, computes term frequencies, performs SVD decomposition, and ranks sentences based on their semantic similarity to the overall document structure. This class is typically instantiated by summarization pipeline components or directly by users seeking LSA-based summarization.

The class inherits from AbstractSummarizer and provides a concrete implementation of the summarization algorithm using linear algebra techniques to capture latent semantic relationships between words and sentences.

## State:
- _stop_words: frozenset of normalized and stemmed words to exclude from the analysis
- MIN_DIMENSIONS: class constant (3) representing minimum number of dimensions for SVD reduction
- REDUCTION_RATIO: class constant (1.0) controlling the proportion of dimensions to retain in SVD

## Lifecycle:
Creation: Instantiate with optional stemmer parameter (inherited from AbstractSummarizer). Stop words can be set via the stop_words property.
Usage: Call the instance with a document object and desired number of sentences to extract.
Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[LsaSummarizer.__call__) --> B[_ensure_dependencies_installed]
    B --> C[_create_dictionary]
    C --> D[_create_matrix]
    D --> E[_compute_term_frequency]
    E --> F[singular_value_decomposition]
    F --> G[_compute_ranks]
    G --> H[_get_best_sentences]
```

## Raises:
- ValueError: When NumPy dependency is not installed during initialization
- AssertionError: In _compute_term_frequency when smooth parameter is out of bounds [0.0, 1.0)
- AssertionError: In _compute_ranks when sigma and v_matrix dimensions don't match

## Example:
```python
from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

# Create summarizer instance
summarizer = LsaSummarizer()

# Set custom stop words if needed
summarizer.stop_words = ["the", "and", "or"]

# Parse document
parser = PlaintextParser.from_string("Your long text here...", Tokenizer("english"))
document = parser.document

# Generate summary
summary = summarizer(document, sentences_count=3)
for sentence in summary:
    print(sentence)
```

### `sumy.summarizers.lsa.LsaSummarizer.stop_words` · *method*

## Summary:
Sets the stop words for the LSA summarizer by normalizing and storing them as a frozenset.

## Description:
This method serves as a setter property for the `_stop_words` attribute in the LsaSummarizer class. It takes a collection of words, normalizes each word using the inherited `normalize_word` method (which converts to lowercase Unicode), and stores them as an immutable frozenset in the instance variable `_stop_words`. This set is subsequently used by the `_create_dictionary` method to filter out common words during the document processing phase of LSA summarization.

## Args:
    words (iterable): An iterable collection of words to be treated as stop words.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._stop_words

## Constraints:
    Preconditions: The `words` parameter should be iterable containing string-like objects.
    Postconditions: The `_stop_words` attribute is updated to contain a frozenset of normalized words.

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only modifies the instance's internal state.

### `sumy.summarizers.lsa.LsaSummarizer.__call__` · *method*

## Summary:
Performs Latent Semantic Analysis (LSA) based text summarization by computing sentence rankings using SVD decomposition and returning the highest-ranked sentences.

## Description:
This method implements the core LSA summarization algorithm that analyzes semantic relationships between words and sentences in a document. It constructs a term-document matrix, applies TF-IDF weighting, performs singular value decomposition to reduce dimensionality, and computes sentence ranks based on their semantic importance. The method is designed to be called as part of the summarization pipeline where it processes a document and returns a summary of the specified length.

## Args:
    document (Document): The input document containing sentences to summarize
    sentences_count (int): The desired number of sentences in the resulting summary

## Returns:
    tuple[Sentence]: A tuple of Sentence objects representing the most important sentences in the document, ordered by importance

## Raises:
    ValueError: If NumPy dependencies are not installed (when _ensure_dependecies_installed fails)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - Document must contain sentences to process
        - Sentences_count must be a positive integer
        - NumPy must be installed for the algorithm to function
    Postconditions:
        - Returns a tuple of sentences ordered by semantic importance
        - Returns empty tuple if no valid dictionary can be created from the document

## Side Effects:
    - May issue warning if number of words is less than number of sentences
    - Calls external NumPy SVD function
    - May raise ValueError if NumPy is not installed

### `sumy.summarizers.lsa.LsaSummarizer._ensure_dependecies_installed` · *method*

## Summary:
Validates that the NumPy dependency is properly installed and available for LSA summarization.

## Description:
This method performs a runtime check to ensure that the NumPy library is available, as it's a required dependency for the LSA (Latent Semantic Analysis) summarizer algorithm. The method is called during the summarization process before any NumPy-dependent operations are performed. This validation prevents runtime errors that would occur if NumPy were missing.

Note: The current implementation contains a logical flaw - it checks `if numpy is None` which will never be true since NumPy is imported at the module level. A correct implementation would typically attempt to import NumPy or check for specific NumPy functionality to ensure it's properly available.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError: When NumPy is not available (though the current implementation has a logical flaw - it checks `if numpy is None` which will never be true since numpy is imported)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method should be called before any NumPy operations in the summarization pipeline
    Postconditions: If successful, guarantees NumPy is available for subsequent operations

## Side Effects:
    None

### `sumy.summarizers.lsa.LsaSummarizer._create_dictionary` · *method*

## Summary:
Creates a mapping from stemmed words to sequential integer indices while filtering out stop words.

## Description:
Constructs a dictionary that maps unique stemmed words from the input document to consecutive integer indices starting from zero. This dictionary serves as a vocabulary for subsequent matrix operations in the LSA summarization process. The method filters out stop words and duplicates to create a compact representation of the document's vocabulary.

This method is separated from other processing steps to encapsulate the vocabulary creation logic, making the LSA algorithm's pipeline more modular and easier to test independently.

## Args:
    document: A document object containing text content with .words and .sentences attributes

## Returns:
    dict[str, int]: A dictionary mapping stemmed words to their sequential indices

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._stop_words, self.normalize_word, self.stem_word
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Document must have a .words attribute that can be iterated over
    - Document must have a .sentences attribute
    - self._stop_words must be a collection that supports 'not in' operations
    
    Postconditions:
    - Returned dictionary contains only unique stemmed words from the document
    - Words in the dictionary are filtered to exclude stop words
    - Dictionary keys are stemmed versions of normalized words
    - Indices are assigned sequentially starting from 0

## Side Effects:
    None

### `sumy.summarizers.lsa.LsaSummarizer._create_matrix` · *method*

## Summary:
Creates a term-document frequency matrix for Latent Semantic Analysis (LSA) processing by counting word occurrences in sentences.

## Description:
This method constructs a numerical matrix representation of a document where each row corresponds to a unique word from the dictionary and each column corresponds to a sentence. The matrix elements represent word frequencies, enabling subsequent LSA computations. The method applies stemming to words before indexing them in the matrix.

## Args:
    document: Document object containing sentences to process
    dictionary: Mapping of stemmed words to row indices in the resulting matrix

## Returns:
    numpy.ndarray: A 2D matrix of shape (words_count, sentences_count) where each element represents the frequency of a word in a sentence

## Raises:
    None explicitly raised, but issues a warning via Python's warnings module when words_count < sentences_count

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The dictionary must contain mappings for all words that appear in the document sentences
        - The document must have at least one sentence
        - The dictionary must contain at least one word
    Postconditions:
        - Returns a NumPy array with dimensions matching the dictionary size and sentence count
        - All matrix entries are non-negative integers representing word frequencies

## Side Effects:
    Issues a warning via Python's warnings module when the number of words in the dictionary is less than the number of sentences in the document

### `sumy.summarizers.lsa.LsaSummarizer._compute_term_frequency` · *method*

## Summary:
Normalizes term frequencies in a document-term matrix using max frequency normalization with smoothing.

## Description:
This method performs term frequency normalization on a document-term matrix by dividing each term frequency by the maximum frequency of that term across all documents, then applying smoothing to prevent zero values. This normalization is a crucial preprocessing step in Latent Semantic Analysis (LSA) for text summarization.

The method is called during the LSA summarization pipeline in the `__call__` method of `LsaSummarizer` after creating the initial document-term matrix but before performing singular value decomposition.

## Args:
    matrix (numpy.ndarray): A 2D array where rows represent terms and columns represent documents, containing raw term frequencies.
    smooth (float): Smoothing parameter for frequency normalization. Must be between 0.0 and 1.0 (exclusive of 1.0). Defaults to 0.4.

## Returns:
    numpy.ndarray: The normalized matrix with smoothed term frequencies, where each column represents a document and each row represents a term.

## Raises:
    AssertionError: When the smooth parameter is outside the valid range [0.0, 1.0).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The matrix must be a 2D numpy array
        - The smooth parameter must satisfy 0.0 ≤ smooth < 1.0
    Postconditions:
        - All values in the returned matrix are between smooth and 1.0
        - Each column (document) in the returned matrix has been normalized by its maximum term frequency

## Side Effects:
    None

### `sumy.summarizers.lsa.LsaSummarizer._compute_ranks` · *method*

## Summary:
Computes rank scores for sentences based on singular value decomposition results in LSA summarization.

## Description:
This method calculates rank scores for sentences using the singular values (sigma) and right singular vectors (v_matrix) obtained from SVD decomposition. It's a core component of the Latent Semantic Analysis (LSA) summarization algorithm that determines sentence importance for selection.

The method is called during the summarization process after matrix decomposition, specifically in the `__call__` method of LsaSummarizer. It processes the SVD results to compute relevance scores for each sentence in the document.

## Args:
    sigma (tuple/list): Singular values from SVD decomposition, representing the importance of each dimension
    v_matrix (numpy.ndarray): Right singular vectors matrix from SVD decomposition, where each column represents a sentence's representation in the reduced semantic space

## Returns:
    list[float]: Rank scores for each sentence in the document, where higher values indicate more important sentences

## Raises:
    AssertionError: When the length of sigma doesn't match the number of rows in v_matrix, indicating incompatible matrices

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - sigma must be a sequence with length equal to v_matrix.shape[0]
        - v_matrix must be a 2D numpy array
        - Both sigma and v_matrix should result from compatible SVD decomposition
    
    Postconditions:
        - Returns a list of rank scores with the same length as the number of columns in v_matrix
        - All returned rank scores are non-negative real numbers

## Side Effects:
    None

