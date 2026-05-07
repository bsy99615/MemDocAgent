# `tokenizers.py`

## `sumy.nlp.tokenizers.DefaultWordTokenizer` · *class*

## Summary:
DefaultWordTokenizer provides a standard word tokenization implementation using NLTK's word_tokenize function.

## Description:
This class serves as the default implementation for word tokenization in the NLP pipeline. It wraps NLTK's word_tokenize method to provide a consistent interface for splitting text into individual words or tokens. The class is designed to be used when no language-specific or specialized tokenizer is required, providing a general-purpose solution for basic word tokenization tasks.

## State:
- No instance attributes beyond the standard object attributes
- The class does not store any state between tokenization calls
- __init__ method accepts no parameters and initializes the object with default settings

## Lifecycle:
- Creation: Instantiated without arguments using DefaultWordTokenizer()
- Usage: Call the tokenize() method with a text string argument
- Destruction: Standard Python object cleanup via garbage collection

## Method Map:
```mermaid
graph TD
    A[DefaultWordTokenizer] --> B[tokenize(text)]
    B --> C[nltk.word_tokenize(text)]
```

## Raises:
- No explicit exceptions are raised by the __init__ method
- The tokenize method may raise exceptions from NLTK's word_tokenize if the input text is not properly formatted

## Example:
```python
from sumy.nlp.tokenizers import DefaultWordTokenizer

tokenizer = DefaultWordTokenizer()
tokens = tokenizer.tokenize("Hello world! How are you?")
# Returns: ['Hello', 'world', '!', 'How', 'are', 'you', '?']
```

### `sumy.nlp.tokenizers.DefaultWordTokenizer.tokenize` · *method*

## Summary:
Tokenizes input text into a list of word tokens using NLTK's word tokenizer.

## Description:
This method serves as a simple wrapper around NLTK's word_tokenize function to split input text into individual word tokens. It is designed to be part of a tokenization pipeline where text needs to be converted into discrete word units for further processing such as summarization.

The method is typically called during the preprocessing phase of text analysis workflows, specifically when preparing text data for summarization algorithms that require tokenized input.

## Args:
    text (str): The input text string to be tokenized into individual words and punctuation marks.

## Returns:
    list[str]: A list of tokenized elements (words and punctuation) extracted from the input text. Each element represents a distinct word or punctuation mark as determined by NLTK's word tokenization algorithm.

## Raises:
    None explicitly raised by this method, though underlying NLTK functions may raise exceptions for malformed input.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input text parameter must be a valid string.
    Postconditions: The returned list contains all tokens from the input text in order, preserving punctuation and word boundaries.

## Side Effects:
    None - This method is stateless and does not perform any I/O operations or modify external state.

## `sumy.nlp.tokenizers.HebrewWordTokenizer` · *class*

## Summary:
A specialized tokenizer for Hebrew text that removes punctuation and extracts Hebrew words from input text.

## Description:
The HebrewWordTokenizer class provides a method to tokenize Hebrew text by removing punctuation and filtering for Hebrew characters. It serves as a language-specific tokenizer that handles Hebrew text processing in natural language processing pipelines. This class is typically used when working with Hebrew documents that require tokenization for tasks like text analysis, summarization, or machine learning preprocessing.

## State:
- `_TRANSLATOR`: Class attribute of type `dict` created by `str.maketrans("", "", string.punctuation)` that maps punctuation characters to None for removal
- The class maintains no instance state; it operates purely on input text through its classmethod

## Lifecycle:
- Creation: The class is instantiated automatically when the module is imported; no explicit instantiation required
- Usage: Call the `tokenize` classmethod with Hebrew text as argument
- Destruction: No special cleanup required; class is stateless

## Method Map:
```mermaid
graph TD
    A[HebrewWordTokenizer.tokenize] --> B[text.translate(_TRANSLATOR)]
    B --> C[hebrew_tokenizer.tokenize(text)]
    C --> D{token in (HEBREW, HEBREW_1, HEBREW_2)}
    D --> E[Return filtered Hebrew words]
```

## Raises:
- `ValueError`: Raised when the `hebrew_tokenizer` library is not installed, with message "Hebrew tokenizer requires hebrew_tokenizer. Please, install it by command 'pip install hebrew_tokenizer'."

## Example:
```python
# Tokenize Hebrew text
text = "שלום עולם! איך אתה?"
tokens = HebrewWordTokenizer.tokenize(text)
# Returns: ['שלום', 'עולם', 'איך', 'אתה']

# This would raise ValueError if hebrew_tokenizer is not installed
try:
    tokens = HebrewWordTokenizer.tokenize("טקסט בעברית")
except ValueError as e:
    print(f"Missing dependency: {e}")
```

### `sumy.nlp.tokenizers.HebrewWordTokenizer.tokenize` · *method*

*No documentation generated.*

## `sumy.nlp.tokenizers.JapaneseWordTokenizer` · *class*

## Summary:
JapaneseWordTokenizer is a text processing class that segments Japanese text into individual words using the TinySegmenter library.

## Description:
This class provides Japanese text tokenization functionality by leveraging the TinySegmenter library, which is specifically designed for Japanese word segmentation. It serves as a specialized tokenizer for Japanese language processing within the sumy library ecosystem. The class is typically instantiated by language-specific tokenizer factories or configuration systems that detect and handle different language requirements.

## State:
- No instance attributes maintained
- The class relies on the tinysegmenter library for all tokenization operations
- No initialization parameters required

## Lifecycle:
- Creation: Instantiated without parameters; the class is stateless
- Usage: Call the tokenize() method with a Unicode string containing Japanese text
- Destruction: No special cleanup required; uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[JapaneseWordTokenizer] --> B[tokenize(text)]
    B --> C{tinysegmenter available?}
    C -->|Yes| D[segmenter.tokenize(text)]
    C -->|No| E[ValueError]
```

## Raises:
- ValueError: Raised when the tinysegmenter library is not installed, with a descriptive message instructing users to install it via 'pip install tinysegmenter'

## Example:
```python
# Create tokenizer instance
tokenizer = JapaneseWordTokenizer()

# Tokenize Japanese text
text = "私はPythonが好きです"
tokens = tokenizer.tokenize(text)
# Returns segmented tokens like ['私', 'は', 'Python', 'が', '好き', 'です']
```

### `sumy.nlp.tokenizers.JapaneseWordTokenizer.tokenize` · *method*

## Summary:
Tokenizes Japanese text into individual words using the tinysegmenter library.

## Description:
This method performs Japanese word segmentation on the provided text using the tinysegmenter library. It is designed to handle Japanese text specifically, breaking it down into meaningful word units that can be processed further in natural language processing pipelines.

## Args:
    text (str): A string containing Japanese text to be tokenized.

## Returns:
    list[str]: A list of tokens (words) extracted from the input Japanese text.

## Raises:
    ValueError: When the tinysegmenter library is not installed, with a descriptive message instructing the user to install it via 'pip install tinysegmenter'.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input text must be a string containing Japanese characters.
    Postconditions: The returned list contains segmented Japanese words.

## Side Effects:
    None

## `sumy.nlp.tokenizers.ChineseWordTokenizer` · *class*

## Summary:
ChineseWordTokenizer is a text processing class that performs word segmentation on Chinese text using the jieba library.

## Description:
This class provides a standardized interface for tokenizing Chinese text into individual words or tokens. It serves as a specialized tokenizer within the sumy library's natural language processing capabilities, specifically designed for handling Chinese language text where word boundaries are not explicitly marked like in English.

The tokenizer is intended to be used when processing Chinese documents for tasks such as text summarization, where proper word segmentation is crucial for accurate analysis. It acts as a wrapper around the jieba library, providing error handling for missing dependencies.

## State:
- No instance attributes are stored
- The class relies on the jieba library being available at runtime

## Lifecycle:
- Creation: Instances can be created directly with no constructor arguments required
- Usage: Call the tokenize() method with a string argument containing Chinese text
- Destruction: No special cleanup required; standard Python garbage collection applies

## Method Map:
```mermaid
graph TD
    A[ChineseWordTokenizer] --> B[tokenize(text)]
    B --> C{import jieba}
    C -->|Success| D[jieba.cut(text)]
    C -->|Failure| E[ValueError]
```

## Raises:
- ValueError: Raised when the jieba library is not installed, with a descriptive message instructing the user to install it via 'pip install jieba'

## Example:
```python
tokenizer = ChineseWordTokenizer()
chinese_text = "我爱自然语言处理技术"
tokens = tokenizer.tokenize(chinese_text)
# Returns segmented words from jieba
for token in tokens:
    print(token)
```

### `sumy.nlp.tokenizers.ChineseWordTokenizer.tokenize` · *method*

## Summary:
Tokenizes Chinese text into individual words using the jieba library.

## Description:
This method performs Chinese word segmentation on the provided text using the jieba library. It is designed to handle Chinese text specifically and returns a generator of tokens representing individual words. The method is part of the ChineseWordTokenizer class which provides language-specific tokenization capabilities for Chinese text processing.

## Args:
    text (str): The Chinese text to be tokenized into individual words.

## Returns:
    generator[str]: A generator yielding individual Chinese words (tokens) from the input text.

## Raises:
    ValueError: When the jieba library is not installed, with a descriptive message instructing the user to install it via 'pip install jieba'.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input text must be a string containing Chinese characters.
    Postconditions: The returned generator will yield individual Chinese words that were segmented by jieba.

## Side Effects:
    None

## `sumy.nlp.tokenizers.KoreanSentencesTokenizer` · *class*

## Summary:
Tokenizes Korean text into sentences using the Kkma tokenizer from konlpy.

## Description:
This class provides sentence segmentation for Korean text by utilizing the Kkma (Korean Natural Language Processing Toolkit) tokenizer from the konlpy library. It serves as a wrapper around the Kkma.sentences() method to provide a consistent interface for Korean sentence tokenization within the sumy library ecosystem.

## State:
- No instance attributes maintained
- The class requires konlpy library to be installed
- No class invariants to maintain

## Lifecycle:
- Creation: Instantiation requires no arguments
- Usage: Call the tokenize() method with a Korean text string
- Destruction: No explicit cleanup required as it uses temporary Kkma instances

## Method Map:
```mermaid
graph TD
    A[KoreanSentencesTokenizer] --> B[tokenize(text)]
    B --> C{konlpy import}
    C -->|Success| D[Kkma()]
    C -->|Failure| E[ValueError]
    D --> F[Kkma.sentences(text)]
    F --> G[Return sentences]
    E --> H[Throw ValueError]
```

## Raises:
- ValueError: Raised when the konlpy library is not installed, with a descriptive message instructing the user to install it via 'pip install konlpy'

## Example:
```python
tokenizer = KoreanSentencesTokenizer()
text = "안녕하세요. 저는 프로그래머입니다. 잘 부탁드립니다."
sentences = tokenizer.tokenize(text)
# Returns list of sentences like ['안녕하세요.', '저는 프로그래머입니다.', '잘 부탁드립니다.']
```

### `sumy.nlp.tokenizers.KoreanSentencesTokenizer.tokenize` · *method*

## Summary:
Tokenizes Korean text into sentences using the Kkma tokenizer from konlpy.

## Description:
This method performs sentence segmentation on Korean text by utilizing the Kkma (Korean Natural Language Processing Toolkit) tokenizer. It is designed to split Korean text into meaningful sentence units, which is a crucial preprocessing step for Korean text analysis and summarization tasks. The method is part of the KoreanSentencesTokenizer class and follows the standard tokenization interface used throughout the sumy library.

## Args:
    text (str): The Korean text to be segmented into sentences.

## Returns:
    list[str]: A list of sentence strings extracted from the input text.

## Raises:
    ValueError: When the konlpy library is not installed, with a descriptive message instructing the user to install it via 'pip install konlpy'.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The input text must be a string containing Korean characters
    - The konlpy library must be installed in the environment
    
    Postconditions:
    - Returns a list of strings, each representing a sentence from the input text
    - The returned list will be empty if the input text is empty or contains no sentences

## Side Effects:
    None

## `sumy.nlp.tokenizers.KoreanWordTokenizer` · *class*

## Summary:
A Korean language word tokenizer that extracts noun tokens from Korean text using the Kkma morphological analyzer.

## Description:
The KoreanWordTokenizer is a specialized tokenizer designed for processing Korean text by extracting noun tokens. It leverages the Kkma (Korean Morphological Analyzer) from the konlpy library to perform Korean-specific natural language processing. This class should be instantiated when processing Korean-language documents for text analysis, tokenization, or natural language processing tasks.

## State:
- No instance attributes beyond the standard object attributes
- The tokenize method requires a text parameter of type str
- The class depends on the konlpy library being installed

## Lifecycle:
- Creation: Instantiated without parameters; requires konlpy library to be installed
- Usage: Call the tokenize() method with a Korean text string as argument
- Destruction: No special cleanup required; uses standard Python object lifecycle

## Method Map:
```mermaid
graph TD
    A[KoreanWordTokenizer] --> B[tokenize(text)]
    B --> C{konlpy available?}
    C -->|No| D[ValueError]
    C -->|Yes| E[Kkma().nouns(text)]
    E --> F[Return noun tokens]
```

## Raises:
- ValueError: Raised when the konlpy library is not installed, with a descriptive message instructing the user to install it via 'pip install konlpy'

## Example:
```python
from sumy.nlp.tokenizers import KoreanWordTokenizer

# Create tokenizer instance
tokenizer = KoreanWordTokenizer()

# Tokenize Korean text
text = "안녕하세요, 저는 프로그래밍을 좋아합니다."
tokens = tokenizer.tokenize(text)
print(tokens)  # Output: ['안녕하세요', '프로그래밍', '좋아합니다']
```

### `sumy.nlp.tokenizers.KoreanWordTokenizer.tokenize` · *method*

## Summary:
Extracts Korean nouns from input text using the Kkma tokenizer library.

## Description:
This method implements Korean word tokenization by leveraging the Kkma (Korean Natural Language Processing) library from konlpy. It processes Korean text and returns a list of extracted noun tokens, which are commonly used for text analysis and summarization tasks in Korean language processing pipelines.

## Args:
    text (str): The Korean text to tokenize into nouns.

## Returns:
    list[str]: A list of Korean noun tokens extracted from the input text.

## Raises:
    ValueError: When the konlpy library is not installed, with a message instructing the user to install it via 'pip install konlpy'.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input text must be a valid string containing Korean characters.
    Postconditions: The returned list contains only Korean noun tokens extracted from the input text.

## Side Effects:
    None

## `sumy.nlp.tokenizers.GreekSentencesTokenizer` · *class*

## Summary:
A sentence tokenizer specifically designed for Greek language text that splits text into individual sentences using NLTK's Greek sentence tokenizer with additional post-processing.

## Description:
This class provides functionality to split Greek text into individual sentences. It leverages NLTK's sentence tokenization capabilities with Greek language support and applies additional processing to handle special cases in Greek punctuation. The tokenizer is intended for use in natural language processing pipelines where Greek text needs to be segmented into sentences for further analysis.

## State:
- No instance attributes maintained
- The class operates purely on the input text provided to the tokenize method
- Uses NLTK's Greek sentence tokenizer internally

## Lifecycle:
- Creation: Instantiation is not required as this is a classmethod-based interface
- Usage: Call the static `tokenize` classmethod with Greek text as argument
- Destruction: No cleanup required as it's stateless

## Method Map:
```mermaid
graph TD
    A[Input Greek Text] --> B[nltk.sent_tokenize with language='greek']
    B --> C[filter(None, re.split(...)) on each sentence]
    C --> D[Return list of stripped sentences]
```

## Raises:
- None explicitly raised by the tokenize method
- May raise exceptions from NLTK's sentence tokenizer if invalid input is provided

## Example:
```python
from sumy.nlp.tokenizers import GreekSentencesTokenizer

text = "Αυτό είναι ένα παράδειγμα κειμένου. Αυτό είναι ένα άλλο παράδειγμα."
sentences = GreekSentencesTokenizer.tokenize(text)
# Returns: ['Αυτό είναι ένα παράδειγμα κειμένου.', 'Αυτό είναι ένα άλλο παράδειγμα.']
```

### `sumy.nlp.tokenizers.GreekSentencesTokenizer.tokenize` · *method*

## Summary:
Splits Greek text into individual sentences, handling compound sentences separated by semicolons.

## Description:
Tokenizes Greek text into sentences using NLTK's sentence tokenizer configured for Greek language, then further splits compound sentences that contain semicolons into separate sentences. This method processes each sentence to split on semicolons followed by whitespace, effectively separating semicolon-delimited clauses into individual sentences.

## Args:
    text (str): Greek text to be tokenized into sentences

## Returns:
    list[str]: List of individual sentences extracted from the input text, with leading/trailing whitespace removed. Empty strings are filtered out from the result.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Input text must be a valid string containing Greek text
    Postconditions: Returns a list of non-empty sentences with whitespace stripped

## Side Effects:
    None

## `sumy.nlp.tokenizers.ArabicWordTokenizer` · *class*

## Summary:
Tokenizes Arabic text into individual words using the pyarabic library.

## Description:
The ArabicWordTokenizer class provides a simple interface for tokenizing Arabic text. When the tokenize method is called, it attempts to import and use the tokenize function from the pyarabic library. This class is designed to be used when Arabic text processing is required in a natural language processing pipeline.

## State:
- No instance attributes maintained
- The class does not store any state between method calls
- __init__ method is implicit (no parameters required)

## Lifecycle:
- Creation: Instantiation is straightforward with no constructor arguments required
- Usage: Call the tokenize() method with Arabic text as a string argument
- Destruction: No special cleanup required; uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[ArabicWordTokenizer] --> B[tokenize(text)]
    B --> C{pyarabic import}
    C -->|Success| D[return tokenize(text)]
    C -->|Failure| E[raise ValueError]
```

## Raises:
- ValueError: Raised when the pyarabic library is not installed, with a descriptive message instructing users to install it via 'pip install pyarabic'

## Example:
```python
# Create tokenizer instance
tokenizer = ArabicWordTokenizer()

# Tokenize Arabic text
arabic_text = "هذا نص عربي للاختبار"
tokens = tokenizer.tokenize(arabic_text)
print(tokens)  # Output will be list of Arabic words
```

### `sumy.nlp.tokenizers.ArabicWordTokenizer.tokenize` · *method*

## Summary:
Tokenizes Arabic text into individual words using the pyarabic library.

## Description:
This method performs word tokenization on Arabic text by leveraging the pyarabic library's tokenize function. It is designed to handle the specific linguistic characteristics of Arabic text, including its unique script and morphological properties. The method is part of a language-specific tokenizer system that provides appropriate tokenization for different languages.

## Args:
    text (str): The Arabic text to be tokenized into individual words.

## Returns:
    list[str]: A list of tokenized Arabic words extracted from the input text.

## Raises:
    ValueError: When the pyarabic library is not installed, with a descriptive message instructing the user to install it via 'pip install pyarabic'.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The input text must be a string containing Arabic characters
    - The pyarabic library must be installed in the environment
    
    Postconditions:
    - Returns a list of strings representing individual Arabic words
    - The returned list contains no empty strings

## Side Effects:
    None

## `sumy.nlp.tokenizers.ArabicSentencesTokenizer` · *class*

## Summary:
Tokenizes Arabic text into sentences using the pyarabic library.

## Description:
The ArabicSentencesTokenizer class provides functionality to split Arabic text into individual sentences. It serves as a specialized tokenizer for Arabic language processing tasks where sentence-level segmentation is required. This class is typically used in natural language processing pipelines for Arabic text analysis and summarization.

## State:
- No instance attributes maintained
- The class relies on external pyarabic library for actual tokenization
- No initialization parameters required

## Lifecycle:
- Creation: Instantiation is straightforward with no constructor arguments required
- Usage: Call the tokenize() method with Arabic text string as argument
- Destruction: No special cleanup required as it's a stateless utility class

## Method Map:
```mermaid
graph TD
    A[ArabicSentencesTokenizer] --> B[tokenize(text)]
    B --> C{pyarabic import}
    C -->|Success| D[sentence_tokenize(text)]
    C -->|Failure| E[ValueError]
```

## Raises:
- ValueError: Raised when the pyarabic library is not installed, with message instructing user to install via 'pip install pyarabic'

## Example:
```python
tokenizer = ArabicSentencesTokenizer()
text = "مرحبا بك في هذا البرنامج. كيف حالك اليوم؟"
sentences = tokenizer.tokenize(text)
# Returns list of sentences: ['مرحبا بك في هذا البرنامج.', 'كيف حالك اليوم؟']
```

### `sumy.nlp.tokenizers.ArabicSentencesTokenizer.tokenize` · *method*

*No documentation generated.*

## `sumy.nlp.tokenizers.Tokenizer` · *class*

## Summary:
A multilingual tokenizer that provides sentence and word tokenization services for various languages, with specialized handling for Hebrew, Japanese, Chinese, Korean, Greek, and Arabic.

## Description:
The Tokenizer class serves as a unified interface for tokenizing text into sentences and words across multiple languages. It automatically selects appropriate tokenization strategies based on the specified language, falling back to NLTK's standard tokenizers for unsupported languages. This class is designed to handle the complexities of different linguistic structures while providing a consistent API for downstream text processing tasks.

The tokenizer is typically instantiated by passing a language identifier to the constructor, and then used to process paragraphs into sentences and sentences into words. It handles language aliases (like Slovak mapping to Czech) and includes special abbreviations for better sentence boundary detection in various languages.

## State:
- `_language`: The canonical language identifier for this tokenizer instance
- `_sentence_tokenizer`: The sentence tokenizer object for the specified language
- `_word_tokenizer`: The word tokenizer object for the specified language
- `_WORD_PATTERN`: Regular expression pattern used to validate words
- `LANGUAGE_ALIASES`: Maps language aliases to canonical language names
- `LANGUAGE_EXTRA_ABREVS`: Additional abbreviation lists for better sentence tokenization
- `SPECIAL_SENTENCE_TOKENIZERS`: Language-specific sentence tokenizers
- `SPECIAL_WORD_TOKENIZERS`: Language-specific word tokenizers

The `language` property returns the language identifier.

## Lifecycle:
Creation: Instantiate with a language identifier string (e.g., "english", "french"). The constructor normalizes the language name and selects appropriate tokenizers.

Usage: Call `to_sentences()` to split text into sentences, then `to_words()` to split sentences into words. The tokenizers are stateless and can be reused multiple times.

Destruction: No explicit cleanup required. The class implements no resource management beyond standard Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[Tokenizer.__init__] --> B[Tokenizer._get_sentence_tokenizer]
    A --> C[Tokenizer._get_word_tokenizer]
    D[Tokenizer.to_sentences] --> B
    E[Tokenizer.to_words] --> C
    F[Tokenizer._is_word] --> G[_WORD_PATTERN.match]
    D --> H[tokenizer.tokenize]
    E --> I[tokenizer.tokenize]
    H --> J[unicode.strip]
    I --> K[filter(_is_word)]
```

## Raises:
- `LookupError`: Raised when NLTK tokenizers are missing or when a language is not supported. This occurs during initialization when trying to load NLTK tokenizers that aren't installed.

## Example:
```python
# Create a tokenizer for English
tokenizer = Tokenizer("english")

# Split text into sentences
paragraph = "Hello world! How are you? I'm fine."
sentences = tokenizer.to_sentences(paragraph)
# Result: ('Hello world!', 'How are you?', "I'm fine.")

# Split sentences into words
words = tokenizer.to_words(sentences[0])
# Result: ('Hello', 'world')

# Access the language
print(tokenizer.language)  # Output: "english"
```

### `sumy.nlp.tokenizers.Tokenizer.__init__` · *method*

## Summary:
Initializes a tokenizer with the specified language and configures language-specific sentence and word tokenizers.

## Description:
The constructor method sets up the tokenizer for processing text in the specified language. It normalizes the language identifier, resolves language aliases, and initializes appropriate sentence and word tokenizers based on the language requirements. This method prepares the tokenizer object for subsequent text processing operations like sentence splitting and word tokenization.

## Args:
    language (str): Language identifier for text processing. Supports various language codes that will be normalized and resolved through aliases.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    LookupError: Raised when NLTK tokenizers are missing or the specified language is not supported, particularly when loading punkt tokenizers for standard languages.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._language: Stores the normalized language identifier
    - self._sentence_tokenizer: Stores the sentence tokenizer for the specified language
    - self._word_tokenizer: Stores the word tokenizer for the specified language

## Constraints:
    Preconditions: 
    - The language parameter must be a valid string identifier
    - NLTK data must be properly installed for standard languages
    - Language aliases defined in LANGUAGE_ALIASES must be valid
    
    Postconditions:
    - self._language contains the normalized language identifier
    - self._sentence_tokenizer is initialized with appropriate sentence tokenizer
    - self._word_tokenizer is initialized with appropriate word tokenizer

## Side Effects:
    - May trigger NLTK data loading from disk when initializing standard language tokenizers
    - Accesses external NLTK resources for language-specific tokenizers
    - May raise LookupError if required NLTK data is missing

### `sumy.nlp.tokenizers.Tokenizer.language` · *method*

## Summary:
Returns the language identifier associated with this tokenizer instance.

## Description:
This property provides read-only access to the language setting that determines which tokenizers and language-specific rules are used for text processing. The language is set during object initialization and influences sentence and word tokenization behavior.

## Args:
    None

## Returns:
    str: The language identifier string used for tokenization operations.

## Raises:
    None

## State Changes:
    Attributes READ: self._language
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Tokenizer object must be properly initialized with a valid language parameter.
    Postconditions: The returned value is identical to the language parameter provided during initialization.

## Side Effects:
    None

### `sumy.nlp.tokenizers.Tokenizer._get_sentence_tokenizer` · *method*

## Summary:
Returns a sentence tokenizer appropriate for the specified language, either from special handlers or NLTK punkt tokenizers.

## Description:
This method retrieves a sentence tokenizer for the given language. It first checks if a special sentence tokenizer is defined for the language in the SPECIAL_SENTENCE_TOKENIZERS dictionary. If not, it attempts to load an NLTK punkt tokenizer from the standard NLTK data path. This method is primarily used during Tokenizer initialization to set up the sentence tokenizer for the specified language.

## Args:
    language (str): Language code for which to retrieve a sentence tokenizer

## Returns:
    object: A sentence tokenizer instance appropriate for the specified language

## Raises:
    LookupError: When NLTK tokenizers are missing or the language is not supported

## State Changes:
    Attributes READ: self.SPECIAL_SENTENCE_TOKENIZERS
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The language parameter must be a valid language identifier recognized by the system
    Postconditions: Returns a valid sentence tokenizer object that can tokenize text into sentences

## Side Effects:
    I/O: May perform file I/O operations when loading NLTK tokenizer data from disk
    External service calls: None

### `sumy.nlp.tokenizers.Tokenizer._get_word_tokenizer` · *method*

## Summary:
Selects and returns an appropriate word tokenizer for the specified language, falling back to a default tokenizer if none is available.

## Description:
This method serves as a factory for word tokenizers, choosing language-specific implementations when available or providing a default fallback. It is called during the initialization of the Tokenizer class to set up the appropriate word tokenizer for processing text in the specified language.

## Args:
    language (str): The language code for which to retrieve a word tokenizer

## Returns:
    BaseWordTokenizer: An instance of a language-specific word tokenizer or DefaultWordTokenizer if no special tokenizer is defined for the language

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.SPECIAL_WORD_TOKENIZERS
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The language parameter must be a valid language identifier that can be processed by the tokenizer system
    Postconditions: Returns a valid word tokenizer instance that implements a tokenize() method

## Side Effects:
    None

### `sumy.nlp.tokenizers.Tokenizer.to_sentences` · *method*

## Summary:
Converts a paragraph into a tuple of sentence strings by applying language-specific sentence tokenization.

## Description:
Tokenizes the input paragraph into individual sentences using the appropriate sentence tokenizer for the configured language. This method handles language-specific abbreviation expansions to improve sentence boundary detection accuracy.

## Args:
    paragraph (str): The input text paragraph to be split into sentences.

## Returns:
    tuple[str]: A tuple containing individual sentences as strings, with leading/trailing whitespace removed.

## Raises:
    LookupError: When NLTK tokenizers are missing or the language is not supported.

## State Changes:
    Attributes READ: self._sentence_tokenizer, self._language, self.LANGUAGE_EXTRA_ABREVS
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The tokenizer must be properly initialized with a valid language.
    Postconditions: Returns a tuple of strings with no empty elements (unless original paragraph contained them).

## Side Effects:
    None

### `sumy.nlp.tokenizers.Tokenizer.to_words` · *method*

## Summary:
Converts a sentence into a tuple of valid word tokens by applying language-specific tokenization followed by filtering.

## Description:
Processes an input sentence by first applying language-specific word tokenization and then filtering out invalid tokens. This method serves as a standardized interface for extracting meaningful words from text while respecting language-specific tokenization rules and excluding punctuation, numbers, and other non-word elements.

## Args:
    sentence (str): Input text to be converted into word tokens.

## Returns:
    tuple[str]: A tuple containing only valid word tokens extracted from the input sentence, with each word matching the word pattern regex.

## Raises:
    None explicitly raised, but underlying tokenization operations may raise exceptions from NLTK or other tokenizer libraries.

## State Changes:
    Attributes READ: self._word_tokenizer, self._is_word
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Tokenizer instance must be properly initialized with a valid language.
    Postconditions: The returned tuple contains only valid words according to the language-specific word pattern.

## Side Effects:
    None

### `sumy.nlp.tokenizers.Tokenizer._is_word` · *method*

## Summary:
Checks if a string matches the tokenizer's word pattern.

## Description:
This method evaluates whether a given string conforms to the tokenizer's word pattern specification. It is used internally to identify valid word tokens during text processing operations.

## Args:
    word (str): The string to validate against the word pattern.

## Returns:
    bool: True if the word matches the tokenizer's word pattern, False otherwise.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: _WORD_PATTERN (assumed to be a class attribute)
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The word parameter must be a string.
    Postconditions: Returns a boolean indicating pattern match result.

## Side Effects:
    None.

